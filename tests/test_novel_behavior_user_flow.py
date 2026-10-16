"""
CRIME DNA — Behavioral Pattern Fit & Novelty Detection Tests

Tests the integration of novelty/anomaly analysis into the user-driven incident flow:
1. Normal cases exhibiting high behavioral pattern fit and standard novelty.
2. Novel cases exhibiting unusual behavioral combinations, triggering the warning banner:
   "⚠️ NOVEL BEHAVIORAL PATTERN"
   "This incident contains a behavioral combination that does not closely match the major patterns learned from the historical dataset."
3. Extraction of most unusual supported behavioral factors with human-readable labels.
4. Grounding in scientifically calibrated Phase 9 thresholds (0.4363, 0.5985, 0.7383).
5. Strict adherence to ethical guidelines (no offender characterization or predictive claims).
6. End-to-end FastAPI HTTP serialization on POST /api/analyze/input.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state
from src.services.analysis_engine import analysis_engine
from src.services.novelty_service import novelty_service, EMPIRICAL_NOVELTY_THRESHOLDS


@pytest.fixture(scope="module", autouse=True)
def ensure_state_ready():
    """Ensure in-memory ML model registry is loaded."""
    if not state.is_ready:
        state.load_all()


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


def test_normal_incident_pattern_fit_and_novelty():
    """Validates that a typical crime incident yields high pattern fit and standard novelty."""
    normal_incident = {
        "scenario_title": "Routine Daytime Commercial Shoplifting",
        "incident_date": "2024-05-14",
        "incident_time": "14:15",
        "crime_category": "theft",
        "location_type": "commercial",
        "is_weekend": False,
        "has_property": True,
        "property_value": 85.0,
        "has_weapon": False,
        "has_injury": False
    }

    result = analysis_engine.analyze(normal_incident)

    assert "novelty" in result
    nov = result["novelty"]

    # 1. Behavioral Pattern Fit
    assert "behavioral_pattern_fit" in nov
    fit = nov["behavioral_pattern_fit"]
    assert 0.0 <= fit["fit_score"] <= 1.0
    assert 0.0 <= fit["fit_percentage"] <= 100.0
    assert fit["fit_level"] == "High Fit"
    assert "alignment" in fit["fit_summary"].lower()

    # 2. Novelty Tier & Score
    assert nov["novelty_score"] < EMPIRICAL_NOVELTY_THRESHOLDS["moderate_novelty_p95"]
    assert nov["novelty_tier"] == "Standard Behavioral Pattern"
    assert nov["is_novel"] is False
    assert nov["is_unusual"] is False

    # 3. Standard Banner (not a warning)
    assert nov["banner_title"] == "STANDARD BEHAVIORAL PATTERN"
    assert "consistent with major patterns" in nov["banner_message"]


def test_novel_incident_triggers_warning_banner_and_factors():
    """Validates that an atypical incident combination triggers the novel pattern warning."""
    novel_incident = {
        "scenario_title": "Atypical Armed Compound Burglary with Multiple Weapons, Drugs, and Injuries",
        "incident_date": "2024-09-20",
        "incident_time": "03:40",
        "crime_category": "burglary",
        "location_type": "residential",
        "is_weekend": True,
        "has_property": True,
        "property_value": 150000.0,
        "has_weapon": True,
        "weapon_count": 4,
        "is_multi_weapon": True,
        "has_injury": True,
        "injury_count": 3,
        "victim_count": 4,
        "offender_count": 4,
        "is_co_offender": True,
        "has_drug": True,
        "has_criminal_activity": True
    }

    result = analysis_engine.analyze(novel_incident)

    assert "novelty" in result
    nov = result["novelty"]

    # 1. Novelty Tier & Score Elevated
    assert nov["novelty_score"] >= EMPIRICAL_NOVELTY_THRESHOLDS["moderate_novelty_p95"]
    assert nov["novelty_tier"] in [
        "Moderate Behavioral Novelty",
        "High Behavioral Outlier",
        "Extreme Behavioral Outlier"
    ]
    assert nov["is_novel"] is True
    assert nov["is_unusual"] is True

    # 2. Exact Required Warning Banner Phrasing
    assert nov["banner_title"] == "⚠️ NOVEL BEHAVIORAL PATTERN"
    expected_message = (
        "This incident contains a behavioral combination that does not closely match "
        "the major patterns learned from the historical dataset."
    )
    assert nov["banner_message"] == expected_message

    # 3. Behavioral Pattern Fit reflects lower alignment
    fit = nov["behavioral_pattern_fit"]
    assert fit["fit_level"] in ["Moderate Fit", "Low Fit (Atypical Combination)"]

    # 4. Most Unusual Supported Behavioral Factors
    assert "unusual_behavioral_factors" in nov
    factors = nov["unusual_behavioral_factors"]
    assert len(factors) > 0

    for factor in factors:
        assert "factor_name" in factor
        assert isinstance(factor["factor_name"], str)
        assert factor["direction"] in ["Elevated", "Suppressed"]
        assert "incident_value" in factor
        assert "cluster_baseline_value" in factor
        assert "deviation_delta" in factor
        assert "explanation" in factor
        assert len(factor["explanation"]) > 0


def test_ethical_non_offender_language_guidelines():
    """Ensures that novelty responses never use prohibited personal or predictive terms."""
    incident = {
        "scenario_title": "Violent Street Confrontation",
        "incident_date": "2024-06-12",
        "incident_time": "22:15",
        "crime_category": "assault",
        "location_type": "street_outdoor",
        "is_weekend": True,
        "has_weapon": True,
        "weapon_count": 2,
        "has_injury": True,
        "victim_count": 2
    }

    result = analysis_engine.analyze(incident)
    nov = result["novelty"]

    # Prohibited terms list as explicitly instructed
    prohibited_terms = [
        "suspicious person",
        "dangerous person",
        "criminal person",
        "likely offender",
        "future crime",
        "high-risk individual"
    ]

    serialized_text = str(nov).lower()
    for term in prohibited_terms:
        assert term not in serialized_text, f"Found prohibited ethical term '{term}' in novelty output!"

    # Ensure ethical advisory explicitly grounds novelty in historical dataset combinations
    advisory = nov.get("ethical_advisory", "")
    assert "statistical rarity" in advisory.lower()
    assert "does not evaluate individual criminality" in advisory.lower()


def test_documented_empirical_thresholds():
    """Validates that thresholds adhere strictly to the Phase 9 calibrated quantiles."""
    thresholds = novelty_service.thresholds
    assert thresholds["moderate_novelty_p95"] == pytest.approx(0.4363, abs=1e-4)
    assert thresholds["high_outlier_p99"] == pytest.approx(0.5985, abs=1e-4)
    assert thresholds["extreme_outlier_p999"] == pytest.approx(0.7383, abs=1e-4)


def test_api_endpoint_serializes_novelty_result(client: TestClient):
    """Validates that POST /api/analyze/input returns the complete structured novelty model."""
    payload = {
        "scenario_title": "Commercial Armed Burglary Test",
        "incident_date": "2024-07-04",
        "incident_time": "01:20",
        "crime_category": "burglary",
        "location_type": "commercial",
        "is_weekend": True,
        "has_property": True,
        "property_value": 4500.0,
        "has_weapon": True,
        "weapon_count": 1,
        "has_injury": False
    }

    response = client.post("/api/analyze/input", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "novelty" in data
    nov = data["novelty"]

    assert "behavioral_pattern_fit" in nov
    assert "fit_score" in nov["behavioral_pattern_fit"]
    assert "fit_percentage" in nov["behavioral_pattern_fit"]
    assert "fit_level" in nov["behavioral_pattern_fit"]

    assert "novelty_score" in nov
    assert "novelty_tier" in nov
    assert "is_novel" in nov
    assert "banner_title" in nov
    assert "banner_message" in nov
    assert "unusual_behavioral_factors" in nov
    assert "ethical_advisory" in nov
