"""
Unit and Integration Tests for CRIME DNA Phase 2 Preprocessing Pipeline
"""

import os
import unittest
import numpy as np
import pandas as pd

from src.data.cleaner import (
    CONSTANT_COLUMNS,
    REDUNDANT_COLUMNS,
    IDENTIFIER_COLUMNS,
    POST_INCIDENT_OUTCOME_COLUMNS,
    add_incident_identifier,
    drop_uninformative_columns,
    correct_encoding_artifacts,
    handle_missing_and_sentinels,
    categorize_columns
)


class TestPreprocessingPipeline(unittest.TestCase):
    """Unit tests for individual pipeline transformation components."""

    def setUp(self):
        """Create a representative mock DataFrame."""
        self.mock_data = pd.DataFrame({
            "agency_id": [101, 102, 103, 104],
            "incident_year": [2024, 2024, 2024, 2024],          # Constant
            "cargo_theft_flag_nan": [0, 0, 0, 0],               # Constant
            "offense_count": [1, 2, 1, 3],
            "offense_names_count": [1, 2, 1, 3],                # Redundant collinear
            "location_count": [1, 1, 2, 1],
            "location_type_count": [1, 1, 2, 1],                # Redundant collinear
            "location_types_count": [1, 1, 2, 1],               # Redundant collinear
            "has_weapon": [0, 1, 0, 1],
            "weapon_types_count": [1, 2, 1, 1],                 # Upstream artifact (1 on unarmed)
            "has_drug": [0, 1, 0, 0],
            "drug_types_count": [1, 2, 1, 1],                   # Upstream artifact (1 on drug-free)
            "has_arrest": [0, 1, 0, 1],
            "arrestee_age_known": [0, 1, 0, 0],
            "arrestee_avg_age": [35.0, 28.0, 35.0, 0.0],       # Artificial 35.0 on non-arrest
            "victim_age_known": [1, 0, 1, 0],
            "victim_avg_age": [42.0, 0.0, 19.0, 0.0],
            "victim_min_age": [42.0, 0.0, 19.0, 0.0],
            "victim_max_age": [42.0, 0.0, 19.0, 0.0],
            "offender_age_known": [1, 1, 0, 1],
            "offender_avg_age": [30.0, 25.0, 0.0, 45.0],
            "offender_min_age": [30.0, 25.0, 0.0, 45.0],
            "offender_max_age": [30.0, 25.0, 0.0, 45.0],
            "property_value": [500.0, 999999999.0, 0.0, 1200.0] # NIBRS sentinel
        })

    def test_add_incident_identifier(self):
        """Verify deterministic generation of unique primary key incident_id."""
        df_res = add_incident_identifier(self.mock_data)
        self.assertIn("incident_id", df_res.columns)
        self.assertEqual(df_res["incident_id"].iloc[0], "INC_000001")
        self.assertEqual(df_res["incident_id"].iloc[3], "INC_000004")
        self.assertEqual(df_res["incident_id"].nunique(), len(df_res))

    def test_drop_uninformative_columns(self):
        """Verify zero-variance and redundant collinear columns are removed."""
        df_res, dropped = drop_uninformative_columns(self.mock_data)
        for col in ["incident_year", "cargo_theft_flag_nan", "offense_names_count", "location_type_count"]:
            self.assertNotIn(col, df_res.columns)
        self.assertIn("offense_count", df_res.columns)
        self.assertIn("location_count", df_res.columns)

    def test_correct_encoding_artifacts(self):
        """Verify correction of weapon, drug, and arrestee age artifacts."""
        df_res = correct_encoding_artifacts(self.mock_data)

        # Unarmed weapon_types_count must be 0
        self.assertEqual(df_res.loc[df_res["has_weapon"] == 0, "weapon_types_count"].tolist(), [0, 0])
        # Armed weapon_types_count must remain intact
        self.assertEqual(df_res.loc[df_res["has_weapon"] == 1, "weapon_types_count"].tolist(), [2, 1])

        # Drug-free drug_types_count must be 0
        self.assertEqual(df_res.loc[df_res["has_drug"] == 0, "drug_types_count"].tolist(), [0, 0, 0])
        # Drug-involved must remain intact
        self.assertEqual(df_res.loc[df_res["has_drug"] == 1, "drug_types_count"].tolist(), [2])

        # Non-arrest arrestee_avg_age must be NaN, NOT 35.0
        no_arrest_ages = df_res.loc[df_res["has_arrest"] == 0, "arrestee_avg_age"]
        self.assertTrue(no_arrest_ages.isna().all())

        # Unknown arrestee age on arrest must be NaN
        unknown_arrest_age = df_res.loc[3, "arrestee_avg_age"]
        self.assertTrue(np.isnan(unknown_arrest_age))

        # Known arrestee age must remain intact
        self.assertEqual(df_res.loc[1, "arrestee_avg_age"], 28.0)

    def test_handle_missing_and_sentinels(self):
        """Verify unknown ages and sentinel property values are converted to NaN."""
        df_res = handle_missing_and_sentinels(self.mock_data)

        # Unknown victim ages must be NaN
        self.assertTrue(np.isnan(df_res.loc[1, "victim_avg_age"]))
        self.assertEqual(df_res.loc[0, "victim_avg_age"], 42.0)

        # Unknown offender ages must be NaN
        self.assertTrue(np.isnan(df_res.loc[2, "offender_avg_age"]))
        self.assertEqual(df_res.loc[0, "offender_avg_age"], 30.0)

        # Sentinel property value 999999999.0 must be NaN
        self.assertTrue(np.isnan(df_res.loc[1, "property_value"]))
        self.assertEqual(df_res.loc[0, "property_value"], 500.0)

    def test_categorize_columns(self):
        """Verify columns are partitioned into valid architectural buckets."""
        cols = [
            "incident_id", "agency_id", "incident_hour", "offense_count",
            "victim_count", "offender_count", "has_weapon", "has_property",
            "county_name_baldwin", "has_arrest"
        ]
        groups = categorize_columns(cols)
        self.assertIn("incident_id", groups["identifiers"])
        self.assertIn("agency_id", groups["identifiers"])
        self.assertIn("incident_hour", groups["temporal_features"])
        self.assertIn("has_weapon", groups["weapon_violence_features"])
        self.assertIn("has_arrest", groups["post_incident_outcomes"])
        self.assertIn("county_name_baldwin", groups["environmental_geographic_features"])


