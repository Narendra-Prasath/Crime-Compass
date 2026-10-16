"""
CRIME DNA — Phase 11: Backend API Configuration

Provides environment-aware configuration settings for the FastAPI application.
All paths are resolved relative to the workspace root without hardcoded absolute paths,
and can be overridden via environment variables.
"""

import os
from pathlib import Path
from typing import List


# Dynamically resolve workspace root (3 levels up from src/api/config.py)
DEFAULT_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE_ROOT = Path(os.getenv("CRIME_DNA_WORKSPACE_ROOT", str(DEFAULT_WORKSPACE_ROOT)))

# Data Directories
DATA_DIR = Path(os.getenv("CRIME_DNA_DATA_DIR", str(WORKSPACE_ROOT / "data")))
PROCESSED_DIR = Path(os.getenv("CRIME_DNA_PROCESSED_DIR", str(DATA_DIR / "processed")))

# Model & Artifact Directories
SIMILARITY_DIR = Path(os.getenv("CRIME_DNA_SIMILARITY_DIR", str(PROCESSED_DIR / "similarity_index")))
CLUSTERS_DIR = Path(os.getenv("CRIME_DNA_CLUSTERS_DIR", str(PROCESSED_DIR / "clusters")))
CROSS_CRIME_DIR = Path(os.getenv("CRIME_DNA_CROSS_CRIME_DIR", str(PROCESSED_DIR / "cross_crime")))
EVOLUTION_DIR = Path(os.getenv("CRIME_DNA_EVOLUTION_DIR", str(PROCESSED_DIR / "evolution")))
ANOMALY_DIR = Path(os.getenv("CRIME_DNA_ANOMALY_DIR", str(PROCESSED_DIR / "anomaly")))
EXPLAINABILITY_DIR = Path(os.getenv("CRIME_DNA_EXPLAIN_DIR", str(PROCESSED_DIR / "explainability")))

# File Paths
CLEANED_CSV_PATH = Path(os.getenv("CRIME_DNA_CLEANED_CSV", str(PROCESSED_DIR / "crime_dna_cleaned.csv")))
DNA_FEATURES_CSV_PATH = Path(os.getenv("CRIME_DNA_FEATURES_CSV", str(PROCESSED_DIR / "crime_dna_behavioral_features.csv")))
CLEANING_METADATA_PATH = Path(os.getenv("CRIME_DNA_CLEANING_META", str(PROCESSED_DIR / "cleaning_metadata.json")))
DNA_METADATA_PATH = Path(os.getenv("CRIME_DNA_DNA_META", str(PROCESSED_DIR / "behavioral_dna_metadata.json")))

# API Server Settings
API_TITLE = "Crime Compass 🧭 — Behavioral Pattern Analyzer API"
API_VERSION = "2.0.0"
API_DESCRIPTION = (
    "Crime Compass helps users analyze crime incident data, discover behavioral similarities, "
    "explore patterns across crime categories, and understand how incidents compare with historical records."
)

HOST = os.getenv("CRIME_DNA_HOST", "0.0.0.0")
PORT = int(os.getenv("CRIME_DNA_PORT", "8000"))
DEBUG = os.getenv("CRIME_DNA_DEBUG", "false").lower() in ("1", "true", "yes")

# CORS Configuration
CORS_ORIGINS_RAW = os.getenv("CRIME_DNA_CORS_ORIGINS", "*")
CORS_ORIGINS: List[str] = [origin.strip() for origin in CORS_ORIGINS_RAW.split(",") if origin.strip()]

# Query Limits
DEFAULT_TOP_K = 5
MAX_TOP_K = 50
DEFAULT_OUTLIER_LIMIT = 50
MAX_OUTLIER_LIMIT = 200
