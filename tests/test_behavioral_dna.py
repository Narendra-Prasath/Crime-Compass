"""
Unit and Integration Tests for CRIME DNA Phase 3 Behavioral DNA Pipeline
"""

import os
import json
import unittest
import numpy as np
import pandas as pd

from src.features.config import (
    FEATURE_GROUPS,
    FEATURE_DESCRIPTIONS,
    SCALING_PARAMS
)
from src.features.dna_encoder import BehavioralDNAEncoder


class TestBehavioralDNAEncoder(unittest.TestCase):
    """Unit tests for the Behavioral DNA feature engineering logic."""

    def setUp(self):
        """Create a mock cleaned DataFrame matching the schema from Phase 2."""
        self.encoder = BehavioralDNAEncoder()
        
        # 4 representative mock incidents
        self.mock_cleaned_data = pd.DataFrame({
            "incident_id": ["INC_000001", "INC_000002", "INC_000003", "INC_000004"],
            "agency_id": [101, 102, 103, 104],
            "incident_hour": [2, 14, 23, 0],
            "incident_month": [1, 6, 12, 4],
            "incident_day": [15, 2, 28, 10],
            "incident_weekday": [5, 1, 6, 0],
            "is_weekend": [1, 0, 1, 0],
            "is_night": [1, 0, 1, 1],
            "incident_quarter": [1, 2, 4, 2],
            "crime_against_person": [1, 0, 0, 0],
            "crime_against_property": [0, 1, 0, 0],
            "crime_against_society": [0, 0, 1, 0],
            "crime_against_person___property": [0, 0, 0, 1],
            "crime_against_person___society": [0, 0, 0, 0],
            "crime_against_property___society": [0, 0, 0, 0],
            "crime_against_person___property___society": [0, 0, 0, 0],
            "offense_count": [1, 3, 2, 4],
            "offense_categories_count": [1, 2, 1, 3],
            "attempted_count": [0, 1, 0, 0],
            "location_count": [1, 2, 1, 1],
            "population": [50000, 150000, 2500, 80000],
            "agency_type_name_state_police": [0, 0, 1, 0],
            "has_weapon": [1, 0, 0, 1],
            "weapon_count": [1.0, 0.0, 0.0, 2.0],
            "weapon_types_count": [1, 0, 0, 2],
            "has_criminal_activity": [0, 0, 1, 0],
            "criminal_activity_count": [0.0, 0.0, 2.0, 0.0],
            "has_relationship": [1, 0, 0, 0],
            "relationship_count": [1.0, 0.0, 0.0, 0.0],
            "victim_count": [1, 2, 1, 3],
            "victim_age_known": [1, 0, 1, 1],
            "victim_avg_age": [34.0, np.nan, 21.0, 45.0],
            "victim_min_age": [34.0, np.nan, 21.0, 20.0],
            "victim_max_age": [34.0, np.nan, 21.0, 60.0],
            "victim_sexes_count": [1, 2, 1, 2],
            "victim_types_count": [1, 1, 1, 2],
            "offender_count": [1, 2, 1, 4],
            "offender_age_known": [1, 1, 0, 1],
            "offender_avg_age": [28.0, 22.0, np.nan, 30.0],
            "offender_min_age": [28.0, 20.0, np.nan, 25.0],
            "offender_max_age": [28.0, 24.0, np.nan, 35.0],
            "offender_sexes_count": [1, 2, 1, 2],
            "has_property": [0, 1, 0, 1],
            "property_record_count": [0.0, 2.0, 0.0, 3.0],
            "stolen_count": [0.0, 4.0, 0.0, 8.0],
            "property_value_log": [0.0, 7.82, 0.0, 11.2],
            "cargo_theft_flag_t": [0, 0, 0, 1],
            "has_injury": [1, 0, 0, 0],
            "injury_record_count": [1.0, 0.0, 0.0, 0.0],
            "has_drug": [0, 0, 1, 0],
            "suspected_drug_count": [0.0, 0.0, 2.0, 0.0],
            "estimated_drug_quantity": [0.0, 0.0, 50.0, 0.0],
            "bias_count": [1, 1, 2, 1],
            "has_arrest": [1, 0, 1, 0],
            "arrest_count": [1.0, 0.0, 1.0, 0.0],
            # Add population group desc columns
            "population_group_desc_cities_from_10,000_thru_24,999": [0, 0, 0, 0],
            "population_group_desc_cities_from_100,000_thru_249,999": [0, 1, 0, 0],
            "population_group_desc_cities_from_2,500_thru_9,999": [0, 0, 1, 0],
            "population_group_desc_cities_from_25,000_thru_49,999": [0, 0, 0, 0],
            "population_group_desc_cities_from_50,000_thru_99,999": [1, 0, 0, 1],
            "population_group_desc_cities_under_2,500": [0, 0, 0, 0],
            "population_group_desc_msa_counties_100,000_or_over": [0, 0, 0, 0],
            "population_group_desc_msa_counties_from_10,000_thru_24,999": [0, 0, 0, 0],
            "population_group_desc_msa_counties_from_25,000_thru_99,999": [0, 0, 0, 0],
            "population_group_desc_msa_counties_under_10,000": [0, 0, 0, 0],
            "population_group_desc_non_msa_state_police": [0, 0, 0, 0],
            "population_group_desc_non_msa_counties_from_10,000_thru_24,999": [0, 0, 0, 0],
            "population_group_desc_non_msa_counties_from_25,000_thru_99,999": [0, 0, 0, 0],
            "population_group_desc_non_msa_counties_under_10,000": [0, 0, 0, 0]
        })

    def test_feature_generation_dimension_and_names(self):
        """Verify encoder produces exactly 70 features plus incident_id."""
        dna_df = self.encoder.transform(self.mock_cleaned_data)
        self.assertEqual(dna_df.shape[0], 4)
        self.assertEqual(dna_df.shape[1], 71)  # 1 ID + 70 features
        self.assertIn("incident_id", dna_df.columns)
        
        feature_cols = [c for c in dna_df.columns if c != "incident_id"]
        self.assertEqual(len(feature_cols), 70)
        self.assertEqual(feature_cols, self.encoder.all_feature_names)

    def test_feature_bounds_and_no_missing_values(self):
        """Verify all feature values are strictly in [0.0, 1.0] with zero NaNs."""
        dna_df = self.encoder.transform(self.mock_cleaned_data)
        feature_cols = [c for c in dna_df.columns if c != "incident_id"]
        
        # Check no missing values
        null_count = dna_df[feature_cols].isna().sum().sum()
        self.assertEqual(null_count, 0, "Behavioral DNA must contain zero NaN values")
        
        # Check min/max bounds
        min_val = dna_df[feature_cols].min().min()
        max_val = dna_df[feature_cols].max().max()
        self.assertGreaterEqual(min_val, 0.0, "Feature values must be >= 0.0")
        self.assertLessEqual(max_val, 1.0, "Feature values must be <= 1.0")

    def test_cyclical_hour_proximity(self):
        """Verify that 23:00 and 00:00 have close representations in cyclical space."""
        dna_df = self.encoder.transform(self.mock_cleaned_data)
        # Row 2 is 23:00, Row 3 is 00:00
        h23_sin, h23_cos = dna_df.loc[2, ["time_hour_sin", "time_hour_cos"]]
        h00_sin, h00_cos = dna_df.loc[3, ["time_hour_sin", "time_hour_cos"]]
        
        dist_23_00 = np.sqrt((h23_sin - h00_sin)**2 + (h23_cos - h00_cos)**2)
        
        # Row 1 is 14:00 (2 PM)
        h14_sin, h14_cos = dna_df.loc[1, ["time_hour_sin", "time_hour_cos"]]
        dist_23_14 = np.sqrt((h23_sin - h14_sin)**2 + (h23_cos - h14_cos)**2)
        
        self.assertLess(dist_23_00, dist_23_14, "23:00 must be closer to 00:00 than to 14:00")

    def test_feature_groups_integrity(self):
        """Verify all 7 feature groups are represented and mutually exclusive."""
        all_features = []
        for grp_name, feat_list in FEATURE_GROUPS.items():
            self.assertGreater(len(feat_list), 0, f"Group {grp_name} cannot be empty")
            all_features.extend(feat_list)
            
        self.assertEqual(len(all_features), 70)
        self.assertEqual(len(set(all_features)), 70, "Feature names must be unique across all groups")


