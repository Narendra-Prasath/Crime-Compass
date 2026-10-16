"""
Crime Compass 🧭 — Domain Coverage, Fingerprint, Similarity & Explainability Tests
Tests Parts A through I requirements:
- Behavioral Data Coverage calculation across 6 schema domains
- Missing and Not Applicable field handling
- Compact Behavioral Fingerprint with Yes/No/Unknown/Not applicable statuses
- Query Self-Exclusion in similarity search
- Observed Feature Comparison (Similar/Different/Unknown)
- Neutral novelty detection labels
- Unknown trait handling in incident comparison (unknowns not counted as matches)
"""

import pytest
import numpy as np
from src.features.input_bridge import bridge
from src.services.analysis_engine import analysis_engine
from src.services.comparison_service import comparison_service
from src.services.novelty_service import novelty_service
from src.api.state import state


@pytest.fixture(scope="module", autouse=True)
def ensure_state_ready():
    """Ensure state is loaded once for all tests."""
    if not state.is_ready:
        state.load_all()


def test_domain_coverage_calculation():
    """Part B: Test that domain coverage computes valid / applicable * 100% across the 6 domains."""
    payload = {
        "scenario_title": "Commercial Armed Robbery",
        "incident_date": "2024-11-15",
        "incident_time": "21:45",
        "incident_hour": 21,
        "is_weekend": False,
        "crime_category": "person_property",
        "is_attempted": False,
        "offense_count": 2,
        "population_setting": "mid_sized_city",
        "has_weapon": True,
        "weapon_count": 2,
        "victim_count": 2,
        "victim_avg_age": 34.0,
        "offender_count": 2,
        "offender_avg_age": 22.0,
        "has_property": True,
        "property_value": 3500.0,
        "has_injury": True,
        "has_arrest": False
    }

    coverage = bridge.compute_domain_data_coverage(payload)

    assert "overall_coverage_pct" in coverage
    assert 0.0 <= coverage["overall_coverage_pct"] <= 100.0
    assert "domains" in coverage
    domains = coverage["domains"]

    # Must contain exactly the 6 schema-supported domains
    expected_domains = [
        "temporal_dynamics",
        "crime_characteristics",
        "location_and_environment",
        "method_and_activity",
        "people_and_context",
        "property_and_impact"
    ]
    for dom in expected_domains:
        assert dom in domains, f"Missing domain: {dom}"
        info = domains[dom]
        assert "coverage_pct" in info
        assert "available_fields_count" in info
        assert "unspecified_fields_count" in info
        assert "not_applicable_fields_count" in info
        assert "description" in info
        assert 0.0 <= info["coverage_pct"] <= 100.0

        # Verify formula: available / (available + unspecified) * 100%
        denom = info["available_fields_count"] + info["unspecified_fields_count"]
        if denom > 0:
            expected_pct = round((info["available_fields_count"] / denom) * 100.0, 1)
            assert info["coverage_pct"] == expected_pct


def test_not_applicable_fields_not_penalized():
    """Part B: When prerequisite flags are False, dependent fields are not applicable, not penalized."""
    # Unarmed, no property, no injuries
    payload = {
        "scenario_title": "Simple Disorderly Conduct",
        "incident_date": "2024-03-10",
        "incident_time": "14:00",
        "crime_category": "society",
        "population_setting": "small_town",
        "has_weapon": False,
        "has_property": False,
        "has_injury": False,
        "has_arrest": False,
        "has_criminal_activity": False
    }

    coverage = bridge.compute_domain_data_coverage(payload)
    method_info = coverage["domains"]["method_and_activity"]
    prop_info = coverage["domains"]["property_and_impact"]

    # weapon_count and weapon_types_count must be counted as not_applicable, NOT unspecified
    assert method_info["not_applicable_fields_count"] >= 2
    # property fields must be counted as not_applicable
    assert prop_info["not_applicable_fields_count"] >= 4
    # Coverage must not treat not-applicable fields as missing/unspecified
    assert "advisory" in coverage
    assert "negative evidence" in coverage["advisory"].lower()


def test_compact_behavioral_fingerprint():
    """Part C: Test compact behavioral traits with clear Yes / No / Unknown / Not applicable statuses."""
    payload = {
        "scenario_title": "Night Robbery",
        "incident_date": "2024-05-18",  # Saturday
        "incident_time": "23:30",
        "crime_category": "person_property",
        "population_setting": "metropolis",
        "has_weapon": True,
        "has_injury": False,
        "has_property": True
    }

    raw_vec, _, _ = bridge.encode(payload)
    human_dna = bridge.generate_human_readable_fingerprint(payload, raw_vec)

    assert "compact_traits" in human_dna
    traits = human_dna["compact_traits"]
    assert len(traits) >= 6

    trait_names = [t["trait_name"] for t in traits]
    assert any("Time" in name for name in trait_names)
    assert any("Weekly" in name for name in trait_names)
    assert any("Weapon" in name for name in trait_names)
    assert any("Injury" in name for name in trait_names)

    valid_statuses = {"Yes", "No", "Unknown", "Applicable", "Not applicable"}
    for t in traits:
        assert t["status"] in valid_statuses, f"Invalid status: {t['status']}"
        assert "value" in t
        assert "detail" in t

    # In our payload: hour 23 -> Nighttime (Yes), Saturday -> Weekend (Yes), Weapon -> Yes, Injury -> No
    time_trait = next(t for t in traits if "Time" in t["trait_name"])
    assert time_trait["status"] == "Yes"

    weapon_trait = next(t for t in traits if "Weapon" in t["trait_name"])
    assert weapon_trait["status"] == "Yes"

    injury_trait = next(t for t in traits if "Injury" in t["trait_name"])
    assert injury_trait["status"] == "No"


