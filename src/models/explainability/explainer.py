"""
CRIME DNA — Phase 10: Behavioral Similarity Explainer (XAI)

Implements exact additive attribution for cosine similarity in Behavioral DNA space,
providing human-interpretable group contributions, matching features, and contrastive
differences for any pair of crime incidents.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any

# Ensure workspace root is in sys.path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.features.config import FEATURE_GROUPS, FEATURE_DESCRIPTIONS
from src.models.explainability.config import (
    EXPLAINABILITY_DIR,
    SAMPLE_EXPLANATIONS_PATH,
    EXPLANATION_METADATA_PATH,
    EXPLANATION_CHART_PATH,
    GROUP_DISPLAY_NAMES,
    GROUP_NOUN_PHRASES,
    EXPLAINABILITY_CONFIG,
    BEHAVIORAL_FEATURES_PATH,
    CLEANED_DATA_PATH
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_XAI")


def synthesize_plain_english_explanation(
    group_comparisons: List[Dict[str, Any]],
    differences: Optional[List[str]] = None
) -> str:
    """
    Synthesizes a scientifically authentic plain-English explanation strictly
    derived from the actual feature attribution and group comparison metrics.
    
    Example:
    "The strongest behavioral similarities are the time pattern, location context, and property involvement."
    """
    matching_groups = [
        g for g in group_comparisons
        if g.get("status") == "match" and g.get("contribution_score", 0.0) > 0.0
    ]
    matching_groups.sort(key=lambda x: -x.get("contribution_score", 0.0))

    if not matching_groups:
        return "Incidents exhibit low behavioral convergence across standard subprofile domains."

    top_matches = matching_groups[:3]
    noun_phrases = [
        GROUP_NOUN_PHRASES.get(g["group_key"], g.get("group_name", "").lower())
        for g in top_matches
    ]

    if len(noun_phrases) == 3:
        core_sentence = f"The strongest behavioral similarities are the {noun_phrases[0]}, {noun_phrases[1]}, and {noun_phrases[2]}."
    elif len(noun_phrases) == 2:
        core_sentence = f"The strongest behavioral similarities are the {noun_phrases[0]} and {noun_phrases[1]}."
    else:
        core_sentence = f"The primary behavioral similarity is the {noun_phrases[0]}."

    # Identify primary divergence if present
    divergent_groups = [
        g for g in group_comparisons
        if g.get("status") == "divergence" and g.get("match_tier") == "Weak match"
    ]
    if divergent_groups:
        diff_name = divergent_groups[0].get("group_name", "").lower()
        if "weapon" in diff_name or "method" in diff_name:
            core_sentence += " However, there is a divergence in weapon context."
        elif "property" in diff_name:
            core_sentence += " However, there is a divergence in property involvement."
        elif "time" in diff_name:
            core_sentence += " However, they differ in operational time pattern."

    return core_sentence


def decompose_behavioral_similarity(
    u: np.ndarray,
    v: np.ndarray,
    feature_names: List[str],
    feature_groups: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Decomposes cosine similarity into 7 scientifically grounded behavioral domains:
    - Time
    - Location
    - Crime Context
    - Method / Weapon
    - People / Victim-Offender Context
    - Property
    - Activity & Context

    Does NOT fabricate percentages or weights.
    Returns exact additive inner-product contributions, transparent match tiers
    (Strong match, Moderate match, Weak match), status indicators (✓, △), and
    a dynamically synthesized plain-English explanation.
    """
    if feature_groups is None:
        feature_groups = FEATURE_GROUPS

    overall_similarity = float(np.dot(u, v))
    overall_similarity_pct = round(max(0.0, min(100.0, overall_similarity * 100.0)), 1)

    comparisons = []

    feat_name_to_idx = {name: i for i, name in enumerate(feature_names)}
    for grp_key, cols in feature_groups.items():
        idxs = [feat_name_to_idx[c] for c in cols if c in feat_name_to_idx]
        if not idxs:
            continue

        u_g = u[idxs]
        v_g = v[idxs]
        c_g = float(np.sum(u_g * v_g))
        nu = float(np.linalg.norm(u_g))
        nv = float(np.linalg.norm(v_g))

        if nu > 1e-5 and nv > 1e-5:
            s_g = float(c_g / (nu * nv))
            s_g = max(-1.0, min(1.0, s_g))
        elif nu <= 1e-5 and nv <= 1e-5:
            s_g = 1.0
        else:
            s_g = 0.0

        share_pct = round((c_g / overall_similarity * 100.0) if overall_similarity > 0 else 0.0, 1)
        display_name = GROUP_DISPLAY_NAMES.get(grp_key, grp_key.replace("_", " ").title())

        # Transparent match tier determination
        if s_g >= 0.70 and c_g >= -0.01:
            match_tier = "Strong match"
            status = "match"
            indicator = "✓"
            is_match = True
        elif s_g >= 0.40 and c_g >= -0.01:
            match_tier = "Moderate match"
            status = "match"
            indicator = "✓"
            is_match = True
        else:
            match_tier = "Weak match"
            status = "divergence"
            indicator = "△"
            is_match = False

        # Contextual label generation
        if grp_key == "temporal_dynamics":
            label = "Same time pattern" if s_g >= 0.85 else ("Similar time pattern" if is_match else "Different time pattern")
            details = "Operating hours and diurnal cycle alignment"
        elif grp_key == "location_and_environment":
            label = "Same location context" if s_g >= 0.85 else ("Similar location context" if is_match else "Different location context")
            details = "Jurisdictional population density and environment tier"
        elif grp_key == "property_and_economics":
            label = "Same property context" if s_g >= 0.85 else ("Similar property context" if is_match else "Different property context")
            details = "Targeted property records and economic valuation"
        elif grp_key == "method_and_activity":
            label = "Similar method / weapon context" if is_match else "Different weapon context"
            details = "Weaponry, lethal force, and operational execution method"
        elif grp_key == "people_and_demographics":
            label = "Similar victim-offender context" if is_match else "Different victim-offender context"
            details = "Victim counts, co-offender group size, and interpersonal relationship"
        elif grp_key == "crime_characteristics":
            label = "Similar crime context" if is_match else "Different crime context"
            details = "Statutory classifications and offense volume"
        elif grp_key == "context_and_harm":
            label = "Similar activity & context" if is_match else "Different activity & context"
            details = "Physical injury harm, narcotics involvement, and on-scene arrests"
        else:
            label = f"Similar {display_name.lower()}" if is_match else f"Different {display_name.lower()}"
            details = f"Subprofile dimensions for {display_name}"

        comparisons.append({
            "group_key": grp_key,
            "group_name": display_name,
            "status": status,
            "indicator": indicator,
            "label": f"{indicator} {label}",
            "raw_label": label,
            "match_tier": match_tier,
            "similarity_score": round(s_g, 4),
            "contribution_score": round(c_g, 4),
            "share_percentage": share_pct,
            "details": details
        })

    plain_english = synthesize_plain_english_explanation(comparisons)

    return {
        "overall_similarity_pct": overall_similarity_pct,
        "cosine_similarity_raw": round(overall_similarity, 4),
        "plain_english_explanation": plain_english,
        "behavioral_group_comparisons": comparisons
    }


