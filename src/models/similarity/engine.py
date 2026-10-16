"""
CRIME DNA — Phase 5: Behavioral Similarity Engine

Implements nearest-neighbor retrieval over 70-dimensional Behavioral DNA vectors,
computing exact cosine similarities, providing sub-profile similarity breakdowns,
and excluding self-matches.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Optional, Tuple, Union, Any

# Ensure workspace root is in sys.path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import numpy as np
import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors

from src.features.config import FEATURE_GROUPS, FEATURE_DESCRIPTIONS
from src.models.similarity.config import (
    SIMILARITY_DIR,
    INDEX_MODEL_PATH,
    FEATURE_MATRIX_PATH,
    INCIDENT_IDS_PATH,
    METADATA_PATH,
    SIMILARITY_CONFIG,
    SUBPROFILE_WEIGHTS
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_SIMILARITY")


def normalize_category_for_matching(cat: Optional[str]) -> str:
    """Normalizes statutory crime categories for behavioral cross-crime comparison."""
    c = str(cat or "").lower().strip()
    if "person" in c and "property" in c:
        return "person_property"
    elif "person" in c:
        return "person"
    elif "property" in c or "theft" in c or "burglary" in c or "larceny" in c:
        return "property"
    elif "society" in c or "drug" in c or "vice" in c or "weapon" in c:
        return "society"
    return "other"


def extract_relevant_behavioral_characteristics(ctx: Optional[Dict[str, Any]]) -> List[str]:
    """Dynamically extracts salient behavioral characteristics from incident context."""
    traits: List[str] = []
    if not ctx:
        return ["Standard operational execution profile"]

    # 1. Temporal
    hr = ctx.get("incident_hour", 12)
    is_night = bool(ctx.get("is_night", False))
    is_weekend = bool(ctx.get("is_weekend", False))
    time_str = f"{hr:02d}:00"
    if is_night:
        traits.append(f"🌙 Nocturnal execution ({time_str})")
    else:
        traits.append(f"☀️ Daytime execution ({time_str})")
    if is_weekend:
        traits.append("📅 Weekend operation")

    # 2. Weapon & Modus Operandi
    if ctx.get("has_weapon"):
        traits.append("🔫 Armed encounter (weapon deployed)")
    else:
        traits.append("🚫 Unarmed execution (no weapon)")

    # 3. Setting / Environment
    pop = float(ctx.get("population", 0.0))
    if pop >= 250000:
        traits.append("🏢 Metropolitan Core setting")
    elif pop >= 50000:
        traits.append("🏙️ Commercial / Urban jurisdiction")
    elif pop >= 10000:
        traits.append("🏠 Suburban community")
    elif pop > 0:
        traits.append("🌾 Rural jurisdiction")

    # 4. Demographics
    v_count = int(ctx.get("victim_count", 0))
    if v_count > 1:
        traits.append(f"👥 Multiple victims ({v_count} victims)")
    elif v_count == 1:
        traits.append("👤 Solo victim targeted")

    o_count = int(ctx.get("offender_count", 0))
    if o_count > 1:
        traits.append(f"👥 Co-offender group ({o_count} perpetrators)")
    elif o_count == 1:
        traits.append("👤 Solo perpetrator")

    # 5. Economic loss
    prop_val = float(ctx.get("property_value", 0.0))
    if ctx.get("has_property") or prop_val > 0:
        if prop_val >= 2500:
            traits.append(f"📦 High-value property loss (${prop_val:,.0f})")
        elif prop_val > 0:
            traits.append(f"📦 Property involved (${prop_val:,.0f})")
        else:
            traits.append("📦 Property targeted")

    # 6. Physical Harm / Arrest
    if ctx.get("has_injury"):
        traits.append("🩹 Physical injury sustained")
    if ctx.get("has_arrest"):
        traits.append("⚖️ On-scene arrest effected")
    else:
        traits.append("🏃 Perpetrator fled scene")

    return traits[:5]


class BehavioralSimilarityEngine:
    """
    Nearest-neighbor retrieval system for incident-level Behavioral DNA fingerprints.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or SIMILARITY_CONFIG
        self.model: Optional[NearestNeighbors] = None
        self.features_norm: Optional[np.ndarray] = None
        self.raw_features: Optional[np.ndarray] = None
        self.incident_ids: List[str] = []
        self.id_to_idx: Dict[str, int] = {}
        self.feature_names: List[str] = []
        self.feature_groups: Dict[str, List[str]] = FEATURE_GROUPS
        self.group_indices: Dict[str, List[int]] = {}

    def build_index(
        self,
        features_csv_path: str = "data/processed/crime_dna_behavioral_features.csv"
    ) -> "BehavioralSimilarityEngine":
        """
        Builds the NearestNeighbors index from the Phase 3 feature dataset.
        """
        if not os.path.exists(features_csv_path):
            raise FileNotFoundError(f"Behavioral DNA features not found at {features_csv_path}")

        logger.info(f"Loading Behavioral DNA dataset from {features_csv_path}...")
        df = pd.read_csv(features_csv_path, low_memory=False)

        if "incident_id" not in df.columns:
            raise ValueError("Input dataset must contain 'incident_id' column")

        self.incident_ids = df["incident_id"].tolist()
        self.id_to_idx = {inc_id: idx for idx, inc_id in enumerate(self.incident_ids)}
        
        feature_df = df.drop(columns=["incident_id"])
        self.feature_names = feature_df.columns.tolist()
        self.raw_features = feature_df.values.astype(np.float32)

        # Precompute group column indices for fast subprofile similarity
        self.group_indices = {
            grp_name: [self.feature_names.index(col) for col in cols if col in self.feature_names]
            for grp_name, cols in self.feature_groups.items()
        }

        # Normalize features to unit L2 norm for exact cosine similarity
        logger.info("Normalizing feature vectors to unit L2 norm...")
        norms = np.linalg.norm(self.raw_features, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        self.features_norm = self.raw_features / norms

        # Build NearestNeighbors index
        logger.info(f"Fitting NearestNeighbors index (metric={self.config['metric']}, algorithm={self.config['algorithm']})...")
        self.model = NearestNeighbors(
            metric=self.config["metric"],
            algorithm=self.config["algorithm"],
            n_jobs=self.config["n_jobs"]
        )
        self.model.fit(self.features_norm)
        logger.info(f"Similarity index successfully built across {len(self.incident_ids):,} incidents.")
        return self

    def save(self, output_dir: str = SIMILARITY_DIR) -> None:
        """
        Persists the index model, normalized matrices, incident ID mappings, and metadata.
        """
        if self.model is None or self.features_norm is None:
            raise ValueError("Cannot save an unbuilt similarity index. Run build_index() first.")

        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, "knn_index.joblib")
        matrix_path = os.path.join(output_dir, "normalized_dna_matrix.npy")
        ids_path = os.path.join(output_dir, "incident_ids.json")
        meta_path = os.path.join(output_dir, "similarity_engine_metadata.json")

        logger.info(f"Saving NearestNeighbors model to {model_path}...")
        joblib.dump(self.model, model_path)

        logger.info(f"Saving normalized feature matrix to {matrix_path}...")
        np.save(matrix_path, self.features_norm)

        logger.info(f"Saving incident IDs registry to {ids_path}...")
        with open(ids_path, "w") as f:
            json.dump(self.incident_ids, f)

        metadata = {
            "version": "1.0",
            "total_incidents": len(self.incident_ids),
            "vector_dimension": len(self.feature_names),
            "metric": self.config["metric"],
            "algorithm": self.config["algorithm"],
            "feature_names": self.feature_names,
            "feature_groups": self.feature_groups
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"All similarity artifacts successfully persisted in {output_dir}")

    def load(self, input_dir: str = SIMILARITY_DIR) -> "BehavioralSimilarityEngine":
        """
        Loads the prebuilt similarity index and metadata from disk.
        """
        model_path = os.path.join(input_dir, "knn_index.joblib")
        matrix_path = os.path.join(input_dir, "normalized_dna_matrix.npy")
        ids_path = os.path.join(input_dir, "incident_ids.json")
        meta_path = os.path.join(input_dir, "similarity_engine_metadata.json")

        for p in [model_path, matrix_path, ids_path, meta_path]:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Missing required artifact at {p}")

        logger.info(f"Loading similarity index from {model_path}...")
        self.model = joblib.load(model_path)
        self.features_norm = np.load(matrix_path)

        with open(ids_path) as f:
            self.incident_ids = json.load(f)
        self.id_to_idx = {inc_id: idx for idx, inc_id in enumerate(self.incident_ids)}

        with open(meta_path) as f:
            meta = json.load(f)
        self.feature_names = meta["feature_names"]
        self.feature_groups = meta["feature_groups"]

        self.group_indices = {
            grp_name: [self.feature_names.index(col) for col in cols if col in self.feature_names]
            for grp_name, cols in self.feature_groups.items()
        }
        logger.info(f"Similarity engine loaded: {len(self.incident_ids):,} incidents, {len(self.feature_names)} features.")
        return self

    def _compute_subprofile_similarity(
        self,
        query_vec: np.ndarray,
        match_vec: np.ndarray
    ) -> Dict[str, float]:
        """
        Computes cosine similarity independently across each of the 7 behavioral sub-profiles.
        """
        breakdown = {}
        for grp_name, indices in self.group_indices.items():
            if not indices:
                continue
            u = query_vec[indices]
            v = match_vec[indices]
            norm_u = np.linalg.norm(u)
            norm_v = np.linalg.norm(v)
            if norm_u == 0.0 or norm_v == 0.0:
                sim = 1.0 if norm_u == norm_v else 0.0
            else:
                sim = float(np.dot(u, v) / (norm_u * norm_v))
            breakdown[grp_name] = round(max(0.0, min(1.0, sim)) * 100.0, 2)
        return breakdown

    def kneighbors_fast(
        self,
        query_norm_vec: np.ndarray,
        n_neighbors: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fast BLAS-accelerated cosine nearest-neighbor search for unit L2 normalized vectors.
        Exact mathematical equivalent to model.kneighbors with brute-force cosine distance,
        operating at ~1.5ms instead of ~14ms.
        """
        if self.features_norm is None:
            if self.model is not None:
                q = query_norm_vec.reshape(1, -1) if query_norm_vec.ndim == 1 else query_norm_vec
                return self.model.kneighbors(q, n_neighbors=n_neighbors)
            raise RuntimeError("Similarity engine features_norm is not loaded.")

        q = query_norm_vec.ravel()
        n_cand = min(max(1, n_neighbors), len(self.features_norm))
        # Exact dot product for unit vectors = cosine similarity
        sims = np.dot(self.features_norm, q)
        top_idx = np.argpartition(-sims, n_cand)[:n_cand]
        # Sort descending by similarity (ascending by distance)
        sorted_order = np.argsort(-sims[top_idx])
        top_idx = top_idx[sorted_order]
        top_dist = np.clip(1.0 - sims[top_idx], 0.0, 2.0).astype(np.float32)

        return top_dist.reshape(1, -1), top_idx.reshape(1, -1)

    def find_similar(
        self,
        incident_id: str,
        top_k: int = 5,
        include_breakdown: bool = True
    ) -> Dict[str, Any]:
        """
        Finds the top K behaviorally similar incidents for a given query incident_id.
        Excludes the queried incident itself from its own results.
        """
        if self.model is None or self.features_norm is None:
            raise RuntimeError("Similarity engine has not been built or loaded.")

        if incident_id not in self.id_to_idx:
            raise KeyError(f"Incident ID '{incident_id}' not found in similarity index.")

        query_idx = self.id_to_idx[incident_id]
        query_vec = self.features_norm[query_idx : query_idx + 1]

        # Request top_k + 1 neighbors to ensure we have top_k after excluding self
        n_query = min(top_k + 1, len(self.incident_ids))
        distances, indices = self.kneighbors_fast(query_vec, n_neighbors=n_query)

        distances = distances[0]
        indices = indices[0]

        matches = []
        rank = 1
        for dist, idx in zip(distances, indices):
            matched_id = self.incident_ids[idx]
            
            # Explicitly exclude the queried incident itself
            if matched_id == incident_id:
                continue

            # Cosine similarity in range [0.0, 1.0]
            # dist is cosine distance = 1 - cosine_similarity
            cos_sim = float(np.clip(1.0 - dist, 0.0, 1.0))
            sim_percentage = round(cos_sim * 100.0, 2)

            match_info = {
                "rank": rank,
                "incident_id": matched_id,
                "similarity_score_pct": sim_percentage,
                "cosine_distance": round(float(dist), 6),
            }

            if include_breakdown:
                match_vec = self.features_norm[idx]
                match_info["subprofile_similarity_pct"] = self._compute_subprofile_similarity(
                    query_vec[0], match_vec
                )

            matches.append(match_info)
            rank += 1
            if len(matches) == top_k:
                break

        return {
            "query_incident_id": incident_id,
            "top_k_requested": top_k,
            "total_matches_returned": len(matches),
            "matches": matches
        }

    def find_similar_by_vector(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        include_breakdown: bool = True
    ) -> Dict[str, Any]:
        """
        Finds the top K behaviorally similar incidents for an arbitrary external query vector.
        """
        if self.model is None or self.features_norm is None:
            raise RuntimeError("Similarity engine has not been built or loaded.")

        query_vector = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        if query_vector.shape[1] != len(self.feature_names):
            raise ValueError(f"Query vector length {query_vector.shape[1]} does not match index dimension {len(self.feature_names)}")

        # Normalize query vector
        norm = np.linalg.norm(query_vector)
        query_norm = query_vector / (norm if norm > 0 else 1.0)

        n_query = min(top_k, len(self.incident_ids))
        distances, indices = self.model.kneighbors(query_norm, n_neighbors=n_query)

        matches = []
        for rank, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
            matched_id = self.incident_ids[idx]
            cos_sim = float(np.clip(1.0 - dist, 0.0, 1.0))
            sim_percentage = round(cos_sim * 100.0, 2)

            match_info = {
                "rank": rank,
                "incident_id": matched_id,
                "similarity_score_pct": sim_percentage,
                "cosine_distance": round(float(dist), 6),
            }

            if include_breakdown:
                match_vec = self.features_norm[idx]
                match_info["subprofile_similarity_pct"] = self._compute_subprofile_similarity(
                    query_norm[0], match_vec
                )

            matches.append(match_info)

        return {
            "query_type": "custom_vector",
            "top_k_requested": top_k,
            "total_matches_returned": len(matches),
            "matches": matches
        }


def build_and_save_index():
    """Builds and serializes the default similarity engine."""
    engine = BehavioralSimilarityEngine()
    engine.build_index()
    engine.save()


def main():
    parser = argparse.ArgumentParser(description="CRIME DNA Behavioral Similarity Engine CLI")
    parser.add_argument("--build", action="store_true", help="Build and persist the similarity index")
    parser.add_argument("--query", type=str, default=None, help="Query incident ID to find matches for")
    parser.add_argument("--top-k", type=int, default=5, help="Number of similar incidents to retrieve")
    args = parser.parse_args()

    engine = BehavioralSimilarityEngine()
    
    if args.build or not os.path.exists(INDEX_MODEL_PATH):
        logger.info("Building similarity index...")
        engine.build_index()
        engine.save()

    if args.query:
        if engine.model is None:
            engine.load()
        results = engine.find_similar(args.query, top_k=args.top_k)
        print("\n" + "="*60)
        print(f"QUERY INCIDENT: {results['query_incident_id']}")
        print("="*60)
        for m in results["matches"]:
            print(f"Rank {m['rank']}: {m['incident_id']} | Similarity: {m['similarity_score_pct']}% | Cosine Dist: {m['cosine_distance']}")
            if "subprofile_similarity_pct" in m:
                print("  Subprofile Breakdown:")
                for grp, score in m["subprofile_similarity_pct"].items():
                    print(f"    - {grp.replace('_', ' ').title()}: {score}%")
            print("-" * 50)


if __name__ == "__main__":
    main()
