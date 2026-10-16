"""
CRIME DNA — Canonical Product API Test Suite

Validates that all 11 canonical product endpoints operate cleanly,
strictly validate input, return structured JSON schemas, handle errors properly,
utilize pre-loaded ML models without retraining, and preserve full backward
compatibility for existing API consumers.

Endpoints tested:
1.  GET  /health
2.  GET  /stats
3.  POST /analyze
4.  GET  /analysis/{analysis_id}
5.  GET  /analyses
6.  GET  /patterns
7.  GET  /patterns/{pattern_id}
8.  POST /compare
9.  GET  /evolution/{pattern_id}
10. POST /feedback
11. GET  /connection-map
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="module")
def client():
    """Module-scoped test client running within application lifespan (all ML models preloaded)."""
    with TestClient(app) as c:
        yield c


# ============================================================================
# 1. GET /health
# ============================================================================
def test_canonical_health(client):
    """Validates GET /health returns structured JSON with system readiness."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "api_version" in data
    assert "uptime_seconds" in data
    assert "components_status" in data
    assert data["indexed_incidents"] == 220663
    assert data["vector_dimension"] == 70

    # Verify backward compatible /api/health
    res_api = client.get("/api/health")
    assert res_api.status_code == 200
    assert res_api.json()["indexed_incidents"] == 220663


# ============================================================================
# 2. GET /stats
# ============================================================================
def test_canonical_stats(client):
    """Validates GET /stats returns dataset and model pipeline statistics."""
    res = client.get("/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_incidents"] == 220663
    assert data["behavioral_dna_features_count"] == 70
    assert data["clusters_count"] == 8
    assert "feature_taxonomy_counts" in data

    # Verify backward compatible /api/stats
    res_api = client.get("/api/stats")
    assert res_api.status_code == 200
    assert res_api.json()["total_incidents"] == 220663


# ============================================================================
# 3. POST /analyze
# ============================================================================
SAMPLE_INCIDENT_PAYLOAD = {
    "scenario_title": "Evening Convenience Store Robbery",
    "incident_date": "2024-11-15",
    "incident_time": "21:30",
    "crime_category": "person_property",
    "is_attempted": False,
    "offense_count": 2,
    "offense_categories_count": 2,
    "population_setting": "mid_sized_city",
    "location_count": 1,
    "has_weapon": True,
    "weapon_count": 1,
    "weapon_types_count": 1,
    "has_criminal_activity": True,
    "criminal_activity_count": 1,
    "has_relationship": False,
    "victim_count": 1,
    "victim_avg_age": 35.0,
    "victim_sexes_count": 1,
    "offender_count": 2,
    "offender_avg_age": 24.0,
    "offender_sexes_count": 1,
    "has_property": True,
    "has_stolen_property": True,
    "property_value": 1500.0,
    "is_cargo_theft": False,
    "has_injury": False,
    "injury_record_count": 0,
    "has_drug": False,
    "has_bias_motivation": False,
    "has_arrest": False,
    "arrest_count": 0,
    "user_id": "test_investigator"
}


def test_canonical_post_analyze(client):
    """Validates POST /analyze converts incident input into 70D DNA vector and intelligence layers."""
    res = client.post("/analyze", json=SAMPLE_INCIDENT_PAYLOAD)
    assert res.status_code == 200
    data = res.json()

    # Behavioral DNA vector verification
    assert "behavioral_dna" in data
    dna = data["behavioral_dna"]
    assert dna["vector_dimension"] == 70
    assert len(dna["machine_readable"]["normalized_vector"]) == 70
    assert len(dna["top_active_traits"]) > 0

    # Nearest neighbor similarity
    assert "similar_historical_incidents" in data
    matches = data["similar_historical_incidents"]
    assert len(matches) > 0
    top = matches[0]
    assert 0.0 <= top["similarity_score_pct"] <= 100.0
    assert "incident_id" in top

    # Behavioral Pattern Archetype
    assert "cluster_assignment" in data
    cluster = data["cluster_assignment"]
    assert 0 <= cluster["cluster_id"] <= 7
    assert "archetype_name" in cluster

    # Cross-Crime Matching
    assert "cross_crime_matches" in data or "cross_crime_mapping" in data

    # Behavioral Evolution
    assert "behavioral_evolution" in data

    # Novelty Detection
    assert "novelty" in data or "novelty_assessment" in data

    # Verify backward compatible /api/analyze and /api/analyze/input
    res_alias1 = client.post("/api/analyze", json=SAMPLE_INCIDENT_PAYLOAD)
    assert res_alias1.status_code == 200
    res_alias2 = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_PAYLOAD)
    assert res_alias2.status_code == 200


