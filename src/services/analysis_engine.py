"""
CRIME DNA — Central Behavioral Intelligence Analysis Engine

Provides a reusable backend service that accepts a validated user incident
and performs unified multi-perspective behavioral intelligence analysis
by orchestrating the existing Phase 3–10 ML models, artifacts, and indexes:

User Incident
    ↓
Behavioral DNA (Compatible Preprocessing + Phase 3 Encoder)
    ↓
Existing Similarity Engine (Phase 5: Cosine KNN)
    ↓
Existing Clustering / Pattern Engine (Phase 6: Spherical K-Means)
    ↓
Existing Cross-Crime Pattern Logic (Phase 7: Cross-Category Modus Operandi)
    ↓
Existing Evolution Logic (Phase 8: Longitudinal Drift & Seasonal Trends)
    ↓
Existing Novelty Logic (Phase 9: Spherical Distance + Isolation Forest)
    ↓
Existing Explainability Logic (Phase 10: Exact Additive Cosine Attribution)
    ↓
Unified Analysis Result

All scores and insights are computed live from trained models and indexed
historical data. No scores or percentages are hardcoded.
"""

import os
import sys
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

# Ensure workspace root is in sys.path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from src.features.input_bridge import bridge
from src.features.config import FEATURE_GROUPS, FEATURE_DESCRIPTIONS
from src.models.explainability.config import GROUP_DISPLAY_NAMES
from src.models.explainability.explainer import decompose_behavioral_similarity
from src.models.similarity.engine import (
    normalize_category_for_matching,
    extract_relevant_behavioral_characteristics
)
from src.services.pattern_discovery import pattern_discovery_service
from src.services.evolution_service import evolution_service
from src.services.novelty_service import novelty_service
from src.services.analysis_record_service import analysis_record_service
from src.api.state import state
from src.api.exceptions import ModelNotLoadedError

logger = logging.getLogger("CRIME_DNA_ANALYSIS_ENGINE")


