"""
CRIME DNA — Phase 9: Behavioral Anomaly & Novelty Detection Configuration
"""

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data/processed")
ANOMALY_DIR = os.path.join(DATA_PROCESSED_DIR, "anomaly")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs/figures")

# Input file paths
BEHAVIORAL_FEATURES_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_behavioral_features.csv")
CLUSTER_MODEL_PATH = os.path.join(DATA_PROCESSED_DIR, "clusters/kmeans_model.joblib")
CLUSTER_LABELS_PATH = os.path.join(DATA_PROCESSED_DIR, "clusters/incident_cluster_labels.csv")
CLUSTER_PROFILES_PATH = os.path.join(DATA_PROCESSED_DIR, "clusters/cluster_profiles.json")

# Output artifact paths
MODEL_PATH = os.path.join(ANOMALY_DIR, "isolation_forest.joblib")
SCORES_CSV_PATH = os.path.join(ANOMALY_DIR, "incident_anomaly_scores.csv")
TOP_OUTLIERS_JSON_PATH = os.path.join(ANOMALY_DIR, "top_behavioral_outliers.json")
ANOMALY_SUMMARY_PATH = os.path.join(ANOMALY_DIR, "anomaly_metadata.json")
ANOMALY_CHART_PATH = os.path.join(FIGURES_DIR, "16_behavioral_anomaly_distribution.png")

# Detection hyperparameters & threshold calibrations
ANOMALY_CONFIG = {
    "n_estimators": 100,
    "max_samples": 1024,
    "contamination": 0.01,
    "random_state": 42,
    "n_jobs": -1,
    "weight_centroid_dist": 0.5,
    "weight_isolation_score": 0.5,
    # Quantile-based threshold definitions
    "threshold_moderate_quantile": 0.95,   # Top 5%
    "threshold_high_quantile": 0.99,       # Top 1%
    "threshold_extreme_quantile": 0.999,   # Top 0.1%
    "top_unusual_features_count": 5
}

# Neutral terminology labels
ANOMALY_TIER_LABELS = {
    "standard": "Standard Behavioral Pattern",
    "moderate": "Moderate Behavioral Novelty",
    "high": "High Behavioral Outlier",
    "extreme": "Extreme Behavioral Outlier"
}
