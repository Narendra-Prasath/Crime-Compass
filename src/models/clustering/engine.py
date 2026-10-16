"""
CRIME DNA — Phase 6: Behavioral Clustering Engine

Implements scalable, reproducible unsupervised clustering over 70-dimensional
Behavioral DNA representations, generating detailed behavioral profiles for
each discovered cluster.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Optional, Tuple, Any

# Ensure workspace root is in sys.path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import numpy as np
import pandas as pd
import joblib
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

from src.features.config import FEATURE_GROUPS
from src.models.clustering.config import (
    CLUSTERS_DIR,
    MODEL_PATH,
    LABELS_PATH,
    PROFILES_PATH,
    METADATA_PATH,
    CLUSTERING_CONFIG,
    CLUSTER_ARCHETYPES
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_CLUSTERING")


class BehavioralClusterer:
    """
    Unsupervised clustering engine for incident-level Behavioral DNA vectors.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = {**CLUSTERING_CONFIG, **(config or {})}
        self.model: Optional[MiniBatchKMeans] = None
        self.feature_names: List[str] = []
        self.incident_ids: List[str] = []
        self.cluster_labels: Optional[np.ndarray] = None
        self.cluster_profiles: Dict[int, Dict[str, Any]] = {}
        self.evaluation_metrics: Dict[str, float] = {}

    def fit(
        self,
        features_csv_path: str = "data/processed/crime_dna_behavioral_features.csv",
        n_clusters: Optional[int] = None
    ) -> "BehavioralClusterer":
        """
        Fits MiniBatchKMeans over the Behavioral DNA matrix and profiles each cluster.
        """
        if not os.path.exists(features_csv_path):
            raise FileNotFoundError(f"Feature dataset not found at {features_csv_path}")

        logger.info(f"Loading Behavioral DNA from {features_csv_path}...")
        df = pd.read_csv(features_csv_path, low_memory=False)

        self.incident_ids = df["incident_id"].tolist()
        feature_df = df.drop(columns=["incident_id"])
        self.feature_names = feature_df.columns.tolist()
        raw_matrix = feature_df.values.astype(np.float32)

        # L2-normalize vectors so spherical Euclidean distance is monotonic with Cosine Distance
        logger.info("Projecting vectors onto unit L2 hypersphere...")
        norms = np.linalg.norm(raw_matrix, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        features_norm = raw_matrix / norms

        k = n_clusters or self.config["n_clusters"]
        logger.info(f"Fitting MiniBatchKMeans (k={k}, batch_size={self.config['batch_size']})...")
        
        self.model = MiniBatchKMeans(
            n_clusters=k,
            batch_size=self.config["batch_size"],
            random_state=self.config["random_state"],
            n_init=self.config["n_init"],
            max_iter=self.config["max_iter"],
            reassignment_ratio=self.config.get("reassignment_ratio", 0.01)
        )
        self.cluster_labels = self.model.fit_predict(features_norm)
        logger.info("Clustering model converged successfully.")

        # Compute evaluation metrics on stratified sample
        logger.info("Calculating unsupervised cluster evaluation metrics...")
        np.random.seed(self.config["random_state"])
        sample_size = min(15000, len(features_norm))
        sample_idx = np.random.choice(len(features_norm), size=sample_size, replace=False)
        sample_feats = features_norm[sample_idx]
        sample_labels = self.cluster_labels[sample_idx]

        self.evaluation_metrics = {
            "inertia": float(self.model.inertia_),
            "silhouette_cosine": round(float(silhouette_score(sample_feats, sample_labels, metric="cosine")), 4),
            "davies_bouldin_index": round(float(davies_bouldin_score(sample_feats, sample_labels)), 4),
            "calinski_harabasz_index": round(float(calinski_harabasz_score(sample_feats, sample_labels)), 1),
            "evaluation_sample_size": sample_size
        }
        logger.info(f"Metrics: Silhouette={self.evaluation_metrics['silhouette_cosine']}, DB={self.evaluation_metrics['davies_bouldin_index']}, CH={self.evaluation_metrics['calinski_harabasz_index']}")

        # Build behavioral profiles for each cluster
        logger.info("Synthesizing behavioral profiles for each discovered cluster...")
        self._build_cluster_profiles(feature_df, self.cluster_labels)
        return self

    def _build_cluster_profiles(
        self,
        feature_df: pd.DataFrame,
        labels: np.ndarray
    ) -> None:
        """
        Computes dominant characteristics, subprofile summaries, and differential metrics per cluster.
        """
        df_labeled = feature_df.copy()
        df_labeled["cluster"] = labels
        total_records = len(df_labeled)

        global_means = feature_df.mean()
        cluster_means = df_labeled.groupby("cluster").mean()
        cluster_counts = pd.Series(labels).value_counts().sort_index()

        self.cluster_profiles = {}

        for cl_id in range(self.config["n_clusters"]):
            val = cluster_counts.get(cl_id, 0)
            count = int(val) if val is not None else 0
            pct = round((count / total_records) * 100.0, 2)
            c_mean = cluster_means.loc[cl_id]
            diff = c_mean - global_means

            # Top distinctive features relative to global baseline
            distinctive_features = [
                {
                    "feature": feat,
                    "cluster_mean": round(float(c_mean[feat]), 3),
                    "global_mean": round(float(global_means[feat]), 3),
                    "difference": round(float(diff[feat]), 3)
                }
                for feat in diff.sort_values(ascending=False).head(8).index
            ]

            # Sub-profile summaries
            archetype = CLUSTER_ARCHETYPES.get(cl_id, {
                "name": f"Behavioral Cluster {cl_id}",
                "category": "Mixed",
                "summary": "Multi-dimensional behavioral grouping."
            })

            profile = {
                "cluster_id": cl_id,
                "name": archetype["name"],
                "macro_category": archetype["category"],
                "summary": archetype["summary"],
                "incident_count": count,
                "percentage_of_total": pct,
                "dominant_patterns": {
                    "crime_characteristics": {
                        "against_person_pct": round(float(c_mean.get("crime_against_person", 0)) * 100, 1),
                        "against_property_pct": round(float(c_mean.get("crime_against_property", 0)) * 100, 1),
                        "against_society_pct": round(float(c_mean.get("crime_against_society", 0)) * 100, 1),
                        "attempted_rate_pct": round(float(c_mean.get("is_attempted", 0)) * 100, 1),
                    },
                    "temporal_patterns": {
                        "nighttime_pct": round(float(c_mean.get("time_is_night", 0)) * 100, 1),
                        "weekend_pct": round(float(c_mean.get("time_is_weekend", 0)) * 100, 1),
                    },
                    "location_patterns": {
                        "population_density_index": round(float(c_mean.get("population_log_scaled", 0)), 3),
                        "multi_location_rate_pct": round(float(c_mean.get("location_count_scaled", 0)) * 100, 1),
                        "state_police_pct": round(float(c_mean.get("agency_is_state_police", 0)) * 100, 1),
                    },
                    "weapon_characteristics": {
                        "weapon_presence_pct": round(float(c_mean.get("has_weapon", 0)) * 100, 1),
                        "multi_weapon_pct": round(float(c_mean.get("is_multi_weapon", 0)) * 100, 1),
                    },
                    "property_characteristics": {
                        "property_involvement_pct": round(float(c_mean.get("has_property", 0)) * 100, 1),
                        "theft_rate_pct": round(float(c_mean.get("has_stolen_property", 0)) * 100, 1),
                        "log_property_value": round(float(c_mean.get("property_value_log_scaled", 0)), 3),
                        "cargo_theft_rate_pct": round(float(c_mean.get("is_cargo_theft", 0)) * 100, 2),
                    },
                    "people_patterns": {
                        "multi_victim_rate_pct": round(float(c_mean.get("is_multi_victim", 0)) * 100, 1),
                        "co_offender_rate_pct": round(float(c_mean.get("is_co_offender", 0)) * 100, 1),
                        "known_relationship_pct": round(float(c_mean.get("has_relationship", 0)) * 100, 1),
                    },
                    "context_and_harm": {
                        "physical_injury_pct": round(float(c_mean.get("has_injury", 0)) * 100, 1),
                        "drug_involvement_pct": round(float(c_mean.get("has_drug", 0)) * 100, 1),
                        "criminal_activity_pct": round(float(c_mean.get("has_criminal_activity", 0)) * 100, 1),
                        "on_scene_arrest_pct": round(float(c_mean.get("has_arrest_on_scene", 0)) * 100, 1),
                        "bias_motivated_pct": round(float(c_mean.get("has_bias_motivation", 0)) * 100, 2),
                    }
                },
                "top_distinctive_features": distinctive_features
            }
            self.cluster_profiles[cl_id] = profile

    def save(self, output_dir: str = CLUSTERS_DIR) -> None:
        """
        Serializes model, cluster profiles, metadata, and incident-cluster mapping.
        """
        if self.model is None:
            raise ValueError("Cannot save an un-fitted clustering model.")

        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, "kmeans_model.joblib")
        labels_path = os.path.join(output_dir, "incident_cluster_labels.csv")
        profiles_path = os.path.join(output_dir, "cluster_profiles.json")
        meta_path = os.path.join(output_dir, "cluster_metadata.json")

        if self.cluster_labels is None:
            raise ValueError("Cluster labels have not been computed. Call fit() before saving.")
        labels = self.cluster_labels

        logger.info(f"Saving clustering model to {model_path}...")
        joblib.dump(self.model, model_path)

        logger.info(f"Saving incident-cluster labels to {labels_path}...")
        labels_df = pd.DataFrame({
            "incident_id": self.incident_ids,
            "cluster_id": labels,
            "cluster_name": [CLUSTER_ARCHETYPES[c]["name"] for c in labels]
        })
        labels_df.to_csv(labels_path, index=False)

        logger.info(f"Saving cluster profiles to {profiles_path}...")
        with open(profiles_path, "w") as f:
            json.dump(self.cluster_profiles, f, indent=2)

        metadata = {
            "version": "1.0",
            "total_incidents": len(self.incident_ids),
            "n_clusters": self.config["n_clusters"],
            "algorithm": self.config["algorithm"],
            "evaluation_metrics": self.evaluation_metrics,
            "cluster_counts": {
                cl_id: int((labels == cl_id).sum())
                for cl_id in range(self.config["n_clusters"])
            }
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Cluster artifacts successfully persisted in {output_dir}")

    def load(self, input_dir: str = CLUSTERS_DIR) -> "BehavioralClusterer":
        """
        Loads saved clustering model, metadata, and profiles from disk.
        """
        model_path = os.path.join(input_dir, "kmeans_model.joblib")
        profiles_path = os.path.join(input_dir, "cluster_profiles.json")
        meta_path = os.path.join(input_dir, "cluster_metadata.json")

        for p in [model_path, profiles_path, meta_path]:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Missing required cluster artifact at {p}")

        logger.info(f"Loading clustering model from {model_path}...")
        self.model = joblib.load(model_path)

        with open(profiles_path) as f:
            self.cluster_profiles = {int(k): v for k, v in json.load(f).items()}

        with open(meta_path) as f:
            meta = json.load(f)
        self.evaluation_metrics = meta["evaluation_metrics"]
        logger.info(f"Clustering engine loaded: {len(self.cluster_profiles)} behavioral clusters.")
        return self

    def predict_cluster(self, vector: np.ndarray) -> Dict[str, Any]:
        """
        Assigns a single 70-dimensional Behavioral DNA vector to its nearest cluster.
        """
        if self.model is None:
            raise RuntimeError("Clustering engine has not been fitted or loaded.")

        vec = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        norm = np.linalg.norm(vec)
        vec_norm = vec / (norm if norm > 0 else 1.0)

        cl_id = int(self.model.predict(vec_norm)[0])
        centroid = self.model.cluster_centers_[cl_id]
        distance_to_centroid = float(np.linalg.norm(vec_norm[0] - centroid))

        return {
            "assigned_cluster_id": cl_id,
            "cluster_name": self.cluster_profiles[cl_id]["name"],
            "macro_category": self.cluster_profiles[cl_id]["macro_category"],
            "distance_to_centroid": round(distance_to_centroid, 4),
            "cluster_summary": self.cluster_profiles[cl_id]["summary"]
        }


def build_and_save_clusters():
    """Trains and serializes the production clustering engine."""
    clusterer = BehavioralClusterer()
    clusterer.fit()
    clusterer.save()


def main():
    parser = argparse.ArgumentParser(description="CRIME DNA Behavioral Clustering CLI")
    parser.add_argument("--train", action="store_true", help="Fit and persist the clustering model")
    parser.add_argument("--predict", type=str, default=None, help="Incident ID to predict cluster for")
    args = parser.parse_args()

    clusterer = BehavioralClusterer()

    if args.train or not os.path.exists(MODEL_PATH):
        clusterer.fit()
        clusterer.save()

    if args.predict:
        if clusterer.model is None:
            clusterer.load()
        # Look up vector from features CSV
        feat_df = pd.read_csv("data/processed/crime_dna_behavioral_features.csv")
        row = feat_df[feat_df["incident_id"] == args.predict]
        if row.empty:
            print(f"Incident {args.predict} not found.")
            return
        vec = row.drop(columns=["incident_id"]).values[0]
        res = clusterer.predict_cluster(vec)
        print("\n" + "="*60)
        print(f"INCIDENT: {args.predict}")
        print(f"Assigned Cluster: {res['assigned_cluster_id']} — {res['cluster_name']}")
        print(f"Macro Category:   {res['macro_category']}")
        print(f"Centroid Dist:    {res['distance_to_centroid']}")
        print(f"Summary:          {res['cluster_summary']}")
        print("="*60)


if __name__ == "__main__":
    main()
