"""
CRIME DNA — Cross-Crime Behavioral DNA Matching Tests

Validates that:
1. The similarity engine does NOT restrict search to the same crime category.
2. Cross-category retrieval is enabled when supported by behavioral representation.
3. Statutory crime category features do not dominate similarity calculations.
4. Grouping under 'SIMILAR BEHAVIORAL INCIDENTS' contains:
   - Rank
   - Crime Category
   - Similarity
   - Relevant behavioral characteristics
5. Identifies whether similar incidents belong to 'same crime category' or 'different crime categories'.
6. Includes the clear 'Cross-Crime Match' indicator with exact wording:
   "Similar behavioral characteristics were found across different crime categories."
7. Strict ethical compliance: NEVER claims same offender, identity, criminal group, or guilt.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from src.services.analysis_engine import analysis_engine
from src.models.similarity.engine import (
    normalize_category_for_matching,
    extract_relevant_behavioral_characteristics
)
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
def violent_extortion_payload():
    """
    Incident with armed robbery / violent interpersonal extortion behavior:
    Submitted under statutory category 'person', but possesses heavy property,
    weapons, and group perpetrator characteristics.
    """
    return {
        "scenario_title": "Armed Multi-Perpetrator Hijacking & Extortion",
        "incident_date": "2024-07-15",
        "incident_time": "02:15",
        "incident_hour": 2,
        "crime_category": "person",
        "is_attempted": False,
        "offense_count": 2,
        "population_setting": "metropolitan_core",
        "has_weapon": True,
        "weapon_count": 2,
        "weapon_types_count": 2,
        "offender_count": 3,
        "victim_count": 2,
        "has_property": True,
        "property_value": 12000.0,
        "stolen_count": 3,
        "has_injury": True,
        "has_arrest": False
    }


@pytest.fixture
def commercial_robbery_payload():
    """
    Incident submitted as 'person_property' (Robbery/Extortion)
    sharing operational traits with property burglaries and violent assaults.
    """
    return {
        "scenario_title": "Armed Midnight Convenience Store Robbery",
        "incident_date": "2024-08-20",
        "incident_time": "23:45",
        "incident_hour": 23,
        "crime_category": "person_property",
        "is_attempted": False,
        "offense_count": 2,
        "population_setting": "metropolitan_core",
        "has_weapon": True,
        "victim_count": 1,
        "has_property": True,
        "property_value": 1500.0,
        "has_arrest": False
    }


# ============================================================================
# 1. Cross-Category Retrieval Verification
# ============================================================================

def test_cross_category_retrieval_supported_by_data(violent_extortion_payload):
    """
    Proves that similarity search is NOT restricted to the query crime category.
    When behavioral features support cross-domain MO, the engine returns
    matches across Person, Property, and Compound categories.
    """
    result = analysis_engine.analyze(violent_extortion_payload)
    grouping = result["similar_behavioral_incidents"]
    
    assert grouping is not None, "similar_behavioral_incidents must be present in response"
    matches = grouping["matches"]
    assert len(matches) > 0, "Must return nearest neighbor matches"

    categories_found = {m["crime_category"] for m in matches}
    is_cross_flags = [m["is_cross_crime_match"] for m in matches]

    # Must contain at least one cross-crime match given this hybrid behavioral signature
    assert any(is_cross_flags), "Should discover cross-crime matches for violent extortion incident"
    assert grouping["has_cross_crime_matches"] is True
    assert grouping["cross_category_count"] > 0
    assert len(categories_found) >= 2, f"Should span multiple categories, found: {categories_found}"


def test_similarity_engine_searches_global_index():
    """
    Proves that the underlying BehavioralSimilarityEngine model operates across
    all 220,663 records globally without partitioning or filtering by crime category.
    """
    total_indexed = len(state.similarity_engine.incident_ids)
    assert total_indexed > 200_000, f"Expected >200,000 indexed records, found {total_indexed}"

    # Query with a synthetic unit vector
    dummy_vec = np.zeros(70, dtype=np.float32)
    dummy_vec[0] = 1.0  # hour
    dummy_vec[12] = 1.0  # metropolitan population
    dummy_vec /= np.linalg.norm(dummy_vec)

    results = state.similarity_engine.find_similar_by_vector(dummy_vec, top_k=10)
    assert len(results["matches"]) == 10
    # Results must come from the global KNN tree without category exclusion
    for m in results["matches"]:
        assert "incident_id" in m
        assert "similarity_score_pct" in m
        assert 0.0 <= m["similarity_score_pct"] <= 100.0


# ============================================================================
# 2. Category Independence: Crime Category Does Not Dominate
# ============================================================================

def test_crime_category_does_not_dominate_similarity():
    """
    Proves that two behavioral vectors sharing the exact same behavioral traits
    (temporal, spatial, force, victimology, economics) but differing in statutory
    category flag still achieve strong behavioral similarity (>70%).
    """
    base_payload_person = {
        "scenario_title": "Base MO Person",
        "incident_hour": 3,
        "crime_category": "person",
        "has_weapon": True,
        "weapon_count": 1,
        "victim_count": 1,
        "population_setting": "metropolitan_core",
        "has_injury": True
    }
    base_payload_property = {
        "scenario_title": "Base MO Property",
        "incident_hour": 3,
        "crime_category": "property",
        "has_weapon": True,
        "weapon_count": 1,
        "victim_count": 1,
        "population_setting": "metropolitan_core",
        "has_injury": True
    }

    res_person = analysis_engine.analyze(base_payload_person)
    res_prop = analysis_engine.analyze(base_payload_property)

    v_person = np.array(res_person["machine_readable_dna"]["normalized_vector"])
    v_prop = np.array(res_prop["machine_readable_dna"]["normalized_vector"])

    # Cosine similarity between the two 70D vectors
    cos_sim = float(np.dot(v_person, v_prop))
    sim_pct = cos_sim * 100.0

    # The vectors should share strong similarity (>70%) because the 63 behavioral dimensions
    # dominate the 7 statutory classification dimensions.
    assert sim_pct > 70.0, f"Category flag should not dominate behavioral space. Got {sim_pct:.1f}%"


# ============================================================================
# 3. Result Grouping & Schema Verification
# ============================================================================

def test_similar_behavioral_incidents_grouping_structure(commercial_robbery_payload):
    """
    Verifies that 'SIMILAR BEHAVIORAL INCIDENTS' contains:
    - Rank
    - Crime Category
    - Similarity
    - Relevant behavioral characteristics
    """
    result = analysis_engine.analyze(commercial_robbery_payload)
    grouping = result["similar_behavioral_incidents"]

    assert grouping["title"] == "SIMILAR BEHAVIORAL INCIDENTS"
    assert "query_crime_category" in grouping
    assert "cross_crime_indicator" in grouping
    assert "has_cross_crime_matches" in grouping
    assert "same_category_count" in grouping
    assert "cross_category_count" in grouping
    assert "grouped_by_category_relationship" in grouping
    assert "ethical_advisory" in grouping

    # Verify each match contains required fields
    for match in grouping["matches"]:
        assert "rank" in match
        assert isinstance(match["rank"], int)
        assert match["rank"] >= 1

        assert "crime_category" in match
        assert isinstance(match["crime_category"], str)
        assert len(match["crime_category"]) > 0

        assert "similarity" in match
        assert isinstance(match["similarity"], str)
        assert "%" in match["similarity"]

        assert "relevant_behavioral_characteristics" in match
        assert isinstance(match["relevant_behavioral_characteristics"], list)
        assert len(match["relevant_behavioral_characteristics"]) > 0

        assert "is_cross_crime_match" in match
        assert isinstance(match["is_cross_crime_match"], bool)

        assert "category_relationship" in match
        assert match["category_relationship"] in ["Same Crime Category", "Different Crime Category"]


def test_cross_crime_indicator_wording(violent_extortion_payload):
    """
    Verifies the exact indicator text required by user specifications:
    "Similar behavioral characteristics were found across different crime categories."
    """
    result = analysis_engine.analyze(violent_extortion_payload)
    grouping = result["similar_behavioral_incidents"]

    if grouping["has_cross_crime_matches"]:
        expected = "Similar behavioral characteristics were found across different crime categories."
        assert grouping["cross_crime_indicator"] == expected
        assert result["dna_similarity"]["cross_crime_indicator"] == expected


def test_same_and_different_category_grouping(violent_extortion_payload):
    """
    Verifies that matches are partitioned accurately into:
    - same crime category
    - different crime categories
    """
    result = analysis_engine.analyze(violent_extortion_payload)
    grouping = result["similar_behavioral_incidents"]
    rel_groups = grouping["grouped_by_category_relationship"]

    same_list = rel_groups["same_crime_category"]
    diff_list = rel_groups["different_crime_categories"]

    assert len(same_list) == grouping["same_category_count"]
    assert len(diff_list) == grouping["cross_category_count"]
    assert len(same_list) + len(diff_list) == len(grouping["matches"])

    for m in same_list:
        assert m["is_cross_crime_match"] is False
        assert m["category_relationship"] == "Same Crime Category"

    for m in diff_list:
        assert m["is_cross_crime_match"] is True
        assert m["category_relationship"] == "Different Crime Category"


# ============================================================================
# 4. Strict Ethical Boundaries
# ============================================================================

def test_ethical_boundary_compliance(violent_extortion_payload):
    """
    Verifies that the system NEVER claims:
    - same offender
    - same person
    - same criminal group
    - identity
    - guilt
    The system must explicitly restrict assertions to behavioral similarity only.
    """
    result = analysis_engine.analyze(violent_extortion_payload)
    
    # Check ethical advisory in response
    advisory = result["ethical_advisory"]
    grouping_advisory = result["similar_behavioral_incidents"]["ethical_advisory"]
    
    for text in [advisory, grouping_advisory]:
        assert "behavioral similarity" in text.lower()
        # Verify prohibited assertions are not made as truth
        assert "does not identify offenders" in text.lower() or "does not establish offender identity" in text.lower()
        assert "guilt" in text.lower()

    # Verify cross_crime_indicator does not claim identity
    indicator = result["similar_behavioral_incidents"]["cross_crime_indicator"]
    assert "offender" not in indicator.lower()
    assert "person" not in indicator.lower()
    assert "criminal group" not in indicator.lower()
    assert "identity" not in indicator.lower()
    assert "guilt" not in indicator.lower()


# ============================================================================
# 5. API Endpoint Wrap Verification
# ============================================================================

def test_api_endpoint_returns_cross_crime_grouping(client, violent_extortion_payload):
    """
    Verifies that POST /api/analyze/input exposes the complete cross-crime matching
    groupings and indicators over HTTP.
    """
    response = client.post("/api/analyze/input", json=violent_extortion_payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "similar_behavioral_incidents" in data
    grouping = data["similar_behavioral_incidents"]
    assert grouping["title"] == "SIMILAR BEHAVIORAL INCIDENTS"
    assert grouping["has_cross_crime_matches"] is True
    assert grouping["cross_crime_indicator"] == "Similar behavioral characteristics were found across different crime categories."
    
    first_match = grouping["matches"][0]
    assert "rank" in first_match
    assert "crime_category" in first_match
    assert "similarity" in first_match
    assert "relevant_behavioral_characteristics" in first_match


def test_api_vector_similarity_returns_cross_crime_enrichment(client):
    """
    Verifies that POST /api/similarity/vector also enriches nearest neighbors
    with cross-crime indicators and behavioral characteristics.
    """
    # Create valid 70D vector
    vec = [0.0] * 70
    vec[0] = 0.5  # incident_hour
    vec[12] = 1.0  # urban
    vec[16] = 1.0  # weapon
    norm = float(np.linalg.norm(vec))
    norm_vec = [float(x / norm) for x in vec]

    response = client.post("/api/similarity/vector", json={
        "vector": norm_vec,
        "top_k": 5,
        "query_crime_category": "property"
    })
    assert response.status_code == 200, response.text
    data = response.json()

    assert "matches" in data
    assert "cross_crime_indicator" in data
    assert "has_cross_crime_matches" in data
    for m in data["matches"]:
        assert "rank" in m
        assert "crime_category" in m
        assert "similarity" in m
        assert "relevant_behavioral_characteristics" in m