def test_post_analyze_input_validation(client):
    """Validates POST /analyze rejects invalid payloads with HTTP 422."""
    invalid_payload = {
        "incident_date": "invalid-date",
        "offense_count": -5,
        "weapon_count": -1
    }
    res = client.post("/analyze", json=invalid_payload)
    assert res.status_code == 422


# ============================================================================
# 4. GET /analyses & 5. GET /analysis/{analysis_id}
# ============================================================================
def test_canonical_analyses_and_analysis_detail(client):
    """Validates GET /analyses and GET /analysis/{analysis_id} records pipeline."""
    # Run an analysis to ensure a stored record exists
    analyze_res = client.post("/analyze", json=SAMPLE_INCIDENT_PAYLOAD)
    assert analyze_res.status_code == 200

    # Query analyses list
    list_res = client.get("/analyses?limit=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "records" in list_data
    assert list_data["total_count"] > 0
    records = list_data["records"]
    assert len(records) > 0

    target_record = records[0]
    analysis_id = target_record["analysis_id"]

    # Query single analysis by ID
    detail_res = client.get(f"/analysis/{analysis_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["analysis_id"] == analysis_id
    assert "behavioral_dna" in detail_data
    assert "similarity_summary" in detail_data
    assert "pattern_summary" in detail_data
    assert "novelty_summary" in detail_data

    # Test 404 on nonexistent analysis ID
    nf_res = client.get("/analysis/NONEXISTENT_ANALYSIS_ID_99999")
    assert nf_res.status_code == 404

    # Verify backward compatible /api/analyses and /api/analysis/{id}
    api_list = client.get("/api/analyses")
    assert api_list.status_code == 200
    api_detail = client.get(f"/api/analysis/{analysis_id}")
    assert api_detail.status_code == 200


# ============================================================================
# 6. GET /patterns & 7. GET /patterns/{pattern_id}
# ============================================================================
def test_canonical_patterns_and_pattern_detail(client):
    """Validates GET /patterns and GET /patterns/{pattern_id}."""
    # List all 8 discovered empirical patterns
    patterns_res = client.get("/patterns")
    assert patterns_res.status_code == 200
    data = patterns_res.json()
    assert data["total_patterns"] == 8
    assert len(data["patterns"]) == 8

    # Query pattern detail using index '0'
    p0_res = client.get("/patterns/0")
    assert p0_res.status_code == 200
    p0 = p0_res.json()
    assert p0["cluster_id"] == 0
    assert "pattern_name" in p0
    assert "behavioral_characteristics" in p0
    assert p0["supporting_incident_count"] > 0

    # Query pattern detail using pattern code 'CCP_00'
    pcode_res = client.get("/patterns/CCP_00")
    assert pcode_res.status_code == 200
    assert pcode_res.json()["cluster_id"] == 0

    # Query pattern detail using formatted name 'PATTERN 01'
    pname_res = client.get("/patterns/PATTERN 01")
    assert pname_res.status_code == 200
    assert pname_res.json()["cluster_id"] == 0

    # Test 404 on unknown pattern ID
    nf_res = client.get("/patterns/UNKNOWN_PATTERN_999")
    assert nf_res.status_code == 404

    # Verify backward compatible /api/patterns
    api_patterns = client.get("/api/patterns")
    assert api_patterns.status_code == 200
    assert api_patterns.json()["total_patterns"] == 8


# ============================================================================
# 8. POST /compare
# ============================================================================
def test_canonical_post_compare(client):
    """Validates POST /compare side-by-side DNA comparison and 'What Changed?' explanation."""
    compare_payload = {
        "incident_a": {
            "payload": {
                "scenario_title": "Commercial Burglary",
                "crime_category": "property",
                "incident_date": "2024-04-10",
                "incident_time": "02:30",
                "has_weapon": False,
                "has_injury": False,
                "offender_count": 1,
                "property_value": 4500.0
            }
        },
        "incident_b": {
            "payload": {
                "scenario_title": "Armed Robbery Escalation",
                "crime_category": "person_property",
                "incident_date": "2024-04-11",
                "incident_time": "22:15",
                "has_weapon": True,
                "weapon_count": 1,
                "has_injury": True,
                "offender_count": 2,
                "property_value": 1200.0
            }
        }
    }

    res = client.post("/compare", json=compare_payload)
    assert res.status_code == 200
    data = res.json()
    assert "dna_similarity" in data
    assert "dna_comparison_table" in data
    assert "what_changed" in data
    assert "match_items" in data["what_changed"]
    assert "differ_items" in data["what_changed"]

    # Verify backward compatible /api/compare
    api_res = client.post("/api/compare", json=compare_payload)
    assert api_res.status_code == 200


def test_post_compare_invalid_input(client):
    """Validates POST /compare rejects invalid or empty comparison specs."""
    bad_payload = {
        "incident_a": {},
        "incident_b": {}
    }
    res = client.post("/compare", json=bad_payload)
    assert res.status_code in (400, 422)


# ============================================================================
# 9. GET /evolution/{pattern_id}
# ============================================================================
def test_canonical_evolution_by_pattern_id(client):
    """Validates GET /evolution/{pattern_id} returns chronological 3-stage evolution."""
    res = client.get("/evolution/0")
    assert res.status_code == 200
    data = res.json()
    assert "timeline_stages" in data
    assert len(data["timeline_stages"]) >= 2
    assert "pattern_name" in data
    assert "dataset_time_span" in data

    # Test resolution with pattern label 'PATTERN 02'
    res_p2 = client.get("/evolution/PATTERN 02")
    assert res_p2.status_code == 200
    assert len(res_p2.json()["timeline_stages"]) >= 2

    # Test 404 on invalid pattern ID
    nf_res = client.get("/evolution/INVALID_PATTERN_XYZ")
    assert nf_res.status_code == 404

    # Verify backward compatible /api/evolution/{pattern_id}
    api_res = client.get("/api/evolution/0")
    assert api_res.status_code == 200


# ============================================================================
# 10. POST /feedback
# ============================================================================
def test_canonical_post_feedback(client):
    """Validates POST /feedback records human-in-the-loop investigator evaluation."""
    feedback_payload = {
        "is_useful": True,
        "target_type": "pattern",
        "target_id": "0",
        "useful_aspects": ["temporal_dynamics", "property_involvement"],
        "notes": "Verified match to local commercial burglary pattern cluster."
    }

    res = client.post("/feedback", json=feedback_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "received"
    assert "feedback_id" in data
    assert data["is_useful"] is True

    # Check feedback summary
    summary_res = client.get("/feedback/summary")
    assert summary_res.status_code == 200
    assert summary_res.json()["total_feedback_count"] > 0

    # Verify backward compatible /api/feedback
    api_res = client.post("/api/feedback", json=feedback_payload)
    assert api_res.status_code == 200


# ============================================================================
# 11. GET /connection-map
# ============================================================================
def test_canonical_connection_map(client):
    """Validates GET /connection-map returns graph topology nodes, edges, and counts."""
    res = client.get("/connection-map")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert "total_nodes" in data
    assert "total_edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

    # Test filtering by pattern
    filter_res = client.get("/connection-map?pattern_id=0")
    assert filter_res.status_code == 200
    filter_data = filter_res.json()
    assert len(filter_data["nodes"]) > 0

    # Verify backward compatible /api/connection-map
    api_res = client.get("/api/connection-map")
    assert api_res.status_code == 200
    assert len(api_res.json()["nodes"]) == len(data["nodes"])
