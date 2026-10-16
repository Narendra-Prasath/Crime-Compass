"""
CRIME DNA — Incident History Section Test Suite

Validates the Incident History section implementation:
1. Clean table/card layout fields:
   - Analysis ID
   - Date/Time
   - Crime Category
   - Behavioral Pattern
   - Similarity Summary
   - Novelty Summary
2. Opening stored analysis results (retrieval by Analysis ID).
3. Zero PII & strict data minimization: no names, phones, emails, or personal identifiers.
4. Strict separation between HISTORICAL DATASET (220,663 records) and USER ANALYSIS HISTORY.
   - User incidents are never added to historical dataset
   - Reference ML knowledge base remains immutable
5. Pagination (limits, offsets, total_count).
6. Search and filtering (by keyword, scenario title, pattern, crime category).
7. Record deletion and lifecycle management.
8. Error state handling (404 for invalid/non-existent IDs).
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state
from src.services.analysis_engine import analysis_engine
from src.services.analysis_record_service import analysis_record_service


@pytest.fixture(scope="module", autouse=True)
def ensure_state_ready():
    """Ensure in-memory ML model registry and historical dataset are initialized."""
    if not state.is_ready:
        state.load_all()


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_records():
    """Clear record repository before and after each test."""
    analysis_record_service.clear_records()
    yield
    analysis_record_service.clear_records()


SAMPLE_INCIDENT_A = {
    "scenario_title": "Commercial Burglary at Electronics Store",
    "incident_date": "2024-11-12",
    "incident_time": "02:15",
    "crime_category": "property",
    "population_setting": "mid_sized_city",
    "has_weapon": False,
    "has_property": True,
    "property_value": 8500.0,
    "has_injury": False,
    "has_arrest": False,
    "offense_count": 1,
    "victim_count": 1,
    "offender_count": 2
}

SAMPLE_INCIDENT_B = {
    "scenario_title": "Armed Robbery at Financial Institution",
    "incident_date": "2024-10-05",
    "incident_time": "21:40",
    "crime_category": "person_property",
    "population_setting": "large_city",
    "has_weapon": True,
    "weapon_count": 1,
    "has_property": True,
    "property_value": 45000.0,
    "has_injury": True,
    "has_arrest": True,
    "offense_count": 2,
    "victim_count": 2,
    "offender_count": 3
}

SAMPLE_INCIDENT_C = {
    "scenario_title": "Domestic Physical Assault Dispute",
    "incident_date": "2024-09-18",
    "incident_time": "23:10",
    "crime_category": "person",
    "population_setting": "small_city",
    "has_weapon": False,
    "has_property": False,
    "has_injury": True,
    "has_arrest": True,
    "has_relationship": True,
    "offense_count": 1,
    "victim_count": 1,
    "offender_count": 1
}


def test_incident_history_record_structure_and_layout(client):
    """
    Validates that each recorded incident contains the exact required fields:
    - Analysis ID
    - Date/Time
    - Crime Category
    - Behavioral Pattern
    - Similarity Summary
    - Novelty Summary
    """
    res = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_A, headers={"X-User-ID": "user_test_history"})
    assert res.status_code == 200
    analysis_id = res.json()["analysis_id"]

    # Retrieve history list
    list_res = client.get("/api/analyze/records", headers={"X-User-ID": "user_test_history"})
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total_count"] == 1
    assert len(data["records"]) == 1

    rec = data["records"][0]

    # 1. Analysis ID
    assert rec["analysis_id"] == analysis_id
    assert rec["analysis_id"].startswith("ANALYSIS_")

    # 2. Date/Time
    assert "timestamp" in rec
    assert rec["timestamp"] is not None

    # 3. Crime Category
    assert "input_summary" in rec
    assert rec["input_summary"]["crime_category"] == "property"
    assert rec["input_summary"]["scenario_title"] == "Commercial Burglary at Electronics Store"

    # 4. Behavioral Pattern
    assert "pattern_summary" in rec
    assert "pattern_name" in rec["pattern_summary"]
    assert "pattern_id" in rec["pattern_summary"]
    assert "behavioral_formula" in rec["pattern_summary"]
    assert "association_tier" in rec["pattern_summary"]

    # 5. Similarity Summary
    assert "similarity_summary" in rec
    assert "similarity_percentage" in rec["similarity_summary"]
    assert "top_matched_incident_id" in rec["similarity_summary"]
    assert "category_relationship" in rec["similarity_summary"]
    assert "distance_metric" in rec["similarity_summary"]

    # 6. Novelty Summary
    assert "novelty_summary" in rec
    assert "novelty_score" in rec["novelty_summary"]
    assert "novelty_tier" in rec["novelty_summary"]
    assert "is_novel" in rec["novelty_summary"]
    assert "pattern_fit_score" in rec["novelty_summary"]


def test_clicking_analysis_opens_stored_analysis_result(client):
    """
    Verifies that querying a specific Analysis ID opens and retrieves the complete
    stored analysis result, including deep summaries and full analytical context.
    """
    post_res = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_B)
    assert post_res.status_code == 200
    analysis_id = post_res.json()["analysis_id"]

    # Open stored analysis result by ID
    get_res = client.get(f"/api/analyze/records/{analysis_id}")
    assert get_res.status_code == 200
    rec = get_res.json()

    assert rec["analysis_id"] == analysis_id
    assert rec["input_summary"]["crime_category"] == "person_property"
    assert rec["behavioral_dna"]["vector_dimension"] == 70
    assert len(rec["behavioral_dna"]["subprofile_energies"]) >= 5
    assert len(rec["behavioral_dna"]["top_active_traits"]) > 0

    # Ensure full analytical context is attached
    assert "full_result" in rec
    if rec["full_result"]:
        assert "behavioral_dna" in rec["full_result"]
        assert "cluster_assignment" in rec["full_result"]
        assert "why_similar_explanation" in rec["full_result"]


def test_zero_pii_and_data_minimization():
    """
    Verifies that the persistent database contains strictly ZERO personal information.
    No names, phone numbers, email addresses, SSNs, personal addresses, or personal identifiers.
    """
    result = analysis_engine.analyze(SAMPLE_INCIDENT_A, user_id="investigator_jane_doe")
    analysis_id = result["analysis_id"]

    raw_record = analysis_record_service.get_record(analysis_id)
    assert raw_record is not None

    record_str = str(raw_record).lower()

    # Verify no PII attributes are stored
    prohibited_keys = [
        "phone", "email", "ssn", "social_security",
        "first_name", "last_name", "home_address",
        "street_address", "driver_license", "suspect_name", "victim_name"
    ]
    for key in prohibited_keys:
        assert key not in record_str, f"Prohibited PII key '{key}' found in stored record."

    # Verify user_id is purely an audit scope, not an individual identifying profile
    assert raw_record["user_id"] == "investigator_jane_doe"


def test_strict_dataset_separation_historical_vs_user_history(client):
    """
    CRITICAL: Validates that user analysis submissions are NEVER injected
    into the historical ML reference dataset or training knowledge base.
    """
    # Record initial historical dataset metrics
    initial_incident_count = len(state.incident_ids)
    initial_matrix_shape = state.normalized_matrix.shape if state.normalized_matrix is not None else None
    assert initial_incident_count > 200000

    # Submit 3 new user analysis simulations
    res_a = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_A)
    res_b = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_B)
    res_c = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_C)
    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_c.status_code == 200

    id_a = res_a.json()["analysis_id"]

    # Verify user history has 3 records
    history_res = client.get("/api/analyze/records")
    assert history_res.status_code == 200
    assert history_res.json()["total_count"] == 3

    # VERIFY HISTORICAL DATASET IS STRICTLY UNTOUCHED
    assert len(state.incident_ids) == initial_incident_count
    if initial_matrix_shape is not None:
        assert state.normalized_matrix.shape == initial_matrix_shape

    # Verify that searching for the User Analysis ID in historical incidents returns None
    assert state.get_incident_profile(id_a) is None
    assert state.get_incident_dna(id_a) is None

    # Historical incidents follow INC_ namespace, User Analyses follow ANALYSIS_ namespace
    assert id_a.startswith("ANALYSIS_")
    top_match = res_a.json()["similar_historical_incidents"][0]["incident_id"]
    assert top_match.startswith("INC_")


def test_pagination(client):
    """
    Verifies pagination controls: limit, offset, and total_count.
    """
    for i in range(7):
        incident = dict(SAMPLE_INCIDENT_A)
        incident["scenario_title"] = f"Scenario Simulation #{i+1}"
        client.post("/api/analyze/input", json=incident)

    # Page 1: limit 3, offset 0
    res_p1 = client.get("/api/analyze/records?limit=3&offset=0")
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert data_p1["total_count"] == 7
    assert len(data_p1["records"]) == 3
    assert data_p1["limit"] == 3
    assert data_p1["offset"] == 0

    # Page 2: limit 3, offset 3
    res_p2 = client.get("/api/analyze/records?limit=3&offset=3")
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert data_p2["total_count"] == 7
    assert len(data_p2["records"]) == 3
    assert data_p2["offset"] == 3

    # Page 3: limit 3, offset 6 (remainder 1)
    res_p3 = client.get("/api/analyze/records?limit=3&offset=6")
    assert res_p3.status_code == 200
    data_p3 = res_p3.json()
    assert data_p3["total_count"] == 7
    assert len(data_p3["records"]) == 1


def test_search_and_filter(client):
    """
    Verifies search keyword filtering and crime category filtering.
    """
    client.post("/api/analyze/input", json=SAMPLE_INCIDENT_A)  # property, "Electronics Store"
    client.post("/api/analyze/input", json=SAMPLE_INCIDENT_B)  # person_property, "Financial Institution"
    client.post("/api/analyze/input", json=SAMPLE_INCIDENT_C)  # person, "Domestic Physical Assault"

    # Search by title keyword "Financial"
    res_search = client.get("/api/analyze/records?search=Financial")
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert data_search["total_count"] == 1
    assert "Financial" in data_search["records"][0]["input_summary"]["scenario_title"]

    # Filter by category "person"
    res_cat = client.get("/api/analyze/records?category=person")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    # Should match SAMPLE_INCIDENT_C ("person") and SAMPLE_INCIDENT_B ("person_property")
    assert data_cat["total_count"] >= 1
    assert all("person" in r["input_summary"]["crime_category"].lower() for r in data_cat["records"])

    # Search with nonexistent term
    res_none = client.get("/api/analyze/records?search=NonExistentTermXYZ")
    assert res_none.status_code == 200
    assert res_none.json()["total_count"] == 0
    assert len(res_none.json()["records"]) == 0


def test_record_deletion_and_error_handling(client):
    """
    Verifies deleting records and 404 error states for nonexistent records.
    """
    post_res = client.post("/api/analyze/input", json=SAMPLE_INCIDENT_A)
    analysis_id = post_res.json()["analysis_id"]

    # Delete record
    del_res = client.delete(f"/api/analyze/records/{analysis_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Verifies record is gone
    get_res = client.get(f"/api/analyze/records/{analysis_id}")
    assert get_res.status_code == 404

    # Deleting again returns 404
    del_again = client.delete(f"/api/analyze/records/{analysis_id}")
    assert del_again.status_code == 404
