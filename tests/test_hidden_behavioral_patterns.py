"""
CRIME DNA — Hidden Behavioral Pattern Discovery Tests

Tests the user-facing Hidden Behavioral Pattern feature, ensuring:
1. Pattern association with empirical historical clusters and cross-crime archetypes
2. Correct extraction of pattern identifier, behavioral characteristics, and formulas
3. Grounding in actual historical models (no hardcoded incident counts, categories, or scores)
4. Scientific confidence tiering based on spherical cosine similarity
5. Cross-category representation breakdown
6. Strict adherence to ethical non-offender attribution guidelines
7. End-to-end FastAPI endpoint serialization
"""

import json
import pytest
import numpy as np
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.analysis_engine import analysis_engine
from src.services.pattern_discovery import pattern_discovery_service
from src.api.state import state


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_hidden_pattern_detection_structure():
    """Validates that pattern discovery produces all required fields with proper types."""
    incident = {
        "scenario_title": "Nocturnal Residential Burglary",
        "incident_date": "2024-03-15",
        "incident_time": "23:45",
        "crime_category": "burglary",
        "location_type": "residential",
        "is_weekend": True,
        "has_property": True,
        "property_value": 2500.0,
        "has_weapon": False,
        "has_injury": False
    }
    result = analysis_engine.analyze(incident)

    assert "hidden_behavioral_patterns" in result
    hbp = result["hidden_behavioral_patterns"]

    # 1. Pattern identifier & name
    assert hbp["pattern_detected"] is True
    assert hbp["pattern_identifier"].startswith("CCP_")
    assert isinstance(hbp["pattern_name"], str) and len(hbp["pattern_name"]) > 0
    assert isinstance(hbp["archetype_name"], str)

    # 2. Behavioral characteristics & formula
    assert isinstance(hbp["behavioral_characteristics"], list)
    assert len(hbp["behavioral_characteristics"]) >= 3
    assert isinstance(hbp["behavioral_formula"], str)
    assert " + " in hbp["behavioral_formula"]

    # 3. Supporting historical incidents & categories
    assert isinstance(hbp["number_of_supporting_historical_incidents"], int)
    assert hbp["number_of_supporting_historical_incidents"] > 0
    assert isinstance(hbp["number_of_crime_categories_represented"], int)
    assert hbp["number_of_crime_categories_represented"] >= 1
    assert isinstance(hbp["relevant_crime_categories"], list)
    assert len(hbp["relevant_crime_categories"]) >= 1

    # 4. Association strength / confidence
    assoc = hbp["association_strength"]
    assert "association_score" in assoc
    assert "confidence_score_pct" in assoc
    assert "confidence_tier" in assoc
    assert assoc["confidence_tier"] in ["Strong Association", "Moderate Association", "Weak Association"]
    assert 0.0 <= assoc["confidence_score_pct"] <= 100.0
    assert 0.0 <= assoc["distance_to_centroid"] <= 2.0


def test_values_come_from_actual_model_and_not_hardcoded():
    """Proves that incident counts, category counts, and pattern IDs vary dynamically based on ML model output."""
    burglary_incident = {
        "incident_date": "2024-03-15",
        "incident_time": "23:45",
        "crime_category": "burglary",
        "location_type": "residential",
        "is_weekend": True,
        "has_property": True,
        "has_weapon": False,
        "has_injury": False
    }

    assault_incident = {
        "incident_date": "2024-07-20",
        "incident_time": "14:15",
        "crime_category": "assault",
        "location_type": "public_space",
        "is_weekend": False,
        "has_property": False,
        "has_weapon": True,
        "has_injury": True,
        "has_relationship": True
    }

    res_burglary = analysis_engine.analyze(burglary_incident)["hidden_behavioral_patterns"]
    res_assault = analysis_engine.analyze(assault_incident)["hidden_behavioral_patterns"]

    # Patterns must differ based on behavior
    assert res_burglary["pattern_identifier"] != res_assault["pattern_identifier"]
    assert res_burglary["pattern_name"] != res_assault["pattern_name"]
    assert res_burglary["behavioral_formula"] != res_assault["behavioral_formula"]

    # Incident counts must match the actual empirical count in cross_crime_patterns.json
    cc_key_burg = res_burglary["pattern_identifier"]
    cc_key_aslt = res_assault["pattern_identifier"]
    expected_burg_count = state.cross_crime_patterns[cc_key_burg]["total_incidents"]
    expected_aslt_count = state.cross_crime_patterns[cc_key_aslt]["total_incidents"]

    assert res_burglary["number_of_supporting_historical_incidents"] == expected_burg_count
    assert res_assault["number_of_supporting_historical_incidents"] == expected_aslt_count


