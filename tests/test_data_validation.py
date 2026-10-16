"""
Data Validation Test Suite for CRIME DNA (Phase 14).

Tests:
- Missing critical values
- Duplicate incident IDs
- Valid range constraints (hours, months, weekdays, population, property value)
- Preprocessing & Behavioral DNA encoding reproducibility
- Feature value bounds [0, 1] and L2 normalization correctness
"""

import os
import pytest
import numpy as np
import pandas as pd

from src.features.dna_encoder import BehavioralDNAEncoder

CLEANED_CSV_PATH = "data/processed/crime_dna_cleaned.csv"
BEHAVIORAL_CSV_PATH = "data/processed/crime_dna_behavioral_features.csv"
NORMALIZED_MATRIX_PATH = "data/processed/similarity_index/normalized_dna_matrix.npy"


@pytest.fixture(scope="module")
def cleaned_df():
    assert os.path.exists(CLEANED_CSV_PATH), f"Cleaned dataset missing at {CLEANED_CSV_PATH}"
    return pd.read_csv(CLEANED_CSV_PATH, low_memory=False)


@pytest.fixture(scope="module")
def behavioral_df():
    assert os.path.exists(BEHAVIORAL_CSV_PATH), f"Behavioral DNA features missing at {BEHAVIORAL_CSV_PATH}"
    return pd.read_csv(BEHAVIORAL_CSV_PATH, low_memory=False)


def test_cleaned_dataset_integrity(cleaned_df):
    """Verify absence of duplicates, missing critical values, and valid ranges."""
    assert len(cleaned_df) == 220663, f"Expected 220,663 rows, found {len(cleaned_df)}"
    
    # Duplicate check
    assert cleaned_df["incident_id"].duplicated().sum() == 0, "Duplicate incident_ids detected"
    
    # Missing critical values
    critical_cols = ["incident_id", "incident_hour", "incident_month", "incident_weekday"]
    for col in critical_cols:
        assert cleaned_df[col].isna().sum() == 0, f"Critical column {col} contains missing values"
        
    # Range constraints
    assert ((cleaned_df["incident_hour"] >= 0) & (cleaned_df["incident_hour"] <= 23)).all(), "Invalid incident_hour"
    assert ((cleaned_df["incident_month"] >= 1) & (cleaned_df["incident_month"] <= 12)).all(), "Invalid incident_month"
    assert ((cleaned_df["incident_weekday"] >= 0) & (cleaned_df["incident_weekday"] <= 6)).all(), "Invalid incident_weekday"
    assert (cleaned_df["population"] >= 0).all(), "Negative population values detected"
    assert (cleaned_df["property_value"].dropna() >= 0).all(), "Negative property_value detected"


def test_behavioral_features_bounds(behavioral_df):
    """Verify Behavioral DNA vectors: bounds in [0, 1], 70 dimensions, no NaNs or Infs."""
    assert len(behavioral_df) == 220663
    feature_cols = [c for c in behavioral_df.columns if c != "incident_id"]
    assert len(feature_cols) == 70, f"Expected 70 behavioral dimensions, found {len(feature_cols)}"
    
    mat = behavioral_df[feature_cols].values
    assert not np.isnan(mat).any(), "NaNs detected in behavioral feature matrix"
    assert not np.isinf(mat).any(), "Infs detected in behavioral feature matrix"
    assert mat.min() >= -1e-6, f"Feature minimum < 0: {mat.min()}"
    assert mat.max() <= 1.0 + 1e-6, f"Feature maximum > 1: {mat.max()}"


def test_l2_normalization_matrix():
    """Verify L2 unit norm invariant of the precomputed similarity matrix."""
    assert os.path.exists(NORMALIZED_MATRIX_PATH), f"Normalized matrix missing at {NORMALIZED_MATRIX_PATH}"
    matrix = np.load(NORMALIZED_MATRIX_PATH)
    
    assert matrix.shape == (220663, 70)
    norms = np.linalg.norm(matrix, axis=1)
    # Every non-zero row should have L2 norm within 1e-4 of 1.0
    valid_norms = norms[norms > 1e-6]
    assert np.allclose(valid_norms, 1.0, atol=1e-4), "L2 normalization violated in feature matrix"


def test_preprocessing_reproducibility(cleaned_df):
    """Verify feature extraction reproduces exact numerical values deterministically."""
    sample = cleaned_df.head(200).copy()
    encoder = BehavioralDNAEncoder()
    
    res1 = encoder.transform(sample)
    res2 = encoder.transform(sample)
    
    feature_cols = [c for c in res1.columns if c != "incident_id"]
    mat1 = np.asarray(res1[feature_cols].values, dtype=float)
    mat2 = np.asarray(res2[feature_cols].values, dtype=float)
    
    np.testing.assert_allclose(mat1, mat2, atol=1e-7, err_msg="Feature extraction is not deterministic")
