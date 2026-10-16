"""
CRIME DNA — Central Behavioral Intelligence Analysis Engine Pipeline Tests

Validates that:
1. The CrimeDnaAnalysisEngine executes the complete end-to-end flow:
   User Incident → Behavioral DNA → Similarity → Clustering → Cross-Crime → Evolution → Novelty → Explainability → Unified Result.
2. The response contains all required structured sections:
   - incident_summary
   - behavioral_dna
   - dna_similarity
   - similar_historical_incidents
   - cross_crime_matches
   - hidden_behavioral_patterns
   - why_similar
   - behavioral_evolution
   - novelty
   - technical_metadata
3. All scores are computed dynamically from real models (never hardcoded 91%, 88%, 84%).
4. Different incident inputs yield distinct behavioral profiles, clusters, and matches.
5. No models are retrained during analysis requests (weights/centroids remain immutable).
6. The FastAPI endpoint /api/analyze/input correctly wraps the engine.
"""

import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.services.analysis_engine import CrimeDnaAnalysisEngine, analysis_engine
from src.api.state import state
from src.api.main import app


@pytest.fixture(scope="module", autouse=True)
def ensure_state_ready():
    """Ensure in-memory ML model registry is fully loaded."""
    if not state.is_ready:
        state.load_all()


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_violent_incident():
    """Sample armed commercial robbery payload."""
    return {
        "scenario_title": "Armed Commercial Robbery at Convenience Store",
        "incident_date": "2024-07-12",
        "incident_time": "22:45",
        "crime_category": "person_property",
        "is_attempted": False,
        "offense_count": 2,
        "population_setting": "mid_sized_city",
        "has_weapon": True,
        "weapon_count": 2,
        "victim_count": 2,
        "victim_avg_age": 32.0,
        "offender_count": 2,
        "offender_avg_age": 24.0,
        "has_property": True,
        "property_value": 4200.0,
        "has_injury": True,
        "has_arrest": False
    }


@pytest.fixture
def sample_property_incident():
    """Sample nocturnal residential burglary payload."""
    return {
        "scenario_title": "Daytime Bicycle Theft at Public Park",
        "incident_date": "2024-04-18",
        "incident_time": "14:15",
        "crime_category": "property",
        "is_attempted": False,
        "offense_count": 1,
        "population_setting": "small_city",
        "has_weapon": False,
        "weapon_count": 0,
        "victim_count": 1,
        "victim_avg_age": 45.0,
        "offender_count": 1,
        "has_property": True,
        "property_value": 750.0,
        "has_injury": False,
        "has_arrest": True
    }


def test_complete_analysis_pipeline_structure(sample_violent_incident):
    """Verifies that CrimeDnaAnalysisEngine returns all 10 required structured analytical sections."""
    result = analysis_engine.analyze(sample_violent_incident)

    # 1. Incident Summary
    assert "incident_summary" in result
    summary = result["incident_summary"]
    assert summary["scenario_title"] == "Armed Commercial Robbery at Convenience Store"
    assert summary["force_and_weapons"]["has_weapon"] is True
    assert summary["force_and_weapons"]["weapon_count"] == 2
    assert summary["demographics"]["victim_count"] == 2
    assert summary["economic_impact"]["property_value_usd"] == 4200.0

    # 2. Behavioral DNA
    assert "behavioral_dna" in result
    dna = result["behavioral_dna"]
    assert dna["vector_dimension"] == 70
    assert len(dna["subprofile_energies"]) == 7
    assert "human_readable" in dna
    assert "machine_readable" in dna
    assert dna["machine_readable"]["l2_norm"] == pytest.approx(1.0, abs=1e-4)

    # 3. DNA Similarity
    assert "dna_similarity" in result
    similarity = result["dna_similarity"]
    assert "top_match_similarity_pct" in similarity
    assert 0.0 <= similarity["top_match_similarity_pct"] <= 100.0
    assert similarity["k_neighbors_searched"] == 5
    assert similarity["top_matched_incident_id"] is not None

    # 4. Similar Historical Incidents
    assert "similar_historical_incidents" in result
    matches = result["similar_historical_incidents"]
    assert len(matches) == 5
    for rank, match in enumerate(matches, start=1):
        assert match["rank"] == rank
        assert match["incident_id"].startswith("INC_")
        assert 0.0 <= match["similarity_score_pct"] <= 100.0
        # Cosine distance and similarity percentage must strictly correspond: sim = (1 - dist) * 100
        expected_sim = round(max(0.0, min(100.0, (1.0 - match["cosine_distance"]) * 100.0)), 2)
        assert match["similarity_score_pct"] == pytest.approx(expected_sim, abs=0.05)

    # 5. Cross-Crime Matches
    assert "cross_crime_matches" in result
    cc = result["cross_crime_matches"]
    assert "dominant_cross_crime_pattern" in cc
    assert cc["dominant_cross_crime_pattern"].startswith("CCP_")
    assert "cross_crime_pattern_name" in cc
    assert "represented_categories" in cc
    assert "behavioral_synergy" in cc

    # 6. Hidden Behavioral Patterns (Cluster Archetype)
    assert "hidden_behavioral_patterns" in result
    cluster = result["hidden_behavioral_patterns"]
    assert 0 <= cluster["cluster_id"] < 8
    assert cluster["cluster_name"] != ""
    assert isinstance(cluster["macro_category"], str) and len(cluster["macro_category"]) > 0
    assert cluster["distance_to_centroid"] >= 0.0

    # 7. Why Similar (Explainability Attribution)
    assert "why_similar" in result
    why = result["why_similar"]
    assert why["target_incident_id"] == matches[0]["incident_id"]
    assert why["overall_similarity_pct"] == matches[0]["similarity_score_pct"]
    assert len(why["group_attributions"]) > 0
    assert len(why["top_matching_features"]) > 0
    # Group percentage shares should sum close to 100%
    total_group_share = sum(g["share_percentage"] for g in why["group_attributions"])
    assert total_group_share == pytest.approx(100.0, abs=1.5)

    # 8. Behavioral Evolution
    assert "behavioral_evolution" in result
    evo = result["behavioral_evolution"]
    assert evo["calendar_month"] == 7
    assert evo["hour_of_day"] == 22
    assert "Summer" in evo["calendar_quarter"]
    assert len(evo["aligned_shifts"]) > 0  # Should match Summer Nocturnal Surge

    # 9. Novelty Assessment
    assert "novelty" in result
    nov = result["novelty"]
    assert 0.0 <= nov["novelty_score"] <= 2.0
    assert nov["novelty_tier"] in [
        "Standard Behavioral Pattern",
        "Moderate Behavioral Novelty",
        "High Behavioral Outlier",
        "Extreme Behavioral Outlier"
    ]
    assert nov["distance_to_nearest_cluster"] >= 0.0

    # 10. Technical Metadata
    assert "technical_metadata" in result
    meta = result["technical_metadata"]
    assert meta["engine_version"] == "2.0.0"
    assert meta["vector_dimension"] == 70
    assert meta["historical_index_size"] == len(state.incident_ids)
    assert meta["historical_index_size"] > 0


