"""
CRIME DNA — User-Facing Hidden Behavioral Pattern Discovery Service

Evaluates a user-submitted incident's 70-dimensional Behavioral DNA vector
against empirical behavioral cluster archetypes and cross-crime patterns
discovered from the historical 220,663 incident corpus.

Scientifically grounds pattern association via spherical cosine alignment to
empirical centroids, exact incident counts, and cross-category representation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from src.models.clustering.config import CLUSTER_ARCHETYPES
from src.models.cross_crime.config import CATEGORY_SHORT_NAMES

logger = logging.getLogger("CRIME_DNA_PATTERN_DISCOVERY")


class HiddenBehavioralPatternService:
    """
    Service for evaluating incident association with historical behavioral patterns.
    """

    def __init__(self):
        pass

    def identify_patterns(
        self,
        norm_vec: np.ndarray,
        input_data: Dict[str, Any],
        state: Any
    ) -> Dict[str, Any]:
        """
        Determines the primary and secondary behavioral patterns associated with an incident.

        Args:
            norm_vec: Unit L2-normalized 70D Behavioral DNA vector of the query incident.
            input_data: Raw input parameters submitted by the user.
            state: ApplicationState instance containing preloaded models and artifacts.

        Returns:
            Structured hidden behavioral pattern discovery result.
        """
        # Ensure query vector is unit normalized
        vec = np.asarray(norm_vec, dtype=np.float32).reshape(-1)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        # 1. Evaluate association against all 8 empirical cluster centroids
        similarities: List[Tuple[int, float]] = []
        cluster_centers = None
        if state.clusterer is not None and state.clusterer.model is not None:
            cluster_centers = state.clusterer.model.cluster_centers_
        elif not getattr(state, "is_ready", False):
            state.load_all()
            if state.clusterer is not None and state.clusterer.model is not None:
                cluster_centers = state.clusterer.model.cluster_centers_

        if cluster_centers is None:
            from src.api.exceptions import ModelNotLoadedError
            raise ModelNotLoadedError("Behavioral Clustering Engine is not loaded in application state.")

        for k in range(len(cluster_centers)):
            c = cluster_centers[k]
            c_norm = np.linalg.norm(c)
            c_unit = c / (c_norm if c_norm > 0 else 1.0)
            sim = float(np.dot(vec, c_unit))
            similarities.append((k, sim))

        # Sort clusters by cosine similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        primary_k, primary_sim = similarities[0]

        # Calculate primary distance
        primary_dist = max(0.0, 1.0 - primary_sim)

        # Retrieve pattern metadata from Cross-Crime and Clustering artifacts
        cc_key = f"CCP_{primary_k:02d}"
        cc_info = state.cross_crime_patterns.get(cc_key) or state.cross_crime_patterns.get(str(primary_k), {})
        cluster_profile = state.cluster_profiles.get(str(primary_k), {})
        archetype = CLUSTER_ARCHETYPES.get(primary_k, {
            "name": f"Behavioral Cluster {primary_k}",
            "category": "Mixed",
            "summary": "Multi-dimensional behavioral grouping."
        })

        # Pattern identification
        pattern_id = cc_info.get("pattern_id", cc_key)
        pattern_name = cc_info.get("pattern_name", f"Cross-Crime: {archetype['name']}")
        archetype_name = archetype.get("name", f"Cluster {primary_k}")
        macro_category = archetype.get("category", "General")
        cluster_summary = archetype.get("summary", "")

        # Historical incident counts & category diversity from actual ML artifacts
        total_incidents = int(cc_info.get("total_incidents", cluster_profile.get("incident_count", 0)))
        categories_represented = cc_info.get("categories_represented", [])
        categories_count = int(cc_info.get("cross_crime_evidence", {}).get(
            "categories_count",
            len(categories_represented)
        ))

        # Scientific confidence / association strength tiering
        confidence_tier = self._classify_association_tier(primary_sim)
        confidence_score_pct = round(max(0.0, primary_sim) * 100.0, 1)

        # Synthesize behavioral characteristics from actual input and pattern traits
        behavioral_characteristics, formula = self._synthesize_behavioral_characteristics(
            input_data=input_data,
            pattern_info=cc_info,
            norm_vec=vec
        )

        # Build list of all associated patterns with significant affinity
        associated_patterns = []
        for k, sim in similarities:
            p_key = f"CCP_{k:02d}"
            p_info = state.cross_crime_patterns.get(p_key, {})
            p_arch = CLUSTER_ARCHETYPES.get(k, {})
            associated_patterns.append({
                "pattern_identifier": p_key,
                "cluster_id": k,
                "pattern_name": p_info.get("pattern_name", f"Cross-Crime: {p_arch.get('name', f'Pattern {k}')}"),
                "association_score": round(float(sim), 4),
                "confidence_score_pct": round(max(0.0, float(sim)) * 100.0, 1),
                "confidence_tier": self._classify_association_tier(sim),
                "supporting_historical_incidents": int(p_info.get("total_incidents", 0)),
                "categories_represented_count": len(p_info.get("categories_represented", [])),
                "is_primary": (k == primary_k)
            })

        # Structured response
        is_cross_crime = categories_count > 1
        cross_crime_summary = "Found across multiple crime categories." if is_cross_crime else "Concentrated within single crime category."
        shared_profile_text = "These crime categories share a similar behavioral profile."

        ethical_advisory = (
            "Based on patterns learned from historical incidents. "
            "CRIME DNA analyzes behavioral patterns in historical incident data. "
            "Similarity or novelty does not establish offender identity, guilt, or causation. "
            "CRIME DNA detects behavioral patterns across incidents. These patterns indicate shared "
            "modus operandi and environmental factors, not that offenses were committed by the same individual."
        )

        return {
            # Core Hidden Behavioral Pattern identification
            "pattern_detected": True,
            "pattern_identifier": pattern_id,
            "pattern_name": pattern_name,
            "archetype_name": archetype_name,
            "behavioral_characteristics": behavioral_characteristics,
            "behavioral_formula": formula,
            "number_of_supporting_historical_incidents": total_incidents,
            "number_of_crime_categories_represented": categories_count,
            "relevant_crime_categories": categories_represented,
            "association_strength": {
                "association_score": round(float(primary_sim), 4),
                "confidence_score_pct": confidence_score_pct,
                "confidence_tier": confidence_tier,
                "distance_to_centroid": round(float(primary_dist), 4),
                "metric": "Cosine Similarity to Spherical Archetype Centroid"
            },
            "is_cross_crime_pattern": is_cross_crime,
            "cross_crime_summary": cross_crime_summary,
            "shared_profile_text": shared_profile_text,
            "associated_patterns": associated_patterns,
            "inter_category_similarities": cc_info.get("inter_category_similarities", {}),
            "cross_crime_evidence": cc_info.get("cross_crime_evidence", {}),
            "ethical_advisory": ethical_advisory,

            # Backwards-compatible cluster_assignment fields
            "cluster_id": primary_k,
            "cluster_name": archetype_name,
            "macro_category": macro_category,
            "distance_to_centroid": round(float(primary_dist), 4),
            "cluster_summary": cluster_summary,
            "archetype_details": cluster_profile
        }

    def _classify_association_tier(self, cosine_sim: float) -> str:
        """Categorizes cosine similarity into a transparent, scientifically valid confidence tier."""
        if cosine_sim >= 0.80:
            return "Strong Association"
        elif cosine_sim >= 0.60:
            return "Moderate Association"
        else:
            return "Weak Association"

    def _synthesize_behavioral_characteristics(
        self,
        input_data: Dict[str, Any],
        pattern_info: Dict[str, Any],
        norm_vec: np.ndarray
    ) -> Tuple[List[str], str]:
        """
        Synthesizes the salient 4-part behavioral characteristics formula
        from the actual incident parameters and empirical pattern traits.
        """
        traits: List[str] = []

        # 1. Temporal Trait
        is_night = bool(input_data.get("is_night", False))
        time_str = str(input_data.get("incident_time") or "")
        if time_str and ":" in time_str:
            try:
                hour = int(time_str.split(":")[0])
                if hour < 6 or hour >= 20:
                    is_night = True
            except ValueError:
                pass

        if is_night:
            traits.append("Night")
        else:
            traits.append("Daytime")

        # 2. Location Trait
        loc_type = str(input_data.get("location_type", "residential")).lower()
        if "residential" in loc_type or "home" in loc_type:
            traits.append("Residential")
        elif "commercial" in loc_type or "store" in loc_type or "retail" in loc_type:
            traits.append("Commercial")
        elif "public" in loc_type or "park" in loc_type or "street" in loc_type:
            traits.append("Public Space")
        elif "transit" in loc_type or "vehicle" in loc_type:
            traits.append("Transit / Vehicle")
        else:
            pop_setting = str(input_data.get("population_setting", "")).lower()
            if "metropolitan" in pop_setting or "dense" in pop_setting:
                traits.append("Metropolitan Core")
            elif "small" in pop_setting or "town" in pop_setting:
                traits.append("Small Municipality")
            else:
                traits.append("Municipal Setting")

        # 3. Property / Drug Involvement Trait
        has_property = bool(input_data.get("has_property", False)) or float(input_data.get("property_value", 0.0)) > 0
        has_drug = bool(input_data.get("has_drug", False))

        if has_drug:
            traits.append("Contraband / Drug involvement")
        elif has_property:
            traits.append("Property involved")
        else:
            traits.append("No property involved")

        # 4. Harm / Weapon / Violence Trait
        has_injury = bool(input_data.get("has_injury", False))
        has_weapon = bool(input_data.get("has_weapon", False))
        has_arrest = bool(input_data.get("has_arrest", False))

        if has_injury:
            traits.append("Bodily injury")
        elif has_weapon:
            traits.append("Weapon displayed")
        elif has_arrest:
            traits.append("On-scene arrest")
        elif not has_injury:
            traits.append("No injury")
        else:
            traits.append("Standard contact")

        formula = " + ".join(traits)
        return traits, formula


# Global singleton instance
pattern_discovery_service = HiddenBehavioralPatternService()
