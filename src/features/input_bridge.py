"""
CRIME DNA — Input Ingestion Bridge & Feature Encoder
Reuses Phase 3 BehavioralDNAEncoder to transform validated user inputs into
both Human-Readable Behavioral DNA and Machine-Readable 70D Unit Vectors.
"""

import os
import sys
import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

# Ensure workspace root in path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from src.features.config import (
    SCALING_PARAMS,
    FEATURE_GROUPS,
    FEATURE_DESCRIPTIONS,
    FEATURE_FRIENDLY_NAMES,
    FEATURE_BEHAVIORAL_DOMAINS,
    DOMAIN_LABELS,
    FEATURE_SALIENCE_WEIGHTS
)
from src.features.dna_encoder import BehavioralDNAEncoder

logger = logging.getLogger("CRIME_DNA_INPUT_BRIDGE")

# Ordered list of all 70 features matching production matrix columns
ORDERED_FEATURE_NAMES: List[str] = [
    # 1. Temporal Dynamics (8)
    "time_hour_sin",
    "time_hour_cos",
    "time_month_sin",
    "time_month_cos",
    "time_weekday_sin",
    "time_weekday_cos",
    "time_is_weekend",
    "time_is_night",
    # 2. Crime Characteristics (10)
    "crime_against_person",
    "crime_against_property",
    "crime_against_society",
    "crime_against_person_property",
    "crime_against_person_society",
    "crime_against_property_society",
    "crime_against_person_property_society",
    "offense_count_scaled",
    "offense_categories_count_scaled",
    "is_attempted",
    # 3. Location & Environment (17)
    "location_count_scaled",
    "population_log_scaled",
    "population_group_desc_cities_from_10,000_thru_24,999",
    "population_group_desc_cities_from_100,000_thru_249,999",
    "population_group_desc_cities_from_2,500_thru_9,999",
    "population_group_desc_cities_from_25,000_thru_49,999",
    "population_group_desc_cities_from_50,000_thru_99,999",
    "population_group_desc_cities_under_2,500",
    "population_group_desc_msa_counties_100,000_or_over",
    "population_group_desc_msa_counties_from_10,000_thru_24,999",
    "population_group_desc_msa_counties_from_25,000_thru_99,999",
    "population_group_desc_msa_counties_under_10,000",
    "population_group_desc_non_msa_state_police",
    "population_group_desc_non_msa_counties_from_10,000_thru_24,999",
    "population_group_desc_non_msa_counties_from_25,000_thru_99,999",
    "population_group_desc_non_msa_counties_under_10,000",
    "agency_is_state_police",
    # 4. Method & Activity (8)
    "has_weapon",
    "weapon_count_scaled",
    "weapon_types_count_scaled",
    "is_multi_weapon",
    "has_criminal_activity",
    "criminal_activity_count_scaled",
    "has_relationship",
    "relationship_count_scaled",
    # 5. People & Demographics (13)
    "victim_count_scaled",
    "is_multi_victim",
    "victim_age_known",
    "victim_avg_age_scaled",
    "victim_age_spread_scaled",
    "victim_sexes_count_scaled",
    "victim_types_count_scaled",
    "offender_count_scaled",
    "is_co_offender",
    "offender_age_known",
    "offender_avg_age_scaled",
    "offender_age_spread_scaled",
    "offender_sexes_count_scaled",
    # 6. Property & Economics (6)
    "has_property",
    "property_record_count_scaled",
    "has_stolen_property",
    "stolen_count_scaled",
    "property_value_log_scaled",
    "is_cargo_theft",
    # 7. Context & Harm (8)
    "has_injury",
    "injury_record_count_scaled",
    "has_drug",
    "suspected_drug_count_scaled",
    "estimated_drug_quantity_log_scaled",
    "has_bias_motivation",
    "has_arrest_on_scene",
    "arrest_count_scaled"
]

ALL_POP_DESC_COLS: List[str] = [
    "population_group_desc_cities_from_10,000_thru_24,999",
    "population_group_desc_cities_from_100,000_thru_249,999",
    "population_group_desc_cities_from_2,500_thru_9,999",
    "population_group_desc_cities_from_25,000_thru_49,999",
    "population_group_desc_cities_from_50,000_thru_99,999",
    "population_group_desc_cities_under_2,500",
    "population_group_desc_msa_counties_100,000_or_over",
    "population_group_desc_msa_counties_from_10,000_thru_24,999",
    "population_group_desc_msa_counties_from_25,000_thru_99,999",
    "population_group_desc_msa_counties_under_10,000",
    "population_group_desc_non_msa_state_police",
    "population_group_desc_non_msa_counties_from_10,000_thru_24,999",
    "population_group_desc_non_msa_counties_from_25,000_thru_99,999",
    "population_group_desc_non_msa_counties_under_10,000"
]