class TestCleanedDatasetIntegrity(unittest.TestCase):
    """Integration test verifying properties of the actual saved cleaned dataset."""

    CLEANED_CSV_PATH = "data/processed/crime_dna_cleaned.csv"
    RAW_CSV_PATH = "crime_dna_ml.csv"

    def test_cleaned_file_properties(self):
        """Verify row count, column count, dropped columns, and integrity constraints."""
        if not os.path.exists(self.CLEANED_CSV_PATH):
            self.skipTest(f"{self.CLEANED_CSV_PATH} not found.")

        df = pd.read_csv(self.CLEANED_CSV_PATH, nrows=5000)

        # Dimension checks
        self.assertEqual(df.shape[1], 196, "Expected exactly 196 columns in cleaned dataset")
        self.assertIn("incident_id", df.columns)

        # Verify all constant columns were removed
        for col in CONSTANT_COLUMNS:
            self.assertNotIn(col, df.columns, f"Constant column {col} was not removed")

        # Verify all collinear redundant columns were removed
        for col in REDUNDANT_COLUMNS:
            self.assertNotIn(col, df.columns, f"Redundant column {col} was not removed")

        # Verify weapon fix: when has_weapon == 0, weapon_types_count must be 0
        unarmed = df[df["has_weapon"] == 0]
        self.assertTrue((unarmed["weapon_types_count"] == 0).all(), "Unarmed incidents must have weapon_types_count == 0")

        # Verify drug fix: when has_drug == 0, drug_types_count must be 0
        nodrug = df[df["has_drug"] == 0]
        self.assertTrue((nodrug["drug_types_count"] == 0).all(), "Drug-free incidents must have drug_types_count == 0")

        # Verify arrestee age fix: when has_arrest == 0, arrestee_avg_age must NOT be 35.0 (must be NaN)
        no_arrest = df[df["has_arrest"] == 0]
        self.assertTrue(no_arrest["arrestee_avg_age"].isna().all(), "Non-arrest incidents must have NaN for arrestee_avg_age")

    def test_raw_dataset_untouched(self):
        """Verify the raw dataset file exists and has not been truncated or modified."""
        self.assertTrue(os.path.exists(self.RAW_CSV_PATH))
        self.assertGreater(os.path.getsize(self.RAW_CSV_PATH), 100 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