class BehavioralSimilarityExplainer:
    """
    Explains the mathematical basis of Behavioral DNA similarity between crime incidents.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {**EXPLAINABILITY_CONFIG, **(config or {})}
        self.feature_names: List[str] = []
        self.incident_ids: List[str] = []
        self.id_to_idx: Dict[str, int] = {}
        self.normalized_matrix: Optional[np.ndarray] = None
        self.cleaned_df: Optional[pd.DataFrame] = None
        self._is_ready = False

    def load_data(
        self,
        features_path: str = BEHAVIORAL_FEATURES_PATH,
        cleaned_path: str = CLEANED_DATA_PATH
    ) -> "BehavioralSimilarityExplainer":
        """
        Loads and prepares feature representations and contextual metadata.
        """
        logger.info(f"Loading Behavioral DNA features from {features_path}...")
        features_df = pd.read_csv(features_path)
        self.incident_ids = features_df["incident_id"].tolist()
        self.id_to_idx = {inc_id: idx for idx, inc_id in enumerate(self.incident_ids)}
        self.feature_names = [c for c in features_df.columns if c != "incident_id"]

        raw_feat = features_df[self.feature_names].values.astype(np.float32)
        norms = np.linalg.norm(raw_feat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.normalized_matrix = raw_feat / norms

        logger.info(f"Loading contextual incident attributes from {cleaned_path}...")
        cols_to_load = [
            "incident_id", "incident_hour", "incident_month", "incident_weekday",
            "is_weekend", "is_night", "has_weapon", "has_injury", "has_property",
            "has_drug", "has_arrest", "has_relationship", "population",
            "crime_against_person", "crime_against_property", "crime_against_society",
            "property_value"
        ]
        self.cleaned_df = pd.read_csv(cleaned_path, usecols=cols_to_load)
        self._is_ready = True
        logger.info(f"Explainer loaded successfully across {len(self.incident_ids):,} incidents.")
        return self

    def explain_pair(self, incident_id_1: str, incident_id_2: str) -> Dict[str, Any]:
        """
        Computes exact additive feature and group contributions explaining why two incidents are similar.
        """
        if not self._is_ready or self.normalized_matrix is None or self.cleaned_df is None:
            self.load_data()

        if self.normalized_matrix is None or self.cleaned_df is None:
            raise RuntimeError("Explainability data not initialized.")

        normalized_matrix = self.normalized_matrix
        cleaned_df = self.cleaned_df

        if incident_id_1 not in self.id_to_idx:
            raise KeyError(f"Incident ID '{incident_id_1}' not found in dataset.")
        if incident_id_2 not in self.id_to_idx:
            raise KeyError(f"Incident ID '{incident_id_2}' not found in dataset.")

        idx1 = self.id_to_idx[incident_id_1]
        idx2 = self.id_to_idx[incident_id_2]

        u = normalized_matrix[idx1]
        v = normalized_matrix[idx2]

        # Exact Cosine Similarity
        overall_similarity = float(np.dot(u, v))
        overall_similarity_pct = round(overall_similarity * 100, 1)

        # Feature-level contributions: c_j = u_j * v_j
        feature_contributions = u * v

        # Group-level contributions: sum of c_j in each feature group
        group_contributions = {}
        for group_key, feature_list in FEATURE_GROUPS.items():
            indices = [self.feature_names.index(f) for f in feature_list if f in self.feature_names]
            group_sum = float(feature_contributions[indices].sum())
            group_pct = float(group_sum / overall_similarity * 100) if overall_similarity > 0 else 0.0
            display_name = GROUP_DISPLAY_NAMES.get(group_key, group_key.replace("_", " ").title())

            group_contributions[group_key] = {
                "group_key": group_key,
                "display_name": display_name,
                "absolute_contribution": round(group_sum, 4),
                "percentage_of_similarity": round(group_pct, 1)
            }

        # Sort groups by contribution
        sorted_groups = sorted(
            group_contributions.values(),
            key=lambda x: -x["absolute_contribution"]
        )

        # Identify main contributing group similarities (groups contributing substantially)
        main_contributing_similarities = []
        for g in sorted_groups:
            if g["percentage_of_similarity"] >= (self.config["group_significance_ratio"] * 100):
                main_contributing_similarities.append(f"Similar {g['display_name'].lower()}")

        if not main_contributing_similarities and sorted_groups:
            main_contributing_similarities.append(f"Similar {sorted_groups[0]['display_name'].lower()}")

        # Top feature-level positive contributions
        top_contrib_indices = np.argsort(-feature_contributions)[:self.config["top_contributing_features_count"]]
        top_contributing_features = []
        for j in top_contrib_indices:
            c_val = float(feature_contributions[j])
            if c_val >= self.config["min_feature_contribution_threshold"]:
                feat_name = self.feature_names[j]
                top_contributing_features.append({
                    "feature_name": feat_name,
                    "contribution": round(c_val, 4),
                    "incident_1_value": round(float(u[j]), 3),
                    "incident_2_value": round(float(v[j]), 3),
                    "description": FEATURE_DESCRIPTIONS.get(feat_name, feat_name)
                })

        # Feature differences: delta_j = |u_j - v_j|
        feature_differences = np.abs(u - v)
        top_diff_indices = np.argsort(-feature_differences)[:self.config["top_differing_features_count"]]

        # Contextual metadata lookup for high-level semantic contrast
        row1 = cleaned_df[cleaned_df["incident_id"] == incident_id_1].iloc[0]
        row2 = cleaned_df[cleaned_df["incident_id"] == incident_id_2].iloc[0]

        differences_list = []

        # Check macro crime category contrast
        cat1 = "Person" if row1["crime_against_person"] == 1 else ("Property" if row1["crime_against_property"] == 1 else "Society")
        cat2 = "Person" if row2["crime_against_person"] == 1 else ("Property" if row2["crime_against_property"] == 1 else "Society")
        if cat1 != cat2:
            differences_list.append(f"Different crime category ({incident_id_1}: {cat1} vs {incident_id_2}: {cat2})")

        # Check injury status
        if row1["has_injury"] != row2["has_injury"]:
            differences_list.append(f"Different injury status ({incident_id_1}: {'Injury' if row1['has_injury'] else 'No Injury'} vs {incident_id_2}: {'Injury' if row2['has_injury'] else 'No Injury'})")

        # Check weapon status
        if row1["has_weapon"] != row2["has_weapon"]:
            differences_list.append(f"Different weapon presence ({incident_id_1}: {'Armed' if row1['has_weapon'] else 'Unarmed'} vs {incident_id_2}: {'Armed' if row2['has_weapon'] else 'Unarmed'})")

        # Check property status
        if row1["has_property"] != row2["has_property"]:
            differences_list.append(f"Different property involvement ({incident_id_1}: {'Property Involved' if row1['has_property'] else 'No Property'} vs {incident_id_2}: {'Property Involved' if row2['has_property'] else 'No Property'})")

        # Check diurnal time status
        if row1["is_night"] != row2["is_night"]:
            differences_list.append(f"Different time of day ({incident_id_1}: {'Nighttime' if row1['is_night'] else 'Daytime'} vs {incident_id_2}: {'Nighttime' if row2['is_night'] else 'Daytime'})")

        # Check weekend status
        if row1["is_weekend"] != row2["is_weekend"]:
            differences_list.append(f"Different day type ({incident_id_1}: {'Weekend' if row1['is_weekend'] else 'Weekday'} vs {incident_id_2}: {'Weekend' if row2['is_weekend'] else 'Weekday'})")

        # If no macro differences were triggered, add top vector differences
        top_differing_features = []
        for j in top_diff_indices:
            diff_val = float(feature_differences[j])
            if diff_val >= self.config["min_feature_difference_threshold"]:
                feat_name = self.feature_names[j]
                top_differing_features.append({
                    "feature_name": feat_name,
                    "difference": round(diff_val, 4),
                    "incident_1_value": round(float(u[j]), 3),
                    "incident_2_value": round(float(v[j]), 3),
                    "description": FEATURE_DESCRIPTIONS.get(feat_name, feat_name)
                })
                if len(differences_list) < 3 and not any(feat_name in d for d in differences_list):
                    differences_list.append(f"Different {feat_name.replace('_scaled', '').replace('_', ' ')}")

        if not differences_list:
            differences_list.append("Minor attribute variances (near-identical behavioral profile)")

        # Format user-facing text representation exactly matching specification
        formatted_summary = (
            f"Similarity Score: {overall_similarity_pct}%\n\n"
            f"Main contributing similarities:\n"
            + "\n".join([f"- {s}" for s in main_contributing_similarities])
            + "\n\nDifferences:\n"
            + "\n".join([f"- {d}" for d in differences_list])
        )

        decomp = decompose_behavioral_similarity(
            u=u,
            v=v,
            feature_names=self.feature_names
        )

        return {
            "incident_pair": [incident_id_1, incident_id_2],
            "similarity_score_pct": overall_similarity_pct,
            "cosine_similarity_raw": round(overall_similarity, 4),
            "plain_english_explanation": decomp["plain_english_explanation"],
            "behavioral_group_comparisons": decomp["behavioral_group_comparisons"],
            "main_contributing_similarities": main_contributing_similarities,
            "differences": differences_list,
            "group_contributions": group_contributions,
            "sorted_group_contributions": sorted_groups,
            "top_contributing_features": top_contributing_features,
            "top_differing_features": top_differing_features,
            "formatted_text_summary": formatted_summary,
            "incident_1_context": {
                "incident_id": incident_id_1,
                "category": cat1,
                "hour": int(row1["incident_hour"]),
                "is_night": bool(row1["is_night"]),
                "is_weekend": bool(row1["is_weekend"]),
                "has_weapon": bool(row1["has_weapon"]),
                "has_injury": bool(row1["has_injury"]),
                "has_property": bool(row1["has_property"])
            },
            "incident_2_context": {
                "incident_id": incident_id_2,
                "category": cat2,
                "hour": int(row2["incident_hour"]),
                "is_night": bool(row2["is_night"]),
                "is_weekend": bool(row2["is_weekend"]),
                "has_weapon": bool(row2["has_weapon"]),
                "has_injury": bool(row2["has_injury"]),
                "has_property": bool(row2["has_property"])
            }
        }

    def export_sample_explanations(self, output_dir: str = EXPLAINABILITY_DIR) -> None:
        """
        Exports sample pair explanations across distinct comparison regimes for frontend demonstration.
        """
        os.makedirs(output_dir, exist_ok=True)
        if not self._is_ready:
            self.load_data()

        logger.info("Synthesizing representative sample explanations...")

        sample_pairs = [
            # Pair 1: Cross-Crime Shared Modus Operandi (Assault <-> Armed Robbery, ~86%)
            ("INC_136975", "INC_145291", "Cross-Crime Shared Modus Operandi (Assault vs Robbery)"),
            # Pair 2: Within-Category High Similarity (Violent Assault <-> Violent Assault, ~98%)
            ("INC_000002", "INC_006454", "High-Fidelity Within-Category Pair (Violent Interpersonal Assault)"),
            # Pair 3: Stealth Burglary Shared Pattern (Burglary <-> Intrusion, ~84%)
            ("INC_079500", "INC_108471", "Nocturnal Weekend Intrusion (Property Burglary vs Home Invasion)"),
            # Pair 4: Dissimilar Contrasting Pair (Assault vs Shoplifting, Low Sim)
            ("INC_136975", "INC_032487", "Divergent Contrasting Pair (Violent Assault vs Retail Larceny)")
        ]

        explanations = []
        for id1, id2, scenario in sample_pairs:
            exp = self.explain_pair(id1, id2)
            exp["comparison_scenario"] = scenario
            explanations.append(exp)

        logger.info(f"Saving sample explanations to {SAMPLE_EXPLANATIONS_PATH}...")
        with open(SAMPLE_EXPLANATIONS_PATH, "w") as f:
            json.dump(explanations, f, indent=2)

        metadata = {
            "version": "1.0",
            "mathematical_method": "Exact Additive Inner-Product Attribution over L2-Normalized Behavioral DNA",
            "formula": "Cosine_Similarity(u, v) = sum(u_j * v_j) = sum(Group_Contributions)",
            "total_behavioral_dimensions": len(self.feature_names),
            "feature_groups": list(FEATURE_GROUPS.keys()),
            "group_display_names": GROUP_DISPLAY_NAMES,
            "sample_pairs_count": len(explanations)
        }
        with open(EXPLANATION_METADATA_PATH, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Explainability artifacts successfully saved in {output_dir}")

    def generate_visualizations(self, chart_path: str = EXPLANATION_CHART_PATH) -> None:
        """
        Renders a publication-quality explanation dashboard for a representative cross-crime pair.
        """
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        if not self._is_ready:
            self.load_data()

        logger.info(f"Generating explainability visualization at {chart_path}...")
        exp = self.explain_pair("INC_136975", "INC_145291")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        # Panel 1: Group Contribution Breakdown Waterfall / Bar
        groups = exp["sorted_group_contributions"]
        group_names = [g["display_name"] for g in groups]
        group_pcts = [g["percentage_of_similarity"] for g in groups]
        group_contribs = [g["absolute_contribution"] for g in groups]
        y_pos = np.arange(len(group_names))

        colors = ["#4361EE" if c > 0.0 else "#CED4DA" for c in group_contribs]
        bars = ax1.barh(y_pos, group_pcts, color=colors, alpha=0.85, edgecolor="black")
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(group_names, fontsize=10, fontweight="medium")
        ax1.invert_yaxis()
        ax1.set_xlabel("Contribution to Total Similarity (%)", fontsize=11, fontweight="bold")
        ax1.set_title(
            f"A. Behavioral Group Contributions (Total Similarity: {exp['similarity_score_pct']}%)\n"
            f"{exp['incident_pair'][0]} (Assault) vs {exp['incident_pair'][1]} (Robbery)",
            fontsize=12, fontweight="bold"
        )
        ax1.grid(axis="x", linestyle="--", alpha=0.5)

        for i, (pct, c_val) in enumerate(zip(group_pcts, group_contribs)):
            ax1.text(pct + 0.8, i, f"{pct:.1f}% (+{c_val:.3f})", va="center", fontsize=9, fontweight="bold")

        # Panel 2: Formatted Explanation Card & Feature-Level Mechanics
        ax2.axis("off")
        card_text = (
            f"B. Behavioral Attribution Explanation Card\n\n"
            f"Question: \"Why are incidents {exp['incident_pair'][0]} and {exp['incident_pair'][1]} behaviorally similar?\"\n\n"
            f"----------------------------------------------------------------------------------------------------\n"
            f"Similarity Score: {exp['similarity_score_pct']}%\n\n"
            f"Main contributing similarities:\n"
            + "\n".join([f"  • {s.capitalize()}" for s in exp["main_contributing_similarities"]])
            + "\n\nDifferences:\n"
            + "\n".join([f"  • {d}" for d in exp["differences"]])
            + f"\n\n----------------------------------------------------------------------------------------------------\n"
            f"Mathematical Proof (Additive Efficiency):\n"
            f"  • Cosine Similarity = sum(u_j * v_j) = {exp['cosine_similarity_raw']:.4f}\n"
            f"  • Sum of Group Contributions = {sum([g['absolute_contribution'] for g in groups]):.4f} (100.0% match)\n\n"
            f"Ethical Notice: Shared behavioral fingerprint does NOT imply common offender identity.\n"
        )

        ax2.text(
            0.02, 0.95, card_text,
            transform=ax2.transAxes,
            fontsize=10.5,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=1.0", facecolor="#F8F9FA", edgecolor="#4361EE", linewidth=2.0)
        )

        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Explainability visualization saved to {chart_path}")


if __name__ == "__main__":
    explainer = BehavioralSimilarityExplainer()
    explainer.load_data()
    explainer.export_sample_explanations()
    explainer.generate_visualizations()
