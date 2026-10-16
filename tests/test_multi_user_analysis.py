"""
CRIME DNA — Multi-User & Multi-Incident Analysis Architecture Tests

Tests multi-user / multi-incident analysis handling:
1. Support for User A → Incident A → Analysis A, User B → Incident B → Analysis B, User C → Incident C → Analysis C.
2. Shared historical ML models and indexes across all users (NO retraining per request).
3. Collision-resistant unique Analysis IDs generated for each analysis.
4. Clean analysis record schema containing:
   - Analysis ID
   - Timestamp
   - Input summary
   - Behavioral DNA
   - Similarity summary
   - Pattern summary
   - Novelty summary
   - Ethical advisory
5. Strict data minimization and zero PII persistence.
6. Retrieval of clean records by Analysis ID and user-scoped filtering.
7. Concurrent execution safety and statelessness across independent threads.
8. HTTP REST API endpoints (/api/analyze/input, /api/analyze/records, /api/analyze/records/{id}).
"""

import concurrent.futures
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state
from src.services.analysis_engine import analysis_engine
from src.services.analysis_record_service import analysis_record_service


@pytest.fixture(scope="module", autouse=True)
def ensure_state_ready():
    """Ensure in-memory ML model registry is loaded once."""
    if not state.is_ready:
        state.load_all()


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_records():
    """Clear record repository before each test to guarantee test isolation."""
    analysis_record_service.clear_records()
    yield
    analysis_record_service.clear_records()


