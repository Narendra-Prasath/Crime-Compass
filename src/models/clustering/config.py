"""
CRIME DNA — Behavioral Clustering Configuration & Cluster Archetype Dictionary
"""

import os
from typing import Dict, Any

CLUSTERS_DIR = "data/processed/clusters"
MODEL_PATH = os.path.join(CLUSTERS_DIR, "kmeans_model.joblib")
LABELS_PATH = os.path.join(CLUSTERS_DIR, "incident_cluster_labels.csv")
PROFILES_PATH = os.path.join(CLUSTERS_DIR, "cluster_profiles.json")
METADATA_PATH = os.path.join(CLUSTERS_DIR, "cluster_metadata.json")

CLUSTERING_CONFIG: Dict[str, Any] = {
    "algorithm": "MiniBatchKMeans",
    "n_clusters": 8,
    "batch_size": 4096,
    "random_state": 42,
    "n_init": 5,
    "max_iter": 300,
    "reassignment_ratio": 0.01,
}

# Semantic archetype definitions for each cluster based on empirical centroid profiling
CLUSTER_ARCHETYPES: Dict[int, Dict[str, str]] = {
    0: {
        "name": "Small-City Property & Structure Theft",
        "category": "Property",
        "summary": "Opportunistic property and structure offenses occurring predominantly in small municipal jurisdictions (10k-25k population)."
    },
    1: {
        "name": "Violent Armed Interpersonal & Domestic Assaults",
        "category": "Violent Person",
        "summary": "High-lethality violent encounters against persons characterized by weapon brandishing, prior relationship ties, and physical bodily injury."
    },
    2: {
        "name": "Suburban & Mid-Sized Town Daytime Property Theft",
        "category": "Property",
        "summary": "Daytime property offenses and larcenies occurring across suburban municipalities and mid-sized cities (25k-50k population)."
    },
    3: {
        "name": "Nocturnal & Weekend Residential/Commercial Burglary",
        "category": "Property / Stealth",
        "summary": "Property break-ins and burglaries committed during weekend and nocturnal hours with elevated economic property damage."
    },
    4: {
        "name": "Weekend Nightlife Vice & Public Order Enforcement",
        "category": "Society / Vice",
        "summary": "Weekend societal infractions, nightlife vice operations, and public disorder incidents with high on-scene arrest rates."
    },
    5: {
        "name": "Regulatory & Non-Drug Societal Enterprise Offenses",
        "category": "Society / Regulatory",
        "summary": "Public order, weapons violations, and non-narcotics enterprise activities resulting in formal citations and arrests."
    },
    6: {
        "name": "Metropolitan Core High-Density Larceny & Shoplifting",
        "category": "Property / Urban",
        "summary": "Daytime retail thefts, grand larcenies, and property offenses concentrated in dense metropolitan core cities (100k-250k population)."
    },
    7: {
        "name": "Narcotics Trafficking & Contraband Vice Operations",
        "category": "Society / Narcotics",
        "summary": "Proactive law enforcement operations seizing illicit narcotics, controlled substances, and contraband with high on-scene arrest rates."
    }
}
