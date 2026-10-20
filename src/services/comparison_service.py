"""
CRIME DNA — Behavioral DNA Comparison Service

Compares two incidents (Incident A vs Incident B) using the unified
70-dimensional Behavioral DNA representation.

Both incidents can be:
- Newly entered incidents (custom user input payload)
- Selected historical incidents (retrieved via incident_id)
- A combination of both (custom input vs historical incident)

Produces:
1. Side-by-side feature comparison table (Time, Location, Property, Weapon, Injury, Crime, etc.)
   with exact match indicators (✓ for match, △ for differ, ~ for partial)
2. Scientifically valid DNA similarity score based on unit L2 cosine similarity
3. Matching Characteristics breakdown
4. Differing Characteristics breakdown
5. "What Changed?" prominent analytical section capturing behavioral transitions and escalations
6. Subprofile radar energy comparison across all 7 behavioral domains
7. Strict non-offender attribution ethical boundary
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from src.features.input_bridge import bridge
from src.features.config import FEATURE_GROUPS

logger = logging.getLogger("CRIME_DNA_COMPARISON_SERVICE")


SEVEN_DOMAINS_METADATA = [
    {
        "domain_id": "temporal_dynamics",
        "domain_name": "Temporal Dynamics",
        "description": "What time-related information is recorded, including incident time, day of week, month, and day/night classification.",
        "start_idx": 0,
        "end_idx": 8,
        "expected_fields": ["incident_time", "incident_hour", "incident_date", "incident_month", "incident_weekday", "is_weekend", "is_night"],
        "formula": "E_temp = ||v_temp||_2 = sqrt(sum_{i in temporal} v_i^2) over unit hypersphere S^69"
    },
    {
        "domain_id": "crime_characteristics",
        "domain_name": "Crime Characteristics",
        "description": "What statutory crime category, attempt status, and offense counts are recorded.",
        "start_idx": 8,
        "end_idx": 18,
        "expected_fields": ["crime_category", "primary_crime_category", "is_attempted", "offense_count"],
        "formula": "E_crime = ||v_crime||_2 = sqrt(sum_{i in crime} v_i^2) over unit hypersphere S^69"
    },
    {
        "domain_id": "location_and_environment",
        "domain_name": "Location and Environment",
        "description": "What location type, premises setting, and geographic environmental context are recorded.",
        "start_idx": 18,
        "end_idx": 35,
        "expected_fields": ["location_type", "location", "population_setting", "location_count", "population"],
        "formula": "E_loc = ||v_loc||_2 = sqrt(sum_{i in location} v_i^2) over unit hypersphere S^69"
    },
    {
        "domain_id": "method_and_activity",
        "domain_name": "Method and Activity",
        "description": "What method, weapon context, or secondary criminal activity is recorded.",
        "start_idx": 35,
        "end_idx": 43,
        "expected_fields": ["has_weapon", "weapon_count", "weapon_types", "has_criminal_activity"],
        "formula": "E_method = ||v_method||_2 = sqrt(sum_{i in method} v_i^2) over unit hypersphere S^69"
    },
    {
        "domain_id": "people_and_demographics",
        "domain_name": "People and Demographics",
        "description": "What people-related counts and aggregate demographics are recorded (never used for personal identity matching).",
        "start_idx": 43,
        "end_idx": 56,
        "expected_fields": ["victim_count", "victim_avg_age", "victim_sexes_count", "offender_count", "offender_avg_age", "offender_sexes_count"],
        "formula": "E_people = ||v_people||_2 = sqrt(sum_{i in people} v_i^2) over unit hypersphere S^69"
    },
    {
        "domain_id": "property_and_economics",
        "domain_name": "Property and Economics",
        "description": "What property involvement, loss type, stolen items, or monetary valuations are recorded.",
        "start_idx": 56,
        "end_idx": 62,
        "expected_fields": ["has_property", "property_value", "property_record_count", "has_stolen_property", "stolen_count", "is_cargo_theft"],
        "formula": "E_prop = ||v_prop||_2 = sqrt(sum_{i in property} v_i^2) over unit hypersphere S^69"
    },
    {
        "domain_id": "context_and_harm",
        "domain_name": "Context and Harm",
        "description": "What physical victim injury, substance presence, bias motivation, or on-scene arrest is recorded.",
        "start_idx": 62,
        "end_idx": 70,
        "expected_fields": ["has_injury", "injury_record_count", "has_drug", "suspected_drug_count", "has_bias_motivation", "has_arrest", "arrest_count"],
        "formula": "E_harm = ||v_harm||_2 = sqrt(sum_{i in harm} v_i^2) over unit hypersphere S^69"
    }
]


def calculate_incident_coverage(raw_data: Dict[str, Any], attributes: Dict[str, Any], domain_meta: Dict[str, Any]) -> Dict[str, Any]:
    dom_id = domain_meta["domain_id"]
    valid_fields = []
    missing_fields = []
    not_applicable = []
    data = {**raw_data, **attributes}

    if dom_id == "method_and_activity":
        has_wep = data.get("has_weapon")
        if has_wep is False:
            not_applicable.extend(["weapon_count", "weapon_types"])
    elif dom_id == "property_and_economics":
        has_prop = data.get("has_property")
        if has_prop is False:
            not_applicable.extend(["property_value", "property_record_count", "has_stolen_property", "stolen_count", "is_cargo_theft"])
    elif dom_id == "context_and_harm":
        has_inj = data.get("has_injury")
        if has_inj is False:
            not_applicable.append("injury_record_count")
        has_drg = data.get("has_drug")
        if has_drg is False:
            not_applicable.append("suspected_drug_count")
        has_arr = data.get("has_arrest")
        if has_arr is False:
            not_applicable.append("arrest_count")

    for f in domain_meta["expected_fields"]:
        if f in not_applicable:
            continue
        v = data.get(f)
        if v is not None and v != "" and str(v).lower() not in ("unknown", "unspecified", "null", "?", "none"):
            valid_fields.append(f)
        else:
            missing_fields.append(f)

    total_applicable = len(valid_fields) + len(missing_fields)
    pct = round((len(valid_fields) / max(1, total_applicable)) * 100, 1)
    status = "Sufficient data" if pct >= 60.0 else ("Partial data" if pct > 0 else "Insufficient data")
    return {
        "valid_count": len(valid_fields),
        "total_applicable": total_applicable,
        "valid_fields": valid_fields,
        "missing_fields": missing_fields,
        "not_applicable": not_applicable,
        "coverage_pct": pct,
        "status": status,
        "display": f"{len(valid_fields)} of {total_applicable} expected fields ({pct}%)"
    }


def extract_domain_contributing_features(data: Dict[str, Any], attributes: Dict[str, Any], dom_id: str) -> List[str]:
    merged = {**data, **attributes}
    traits = []
    if dom_id == "temporal_dynamics":
        if "time" in attributes and "unknown" not in str(attributes["time"]).lower():
            traits.append(f"Recorded timing: {attributes['time']}")
        if merged.get("is_weekend") is not None:
            traits.append("Weekend occurrence" if merged["is_weekend"] else "Weekday occurrence")
        if merged.get("incident_month") is not None:
            traits.append(f"Month: {merged['incident_month']}")
    elif dom_id == "crime_characteristics":
        if "crime" in attributes and "unknown" not in str(attributes["crime"]).lower():
            traits.append(f"Category: {attributes['crime']}")
        if merged.get("is_attempted") is not None:
            traits.append("Attempted crime" if merged["is_attempted"] else "Completed crime")
        if merged.get("offense_count") is not None:
            traits.append(f"Offense count: {merged['offense_count']}")
    elif dom_id == "location_and_environment":
        if "location" in attributes and "unknown" not in str(attributes["location"]).lower():
            traits.append(f"Setting: {attributes['location']}")
        if merged.get("population_setting") is not None:
            traits.append(f"Population setting: {str(merged['population_setting']).replace('_', ' ').title()}")
    elif dom_id == "method_and_activity":
        if merged.get("has_weapon") is not None:
            traits.append("Armed encounter" if merged["has_weapon"] else "Unarmed execution")
        if merged.get("has_criminal_activity") is not None:
            traits.append("Associated criminal activity" if merged["has_criminal_activity"] else "No secondary criminal activity")
    elif dom_id == "people_and_demographics":
        if merged.get("victim_count") is not None:
            traits.append(f"Victim count: {merged['victim_count']}")
        if merged.get("offender_count") is not None:
            traits.append(f"Offender count: {merged['offender_count']}")
    elif dom_id == "property_and_economics":
        if merged.get("has_property") is not None:
            if merged["has_property"]:
                val = merged.get("property_value", 0.0)
                traits.append(f"Property targeted (${val:,.0f})" if val > 0 else "Property targeted")
            else:
                traits.append("Non-property motive")
    elif dom_id == "context_and_harm":
        if merged.get("has_injury") is not None:
            traits.append("Physical harm inflicted" if merged["has_injury"] else "No physical injury reported")
        if merged.get("has_drug") is not None:
            traits.append("Substance involvement" if merged["has_drug"] else "No substance involvement")
        if merged.get("has_arrest") is not None:
            traits.append("Scene arrest effectuated" if merged["has_arrest"] else "No scene arrest")
    return traits


def extract_domain_missing_features(cov: Dict[str, Any]) -> List[str]:
    friendly_names = {
        "incident_time": "Incident time",
        "incident_hour": "Incident hour",
        "incident_date": "Incident date",
        "incident_month": "Calendar month",
        "incident_weekday": "Day of week",
        "is_weekend": "Weekend status",
        "is_night": "Diurnal classification",
        "crime_category": "Crime category",
        "primary_crime_category": "Statutory category",
        "is_attempted": "Attempted flag",
        "offense_count": "Offense count",
        "location_type": "Location type",
        "location": "Setting context",
        "population_setting": "Population setting",
        "location_count": "Location count",
        "population": "Population size",
        "has_weapon": "Weapon presence",
        "weapon_count": "Weapon count",
        "weapon_types": "Weapon types",
        "has_criminal_activity": "Criminal activity flag",
        "victim_count": "Victim count",
        "victim_avg_age": "Victim age",
        "victim_sexes_count": "Victim demographics",
        "offender_count": "Offender count",
        "offender_avg_age": "Offender age",
        "offender_sexes_count": "Offender demographics",
        "has_property": "Property flag",
        "property_value": "Property value",
        "property_record_count": "Property record count",
        "has_stolen_property": "Stolen property status",
        "stolen_count": "Stolen items count",
        "is_cargo_theft": "Cargo theft flag",
        "has_injury": "Injury flag",
        "injury_record_count": "Injury records count",
        "has_drug": "Drug flag",
        "suspected_drug_count": "Suspected drug count",
        "has_bias_motivation": "Bias motivation flag",
        "has_arrest": "Arrest flag",
        "arrest_count": "Arrest count"
    }
    return [friendly_names.get(f, f.replace("_", " ").title()) for f in cov.get("missing_fields", [])]


class BehavioralComparisonService:
    """
    Core service for comparative behavioral analysis between two incidents.
    """

    def __init__(self):
        pass

    def resolve_incident(
        self,
        spec: Dict[str, Any],
        state: Any = None,
        default_label: str = "Incident"
    ) -> Dict[str, Any]:
        """
        Resolves an incident specification into a standardized profile and 70D unit DNA vector.

        Spec can be:
        1. {"incident_id": "INC_000001"} -> Historical incident
        2. {"input_data": {...}} or directly {...} -> Custom user input
        """
        label = spec.get("label") or default_label

        if state is None:
            from src.api.state import state as global_state
            state = global_state

        # Case 1: Historical incident requested via incident_id
        inc_id = spec.get("incident_id")
        if inc_id and getattr(state, "is_ready", False):
            idx = state.get_incident_index(inc_id)
            if idx is not None:
                vec = state.get_incident_dna_vector(inc_id)
                profile = state.get_incident_profile(inc_id)
                context = profile.get("context", {})
                cluster_info = profile.get("cluster", {})

                # Standardize display attributes
                hour = context.get("incident_hour", 12)
                is_night = context.get("is_night", False)
                time_str = f"{'Night' if is_night else 'Daytime'} ({hour:02d}:00)"

                has_wep = bool(context.get("has_weapon", False))
                wep_str = "Armed Encounter" if has_wep else "None"

                has_prop = bool(context.get("has_property", False))
                prop_val = float(context.get("property_value", 0.0))
                prop_str = f"Yes (${prop_val:,.0f})" if (has_prop and prop_val > 0) else ("Yes" if has_prop else "No")

                has_inj = bool(context.get("has_injury", False))
                inj_str = "Yes" if has_inj else "No"

                # Crime category
                crime_cat = context.get("primary_crime_category", "Unknown")
                if "Property Crime" in crime_cat:
                    crime_simple = "Property / Theft"
                elif "Person & Property" in crime_cat:
                    crime_simple = "Robbery / Extortion"
                elif "Person" in crime_cat:
                    crime_simple = "Assault / Violent Crime"
                elif "Society" in crime_cat:
                    crime_simple = "Narcotics / Society Offense"
                else:
                    crime_simple = crime_cat

                # Subprofile energies
                subprofile_energies = {}
                if vec is not None:
                    grp_map = getattr(state, "feature_group_indices", None) or {
                        k: [state.feature_names.index(c) for c in cols if c in state.feature_names]
                        for k, cols in getattr(state, "feature_groups", {}).items()
                    }
                    for grp_name, indices in grp_map.items():
                        if indices:
                            sub_v = vec[indices]
                            subprofile_energies[grp_name] = round(float(np.linalg.norm(sub_v)), 4)

                return {
                    "source_type": "historical",
                    "incident_id": inc_id,
                    "label": spec.get("label") or f"Historical Incident {inc_id}",
                    "norm_vector": vec,
                    "subprofile_energies": subprofile_energies,
                    "raw_data": context,
                    "attributes": {
                        "time": time_str,
                        "is_night": is_night,
                        "is_weekend": bool(context.get("is_weekend", False)),
                        "location": "Urban / County Area",  # Contextual baseline
                        "property": prop_str,
                        "has_property": has_prop,
                        "property_value": prop_val,
                        "weapon": wep_str,
                        "has_weapon": has_wep,
                        "injury": inj_str,
                        "has_injury": has_inj,
                        "crime": crime_simple,
                        "raw_crime_category": crime_cat,
                        "victim_count": int(context.get("victim_count", 1)),
                        "offender_count": int(context.get("offender_count", 1)),
                        "has_drug": bool(context.get("has_drug", False)),
                        "has_arrest": bool(context.get("has_arrest", False)),
                        "cluster_name": cluster_info.get("cluster_name", "")
                    }
                }

        # Case 2: Custom user-submitted incident payload
        input_data = spec.get("payload") or spec.get("input_data")
        if input_data is None:
            # Check if spec itself contains incident attributes
            if any(k in spec for k in ("crime_category", "scenario_title", "incident_time", "incident_date")):
                input_data = spec
            else:
                raise ValueError(
                    f"Incident specification for '{label}' must provide either a valid 'incident_id' or incident payload data ('payload' or 'input_data')."
                )

        if isinstance(input_data, dict):
            if "payload" in input_data and isinstance(input_data["payload"], dict):
                input_data = input_data["payload"]
            elif "input_data" in input_data and isinstance(input_data["input_data"], dict):
                input_data = input_data["input_data"]

        raw_vec, norm_vec, subprofile_energies = bridge.encode(input_data)
        human_dna = bridge.generate_human_readable_fingerprint(input_data, raw_vec)

        # Standardize display attributes
        hour = 14
        if input_data.get("incident_time"):
            try:
                hour = int(str(input_data["incident_time"]).split(":")[0])
            except Exception:
                hour = 14
        elif input_data.get("incident_hour") is not None:
            hour = int(input_data["incident_hour"])
        is_night = bool(input_data.get("is_night") or (hour >= 20 or hour < 6))
        time_str = f"{'Night' if is_night else 'Daytime'} ({input_data.get('incident_time') or f'{hour:02d}:00'})"

        loc_type = "Residential"
        if "location_type" in input_data and input_data["location_type"] is not None:
            loc_raw = str(input_data["location_type"]).lower()
            if "residen" in loc_raw or "home" in loc_raw or "apart" in loc_raw or "house" in loc_raw:
                loc_type = "Residential"
            elif "commercial" in loc_raw or "store" in loc_raw or "retail" in loc_raw or "business" in loc_raw:
                loc_type = "Commercial"
            elif "transit" in loc_raw or "subway" in loc_raw or "bus" in loc_raw:
                loc_type = "Transit"
            elif "street" in loc_raw or "park" in loc_raw or "open" in loc_raw or "outdoor" in loc_raw or "highway" in loc_raw:
                loc_type = "Public Space"
            else:
                loc_type = loc_raw.replace("_", " ").title()
        elif "population_setting" in input_data and input_data["population_setting"] is not None:
            loc_type = str(input_data["population_setting"]).replace("_", " ").title()

        # Property
        if "has_property" in input_data and input_data["has_property"] is not None:
            has_prop = bool(input_data["has_property"])
            prop_val = float(input_data.get("property_value", 0.0))
            prop_str = f"Yes (${prop_val:,.0f})" if (has_prop and prop_val > 0) else ("Yes" if has_prop else "No")
        else:
            has_prop = None
            prop_val = 0.0
            prop_str = "Unknown"

        # Weapon
        if "has_weapon" in input_data and input_data["has_weapon"] is not None:
            has_wep = bool(input_data["has_weapon"])
            wep_cnt = int(input_data.get("weapon_count", 0))
            wep_types = input_data.get("weapon_types", [])
            if has_wep:
                if wep_types and isinstance(wep_types, list) and len(wep_types) > 0:
                    wep_str = str(wep_types[0]).replace("_", " ").title()
                elif wep_cnt > 1:
                    wep_str = f"Armed Encounter ({wep_cnt} weapons)"
                else:
                    wep_str = "Armed Encounter"
            else:
                wep_str = "None"
        else:
            has_wep = None
            wep_str = "Unknown"

        # Injury
        if "has_injury" in input_data and input_data["has_injury"] is not None:
            has_inj = bool(input_data["has_injury"])
            inj_str = "Yes" if has_inj else "No"
        else:
            has_inj = None
            inj_str = "Unknown"

        crime_cat = str(input_data.get("crime_category", "property")).replace("_", " ").title()

        return {
            "source_type": "new_input",
            "incident_id": spec.get("incident_id"),
            "label": spec.get("label") or input_data.get("scenario_title") or default_label,
            "norm_vector": norm_vec,
            "subprofile_energies": subprofile_energies,
            "raw_data": input_data,
            "human_dna_chips": human_dna.get("summary_chips", []),
            "attributes": {
                "time": time_str,
                "is_night": is_night,
                "is_weekend": bool(input_data.get("is_weekend", False)),
                "location": loc_type,
                "property": prop_str,
                "has_property": has_prop,
                "property_value": prop_val,
                "weapon": wep_str,
                "has_weapon": has_wep,
                "injury": inj_str,
                "has_injury": has_inj,
                "crime": crime_cat,
                "raw_crime_category": input_data.get("crime_category", "property"),
                "victim_count": int(input_data.get("victim_count", 1)),
                "offender_count": int(input_data.get("offender_count", 1)),
                "has_drug": bool(input_data.get("has_drug", False)),
                "has_arrest": bool(input_data.get("has_arrest", False)),
                "cluster_name": ""
            }
        }

    def compare(
        self,
        incident_a: Dict[str, Any],
        incident_b: Dict[str, Any],
        state: Any = None
    ) -> Dict[str, Any]:
        """
        Performs comprehensive comparative Behavioral DNA analysis between two incidents.

        Args:
            incident_a: Spec for Incident A (historical ID or input payload).
            incident_b: Spec for Incident B (historical ID or input payload).
            state: ApplicationState instance (optional, defaults to global state).

        Returns:
            Structured comparison result with similarity, DNA table, matching/differing
            characteristics, neutral explanations, 7 audited domain energies, and technical details.
        """
        if state is None:
            from src.api.state import state as global_state
            state = global_state

        # 1. Resolve both incidents to standardized representations
        res_a = self.resolve_incident(incident_a, state, default_label="Incident A")
        res_b = self.resolve_incident(incident_b, state, default_label="Incident B")

        vec_a = res_a["norm_vector"]
        vec_b = res_b["norm_vector"]

        # Ensure unit L2 normalization on S^69
        if vec_a is not None:
            norm_a = float(np.linalg.norm(vec_a))
            vec_a = vec_a / (norm_a if norm_a > 0 else 1.0)
        if vec_b is not None:
            norm_b = float(np.linalg.norm(vec_b))
            vec_b = vec_b / (norm_b if norm_b > 0 else 1.0)

        # 2. Scientifically valid DNA similarity score using cosine dot product
        if vec_a is not None and vec_b is not None:
            raw_cosine = float(np.dot(vec_a, vec_b))
            similarity_score_pct = round(max(0.0, min(100.0, raw_cosine * 100.0)), 2)
            cosine_distance = round(max(0.0, min(2.0, 1.0 - raw_cosine)), 4)
        else:
            raw_cosine = 0.0
            similarity_score_pct = 0.0
            cosine_distance = 1.0

        # Documented threshold tiers (product-defined interpretation)
        if similarity_score_pct >= 90.0:
            match_tier = "High Behavioral Affinity"
            affinity_summary = "Very high alignment across modus operandi dimensions (threshold: ≥90.0%)."
        elif similarity_score_pct >= 75.0:
            match_tier = "Moderate Behavioral Affinity"
            affinity_summary = "Noticeable behavioral alignment with identifiable divergences (threshold: 75.0%–89.9%)."
        elif similarity_score_pct >= 50.0:
            match_tier = "Partial Behavioral Overlap"
            affinity_summary = "Shared characteristics in select operational domains (threshold: 50.0%–74.9%)."
        else:
            match_tier = "Divergent Behavioral Profiles"
            affinity_summary = "Substantially distinct modus operandi profiles (threshold: <50.0%)."

        # 3. Construct Feature-by-Feature DNA Comparison across 7 Observable Dimensions
        attr_a = res_a["attributes"]
        attr_b = res_b["attributes"]
        raw_a = res_a.get("raw_data", {})
        raw_b = res_b.get("raw_data", {})

        table_rows = []
        matching_chars = []
        differing_chars = []
        unknown_chars = []
        transitions = []
        escalations = []
        match_items = []
        differ_items = []
        unknown_items = []
        matched_statements = []
        differing_statements = []
        unknown_statements = []
        strongest_similarities = []
        most_meaningful_differences = []

        def is_val_unknown(val: Any) -> bool:
            if val is None:
                return True
            if isinstance(val, bool):
                return False
            if isinstance(val, (int, float)):
                return False
            s = str(val).strip().lower()
            return s in ("unknown", "unspecified", "not recorded", "null", "?", "none_recorded")

        # --- Dimension 1: Time ---
        time_a_unk = is_val_unknown(attr_a.get("time")) or attr_a.get("is_night") is None
        time_b_unk = is_val_unknown(attr_b.get("time")) or attr_b.get("is_night") is None
        time_val_a = "Unknown" if time_a_unk else ("Night" if attr_a["is_night"] else "Daytime")
        time_val_b = "Unknown" if time_b_unk else ("Night" if attr_b["is_night"] else "Daytime")

        if time_a_unk or time_b_unk:
            table_rows.append({
                "feature": "Time",
                "incident_a": time_val_a,
                "incident_b": time_val_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Timing unobserved in one or both records ({time_val_a} vs {time_val_b})"
            })
            unknown_items.append("Time / diurnal cycle")
            unknown_chars.append("Diurnal timing unrecorded or unspecified in one or both records")
            unknown_statements.append("Diurnal timing (day/night) was unobserved in one or both records.")
        else:
            time_match = (attr_a["is_night"] == attr_b["is_night"])
            time_status = "MATCH" if time_match else "DIFFER"
            time_sym = "✓" if time_match else "△"
            table_rows.append({
                "feature": "Time",
                "incident_a": time_val_a,
                "incident_b": time_val_b,
                "result": time_sym,
                "match_status": time_status,
                "details": f"Incident A: {attr_a['time']} vs Incident B: {attr_b['time']}"
            })
            if time_match:
                match_items.append(time_val_a)
                stmt = f"Both incidents occurred during {time_val_a.lower()} hours."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
                strongest_similarities.append(f"Consistent timing: both offenses occurred during {time_val_a.lower()} hours.")
            else:
                differ_items.append("Timing / diurnal pattern")
                stmt = f"Incident A occurred during the {'night' if attr_a['is_night'] else 'day'}; Incident B occurred {'at night' if attr_b['is_night'] else 'during the day'}."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                transitions.append(f"Timing shifted: Incident A was {time_val_a} while Incident B was {time_val_b}.")
                most_meaningful_differences.append(f"Diurnal shift: Incident A occurred during {time_val_a.lower()} hours while Incident B occurred during {time_val_b.lower()} hours.")

        # --- Dimension 2: Location ---
        loc_a = attr_a.get("location", "Unknown")
        loc_b = attr_b.get("location", "Unknown")
        loc_a_unk = is_val_unknown(loc_a)
        loc_b_unk = is_val_unknown(loc_b)

        if loc_a_unk or loc_b_unk:
            table_rows.append({
                "feature": "Location",
                "incident_a": loc_a,
                "incident_b": loc_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Location setting unspecified in one or both records ({loc_a} vs {loc_b})"
            })
            unknown_items.append("Location context")
            unknown_chars.append("Location environment unspecified or unobserved")
            unknown_statements.append("Location setting was unobserved or unspecified in one or both records.")
        else:
            loc_match = (loc_a.lower() == loc_b.lower())
            loc_status = "MATCH" if loc_match else "DIFFER"
            loc_sym = "✓" if loc_match else "△"
            table_rows.append({
                "feature": "Location",
                "incident_a": loc_a,
                "incident_b": loc_b,
                "result": loc_sym,
                "match_status": loc_status,
                "details": f"Setting comparison: {loc_a} vs {loc_b}"
            })
            if loc_match:
                match_items.append(loc_a)
                stmt = f"Both incidents occurred in {loc_a.lower()} settings."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
                strongest_similarities.append(f"Identical location setting: both incidents targeted {loc_a.lower()} environments.")
            else:
                differ_items.append("Location context")
                stmt = f"Location environment differs (Incident A: {loc_a} vs Incident B: {loc_b})."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                transitions.append(f"Location setting differs: {loc_a} in Incident A vs {loc_b} in Incident B.")
                most_meaningful_differences.append(f"Location setting differed: Incident A targeted {loc_a} whereas Incident B targeted {loc_b}.")

        # --- Dimension 3: Property ---
        prop_a_unk = attr_a.get("has_property") is None
        prop_b_unk = attr_b.get("has_property") is None
        prop_a = "Unknown" if prop_a_unk else ("Yes" if attr_a["has_property"] else "No")
        prop_b = "Unknown" if prop_b_unk else ("Yes" if attr_b["has_property"] else "No")

        if prop_a_unk or prop_b_unk:
            table_rows.append({
                "feature": "Property",
                "incident_a": prop_a,
                "incident_b": prop_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Property targeting unobserved in one or both records ({prop_a} vs {prop_b})"
            })
            unknown_items.append("Property involvement")
            unknown_chars.append("Property involvement data unrecorded in one or both incidents")
            unknown_statements.append("Property involvement status was unrecorded in one or both records.")
        else:
            prop_match = (attr_a["has_property"] == attr_b["has_property"])
            prop_status = "MATCH" if prop_match else "DIFFER"
            prop_sym = "✓" if prop_match else "△"
            table_rows.append({
                "feature": "Property",
                "incident_a": prop_a,
                "incident_b": prop_b,
                "result": prop_sym,
                "match_status": prop_status,
                "details": f"Incident A: {attr_a.get('property', prop_a)} vs Incident B: {attr_b.get('property', prop_b)}"
            })
            if prop_match:
                match_items.append("Property" if attr_a["has_property"] else "No property")
                stmt = "Both involved property." if attr_a["has_property"] else "Neither involved property."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
                if attr_a["has_property"]:
                    strongest_similarities.append("Target property motive: both incidents involved property acquisition.")
                else:
                    strongest_similarities.append("Non-property motive: neither incident targeted property theft.")
            else:
                differ_items.append("Property involvement")
                stmt = f"Property involvement differs (Incident A: {prop_a} vs Incident B: {prop_b})."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                transitions.append(f"Property involvement differs: {prop_a} in Incident A vs {prop_b} in Incident B.")
                most_meaningful_differences.append(f"Property involvement differed: Incident A was {prop_a.lower()} whereas Incident B was {prop_b.lower()}.")

        # --- Dimension 4: Weapon ---
        wep_a_unk = attr_a.get("has_weapon") is None or is_val_unknown(attr_a.get("weapon"))
        wep_b_unk = attr_b.get("has_weapon") is None or is_val_unknown(attr_b.get("weapon"))
        wep_a = "Unknown" if wep_a_unk else ("None" if not attr_a["has_weapon"] else attr_a["weapon"])
        wep_b = "Unknown" if wep_b_unk else ("None" if not attr_b["has_weapon"] else attr_b["weapon"])

        if wep_a_unk or wep_b_unk:
            table_rows.append({
                "feature": "Weapon",
                "incident_a": wep_a,
                "incident_b": wep_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Weapon information unknown in one or both records ({wep_a} vs {wep_b})"
            })
            unknown_items.append("Weapon presence")
            unknown_chars.append("Weapon deployment unobserved or unspecified in one or both incidents")
            unknown_statements.append("Weapon deployment context was unobserved or unspecified in one or both records.")
        else:
            wep_match = (attr_a["has_weapon"] == attr_b["has_weapon"])
            wep_status = "MATCH" if wep_match else "DIFFER"
            wep_sym = "✓" if wep_match else "△"
            table_rows.append({
                "feature": "Weapon",
                "incident_a": wep_a,
                "incident_b": wep_b,
                "result": wep_sym,
                "match_status": wep_status,
                "details": f"Weapon presence: {wep_a} vs {wep_b}"
            })
            if wep_match:
                match_items.append("No weapon" if not attr_a["has_weapon"] else "Weapon present")
                stmt = "Both incidents were unarmed encounters." if not attr_a["has_weapon"] else "Both incidents involved weapons."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
                if not attr_a["has_weapon"]:
                    strongest_similarities.append("Unarmed execution: neither incident deployed weapons or lethal force.")
                else:
                    strongest_similarities.append("Armed encounter: both incidents involved weapons.")
            else:
                differ_items.append("Weapon context")
                stmt = f"Weapon context differs (Incident A: {wep_a} vs Incident B: {wep_b})."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                transitions.append(f"Weapon deployment differed: {wep_a} in Incident A vs {wep_b} in Incident B.")
                if not attr_a["has_weapon"] and attr_b["has_weapon"]:
                    escalations.append(f"Weapon Context: Transitioned from unarmed to armed encounter ({wep_b}).")
                elif attr_a["has_weapon"] and not attr_b["has_weapon"]:
                    escalations.append(f"Weapon Context: Armed encounter in Incident A reduced to unarmed in Incident B.")
                most_meaningful_differences.append(f"Weapon context differs: Incident A was {wep_a} whereas Incident B was {wep_b}.")

        # --- Dimension 5: Injury ---
        inj_a_unk = attr_a.get("has_injury") is None or is_val_unknown(attr_a.get("injury"))
        inj_b_unk = attr_b.get("has_injury") is None or is_val_unknown(attr_b.get("injury"))
        inj_a = "Unknown" if inj_a_unk else attr_a.get("injury", "No")
        inj_b = "Unknown" if inj_b_unk else attr_b.get("injury", "No")

        if inj_a_unk or inj_b_unk:
            table_rows.append({
                "feature": "Injury",
                "incident_a": inj_a,
                "incident_b": inj_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Physical trauma outcome unrecorded in one or both incidents ({inj_a} vs {inj_b})"
            })
            unknown_items.append("Physical injury")
            unknown_chars.append("Injury outcome unspecified or unrecorded in one or both records")
            unknown_statements.append("Physical trauma outcome was unrecorded in one or both records.")
        else:
            inj_match = (attr_a["has_injury"] == attr_b["has_injury"])
            inj_status = "MATCH" if inj_match else "DIFFER"
            inj_sym = "✓" if inj_match else "△"
            table_rows.append({
                "feature": "Injury",
                "incident_a": inj_a,
                "incident_b": inj_b,
                "result": inj_sym,
                "match_status": inj_status,
                "details": f"Physical harm inflicted: {inj_a} vs {inj_b}"
            })
            if inj_match:
                match_items.append("No injury" if not attr_a["has_injury"] else "Physical injury")
                stmt = "Both reported no physical injury." if not attr_a["has_injury"] else "Both reported physical victim injury."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
                if not attr_a["has_injury"]:
                    strongest_similarities.append("Zero physical harm: no victim injuries occurred in either offense.")
                else:
                    strongest_similarities.append("Harm outcome: physical injuries were sustained in both offenses.")
            else:
                differ_items.append("Injury / physical harm")
                stmt = f"Physical injury context differs (Incident A: {inj_a} vs Incident B: {inj_b})."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                transitions.append(f"Harm outcome differed: {inj_a} in Incident A vs {inj_b} in Incident B.")
                if not attr_a["has_injury"] and attr_b["has_injury"]:
                    escalations.append("Harm / Injury Context: Physical victim injury reported in Incident B.")
                most_meaningful_differences.append(f"Physical injury context differs: Incident A was {inj_a.lower()} whereas Incident B was {inj_b.lower()}.")

        # --- Dimension 6: Crime Category ---
        crime_a = attr_a.get("crime", "Unknown")
        crime_b = attr_b.get("crime", "Unknown")
        crime_a_unk = is_val_unknown(crime_a)
        crime_b_unk = is_val_unknown(crime_b)

        if crime_a_unk or crime_b_unk:
            same_crime_category = False
            crime_category_status = "Unknown Offense Category"
            crime_category_detail = "Offense classification was not completely specified in one or both incidents."
            table_rows.append({
                "feature": "Crime",
                "incident_a": crime_a,
                "incident_b": crime_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Offense classification unknown ({crime_a} vs {crime_b})"
            })
            unknown_items.append("Crime category")
            unknown_chars.append("Offense category classification unobserved")
            unknown_statements.append("Statutory offense category was unspecified in one or both records.")
        else:
            crime_match = (crime_a.lower() == crime_b.lower())
            crime_status = "MATCH" if crime_match else "DIFFER"
            crime_sym = "✓" if crime_match else "△"
            table_rows.append({
                "feature": "Crime",
                "incident_a": crime_a,
                "incident_b": crime_b,
                "result": crime_sym,
                "match_status": crime_status,
                "details": f"Statutory classification: {crime_a} vs {crime_b}"
            })
            same_crime_category = crime_match
            if crime_match:
                match_items.append(f"Crime category ({crime_a})")
                stmt = f"Both incidents fall under the {crime_a} category."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
                crime_category_status = "Same Crime Category"
                crime_category_detail = f"Both incidents belong to the same statutory category: {crime_a}."
                strongest_similarities.append(f"Statutory crime category aligned: {crime_a}.")
            else:
                differ_items.append("Crime category")
                stmt = f"The recorded crime categories differ (Incident A: {crime_a} vs Incident B: {crime_b})."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                transitions.append(f"Offense category differed: {crime_a} in Incident A vs {crime_b} in Incident B.")
                crime_category_status = "Different Crime Category"
                crime_category_detail = f"Different crime categories: Incident A is {crime_a} while Incident B is {crime_b}. The DNA engine evaluates behavioral MO alignment despite different legal labels."
                most_meaningful_differences.append(f"Statutory crime categories differ: Incident A is {crime_a} whereas Incident B is {crime_b}.")

        # --- Dimension 7: Victim Count ---
        vic_a = str(attr_a.get("victim_count", "1"))
        vic_b = str(attr_b.get("victim_count", "1"))
        vic_a_unk = is_val_unknown(vic_a)
        vic_b_unk = is_val_unknown(vic_b)

        if vic_a_unk or vic_b_unk:
            table_rows.append({
                "feature": "Victim Count",
                "incident_a": "Unknown" if vic_a_unk else vic_a,
                "incident_b": "Unknown" if vic_b_unk else vic_b,
                "result": "?",
                "match_status": "UNKNOWN",
                "details": f"Victim headcount unspecified in one or both records"
            })
            unknown_items.append("Victim headcount")
            unknown_chars.append("Victim headcount unspecified or unobserved")
            unknown_statements.append("Victim headcount was unrecorded or unspecified in one or both records.")
        else:
            vic_match = (vic_a == vic_b)
            vic_status = "MATCH" if vic_match else "DIFFER"
            vic_sym = "✓" if vic_match else "△"
            table_rows.append({
                "feature": "Victim Count",
                "incident_a": f"{vic_a} {'victim' if vic_a == '1' else 'victims'}",
                "incident_b": f"{vic_b} {'victim' if vic_b == '1' else 'victims'}",
                "result": vic_sym,
                "match_status": vic_status,
                "details": f"Victim headcount comparison ({vic_a} vs {vic_b})"
            })
            if vic_match:
                match_items.append(f"Victim headcount ({vic_a})")
                stmt = f"Both involved {vic_a} victim{'s' if vic_a != '1' else ''}."
                matching_chars.append(stmt)
                matched_statements.append(stmt)
            else:
                differ_items.append("Victim headcount")
                stmt = f"Victim headcount differs (Incident A: {vic_a} vs Incident B: {vic_b})."
                differing_chars.append(stmt)
                differing_statements.append(stmt)
                most_meaningful_differences.append(f"Victim headcount diverged: {vic_a} vs {vic_b}.")

        # 4. Strict Count Calculation (Zero Double-Counting, Mutually Exclusive)
        match_count = len(matched_statements)
        differ_count = len(differing_statements)
        unknown_count = len(unknown_statements)
        total_dimensions = len(table_rows)

        summary_match_line = f"{match_count} behavioral characteristic{'s' if match_count != 1 else ''} match."
        summary_differ_line = f"{differ_count} behavioral characteristic{'s' if differ_count != 1 else ''} differ."
        summary_unknown_line = f"{unknown_count} behavioral characteristic{'s' if unknown_count != 1 else ''} unknown or unobserved."
        summary_text = f"{summary_match_line}\n\n{summary_differ_line}" + (f"\n\n{summary_unknown_line}" if unknown_count > 0 else "")

        if not strongest_similarities:
            strongest_similarities = ["Limited behavioral commonality observed across primary dimensions."]
        if not most_meaningful_differences:
            most_meaningful_differences = ["Zero behavioral differences detected across compared dimensions."]

        if differ_count == 0 and unknown_count == 0:
            headline = "Homogeneous Modus Operandi: High behavioral continuity across all compared dimensions."
            narrative = (
                f"Incident A and Incident B exhibit identical behavioral patterns across timing, location setting, "
                f"property involvement, weapon state, injury dynamics, and victim count."
            )
        else:
            diff_names = [r["feature"] for r in table_rows if r["match_status"] == "DIFFER"]
            diff_summary_str = ", ".join(diff_names[:3]) if diff_names else "Observed Dimensions"
            headline = f"Behavioral Transition in {diff_summary_str}: {match_count} dimensions matched, {differ_count} diverged, {unknown_count} unobserved."

            narrative_parts = []
            if transitions:
                narrative_parts.append(f"Observed behavioral differences: {'; '.join(transitions[:3])}.")
            if matching_chars:
                narrative_parts.append(f"Shared behavioral patterns include {matching_chars[0].lower()}.")
            if unknown_chars:
                narrative_parts.append(f"Note: {unknown_count} characteristic(s) were unobserved and strictly excluded from matching.")

            narrative = " ".join(narrative_parts)

        what_changed = {
            "headline": headline,
            "escalations": escalations,
            "transitions": transitions,
            "narrative": narrative,
            "match_count": match_count,
            "differ_count": differ_count,
            "unknown_count": unknown_count,
            "total_dimensions_compared": total_dimensions,
            "summary_match_line": summary_match_line,
            "summary_differ_line": summary_differ_line,
            "summary_unknown_line": summary_unknown_line,
            "summary_text": summary_text,
            "match_items": match_items,
            "differ_items": differ_items,
            "unknown_items": unknown_items,
            "matched_statements": matched_statements,
            "differing_statements": differing_statements,
            "unknown_statements": unknown_statements,
            "same_crime_category": same_crime_category,
            "crime_category_status": crime_category_status,
            "crime_category_detail": crime_category_detail,
            "strongest_similarities": strongest_similarities,
            "most_meaningful_differences": most_meaningful_differences,
        }

        # 5. Audited 7-Domain Behavioral Energies & Covariance
        subprofile_comparison = []
        domain_attributions = []
        total_dot = float(np.dot(vec_a, vec_b)) if (vec_a is not None and vec_b is not None) else 0.0

        for d_meta in SEVEN_DOMAINS_METADATA:
            dom_id = d_meta["domain_id"]
            dom_name = d_meta["domain_name"]
            st: int = int(d_meta["start_idx"])
            en: int = int(d_meta["end_idx"])
            slice_len: int = en - st

            u_g = vec_a[st:en] if vec_a is not None else np.zeros(slice_len)
            v_g = vec_b[st:en] if vec_b is not None else np.zeros(slice_len)

            e_a = round(float(np.linalg.norm(u_g)), 4)
            e_b = round(float(np.linalg.norm(v_g)), 4)
            delta = round(e_b - e_a, 4)

            score_a_pct = round(e_a * 100.0, 1)
            score_b_pct = round(e_b * 100.0, 1)
            delta_pct = round((e_b - e_a) * 100.0, 1)

            if delta > 0:
                delta_display = f"+{delta_pct:.1f} percentage points (+{delta:.3f})"
            elif delta < 0:
                delta_display = f"{delta_pct:.1f} percentage points ({delta:.3f})"
            else:
                delta_display = "0.0 percentage points (0.000)"

            # Data Coverage calculation
            cov_a = calculate_incident_coverage(raw_a, attr_a, d_meta)
            cov_b = calculate_incident_coverage(raw_b, attr_b, d_meta)

            if cov_a["status"] == "Sufficient data" and cov_b["status"] == "Sufficient data":
                cov_status = "Sufficient data"
            elif cov_a["status"] == "Insufficient data" or cov_b["status"] == "Insufficient data":
                cov_status = "Insufficient data"
            else:
                cov_status = "Partial data"

            # Dot-product similarity and attribution
            dot_g = float(np.dot(u_g, v_g))
            if e_a > 0.001 and e_b > 0.001:
                dom_sim_pct = round(max(0.0, min(100.0, (dot_g / (e_a * e_b)) * 100.0)), 1)
            elif e_a == 0.0 and e_b == 0.0:
                dom_sim_pct = None  # Concordantly zero activation, not 100%
            else:
                dom_sim_pct = 0.0

            dom_contrib_pct = round((max(0.0, dot_g) / max(1e-6, total_dot)) * 100.0, 1) if total_dot > 0 else 0.0

            traits_a = extract_domain_contributing_features(raw_a, attr_a, dom_id)
            traits_b = extract_domain_contributing_features(raw_b, attr_b, dom_id)
            missing_a = extract_domain_missing_features(cov_a)
            missing_b = extract_domain_missing_features(cov_b)

            # Plain-English Interpretation
            if e_a == 0.0 and e_b == 0.0:
                interpretation = f"Zero recorded activation in both incidents (no {dom_name.lower()} signal observed, such as unarmed execution or zero physical harm)."
            elif abs(delta) < 0.02:
                interpretation = f"Equal domain scores ({e_a:.3f}); both incidents show similar coordinate activation in {dom_name.lower()}."
            elif delta > 0:
                interpretation = f"Incident B exhibits higher {dom_name.lower()} activation ({e_b:.3f} vs {e_a:.3f}, Δ = +{delta:.3f})."
            else:
                interpretation = f"Incident B exhibits lower {dom_name.lower()} activation ({e_b:.3f} vs {e_a:.3f}, Δ = {delta:.3f})."

            alignment_label = "Aligned" if abs(delta) < 0.1 else ("Elevated in B" if delta > 0 else "Elevated in A")

            subprofile_comparison.append({
                "group_name": dom_name,
                "domain_id": dom_id,
                "description": d_meta["description"],
                "energy_a": e_a,
                "energy_b": e_b,
                "delta": delta,
                "score_a_pct": score_a_pct,
                "score_b_pct": score_b_pct,
                "delta_pct": delta_pct,
                "delta_display": delta_display,
                "data_coverage_a": cov_a["display"],
                "data_coverage_b": cov_b["display"],
                "data_coverage_status": cov_status,
                "domain_similarity_pct": dom_sim_pct,
                "domain_contribution_pct": dom_contrib_pct,
                "alignment": alignment_label,
                "interpretation": interpretation,
                "contributing_features_a": traits_a,
                "contributing_features_b": traits_b,
                "missing_features_a": missing_a,
                "missing_features_b": missing_b,
                "calculation_formula": d_meta["formula"]
            })

            domain_attributions.append({
                "domain": dom_name,
                "dot_product": round(dot_g, 4),
                "contribution_pct": dom_contrib_pct
            })

        # 6. Technical Details Block
        technical_details = {
            "vector_length": 70,
            "norm_vector_a": [round(float(x), 4) for x in vec_a] if vec_a is not None else [],
            "norm_vector_b": [round(float(x), 4) for x in vec_b] if vec_b is not None else [],
            "raw_cosine_similarity": round(raw_cosine, 4),
            "cosine_distance": cosine_distance,
            "similarity_formula": "S(u, v) = u · v = sum_{i=1}^{70} u_i * v_i over unit hypersphere S^69 (||u||_2 = 1.0, ||v||_2 = 1.0)",
            "score_conversion_formula": "Similarity Score (%) = max(0.0, min(100.0, raw_cosine * 100.0))",
            "threshold_tiers": {
                "High Behavioral Affinity": "≥ 90.0%",
                "Moderate Behavioral Affinity": "75.0% – 89.9%",
                "Partial Behavioral Overlap": "50.0% – 74.9%",
                "Divergent Behavioral Profiles": "< 50.0%"
            },
            "domain_attributions": domain_attributions
        }

        # 7. Ethical Non-Offender Boundary and Network Map Explanation
        ethical_advisory = (
            "Crime Compass analyzes recorded incident characteristics and historical behavioral patterns. "
            "Similarity and novelty scores describe patterns in the available data. "
            "They do not establish offender identity, guilt, causation, or investigative linkage. "
            "Behavioral similarity reflects shared modus operandi characteristics between incidents; "
            "it does NOT indicate the same offender or establish investigative linkage without physical forensic evidence. "
            "All graph nodes, connection maps, and network links represent crime categories, behavioral clusters, or environmental patterns—never identified persons."
        )

        return {
            "comparison_title": "🧭 BEHAVIORAL COMPARISON",
            "incident_a": {
                "label": res_a["label"],
                "incident_id": res_a["incident_id"],
                "source_type": res_a["source_type"]
            },
            "incident_b": {
                "label": res_b["label"],
                "incident_id": res_b["incident_id"],
                "source_type": res_b["source_type"]
            },
            "dna_similarity": {
                "similarity_score_pct": similarity_score_pct,
                "cosine_distance": cosine_distance,
                "match_tier": match_tier,
                "affinity_summary": affinity_summary
            },
            "dna_comparison_table": table_rows,
            "matching_characteristics": matching_chars,
            "differing_characteristics": differing_chars,
            "unknown_characteristics": unknown_chars,
            "what_changed": what_changed,
            "subprofile_comparison": subprofile_comparison,
            "technical_details": technical_details,
            "ethical_advisory": ethical_advisory
        }


# Global singleton instance
comparison_service = BehavioralComparisonService()
