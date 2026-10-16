"""
Unit and Integration Tests for Behavioral Connection Map Graph Generation
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state
from src.services.behavioral_graph_service import behavioral_graph_service


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_behavioral_connection_map_generation(client):
    """Test dynamic generation of nodes and edges without hardcoding."""
    graph = behavioral_graph_service.get_connection_map(state)

    assert graph["title"] == "Behavioral Connection Map"
    assert graph["corpus_incident_count"] == 220663
    assert graph["total_nodes"] > 10
    assert graph["total_edges"] > 20

    nodes = graph["nodes"]
    edges = graph["edges"]

    category_nodes = [n for n in nodes if n["type"] == "crime_category"]
    pattern_nodes = [n for n in nodes if n["type"] == "behavioral_pattern"]

    # There should be 8 behavioral patterns and at least 6 crime categories
    assert len(pattern_nodes) == 8
    assert len(category_nodes) >= 6

    # Verify node structure
    for node in nodes:
        assert node["id"]
        assert node["label"]
        assert node["title"]
        assert node["type"] in ("crime_category", "behavioral_pattern")
        assert node["incident_count"] > 0
        assert 0.0 <= node["percentage"] <= 100.0
        assert node["color"].startswith("#")

    # Verify edges and shared behavioral DNA
    node_ids = {n["id"] for n in nodes}
    for edge in edges:
        assert edge["id"]
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert edge["incident_count"] > 0
        assert 0.0 <= edge["percentage_of_pattern"] <= 100.0
        assert 0.0 <= edge["percentage_of_category"] <= 100.0
        assert 0.0 <= edge["similarity_score"] <= 100.0
        assert edge["strength_label"]

        # Verify Shared Behavioral DNA fields
        shared = edge["shared_behavioral_dna"]
        assert "time" in shared and len(shared["time"]) > 5
        assert "location" in shared and len(shared["location"]) > 5
        assert "property" in shared and len(shared["property"]) > 5
        assert "weapon" in shared and len(shared["weapon"]) > 5
        assert "context_harm" in shared and len(shared["context_harm"]) > 5
        assert len(shared["key_shared_traits"]) >= 1
        assert "why_connected" in shared and len(shared["why_connected"]) > 20


def test_ethical_and_non_offender_constraints(client):
    """Ensure the connection map explicitly forbids offender and criminal network attribution."""
    graph = behavioral_graph_service.get_connection_map(state)
    advisory = graph["ethical_advisory"].lower()

    # Must explicitly state it does NOT represent people/suspects/offenders/networks
    assert "not represent people" in advisory
    assert "offenders" in advisory
    assert "criminal networks" in advisory


def test_connection_map_api_endpoint(client):
    """Test FastAPI GET /api/patterns/connection-map endpoint."""
    res = client.get("/api/patterns/connection-map")
    assert res.status_code == 200
    data = res.json()

    assert data["title"] == "Behavioral Connection Map"
    assert data["total_nodes"] == len(data["nodes"])
    assert data["total_edges"] == len(data["edges"])
    assert len(data["nodes"]) >= 14
    assert len(data["edges"]) >= 25

    # Test cross-crime alias endpoint
    res_cc = client.get("/api/cross-crime/connection-map")
    assert res_cc.status_code == 200
    assert res_cc.json()["total_nodes"] == data["total_nodes"]


def test_connection_map_filtering(client):
    """Test filtering connection map by pattern or category."""
    # Filter by pattern
    filtered_pattern = behavioral_graph_service.get_connection_map(state, filter_pattern_id="PATTERN 04")
    edges_p4 = filtered_pattern["edges"]
    assert len(edges_p4) > 0
    for e in edges_p4:
        assert e["target_label"] == "PATTERN 04"

    # Filter by category
    filtered_cat = behavioral_graph_service.get_connection_map(state, filter_category="Property")
    edges_prop = filtered_cat["edges"]
    assert len(edges_prop) > 0
    for e in edges_prop:
        assert e["source_label"] == "Property"