POPULATION_SETTING_MAPPING: Dict[str, Dict[str, Any]] = {
    "small_city": {
        "col": "population_group_desc_cities_from_10,000_thru_24,999",
        "population": 16500.0,
        "is_state_police": False
    },
    "mid_sized_city": {
        "col": "population_group_desc_cities_from_25,000_thru_49,999",
        "population": 35000.0,
        "is_state_police": False
    },
    "large_city": {
        "col": "population_group_desc_cities_from_50,000_thru_99,999",
        "population": 72000.0,
        "is_state_police": False
    },
    "metropolitan_core": {
        "col": "population_group_desc_cities_from_100,000_thru_249,999",
        "population": 155000.0,
        "is_state_police": False
    },
    "small_town": {
        "col": "population_group_desc_cities_from_2,500_thru_9,999",
        "population": 5500.0,
        "is_state_police": False
    },
    "rural_community": {
        "col": "population_group_desc_cities_under_2,500",
        "population": 1800.0,
        "is_state_police": False
    },
    "state_police": {
        "col": "population_group_desc_non_msa_state_police",
        "population": 25000.0,
        "is_state_police": True
    }
}

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class InputFeatureBridge:
    """
    Transforms sanitized user incident dictionary inputs into calibrated 70D Behavioral DNA vectors
    by reusing the production BehavioralDNAEncoder.
    """

    def __init__(self, scaling_params: Optional[Dict[str, float]] = None):
        self.params = scaling_params or SCALING_PARAMS
        self.feature_names = ORDERED_FEATURE_NAMES
        self.feature_groups = FEATURE_GROUPS
        self.dna_encoder = BehavioralDNAEncoder(scaling_params=self.params)
        self.feature_name_to_idx = {name: i for i, name in enumerate(self.feature_names)}
        self.group_slices = {
            "temporal_dynamics": (0, 8),
            "crime_characteristics": (8, 18),
            "location_and_environment": (18, 35),
            "method_and_activity": (35, 43),
            "people_and_demographics": (43, 56),
            "property_and_economics": (56, 62),
            "context_and_harm": (62, 70),
        }

    def to_cleaned_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Constructs a 1-row DataFrame strictly adhering to the schema of crime_dna_cleaned.csv,
        ensuring 100% compatibility with the Phase 3 feature engineering pipeline.
        """
        # 1. Temporal parsing
        hour = 14
        if data.get("incident_time"):
            try:
                hour = int(str(data["incident_time"]).split(":")[0])
            except Exception:
                hour = 14
        elif data.get("incident_hour") is not None:
            hour = int(data["incident_hour"])
        hour = max(0, min(23, hour))

        month = 7
        weekday = 3
        if data.get("incident_date"):
            try:
                dt = datetime.fromisoformat(str(data["incident_date"]).split("T")[0])
                month = dt.month
                weekday = dt.weekday()
            except Exception:
                month = 7
                weekday = 3
        else:
            if data.get("incident_month") is not None:
                month = int(data["incident_month"])
            if data.get("incident_weekday") is not None:
                weekday = int(data["incident_weekday"])

        month = max(1, min(12, month))
        weekday = max(0, min(6, weekday))

        is_night = bool(data.get("is_night", (hour >= 20 or hour < 6)))
        is_weekend = bool(data.get("is_weekend", (weekday in (5, 6))))

        # 2. Crime category flags
        cat_str = str(data.get("crime_category", "property")).strip().lower()
        has_person = "person" in cat_str
        has_property = "property" in cat_str
        has_society = "society" in cat_str
        if not (has_person or has_property or has_society):
            has_property = True

        offense_count = max(1, int(data.get("offense_count") or 1))
        num_categories = sum([1 for flag in [has_person, has_property, has_society] if flag])
        is_attempted = bool(data.get("is_attempted", False))

        # 3. Environmental & Population
        location_count = max(1, int(data.get("location_count") or 1))
        setting_key = str(data.get("population_setting") or data.get("location_setting") or "small_city").strip().lower()
        setting_cfg = POPULATION_SETTING_MAPPING.get(setting_key, POPULATION_SETTING_MAPPING["small_city"])
        population = float(data.get("population") or setting_cfg["population"])
        is_sp = bool(data.get("is_state_police", setting_cfg["is_state_police"]))

        # 4. Modus Operandi & Weapons
        has_wep = bool(data.get("has_weapon", False))
        wep_count = int(data.get("weapon_count") or (1 if has_wep else 0))
        wep_types = int(data.get("weapon_types_count") or (1 if has_wep else 0))

        has_crim_act = bool(data.get("has_criminal_activity", False))
        crim_act_count = int(data.get("criminal_activity_count") or (1 if has_crim_act else 0))

        has_rel = bool(data.get("has_relationship", False))
        rel_count = int(data.get("relationship_count") or (1 if has_rel else 0))

        # 5. People & Demographics
        vic_count = max(0, int(data.get("victim_count") or 1))
        vic_avg_age = float(data["victim_avg_age"]) if data.get("victim_avg_age") is not None else None
        vic_spread = float(data.get("victim_age_spread") or 0.0)
        vic_sexes = max(1, int(data.get("victim_sexes_count") or 1))
        vic_types = max(1, int(data.get("victim_types_count") or 1))

        off_count = max(0, int(data.get("offender_count") or 1))
        off_avg_age = float(data["offender_avg_age"]) if data.get("offender_avg_age") is not None else None
        off_spread = float(data.get("offender_age_spread") or 0.0)
        off_sexes = max(1, int(data.get("offender_sexes_count") or 1))

        # 6. Property & Economics
        has_prop = bool(data.get("has_property", True if "property" in cat_str else False))
        prop_rec_count = int(data.get("property_record_count") or (1 if has_prop else 0))
        has_stolen = bool(data.get("has_stolen_property", has_prop))
        stolen_count = int(data.get("stolen_count") or (1 if has_stolen else 0))
        prop_val = max(0.0, float(data.get("property_value") or 0.0))
        is_cargo = bool(data.get("is_cargo_theft", False))

        # 7. Harm & Outcomes
        has_inj = bool(data.get("has_injury", False))
        inj_count = int(data.get("injury_record_count") or (1 if has_inj else 0))
        has_drg = bool(data.get("has_drug", False))
        drg_count = int(data.get("suspected_drug_count") or (1 if has_drg else 0))
        drg_qty = max(0.0, float(data.get("estimated_drug_quantity") or 0.0))
        has_bias = bool(data.get("has_bias_motivation", False))
        has_arr = bool(data.get("has_arrest", False))
        arr_count = int(data.get("arrest_count") or (1 if has_arr else 0))

        # Construct single-row dictionary adhering to crime_dna_cleaned.csv schema
        row: Dict[str, Any] = {
            "incident_id": "USER_INPUT_001",
            "incident_hour": hour,
            "incident_month": month,
            "incident_weekday": weekday,
            "is_weekend": 1.0 if is_weekend else 0.0,
            "is_night": 1.0 if is_night else 0.0,
            "crime_against_person": 1.0 if has_person else 0.0,
            "crime_against_property": 1.0 if has_property else 0.0,
            "crime_against_society": 1.0 if has_society else 0.0,
            "crime_against_person___property": 1.0 if (has_person and has_property and not has_society) else 0.0,
            "crime_against_person___society": 1.0 if (has_person and has_society and not has_property) else 0.0,
            "crime_against_property___society": 1.0 if (has_property and has_society and not has_person) else 0.0,
            "crime_against_person___property___society": 1.0 if (has_person and has_property and has_society) else 0.0,
            "offense_count": offense_count,
            "offense_categories_count": num_categories,
            "attempted_count": 1.0 if is_attempted else 0.0,
            "location_count": location_count,
            "population": population,
            "agency_type_name_state_police": 1.0 if is_sp else 0.0,
            "has_weapon": 1.0 if has_wep else 0.0,
            "weapon_count": wep_count,
            "weapon_types_count": wep_types,
            "has_criminal_activity": 1.0 if has_crim_act else 0.0,
            "criminal_activity_count": crim_act_count,
            "has_relationship": 1.0 if has_rel else 0.0,
            "relationship_count": rel_count,
            "victim_count": vic_count,
            "victim_age_known": 1.0 if vic_avg_age is not None else 0.0,
            "victim_avg_age": vic_avg_age if vic_avg_age is not None else np.nan,
            "victim_min_age": (vic_avg_age - vic_spread / 2.0) if vic_avg_age is not None else np.nan,
            "victim_max_age": (vic_avg_age + vic_spread / 2.0) if vic_avg_age is not None else np.nan,
            "victim_sexes_count": vic_sexes,
            "victim_types_count": vic_types,
            "offender_count": off_count,
            "offender_age_known": 1.0 if off_avg_age is not None else 0.0,
            "offender_avg_age": off_avg_age if off_avg_age is not None else np.nan,
            "offender_min_age": (off_avg_age - off_spread / 2.0) if off_avg_age is not None else np.nan,
            "offender_max_age": (off_avg_age + off_spread / 2.0) if off_avg_age is not None else np.nan,
            "offender_sexes_count": off_sexes,
            "has_property": 1.0 if has_prop else 0.0,
            "property_record_count": prop_rec_count,
            "stolen_count": stolen_count,
            "property_value_log": np.log1p(prop_val),
            "cargo_theft_flag_t": 1.0 if is_cargo else 0.0,
            "has_injury": 1.0 if has_inj else 0.0,
            "injury_record_count": inj_count,
            "has_drug": 1.0 if has_drg else 0.0,
            "suspected_drug_count": drg_count,
            "estimated_drug_quantity": drg_qty,
            "bias_count": 2.0 if has_bias else 0.0,
            "has_arrest": 1.0 if has_arr else 0.0,
            "arrest_count": arr_count
        }

        # 14 Population Group one-hot indicators
        target_col = setting_cfg["col"]
        for c in ALL_POP_DESC_COLS:
            row[c] = 1.0 if c == target_col else 0.0

        return pd.DataFrame([row])

    def encode(self, data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
        """
        Encodes user input dictionary into calibrated 70D Behavioral DNA vector
        and subprofile energies with microsecond latency using direct vector arithmetic.
        """
        vec = np.zeros(70, dtype=np.float32)

        # 1. Temporal parsing
        hour = 14
        if data.get("incident_time"):
            try:
                hour = int(str(data["incident_time"]).split(":")[0])
            except Exception:
                hour = 14
        elif data.get("incident_hour") is not None:
            hour = int(data["incident_hour"])
        hour = max(0, min(23, hour))

        month = 7
        weekday = 3
        if data.get("incident_date"):
            try:
                dt = datetime.fromisoformat(str(data["incident_date"]).split("T")[0])
                month = dt.month
                weekday = dt.weekday()
            except Exception:
                month = 7
                weekday = 3
        else:
            if data.get("incident_month") is not None:
                month = int(data["incident_month"])
            if data.get("incident_weekday") is not None:
                weekday = int(data["incident_weekday"])

        month = max(1, min(12, month))
        weekday = max(0, min(6, weekday))

        is_night = bool(data.get("is_night", (hour >= 20 or hour < 6)))
        is_weekend = bool(data.get("is_weekend", (weekday in (5, 6))))

        pi2 = 2.0 * math.pi
        vec[0] = (math.sin(pi2 * hour / 24.0) + 1.0) / 2.0
        vec[1] = (math.cos(pi2 * hour / 24.0) + 1.0) / 2.0
        vec[2] = (math.sin(pi2 * (month - 1.0) / 12.0) + 1.0) / 2.0
        vec[3] = (math.cos(pi2 * (month - 1.0) / 12.0) + 1.0) / 2.0
        vec[4] = (math.sin(pi2 * weekday / 7.0) + 1.0) / 2.0
        vec[5] = (math.cos(pi2 * weekday / 7.0) + 1.0) / 2.0
        vec[6] = 1.0 if is_weekend else 0.0
        vec[7] = 1.0 if is_night else 0.0

        # 2. Crime category flags
        cat_str = str(data.get("crime_category", "property")).strip().lower()
        has_person = "person" in cat_str
        has_property = "property" in cat_str
        has_society = "society" in cat_str
        if not (has_person or has_property or has_society):
            has_property = True

        vec[8] = 1.0 if has_person else 0.0
        vec[9] = 1.0 if has_property else 0.0
        vec[10] = 1.0 if has_society else 0.0
        vec[11] = 1.0 if (has_person and has_property and not has_society) else 0.0
        vec[12] = 1.0 if (has_person and has_society and not has_property) else 0.0
        vec[13] = 1.0 if (has_property and has_society and not has_person) else 0.0
        vec[14] = 1.0 if (has_person and has_property and has_society) else 0.0

        offense_count = max(1, int(data.get("offense_count") or 1))
        num_categories = (1 if has_person else 0) + (1 if has_property else 0) + (1 if has_society else 0)
        is_attempted = bool(data.get("is_attempted", False))

        cap_off = self.params["cap_offense_count"]
        cap_cat = self.params["cap_offense_categories"]
        vec[15] = min(max(offense_count - 1.0, 0.0), cap_off - 1.0) / (cap_off - 1.0)
        vec[16] = min(max(num_categories - 1.0, 0.0), cap_cat - 1.0) / (cap_cat - 1.0)
        vec[17] = 1.0 if is_attempted else 0.0

        # 3. Location & Environment
        location_count = max(1, int(data.get("location_count") or 1))
        setting_key = str(data.get("population_setting") or data.get("location_setting") or "small_city").strip().lower()
        setting_cfg = POPULATION_SETTING_MAPPING.get(setting_key, POPULATION_SETTING_MAPPING["small_city"])
        population = float(data.get("population") or setting_cfg["population"])
        is_sp = bool(data.get("is_state_police", data.get("agency_is_state_police", setting_cfg["is_state_police"])))

        cap_loc = self.params["cap_location_count"]
        max_pop = self.params["max_population"]
        vec[18] = min(max(location_count - 1.0, 0.0), cap_loc - 1.0) / (cap_loc - 1.0)
        vec[19] = math.log1p(population) / math.log1p(max_pop)

        target_pop_col = setting_cfg["col"]
        for col in ALL_POP_DESC_COLS:
            idx = self.feature_name_to_idx[col]
            vec[idx] = 1.0 if col == target_pop_col else 0.0

        vec[34] = 1.0 if is_sp else 0.0

        # 4. Method & Activity
        has_wep = bool(data.get("has_weapon", False))
        wep_count = int(data.get("weapon_count") or (1 if has_wep else 0))
        wep_types = int(data.get("weapon_types_count") or (1 if has_wep else 0))
        has_crim_act = bool(data.get("has_criminal_activity", False))
        crim_act_count = int(data.get("criminal_activity_count") or (1 if has_crim_act else 0))
        has_rel = bool(data.get("has_relationship", False))
        rel_count = int(data.get("relationship_count") or (1 if has_rel else 0))

        cap_wep = self.params["cap_weapon_count"]
        cap_wep_t = self.params["cap_weapon_types"]
        cap_act = self.params["cap_criminal_activities"]
        cap_rel = self.params["cap_relationships"]

        vec[35] = 1.0 if has_wep else 0.0
        vec[36] = min(max(wep_count, 0.0), cap_wep) / cap_wep
        vec[37] = min(max(wep_types, 0.0), cap_wep_t) / cap_wep_t
        vec[38] = 1.0 if wep_count > 1 else 0.0
        vec[39] = 1.0 if has_crim_act else 0.0
        vec[40] = min(max(crim_act_count, 0.0), cap_act) / cap_act
        vec[41] = 1.0 if has_rel else 0.0
        vec[42] = min(max(rel_count, 0.0), cap_rel) / cap_rel

        # 5. People & Demographics
        vic_count = max(0, int(data.get("victim_count") or 1))
        vic_avg_age = float(data["victim_avg_age"]) if data.get("victim_avg_age") is not None else None
        vic_spread = float(data.get("victim_age_spread") or 0.0)
        vic_sexes = max(1, int(data.get("victim_sexes_count") or 1))
        vic_types = max(1, int(data.get("victim_types_count") or 1))

        off_count = max(0, int(data.get("offender_count") or 1))
        off_avg_age = float(data["offender_avg_age"]) if data.get("offender_avg_age") is not None else None
        off_spread = float(data.get("offender_age_spread") or 0.0)
        off_sexes = max(1, int(data.get("offender_sexes_count") or 1))

        cap_vic = self.params["cap_victim_count"]
        med_vic_age = self.params["median_victim_age"]
        cap_vic_spread = self.params["cap_victim_age_spread"]
        cap_off_p = self.params["cap_offender_count"]
        med_off_age = self.params["median_offender_age"]
        cap_off_spread = self.params["cap_offender_age_spread"]

        vec[43] = min(max(vic_count - 1.0, 0.0), cap_vic - 1.0) / (cap_vic - 1.0)
        vec[44] = 1.0 if vic_count > 1 else 0.0
        vec[45] = 1.0 if vic_avg_age is not None else 0.0
        v_age = vic_avg_age if vic_avg_age is not None else med_vic_age
        vec[46] = min(max(v_age / 100.0, 0.0), 1.0)
        v_spr = vic_spread if vic_avg_age is not None else 0.0
        vec[47] = min(max(v_spr / cap_vic_spread, 0.0), 1.0)
        vec[48] = min(max(vic_sexes - 1.0, 0.0), 1.0)
        vec[49] = min(max(vic_types - 1.0, 0.0), 1.0)

        vec[50] = min(max(off_count - 1.0, 0.0), cap_off_p - 1.0) / (cap_off_p - 1.0)
        vec[51] = 1.0 if off_count > 1 else 0.0
        vec[52] = 1.0 if off_avg_age is not None else 0.0
        o_age = off_avg_age if off_avg_age is not None else med_off_age
        vec[53] = min(max(o_age / 100.0, 0.0), 1.0)
        o_spr = off_spread if off_avg_age is not None else 0.0
        vec[54] = min(max(o_spr / cap_off_spread, 0.0), 1.0)
        vec[55] = min(max(off_sexes - 1.0, 0.0), 1.0)

        # 6. Property & Economics
        has_prop = bool(data.get("has_property", True if "property" in cat_str else False))
        prop_rec_count = int(data.get("property_record_count") or (1 if has_prop else 0))
        has_stolen = bool(data.get("has_stolen_property", has_prop))
        stolen_count = int(data.get("stolen_count") or (1 if has_stolen else 0))
        prop_val = max(0.0, float(data.get("property_value") or 0.0))
        is_cargo = bool(data.get("is_cargo_theft", False))

        cap_prop_rec = self.params["cap_property_records"]
        cap_stolen = self.params["cap_stolen_count"]
        max_log_val = self.params["max_property_value_log"]

        vec[56] = 1.0 if has_prop else 0.0
        vec[57] = min(max(prop_rec_count, 0.0), cap_prop_rec) / cap_prop_rec
        vec[58] = 1.0 if stolen_count > 0 else 0.0
        vec[59] = min(max(stolen_count, 0.0), cap_stolen) / cap_stolen
        vec[60] = min(max(math.log1p(prop_val) / max_log_val, 0.0), 1.0)
        vec[61] = 1.0 if is_cargo else 0.0

        # 7. Harm & Outcomes
        has_inj = bool(data.get("has_injury", False))
        inj_count = int(data.get("injury_record_count") or (1 if has_inj else 0))
        has_drg = bool(data.get("has_drug", False))
        drg_count = int(data.get("suspected_drug_count") or (1 if has_drg else 0))
        drg_qty = max(0.0, float(data.get("estimated_drug_quantity") or 0.0))
        has_bias = bool(data.get("has_bias_motivation", False))
        has_arr = bool(data.get("has_arrest", False))
        arr_count = int(data.get("arrest_count") or (1 if has_arr else 0))

        cap_inj = self.params["cap_injury_records"]
        cap_drg = self.params["cap_drug_records"]
        max_drg_qty = self.params["max_drug_quantity"]
        cap_arr = self.params["cap_arrest_count"]

        vec[62] = 1.0 if has_inj else 0.0
        vec[63] = min(max(inj_count, 0.0), cap_inj) / cap_inj
        vec[64] = 1.0 if has_drg else 0.0
        vec[65] = min(max(drg_count, 0.0), cap_drg) / cap_drg
        vec[66] = min(max(math.log1p(drg_qty) / math.log1p(max_drg_qty), 0.0), 1.0)
        vec[67] = 1.0 if has_bias else 0.0
        vec[68] = 1.0 if has_arr else 0.0
        vec[69] = min(max(arr_count, 0.0), cap_arr) / cap_arr

        # Normalize to unit L2 norm
        norm = float(np.linalg.norm(vec))
        if norm > 0.0:
            norm_vec = vec / norm
        else:
            norm_vec = np.zeros_like(vec)

        # 7 Subprofile energy allocation
        # In unit L2 space (||norm_vec||_2 == 1.0), the Euclidean L2 norm of each sub-vector represents
        # its normalized geometric magnitude (energy) in [0.0, 1.0].
        # Its squared L2 norm represents its exact fraction of total vector energy (variance), summing to 1.0.
        subprofile_energies: Dict[str, float] = {}
        for grp_key, (st, en) in self.group_slices.items():
            sub_vec = norm_vec[st:en]
            sub_norm = float(np.linalg.norm(sub_vec))
            subprofile_energies[grp_key] = round(sub_norm, 4)

        return vec, norm_vec, subprofile_energies

    def compute_domain_data_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Behavioral Data Coverage across the 6 schema-supported domains:
        - Temporal Dynamics
        - Crime Characteristics
        - Location and Environment
        - Method and Activity
        - People and Incident Context
        - Property and Impact

        Formula: valid_applicable_fields / total_applicable_fields
        Missing or not-applicable values are not treated as negative evidence.
        Coverage measures data completeness, not crime risk, severity, or confidence.
        """
        domain_definitions = {
            "temporal_dynamics": {
                "label": "Temporal Dynamics",
                "description": "Incident timing, diurnal rhythms (day/night), seasonality, day of week, and weekend indicators.",
                "fields": ["incident_time", "incident_hour", "incident_date", "incident_month", "incident_weekday", "is_weekend"]
            },
            "crime_characteristics": {
                "label": "Crime Characteristics",
                "description": "Statutory offense category, incident offense counts, category breadth, and attempted vs. completed status.",
                "fields": ["crime_category", "offense_count", "offense_categories_count", "is_attempted"]
            },
            "location_and_environment": {
                "label": "Location and Environment",
                "description": "Population setting, premises density classification, and administrative geographic locality.",
                "fields": ["population_setting", "population", "location_count", "country", "state_ut", "district", "city_town", "locality", "pin_code"]
            },
            "method_and_activity": {
                "label": "Method and Activity",
                "description": "Modus operandi, weapon deployment and diversity, and secondary criminal activity indicators.",
                "fields": ["has_weapon", "weapon_count", "weapon_types_count", "has_criminal_activity", "criminal_activity_count"]
            },
            "people_and_context": {
                "label": "People and Incident Context",
                "description": "Victim and offender headcounts, demographic spread, interpersonal relationship, injury, and on-scene arrest.",
                "fields": [
                    "victim_count", "victim_avg_age", "victim_sexes_count", "victim_types_count",
                    "offender_count", "offender_avg_age", "offender_sexes_count",
                    "has_relationship", "has_injury", "injury_record_count", "has_arrest", "arrest_count", "has_bias_motivation"
                ]
            },
            "property_and_impact": {
                "label": "Property and Impact",
                "description": "Physical property targeting, damage/loss documentation, valuation, stolen item counts, and cargo freight indicators.",
                "fields": ["has_property", "property_record_count", "has_stolen_property", "stolen_count", "property_value", "is_cargo_theft", "currency"]
            }
        }

        domains_result: Dict[str, Any] = {}
        total_valid = 0
        total_applicable = 0

        for dom_key, dom_info in domain_definitions.items():
            valid_fields = []
            unspecified_fields = []
            not_applicable_fields = []

            for field in dom_info["fields"]:
                val = data.get(field)

                # Check not-applicable conditions based on prerequisite flags
                if field in ("weapon_count", "weapon_types_count") and not data.get("has_weapon", False):
                    not_applicable_fields.append(field)
                    continue
                if field in ("injury_record_count",) and not data.get("has_injury", False):
                    not_applicable_fields.append(field)
                    continue
                if field in ("arrest_count",) and not data.get("has_arrest", False):
                    not_applicable_fields.append(field)
                    continue
                if field in ("property_record_count", "has_stolen_property", "stolen_count", "is_cargo_theft") and not data.get("has_property", False):
                    not_applicable_fields.append(field)
                    continue
                if field in ("criminal_activity_count",) and not data.get("has_criminal_activity", False):
                    not_applicable_fields.append(field)
                    continue

                # Determine if value is validly specified
                if val is not None and val != "" and str(val).strip().lower() not in ("unknown", "null", "none"):
                    valid_fields.append(field)
                else:
                    unspecified_fields.append(field)

            applicable_count = len(valid_fields) + len(unspecified_fields)
            coverage_pct = round((len(valid_fields) / applicable_count * 100.0), 1) if applicable_count > 0 else 0.0

            total_valid += len(valid_fields)
            total_applicable += applicable_count

            domains_result[dom_key] = {
                "domain_key": dom_key,
                "domain_id": dom_key,
                "label": dom_info["label"],
                "name": dom_info["label"],
                "description": dom_info["description"],
                "coverage_pct": coverage_pct,
                "available_fields_count": len(valid_fields),
                "valid_fields_count": len(valid_fields),
                "total_applicable_fields": applicable_count,
                "unspecified_fields_count": len(unspecified_fields),
                "not_applicable_fields_count": len(not_applicable_fields),
                "total_supported_fields": len(dom_info["fields"]),
                "available_fields": valid_fields,
                "unspecified_fields": unspecified_fields
            }

        overall_coverage_pct = round((total_valid / total_applicable * 100.0), 1) if total_applicable > 0 else 0.0

        return {
            "overall_coverage_pct": overall_coverage_pct,
            "total_available_fields": total_valid,
            "total_applicable_fields": total_applicable,
            "domains": domains_result,
            "advisory": (
                "Behavioral Data Coverage measures the availability of usable incident information in each domain. "
                "Missing or unspecified fields are not treated as negative evidence. "
                "Coverage does not indicate crime risk, behavioral severity, model confidence, or probability."
            )
        }

    def generate_human_readable_fingerprint(
        self,
        data: Dict[str, Any],
        raw_vec: np.ndarray
    ) -> Dict[str, Any]:
        """
        Generates dynamic, human-interpretable Behavioral DNA labels and emoji chips
        derived directly from the submitted values. No hardcoding.
        """
        chips: List[str] = []
        traits: List[Dict[str, Any]] = []

        # 1. Temporal Dynamics
        hour = 14
        if data.get("incident_time"):
            try:
                hour = int(str(data["incident_time"]).split(":")[0])
            except Exception:
                hour = 14
        elif data.get("incident_hour") is not None:
            hour = int(data["incident_hour"])
        time_str = str(data.get("incident_time") or f"{hour:02d}:00")

        if hour >= 20 or hour < 6:
            chips.append(f"🌙 Night ({time_str})")
            traits.append({
                "id": "diurnal_execution",
                "icon": "🌙",
                "label": f"Nocturnal Execution ({time_str})",
                "category": "Temporal Dynamics",
                "description": "Executed under cover of darkness during night/early-morning window (20:00-05:59).",
                "is_elevated": True
            })
        else:
            time_phase = "Morning" if hour < 12 else ("Afternoon" if hour < 17 else "Evening")
            chips.append(f"☀️ Daytime ({time_str})")
            traits.append({
                "id": "diurnal_execution",
                "icon": "☀️",
                "label": f"Daytime Execution ({time_phase}, {time_str})",
                "category": "Temporal Dynamics",
                "description": f"Executed during daylight {time_phase.lower()} business/routine hours.",
                "is_elevated": False
            })

        weekday = 3
        if data.get("incident_date"):
            try:
                weekday = datetime.fromisoformat(str(data["incident_date"]).split("T")[0]).weekday()
            except Exception:
                weekday = 3
        elif data.get("incident_weekday") is not None:
            weekday = int(data["incident_weekday"])
        w_name = WEEKDAY_NAMES[weekday]
        is_weekend = bool(data.get("is_weekend", weekday in (5, 6)))

        if is_weekend:
            chips.append(f"📅 Weekend ({w_name})")
            traits.append({
                "id": "weekend_execution",
                "icon": "📅",
                "label": f"Weekend Cycle ({w_name})",
                "category": "Temporal Dynamics",
                "description": "Occurred during weekend recreational cycle with distinct leisure mobility.",
                "is_elevated": True
            })
        else:
            chips.append(f"💼 Weekday ({w_name})")
            traits.append({
                "id": "weekend_execution",
                "icon": "💼",
                "label": f"Weekday Baseline ({w_name})",
                "category": "Temporal Dynamics",
                "description": "Occurred during structured weekday operational rhythm.",
                "is_elevated": False
            })

        # 2. Jurisdiction & Setting
        setting_key = str(data.get("population_setting") or data.get("location_setting") or "mid_sized_city").lower()
        setting_labels = {
            "metropolitan_core": ("🌆", "Metropolitan Core (100k+ pop)", "Dense metropolitan center."),
            "large_city": ("🏙️", "Large City (50k-100k pop)", "Regional urban city center."),
            "mid_sized_city": ("🏙️", "Mid-Sized City (25k-50k pop)", "Mid-sized municipality."),
            "small_city": ("🏘️", "Small City (10k-25k pop)", "Small city / suburban jurisdiction."),
            "small_town": ("🏡", "Small Town (2.5k-10k pop)", "Low-density township setting."),
            "rural_community": ("🌲", "Rural Community (<2.5k pop)", "Rural / low-density county setting."),
            "state_police": ("🚔", "State Highway Jurisdiction", "Highway patrol or regional transit jurisdiction.")
        }
        loc_icon, loc_label, loc_desc = setting_labels.get(setting_key, ("🏙️", "Municipal Setting", "Standard municipal jurisdiction."))
        chips.append(f"{loc_icon} {loc_label.split('(')[0].strip()}")
        traits.append({
            "id": "setting_profile",
            "icon": loc_icon,
            "label": loc_label,
            "category": "Location & Environment",
            "description": loc_desc,
            "is_elevated": "metro" in setting_key or "large" in setting_key
        })

        # 3. Target Category & Crime Characteristics
        cat_str = str(data.get("crime_category", "property")).lower()
        if "person_property" in cat_str:
            chips.append("💥📦 Violent Property Compound")
            traits.append({
                "id": "crime_domain",
                "icon": "💥📦",
                "label": "Compound Violent Property Offense",
                "category": "Crime Characteristics",
                "description": "High-severity encounter combining property targeting with direct interpersonal coercion.",
                "is_elevated": True
            })
        elif "person" in cat_str:
            chips.append("💥 Violent / Interpersonal")
            traits.append({
                "id": "crime_domain",
                "icon": "💥",
                "label": "Interpersonal / Violent Crime",
                "category": "Crime Characteristics",
                "description": "Direct offense against person with physical, psychological, or bodily threat.",
                "is_elevated": True
            })
        elif "society" in cat_str:
            chips.append("⚖️ Crime Against Society")
            traits.append({
                "id": "crime_domain",
                "icon": "⚖️",
                "label": "Public Order / Societal Offense",
                "category": "Crime Characteristics",
                "description": "Violation of public welfare, narcotics restrictions, or regulatory codes.",
                "is_elevated": False
            })
        else:
            chips.append("📦 Property Offense")
            traits.append({
                "id": "crime_domain",
                "icon": "📦",
                "label": "Property & Structure Offense",
                "category": "Crime Characteristics",
                "description": "Deprivation, entry, theft, or damage directed toward material goods or premises.",
                "is_elevated": False
            })

        # 4. Weapons & Force
        has_wep = bool(data.get("has_weapon", False))
        wep_cnt = int(data.get("weapon_count") or 0)
        if has_wep:
            w_text = f"Armed Encounter ({wep_cnt} weapons)" if wep_cnt > 1 else "Armed Encounter"
            chips.append(f"🔫 {w_text}")
            traits.append({
                "id": "weapon_deployment",
                "icon": "🔫",
                "label": w_text,
                "category": "Method & Weapon",
                "description": "Weapon displayed, threatened, or discharged during execution.",
                "is_elevated": True
            })
        else:
            chips.append("🚫 No Weapon (Unarmed)")
            traits.append({
                "id": "weapon_deployment",
                "icon": "🚫",
                "label": "Unarmed Execution",
                "category": "Method & Weapon",
                "description": "No weapon deployed, displayed, or recovered on scene.",
                "is_elevated": False
            })

        # 5. People & Demographics
        vic_cnt = int(data.get("victim_count") or 1)
        vic_age = data.get("victim_avg_age")
        if vic_cnt > 1:
            age_suffix = f" (avg age {float(vic_age):.0f})" if vic_age is not None else ""
            chips.append(f"👥 {vic_cnt} Victims{age_suffix}")
            traits.append({
                "id": "victimology",
                "icon": "👥",
                "label": f"Multiple Victims ({vic_cnt} persons){age_suffix}",
                "category": "People & Demographics",
                "description": "Multi-victim incident presenting compounded interpersonal harm.",
                "is_elevated": True
            })
        elif vic_cnt == 1:
            age_suffix = f" (age {float(vic_age):.0f})" if vic_age is not None else ""
            chips.append(f"👤 1 Victim{age_suffix}")
            traits.append({
                "id": "victimology",
                "icon": "👤",
                "label": f"Single Victim{age_suffix}",
                "category": "People & Demographics",
                "description": "Single individual targeted during execution.",
                "is_elevated": False
            })
        else:
            chips.append("🏢 Institutional Victim")
            traits.append({
                "id": "victimology",
                "icon": "🏢",
                "label": "Commercial / Institutional Target",
                "category": "People & Demographics",
                "description": "Victim entity is a commercial, public, or corporate establishment.",
                "is_elevated": False
            })

        off_cnt = int(data.get("offender_count") or 1)
        off_age = data.get("offender_avg_age")
        if off_cnt > 1:
            age_suffix = f" (avg age {float(off_age):.0f})" if off_age is not None else ""
            chips.append(f"👥 {off_cnt} Co-Offenders{age_suffix}")
            traits.append({
                "id": "offender_structure",
                "icon": "👥",
                "label": f"Co-Offender Syndicate ({off_cnt} suspects){age_suffix}",
                "category": "People & Demographics",
                "description": "Collaborative group operational execution.",
                "is_elevated": True
            })
        elif off_cnt == 1:
            age_suffix = f" (age {float(off_age):.0f})" if off_age is not None else ""
            chips.append(f"👤 Lone Offender{age_suffix}")
            traits.append({
                "id": "offender_structure",
                "icon": "👤",
                "label": f"Lone Offender{age_suffix}",
                "category": "People & Demographics",
                "description": "Single actor executing offense independently.",
                "is_elevated": False
            })

        # 6. Property & Economics
        has_prop = bool(data.get("has_property", True if "property" in cat_str else False))
        prop_val = float(data.get("property_value") or 0.0)
        if has_prop:
            val_text = f" (${prop_val:,.0f} value)" if prop_val > 0 else ""
            chips.append(f"📦 Property Involved{val_text}")
            traits.append({
                "id": "property_impact",
                "icon": "📦",
                "label": f"Property Targeted{val_text}",
                "category": "Property & Economics",
                "description": "Material goods, currency, or structures targeted.",
                "is_elevated": prop_val > 5000.0
            })

        # 7. Physical Injury & Harm
        if bool(data.get("has_injury", False)):
            chips.append("🩹 Physical Injury Sustained")
            traits.append({
                "id": "harm_outcome",
                "icon": "🩹",
                "label": "Bodily Injury Documented",
                "category": "Context & Harm",
                "description": "Physical bodily trauma documented on scene.",
                "is_elevated": True
            })
        else:
            traits.append({
                "id": "harm_outcome",
                "icon": "🛡️",
                "label": "No Bodily Injury",
                "category": "Context & Harm",
                "description": "No bodily injury sustained by victim.",
                "is_elevated": False
            })

        # 8. Contraband / Drugs
        if bool(data.get("has_drug", False)):
            chips.append("💊 Narcotics Involved")
            traits.append({
                "id": "narcotics_presence",
                "icon": "💊",
                "label": "Controlled Substances Present",
                "category": "Context & Harm",
                "description": "Illicit drugs or controlled contraband identified or seized.",
                "is_elevated": True
            })

        # 9. Resolution / Arrest
        if bool(data.get("has_arrest", False)):
            chips.append("⚖️ Immediate On-Scene Arrest")
            traits.append({
                "id": "resolution_state",
                "icon": "⚖️",
                "label": "Apprehended On Scene",
                "category": "Context & Harm",
                "description": "Immediate apprehension executed by responding units.",
                "is_elevated": False
            })
        else:
            chips.append("🏃 Fled Scene (Unarrested)")
            traits.append({
                "id": "resolution_state",
                "icon": "🏃",
                "label": "At Large Upon Departure",
                "category": "Context & Harm",
                "description": "Offender evaded immediate apprehension at time of report.",
                "is_elevated": True
            })

        # 8. Compact Behavioral Fingerprint with explicit Yes / No / Unknown / Not applicable statuses
        compact_traits = [
            {
                "id": "diurnal_execution",
                "trait_name": "Time / Diurnal Timing",
                "value": "Nighttime Occurrence" if (hour >= 20 or hour < 6) else "Daytime Occurrence",
                "status": "Yes" if (hour >= 20 or hour < 6) else "No",
                "status_label": "Nighttime" if (hour >= 20 or hour < 6) else "Daytime",
                "detail": f"{time_str} ({'Nocturnal' if (hour >= 20 or hour < 6) else 'Daylight'} hours)"
            },
            {
                "id": "weekly_cycle",
                "trait_name": "Weekly Cycle",
                "value": "Weekend Incident" if is_weekend else "Weekday Incident",
                "status": "Yes" if is_weekend else "No",
                "status_label": "Weekend" if is_weekend else "Weekday",
                "detail": f"{w_name} ({'Weekend cycle' if is_weekend else 'Weekday cycle'})"
            },
            {
                "id": "setting_type",
                "trait_name": "Location Setting",
                "value": loc_label.split('(')[0].strip(),
                "status": "Applicable",
                "status_label": loc_label.split('(')[0].strip(),
                "detail": loc_desc
            },
            {
                "id": "crime_target",
                "trait_name": "Incident Target",
                "value": "Property-Related" if has_prop else ("Person-Related" if "person" in cat_str else "Public Order / Society"),
                "status": "Applicable",
                "status_label": "Property Target" if has_prop else ("Person Target" if "person" in cat_str else "Public Order"),
                "detail": f"Target domain classified under {cat_str.replace('_', ' ').title()}"
            },
            {
                "id": "weapon_reported",
                "trait_name": "Weapon Reported",
                "value": "Weapon Reported" if data.get("has_weapon") else ("No Weapon Reported" if data.get("has_weapon") is not None else "Unknown"),
                "status": "Yes" if data.get("has_weapon") else ("No" if data.get("has_weapon") is not None else "Unknown"),
                "status_label": "Weapon Present" if data.get("has_weapon") else ("Unarmed" if data.get("has_weapon") is not None else "Unknown"),
                "detail": f"{data.get('weapon_count', 1)} weapon(s) identified" if data.get("has_weapon") else "No weapon threatened or deployed"
            },
            {
                "id": "injury_reported",
                "trait_name": "Physical Injury Inflicted",
                "value": "Injury Inflicted" if data.get("has_injury") else ("No Injury Documented" if data.get("has_injury") is not None else "Unknown"),
                "status": "Yes" if data.get("has_injury") else ("No" if data.get("has_injury") is not None else "Unknown"),
                "status_label": "Injury Inflicted" if data.get("has_injury") else ("No Physical Harm" if data.get("has_injury") is not None else "Unknown"),
                "detail": "Victim sustained physical trauma" if data.get("has_injury") else "No physical injuries recorded"
            },
            {
                "id": "relationship_reported",
                "trait_name": "Prior Interpersonal Link",
                "value": "Known Prior Link" if data.get("has_relationship") else ("Stranger / No Prior Link" if data.get("has_relationship") is not None else "Unknown"),
                "status": "Yes" if data.get("has_relationship") else ("No" if data.get("has_relationship") is not None else "Unknown"),
                "status_label": "Known Link" if data.get("has_relationship") else ("Stranger" if data.get("has_relationship") is not None else "Unknown"),
                "detail": "Known associate or domestic link" if data.get("has_relationship") else "No prior relationship established"
            },
            {
                "id": "arrest_reported",
                "trait_name": "On-Scene Enforcement Clearance",
                "value": "On-Scene Arrest Effected" if data.get("has_arrest") else ("Perpetrator Fled Scene" if data.get("has_arrest") is not None else "Unknown"),
                "status": "Yes" if data.get("has_arrest") else ("No" if data.get("has_arrest") is not None else "Unknown"),
                "status_label": "Arrest Effected" if data.get("has_arrest") else ("Perpetrator Fled" if data.get("has_arrest") is not None else "Unknown"),
                "detail": "Subject apprehended on scene" if data.get("has_arrest") else "Subject departed prior to apprehension"
            }
        ]

        # Assemble clean plain-text presentation matching requested format
        plain_text_lines = ["BEHAVIORAL DNA"]
        for c in chips:
            plain_text_lines.append(c)
        plain_text = "\n".join(plain_text_lines)

        return {
            "title": "BEHAVIORAL DNA",
            "summary_chips": chips,
            "traits": traits,
            "compact_traits": compact_traits,
            "plain_text": plain_text
        }

    def generate_machine_readable_fingerprint(
        self,
        data: Dict[str, Any],
        raw_vec: np.ndarray,
        norm_vec: np.ndarray,
        subprofile_energies: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Returns the machine-readable 70D representation consumed by ML models.
        """
        feature_dict = {
            self.feature_names[i]: round(float(norm_vec[i]), 5)
            for i in range(len(self.feature_names))
        }

        active_traits = self.get_active_traits(raw_vec, top_n=8)

        return {
            "vector_dimension": 70,
            "l2_norm": round(float(np.linalg.norm(norm_vec)), 5),
            "feature_names": self.feature_names,
            "raw_vector": [round(float(v), 5) for v in raw_vec],
            "normalized_vector": [round(float(v), 5) for v in norm_vec],
            "feature_vector_dict": feature_dict,
            "subprofile_energies": subprofile_energies,
            "top_active_traits": active_traits
        }

    def get_active_traits(
        self,
        raw_vec: np.ndarray,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Extracts top non-zero behavioral features sorted by magnitude and salience."""
        traits = []
        for i, val in enumerate(raw_vec):
            if val > 0.05:
                feat_name = self.feature_names[i]
                dom_key = FEATURE_BEHAVIORAL_DOMAINS.get(feat_name, "other")
                dom_label = DOMAIN_LABELS.get(dom_key, dom_key.replace("_", " ").title())
                salience = FEATURE_SALIENCE_WEIGHTS.get(feat_name, 1.0)
                traits.append({
                    "feature": feat_name,
                    "label": FEATURE_FRIENDLY_NAMES.get(feat_name, feat_name.replace("_", " ").title()),
                    "domain": dom_key,
                    "domain_label": dom_label,
                    "value": round(float(val), 4),
                    "energy_share_pct": round(float((val ** 2) * 100.0), 2),
                    "salience": salience,
                    "description": FEATURE_DESCRIPTIONS.get(feat_name, feat_name)
                })
        # Sort by magnitude first, then salience tie-breaker
        traits.sort(key=lambda x: (round(x["value"], 4), x["salience"]), reverse=True)
        for t in traits:
            t.pop("salience", None)
        return traits[:top_n]


# Global bridge singleton
bridge = InputFeatureBridge()
