"""
CRIME DNA — Phase 3: Behavioral DNA Feature Generation Pipeline

Transforms cleaned incident records into dense, bounded, normalized
Behavioral DNA representations suitable for similarity matching,
unsupervised clustering, and behavioral anomaly detection.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, List, Optional, Tuple

# Ensure workspace root is in sys.path for direct script execution
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import pandas as pd
import numpy as np

from src.features.config import (
    SCALING_PARAMS,
    FEATURE_GROUPS,
    FEATURE_DESCRIPTIONS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_FEATURES")


class BehavioralDNAEncoder:
    """
    Transforms raw cleaned incident records into standardized Behavioral DNA vectors.
    All features are strictly normalized to the [0.0, 1.0] interval.
    """

    def __init__(self, scaling_params: Optional[Dict[str, float]] = None):
        self.params = scaling_params or SCALING_PARAMS
        self.feature_groups = FEATURE_GROUPS
        self.all_feature_names = [f for grp in self.feature_groups.values() for f in grp]

    def _extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts cyclical trigonometric temporal patterns and diurnal flags."""
        feats = pd.DataFrame(index=df.index)
        
        # 24-hour diurnal cycle (mapped from [-1, 1] to [0, 1])
        feats["time_hour_sin"] = (np.sin(2.0 * np.pi * df["incident_hour"] / 24.0) + 1.0) / 2.0
        feats["time_hour_cos"] = (np.cos(2.0 * np.pi * df["incident_hour"] / 24.0) + 1.0) / 2.0
        
        # Annual seasonal cycle (mapped to [0, 1])
        feats["time_month_sin"] = (np.sin(2.0 * np.pi * (df["incident_month"] - 1.0) / 12.0) + 1.0) / 2.0
        feats["time_month_cos"] = (np.cos(2.0 * np.pi * (df["incident_month"] - 1.0) / 12.0) + 1.0) / 2.0
        
        # Weekly cycle (mapped to [0, 1])
        feats["time_weekday_sin"] = (np.sin(2.0 * np.pi * df["incident_weekday"] / 7.0) + 1.0) / 2.0
        feats["time_weekday_cos"] = (np.cos(2.0 * np.pi * df["incident_weekday"] / 7.0) + 1.0) / 2.0
        
        # Weekend and nocturnal execution indicators
        feats["time_is_weekend"] = df["is_weekend"].astype(float)
        feats["time_is_night"] = df["is_night"].astype(float)
        return feats

    def _extract_crime_characteristics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts target category violations, complexity, and attempt flags."""
        feats = pd.DataFrame(index=df.index)
        feats["crime_against_person"] = df["crime_against_person"].astype(float)
        feats["crime_against_property"] = df["crime_against_property"].astype(float)
        feats["crime_against_society"] = df["crime_against_society"].astype(float)
        feats["crime_against_person_property"] = df["crime_against_person___property"].astype(float)
        feats["crime_against_person_society"] = df["crime_against_person___society"].astype(float)
        feats["crime_against_property_society"] = df["crime_against_property___society"].astype(float)
        feats["crime_against_person_property_society"] = df["crime_against_person___property___society"].astype(float)
        
        # Offense volume and breadth
        cap_off = self.params["cap_offense_count"]
        feats["offense_count_scaled"] = np.clip(df["offense_count"] - 1.0, 0.0, cap_off - 1.0) / (cap_off - 1.0)
        
        cap_cat = self.params["cap_offense_categories"]
        feats["offense_categories_count_scaled"] = np.clip(df["offense_categories_count"] - 1.0, 0.0, cap_cat - 1.0) / (cap_cat - 1.0)
        
        feats["is_attempted"] = (df["attempted_count"] > 0).astype(float)
        return feats

    def _extract_location_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts scene complexity and environmental / urban hierarchy setting."""
        feats = pd.DataFrame(index=df.index)
        cap_loc = self.params["cap_location_count"]
        feats["location_count_scaled"] = np.clip(df["location_count"] - 1.0, 0.0, cap_loc - 1.0) / (cap_loc - 1.0)
        
        # Log-scaled population density
        max_pop = self.params["max_population"]
        feats["population_log_scaled"] = np.log1p(df["population"]) / np.log1p(max_pop)
        
        # Population scale categories from cleaned dataset
        pop_desc_cols = [c for c in df.columns if c.startswith("population_group_desc_")]
        for col in sorted(pop_desc_cols):
            feats[col] = df[col].astype(float)
            
        feats["agency_is_state_police"] = df["agency_type_name_state_police"].astype(float) if "agency_type_name_state_police" in df.columns else 0.0
        return feats

    def _extract_method_and_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts weapons deployment, criminal enterprise, and relationship dynamics."""
        feats = pd.DataFrame(index=df.index)
        feats["has_weapon"] = df["has_weapon"].astype(float)
        
        cap_wep = self.params["cap_weapon_count"]
        feats["weapon_count_scaled"] = np.clip(df["weapon_count"], 0.0, cap_wep) / cap_wep
        
        cap_wep_t = self.params["cap_weapon_types"]
        feats["weapon_types_count_scaled"] = np.clip(df["weapon_types_count"], 0.0, cap_wep_t) / cap_wep_t
        feats["is_multi_weapon"] = (df["weapon_count"] > 1).astype(float)
        
        feats["has_criminal_activity"] = df["has_criminal_activity"].astype(float)
        cap_act = self.params["cap_criminal_activities"]
        feats["criminal_activity_count_scaled"] = np.clip(df["criminal_activity_count"], 0.0, cap_act) / cap_act
        
        feats["has_relationship"] = df["has_relationship"].astype(float)
        cap_rel = self.params["cap_relationships"]
        feats["relationship_count_scaled"] = np.clip(df["relationship_count"], 0.0, cap_rel) / cap_rel
        return feats

    def _extract_people_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts victimology scale and offender group structure."""
        feats = pd.DataFrame(index=df.index)
        
        # Victims
        cap_vic = self.params["cap_victim_count"]
        feats["victim_count_scaled"] = np.clip(df["victim_count"] - 1.0, 0.0, cap_vic - 1.0) / (cap_vic - 1.0)
        feats["is_multi_victim"] = (df["victim_count"] > 1).astype(float)
        feats["victim_age_known"] = df["victim_age_known"].astype(float)
        
        # Median imputation when unknown, paired with victim_age_known indicator
        med_vic_age = self.params["median_victim_age"]
        vic_age_filled = df["victim_avg_age"].fillna(med_vic_age)
        feats["victim_avg_age_scaled"] = np.clip(vic_age_filled / 100.0, 0.0, 1.0)
        
        cap_vic_spread = self.params["cap_victim_age_spread"]
        vic_spread = np.clip(df["victim_max_age"] - df["victim_min_age"], 0.0, None).fillna(0.0)
        feats["victim_age_spread_scaled"] = np.clip(vic_spread / cap_vic_spread, 0.0, 1.0)
        
        feats["victim_sexes_count_scaled"] = np.clip(df["victim_sexes_count"] - 1.0, 0.0, 1.0)
        feats["victim_types_count_scaled"] = np.clip(df["victim_types_count"] - 1.0, 0.0, 1.0)
        
        # Offenders
        cap_off = self.params["cap_offender_count"]
        feats["offender_count_scaled"] = np.clip(df["offender_count"] - 1.0, 0.0, cap_off - 1.0) / (cap_off - 1.0)
        feats["is_co_offender"] = (df["offender_count"] > 1).astype(float)
        feats["offender_age_known"] = df["offender_age_known"].astype(float)
        
        med_off_age = self.params["median_offender_age"]
        off_age_filled = df["offender_avg_age"].fillna(med_off_age)
        feats["offender_avg_age_scaled"] = np.clip(off_age_filled / 100.0, 0.0, 1.0)
        
        cap_off_spread = self.params["cap_offender_age_spread"]
        off_spread = np.clip(df["offender_max_age"] - df["offender_min_age"], 0.0, None).fillna(0.0)
        feats["offender_age_spread_scaled"] = np.clip(off_spread / cap_off_spread, 0.0, 1.0)
        
        feats["offender_sexes_count_scaled"] = np.clip(df["offender_sexes_count"] - 1.0, 0.0, 1.0)
        return feats

    def _extract_property_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts financial and property targeting modus operandi."""
        feats = pd.DataFrame(index=df.index)
        feats["has_property"] = df["has_property"].astype(float)
        
        cap_prop_rec = self.params["cap_property_records"]
        feats["property_record_count_scaled"] = np.clip(df["property_record_count"], 0.0, cap_prop_rec) / cap_prop_rec
        
        feats["has_stolen_property"] = (df["stolen_count"] > 0).astype(float)
        cap_stolen = self.params["cap_stolen_count"]
        feats["stolen_count_scaled"] = np.clip(df["stolen_count"], 0.0, cap_stolen) / cap_stolen
        
        max_log_val = self.params["max_property_value_log"]
        feats["property_value_log_scaled"] = np.clip(df["property_value_log"].fillna(0.0) / max_log_val, 0.0, 1.0)
        
        feats["is_cargo_theft"] = df["cargo_theft_flag_t"].astype(float)
        return feats

    def _extract_context_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts injury, substance involvement, bias motivation, and on-scene resolution."""
        feats = pd.DataFrame(index=df.index)
        feats["has_injury"] = df["has_injury"].astype(float)
        
        cap_inj = self.params["cap_injury_records"]
        feats["injury_record_count_scaled"] = np.clip(df["injury_record_count"], 0.0, cap_inj) / cap_inj
        
        feats["has_drug"] = df["has_drug"].astype(float)
        cap_drg = self.params["cap_drug_records"]
        feats["suspected_drug_count_scaled"] = np.clip(df["suspected_drug_count"], 0.0, cap_drg) / cap_drg
        
        max_drg_qty = self.params["max_drug_quantity"]
        drug_qty_clean = df["estimated_drug_quantity"].fillna(0.0)
        feats["estimated_drug_quantity_log_scaled"] = np.clip(np.log1p(drug_qty_clean) / np.log1p(max_drg_qty), 0.0, 1.0)
        
        feats["has_bias_motivation"] = (df["bias_count"] > 1).astype(float)
        feats["has_arrest_on_scene"] = df["has_arrest"].astype(float)
        
        cap_arr = self.params["cap_arrest_count"]
        feats["arrest_count_scaled"] = np.clip(df["arrest_count"], 0.0, cap_arr) / cap_arr
        return feats

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes feature transformation pipeline on input cleaned DataFrame.
        Returns a DataFrame containing 'incident_id' followed by the 70 Behavioral DNA dimensions.
        """
        logger.info(f"Extracting Behavioral DNA vectors for {len(df)} incidents...")
        
        # Extract each sub-profile
        time_feats = self._extract_time_features(df)
        crime_feats = self._extract_crime_characteristics(df)
        loc_feats = self._extract_location_features(df)
        meth_feats = self._extract_method_and_activity(df)
        ppl_feats = self._extract_people_features(df)
        prop_feats = self._extract_property_features(df)
        ctx_feats = self._extract_context_features(df)
        
        # Combine all sub-profiles
        dna_df = pd.concat([
            time_feats,
            crime_feats,
            loc_feats,
            meth_feats,
            ppl_feats,
            prop_feats,
            ctx_feats
        ], axis=1)

        # Ensure exact match with declared feature list
        missing_expected = [c for c in self.all_feature_names if c not in dna_df.columns]
        if missing_expected:
            raise ValueError(f"Feature pipeline failed to generate expected features: {missing_expected}")

        # Reorder columns to match canonical order
        dna_df = pd.DataFrame(dna_df[self.all_feature_names])

        # Prepend incident_id
        if "incident_id" in df.columns:
            dna_df.insert(0, "incident_id", df["incident_id"].values)

        logger.info(f"Behavioral DNA vector construction complete. Shape: {dna_df.shape}")
        return dna_df


def build_behavioral_dna(
    input_csv_path: str = "data/processed/crime_dna_cleaned.csv",
    output_csv_path: str = "data/processed/crime_dna_behavioral_features.csv",
    feature_names_path: str = "data/processed/behavioral_dna_feature_names.json",
    metadata_path: str = "data/processed/behavioral_dna_metadata.json"
) -> pd.DataFrame:
    """
    End-to-end execution of Phase 3 feature engineering pipeline.
    """
    logger.info("=== Starting CRIME DNA Phase 3 Feature Pipeline ===")
    
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {input_csv_path}")

    logger.info(f"Loading cleaned dataset from {input_csv_path}...")
    df_clean = pd.read_csv(input_csv_path, low_memory=False)

    encoder = BehavioralDNAEncoder()
    dna_df = encoder.transform(df_clean)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    # Save features CSV
    logger.info(f"Saving Behavioral DNA feature dataset to {output_csv_path}...")
    dna_df.to_csv(output_csv_path, index=False)
    logger.info(f"Saved {output_csv_path} successfully. File size: {os.path.getsize(output_csv_path) / (1024*1024):.2f} MB")

    # Save feature names list
    feature_cols = [c for c in dna_df.columns if c != "incident_id"]
    with open(feature_names_path, "w") as f:
        json.dump(feature_cols, f, indent=2)
    logger.info(f"Saved {len(feature_cols)} feature names to {feature_names_path}")

    # Save rich metadata manifest
    metadata = {
        "dataset_name": "CRIME DNA Behavioral Feature Matrix",
        "version": "1.0",
        "source_data": input_csv_path,
        "features_path": output_csv_path,
        "feature_names_path": feature_names_path,
        "total_records": len(dna_df),
        "total_behavioral_features": len(feature_cols),
        "feature_groups_count": len(encoder.feature_groups),
        "feature_group_breakdown": {
            grp: {
                "count": len(cols),
                "features": cols
            }
            for grp, cols in encoder.feature_groups.items()
        },
        "feature_descriptions": {
            col: FEATURE_DESCRIPTIONS.get(col, "Behavioral feature dimension")
            for col in feature_cols
        },
        "value_bounds": {
            "min_observed": float(dna_df[feature_cols].min().min()),
            "max_observed": float(dna_df[feature_cols].max().max()),
            "null_count": int(dna_df[feature_cols].isna().sum().sum())
        }
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved Behavioral DNA metadata to {metadata_path}")

    logger.info("=== CRIME DNA Phase 3 Feature Pipeline Completed Successfully ===")
    return dna_df


def main():
    parser = argparse.ArgumentParser(description="CRIME DNA Phase 3: Behavioral DNA Feature Generation Pipeline")
    parser.add_argument("--input-path", type=str, default="data/processed/crime_dna_cleaned.csv", help="Input cleaned CSV path")
    parser.add_argument("--output-path", type=str, default="data/processed/crime_dna_behavioral_features.csv", help="Output feature CSV path")
    parser.add_argument("--feature-names-path", type=str, default="data/processed/behavioral_dna_feature_names.json", help="Path for feature names JSON")
    parser.add_argument("--metadata-path", type=str, default="data/processed/behavioral_dna_metadata.json", help="Path for metadata JSON")
    args = parser.parse_args()

    build_behavioral_dna(
        input_csv_path=args.input_path,
        output_csv_path=args.output_path,
        feature_names_path=args.feature_names_path,
        metadata_path=args.metadata_path
    )


if __name__ == "__main__":
    main()
