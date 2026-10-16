"""
CRIME DNA — Phase 8: Behavioral Pattern Evolution Configuration
"""

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data/processed")
EVOLUTION_DIR = os.path.join(DATA_PROCESSED_DIR, "evolution")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs/figures")

# Input file paths
BEHAVIORAL_FEATURES_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_behavioral_features.csv")
CLUSTER_LABELS_PATH = os.path.join(DATA_PROCESSED_DIR, "clusters/incident_cluster_labels.csv")
CLEANED_DATA_PATH = os.path.join(DATA_PROCESSED_DIR, "crime_dna_cleaned.csv")

# Output artifact paths
TEMPORAL_PROFILES_PATH = os.path.join(EVOLUTION_DIR, "temporal_behavioral_profiles.json")
CLUSTER_EVOLUTION_PATH = os.path.join(EVOLUTION_DIR, "cluster_evolution.json")
FEATURE_TRENDS_PATH = os.path.join(EVOLUTION_DIR, "feature_trends.json")
SIGNIFICANT_SHIFTS_PATH = os.path.join(EVOLUTION_DIR, "significant_shifts.json")
TIMELINE_DASHBOARD_PATH = os.path.join(EVOLUTION_DIR, "timeline_dashboard.json")
EVOLUTION_CHART_PATH = os.path.join(FIGURES_DIR, "15_temporal_evolution.png")

# Chronological labels
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

QUARTER_NAMES = {
    1: "Q1 (Winter)",
    2: "Q2 (Spring)",
    3: "Q3 (Summer)",
    4: "Q4 (Fall / Holiday)"
}

# Behavioral feature domains to track chronologically
FEATURE_DOMAINS = {
    "temporal_dynamics": ["is_night", "is_weekend", "incident_hour"],
    "location_urban_context": ["population"],
    "weapon_patterns": ["has_weapon"],
    "crime_macro_categories": [
        "crime_against_person",
        "crime_against_property",
        "crime_against_society"
    ],
    "property_economic": ["has_property"],
    "interpersonal_dynamics": ["has_relationship"],
    "harm_and_enforcement": ["has_injury", "has_drug", "has_arrest", "has_criminal_activity"]
}

EVOLUTION_CONFIG = {
    "significance_alpha": 0.05,
    "high_significance_alpha": 0.001,
    "min_shift_magnitude": 0.015   # 1.5% absolute shift for primary highlight
}
