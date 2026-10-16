"""
CRIME DNA — Input Analysis API Route Tests
Validates POST /api/analyze/input, GET /api/analyze/presets, and payload validation.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_analysis_presets(client: TestClient):
    response = client.get("/api/analyze/presets")
    assert response.status_code == 200
    presets = response.json()
    assert isinstance(presets, list)
    assert len(presets) >= 4
    for p in presets:
        assert "id" in p
        assert "title" in p
        assert "payload" in p
        assert "crime_category" in p["payload"]


def test_post_analyze_preset_payload(client: TestClient):
    presets_res = client.get("/api/analyze/presets")
    assert presets_res.status_code == 200
    first_preset = presets_res.json()[0]

    response = client.post("/api/analyze/input", json=first_preset["payload"])
    assert response.status_code == 200
    data = response.json()

    # Verify all 8 intelligence perspectives in response
    assert "analysis_id" in data
    assert "scenario_title" in data
    assert "behavioral_dna" in data
    assert data["behavioral_dna"]["vector_dimension"] == 70
    assert len(data["behavioral_dna"]["subprofile_energies"]) == 7

    assert "cluster_assignment" in data
    assert "cluster_name" in data["cluster_assignment"]
    assert "distance_to_centroid" in data["cluster_assignment"]

    assert "cross_crime_mapping" in data
    assert "cross_crime_pattern_name" in data["cross_crime_mapping"]

    assert "novelty_assessment" in data
    assert "novelty_score" in data["novelty_assessment"]
    assert "novelty_tier" in data["novelty_assessment"]

    assert "similar_historical_incidents" in data
    assert len(data["similar_historical_incidents"]) == 5
    top_match = data["similar_historical_incidents"][0]
    assert "incident_id" in top_match
    assert "similarity_score_pct" in top_match
    assert top_match["similarity_score_pct"] > 0

    assert "why_similar_explanation" in data
    assert "target_incident_id" in data["why_similar_explanation"]

    assert "evolutionary_context" in data
    assert "dna_comparison" in data
    assert "ethical_advisory" in data
    assert "does not identify offenders" in data["ethical_advisory"].lower()


def test_post_analyze_custom_incident(client: TestClient):
    custom_payload = {
        "scenario_title": "Unit Test Custom Case",
        "incident_date": "2024-05-12",
        "incident_time": "03:15",
        "crime_category": "property",
        "population_setting": "metropolitan_core",
        "has_weapon": False,
        "victim_count": 1,
        "offender_count": 1,
        "property_value": 4500.0,
        "has_property": True,
        "has_stolen_property": True
    }
    response = client.post("/api/analyze/input", json=custom_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_title"] == "Unit Test Custom Case"
    assert len(data["similar_historical_incidents"]) == 5


def test_validation_negative_counts(client: TestClient):
    invalid_payload = {
        "crime_category": "property",
        "victim_count": -5
    }
    response = client.post("/api/analyze/input", json=invalid_payload)
    assert response.status_code == 422
