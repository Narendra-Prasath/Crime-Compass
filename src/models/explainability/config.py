"""
CRIME DNA — Phase 10: Explainable AI (XAI) & Behavioral Attribution Configuration
"""

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data/processed")
EXPLAINABILITY_DIR = os.path.join(DATA_PROCESSED_DIR, "explainability")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs/figures")

# Input file paths
BEHAVIORAL_FEATURES_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_behavioral_features.csv")
FEATURE_NAMES_PATH = os.path.join(DATA_PROCESSED_DIR, "behavioral_dna_feature_names.json")
CLEANED_DATA_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_cleaned.csv")
SIMILARITY_INDEX_DIR = os.path.join(DATA_PROCESSED_DIR, "similarity_index")
KNN_MODEL_PATH = os.path.join(SIMILARITY_INDEX_DIR, "knn_index.joblib")

# Output artifact paths
SAMPLE_EXPLANATIONS_PATH = os.path.join(EXPLAINABILITY_DIR, "sample_explanations.json")
EXPLANATION_METADATA_PATH = os.path.join(EXPLAINABILITY_DIR, "explanation_metadata.json")
EXPLANATION_CHART_PATH = os.path.join(FIGURES_DIR, "17_behavioral_similarity_explanation.png")

# Human-readable labels for the 7 Behavioral DNA Groups
GROUP_DISPLAY_NAMES = {
    "temporal_dynamics": "Time",
    "location_and_environment": "Location",
    "crime_characteristics": "Crime Context",
    "method_and_activity": "Method / Weapon",
    "people_and_demographics": "People / Victim-Offender Context",
    "property_and_economics": "Property",
    "context_and_harm": "Activity & Context"
}

# Plain-English noun phrases for dynamic natural language explanations
GROUP_NOUN_PHRASES = {
    "temporal_dynamics": "time pattern",
    "location_and_environment": "location context",
    "property_and_economics": "property involvement",
    "method_and_activity": "weapon and operational method",
    "people_and_demographics": "victim-offender dynamics",
    "crime_characteristics": "crime context",
    "context_and_harm": "activity and enforcement context"
}

# Explanation parameters
EXPLAINABILITY_CONFIG = {
    "top_contributing_features_count": 6,
    "top_differing_features_count": 5,
    "min_feature_contribution_threshold": 0.005,
    "min_feature_difference_threshold": 0.05,
    "group_significance_ratio": 0.08  # Group must contribute at least 8% to be listed as a 'main' contributor
}
