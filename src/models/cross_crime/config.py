"""
CRIME DNA — Phase 7: Cross-Crime Pattern Analysis Configuration
"""

import os

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data/processed")
CROSS_CRIME_DIR = os.path.join(DATA_PROCESSED_DIR, "cross_crime")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs/figures")

# Input file paths
BEHAVIORAL_FEATURES_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_behavioral_features.csv")
CLUSTER_LABELS_PATH = os.path.join(DATA_PROCESSED_DIR, "clusters/incident_cluster_labels.csv")
CLUSTER_METADATA_PATH = os.path.join(DATA_PROCESSED_DIR, "clusters/cluster_metadata.json")
CLEANED_DATA_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_cleaned.csv")

# Output artifact paths
PATTERNS_JSON_PATH = os.path.join(CROSS_CRIME_DIR, "cross_crime_patterns.json")
SUMMARY_JSON_PATH = os.path.join(CROSS_CRIME_DIR, "cross_crime_summary.json")
MATRIX_CHART_PATH = os.path.join(FIGURES_DIR, "14_cross_crime_matrix.png")

# Analysis parameters
CROSS_CRIME_CONFIG = {
    "min_category_incidents": 10,       # Minimum incident count for category representation
    "similarity_metric": "cosine",
    "top_exemplars_per_category": 3,    # Number of representative incidents per category
    "top_features_count": 8,            # Top distinctive features per pattern
    "random_state": 42
}

# Crime category mapping from one-hot columns to standardized labels
CRIME_CATEGORY_MAPPING = {
    "crime_against_person": "Violent Offense Against Person",
    "crime_against_property": "Property Offense",
    "crime_against_society": "Societal / Public Order Offense",
    "crime_against_person___property": "Violent Robbery / Confrontational Property Crime",
    "crime_against_person___society": "Interpersonal Disorder / Resisting Offense",
    "crime_against_property___society": "Vandalism / Contraband Property Offense",
    "crime_against_person___property___society": "Compound Multi-Tier Crime"
}

CATEGORY_SHORT_NAMES = {
    "crime_against_person": "Person",
    "crime_against_property": "Property",
    "crime_against_society": "Society",
    "crime_against_person___property": "Person + Property",
    "crime_against_person___society": "Person + Society",
    "crime_against_property___society": "Property + Society",
    "crime_against_person___property___society": "Person + Property + Society"
}
