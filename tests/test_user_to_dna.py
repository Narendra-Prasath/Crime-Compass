"""
CRIME DNA — User Incident to Behavioral DNA Pipeline Tests
Proves that:
1. Valid user inputs produce both Human-Readable and Machine-Readable Behavioral DNA.
2. Invalid inputs are rejected.
3. The generated representation is 100% compatible with existing ML components.
4. No fake or unmapped values are generated.
5. Human-readable labels are dynamically generated from submitted values, not hardcoded.
"""

import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.features.input_bridge import (
    bridge,
    ORDERED_FEATURE_NAMES,
    POPULATION_SETTING_MAPPING
)
from src.features.dna_encoder import BehavioralDNAEncoder
from src.api.state import state
from src.api.main import app


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def ensure_state_loaded():
    """Ensure ML state registry is loaded once for test module."""
    if not state.is_ready:
        state.load_all()


def test_dna_generation_valid_input():
    payload = {
        "scenario_title": "Commercial Armed Robbery",
        "incident_date": "2024-11-15",
        "incident_time": "21:45",
        "crime_category": "person_property",
        "is_attempted": False,
        "offense_count": 2,
        "population_setting": "mid_sized_city",
        "has_weapon": True,
        "weapon_count": 2,
        "victim_count": 2,
        "victim_avg_age": 34.0,
        "offender_count": 2,
        "offender_avg_age": 22.0,
        "has_property": True,
        "property_value": 3500.0,
        "has_injury": True,
        "has_arrest": False
    }

    raw_vec, norm_vec, subprofile_energies = bridge.encode(payload)
    human_dna = bridge.generate_human_readable_fingerprint(payload, raw_vec)
    machine_dna = bridge.generate_machine_readable_fingerprint(payload, raw_vec, norm_vec, subprofile_energies)

    # 1. Vector properties
    assert raw_vec.shape == (70,)
    assert norm_vec.shape == (70,)
    assert pytest.approx(np.linalg.norm(norm_vec), abs=1e-5) == 1.0
    assert np.all(raw_vec >= 0.0)
    assert np.all(raw_vec <= 1.0)

    # 2. Machine-readable structure
    assert machine_dna["vector_dimension"] == 70
    assert len(machine_dna["feature_names"]) == 70
    assert machine_dna["feature_names"] == ORDERED_FEATURE_NAMES
    assert len(machine_dna["raw_vector"]) == 70
    assert len(machine_dna["normalized_vector"]) == 70
    assert len(machine_dna["feature_vector_dict"]) == 70

    # 3. Human-readable structure
    assert human_dna["title"] == "BEHAVIORAL DNA"
    assert len(human_dna["summary_chips"]) >= 5
    assert len(human_dna["traits"]) >= 5
    assert "BEHAVIORAL DNA" in human_dna["plain_text"]

    # Verify dynamic traits reflect actual submitted values
    plain_text = human_dna["plain_text"]
    assert "🌙 Night (21:45)" in plain_text
    assert "🔫 Armed Encounter (2 weapons)" in plain_text
    assert "👥 2 Victims (avg age 34)" in plain_text
    assert "👥 2 Co-Offenders (avg age 22)" in plain_text
    assert "📦 Property Involved ($3,500 value)" in plain_text
    assert "🩹 Physical Injury Sustained" in plain_text


def test_dna_generation_dynamic_labels_daytime_unarmed():
    # Contrast case: daytime, unarmed, 1 victim, burglary
    payload = {
        "scenario_title": "Daytime Unarmed Theft",
        "incident_date": "2024-05-14",
        "incident_time": "14:15",
        "crime_category": "property",
        "population_setting": "metropolitan_core",
        "has_weapon": False,
        "victim_count": 1,
        "victim_avg_age": 52.0,
        "offender_count": 1,
        "has_property": True,
        "property_value": 850.0,
        "has_injury": False,
        "has_arrest": True
    }

    raw_vec, norm_vec, subprofile_energies = bridge.encode(payload)
    human_dna = bridge.generate_human_readable_fingerprint(payload, raw_vec)

    plain_text = human_dna["plain_text"]
    # Must NOT contain night, weapon, or injury
    assert "🌙 Night" not in plain_text
    assert "☀️ Daytime (14:15)" in plain_text
    assert "🚫 No Weapon (Unarmed)" in plain_text
    assert "👤 1 Victim (age 52)" in plain_text
    assert "⚖️ Immediate On-Scene Arrest" in plain_text
    assert "🛡️" in [t["icon"] for t in human_dna["traits"]]


def test_compatibility_with_existing_ml_components():
    """Validates that the generated 70D vector is seamlessly accepted by all existing ML models."""
    payload = {
        "crime_category": "person_property",
        "incident_date": "2024-08-10",
        "incident_time": "22:00",
        "population_setting": "mid_sized_city",
        "has_weapon": True,
        "weapon_count": 1,
        "has_property": True,
        "property_value": 1500.0
    }

    _, norm_vec, _ = bridge.encode(payload)
    query_2d = norm_vec.reshape(1, -1)

    # 1. Similarity Engine (KNN index)
    assert state.similarity_engine is not None
    assert state.similarity_engine.model is not None
    distances, indices = state.similarity_engine.model.kneighbors(query_2d, n_neighbors=5)
    assert distances.shape == (1, 5)
    assert indices.shape == (1, 5)
    assert np.all(distances[0] >= 0.0)
    assert np.all(distances[0] <= 2.0)  # Cosine distance range [0, 2]

    # 2. Spherical K-Means Clusterer
    assert state.clusterer is not None
    pred = state.clusterer.predict_cluster(norm_vec)
    assert "assigned_cluster_id" in pred
    assert 0 <= pred["assigned_cluster_id"] < 8
    assert "cluster_name" in pred
    assert pred["distance_to_centroid"] >= 0.0

    # 3. Isolation Forest Anomaly Detector
    if state.isolation_forest is not None:
        dec_score = float(state.isolation_forest.decision_function(query_2d)[0])
        assert np.isfinite(dec_score)


def test_no_fake_or_unmapped_features():
    """Ensures exact 1-to-1 correspondence with the Phase 3 feature taxonomy."""
    df_cleaned = bridge.to_cleaned_dataframe({"crime_category": "property"})
    dna_df = bridge.dna_encoder.transform(df_cleaned)

    # Drop incident_id
    extracted_cols = [c for c in dna_df.columns if c != "incident_id"]
    assert len(extracted_cols) == 70
    assert set(extracted_cols) == set(ORDERED_FEATURE_NAMES)


def test_invalid_input_rejection(client: TestClient):
    """Pydantic validation rejects negative values, invalid ranges, and bad types."""
    # Negative victim count
    res1 = client.post("/api/analyze/input", json={"victim_count": -3, "crime_category": "property"})
    assert res1.status_code == 422

    # Negative property value
    res2 = client.post("/api/analyze/input", json={"property_value": -100.0, "crime_category": "property"})
    assert res2.status_code == 422

    # Out-of-bounds hour
    res3 = client.post("/api/analyze/input", json={"incident_hour": 25, "crime_category": "property"})
    assert res3.status_code == 422