def test_behavioral_characteristics_formula_synthesis():
    """Validates that the behavioral formula components match the actual incident input attributes."""
    incident = {
        "incident_date": "2024-02-10",
        "incident_time": "22:15",
        "location_type": "residential",
        "has_property": True,
        "has_injury": False,
        "has_weapon": False
    }
    res = analysis_engine.analyze(incident)["hidden_behavioral_patterns"]

    traits = res["behavioral_characteristics"]
    formula = res["behavioral_formula"]

    # Should detect: Night, Residential, Property involved, No injury
    assert "Night" in traits
    assert "Residential" in traits
    assert "Property involved" in traits
    assert "No injury" in traits
    assert formula == "Night + Residential + Property involved + No injury"


def test_cross_crime_text_and_shared_profile_wording():
    """Ensures approved cross-crime phrasing without claiming offender identity."""
    incident = {
        "incident_date": "2024-05-12",
        "incident_time": "12:00",
        "crime_category": "theft",
        "location_type": "commercial",
        "has_property": True,
        "has_weapon": False,
        "has_injury": False
    }
    res = analysis_engine.analyze(incident)["hidden_behavioral_patterns"]

    assert res["is_cross_crime_pattern"] is True
    assert res["cross_crime_summary"] == "Found across multiple crime categories."
    assert "These crime categories share a similar behavioral profile." in res["shared_profile_text"]


def test_ethical_non_offender_guidelines():
    """Guarantees that results never claim to identify an individual perpetrator or legal guilt."""
    incident = {
        "incident_date": "2024-09-01",
        "incident_time": "02:00",
        "crime_category": "robbery",
        "has_weapon": True,
        "has_injury": True
    }
    res = analysis_engine.analyze(incident)["hidden_behavioral_patterns"]

    advisory = res["ethical_advisory"]
    assert "not that offenses were committed by the same individual" in advisory
    assert "offender" not in res["pattern_name"].lower()
    assert "perpetrator" not in res["shared_profile_text"].lower()


def test_multi_pattern_associated_patterns_ranking():
    """Validates that secondary associated patterns are ranked by similarity to centroid."""
    incident = {
        "incident_date": "2024-06-18",
        "incident_time": "15:30",
        "location_type": "commercial",
        "has_property": True,
        "has_weapon": False
    }
    res = analysis_engine.analyze(incident)["hidden_behavioral_patterns"]

    associated = res["associated_patterns"]
    assert isinstance(associated, list)
    assert len(associated) == 8  # Evaluates all 8 cluster centroids

    # First pattern in list must be primary
    assert associated[0]["is_primary"] is True
    assert associated[0]["pattern_identifier"] == res["pattern_identifier"]

    # Verify descending similarity order
    scores = [p["association_score"] for p in associated]
    assert scores == sorted(scores, reverse=True)


def test_api_endpoint_serializes_hidden_behavioral_patterns(client):
    """End-to-end integration test verifying FastAPI returns hidden_behavioral_patterns with HTTP 200."""
    payload = {
        "scenario_title": "End-to-End API Test",
        "incident_date": "2024-10-01",
        "incident_time": "01:30",
        "crime_category": "burglary",
        "location_type": "residential",
        "is_weekend": True,
        "has_property": True,
        "has_weapon": False,
        "has_injury": False
    }
    resp = client.post("/api/analyze/input", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "hidden_behavioral_patterns" in data
    hbp = data["hidden_behavioral_patterns"]

    assert hbp["pattern_detected"] is True
    assert hbp["pattern_identifier"] == "CCP_03"
    assert "Burglary" in hbp["pattern_name"]
    assert hbp["behavioral_formula"] == "Night + Residential + Property involved + No injury"
    assert hbp["number_of_supporting_historical_incidents"] == 33335
    assert hbp["number_of_crime_categories_represented"] == 3
    assert len(hbp["relevant_crime_categories"]) == 3
    assert hbp["association_strength"]["confidence_tier"] in ["Strong Association", "Moderate Association"]
    assert hbp["cross_crime_summary"] == "Found across multiple crime categories."
    assert "These crime categories share a similar behavioral profile." in hbp["shared_profile_text"]
