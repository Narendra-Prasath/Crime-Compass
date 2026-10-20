"""
CRIME DNA — Phase 2: Data Preprocessing & Sanitization Pipeline

This module loads the raw `crime_dna_ml.csv` dataset and performs justified,
rigorous data cleaning without altering the original raw data.

Key Operations:
1. Primary Key Generation:
   - Adds unique `incident_id` (INC_000001, INC_000002, ...) for incident-level
     retrieval and similarity search.
2. Removal of Zero-Variance Columns:
   - Eliminates 7 constant columns carrying zero variance across all records
     (incident_year, cargo_theft_flag_nan, county_name_nan, msa_name_nan,
      agency_type_name_nan, population_group_desc_nan, crime_against_nan).
3. Removal of Collinear Exact Duplicate Columns:
   - Drops 8 redundant duplicate count and indicator columns created during
     prior featurization.
4. Correction of Upstream Encoding Artifacts:
   - Corrects weapon_types_count: sets to 0 when has_weapon == 0 (was previously 1).
   - Corrects drug_types_count: sets to 0 when has_drug == 0 (was previously 1).
   - Corrects arrestee_avg_age: sets to NaN when has_arrest == 0 (was previously
     imputed to 35.0, distorting non-arrested incidents) or when arrestee_age_known == 0.
5. Separation & Explicit Missingness Handling for Demographics & Sentinels:
   - Sets victim ages (avg, min, max) to NaN when victim_age_known == 0 (preventing
     conflation of unknown victim ages with newborns/infants).
   - Sets offender ages (avg, min, max) to NaN when offender_age_known == 0.
   - Sets property_value to NaN for the NIBRS sentinel placeholder 999999999.0.
6. Architectural Metadata Tagging:
   - Classifies retained columns into Identifiers, Behavioral MO Features,
     Demographics, Context, and Post-Incident Outcomes (Data Leakage risks).
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, List, Tuple

# Ensure workspace root is in sys.path for direct script execution
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_CLEANER")

# Explicit list of constant / zero-variance columns discovered in Phase 1 audit
CONSTANT_COLUMNS: List[str] = [
    "incident_year",
    "cargo_theft_flag_nan",
    "county_name_nan",
    "msa_name_nan",
    "agency_type_name_nan",
    "population_group_desc_nan",
    "crime_against_nan"
]

# Exact collinear duplicate copies of other retained columns
REDUNDANT_COLUMNS: List[str] = [
    "offense_names_count",     # Identical to offense_count
    "location_type_count",     # Identical to location_count
    "location_types_count",    # Identical to location_count
    "bias_descriptions_count", # Identical to bias_count
    "has_injury_record",       # Identical to has_injury
    "has_arrest_record",       # Identical to has_arrest
    "has_property_record",     # Identical to has_property
    "has_suspected_drug"       # Identical to has_drug
]

# Columns representing post-incident police outcomes / potential leakage
POST_INCIDENT_OUTCOME_COLUMNS: List[str] = [
    "has_arrest",
    "arrest_count",
    "arrestee_avg_age",
    "arrestee_age_known",
    "arrestee_sexes_count",
    "recovered_count"
]

# Non-behavioral administrative identifiers
IDENTIFIER_COLUMNS: List[str] = [
    "incident_id",
    "agency_id"
]


def load_raw_dataset(csv_path: str) -> pd.DataFrame:
    """Loads the raw crime dataset without modifying it."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Raw dataset file not found at: {csv_path}")
    logger.info(f"Loading raw dataset from {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)
    logger.info(f"Raw dataset loaded successfully. Shape: {df.shape} ({len(df)} rows, {df.shape[1]} columns)")
    return df


def add_incident_identifier(df: pd.DataFrame, id_prefix: str = "INC_") -> pd.DataFrame:
    """
    Assigns an explicit, deterministic primary key 'incident_id' to each record.
    Avoids dataframe fragmentation by creating a copy.
    """
    df = df.copy()
    if "incident_id" not in df.columns:
        incident_ids = [f"{id_prefix}{i+1:06d}" for i in range(len(df))]
        df.insert(0, "incident_id", incident_ids)
        logger.info(f"Generated primary key 'incident_id' ({incident_ids[0]} to {incident_ids[-1]}).")
    return df


def drop_uninformative_columns(
    df: pd.DataFrame,
    constant_cols: List[str] = CONSTANT_COLUMNS,
    redundant_cols: List[str] = REDUNDANT_COLUMNS
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Drops zero-variance constant columns and exact collinear duplicate columns.
    """
    df = df.copy()
    cols_to_remove = [c for c in constant_cols + redundant_cols if c in df.columns]
    df = df.drop(columns=cols_to_remove)
    logger.info(f"Dropped {len(cols_to_remove)} uninformative/redundant columns: {cols_to_remove}")
    return df, cols_to_remove


def correct_encoding_artifacts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Corrects upstream synthetic encoding artifacts:
    1. weapon_types_count = 0 when has_weapon == 0 (was 1)
    2. drug_types_count = 0 when has_drug == 0 (was 1)
    3. arrestee_avg_age = NaN when has_arrest == 0 (was artificially 35.0)
    4. arrestee_avg_age = NaN when arrestee_age_known == 0
    """
    df = df.copy()
    
    # 1. Unarmed weapon types count fix
    if "has_weapon" in df.columns and "weapon_types_count" in df.columns:
        unarmed_mask = df["has_weapon"] == 0
        corrected_weapons = (unarmed_mask & (df["weapon_types_count"] != 0)).sum()
        df.loc[unarmed_mask, "weapon_types_count"] = 0
        logger.info(f"Corrected weapon_types_count to 0 for {corrected_weapons} unarmed incidents.")

    # 2. Drug-free drug types count fix
    if "has_drug" in df.columns and "drug_types_count" in df.columns:
        nodrug_mask = df["has_drug"] == 0
        corrected_drugs = (nodrug_mask & (df["drug_types_count"] != 0)).sum()
        df.loc[nodrug_mask, "drug_types_count"] = 0
        logger.info(f"Corrected drug_types_count to 0 for {corrected_drugs} drug-free incidents.")

    # 3. Non-arrest arrestee age artifact fix
    if "has_arrest" in df.columns and "arrestee_avg_age" in df.columns:
        no_arrest_mask = df["has_arrest"] == 0
        corrected_arrest_age = (no_arrest_mask & (df["arrestee_avg_age"] == 35.0)).sum()
        df.loc[no_arrest_mask, "arrestee_avg_age"] = np.nan
        logger.info(f"Replaced artificial 35.0 arrestee age with NaN for {corrected_arrest_age} non-arrest records.")

    # 4. Unknown arrestee age when arrestee_age_known == 0
    if "arrestee_age_known" in df.columns and "arrestee_avg_age" in df.columns:
        has_arrest_cond = (df["has_arrest"] == 1) if "has_arrest" in df.columns else pd.Series(True, index=df.index)
        unknown_arrestee_mask = has_arrest_cond & (df["arrestee_age_known"] == 0)
        corrected_unknown_arrestee = unknown_arrestee_mask.sum()
        df.loc[unknown_arrestee_mask, "arrestee_avg_age"] = np.nan
        logger.info(f"Set arrestee_avg_age to NaN for {corrected_unknown_arrestee} arrest records where age was unknown.")

    return df


def handle_missing_and_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appropriately represents true missingness and sentinel values as NaN,
    preventing ML algorithms from treating unknown ages as neonates/infants
    or sentinel codes as legitimate multi-million dollar values.
    """
    df = df.copy()

    # Victim ages when victim_age_known == 0
    if "victim_age_known" in df.columns:
        unknown_vic = df["victim_age_known"] == 0
        count_vic = unknown_vic.sum()
        for col in ["victim_avg_age", "victim_min_age", "victim_max_age"]:
            if col in df.columns:
                df.loc[unknown_vic, col] = np.nan
        logger.info(f"Converted victim ages (avg/min/max) to NaN for {count_vic} records where victim_age_known == 0.")

    # Offender ages when offender_age_known == 0
    if "offender_age_known" in df.columns:
        unknown_off = df["offender_age_known"] == 0
        count_off = unknown_off.sum()
        for col in ["offender_avg_age", "offender_min_age", "offender_max_age"]:
            if col in df.columns:
                df.loc[unknown_off, col] = np.nan
        logger.info(f"Converted offender ages (avg/min/max) to NaN for {count_off} records where offender_age_known == 0.")

    # Property value sentinel code 999999999.0
    if "property_value" in df.columns:
        sentinel_mask = df["property_value"] == 999999999.0
        count_sentinel = sentinel_mask.sum()
        df.loc[sentinel_mask, "property_value"] = np.nan
        logger.info(f"Replaced {count_sentinel} NIBRS sentinel property_value (999999999.0) with NaN.")

    return df


def categorize_columns(columns: List[str]) -> Dict[str, List[str]]:
    """
    Groups retained columns into semantic architectural roles for downstream
    Behavioral DNA vector construction and model training.
    """
    groups = {
        "identifiers": [],
        "temporal_features": [],
        "behavioral_offense_features": [],
        "victimology_demographics": [],
        "offender_demographics": [],
        "weapon_violence_features": [],
        "property_contraband_features": [],
        "environmental_geographic_features": [],
        "post_incident_outcomes": []
    }

    for col in columns:
        if col in IDENTIFIER_COLUMNS:
            groups["identifiers"].append(col)
        elif col in POST_INCIDENT_OUTCOME_COLUMNS:
            groups["post_incident_outcomes"].append(col)
        elif any(col.startswith(p) for p in ["county_name_", "msa_name_", "agency_type_name_", "population_group_desc_"]) or col == "population":
            groups["environmental_geographic_features"].append(col)
        elif col.startswith("incident_") or col in ["is_weekend", "is_night"]:
            groups["temporal_features"].append(col)
        elif col.startswith("victim_") or col in ["has_injury", "injury_record_count"]:
            groups["victimology_demographics"].append(col)
        elif col.startswith("offender_") or "relationship" in col:
            groups["offender_demographics"].append(col)
        elif "weapon" in col:
            groups["weapon_violence_features"].append(col)
        elif any(k in col for k in ["property", "drug", "stolen"]):
            groups["property_contraband_features"].append(col)
        else:
            groups["behavioral_offense_features"].append(col)

    return groups


def run_pipeline(
    raw_path: str = "crime_dna_ml.csv",
    output_path: str = "data/processed/crime_dna_cleaned.csv",
    metadata_path: str = "data/processed/cleaning_metadata.json"
) -> pd.DataFrame:
    """
    Executes the complete Phase 2 cleaning pipeline end-to-end and saves artifacts.
    """
    logger.info("=== Starting CRIME DNA Phase 2 Preprocessing Pipeline ===")
    
    # 1. Load raw dataset
    df_raw = load_raw_dataset(raw_path)
    initial_shape = df_raw.shape

    # 2. Add explicit incident identifier
    df_clean = add_incident_identifier(df_raw)

    # 3. Drop constant and redundant columns
    df_clean, dropped_cols = drop_uninformative_columns(df_clean)

    # 4. Correct encoding artifacts
    df_clean = correct_encoding_artifacts(df_clean)

    # 5. Handle missingness and sentinel codes
    df_clean = handle_missing_and_sentinels(df_clean)

    # 6. Ensure destination directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 7. Save cleaned dataset
    logger.info(f"Saving cleaned dataset to {output_path}...")
    df_clean.to_csv(output_path, index=False)
    logger.info(f"Saved cleaned dataset successfully. File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

    # 8. Compile and save metadata manifest
    feature_taxonomy = categorize_columns(df_clean.columns.tolist())
    metadata = {
        "source_dataset": raw_path,
        "cleaned_dataset": output_path,
        "initial_dimensions": {"rows": initial_shape[0], "columns": initial_shape[1]},
        "final_dimensions": {"rows": df_clean.shape[0], "columns": df_clean.shape[1]},
        "columns_dropped_count": len(dropped_cols),
        "columns_dropped": dropped_cols,
        "columns_retained_count": df_clean.shape[1],
        "feature_taxonomy_counts": {k: len(v) for k, v in feature_taxonomy.items()},
        "feature_taxonomy": feature_taxonomy
    }

    if metadata_path:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved cleaning metadata manifest to {metadata_path}")

    logger.info("=== CRIME DNA Phase 2 Preprocessing Pipeline Finished Successfully ===")
    return df_clean


def main():
    parser = argparse.ArgumentParser(description="CRIME DNA Phase 2 Preprocessing & Data Cleaning Pipeline")
    parser.add_argument("--input-path", type=str, default="crime_dna_ml.csv", help="Path to raw crime_dna_ml.csv")
    parser.add_argument("--output-path", type=str, default="data/processed/crime_dna_cleaned.csv", help="Path for cleaned CSV output")
    parser.add_argument("--metadata-path", type=str, default="data/processed/cleaning_metadata.json", help="Path for metadata JSON output")
    args = parser.parse_args()

    run_pipeline(
        raw_path=args.input_path,
        output_path=args.output_path,
        metadata_path=args.metadata_path
    )


if __name__ == "__main__":
    main()
