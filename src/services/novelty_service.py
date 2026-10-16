"""
CRIME DNA — Behavioral Novelty & Anomaly Analysis Service

Evaluates a user-submitted incident's 70-dimensional Behavioral DNA vector
against empirical historical patterns using Phase 9 dual-paradigm detection:
1. Geometric spherical centroid distance on the unit hypersphere
2. Isolation Forest structural tree depth isolation score
3. Calibrated empirical quantile thresholds (p95: 0.4363, p99: 0.5985, p99.9: 0.7383)

Enforces strict ethical non-offender attribution guidelines:
- Evaluates purely behavioral combinations within the historical dataset.
- Absolutely prohibits labels such as "suspicious person", "dangerous person",
  "criminal person", "likely offender", "future crime", or "high-risk individual".
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np

logger = logging.getLogger("CRIME_DNA_NOVELTY_SERVICE")

# Documented empirical thresholds calibrated on the 220,663 incident corpus
EMPIRICAL_NOVELTY_THRESHOLDS = {
    "moderate_novelty_p95": 0.4363,   # Top 5% behavioral divergence
    "high_outlier_p99": 0.5985,        # Top 1% behavioral divergence
    "extreme_outlier_p999": 0.7383     # Top 0.1% extreme behavioral divergence
}

# Mapping of raw feature names to human-readable behavioral factors
FEATURE_TO_FACTOR_NAME = {
    "time_is_night": "Nighttime Execution",
    "time_is_weekend": "Weekend Timing",
    "time_hour_sin": "Hour of Day Cyclical Timing (Sin)",
    "time_hour_cos": "Hour of Day Cyclical Timing (Cos)",
    "time_month_sin": "Calendar Month Seasonality (Sin)",
    "time_month_cos": "Calendar Month Seasonality (Cos)",
    "time_weekday_sin": "Day of Week Cycle (Sin)",
    "time_weekday_cos": "Day of Week Cycle (Cos)",
    "crime_against_person": "Direct Interpersonal Violence Focus",
    "crime_against_property": "Direct Property Infiltration Focus",
    "crime_against_society": "Public Order & Societal Dimension",
    "crime_against_person_property": "Compound Person-Property Interaction",
    "crime_against_person_society": "Compound Person-Societal Interaction",
    "crime_against_property_society": "Compound Property-Societal Interaction",
    "crime_against_person_property_society": "Tri-Domain Crime Interaction",
    "has_weapon": "Weapon Utilization",
    "is_multi_weapon": "Multiple Weapon Arsenal",
    "weapon_count_scaled": "Weapon Quantity",
    "weapon_types_count_scaled": "Weapon Diversity",
    "has_injury": "Physical Injury Infliction",
    "injury_record_count_scaled": "Injury Severity/Count",
    "has_property": "Property Involvement",
    "has_stolen_property": "Stolen Property Occurrence",
    "property_value_log_scaled": "High-Value Economic Impact",
    "property_record_count_scaled": "Property Item Multiplicity",
    "stolen_count_scaled": "Stolen Item Volume",
    "is_cargo_theft": "Commercial Cargo/Freight Interception",
    "victim_count_scaled": "Multiple Victims Targeted",
    "is_multi_victim": "Multi-Victim Interaction",
    "victim_avg_age_scaled": "Victim Age Demographic",
    "victim_age_known": "Known Victim Demographic",
    "victim_sexes_count_scaled": "Victim Gender Diversity",
    "victim_types_count_scaled": "Victim Institutional Types",
    "offender_count_scaled": "Offender Group Size",
    "is_co_offender": "Co-Offender Coordination",
    "offender_avg_age_scaled": "Offender Age Demographic",
    "offender_age_known": "Known Offender Characteristics",
    "has_relationship": "Known Interpersonal Relationship",
    "relationship_count_scaled": "Relationship Complexity",
    "has_drug": "Narcotics Connection",
    "suspected_drug_count_scaled": "Drug Type Multiplicity",
    "estimated_drug_quantity_log_scaled": "Commercial Drug Volume",
    "has_criminal_activity": "Associated Criminal Enterprise",
    "criminal_activity_count_scaled": "Criminal Activity Breadth",
    "has_arrest_on_scene": "On-Scene Apprehension",
    "arrest_count_scaled": "Arrest Magnitude",
    "is_attempted": "Attempted vs Completed Dynamic",
    "location_count_scaled": "Multi-Location Incident Scope",
    "population_log_scaled": "Urban Population Density Setting",
    "agency_is_state_police": "Jurisdictional Agency Context"
}


class BehavioralNoveltyService:
    """
    Evaluates incident Behavioral DNA against historical patterns for pattern fit and novelty.
    """

    def __init__(self):
        self.thresholds = EMPIRICAL_NOVELTY_THRESHOLDS

    def evaluate_novelty(
        self,
        norm_vec: np.ndarray,
        centroid_vec: np.ndarray,
        cl_id: int,
        cl_name: str,
        input_data: Dict[str, Any],
        state: Any
    ) -> Dict[str, Any]:
        """
        Determines Behavioral Pattern Fit, Novelty tier, unusual status, and factor deviations.

        Args:
            norm_vec: Unit L2-normalized 70D Behavioral DNA vector.
            centroid_vec: Centroid vector of the nearest cluster archetype.
            cl_id: Matched cluster archetype ID (0-7).
            cl_name: Matched cluster archetype name.
            input_data: User-submitted incident payload.
            state: ApplicationState with loaded IsolationForest and feature registries.

        Returns:
            Structured dictionary with pattern fit, novelty score, warning banners, and factors.
        """
        # Ensure unit normalization
        v_norm = np.linalg.norm(norm_vec)
        unit_vec = norm_vec / (v_norm if v_norm > 0 else 1.0)

        c_norm = np.linalg.norm(centroid_vec)
        cent_unit = centroid_vec / (c_norm if c_norm > 0 else 1.0)

        # 1. Geometric distance on unit hypersphere
        cos_to_cent = float(np.dot(unit_vec, cent_unit))
        centroid_dist = max(0.0, 1.0 - cos_to_cent)

        # 2. Structural Isolation Forest score (if available)
        norm_if_score = centroid_dist
        raw_if_score = None
        if getattr(state, "isolation_forest", None) is not None:
            try:
                norm_matrix_query = unit_vec.reshape(1, -1)
                raw_if = float(state.isolation_forest.decision_function(norm_matrix_query)[0])
                raw_if_score = round(raw_if, 4)
                # Calibrate Isolation Forest score: negative decision function -> high isolation
                norm_if_score = max(0.0, min(1.0, 0.5 - (raw_if * 1.5)))
            except Exception as e:
                logger.warning(f"Error computing Isolation Forest score: {e}")
                norm_if_score = centroid_dist

        # 3. Dual-Paradigm Composite Novelty Score
        composite_novelty = round(0.5 * centroid_dist + 0.5 * norm_if_score, 4)

        # 4. Empirical Quantile Tier Classification
        th_mod = self.thresholds["moderate_novelty_p95"]
        th_high = self.thresholds["high_outlier_p99"]
        th_ext = self.thresholds["extreme_outlier_p999"]

        if composite_novelty >= th_ext:
            novelty_tier = "Extreme Behavioral Outlier"
            percentile_desc = "Top 0.1% Extreme Novelty"
            is_novel = True
            is_unusual = True
        elif composite_novelty >= th_high:
            novelty_tier = "High Behavioral Outlier"
            percentile_desc = "Top 1% Behavioral Divergence"
            is_novel = True
            is_unusual = True
        elif composite_novelty >= th_mod:
            novelty_tier = "Moderate Behavioral Novelty"
            percentile_desc = "Top 5% Behavioral Divergence"
            is_novel = True
            is_unusual = True
        else:
            novelty_tier = "Standard Behavioral Pattern"
            percentile_desc = "Baseline Typical Profile (Bottom 95%)"
            is_novel = False
            is_unusual = False

        # 5. Neutral Label Classification (Part H)
        # Options: Commonly Observed Combination, Less Common Combination, Unusual Combination, Insufficient Information
        # Check for insufficient information (e.g. less than 2 valid features provided or explicitly marked)
        valid_input_count = sum(1 for v in input_data.values() if v is not None and str(v).strip() != "")
        if valid_input_count <= 2:
            neutral_label = "Insufficient Information"
            neutral_label_desc = "Too few observed incident fields were provided to reliably assess pattern novelty."
        elif composite_novelty >= th_high:
            neutral_label = "Unusual Combination"
            neutral_label_desc = "This observed feature combination diverges notably from common patterns in historical reference data."
        elif composite_novelty >= th_mod:
            neutral_label = "Less Common Combination"
            neutral_label_desc = "This observed feature combination appears occasionally in historical data with noticeable behavioral variations."
        else:
            neutral_label = "Commonly Observed Combination"
            neutral_label_desc = "This observed feature combination is frequently represented among standard baseline historical incidents."

        # 6. Behavioral Pattern Fit (Inverse of Behavioral Novelty)
        # Bounded between 0.0 and 1.0 (or percentage 0.0% to 100.0%)
        pattern_fit_score = round(max(0.0, min(1.0, 1.0 - composite_novelty)), 4)
        pattern_fit_pct = round(pattern_fit_score * 100.0, 1)

        if not is_unusual:
            pattern_fit_level = "High Fit"
            pattern_fit_summary = "Strong alignment with historical behavioral archetype."
        elif novelty_tier == "Moderate Behavioral Novelty":
            pattern_fit_level = "Moderate Fit"
            pattern_fit_summary = "Moderate alignment with historical behavioral archetype with identifiable divergences."
        else:
            pattern_fit_level = "Low Fit (Atypical Combination)"
            pattern_fit_summary = "Atypical behavioral combination showing marked divergence from historical archetypes."

        pattern_fit = {
            "fit_score": pattern_fit_score,
            "fit_percentage": pattern_fit_pct,
            "fit_level": pattern_fit_level,
            "fit_summary": pattern_fit_summary,
            "cosine_alignment_to_archetype_pct": round(max(0.0, min(100.0, cos_to_cent * 100.0)), 1)
        }

        # 7. Novelty Warning Banner Phrasing
        if is_unusual:
            banner_title = "⚠️ NOVEL BEHAVIORAL PATTERN"
            banner_message = (
                "This incident contains a behavioral combination that does not closely match "
                "the major patterns learned from the historical dataset."
            )
        else:
            banner_title = "STANDARD BEHAVIORAL PATTERN"
            banner_message = (
                "This incident contains behavioral characteristics consistent with major "
                "patterns learned from the historical dataset."
            )

        # 8. Identify Most Unusual Supported Behavioral Factors
        diffs = unit_vec - cent_unit
        abs_diffs = np.abs(diffs)
        sorted_indices = np.argsort(-abs_diffs)

        unusual_behavioral_factors = []
        unusual_features_legacy = []

        feature_names = getattr(state, "feature_names", [])

        for f_idx in sorted_indices[:6]:
            if f_idx >= len(feature_names):
                continue

            feat_name = feature_names[f_idx]
            delta = float(diffs[f_idx])
            inc_val = float(unit_vec[f_idx])
            cent_val = float(cent_unit[f_idx])

            # Filter for meaningful deviations
            if abs(delta) >= 0.08:
                direction = "Elevated" if delta > 0 else "Suppressed"
                factor_label = FEATURE_TO_FACTOR_NAME.get(feat_name, feat_name.replace("_", " ").title())

                explanation = (
                    f"{direction} {factor_label.lower()} compared to {cl_name} baseline "
                    f"(actual: {inc_val:.2f}, baseline: {cent_val:.2f}, delta: {delta:+.2f})"
                )

                factor_item = {
                    "feature_name": feat_name,
                    "factor_name": factor_label,
                    "incident_value": round(inc_val, 3),
                    "cluster_baseline_value": round(cent_val, 3),
                    "deviation_delta": round(delta, 3),
                    "direction": direction,
                    "explanation": explanation
                }
                unusual_behavioral_factors.append(factor_item)

                # Legacy structure for backward compatibility
                unusual_features_legacy.append({
                    "feature_name": feat_name,
                    "incident_value": round(inc_val, 3),
                    "cluster_centroid_value": round(cent_val, 3),
                    "deviation_delta": round(delta, 3),
                    "direction": direction,
                    "explanation": f"{direction} relative to {cl_name} baseline ({direction.lower()} by {abs(delta):.2f})"
                })

        # 9. Strict Ethical Non-Offender Attribution Advisory
        ethical_advisory = (
            "Based on patterns learned from historical incidents. "
            "CRIME DNA analyzes behavioral patterns in historical incident data. "
            "Similarity or novelty does not establish offender identity, guilt, or causation. "
            "Novelty evaluation reflects the statistical rarity of this novel behavioral combination "
            "relative to the historical reference dataset. It does not evaluate individual criminality, "
            "person dangerousness, or future risk."
        )

        data_limitations = (
            "Evaluated against 220,663 baseline incidents from the 2024 NIBRS reference dataset. "
            "Statistical novelty measures pattern frequency in historical reporting, not offender dangerousness or future criminality."
        )

        method_used = "Spherical Distance to Nearest Cluster Centroid + Isolation Forest Anomaly Score"

        return {
            # Core user-facing sections
            "neutral_label": neutral_label,
            "neutral_label_description": neutral_label_desc,
            "method_used": method_used,
            "data_limitations": data_limitations,
            "observed_features_contributing": unusual_behavioral_factors,
            "behavioral_pattern_fit": pattern_fit,
            "novelty_score": composite_novelty,
            "novelty_tier": novelty_tier,
            "percentile_description": percentile_desc,
            "is_novel": is_novel,
            "is_unusual": is_unusual,
            "banner_title": banner_title,
            "banner_message": banner_message,
            "unusual_behavioral_factors": unusual_behavioral_factors,
            "nearest_cluster_id": cl_id,
            "nearest_cluster_name": cl_name,
            "distance_to_nearest_cluster": round(centroid_dist, 4),
            "isolation_forest_raw_score": raw_if_score,
            "thresholds": self.thresholds,
            "ethical_advisory": ethical_advisory,

            # Backwards-compatible fields preserved for existing consumers
            "unusual_features": unusual_features_legacy
        }


# Global singleton instance
novelty_service = BehavioralNoveltyService()
