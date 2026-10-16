"""
CRIME DNA — Behavioral Similarity Engine Configuration
"""

import os
from typing import Dict, Any

# Root paths
SIMILARITY_DIR = "data/processed/similarity_index"
INDEX_MODEL_PATH = os.path.join(SIMILARITY_DIR, "knn_index.joblib")
FEATURE_MATRIX_PATH = os.path.join(SIMILARITY_DIR, "normalized_dna_matrix.npy")
INCIDENT_IDS_PATH = os.path.join(SIMILARITY_DIR, "incident_ids.json")
METADATA_PATH = os.path.join(SIMILARITY_DIR, "similarity_engine_metadata.json")

# Default similarity algorithm parameters
SIMILARITY_CONFIG: Dict[str, Any] = {
    "metric": "cosine",
    "algorithm": "brute",  # Exact cosine similarity with normalized vectors
    "n_neighbors_default": 5,
    "max_neighbors": 50,
    "n_jobs": -1,
    "vector_dim": 70,
    "normalize_l2": True
}

# Sub-profile weights for explainable similarity breakdown
SUBPROFILE_WEIGHTS: Dict[str, float] = {
    "temporal_dynamics": 1.0,
    "crime_characteristics": 1.0,
    "location_and_environment": 1.0,
    "method_and_activity": 1.0,
    "people_and_demographics": 1.0,
    "property_and_economics": 1.0,
    "context_and_harm": 1.0,
}