def test_real_model_results_not_hardcoded(sample_violent_incident, sample_property_incident):
    """Verifies that scores are derived from real models and differ across distinct incident profiles."""
    res1 = analysis_engine.analyze(sample_violent_incident)
    res2 = analysis_engine.analyze(sample_property_incident)

    # Similarity scores must not be identical hardcoded constants
    sim1 = res1["dna_similarity"]["top_match_similarity_pct"]
    sim2 = res2["dna_similarity"]["top_match_similarity_pct"]
    assert sim1 != sim2

    # Matched incidents must differ
    match_id_1 = res1["similar_historical_incidents"][0]["incident_id"]
    match_id_2 = res2["similar_historical_incidents"][0]["incident_id"]
    assert match_id_1 != match_id_2

    # Cluster archetypes should reflect distinct behaviors (Armed Robbery vs Daytime Theft)
    cl_id_1 = res1["hidden_behavioral_patterns"]["cluster_id"]
    cl_id_2 = res2["hidden_behavioral_patterns"]["cluster_id"]
    # Even if they mapped to same cluster, distance to centroid would differ
    assert (cl_id_1 != cl_id_2) or (
        res1["hidden_behavioral_patterns"]["distance_to_centroid"] !=
        res2["hidden_behavioral_patterns"]["distance_to_centroid"]
    )

    # Novelty scores must be dynamic floating points, not canned constants
    assert res1["novelty"]["novelty_score"] != res2["novelty"]["novelty_score"]


def test_models_are_not_retrained_per_request(sample_violent_incident):
    """Confirms that model states remain strictly immutable during analysis requests."""
    assert state.clusterer is not None
    assert state.clusterer.model is not None

    centroids_before = np.copy(state.clusterer.model.cluster_centers_)
    index_size_before = len(state.incident_ids)

    # Execute multiple analysis calls
    _ = analysis_engine.analyze(sample_violent_incident)
    _ = analysis_engine.analyze(sample_violent_incident)

    centroids_after = state.clusterer.model.cluster_centers_
    index_size_after = len(state.incident_ids)

    # Weights and index size must be identical bit-for-bit
    np.testing.assert_array_equal(centroids_before, centroids_after)
    assert index_size_before == index_size_after


def test_api_endpoint_integration(client: TestClient, sample_violent_incident):
    """Validates that POST /api/analyze/input returns HTTP 200 with complete response."""
    response = client.post("/api/analyze/input", json=sample_violent_incident)
    assert response.status_code == 200
    data = response.json()

    # Check that canonical keys and legacy keys are present
    assert "incident_summary" in data
    assert "behavioral_dna" in data
    assert "dna_similarity" in data
    assert "similar_historical_incidents" in data
    assert "cross_crime_matches" in data
    assert "hidden_behavioral_patterns" in data
    assert "why_similar" in data
    assert "behavioral_evolution" in data
    assert "novelty" in data
    assert "technical_metadata" in data

    # Check backwards-compatible frontend keys
    assert "cluster_assignment" in data
    assert "cross_crime_mapping" in data
    assert "novelty_assessment" in data
    assert "why_similar_explanation" in data
    assert "evolutionary_context" in data
    assert "dna_comparison" in data
    assert "ethical_advisory" in data
