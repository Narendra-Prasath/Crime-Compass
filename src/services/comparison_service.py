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
            characteristics, and "What Changed?" analysis.
        """
        if state is None:
            from src.api.state import state as global_state
            state = global_state

        # 1. Resolve both incidents to standardized representations
        res_a = self.resolve_incident(incident_a, state, default_label="Incident A")
        res_b = self.resolve_incident(incident_b, state, default_label="Incident B")

        vec_a = res_a["norm_vector"]
        vec_b = res_b["norm_vector"]

        # Ensure unit L2 normalization
        if vec_a is not None:
            norm_a = np.linalg.norm(vec_a)
            vec_a = vec_a / (norm_a if norm_a > 0 else 1.0)
        if vec_b is not None:
            norm_b = np.linalg.norm(vec_b)
            vec_b = vec_b / (norm_b if norm_b > 0 else 1.0)

        # 2. Scientifically valid DNA similarity score using cosine representation
        if vec_a is not None and vec_b is not None:
            raw_cosine = float(np.dot(vec_a, vec_b))
            similarity_score_pct = round(max(0.0, min(100.0, raw_cosine * 100.0)), 2)
            cosine_distance = round(max(0.0, min(2.0, 1.0 - raw_cosine)), 4)
        else:
            raw_cosine = 0.0
            similarity_score_pct = 0.0
            cosine_distance = 1.0

        if similarity_score_pct >= 90.0:
            match_tier = "High Behavioral Affinity"
            affinity_summary = "Very high alignment across modus operandi dimensions."
        elif similarity_score_pct >= 75.0:
            match_tier = "Moderate Behavioral Affinity"
            affinity_summary = "Noticeable behavioral alignment with identifiable divergences."
        elif similarity_score_pct >= 50.0:
            match_tier = "Partial Behavioral Overlap"
            affinity_summary = "Shared characteristics in select operational domains."
        else:
            match_tier = "Divergent Behavioral Profiles"
            affinity_summary = "Substantially distinct modus operandi profiles."

        # 3. Construct Feature-by-Feature DNA Comparison Table
        attr_a = res_a["attributes"]
        attr_b = res_b["attributes"]

        table_rows = []
        matching_chars = []
        differing_chars = []
        unknown_chars = []
        transitions = []
        escalations = []
        match_items = []
        differ_items = []
        unknown_items = []
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
            return s in ("unknown", "unspecified", "not recorded", "null", "?")

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
                matching_chars.append(f"Consistent diurnal timing ({time_val_a.lower()} execution)")
                strongest_similarities.append(f"Consistent timing: both offenses occurred during {time_val_a.lower()} hours.")
            else:
                differ_items.append("Timing / diurnal pattern")
                differing_chars.append(f"Diurnal shift: Incident A ({time_val_a}) vs Incident B ({time_val_b})")
                transitions.append(f"Timing transitioned from {time_val_a} to {time_val_b}")
                most_meaningful_differences.append(f"Diurnal shift: Incident A was {time_val_a.lower()} while Incident B was {time_val_b.lower()}.")

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
                matching_chars.append(f"Identical location setting ({loc_a})")
                strongest_similarities.append(f"Identical setting: both incidents targeted {loc_a.lower()} environments.")
            else:
                differ_items.append("Location context")
                differing_chars.append(f"Spatial setting delta: Incident A ({loc_a}) vs Incident B ({loc_b})")
                transitions.append(f"Target location environment shifted from {loc_a} to {loc_b}")
                most_meaningful_differences.append(f"Target environment differed: Incident A was {loc_a} vs Incident B was {loc_b}.")

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
                matching_chars.append(f"Consistent property involvement ({'property acquisition' if attr_a['has_property'] else 'no property target'})")
                if attr_a["has_property"]:
                    strongest_similarities.append("Target property motive: both incidents sought tangible property acquisition.")
                else:
                    strongest_similarities.append("Non-property motive: neither incident targeted property theft.")
            else:
                differ_items.append("Property involvement")
                differing_chars.append(f"Property objective delta: Incident A ({prop_a}) vs Incident B ({prop_b})")
                transitions.append(f"Property involvement shifted from {prop_a} to {prop_b}")
                most_meaningful_differences.append(f"Property motive differed: Incident A was {prop_a.lower()} vs Incident B was {prop_b.lower()}.")

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
                matching_chars.append(f"Equally {'armed' if attr_a['has_weapon'] else 'unarmed'} execution")
                if not attr_a["has_weapon"]:
                    strongest_similarities.append("Unarmed execution: neither incident deployed weapons or lethal force.")
                else:
                    strongest_similarities.append("Armed encounter: both incidents involved weapons.")
            else:
                differ_items.append("Weapon context")
                differing_chars.append(f"Weapon escalation/delta: Incident A ({wep_a}) vs Incident B ({wep_b})")
                transitions.append(f"Weapon deployment changed from {wep_a} to {wep_b}")
                if not attr_a["has_weapon"] and attr_b["has_weapon"]:
                    escalations.append("Weapon Escalation: Transitioned from unarmed to armed encounter.")
                    most_meaningful_differences.append(f"Weapon escalation: Incident A was unarmed while Incident B introduced {wep_b}.")
                elif attr_a["has_weapon"] and not attr_b["has_weapon"]:
                    escalations.append("Weapon De-escalation: Transitioned from armed encounter to unarmed execution.")
                    most_meaningful_differences.append("Weapon de-escalation: armed encounter in Incident A reduced to unarmed in Incident B.")
                else:
                    most_meaningful_differences.append(f"Weapon type disparity: {wep_a} vs {wep_b}.")

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
                matching_chars.append(f"Harm dynamic aligned ({'injury inflicted' if attr_a['has_injury'] else 'no physical injury'})")
                if not attr_a["has_injury"]:
                    strongest_similarities.append("Zero physical harm: no victim injuries occurred in either offense.")
                else:
                    strongest_similarities.append("Harm outcome: physical injuries were sustained in both offenses.")
            else:
                differ_items.append("Injury / physical harm")
                differing_chars.append(f"Physical harm disparity: Incident A ({inj_a}) vs Incident B ({inj_b})")
                transitions.append(f"Injury outcome shifted from {inj_a} to {inj_b}")
                if not attr_a["has_injury"] and attr_b["has_injury"]:
                    escalations.append("Harm Escalation: Physical victim injury was inflicted in Incident B.")
                    most_meaningful_differences.append("Harm escalation: Incident B resulted in victim injury whereas Incident A was non-injurious.")
                else:
                    most_meaningful_differences.append(f"Injury outcome delta: {inj_a} vs {inj_b}.")

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
                matching_chars.append(f"Identical offense category ({crime_a})")
                crime_category_status = "Same Crime Category"
                crime_category_detail = f"Both incidents belong to the same statutory category: {crime_a}."
                strongest_similarities.append(f"Statutory crime category aligned: {crime_a}.")
            else:
                differ_items.append("Crime category")
                differing_chars.append(f"Cross-category divergence: Incident A ({crime_a}) vs Incident B ({crime_b})")
                transitions.append(f"Statutory category shifted from {crime_a} to {crime_b}")
                crime_category_status = "Different Crime Category"
                crime_category_detail = f"Different crime categories: Incident A is {crime_a} while Incident B is {crime_b}. The DNA engine evaluates behavioral MO alignment despite different legal labels."
                most_meaningful_differences.append(f"Statutory crime category shifted from {crime_a} to {crime_b}.")

        # --- Dimension 7: Victim Count ---
        vic_a = str(attr_a.get("victim_count", "1"))
        vic_b = str(attr_b.get("victim_count", "1"))
        vic_match = (vic_a == vic_b)
        table_rows.append({
            "feature": "Victim Count",
            "incident_a": f"{vic_a} {'victim' if vic_a == '1' else 'victims'}",
            "incident_b": f"{vic_b} {'victim' if vic_b == '1' else 'victims'}",
            "result": "✓" if vic_match else "△",
            "match_status": "MATCH" if vic_match else "DIFFER",
            "details": f"Victim headcount comparison ({vic_a} vs {vic_b})"
        })
        if vic_match:
            match_items.append(f"Victim headcount ({vic_a})")
            matching_chars.append(f"Equal victim count ({vic_a})")
        else:
            differ_items.append("Victim headcount")
            differing_chars.append(f"Victim headcount disparity ({vic_a} vs {vic_b})")
            most_meaningful_differences.append(f"Victim headcount diverged: {vic_a} vs {vic_b}.")

        # 4. Synthesize "What Changed?" Prominent Section
        match_count = len(match_items)
        differ_count = len(differ_items)
        unknown_count = len(unknown_items)

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
                f"property involvement, weapon state, and injury dynamics."
            )
        else:
            diff_names = [r["feature"] for r in table_rows if r["match_status"] == "DIFFER"]
            diff_summary_str = ", ".join(diff_names[:3]) if diff_names else "Observed Dimensions"
            headline = f"Behavioral Transition in {diff_summary_str}: {match_count} dimensions matched, {differ_count} diverged, {unknown_count} unobserved."

            narrative_parts = []
            if escalations:
                narrative_parts.append(" ".join(escalations))
            if transitions:
                narrative_parts.append(f"Key operational shifts observed: {'; '.join(transitions[:3])}.")
            if matching_chars:
                narrative_parts.append(f"Underlying behavioral continuity remains rooted in {matching_chars[0].lower()}.")
            if unknown_chars:
                narrative_parts.append(f"Note: {len(unknown_chars)} characteristic(s) were unobserved and not counted toward similarity.")

            narrative = " ".join(narrative_parts)

        what_changed = {
            "headline": headline,
            "escalations": escalations,
            "transitions": transitions,
            "narrative": narrative,
            "match_count": match_count,
            "differ_count": differ_count,
            "unknown_count": unknown_count,
            "total_dimensions_compared": len(table_rows),
            "summary_match_line": summary_match_line,
            "summary_differ_line": summary_differ_line,
            "summary_unknown_line": summary_unknown_line,
            "summary_text": summary_text,
            "match_items": match_items,
            "differ_items": differ_items,
            "unknown_items": unknown_items,
            "same_crime_category": same_crime_category,
            "crime_category_status": crime_category_status,
            "crime_category_detail": crime_category_detail,
            "strongest_similarities": strongest_similarities,
            "most_meaningful_differences": most_meaningful_differences,
        }

        # 5. Subprofile Group Energy Comparison
        energies_a = res_a.get("subprofile_energies", {})
        energies_b = res_b.get("subprofile_energies", {})
        all_groups = list(dict.fromkeys(list(energies_a.keys()) + list(energies_b.keys())))

        subprofile_comparison = []
        for grp in all_groups:
            e_a = energies_a.get(grp, 0.0)
            e_b = energies_b.get(grp, 0.0)
            delta = round(e_b - e_a, 4)
            subprofile_comparison.append({
                "group_name": grp.replace("_", " ").title(),
                "energy_a": e_a,
                "energy_b": e_b,
                "delta": delta,
                "alignment": "Aligned" if abs(delta) < 0.1 else ("Elevated in B" if delta > 0 else "Elevated in A")
            })

        # 6. Ethical Non-Offender Boundary and Network Map Explanation
        ethical_advisory = (
            "Based on patterns learned from historical incidents. "
            "CRIME DNA analyzes behavioral patterns in historical incident data. "
            "Similarity or novelty does not establish offender identity, guilt, or causation. "
            "Behavioral similarity reflects shared modus operandi characteristics between incidents. "
            "It does NOT indicate the same offender or establish investigative linkage without physical forensic evidence. "
            "All graph nodes and connection links represent crime categories, modus operandi clusters, or environmental patterns—never identified persons."
        )

        return {
            "comparison_title": "🧬 CRIME DNA COMPARISON",
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
            "ethical_advisory": ethical_advisory
        }


# Global singleton instance
comparison_service = BehavioralComparisonService()