class TestCleanedDatasetIntegration(unittest.TestCase):
    """Integration test verifying Phase 3 generated files."""

    FEATURES_CSV = "data/processed/crime_dna_behavioral_features.csv"
    NAMES_JSON = "data/processed/behavioral_dna_feature_names.json"
    METADATA_JSON = "data/processed/behavioral_dna_metadata.json"

    def test_output_artifacts_exist_and_consistent(self):
        """Verify the generated Behavioral DNA dataset exists with 70 features."""
        if not os.path.exists(self.FEATURES_CSV):
            self.skipTest(f"{self.FEATURES_CSV} not yet generated.")

        # Check names JSON
        with open(self.NAMES_JSON) as f:
            names = json.load(f)
        self.assertEqual(len(names), 70)

        # Check metadata JSON
        with open(self.METADATA_JSON) as f:
            meta = json.load(f)
        self.assertEqual(meta["total_records"], 220663)
        self.assertEqual(meta["total_behavioral_features"], 70)
        self.assertEqual(meta["feature_groups_count"], 7)

        # Quick check on sample rows from CSV
        sample_df = pd.read_csv(self.FEATURES_CSV, nrows=50)
        self.assertEqual(sample_df.shape[1], 71)
        self.assertIn("incident_id", sample_df.columns)
        self.assertEqual(sample_df.isna().sum().sum(), 0)


if __name__ == "__main__":
    unittest.main()