def test_similarity_query_self_exclusion():
    """Part D: When a historical incident ID is queried, it is never returned as its own neighbor."""
    if not state.incident_ids:
        pytest.skip("Historical incident index is empty")

    query_id = state.incident_ids[0]
    profile = state.get_incident_profile(query_id)
    ctx = profile.get("context", {}) if profile else {}

    payload = {
        "incident_id": query_id,
        "scenario_title": f"Test Query {query_id}",
        "incident_date": "2024-06-15",
        "incident_time": f"{ctx.get('incident_hour', 14):02d}:00",
        "crime_category": ctx.get("primary_crime_category", "property").lower().replace(" ", "_"),
        "has_weapon": bool(ctx.get("has_weapon", False)),
        "has_property": bool(ctx.get("has_property", False)),
        "has_injury": bool(ctx.get("has_injury", False))
    }

    result = analysis_engine.analyze(payload, top_k=5)
    matches = result["similar_historical_incidents"]

    assert len(matches) > 0
    # Query incident must NOT appear in the nearest neighbor matches
    matched_ids = [m["incident_id"] for m in matches]
    assert query_id not in matched_ids, f"Self-exclusion failed: {query_id} found in {matched_ids}"


def test_similarity_score_and_observed_feature_comparison():
    """Part D & E: Similarity score has explanation and each match includes observed feature comparison."""
    payload = {
        "scenario_title": "Commercial Burglary",
        "incident_date": "2024-04-12",
        "incident_time": "03:15",
        "crime_category": "property",
        "population_setting": "suburban",
        "has_weapon": False,
        "has_property": True,
        "has_injury": False
    }

    result = analysis_engine.analyze(payload, top_k=3)
    matches = result["similar_historical_incidents"]

    assert len(matches) > 0
    top_match = matches[0]

    # Verify score limitations exist
    assert "metric_explanation" in result["similar_behavioral_incidents"]
    assert "not a probability" in result["similar_behavioral_incidents"]["metric_explanation"].lower()
    assert "score_limitations" in result["dna_similarity"]

    # Verify observed feature comparison exists on every match
    assert "observed_feature_comparison" in top_match
    comp = top_match["observed_feature_comparison"]
    assert "domains" in comp
    assert "methodology_note" in comp
    assert "not SHAP" in comp["methodology_note"]

    # Domains must be categorized as Similar, Different, or Unknown
    for dom in comp["domains"]:
        assert dom["status"] in ("Similar", "Different", "Unknown")
        assert "details" in dom


def test_novelty_neutral_labels():
    """Part H: Novelty detection outputs neutral labels and does not infer offender criminality."""
    payload = {
        "scenario_title": "Standard Theft",
        "incident_date": "2024-07-20",
        "incident_time": "13:00",
        "crime_category": "property",
        "has_weapon": False,
        "has_property": True
    }

    result = analysis_engine.analyze(payload, top_k=3)
    novelty = result["novelty"]

    assert "neutral_label" in novelty
    valid_neutral_labels = [
        "Commonly Observed Combination",
        "Less Common Combination",
        "Unusual Combination",
        "Insufficient Information"
    ]
    assert novelty["neutral_label"] in valid_neutral_labels
    assert "method_used" in novelty
    assert "data_limitations" in novelty
    assert "danger" not in novelty["neutral_label"].lower()
    assert "criminality" not in novelty["neutral_label"].lower()


def test_comparison_unknown_fields_not_counted_as_matches():
    """Part I: In incident comparison, unknown/missing fields are marked UNKNOWN and not counted as MATCH."""
    # Incident A has known timing and known weapon
    spec_a = {
        "label": "Incident A",
        "payload": {
            "incident_time": "22:00",
            "is_night": True,
            "has_weapon": True,
            "weapon_count": 1,
            "has_property": True,
            "crime_category": "property",
            "has_injury": True
        }
    }

    # Incident B omits weapon and injury (unspecified/unknown)
    spec_b = {
        "label": "Incident B",
        "payload": {
            "incident_time": "22:00",
            "is_night": True,
            "has_weapon": None,  # Unknown
            "has_property": True,
            "crime_category": "property",
            "has_injury": None   # Unknown
        }
    }

    comp = comparison_service.compare(spec_a, spec_b)
    table = comp["dna_comparison_table"]

    # Find rows for Weapon and Injury
    wep_row = next((r for r in table if r["feature"] == "Weapon"), None)
    inj_row = next((r for r in table if r["feature"] == "Injury"), None)

    assert wep_row is not None
    assert inj_row is not None

    # Both must be UNKNOWN, symbol '?', and NOT MATCH
    assert wep_row["match_status"] == "UNKNOWN"
    assert wep_row["result"] == "?"
    assert inj_row["match_status"] == "UNKNOWN"
    assert inj_row["result"] == "?"

    # Unknowns must NOT be in matching_characteristics
    for match_item in comp["matching_characteristics"]:
        assert "weapon" not in match_item.lower()
        assert "injury" not in match_item.lower()

    # Must populate unknown_characteristics
    assert "unknown_characteristics" in comp
    assert len(comp["unknown_characteristics"]) >= 2
