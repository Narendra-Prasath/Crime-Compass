"""
Unit and Integration Tests for Explore Patterns Feature
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state
from src.services.pattern_exploration_service import pattern_exploration_service


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_pattern_exploration_service_cards(client):
    """Test that all 8 pattern cards are returned with exact empirical statistics."""
    res = pattern_exploration_service.get_all_pattern_cards(state)
    assert res["total_patterns"] == 8
    assert res["corpus_incident_count"] == 220663
    patterns = res["patterns"]
    assert len(patterns) == 8

    # Validate cards structure and content
    for idx, card in enumerate(patterns):
        assert card["pattern_id"] == f"PATTERN {idx + 1:02d}"
        assert card["cluster_id"] == idx
        assert card["supporting_incident_count"] > 0
        assert card["percentage_of_total"] > 0.0
        assert "+" in card["behavioral_formula"]
        assert len(card["key_characteristics"]) >= 2
        assert "crime categories" in card["crime_categories_summary"].lower()
        assert card["time_information"]
        assert 0.0 <= card["similarity_strength_score"] <= 100.0


def test_pattern_exploration_service_detail(client):
    """Test retrieving detail views across various identifier formats."""
    # Pattern 01 / cluster 0
    detail = pattern_exploration_service.get_pattern_detail(0, state)
    assert detail["pattern_id"] == "PATTERN 01"
    assert detail["cluster_id"] == 0
    assert "why_this_pattern_exists" in detail
    assert len(detail["why_this_pattern_exists"]) > 20
    assert len(detail["crime_categories_involved"]) >= 1
    assert "evolution_timeline" in detail
    assert len(detail["evolution_timeline"]) == 3
    # Check 3 evolution stages: early, middle, later
    stages = [s["stage_id"] for s in detail["evolution_timeline"]]
    assert stages == ["early", "middle", "later"]
    assert "supporting_evidence" in detail
    assert detail["supporting_evidence"]["total_incidents"] == detail["supporting_incident_count"]
    assert "analysis_details" in detail
    assert "ethical_advisory" in detail

    # Pattern by code CCP_03
    detail_ccp = pattern_exploration_service.get_pattern_detail("CCP_03", state)
    assert detail_ccp["pattern_id"] == "PATTERN 04"
    assert detail_ccp["cluster_id"] == 3

    # Pattern by string "PATTERN 02"
    detail_str = pattern_exploration_service.get_pattern_detail("PATTERN 02", state)
    assert detail_str["pattern_id"] == "PATTERN 02"
    assert detail_str["cluster_id"] == 1


def test_explore_patterns_api_endpoints(client):
    """Test GET /api/patterns and GET /api/patterns/{id} endpoints."""
    # List patterns
    r = client.get("/api/patterns")
    assert r.status_code == 200
    data = r.json()
    assert data["total_patterns"] == 8
    assert data["corpus_incident_count"] == 220663
    assert len(data["patterns"]) == 8

    p1 = data["patterns"][0]
    assert p1["pattern_id"] == "PATTERN 01"
    assert "supporting_incident_count" in p1

    # Detail by pattern_id
    r_detail = client.get("/api/patterns/PATTERN 01")
    assert r_detail.status_code == 200
    det = r_detail.json()
    assert det["pattern_id"] == "PATTERN 01"
    assert det["why_this_pattern_exists"]
    assert det["crime_categories_involved"]
    assert len(det["evolution_timeline"]) == 3

    # Detail by integer id
    r_detail_int = client.get("/api/patterns/0")
    assert r_detail_int.status_code == 200

    # Cluster route fallback /api/clusters/explore
    r_clust = client.get("/api/clusters/explore")
    assert r_clust.status_code == 200
    assert len(r_clust.json()["patterns"]) == 8


def test_ethical_advisory_in_detail(client):
    """Ensure no claims are made regarding individual offender linkage."""
    detail = pattern_exploration_service.get_pattern_detail("PATTERN 01", state)
    advisory = detail["ethical_advisory"].lower()
    assert "not establish that offenses were committed by the same individual" in advisory