# Sample test incidents with distinct behavioral profiles
INCIDENT_A = {
    "scenario_title": "Commercial Burglary at Electronics Warehouse",
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

INCIDENT_B = {
    "scenario_title": "Armed Evening Convenience Store Robbery",
    "incident_date": "2024-10-05",
    "incident_time": "21:40",
    "crime_category": "person_property",
    "population_setting": "large_city",
    "has_weapon": True,
    "weapon_count": 1,
    "has_property": True,
    "property_value": 650.0,
    "has_injury": True,
    "has_arrest": False,
    "offense_count": 2,
    "victim_count": 2,
    "offender_count": 1
}

INCIDENT_C = {
    "scenario_title": "Daytime Park Dispute and Simple Assault",
    "incident_date": "2024-08-19",
    "incident_time": "14:10",
    "crime_category": "person",
    "population_setting": "small_city",
    "has_weapon": False,
    "has_property": False,
    "property_value": 0.0,
    "has_injury": True,
    "has_arrest": True,
    "offense_count": 1,
    "victim_count": 1,
    "offender_count": 1
}


def test_multi_user_independent_analyses():
    """
    CRIME DNA must support:
    User A → Incident A → Analysis A
    User B → Incident B → Analysis B
    User C → Incident C → Analysis C
    """
    # 1. Capture model object references before execution
    sim_model_id_before = id(state.similarity_engine.model)
    cluster_model_id_before = id(state.clusterer.model)
    isolation_forest_id_before = id(state.isolation_forest)

    # 2. Execute analysis for User A
    analysis_a = analysis_engine.analyze(INCIDENT_A, user_id="User_A")
    # 3. Execute analysis for User B
    analysis_b = analysis_engine.analyze(INCIDENT_B, user_id="User_B")
    # 4. Execute analysis for User C
    analysis_c = analysis_engine.analyze(INCIDENT_C, user_id="User_C")

    # Verify each analysis received a distinct, unique Analysis ID
    id_a = analysis_a["analysis_id"]
    id_b = analysis_b["analysis_id"]
    id_c = analysis_c["analysis_id"]

    assert id_a.startswith("ANALYSIS_")
    assert id_b.startswith("ANALYSIS_")
    assert id_c.startswith("ANALYSIS_")

    assert len({id_a, id_b, id_c}) == 3, "All Analysis IDs must be strictly unique"

    # Verify that models were shared and NOT retrained
    assert id(state.similarity_engine.model) == sim_model_id_before
    assert id(state.clusterer.model) == cluster_model_id_before
    assert id(state.isolation_forest) == isolation_forest_id_before

    # Verify each analysis contains independent analytical content
    assert analysis_a["scenario_title"] == "Commercial Burglary at Electronics Warehouse"
    assert analysis_b["scenario_title"] == "Armed Evening Convenience Store Robbery"
    assert analysis_c["scenario_title"] == "Daytime Park Dispute and Simple Assault"

    # Verify user tagging in analysis record
    rec_a = analysis_a["analysis_record"]
    rec_b = analysis_b["analysis_record"]
    rec_c = analysis_c["analysis_record"]

    assert rec_a["user_id"] == "User_A"
    assert rec_b["user_id"] == "User_B"
    assert rec_c["user_id"] == "User_C"


def test_clean_analysis_record_contents():
    """
    Validates that the analysis record contains all required sections without PII.
    """
    res = analysis_engine.analyze(INCIDENT_A, user_id="Analyst_Officer_42")
    rec = res["analysis_record"]

    # Minimum required fields:
    # - Analysis ID
    # - timestamp
    # - input summary
    # - Behavioral DNA
    # - similarity summary
    # - pattern summary
    # - novelty summary
    assert "analysis_id" in rec
    assert "timestamp" in rec
    assert "input_summary" in rec
    assert "behavioral_dna" in rec
    assert "similarity_summary" in rec
    assert "pattern_summary" in rec
    assert "novelty_summary" in rec
    assert "ethical_advisory" in rec

    # Input summary validation (no PII)
    inp = rec["input_summary"]
    assert inp["crime_category"] == "property"
    assert inp["population_setting"] == "mid_sized_city"
    assert inp["behavioral_flags"]["has_weapon"] is False
    assert inp["behavioral_flags"]["has_property"] is True
    # Ensure NO PII fields exist
    for pii_key in ["name", "email", "phone", "ssn", "address", "officer_name"]:
        assert pii_key not in inp

    # Behavioral DNA validation
    dna = rec["behavioral_dna"]
    assert dna["vector_dimension"] == 70
    assert "subprofile_energies" in dna
    assert "top_active_traits" in dna

    # Similarity summary validation
    sim = rec["similarity_summary"]
    assert "top_matched_incident_id" in sim
    assert sim["similarity_percentage"] > 0
    assert "category_relationship" in sim

    # Pattern summary validation
    pat = rec["pattern_summary"]
    assert "pattern_id" in pat
    assert "cluster_id" in pat
    assert "pattern_name" in pat
    assert "behavioral_formula" in pat
    assert pat["supporting_incident_count"] > 0

    # Novelty summary validation
    nov = rec["novelty_summary"]
    assert "novelty_score" in nov
    assert "novelty_tier" in nov
    assert "is_novel" in nov
    assert "pattern_fit_score" in nov


def test_record_persistence_and_scoped_retrieval():
    """
    Tests saving and querying clean analysis records by ID and by user.
    """
    # Create analyses for two different users
    res_1 = analysis_engine.analyze(INCIDENT_A, user_id="User_Alpha")
    res_2 = analysis_engine.analyze(INCIDENT_B, user_id="User_Alpha")
    res_3 = analysis_engine.analyze(INCIDENT_C, user_id="User_Beta")

    id_1 = res_1["analysis_id"]
    id_2 = res_2["analysis_id"]
    id_3 = res_3["analysis_id"]

    # 1. Retrieve by exact ID
    fetched_1 = analysis_record_service.get_record(id_1)
    assert fetched_1 is not None
    assert fetched_1["analysis_id"] == id_1
    assert fetched_1["user_id"] == "User_Alpha"
    assert fetched_1["input_summary"]["crime_category"] == "property"

    # Nonexistent ID returns None
    assert analysis_record_service.get_record("ANALYSIS_NONEXISTENT") is None

    # 2. List records for User_Alpha (should have 2 records)
    list_alpha = analysis_record_service.list_records(user_id="User_Alpha")
    assert list_alpha["total_count"] == 2
    assert len(list_alpha["records"]) == 2
    assert all(r["user_id"] == "User_Alpha" for r in list_alpha["records"])

    # 3. List records for User_Beta (should have 1 record)
    list_beta = analysis_record_service.list_records(user_id="User_Beta")
    assert list_beta["total_count"] == 1
    assert len(list_beta["records"]) == 1
    assert list_beta["records"][0]["analysis_id"] == id_3

    # 4. List all records globally
    list_all = analysis_record_service.list_records()
    assert list_all["total_count"] == 3


def test_concurrent_multi_user_execution():
    """
    Verifies that multiple users submitting incidents concurrently execute safely,
    remain stateless, and do not mutate or collide with shared ML models.
    """
    def run_user_analysis(user_tuple):
        user_name, incident = user_tuple
        return analysis_engine.analyze(incident, user_id=user_name)

    tasks = [
        ("User_1", INCIDENT_A),
        ("User_2", INCIDENT_B),
        ("User_3", INCIDENT_C),
        ("User_4", INCIDENT_A),
        ("User_5", INCIDENT_B)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(run_user_analysis, tasks))

    analysis_ids = [r["analysis_id"] for r in results]
    assert len(set(analysis_ids)) == len(tasks), "Concurrent executions must generate unique Analysis IDs"

    for (user_name, _), result in zip(tasks, results):
        rec = result["analysis_record"]
        assert rec["user_id"] == user_name
        assert rec["analysis_id"] == result["analysis_id"]


def test_api_multi_user_endpoints(client):
    """
    Verifies FastAPI HTTP endpoints for multi-user analysis and record retrieval.
    """
    # 1. Post analysis for User_Desk_1 via request payload
    payload_a = dict(INCIDENT_A)
    payload_a["user_id"] = "User_Desk_1"
    response_a = client.post("/api/analyze/input", json=payload_a)
    assert response_a.status_code == 200
    data_a = response_a.json()
    assert "analysis_id" in data_a
    assert "analysis_record" in data_a
    assert data_a["analysis_record"]["user_id"] == "User_Desk_1"
    id_a = data_a["analysis_id"]

    # 2. Post analysis for User_Desk_2 via X-User-ID header
    response_b = client.post(
        "/api/analyze/input",
        json=INCIDENT_B,
        headers={"X-User-ID": "User_Desk_2"}
    )
    assert response_b.status_code == 200
    data_b = response_b.json()
    assert data_b["analysis_record"]["user_id"] == "User_Desk_2"
    id_b = data_b["analysis_id"]

    assert id_a != id_b

    # 3. Retrieve analysis record by ID
    get_rec = client.get(f"/api/analyze/records/{id_a}")
    assert get_rec.status_code == 200
    rec_json = get_rec.json()
    assert rec_json["analysis_id"] == id_a
    assert rec_json["user_id"] == "User_Desk_1"

    # 4. Filter records by user
    filter_res = client.get("/api/analyze/records?user_id=User_Desk_1")
    assert filter_res.status_code == 200
    filter_data = filter_res.json()
    assert filter_data["total_count"] == 1
    assert filter_data["records"][0]["analysis_id"] == id_a

    # 5. Nonexistent record ID returns 404
    missing_res = client.get("/api/analyze/records/ANALYSIS_NONEXISTENT")
    assert missing_res.status_code == 404
