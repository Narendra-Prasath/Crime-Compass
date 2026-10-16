"""
CRIME DNA — Input Bridge Unit Tests
Validates encoding of human incident inputs into unit L2-normalized 70D Behavioral DNA vectors.
"""

import math
import numpy as np
import pytest
from src.features.input_bridge import bridge, ORDERED_FEATURE_NAMES, POPULATION_SETTING_MAPPING


def test_bridge_ordered_features_count():
    assert len(ORDERED_FEATURE_NAMES) == 70
    assert len(set(ORDERED_FEATURE_NAMES)) == 70


def test_bridge_encode_default_payload():
    payload = {
        "crime_category": "property",
        "incident_date": "2024-06-15",
        "incident_time": "14:30",
        "population_setting": "mid_sized_city"
    }
    raw_vec, norm_vec, subprofile_energies = bridge.encode(payload)

    assert raw_vec.shape == (70,)
    assert norm_vec.shape == (70,)
    assert np.all(np.isfinite(norm_vec))
    # Norm must be exactly 1.0 (unit sphere)
    assert pytest.approx(np.linalg.norm(norm_vec), abs=1e-5) == 1.0
    # Values bounded in [0.0, 1.0]
    assert np.all(norm_vec >= 0.0)
    assert np.all(norm_vec <= 1.0)
    # Check 7 subprofile groups
    assert len(subprofile_energies) == 7
    for grp, val in subprofile_energies.items():
        assert 0.0 <= val <= 100.0


def test_bridge_cyclical_time_encoding():
    # Midnight vs Noon
    raw_0, _, _ = bridge.encode({"incident_time": "00:00"})
    raw_12, _, _ = bridge.encode({"incident_time": "12:00"})

    # sin(0) = 0 -> scaled to 0.5; cos(0) = 1 -> scaled to 1.0
    sin_idx = ORDERED_FEATURE_NAMES.index("time_hour_sin")
    cos_idx = ORDERED_FEATURE_NAMES.index("time_hour_cos")

    assert pytest.approx(raw_0[sin_idx], abs=1e-3) == 0.5
    assert pytest.approx(raw_0[cos_idx], abs=1e-3) == 1.0

    # sin(pi) = 0 -> 0.5; cos(pi) = -1 -> 0.0
    assert pytest.approx(raw_12[sin_idx], abs=1e-3) == 0.5
    assert pytest.approx(raw_12[cos_idx], abs=1e-3) == 0.0


def test_bridge_population_setting_mapping():
    for setting_key, info in POPULATION_SETTING_MAPPING.items():
        payload = {"population_setting": setting_key}
        raw_vec, _, _ = bridge.encode(payload)
        col_idx = ORDERED_FEATURE_NAMES.index(info["col"])
        assert raw_vec[col_idx] == 1.0


def test_bridge_active_traits():
    payload = {
        "crime_category": "person_property",
        "has_weapon": True,
        "weapon_count": 2,
        "property_value": 50000.0
    }
    raw_vec, _, _ = bridge.encode(payload)
    traits = bridge.get_active_traits(raw_vec, top_n=5)
    assert len(traits) <= 5
    assert all("feature" in t and "value" in t for t in traits)
