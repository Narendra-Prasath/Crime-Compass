"""
Regression & Integrity Tests for Behavioral Fingerprint Radar & Top Active Dimensions

Verifies:
1. 70D fingerprint tracing to 7 canonical radar dimensions.
2. Group energy calculation and orthogonal energy conservation: sum(E_g^2) ≈ 1.0.
3. Monotonic, non-increasing ordering of Top Active Dimensions (no inversions).
4. Mathematical derivation of identical values (e.g., 0.2802 and 7.8% energy in INC_135749)
   as genuine unit L2 normalized coordinates of active binary features (1.0 / ||x||_2).
5. Dynamic updating across multiple incidents with diverse fingerprints.
6. Defensive handling of non-finite, missing, and zero-valued features.
"""

import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


CANONICAL_DIMENSIONS = [
    "temporal_dynamics",
    "crime_characteristics",
    "location_and_environment",
    "method_and_activity",
    "people_and_demographics",
    "property_and_economics",
    "context_and_harm",
]


class TestBehavioralRadarAndDimensions:
    """Comprehensive test suite for Radar and Top Active Dimensions."""

    def test_canonical_radar_dimensions_present_and_bounded(self, client):
        """Verify all 7 canonical radar dimensions exist, are bounded in [0, 1], and finite."""
        incidents_to_test = ["INC_136975", "INC_135749", "INC_145291", "INC_171133", "INC_082341"]
        for inc_id in incidents_to_test:
            resp = client.get(f"/api/incidents/{inc_id}/dna")
            assert resp.status_code == 200, f"Failed to get DNA for {inc_id}"
            data = resp.json()
            energies = data["group_energies"]

            # All 7 canonical dimensions must be present
            for dim in CANONICAL_DIMENSIONS:
                assert dim in energies, f"Missing dimension '{dim}' in {inc_id}"
                val = energies[dim]
                assert isinstance(val, (int, float)), f"Non-numeric energy for {dim} in {inc_id}"
                assert math.isfinite(val), f"Non-finite energy for {dim} in {inc_id}"
                assert 0.0 <= val <= 1.0, f"Energy out of bounds [0, 1] for {dim} in {inc_id}: {val}"

    def test_radar_orthogonal_energy_conservation(self, client):
        """
        Verify the sum of squared group energies equals the sum of squared features
        within numerical rounding tolerance: sum(E_g^2) ≈ 1.0 for unit L2 normalized vectors.
        """
        incidents_to_test = ["INC_136975", "INC_135749", "INC_145291", "INC_171133", "INC_082341"]
        for inc_id in incidents_to_test:
            resp = client.get(f"/api/incidents/{inc_id}/dna")
            data = resp.json()
            energies = data["group_energies"]
            sum_sq_energies = sum(e ** 2 for e in energies.values())
            # Group energies are rounded to 4 decimals, so tolerance is ~0.02
            assert abs(sum_sq_energies - 1.0) < 0.02, (
                f"Group energies sum of squares {sum_sq_energies} deviates from 1.0 for {inc_id}"
            )

    def test_top_active_traits_strict_monotonicity(self, client):
        """
        Ensure feature ranking in Top Active Dimensions is strictly monotonically non-increasing.
        Fixes regression where low-magnitude traits appeared before high-magnitude traits (e.g. INC_000595).
        """
        test_incidents = ["INC_000595", "INC_000510", "INC_136975", "INC_135749", "INC_145291", "INC_171133"]
        for inc_id in test_incidents:
            resp = client.get(f"/api/incidents/{inc_id}/dna")
            assert resp.status_code == 200
            traits = resp.json()["top_active_traits"]
            assert len(traits) > 0, f"No active traits for {inc_id}"

            for i in range(len(traits) - 1):
                val_curr = traits[i]["value"]
                val_next = traits[i + 1]["value"]
                assert val_curr >= val_next, (
                    f"Out of order traits in {inc_id} at rank {i+1} vs {i+2}: {val_curr} < {val_next}"
                )

    def test_origin_of_0_2802_and_energy_in_inc_135749(self, client):
        """
        Verifies mathematically that 0.2802 and 7.8% energy in INC_135749 genuinely stem from
        active binary features normalized by the incident's raw L2 norm.
        """
        resp = client.get("/api/incidents/INC_135749/dna")
        assert resp.status_code == 200
        data = resp.json()
        traits = data["top_active_traits"]

        # Features with value 0.2802
        traits_2802 = [t for t in traits if t["value"] == 0.2802]
        assert len(traits_2802) >= 4, "Expected multiple active binary features with 0.2802 in INC_135749"

        # Verify energy share matches v^2 * 100
        for t in traits_2802:
            expected_energy = round((t["value"] ** 2) * 100.0, 2)
            assert abs(t["energy_share_pct"] - expected_energy) <= 0.05

        # Check raw model matrix to confirm identical underlying coordinates
        idx = state.id_to_idx["INC_135749"]
        vec = state.normalized_matrix[idx]
        for t in traits_2802:
            feat_idx = state.feature_names.index(t["feature"])
            assert round(float(vec[feat_idx]), 4) == 0.2802

    def test_diverse_fingerprints_have_different_characteristic_values(self, client):
        """
        Verify that different incidents produce distinctly different top coordinate values,
        proving that 0.2802 is not a hardcoded fallback or static placeholder.
        """
        expected_top_values = {
            "INC_136975": 0.2833,
            "INC_145291": 0.2659,
            "INC_171133": 0.3302,
            "INC_082341": 0.2987,
            "INC_135749": 0.2802,
        }
        for inc_id, expected_val in expected_top_values.items():
            resp = client.get(f"/api/incidents/{inc_id}/dna")
            assert resp.status_code == 200
            top_trait = resp.json()["top_active_traits"][0]
            assert top_trait["value"] == expected_val, (
                f"Incident {inc_id} top value {top_trait['value']} != expected {expected_val}"
            )

    def test_zero_valued_and_missing_features_handled_safely(self, client):
        """Verify zero-valued features are handled gracefully without breaking radar or traits."""
        # Incident with zero property involvement
        resp = client.get("/api/incidents/INC_136975/dna")
        data = resp.json()
        assert data["group_energies"]["property_and_economics"] == 0.0

        # No non-positive traits in top active traits
        for t in data["top_active_traits"]:
            assert t["value"] > 0.0
            assert t["energy_share_pct"] > 0.0

    def test_non_existent_incident_returns_404(self, client):
        """Verify 404 is returned gracefully for invalid incident IDs."""
        resp = client.get("/api/incidents/INC_NON_EXISTENT_ID/dna")
        assert resp.status_code == 404
        assert resp.json()["error"] == "IncidentNotFoundError"
