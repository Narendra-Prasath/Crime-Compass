"""
CRIME DNA — Phase 7: Cross-Crime Pattern Analyzer

Discovers, quantifies, and explains latent behavioral patterns that transcend
statutory crime classifications, providing empirical evidence of shared modus
operandi across legally distinct crime categories.
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
from sklearn.metrics.pairwise import cosine_similarity

from src.features.config import FEATURE_GROUPS
from src.models.cross_crime.config import (
    CROSS_CRIME_DIR,
    PATTERNS_JSON_PATH,
    SUMMARY_JSON_PATH,
    MATRIX_CHART_PATH,
    CROSS_CRIME_CONFIG,
    CRIME_CATEGORY_MAPPING,
    CATEGORY_SHORT_NAMES,
    BEHAVIORAL_FEATURES_PATH,
    CLUSTER_LABELS_PATH,
    CLEANED_DATA_PATH
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_CROSS_CRIME")


class CrossCrimeAnalyzer:
    """
    Analyzes cross-category behavioral convergence across incidents and clusters.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {**CROSS_CRIME_CONFIG, **(config or {})}
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.summary: List[Dict[str, Any]] = []
        self.category_names = list(CRIME_CATEGORY_MAPPING.keys())

    def fit(
        self,
        features_path: str = BEHAVIORAL_FEATURES_PATH,
        labels_path: str = CLUSTER_LABELS_PATH,
        cleaned_path: str = CLEANED_DATA_PATH
    ) -> "CrossCrimeAnalyzer":
        """
        Executes dynamic cross-crime pattern discovery across the corpus.
        """
        logger.info(f"Loading cluster labels from {labels_path}...")
        labels_df = pd.read_csv(labels_path)

        logger.info(f"Loading Behavioral DNA features from {features_path}...")
        features_df = pd.read_csv(features_path)

        logger.info(f"Loading cleaned incident attributes from {cleaned_path}...")
        cleaned_cols = [
            "incident_id", "incident_hour", "incident_weekday", "is_weekend", "is_night",
            "has_weapon", "has_injury", "has_property", "has_drug", "has_arrest",
            "has_relationship", "has_criminal_activity", "population"
        ] + self.category_names
        cleaned_df = pd.read_csv(cleaned_path, usecols=cleaned_cols)

        # Merge datasets
        merged = labels_df.merge(cleaned_df, on="incident_id")
        feature_cols = [c for c in features_df.columns if c != "incident_id"]

        # Ensure L2-normalized feature matrix
        raw_feat = features_df[feature_cols].values.astype(np.float32)
        norms = np.linalg.norm(raw_feat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_feat = raw_feat / norms

        # Determine standardized category label for each incident
        def extract_category_label(row: pd.Series) -> str:
            for cat_col in self.category_names:
                if row[cat_col] == 1:
                    return cat_col
            return "unknown"

        merged["raw_category"] = merged.apply(extract_category_label, axis=1)
        merged["category_name"] = merged["raw_category"].map(lambda x: CATEGORY_SHORT_NAMES.get(x, x))
        merged["category_full_desc"] = merged["raw_category"].map(lambda x: CRIME_CATEGORY_MAPPING.get(x, x))

        cluster_ids = sorted(merged["cluster_id"].unique())
        logger.info(f"Analyzing cross-crime patterns across {len(cluster_ids)} behavioral clusters...")

        self.patterns = {}
        self.summary = []

        for cl_id in cluster_ids:
            cl_mask = (merged["cluster_id"] == cl_id).values
            cl_df = merged[cl_mask]
            cl_name = cl_df["cluster_name"].iloc[0]
            n_incidents = len(cl_df)

            # Crime category distribution
            cat_counts = cl_df["category_name"].value_counts()
            dominant_category = cat_counts.index[0]
            dominant_count = int(cat_counts.iloc[0])
            cross_crime_count = n_incidents - dominant_count
            cross_crime_ratio = float(cross_crime_count / n_incidents)

            # Shannon Entropy & Simpson Diversity Index
            proportions = np.asarray(cat_counts.values, dtype=float) / n_incidents
            shannon_entropy = float(-np.sum(proportions * np.log(proportions + 1e-12)))
            simpson_diversity = float(1.0 - np.sum(proportions ** 2))

            # Categories meeting minimum threshold
            rep_cats = [
                cat for cat, cnt in cat_counts.items()
                if cnt >= self.config["min_category_incidents"]
            ]

            # Cross-Category Centroids & Pairwise Cosine Similarities
            cat_centroids = {}
            for cat in rep_cats:
                cat_mask = (cl_mask & (merged["category_name"] == cat)).values
                cat_centroids[cat] = normalized_feat[cat_mask].mean(axis=0)

            inter_category_sims: Dict[str, float] = {}
            sim_values = []
            for i, c1 in enumerate(rep_cats):
                for j, c2 in enumerate(rep_cats):
                    if i < j:
                        c1_vec = cat_centroids[c1].reshape(1, -1)
                        c2_vec = cat_centroids[c2].reshape(1, -1)
                        sim = float(cosine_similarity(c1_vec, c2_vec)[0, 0])
                        inter_category_sims[f"{c1} <-> {c2}"] = round(sim, 4)
                        sim_values.append(sim)

            avg_inter_cat_sim = float(np.mean(sim_values)) if sim_values else 1.0

            # Compute dominant behavioral metrics for this pattern
            dominant_behavior = {
                "crime_characteristics": {
                    "against_person_pct": round(float(cl_df["crime_against_person"].mean() * 100), 2),
                    "against_property_pct": round(float(cl_df["crime_against_property"].mean() * 100), 2),
                    "against_society_pct": round(float(cl_df["crime_against_society"].mean() * 100), 2),
                    "compound_categories_pct": round(float((cl_df["raw_category"].str.contains("___")).mean() * 100), 2)
                },
                "temporal_patterns": {
                    "nighttime_pct": round(float(cl_df["is_night"].mean() * 100), 2),
                    "weekend_pct": round(float(cl_df["is_weekend"].mean() * 100), 2),
                    "mean_hour": round(float(np.mean(cl_df["incident_hour"])), 1)
                },
                "location_patterns": {
                    "mean_population": int(np.median(cl_df["population"])),
                    "urban_environment": "Metropolitan Core" if float(np.median(cl_df["population"])) > 100000 else (
                        "Suburban / Mid-Size" if float(np.median(cl_df["population"])) > 25000 else "Small Municipality / Town"
                    )
                },
                "weapon_characteristics": {
                    "weapon_presence_pct": round(float(cl_df["has_weapon"].mean() * 100), 2)
                },
                "property_characteristics": {
                    "property_involvement_pct": round(float(cl_df["has_property"].mean() * 100), 2)
                },
                "people_patterns": {
                    "known_relationship_pct": round(float(cl_df["has_relationship"].mean() * 100), 2)
                },
                "context_and_harm": {
                    "physical_injury_pct": round(float(cl_df["has_injury"].mean() * 100), 2),
                    "drug_involvement_pct": round(float(cl_df["has_drug"].mean() * 100), 2),
                    "criminal_activity_pct": round(float(cl_df["has_criminal_activity"].mean() * 100), 2),
                    "on_scene_arrest_pct": round(float(cl_df["has_arrest"].mean() * 100), 2)
                }
            }

            # Select real exemplar incidents representing distinct crime categories
            exemplars = []
            for cat in rep_cats[:int(self.config["top_exemplars_per_category"])]:
                cat_indices = np.where(cl_mask & (merged["category_name"] == cat).values)[0]
                if len(cat_indices) == 0:
                    continue

                # Find exemplar closest to category centroid
                cat_vecs = normalized_feat[cat_indices]
                centroid = cat_centroids[cat].reshape(1, -1)
                dists = np.linalg.norm(cat_vecs - centroid, axis=1)
                best_idx = cat_indices[np.argmin(dists)]

                exemplar_row = merged.iloc[best_idx]
                exemplars.append({
                    "incident_id": str(exemplar_row["incident_id"]),
                    "crime_category": str(exemplar_row["category_name"]),
                    "category_description": str(exemplar_row["category_full_desc"]),
                    "incident_hour": int(exemplar_row["incident_hour"]),
                    "is_weekend": bool(exemplar_row["is_weekend"]),
                    "is_night": bool(exemplar_row["is_night"]),
                    "has_weapon": bool(exemplar_row["has_weapon"]),
                    "has_injury": bool(exemplar_row["has_injury"]),
                    "has_property": bool(exemplar_row["has_property"]),
                    "has_drug": bool(exemplar_row["has_drug"]),
                    "has_relationship": bool(exemplar_row["has_relationship"]),
                    "has_arrest": bool(exemplar_row["has_arrest"])
                })

            # Calculate pairwise exemplar similarity
            exemplar_pairwise_sims = {}
            if len(exemplars) >= 2:
                for i in range(len(exemplars)):
                    for j in range(i + 1, len(exemplars)):
                        idx_i = merged.index[merged["incident_id"] == exemplars[i]["incident_id"]][0]
                        idx_j = merged.index[merged["incident_id"] == exemplars[j]["incident_id"]][0]
                        vec_i = normalized_feat[idx_i].reshape(1, -1)
                        vec_j = normalized_feat[idx_j].reshape(1, -1)
                        sim = float(cosine_similarity(vec_i, vec_j)[0, 0])
                        pair_key = f"{exemplars[i]['incident_id']} ({exemplars[i]['crime_category']}) <-> {exemplars[j]['incident_id']} ({exemplars[j]['crime_category']})"
                        exemplar_pairwise_sims[pair_key] = round(sim, 4)

            # Compile cross-crime evidence
            evidence = {
                "categories_count": len(rep_cats),
                "shannon_entropy": round(shannon_entropy, 4),
                "simpson_diversity": round(simpson_diversity, 4),
                "cross_crime_incidents": cross_crime_count,
                "cross_crime_percentage": round(cross_crime_ratio * 100, 2),
                "avg_inter_category_cosine_similarity": round(avg_inter_cat_sim, 4),
                "shared_behavior_rationale": (
                    f"Despite originating from {len(rep_cats)} legally distinct statutory crime categories, "
                    f"incidents in this pattern share an average behavioral cosine similarity of {avg_inter_cat_sim:.3f}. "
                    f"They converge on identical environmental and modus operandi parameters: "
                    f"weapon presence rate = {dominant_behavior['weapon_characteristics']['weapon_presence_pct']}%, "
                    f"nighttime rate = {dominant_behavior['temporal_patterns']['nighttime_pct']}%, and "
                    f"bodily injury rate = {dominant_behavior['context_and_harm']['physical_injury_pct']}%."
                )
            }

            pattern_id = f"CCP_{cl_id:02d}"
            self.patterns[pattern_id] = {
                "pattern_id": pattern_id,
                "cluster_id": int(cl_id),
                "pattern_name": f"Cross-Crime: {cl_name}",
                "total_incidents": n_incidents,
                "categories_represented": [
                    {
                        "category_name": cat,
                        "incident_count": int(cnt),
                        "percentage": round(float(cnt / n_incidents) * 100, 2)
                    }
                    for cat, cnt in cat_counts.items()
                    if cnt >= self.config["min_category_incidents"]
                ],
                "dominant_behavioral_characteristics": dominant_behavior,
                "inter_category_similarities": inter_category_sims,
                "exemplar_incidents": exemplars,
                "exemplar_pairwise_similarities": exemplar_pairwise_sims,
                "cross_crime_evidence": evidence
            }

            self.summary.append({
                "pattern_id": pattern_id,
                "cluster_id": int(cl_id),
                "pattern_name": f"Cross-Crime: {cl_name}",
                "total_incidents": n_incidents,
                "cross_crime_incidents": cross_crime_count,
                "cross_crime_percentage": round(cross_crime_ratio * 100, 2),
                "distinct_categories_count": len(rep_cats),
                "primary_category": dominant_category,
                "secondary_categories": [c for c in rep_cats if c != dominant_category],
                "avg_inter_category_similarity": round(avg_inter_cat_sim, 4),
                "diversity_index": round(simpson_diversity, 4),
                "key_shared_traits": [
                    f"Nighttime: {dominant_behavior['temporal_patterns']['nighttime_pct']}%",
                    f"Weekend: {dominant_behavior['temporal_patterns']['weekend_pct']}%",
                    f"Weapon: {dominant_behavior['weapon_characteristics']['weapon_presence_pct']}%",
                    f"Injury: {dominant_behavior['context_and_harm']['physical_injury_pct']}%",
                    f"Arrest: {dominant_behavior['context_and_harm']['on_scene_arrest_pct']}%"
                ]
            })

        logger.info(f"Cross-Crime Pattern Analysis complete: {len(self.patterns)} patterns synthesized.")
        return self

    def export_machine_readable(self, output_dir: str = CROSS_CRIME_DIR) -> None:
        """
        Exports machine-readable JSON artifacts for frontend consumption.
        """
        os.makedirs(output_dir, exist_ok=True)
        patterns_path = os.path.join(output_dir, "cross_crime_patterns.json")
        summary_path = os.path.join(output_dir, "cross_crime_summary.json")

        logger.info(f"Exporting cross-crime patterns to {patterns_path}...")
        with open(patterns_path, "w") as f:
            json.dump(self.patterns, f, indent=2)

        logger.info(f"Exporting cross-crime summary to {summary_path}...")
        with open(summary_path, "w") as f:
            json.dump(self.summary, f, indent=2)

        logger.info(f"Artifacts successfully written to {output_dir}")

    def generate_visualizations(self, chart_path: str = MATRIX_CHART_PATH) -> None:
        """
        Generates publication-quality charts detailing cross-crime distribution and convergence.
        """
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        logger.info(f"Generating cross-crime visualization at {chart_path}...")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        # Subplot 1: Distribution of Crime Categories per Pattern
        pattern_names = [p["pattern_name"].replace("Cross-Crime: ", "") for p in self.summary]
        cross_counts = [p["cross_crime_incidents"] for p in self.summary]
        primary_counts = [p["total_incidents"] - p["cross_crime_incidents"] for p in self.summary]
        y_pos = np.arange(len(pattern_names))

        ax1.barh(y_pos, primary_counts, label="Plurality Category", color="#4361EE", alpha=0.85)
        ax1.barh(y_pos, cross_counts, left=primary_counts, label="Cross-Crime (Other Categories)", color="#F72585", alpha=0.85)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(pattern_names, fontsize=9)
        ax1.invert_yaxis()
        ax1.set_xlabel("Number of Incidents", fontsize=11, fontweight="bold")
        ax1.set_title("Cross-Category Crime Representation per Behavioral Cluster", fontsize=12, fontweight="bold")
        ax1.legend(loc="lower right")
        ax1.grid(axis="x", linestyle="--", alpha=0.5)

        for i in range(len(pattern_names)):
            cross_pct = (cross_counts[i] / (primary_counts[i] + cross_counts[i])) * 100
            ax1.text(
                primary_counts[i] + cross_counts[i] + 1500,
                i,
                f"{cross_counts[i]:,} cross-crime ({cross_pct:.1f}%)",
                va="center",
                fontsize=8,
                fontweight="semibold",
                color="#7209B7"
            )

        # Subplot 2: Cross-Category Inter-Similarity & Diversity
        similarities = [p["avg_inter_category_similarity"] for p in self.summary]
        diversities = [p["diversity_index"] for p in self.summary]

        ax2.scatter(similarities, diversities, s=[c / 100 for c in cross_counts], c="#7209B7", alpha=0.6, edgecolors="black", linewidth=1.5)
        ax2.set_xlabel("Average Inter-Category Cosine Similarity (Behavioral Convergence)", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Simpson's Category Diversity Index", fontsize=11, fontweight="bold")
        ax2.set_title("Behavioral Convergence vs Statutory Diversity (Bubble Size = Cross-Crime Vol)", fontsize=12, fontweight="bold")
        ax2.grid(True, linestyle="--", alpha=0.5)

        for i, txt in enumerate(pattern_names):
            ax2.annotate(
                f"P{i}: {txt[:18]}...",
                (similarities[i], diversities[i]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                fontweight="semibold"
            )

        plt.tight_layout()
        plt.savefig(chart_path, dpi=300)
        plt.close()
        logger.info(f"Visualization saved to {chart_path}")


if __name__ == "__main__":
    analyzer = CrossCrimeAnalyzer()
    analyzer.fit()
    analyzer.export_machine_readable()
    analyzer.generate_visualizations()
