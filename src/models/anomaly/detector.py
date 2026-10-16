"""
CRIME DNA — Phase 9: Behavioral Anomaly & Novelty Detector

Implements dual-paradigm unsupervised novelty detection combining geometric
cluster centroid distance on unit hypersphere with Isolation Forest structural
tree isolation, calibrated via empirical extreme value percentiles.
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
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

from src.models.anomaly.config import (
    ANOMALY_DIR,
    MODEL_PATH,
    SCORES_CSV_PATH,
    TOP_OUTLIERS_JSON_PATH,
    ANOMALY_SUMMARY_PATH,
    ANOMALY_CHART_PATH,
    ANOMALY_CONFIG,
    ANOMALY_TIER_LABELS,
    BEHAVIORAL_FEATURES_PATH,
    CLUSTER_MODEL_PATH,
    CLUSTER_LABELS_PATH,
    CLUSTER_PROFILES_PATH
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_ANOMALY")


class BehavioralAnomalyDetector:
    """
    Dual-paradigm unsupervised anomaly and novelty detector for Behavioral DNA vectors.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {**ANOMALY_CONFIG, **(config or {})}
        self.model: Optional[IsolationForest] = None
        self.feature_names: List[str] = []
        self.incident_ids: List[str] = []
        self.cluster_centroids: Optional[np.ndarray] = None
        self.cluster_names: Dict[int, str] = {}
        self.scores_df: Optional[pd.DataFrame] = None
        self.thresholds: Dict[str, float] = {}
        self.metadata: Dict[str, Any] = {}
        self.top_outliers: List[Dict[str, Any]] = []

    def fit(
        self,
        features_path: str = BEHAVIORAL_FEATURES_PATH,
        cluster_model_path: str = CLUSTER_MODEL_PATH,
        cluster_labels_path: str = CLUSTER_LABELS_PATH,
        cluster_profiles_path: str = CLUSTER_PROFILES_PATH
    ) -> "BehavioralAnomalyDetector":
        """
        Trains Isolation Forest and computes calibrated novelty scores across all incidents.
        """
        logger.info(f"Loading Behavioral DNA features from {features_path}...")
        features_df = pd.read_csv(features_path)
        self.incident_ids = features_df["incident_id"].tolist()
        self.feature_names = [c for c in features_df.columns if c != "incident_id"]

        raw_feat = features_df[self.feature_names].values.astype(np.float32)
        norms = np.linalg.norm(raw_feat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_feat = raw_feat / norms

        logger.info(f"Loading KMeans cluster model from {cluster_model_path}...")
        kmeans_model = joblib.load(cluster_model_path)
        raw_centroids = kmeans_model.cluster_centers_.astype(np.float32)
        c_norms = np.linalg.norm(raw_centroids, axis=1, keepdims=True)
        c_norms[c_norms == 0] = 1.0
        self.cluster_centroids = raw_centroids / c_norms

        # Load cluster names
        if os.path.exists(cluster_labels_path):
            labels_df = pd.read_csv(cluster_labels_path)
            self.cluster_names = (
                labels_df.groupby("cluster_id")["cluster_name"].first().to_dict()
            )
        else:
            self.cluster_names = {i: f"Behavioral Cluster {i}" for i in range(len(self.cluster_centroids))}

        # ---------------------------------------------------------------------
        # 1. Geometric Distance to Nearest Cluster Centroids
        # ---------------------------------------------------------------------
        logger.info("Computing geometric cosine distances to behavioral cluster centroids...")
        # Cosine similarity matrix: shape (N, K)
        sim_matrix = np.dot(normalized_feat, self.cluster_centroids.T)

        # Sort similarities per incident in descending order
        sorted_indices = np.argsort(-sim_matrix, axis=1)
        nearest_clusters = sorted_indices[:, 0]
        second_nearest_clusters = sorted_indices[:, 1]

        max_sims = sim_matrix[np.arange(len(sim_matrix)), nearest_clusters]
        second_sims = sim_matrix[np.arange(len(sim_matrix)), second_nearest_clusters]

        centroid_distances = np.clip(1.0 - max_sims, 0.0, 2.0)
        second_distances = np.clip(1.0 - second_sims, 0.0, 2.0)

        # ---------------------------------------------------------------------
        # 2. Isolation Forest Structural Tree Isolation
        # ---------------------------------------------------------------------
        logger.info(
            f"Training IsolationForest (trees={self.config['n_estimators']}, "
            f"samples={self.config['max_samples']}, contamination={self.config['contamination']})..."
        )
        self.model = IsolationForest(
            n_estimators=self.config["n_estimators"],
            max_samples=self.config["max_samples"],
            contamination=self.config["contamination"],
            random_state=self.config["random_state"],
            n_jobs=self.config["n_jobs"]
        )
        self.model.fit(normalized_feat)

        logger.info("Evaluating structural isolation scores...")
        # Higher score = more anomalous
        iso_raw_scores = -self.model.score_samples(normalized_feat)

        # ---------------------------------------------------------------------
        # 3. Min-Max Normalization & Composite Novelty Score
        # ---------------------------------------------------------------------
        c_min, c_max = float(centroid_distances.min()), float(centroid_distances.max())
        norm_centroid_dist = (centroid_distances - c_min) / (c_max - c_min + 1e-12)

        i_min, i_max = float(iso_raw_scores.min()), float(iso_raw_scores.max())
        norm_iso_scores = (iso_raw_scores - i_min) / (i_max - i_min + 1e-12)

        w_c = self.config["weight_centroid_dist"]
        w_i = self.config["weight_isolation_score"]
        composite_scores = w_c * norm_centroid_dist + w_i * norm_iso_scores

        # ---------------------------------------------------------------------
        # 4. Calibrated Threshold Selection
        # ---------------------------------------------------------------------
        logger.info("Calibrating empirical quantile thresholds...")
        th_mod = float(np.quantile(composite_scores, self.config["threshold_moderate_quantile"]))
        th_high = float(np.quantile(composite_scores, self.config["threshold_high_quantile"]))
        th_ext = float(np.quantile(composite_scores, self.config["threshold_extreme_quantile"]))

        self.thresholds = {
            "moderate_novelty_threshold_p95": round(th_mod, 4),
            "high_outlier_threshold_p99": round(th_high, 4),
            "extreme_outlier_threshold_p999": round(th_ext, 4)
        }

        # Assign neutral categorization tiers
        def assign_tier(score: float) -> str:
            if score >= th_high:
                return ANOMALY_TIER_LABELS["high"]
            elif score >= th_mod:
                return ANOMALY_TIER_LABELS["moderate"]
            else:
                return ANOMALY_TIER_LABELS["standard"]

        tiers = [assign_tier(s) for s in composite_scores]

        # Assemble scores DataFrame
        self.scores_df = pd.DataFrame({
            "incident_id": self.incident_ids,
            "novelty_score": np.round(composite_scores, 4),
            "novelty_tier": tiers,
            "nearest_cluster_id": nearest_clusters,
            "nearest_cluster_name": [self.cluster_names.get(int(c), f"Cluster {c}") for c in nearest_clusters],
            "distance_to_nearest_cluster": np.round(centroid_distances, 4),
            "second_nearest_cluster_id": second_nearest_clusters,
            "second_nearest_cluster_name": [self.cluster_names.get(int(c), f"Cluster {c}") for c in second_nearest_clusters],
            "distance_to_second_cluster": np.round(second_distances, 4),
            "isolation_forest_raw_score": np.round(iso_raw_scores, 4)
        })

        # ---------------------------------------------------------------------
        # 5. Feature Deviation Explanations for Top Outliers
        # ---------------------------------------------------------------------
        logger.info("Synthesizing feature deviation explanations for top behavioral outliers...")
        top_indices = np.argsort(-composite_scores)[:200]
        self.top_outliers = []

        global_means = normalized_feat.mean(axis=0)

        for idx in top_indices:
            inc_id = self.incident_ids[idx]
            cl_id = int(nearest_clusters[idx])
            cl_name = self.cluster_names.get(cl_id, f"Cluster {cl_id}")
            centroid = self.cluster_centroids[cl_id]
            inc_vec = normalized_feat[idx]

            # Deviations from nearest cluster centroid
            diffs = inc_vec - centroid
            abs_diffs = np.abs(diffs)
            top_feat_indices = np.argsort(-abs_diffs)[:self.config["top_unusual_features_count"]]

            unusual_features = []
            for f_idx in top_feat_indices:
                feat_name = self.feature_names[f_idx]
                val = float(inc_vec[f_idx])
                cent_val = float(centroid[f_idx])
                delta = float(diffs[f_idx])
                direction = "Elevated" if delta > 0 else "Suppressed"

                unusual_features.append({
                    "feature_name": feat_name,
                    "incident_value": round(val, 4),
                    "cluster_centroid_value": round(cent_val, 4),
                    "deviation_delta": round(delta, 4),
                    "direction": direction,
                    "explanation": f"{direction} relative to {cl_name} (actual: {val:.2f}, cluster baseline: {cent_val:.2f})"
                })

            self.top_outliers.append({
                "incident_id": inc_id,
                "novelty_score": round(float(composite_scores[idx]), 4),
                "novelty_tier": str(tiers[idx]),
                "nearest_cluster": {
                    "cluster_id": cl_id,
                    "cluster_name": cl_name,
                    "distance": round(float(centroid_distances[idx]), 4)
                },
                "second_nearest_cluster": {
                    "cluster_id": int(second_nearest_clusters[idx]),
                    "cluster_name": self.cluster_names.get(int(second_nearest_clusters[idx]), ""),
                    "distance": round(float(second_distances[idx]), 4)
                },
                "unusual_features": unusual_features,
                "behavioral_summary": (
                    f"Incident {inc_id} deviates from {cl_name} primarily due to {unusual_features[0]['feature_name']} "
                    f"({unusual_features[0]['direction'].lower()}) and {unusual_features[1]['feature_name']} "
                    f"({unusual_features[1]['direction'].lower()})."
                )
            })

        # Metadata summary
        tier_counts = self.scores_df["novelty_tier"].value_counts().to_dict()
        self.metadata = {
            "version": "1.0",
            "total_incidents": len(self.incident_ids),
            "algorithm": "Dual-Paradigm: Spherical Centroid Distance + Isolation Forest Ensemble",
            "hyperparameters": {
                "n_estimators": self.config["n_estimators"],
                "max_samples": self.config["max_samples"],
                "contamination": self.config["contamination"],
                "weight_centroid_dist": w_c,
                "weight_isolation_score": w_i
            },
            "thresholds": self.thresholds,
            "tier_counts": {
                k: int(v) for k, v in tier_counts.items()
            },
            "tier_percentages": {
                k: round(float(v / len(self.incident_ids)) * 100, 2)
                for k, v in tier_counts.items()
            },
            "score_statistics": {
                "mean": round(float(composite_scores.mean()), 4),
                "median": round(float(np.median(composite_scores)), 4),
                "std": round(float(composite_scores.std()), 4),
                "min": round(float(composite_scores.min()), 4),
                "max": round(float(composite_scores.max()), 4)
            }
        }

        logger.info(
            f"Anomaly Detection Fit Complete. High Outliers (p99): {tier_counts.get(ANOMALY_TIER_LABELS['high'], 0):,}, "
            f"Moderate Novelty (p95): {tier_counts.get(ANOMALY_TIER_LABELS['moderate'], 0):,}."
        )
        return self

    def explain_incident(self, incident_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed novelty breakdown and feature deviation explanation for a specific incident.
        """
        if self.scores_df is None:
            raise RuntimeError("Detector is not fitted. Call fit() or load() first.")

        matches = self.scores_df[self.scores_df["incident_id"] == incident_id]
        if len(matches) == 0:
            raise KeyError(f"Incident ID '{incident_id}' not found in dataset.")

        row = matches.iloc[0]

        # Check if already cached in top_outliers
        for outlier in self.top_outliers:
            if outlier["incident_id"] == incident_id:
                return outlier

        # If not in top outliers, compute on the fly
        if self.cluster_centroids is None:
            raise ValueError("Cluster centroids have not been initialized or loaded.")
        idx = self.incident_ids.index(incident_id)
        cl_id = int(row["nearest_cluster_id"])
        cl_name = str(row["nearest_cluster_name"])
        centroid = self.cluster_centroids[cl_id]

        features_df = pd.read_csv(BEHAVIORAL_FEATURES_PATH)
        inc_vec = features_df.loc[idx, self.feature_names].values.astype(np.float32)
        norm = np.linalg.norm(inc_vec)
        if norm > 0:
            inc_vec = inc_vec / norm

        diffs = inc_vec - centroid
        top_indices = np.argsort(-np.abs(diffs))[:self.config["top_unusual_features_count"]]

        unusual = []
        for f_idx in top_indices:
            feat_name = self.feature_names[f_idx]
            val = float(inc_vec[f_idx])
            cent_val = float(centroid[f_idx])
            delta = float(diffs[f_idx])
            direction = "Elevated" if delta > 0 else "Suppressed"
            unusual.append({
                "feature_name": feat_name,
                "incident_value": round(val, 4),
                "cluster_centroid_value": round(cent_val, 4),
                "deviation_delta": round(delta, 4),
                "direction": direction,
                "explanation": f"{direction} relative to {cl_name} (actual: {val:.2f}, cluster baseline: {cent_val:.2f})"
            })

        return {
            "incident_id": incident_id,
            "novelty_score": float(row["novelty_score"]),
            "novelty_tier": str(row["novelty_tier"]),
            "nearest_cluster": {
                "cluster_id": cl_id,
                "cluster_name": cl_name,
                "distance": float(row["distance_to_nearest_cluster"])
            },
            "second_nearest_cluster": {
                "cluster_id": int(row["second_nearest_cluster_id"]),
                "cluster_name": str(row["second_nearest_cluster_name"]),
                "distance": float(row["distance_to_second_cluster"])
            },
            "unusual_features": unusual,
            "behavioral_summary": (
                f"Incident {incident_id} deviates from {cl_name} primarily due to {unusual[0]['feature_name']} "
                f"({unusual[0]['direction'].lower()}) and {unusual[1]['feature_name']} "
                f"({unusual[1]['direction'].lower()})."
            )
        }

    def export_artifacts(self, output_dir: str = ANOMALY_DIR) -> None:
        """
        Serializes Isolation Forest model, metadata, top outliers JSON, and incident anomaly scores CSV.
        """
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"Saving Isolation Forest model to {MODEL_PATH}...")
        joblib.dump(self.model, MODEL_PATH)

        if self.scores_df is None:
            raise ValueError("Scores DataFrame is not initialized.")
        logger.info(f"Saving incident anomaly scores to {SCORES_CSV_PATH}...")
        self.scores_df.to_csv(SCORES_CSV_PATH, index=False)

        logger.info(f"Saving top behavioral outliers to {TOP_OUTLIERS_JSON_PATH}...")
        with open(TOP_OUTLIERS_JSON_PATH, "w") as f:
            json.dump(self.top_outliers, f, indent=2)

        logger.info(f"Saving anomaly metadata to {ANOMALY_SUMMARY_PATH}...")
        with open(ANOMALY_SUMMARY_PATH, "w") as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"All anomaly artifacts successfully persisted in {output_dir}")

    def generate_visualizations(self, chart_path: str = ANOMALY_CHART_PATH) -> None:
        """
        Generates publication-quality charts of the anomaly score distribution and cluster outlier rates.
        """
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        logger.info(f"Rendering anomaly distribution visualization at {chart_path}...")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

        if self.scores_df is None:
            raise ValueError("Scores DataFrame is not initialized.")
        scores = self.scores_df["novelty_score"].values
        th_95 = self.thresholds["moderate_novelty_threshold_p95"]
        th_99 = self.thresholds["high_outlier_threshold_p99"]

        # Panel 1: Composite Novelty Score Histogram & Quantiles
        n, bins, patches = ax1.hist(scores, bins=60, color="#4361EE", alpha=0.7, edgecolor="black")
        for b, patch in zip(bins, patches):
            if b >= th_99:
                patch.set_facecolor("#EF233C") # High Outliers
            elif b >= th_95:
                patch.set_facecolor("#F4A261") # Moderate Novelty

        ax1.axvline(th_95, color="#F4A261", linestyle="--", linewidth=2.0, label=f"95th Percentile: {th_95:.3f} (Moderate)")
        ax1.axvline(th_99, color="#EF233C", linestyle="-", linewidth=2.5, label=f"99th Percentile: {th_99:.3f} (High Outlier)")
        ax1.set_title("A. Composite Behavioral Novelty Score Distribution", fontsize=11, fontweight="bold")
        ax1.set_xlabel("Novelty Score (0.0 = Baseline, 1.0 = Extreme Outlier)", fontsize=10, fontweight="bold")
        ax1.set_ylabel("Incident Count", fontsize=10, fontweight="bold")
        ax1.legend(loc="upper right", fontsize=9)
        ax1.grid(True, linestyle="--", alpha=0.5)

        # Panel 2: Distance to Cluster Centroid vs Isolation Forest Score
        sample_idx = np.random.RandomState(42).choice(len(self.scores_df), size=3000, replace=False)
        sample_df = self.scores_df.iloc[sample_idx]

        ax2.scatter(
            sample_df["distance_to_nearest_cluster"],
            sample_df["isolation_forest_raw_score"],
            c=sample_df["novelty_score"],
            cmap="viridis",
            alpha=0.6,
            edgecolors="none",
            s=20
        )
        ax2.set_title("B. Cluster Centroid Distance vs Isolation Forest Score (N=3,000 sample)", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Cosine Distance to Nearest Cluster Centroid", fontsize=10, fontweight="bold")
        ax2.set_ylabel("Isolation Forest Raw Anomaly Score", fontsize=10, fontweight="bold")
        ax2.grid(True, linestyle="--", alpha=0.5)

        # Panel 3: Outlier Prevalence Across Behavioral Clusters
        cl_counts = self.scores_df.groupby("nearest_cluster_id").size()
        cl_outliers = self.scores_df[self.scores_df["novelty_score"] >= th_99].groupby("nearest_cluster_id").size()
        outlier_rates = ((cl_outliers / cl_counts) * 100).fillna(0.0)

        cl_names = [self.cluster_names.get(i, f"C{i}")[:22] for i in range(len(cl_counts))]
        y_pos = np.arange(len(cl_names))

        ax3.barh(y_pos, outlier_rates, color="#D90429", alpha=0.8, edgecolor="black")
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(cl_names, fontsize=8)
        ax3.invert_yaxis()
        ax3.set_title("C. Behavioral Outlier Rate by Nearest Cluster (% >= 99th Percentile)", fontsize=11, fontweight="bold")
        ax3.set_xlabel("Percentage of Cluster Incidents Classified as High Outlier (%)", fontsize=10, fontweight="bold")
        ax3.grid(axis="x", linestyle="--", alpha=0.5)

        for i, v in enumerate(outlier_rates):
            ax3.text(v + 0.05, i, f"{v:.2f}%", va="center", fontsize=8, fontweight="bold")

        # Panel 4: Top Outlier Archetype Feature Deviation Profile
        top_outlier = self.top_outliers[0]
        feats = [f["feature_name"][:20] for f in top_outlier["unusual_features"]]
        deltas = [f["deviation_delta"] for f in top_outlier["unusual_features"]]
        y_f = np.arange(len(feats))

        bar_cols = ["#EF233C" if d > 0 else "#3A86FF" for d in deltas]
        ax4.barh(y_f, deltas, color=bar_cols, alpha=0.85, edgecolor="black")
        ax4.set_yticks(y_f)
        ax4.set_yticklabels(feats, fontsize=9)
        ax4.axvline(0, color="black", linewidth=1.0)
        ax4.set_title(f"D. Top Outlier Feature Deviations: Incident {top_outlier['incident_id']}", fontsize=11, fontweight="bold")
        ax4.set_xlabel("Deviation from Nearest Centroid (+ = Elevated, - = Suppressed)", fontsize=10, fontweight="bold")
        ax4.grid(axis="x", linestyle="--", alpha=0.5)

        for i, d in enumerate(deltas):
            ax4.text(d + (0.01 if d > 0 else -0.04), i, f"{d:+.2f}", va="center", fontsize=8, fontweight="bold")

        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Anomaly visualization saved to {chart_path}")


if __name__ == "__main__":
    detector = BehavioralAnomalyDetector()
    detector.fit()
    detector.export_artifacts()
    detector.generate_visualizations()