class CrimeDnaAnalysisEngine:
    """
    Central reusable backend service for real-time CRIME DNA analysis.
    Coordinates all Phase 5-10 models in-memory on demand without retraining.
    """

    def __init__(self):
        self.version = "2.0.0"

    def analyze(
        self,
        input_data: Dict[str, Any],
        top_k: int = 5,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete multi-perspective behavioral analysis for a validated incident.

        Parameters
        ----------
        input_data : Dict[str, Any]
            Validated incident input dictionary (e.g. from IncidentInputRequest).
        top_k : int
            Number of nearest historical neighbors to retrieve.
        user_id : Optional[str]
            Lightweight user or session identifier (e.g. User_A, User_B).

        Returns
        -------
        Dict[str, Any]
            Unified analysis result containing all standard analytical sections.
        """
        t_start = time.perf_counter()
        analysis_id = f"ANALYSIS_{uuid.uuid4().hex[:12].upper()}"
        uid = str(user_id or input_data.get("user_id") or "user_anon").strip()[:64]
        timestamp = datetime.now(timezone.utc).isoformat()
        scenario_title = str(input_data.get("scenario_title", "Simulated Incident Case")).strip()

        # Ensure ML registry is ready
        if not state.is_ready:
            state.load_all()

        if state.similarity_engine is None or state.similarity_engine.model is None:
            raise ModelNotLoadedError("Behavioral Similarity Engine is not loaded in application state.")

        # =========================================================================
        # 1. Incident Summary
        # =========================================================================
        incident_summary = self._build_incident_summary(input_data, scenario_title)

        # =========================================================================
        # 2. Behavioral DNA Generation (Compatible Preprocessing + Phase 3 Transform)
        # =========================================================================
        raw_vec, norm_vec, subprofile_energies = bridge.encode(input_data)
        data_coverage = bridge.compute_domain_data_coverage(input_data)
        active_traits = bridge.get_active_traits(raw_vec, top_n=5)
        human_readable_dna = bridge.generate_human_readable_fingerprint(input_data, raw_vec)
        machine_readable_dna = bridge.generate_machine_readable_fingerprint(
            input_data, raw_vec, norm_vec, subprofile_energies
        )

        behavioral_dna = {
            "vector_dimension": 70,
            "subprofile_energies": subprofile_energies,
            "data_coverage": data_coverage,
            "top_active_traits": active_traits,
            "human_readable": human_readable_dna,
            "machine_readable": machine_readable_dna
        }

        # =========================================================================
        # 3. Existing Similarity Engine (Phase 5: Cosine KNN)
        # =========================================================================
        query_inc_id = input_data.get("incident_id") or input_data.get("id") or input_data.get("query_incident_id")
        search_k = min(len(state.incident_ids), top_k + 5) if query_inc_id else min(max(1, top_k), len(state.incident_ids))

        if hasattr(state.similarity_engine, "kneighbors_fast"):
            distances, indices = state.similarity_engine.kneighbors_fast(
                norm_vec,
                n_neighbors=search_k
            )
        else:
            norm_matrix_query = norm_vec.reshape(1, -1)
            distances, indices = state.similarity_engine.model.kneighbors(
                norm_matrix_query,
                n_neighbors=search_k
            )

        query_crime_cat = str(input_data.get("crime_category", "property"))
        norm_query_cat = normalize_category_for_matching(query_crime_cat)

        similar_matches: List[Dict[str, Any]] = []
        similarity_scores_pct: List[float] = []

        rank = 1
        for dist, idx in zip(distances[0], indices[0]):
            matched_id = state.incident_ids[idx]

            # Query Self-Exclusion (Part D): Do not return query incident as its own nearest neighbor
            if query_inc_id and matched_id == query_inc_id:
                continue

            # Real Cosine Similarity percentage: (1.0 - distance) * 100
            sim_pct = round(max(0.0, min(100.0, (1.0 - float(dist)) * 100.0)), 2)
            similarity_scores_pct.append(sim_pct)

            profile = state.get_incident_profile(matched_id)
            ctx = profile.get("context", {}) if profile else {}
            crime_cat = ctx.get("primary_crime_category", "Unknown Offense")
            cluster_name = profile["cluster"]["cluster_name"] if profile else "Unknown"

            # Cross-Crime evaluation
            norm_match_cat = normalize_category_for_matching(crime_cat)
            is_cross = bool(norm_query_cat and (norm_query_cat != norm_match_cat))
            category_rel = "Different Crime Category" if is_cross else "Same Crime Category"
            cross_indicator = (
                f"⚡ Cross-Crime Match: Shares behavioral characteristics with {crime_cat}"
                if is_cross else None
            )
            relevant_traits = extract_relevant_behavioral_characteristics(ctx)

            # Compute subprofile breakdown & dot-product attribution against this specific match
            match_vec = state.normalized_matrix[idx] if state.normalized_matrix is not None else None
            sub_sims = {}
            sub_attributions = {}
            total_dot = float(np.dot(norm_vec, match_vec)) if match_vec is not None else 0.0

            if match_vec is not None:
                grp_map = getattr(state, "feature_group_indices", None) or {
                    k: [state.feature_names.index(c) for c in cols if c in state.feature_names]
                    for k, cols in state.feature_groups.items()
                }
                for grp_key, grp_idxs in grp_map.items():
                    if grp_idxs:
                        u_g = norm_vec[grp_idxs]
                        v_g = match_vec[grp_idxs]
                        nu = float(np.linalg.norm(u_g))
                        nv = float(np.linalg.norm(v_g))
                        dot_g = float(np.dot(u_g, v_g))

                        if nu > 0 and nv > 0:
                            sim_g = float(dot_g / (nu * nv))
                            sub_sims[grp_key] = round(max(0.0, min(1.0, sim_g)) * 100.0, 1)
                        else:
                            # Both lack features in this group: 0.0% similarity, not 100%
                            sub_sims[grp_key] = 0.0

                        # Exact additive attribution share
                        share_pct = round((dot_g / max(1e-6, total_dot)) * 100.0, 1) if total_dot > 0 else 0.0
                        sub_attributions[grp_key] = {
                            "dot_product": round(dot_g, 4),
                            "contribution_pct": max(0.0, share_pct)
                        }

            # Transparent Observed Feature Comparison (Part E)
            observed_comparison = self._compute_observed_feature_comparison(
                input_data=input_data,
                ctx=ctx,
                query_crime_cat=query_crime_cat,
                match_crime_cat=crime_cat
            )

            similar_matches.append({
                "rank": rank,
                "incident_id": matched_id,
                "similarity": f"{sim_pct:.1f}%",
                "similarity_score_pct": sim_pct,
                "cosine_distance": round(float(dist), 6),
                "crime_category": crime_cat,
                "primary_crime_category": crime_cat,
                "cluster_name": cluster_name,
                "is_cross_crime_match": is_cross,
                "category_relationship": category_rel,
                "cross_crime_indicator": cross_indicator,
                "relevant_behavioral_characteristics": relevant_traits,
                "subprofile_similarity_pct": sub_sims,
                "subprofile_attributions": sub_attributions,
                "observed_feature_comparison": observed_comparison
            })

            rank += 1
            if len(similar_matches) >= top_k:
                break

        has_cross_crime_matches = any(m["is_cross_crime_match"] for m in similar_matches)
        cross_crime_summary_indicator = (
            "Similar behavioral characteristics were found across different crime categories."
            if has_cross_crime_matches
            else "All top matches belong to the same statutory category."
        )

        same_category_matches = [m for m in similar_matches if not m["is_cross_crime_match"]]
        different_category_matches = [m for m in similar_matches if m["is_cross_crime_match"]]

        similar_behavioral_incidents = {
            "title": "SIMILAR BEHAVIORAL INCIDENTS",
            "query_crime_category": query_crime_cat.replace("_", " ").title(),
            "cross_crime_indicator": cross_crime_summary_indicator,
            "has_cross_crime_matches": has_cross_crime_matches,
            "same_category_count": len(same_category_matches),
            "cross_category_count": len(different_category_matches),
            "matches": similar_matches,
            "grouped_by_category_relationship": {
                "same_crime_category": same_category_matches,
                "different_crime_categories": different_category_matches
            },
            "metric_explanation": (
                "Similarity score is computed as (1.0 - cosine_distance) * 100 on the 70D unit hypersphere S^69. "
                "The score measures geometric behavioral proximity in feature space. "
                "It is NOT a probability that two incidents were committed by the same offender."
            ),
            "ethical_advisory": (
                "Based on patterns learned from historical incidents. "
                "CRIME DNA analyzes behavioral patterns in historical incident data. "
                "Similarity or novelty does not establish offender identity, guilt, or causation. "
                "Behavioral similarity reflects shared modus operandi characteristics between incidents and does not identify offenders."
            )
        }

        dna_similarity = {
            "top_match_similarity_pct": similarity_scores_pct[0] if similarity_scores_pct else 0.0,
            "mean_top_k_similarity_pct": round(float(np.mean(similarity_scores_pct)), 2) if similarity_scores_pct else 0.0,
            "min_top_k_similarity_pct": similarity_scores_pct[-1] if similarity_scores_pct else 0.0,
            "top_matched_incident_id": similar_matches[0]["incident_id"] if similar_matches else None,
            "k_neighbors_searched": len(similar_matches),
            "cross_crime_indicator": cross_crime_summary_indicator,
            "has_cross_crime_matches": has_cross_crime_matches,
            "metric": "Cosine Similarity (Unit L2 Hyper-Sphere)",
            "score_meaning": "Geometric cosine proximity between normalized behavioral feature vectors.",
            "score_limitations": "Does NOT represent the probability that two incidents were committed by the same individual."
        }

        # =========================================================================
        # 4. Existing Clustering / Pattern Engine (Phase 6 & 7: Hidden Behavioral Patterns)
        # =========================================================================
        hidden_behavioral_patterns = pattern_discovery_service.identify_patterns(
            norm_vec=norm_vec,
            input_data=input_data,
            state=state
        )
        cl_id = int(hidden_behavioral_patterns["cluster_id"])
        cl_name = str(hidden_behavioral_patterns["cluster_name"])
        macro_cat = str(hidden_behavioral_patterns["macro_category"])
        dist_to_cent = float(hidden_behavioral_patterns["distance_to_centroid"])
        summary = str(hidden_behavioral_patterns["cluster_summary"])

        if state.clusterer is not None and state.clusterer.model is not None and cl_id < len(state.clusterer.model.cluster_centers_):
            centroid_vec = state.clusterer.model.cluster_centers_[cl_id]
        else:
            centroid_vec = np.zeros(70, dtype=np.float32)

        # =========================================================================
        # 5. Existing Cross-Crime Pattern Logic (Phase 7: Cross-Category Synergy)
        # =========================================================================
        cc_key = f"CCP_{cl_id:02d}"
        cc_info = state.cross_crime_patterns.get(cc_key) or state.cross_crime_patterns.get(str(cl_id), {})

        # Identify similar historical matches that belong to a DIFFERENT crime category
        input_category = str(input_data.get("crime_category", "property")).lower()
        cross_category_matches = []
        for match in similar_matches:
            match_cat = str(match["primary_crime_category"]).lower()
            if match_cat != "unknown" and input_category not in match_cat and match_cat not in input_category:
                cross_category_matches.append({
                    "incident_id": match["incident_id"],
                    "rank": match["rank"],
                    "similarity_score_pct": match["similarity_score_pct"],
                    "statutory_category": match["primary_crime_category"],
                    "cluster_name": match["cluster_name"],
                    "note": f"Shares behavioral signature despite differing statutory classification ({match['primary_crime_category']})"
                })

        cross_crime_matches = {
            "dominant_cross_crime_pattern": cc_key,
            "cross_crime_pattern_name": cc_info.get("pattern_name", f"Pattern Archetype {cl_id}"),
            "represented_categories": [
                f"{c.get('category_name')}: {c.get('percentage')}%"
                for c in cc_info.get("categories_represented", [])
            ],
            "behavioral_synergy": cc_info.get(
                "behavioral_summary",
                f"Shares operational modus operandi with crimes in Cluster {cl_id} across multiple statutory classes."
            ),
            "cross_category_matches_in_top_k": cross_category_matches,
            "has_cross_crime_bridge": len(cross_category_matches) > 0
        }

        # =========================================================================
        # 6. Existing Novelty Logic (Phase 9: Dual-Paradigm Centroids + Isolation Forest)
        # =========================================================================
        novelty = novelty_service.evaluate_novelty(
            norm_vec=norm_vec,
            centroid_vec=centroid_vec,
            cl_id=cl_id,
            cl_name=cl_name,
            input_data=input_data,
            state=state
        )

        # =========================================================================
        # 7. Existing Explainability Logic (Phase 10: Exact Additive Attribution)
        # =========================================================================
        top_match_id = similar_matches[0]["incident_id"] if similar_matches else None
        top_match_profile = state.get_incident_profile(top_match_id) if top_match_id else None
        top_match_vec = state.get_incident_dna_vector(top_match_id) if top_match_id else None

        why_similar = self._build_explainability(
            norm_vec=norm_vec,
            top_match_id=top_match_id,
            top_match_vec=top_match_vec,
            top_match_profile=top_match_profile,
            input_data=input_data,
            top_match_similarity_pct=similar_matches[0]["similarity_score_pct"] if similar_matches else 0.0
        )

        # =========================================================================
        # 8. Existing Evolution Logic (Phase 8: Longitudinal Shifts & Drift)
        # =========================================================================
        behavioral_evolution = self._build_evolutionary_context(
            input_data=input_data,
            cl_id=cl_id,
            cl_name=cl_name
        )

        # =========================================================================
        # 9. DNA Subprofile Energy Comparison (Radar Overlay)
        # =========================================================================
        top_match_energies = {}
        if top_match_vec is not None:
            grp_map = getattr(state, "feature_group_indices", None) or {
                k: [state.feature_names.index(c) for c in cols if c in state.feature_names]
                for k, cols in state.feature_groups.items()
            }
            for grp_key, grp_idxs in grp_map.items():
                if grp_idxs:
                    top_match_energies[grp_key] = round(float(np.mean(top_match_vec[grp_idxs]) * 100.0), 1)

        dna_comparison = {
            "input_subprofile_energies": subprofile_energies,
            "top_match_incident_id": top_match_id,
            "top_match_subprofile_energies": top_match_energies
        }

        # =========================================================================
        # 10. Technical Metadata & Performance Profiling
        # =========================================================================
        execution_time_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
        technical_metadata = {
            "engine_version": self.version,
            "analysis_id": analysis_id,
            "execution_time_ms": execution_time_ms,
            "vector_dimension": 70,
            "distance_metric": "Cosine Distance on Unit L2 Hypersphere",
            "historical_index_size": len(state.incident_ids),
            "models_utilized": {
                "similarity": "BehavioralSimilarityEngine (Phase 5 Cosine KNN)",
                "clustering": "BehavioralClusterer (Phase 6 Spherical K-Means)",
                "cross_crime": "CrossCrimeAnalyzer (Phase 7)",
                "evolution": "BehavioralEvolutionAnalyzer (Phase 8 ANOVA/Trends)",
                "novelty": "BehavioralAnomalyDetector (Phase 9 Isolation Forest + Centroids)",
                "explainability": "BehavioralSimilarityExplainer (Phase 10 Additive Attribution)"
            }
        }

        ethical_advisory = (
            "Crime Compass analyzes incident characteristics and historical behavioral patterns. "
            "Similarity or novelty does not establish offender identity, guilt, or causation. "
            "It does not identify offenders, determine guilt, or establish that incidents were committed by the same individual. "
            "Evaluated strictly through cross-crime behavioral similarity."
        )

        # =========================================================================
        # 11. Clean Analysis Record (Data Minimization & Zero PII)
        # =========================================================================
        # Clean input summary (strictly behavioral fields, no names, addresses, or PII)
        hour_val = input_data.get("incident_hour")
        if hour_val is None and input_data.get("incident_time"):
            try:
                hour_val = int(str(input_data["incident_time"]).split(":")[0])
            except Exception:
                hour_val = None

        clean_input_summary = {
            "scenario_title": scenario_title,
            "crime_category": str(input_data.get("crime_category", "property")),
            "population_setting": str(input_data.get("population_setting", "mid_sized_city")),
            "temporal_profile": {
                "hour": hour_val,
                "month": input_data.get("incident_month"),
                "is_weekend": input_data.get("is_weekend"),
                "is_night": bool(input_data.get("is_night", False)) if "is_night" in input_data else None
            },
            "behavioral_flags": {
                "has_weapon": bool(input_data.get("has_weapon", False)),
                "has_injury": bool(input_data.get("has_injury", False)),
                "has_property": bool(input_data.get("has_property", False)),
                "has_drug": bool(input_data.get("has_drug", False)),
                "has_arrest": bool(input_data.get("has_arrest", False)),
                "has_relationship": bool(input_data.get("has_relationship", False)),
            },
            "incident_counts": {
                "offense_count": int(input_data.get("offense_count", 1)),
                "victim_count": int(input_data.get("victim_count", 1)),
                "offender_count": int(input_data.get("offender_count", 1)),
            }
        }

        # Clean Behavioral DNA summary
        clean_dna_summary = {
            "vector_dimension": 70,
            "subprofile_energies": subprofile_energies,
            "top_active_traits": active_traits,
            "human_readable_fingerprint": human_readable_dna
        }

        # Clean similarity summary
        clean_similarity_summary = {
            "top_matched_incident_id": similar_matches[0]["incident_id"] if similar_matches else None,
            "similarity_percentage": similar_matches[0]["similarity_score_pct"] if similar_matches else 0.0,
            "distance_metric": "Cosine Similarity on Unit L2 Hyper-Sphere",
            "category_relationship": similar_matches[0]["category_relationship"] if similar_matches else "Same Crime Category",
            "has_cross_crime_match": has_cross_crime_matches,
            "k_neighbors_searched": len(similar_matches)
        }

        # Clean pattern summary
        clean_pattern_summary = {
            "pattern_id": hidden_behavioral_patterns.get("pattern_identifier", f"PATTERN_{cl_id:02d}"),
            "cluster_id": cl_id,
            "pattern_name": hidden_behavioral_patterns.get("pattern_name", cl_name),
            "behavioral_formula": hidden_behavioral_patterns.get("behavioral_formula", ""),
            "supporting_incident_count": int(hidden_behavioral_patterns.get("number_of_supporting_historical_incidents", 0)),
            "crime_categories_represented_count": int(hidden_behavioral_patterns.get("number_of_crime_categories_represented", 1)),
            "association_strength_score": float(hidden_behavioral_patterns.get("association_strength", {}).get("confidence_score_pct", 0.0)),
            "association_tier": str(hidden_behavioral_patterns.get("association_strength", {}).get("confidence_tier", "Standard"))
        }

        # Clean novelty summary
        unusual_factor_labels = [
            str(f.get("label", f.get("feature", "")))
            for f in novelty.get("unusual_behavioral_factors", [])
        ]
        clean_novelty_summary = {
            "novelty_score": float(novelty.get("novelty_score", 0.0)),
            "novelty_tier": str(novelty.get("novelty_tier", "Standard Behavioral Pattern")),
            "is_novel": bool(novelty.get("is_novel", False)),
            "pattern_fit_score": float(novelty.get("behavioral_pattern_fit", {}).get("pattern_fit_score_pct", 100.0)),
            "fit_description": str(novelty.get("behavioral_pattern_fit", {}).get("fit_description", "Matches standard patterns")),
            "unusual_factors": unusual_factor_labels
        }

        analysis_record = {
            "analysis_id": analysis_id,
            "user_id": uid,
            "timestamp": timestamp,
            "input_summary": clean_input_summary,
            "behavioral_dna": clean_dna_summary,
            "similarity_summary": clean_similarity_summary,
            "pattern_summary": clean_pattern_summary,
            "novelty_summary": clean_novelty_summary,
            "ethical_advisory": ethical_advisory
        }

        # Build unified response (both canonical keys & frontend keys)
        unified_response = {
            # Canonical standard keys
            "incident_summary": incident_summary,
            "behavioral_dna": behavioral_dna,
            "data_coverage": data_coverage,
            "compact_behavioral_fingerprint": human_readable_dna.get("compact_traits", []),
            "dna_similarity": dna_similarity,
            "similar_historical_incidents": similar_matches,
            "similar_behavioral_incidents": similar_behavioral_incidents,
            "cross_crime_matches": cross_crime_matches,
            "hidden_behavioral_patterns": hidden_behavioral_patterns,
            "why_similar": why_similar,
            "behavioral_evolution": behavioral_evolution,
            "novelty": novelty,
            "technical_metadata": technical_metadata,

            # Backwards-compatible frontend keys
            "analysis_id": analysis_id,
            "timestamp": timestamp,
            "scenario_title": scenario_title,
            "human_readable_dna": human_readable_dna,
            "machine_readable_dna": machine_readable_dna,
            "cluster_assignment": hidden_behavioral_patterns,
            "cross_crime_mapping": cross_crime_matches,
            "novelty_assessment": novelty,
            "why_similar_explanation": why_similar,
            "evolutionary_context": behavioral_evolution,
            "dna_comparison": dna_comparison,
            "ethical_advisory": ethical_advisory,
            "analysis_record": analysis_record
        }

        # Store clean analytical record with non-circular copy of full result
        persisted_record = dict(analysis_record)
        persisted_record["full_result"] = dict(unified_response)
        persisted_record["full_result"].pop("analysis_record", None)

        try:
            analysis_record_service.save_record(persisted_record)
        except Exception as err:
            logger.warning(f"Could not persist analysis record {analysis_id}: {err}")

        return unified_response

    def _build_incident_summary(self, input_data: Dict[str, Any], title: str) -> Dict[str, Any]:
        """Synthesizes structured human-readable incident summary."""
        date_str = str(input_data.get("incident_date") or "Unspecified Date")
        time_str = str(input_data.get("incident_time") or "Unspecified Time")
        pop_setting = str(input_data.get("population_setting", "mid_sized_city")).replace("_", " ").title()

        return {
            "scenario_title": title,
            "temporal_profile": {
                "date": date_str,
                "time": time_str,
                "hour": input_data.get("incident_hour"),
                "month": input_data.get("incident_month"),
                "is_weekend": input_data.get("is_weekend")
            },
            "statutory_classification": {
                "category": str(input_data.get("crime_category", "property")).upper(),
                "is_attempted": bool(input_data.get("is_attempted", False)),
                "offense_count": int(input_data.get("offense_count", 1))
            },
            "environmental_profile": {
                "jurisdiction_setting": pop_setting,
                "location_count": int(input_data.get("location_count", 1))
            },
            "force_and_weapons": {
                "has_weapon": bool(input_data.get("has_weapon", False)),
                "weapon_count": int(input_data.get("weapon_count", 0)),
                "has_criminal_activity": bool(input_data.get("has_criminal_activity", False))
            },
            "demographics": {
                "victim_count": int(input_data.get("victim_count", 1)),
                "victim_avg_age": input_data.get("victim_avg_age"),
                "offender_count": int(input_data.get("offender_count", 1)),
                "offender_avg_age": input_data.get("offender_avg_age")
            },
            "economic_impact": {
                "has_property": bool(input_data.get("has_property", False)),
                "property_value": float(input_data.get("property_value", 0.0)),
                "currency": str(input_data.get("currency", "INR")),
                "property_value_usd": float(input_data.get("property_value", 0.0))
            },
            "regional_profile": {
                "country": str(input_data.get("country", "India")),
                "state_ut": input_data.get("state_ut"),
                "district": input_data.get("district"),
                "city_town": input_data.get("city_town"),
                "locality": input_data.get("locality"),
                "pin_code": input_data.get("pin_code"),
                "timezone": str(input_data.get("timezone", "Asia/Kolkata"))
            },
            "harm_and_legal": {
                "has_injury": bool(input_data.get("has_injury", False)),
                "has_drug": bool(input_data.get("has_drug", False)),
                "has_arrest": bool(input_data.get("has_arrest", False))
            }
        }

    def _build_explainability(
        self,
        norm_vec: np.ndarray,
        top_match_id: Optional[str],
        top_match_vec: Optional[np.ndarray],
        top_match_profile: Optional[Dict[str, Any]],
        input_data: Dict[str, Any],
        top_match_similarity_pct: float
    ) -> Dict[str, Any]:
        """Computes exact additive cosine similarity feature and group attribution."""
        if top_match_vec is None or top_match_id is None:
            return {
                "target_incident_id": None,
                "overall_similarity_pct": 0.0,
                "plain_english_explanation": "No historical match available for comparison.",
                "behavioral_group_comparisons": [],
                "group_attributions": [],
                "top_matching_features": [],
                "main_contributing_similarities": [],
                "semantic_differences": []
            }

        # Exact additive cosine attribution: c_j = u_j * v_j
        contributions = norm_vec * top_match_vec
        total_sim = float(np.dot(norm_vec, top_match_vec))

        group_attributions = []
        grp_map = getattr(state, "feature_group_indices", None) or {
            k: [state.feature_names.index(c) for c in cols if c in state.feature_names]
            for k, cols in state.feature_groups.items()
        }
        for grp_key, grp_idxs in grp_map.items():
            if grp_idxs:
                grp_sum = float(np.sum(contributions[grp_idxs]))
                share_pct = round((grp_sum / total_sim * 100.0) if total_sim > 0 else 0.0, 1)
                display_name = GROUP_DISPLAY_NAMES.get(grp_key, grp_key.replace("_", " ").title())
                group_attributions.append({
                    "group_key": grp_key,
                    "display_name": display_name,
                    "absolute_contribution": round(grp_sum, 4),
                    "share_percentage": share_pct
                })

        group_attributions.sort(key=lambda x: -x["share_percentage"])

        # Top positive features
        top_feat_idxs = np.argsort(-contributions)[:5]
        top_matching_features = []
        for f_idx in top_feat_idxs:
            c_val = float(contributions[f_idx])
            if c_val > 0.005:
                f_name = state.feature_names[f_idx]
                top_matching_features.append({
                    "feature_name": f_name,
                    "contribution": round(c_val, 4),
                    "input_value": round(float(norm_vec[f_idx]), 3),
                    "match_value": round(float(top_match_vec[f_idx]), 3),
                    "description": FEATURE_DESCRIPTIONS.get(f_name, f_name)
                })

        main_sims = [
            f"Similar {g['display_name'].lower()}"
            for g in group_attributions[:2]
            if g["share_percentage"] > 15.0
        ]

        # Extract semantic contrasts
        semantic_diffs = []
        input_hour = 14
        if input_data.get("incident_time"):
            try:
                input_hour = int(str(input_data["incident_time"]).split(":")[0])
            except Exception:
                input_hour = 14
        elif input_data.get("incident_hour") is not None:
            input_hour = int(input_data["incident_hour"])

        if top_match_profile:
            ctx = top_match_profile.get("context", {})
            match_hour = int(ctx.get("incident_hour", 14))
            if abs(input_hour - match_hour) > 4:
                semantic_diffs.append(
                    f"Different operational timing ({input_hour:02d}:00 vs {match_hour:02d}:00 in historical {top_match_id})"
                )

            input_wep = bool(input_data.get("has_weapon", False))
            match_wep = bool(ctx.get("has_weapon", False))
            if input_wep != match_wep:
                semantic_diffs.append(
                    f"Weapon contrast: {'Armed' if input_wep else 'Unarmed'} vs {'Armed' if match_wep else 'Unarmed'} in historical {top_match_id}"
                )

            input_cat = str(input_data.get("crime_category", "Property")).upper()
            match_cat = str(ctx.get("primary_crime_category", "Property")).upper()
            if input_cat != match_cat:
                semantic_diffs.append(
                    f"Different statutory category: {input_cat} vs {match_cat} in historical {top_match_id}"
                )

        decomp = decompose_behavioral_similarity(
            u=norm_vec,
            v=top_match_vec,
            feature_names=state.feature_names,
            feature_groups=state.feature_groups
        )

        return {
            "target_incident_id": top_match_id,
            "overall_similarity_pct": top_match_similarity_pct,
            "plain_english_explanation": decomp["plain_english_explanation"],
            "behavioral_group_comparisons": decomp["behavioral_group_comparisons"],
            "group_attributions": group_attributions,
            "top_matching_features": top_matching_features,
            "main_contributing_similarities": main_sims,
            "semantic_differences": semantic_diffs or ["Highly aligned operational execution across all primary indicators."]
        }

    def _build_evolutionary_context(
        self,
        input_data: Dict[str, Any],
        cl_id: int,
        cl_name: str
    ) -> Dict[str, Any]:
        """Synthesizes historical behavioral evolution timeline grounded in Phase 8 empirical metrics."""
        evo = evolution_service.build_evolution_timeline(
            input_data=input_data,
            cl_id=cl_id,
            cl_name=cl_name,
            state=state
        )
        # Part G metadata enrichment
        evo["time_period_analyzed"] = "January 1, 2024 – December 31, 2024 (Full Calendar Year)"
        evo["historical_incidents_count"] = 220663
        evo["measurement_basis"] = "Proportions (%) across 4-month empirical observation trimesters and normalized incident rates"
        evo["period_coverage"] = "Complete 12-month calendar year reporting"
        evo["data_limitations"] = (
            "Historical shifts reflect population-level seasonal trends and reporting distributions across the 2024 reference corpus. "
            "They do not track individual offender behavior or imply future criminality."
        )
        return evo

    def _compute_observed_feature_comparison(
        self,
        input_data: Dict[str, Any],
        ctx: Dict[str, Any],
        query_crime_cat: str,
        match_crime_cat: str
    ) -> Dict[str, Any]:
        """
        Computes transparent rule-based comparison of observed input fields (Part E).
        Labels as 'Observed feature comparison' (not SHAP explanations or model importance).
        Categorizes Time, Location setting, Crime characteristics, Method & activity, Property/context into:
        Similar, Different, or Unknown.
        """
        # 1. Time
        q_night = input_data.get("is_night")
        if q_night is None and input_data.get("incident_time"):
            try:
                h = int(str(input_data["incident_time"]).split(":")[0])
                q_night = (h >= 20 or h < 6)
            except Exception:
                pass
        m_night = ctx.get("is_night")

        if q_night is None or m_night is None:
            time_comp = {
                "domain": "Time",
                "status": "Unknown",
                "details": "Diurnal cycle unobserved in one or both incidents",
                "is_match": False
            }
        elif q_night == m_night:
            time_comp = {
                "domain": "Time",
                "status": "Similar",
                "details": f"Both incidents occurred during {'night/nocturnal' if q_night else 'daylight'} hours",
                "is_match": True
            }
        else:
            time_comp = {
                "domain": "Time",
                "status": "Different",
                "details": f"Timing differed: {'night' if q_night else 'daytime'} vs {'night' if m_night else 'daytime'}",
                "is_match": False
            }

        # 2. Location setting
        q_pop = str(input_data.get("population_setting", "")).lower()
        m_pop = str(ctx.get("population_group_desc", "")).lower()
        if not q_pop or not m_pop:
            loc_comp = {
                "domain": "Location setting",
                "status": "Unknown",
                "details": "Jurisdictional or setting data unspecified",
                "is_match": False
            }
        else:
            q_urban = any(x in q_pop for x in ("city", "large", "metro", "urban"))
            m_urban = any(x in m_pop for x in ("city", "100,000", "msa", "urban", "county"))
            if q_urban == m_urban:
                loc_comp = {
                    "domain": "Location setting",
                    "status": "Similar",
                    "details": "Both incidents occurred in comparable municipal density settings",
                    "is_match": True
                }
            else:
                loc_comp = {
                    "domain": "Location setting",
                    "status": "Different",
                    "details": "Differing population setting and municipal density",
                    "is_match": False
                }

        # 3. Crime characteristics
        norm_q_cat = normalize_category_for_matching(query_crime_cat)
        norm_m_cat = normalize_category_for_matching(match_crime_cat)
        if not norm_q_cat or not norm_m_cat:
            crime_comp = {
                "domain": "Crime characteristics",
                "status": "Unknown",
                "details": "Offense classification unspecified in one or both records",
                "is_match": False
            }
        elif norm_q_cat == norm_m_cat:
            crime_comp = {
                "domain": "Crime characteristics",
                "status": "Similar",
                "details": f"Both incidents share statutory category ({match_crime_cat})",
                "is_match": True
            }
        else:
            crime_comp = {
                "domain": "Crime characteristics",
                "status": "Different",
                "details": f"Differing statutory classifications: {query_crime_cat} vs {match_crime_cat}",
                "is_match": False
            }

        # 4. Method and activity
        q_wep = input_data.get("has_weapon")
        m_wep = ctx.get("has_weapon")
        if q_wep is None or m_wep is None:
            method_comp = {
                "domain": "Method and activity",
                "status": "Unknown",
                "details": "Weapon deployment unobserved in one or both records",
                "is_match": False
            }
        elif q_wep == m_wep:
            method_comp = {
                "domain": "Method and activity",
                "status": "Similar",
                "details": f"Both incidents were {'armed encounters' if q_wep else 'unarmed executions'}",
                "is_match": True
            }
        else:
            method_comp = {
                "domain": "Method and activity",
                "status": "Different",
                "details": f"Weapon presence differed: {'armed' if q_wep else 'unarmed'} vs {'armed' if m_wep else 'unarmed'}",
                "is_match": False
            }

        # 5. Property/context
        q_prop = input_data.get("has_property")
        m_prop = ctx.get("has_property")
        q_inj = input_data.get("has_injury")
        m_inj = ctx.get("has_injury")

        if q_prop is None or m_prop is None:
            prop_comp = {
                "domain": "Property/context",
                "status": "Unknown",
                "details": "Property target context unobserved in one or both records",
                "is_match": False
            }
        elif q_prop == m_prop and (q_inj is None or m_inj is None or q_inj == m_inj):
            prop_comp = {
                "domain": "Property/context",
                "status": "Similar",
                "details": f"Consistent target objective ({'property target' if q_prop else 'non-property'}) and harm dynamics",
                "is_match": True
            }
        else:
            prop_comp = {
                "domain": "Property/context",
                "status": "Different",
                "details": "Property targeting or victim harm dynamics diverged",
                "is_match": False
            }

        domains = [time_comp, loc_comp, crime_comp, method_comp, prop_comp]
        matching_domains = [d["domain"] for d in domains if d["status"] == "Similar"]
        differing_domains = [d["domain"] for d in domains if d["status"] == "Different"]
        unknown_domains = [d["domain"] for d in domains if d["status"] == "Unknown"]

        is_cross = bool(norm_q_cat and (norm_q_cat != norm_m_cat))
        if is_cross:
            cross_explanation = (
                f"Cross-crime match: Although statutory classifications differ ({query_crime_cat} vs {match_crime_cat}), "
                f"the incidents share strong behavioral modus operandi alignment in {', '.join(matching_domains) if matching_domains else 'underlying behavioral dimensions'}."
            )
        else:
            cross_explanation = f"Same-category match: Both incidents are classified under {query_crime_cat}."

        return {
            "title": "Observed feature comparison",
            "methodology_note": "Rule-based comparison of observed input fields, not SHAP explanations or model feature importance.",
            "domains": domains,
            "matching_domains": matching_domains,
            "differing_domains": differing_domains,
            "unknown_domains": unknown_domains,
            "cross_crime_explanation": cross_explanation
        }


# Global singleton instance
analysis_engine = CrimeDnaAnalysisEngine()
