"""
CRIME DNA — "WHY SIMILAR?" User-Facing Behavioral Explanation System Tests

Validates that:
1. The system does NOT simply return "Similarity = 91%".
2. It explains WHY the incident or crime category is behaviorally similar.
3. Explanations use actual feature contributions from exact additive inner-product decomposition.
4. Explanations are organized into understandable behavioral groups:
   - Time
   - Location
   - Crime Context
   - Method / Weapon
   - Property
   - People / Victim-Offender Context
   - Activity & Context
5. No invented feature importance values or fake percentages are used.
6. Transparent alternative tiers are provided: "Strong match", "Moderate match", "Weak match".
7. Group status indicators include checkmarks (✓) and divergence markers (△):
   - ✓ Same time pattern
   - ✓ Similar location context
   - ✓ Similar property context
   - △ Different weapon context
8. Plain-English explanation is dynamically generated from actual analysis:
   "The strongest behavioral similarities are the time pattern, location context, and property involvement."
9. API endpoints (/api/analyze/input and /api/explain/{id1}/{id2}) expose the complete system.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from src.services.analysis_engine import analysis_engine
from src.models.explainability.explainer import (
    decompose_behavioral_similarity,
    synthesize_plain_english_explanation
)
from src.features.config import FEATURE_GROUPS
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
def residential_burglary_payload():
    """Nocturnal residential property incident."""
    return {
        "scenario_title": "Midnight Residential Burglary",
        "incident_date": "2024-05-10",
        "incident_time": "02:30",
        "incident_hour": 2,
        "crime_category": "property",
        "has_weapon": False,
        "has_property": True,
        "property_value": 3200.0,
        "victim_count": 1,
        "population_setting": "metropolitan_core"
    }


@pytest.fixture
def armed_street_robbery_payload():
    """Violent armed confrontation with multiple perpetrators."""
    return {
        "scenario_title": "Armed Multi-Subject Street Robbery",
        "incident_date": "2024-06-15",
        "incident_time": "23:15",
        "incident_hour": 23,
        "crime_category": "person_property",
        "has_weapon": True,
        "weapon_count": 2,
        "victim_count": 2,
        "offender_count": 3,
        "has_property": True,
        "property_value": 1500.0,
        "has_injury": True,
        "population_setting": "metropolitan_core"
    }


# ============================================================================
# 1. System Explains WHY (Not Simply "Similarity = 91%")
# ============================================================================

def test_why_similar_not_just_single_number(residential_burglary_payload):
    """
    Verifies that the engine returns comprehensive, multi-dimensional
    explanations of similarity rather than just a single numeric score.
    """
    result = analysis_engine.analyze(residential_burglary_payload)
    why = result["why_similar_explanation"]

    assert why is not None
    assert "target_incident_id" in why
    assert "overall_similarity_pct" in why
    # Must have plain-English sentence
    assert "plain_english_explanation" in why
    assert isinstance(why["plain_english_explanation"], str)
    assert len(why["plain_english_explanation"]) > 20

    # Must have behavioral group comparisons
    assert "behavioral_group_comparisons" in why
    assert isinstance(why["behavioral_group_comparisons"], list)
    assert len(why["behavioral_group_comparisons"]) >= 5

    # Must have top matching features
    assert "top_matching_features" in why
    assert len(why["top_matching_features"]) > 0


# ============================================================================
# 2. Behavioral Groups Organization
# ============================================================================

def test_behavioral_groups_coverage(residential_burglary_payload):
    """
    Verifies that explanations are organized into standard, understandable
    behavioral domains: Time, Location, Crime Context, Method / Weapon,
    Property, People / Victim-Offender Context, Activity & Context.
    """
    result = analysis_engine.analyze(residential_burglary_payload)
    why = result["why_similar_explanation"]
    comparisons = why["behavioral_group_comparisons"]

    group_keys = {c["group_key"] for c in comparisons}
    group_names = {c["group_name"] for c in comparisons}

    # Verify standard domains are covered
    expected_keys = {
        "temporal_dynamics",
        "location_and_environment",
        "property_and_economics",
        "method_and_activity",
        "people_and_demographics",
        "crime_characteristics",
        "context_and_harm"
    }
    assert expected_keys.issubset(group_keys), f"Missing groups: {expected_keys - group_keys}"

    # Verify user-friendly domain names
    assert any("Time" in name for name in group_names)
    assert any("Location" in name for name in group_names)
    assert any("Property" in name for name in group_names)
    assert any("Method" in name or "Weapon" in name for name in group_names)
    assert any("People" in name or "Victim" in name for name in group_names)


# ============================================================================
# 3. Scientific Additive Decomposition & No Fake Values
# ============================================================================

def test_no_invented_feature_importance_or_fake_percentages():
    """
    Verifies that:
    1. Contribution scores are mathematically exact inner products (u_j * v_j).
    2. Sum of group contributions equals overall cosine similarity.
    3. Group share percentages sum to 100%.
    4. Transparent qualitative tiers ("Strong match", "Moderate match", "Weak match")
       are used instead of fabricated importance weights.
    """
    id1 = "INC_136975"
    id2 = "INC_145291"
    u = state.get_incident_dna_vector(id1)
    v = state.get_incident_dna_vector(id2)

    decomp = decompose_behavioral_similarity(u, v, state.feature_names, state.feature_groups)
    total_sim = float(np.dot(u, v))

    comparisons = decomp["behavioral_group_comparisons"]
    sum_contrib = sum(c["contribution_score"] for c in comparisons)

    # 1. Exact additive inner-product efficiency
    assert abs(total_sim - sum_contrib) < 1e-3, f"Sum {sum_contrib} != total {total_sim}"

    # 2. Share percentages sum to ~100%
    sum_shares = sum(c["share_percentage"] for c in comparisons)
    assert abs(100.0 - sum_shares) < 1.0, f"Shares sum {sum_shares} != 100%"

    # 3. Transparent tiers
    valid_tiers = {"Strong match", "Moderate match", "Weak match"}
    for c in comparisons:
        assert c["match_tier"] in valid_tiers
        assert 0.0 <= c["share_percentage"] <= 100.0
        assert -1.0 <= c["similarity_score"] <= 1.0


# ============================================================================
# 4. Checkmarks (✓) and Triangles (△) Status Indicators
# ============================================================================

def test_group_comparison_indicators_and_labels(armed_street_robbery_payload):
    """
    Verifies that each group comparison item contains:
    - status: 'match' or 'divergence'
    - indicator: '✓' or '△'
    - label: e.g. '✓ Same time pattern', '△ Different weapon context'
    """
    result = analysis_engine.analyze(armed_street_robbery_payload)
    why = result["why_similar_explanation"]
    comparisons = why["behavioral_group_comparisons"]

    for comp in comparisons:
        assert comp["status"] in ["match", "divergence"]
        assert comp["indicator"] in ["✓", "△"]
        if comp["status"] == "match":
            assert comp["indicator"] == "✓"
        else:
            assert comp["indicator"] == "△"

        assert comp["label"].startswith("✓") or comp["label"].startswith("△")
        assert len(comp["label"]) > 2


# ============================================================================
# 5. Dynamic Plain-English Explanation Synthesis
# ============================================================================

def test_plain_english_explanation_generated_from_analysis(residential_burglary_payload):
    """
    Verifies the plain-English explanation matches the required format:
    "The strongest behavioral similarities are the time pattern, location context, and property involvement."
    and is dynamically generated from actual matching groups.
    """
    result = analysis_engine.analyze(residential_burglary_payload)
    why = result["why_similar_explanation"]
    sentence = why["plain_english_explanation"]

    assert isinstance(sentence, str)
    assert "behavioral similarities" in sentence or "behavioral similarity" in sentence
    assert "The strongest behavioral similarities are the" in sentence or "The primary behavioral similarity is the" in sentence

    # For residential burglary, time and property and location should be highlighted
    assert "time pattern" in sentence
    assert "property" in sentence or "location" in sentence


def test_plain_english_synthesizer_unit_function():
    """
    Direct unit test of synthesize_plain_english_explanation with mock comparisons.
    """
    mock_comparisons = [
        {
            "group_key": "temporal_dynamics",
            "group_name": "Time",
            "status": "match",
            "contribution_score": 0.35,
            "match_tier": "Strong match"
        },
        {
            "group_key": "location_and_environment",
            "group_name": "Location",
            "status": "match",
            "contribution_score": 0.25,
            "match_tier": "Strong match"
        },
        {
            "group_key": "property_and_economics",
            "group_name": "Property",
            "status": "match",
            "contribution_score": 0.20,
            "match_tier": "Strong match"
        },
        {
            "group_key": "method_and_activity",
            "group_name": "Method / Weapon",
            "status": "divergence",
            "contribution_score": 0.01,
            "match_tier": "Weak match"
        }
    ]

    sentence = synthesize_plain_english_explanation(mock_comparisons)
    expected_start = "The strongest behavioral similarities are the time pattern, location context, and property involvement."
    assert sentence.startswith(expected_start)
    assert "divergence in weapon context" in sentence


# ============================================================================
# 6. Contrastive Divergence Identification
# ============================================================================

def test_contrastive_divergences_identified():
    """
    Verifies that when comparing incidents with contrasting traits (e.g. Armed vs Unarmed),
    the divergent dimension is correctly identified as a Weak match with '△'.
    """
    # Incident A: Armed assault
    u = np.zeros(70, dtype=np.float32)
    u[0] = 1.0  # hour
    u[16] = 1.0  # has_weapon
    u /= np.linalg.norm(u)

    # Incident B: Unarmed burglary (has property, no weapon)
    v = np.zeros(70, dtype=np.float32)
    v[0] = 1.0  # hour
    v[36] = 1.0  # has_property
    v /= np.linalg.norm(v)

    decomp = decompose_behavioral_similarity(u, v, state.feature_names, state.feature_groups)
    comparisons = {c["group_key"]: c for c in decomp["behavioral_group_comparisons"]}

    # Temporal dynamics should match
    assert comparisons["temporal_dynamics"]["status"] == "match"
    assert comparisons["temporal_dynamics"]["indicator"] == "✓"

    # Weapon should be divergent
    assert comparisons["method_and_activity"]["status"] == "divergence"
    assert comparisons["method_and_activity"]["indicator"] == "△"
    assert comparisons["method_and_activity"]["match_tier"] == "Weak match"


# ============================================================================
# 7. API Endpoint Verification
# ============================================================================

def test_api_analyze_input_returns_why_similar(client, residential_burglary_payload):
    """
    Verifies that POST /api/analyze/input returns plain_english_explanation
    and behavioral_group_comparisons over HTTP.
    """
    response = client.post("/api/analyze/input", json=residential_burglary_payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "why_similar_explanation" in data
    why = data["why_similar_explanation"]
    assert "plain_english_explanation" in why
    assert "behavioral_group_comparisons" in why
    assert len(why["behavioral_group_comparisons"]) > 0

    first_group = why["behavioral_group_comparisons"][0]
    assert "indicator" in first_group
    assert "match_tier" in first_group
    assert "share_percentage" in first_group


def test_api_explain_endpoint_returns_why_similar(client):
    """
    Verifies that GET /api/explain/{id1}/{id2} returns plain_english_explanation
    and behavioral_group_comparisons over HTTP.
    """
    response = client.get("/api/explain/INC_136975/INC_145291")
    assert response.status_code == 200, response.text
    data = response.json()

    assert "plain_english_explanation" in data
    assert data["plain_english_explanation"] is not None
    assert "behavioral_group_comparisons" in data
    assert len(data["behavioral_group_comparisons"]) > 0
    assert any(c["indicator"] == "✓" for c in data["behavioral_group_comparisons"])
