"""
CRIME DNA — Behavioral DNA Comparison Feature Tests

Validates:
1. DNA Comparison Pipeline:
   - User Incident vs User Incident
   - User Incident vs Historical Incident
   - Historical Incident vs Historical Incident
   - Self-comparison (Identical incident yields 100% similarity, 0 differences)
2. Scientifically valid DNA similarity score using the 70D unit L2 vector representation.
3. DNA Comparison Table features: Time, Location, Property, Weapon, Injury, Crime, Victims.
   Symbols: ✓ for match, △ for differ/escalation, ~ for partial.
4. "What Changed?" analysis: headline, escalations, transitions, narrative.
5. Matching and Differing characteristics lists.
6. Subprofile energy comparisons (Temporal, Spatial, Method/Weapon, etc.).
7. Dynamic calculations (no hardcoded similarity values).
8. Ethical non-offender attribution advisory (no claims of same offender, guilt, or person).
9. FastAPI endpoints: GET /api/compare/presets and POST /api/compare.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from src.services.comparison_service import BehavioralComparisonService, comparison_service
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
def custom_theft_incident():
    """Daytime unarmed theft incident."""
    return {
        "scenario_title": "Daytime Residential Theft",
        "incident_date": "2024-05-10",
        "incident_time": "14:30",
        "crime_category": "property",
        "is_attempted": False,
        "offense_count": 1,
        "population_setting": "suburban",
        "has_weapon": False,
        "weapon_count": 0,
        "weapon_types": [],
        "has_property": True,
        "property_loss_type": "stolen",
        "stolen_val": 1200.0,
        "location_type": "residence_home",
        "victim_count": 0,
        "injury_count": 0,
        "has_injury": False,
        "officer_count": 0,
        "target_vulnerability": "unoccupied",
        "planning_level": "opportunistic"
    }


@pytest.fixture
def custom_burglary_incident():
    """Nighttime armed residential burglary incident."""
    return {
        "scenario_title": "Night Residential Burglary with Firearm",
        "incident_date": "2024-05-12",
        "incident_time": "02:15",
        "crime_category": "property",
        "is_attempted": False,
        "offense_count": 1,
        "population_setting": "suburban",
        "has_weapon": True,
        "weapon_count": 1,
        "weapon_types": ["handgun"],
        "has_property": True,
        "property_loss_type": "stolen",
        "stolen_val": 3500.0,
        "location_type": "residence_home",
        "victim_count": 1,
        "injury_count": 0,
        "has_injury": False,
        "officer_count": 0,
        "target_vulnerability": "asleep",
        "planning_level": "moderate"
    }


@pytest.fixture
def custom_violent_robbery_incident():
    """Night commercial armed robbery with injuries."""
    return {
        "scenario_title": "Armed Commercial Robbery with Assault",
        "incident_date": "2024-06-01",
        "incident_time": "23:45",
        "crime_category": "person_property",
        "is_attempted": False,
        "offense_count": 2,
        "population_setting": "urban_core",
        "has_weapon": True,
        "weapon_count": 1,
        "weapon_types": ["handgun"],
        "has_property": True,
        "property_loss_type": "stolen",
        "stolen_val": 5000.0,
        "location_type": "commercial_retail",
        "victim_count": 2,
        "injury_count": 1,
        "has_injury": True,
        "officer_count": 0,
        "target_vulnerability": "open_business",
        "planning_level": "organized"
    }


class TestDnaComparisonService:
    """Unit tests for BehavioralComparisonService."""

    def test_custom_vs_custom_comparison(self, custom_theft_incident, custom_burglary_incident):
        """Test comparison between two newly entered incidents."""
        spec_a = {"label": "Incident A (Theft)", "payload": custom_theft_incident}
        spec_b = {"label": "Incident B (Burglary)", "payload": custom_burglary_incident}

        result = comparison_service.compare(spec_a, spec_b)

        assert result is not None
        assert "incident_a" in result
        assert "incident_b" in result
        assert "dna_similarity" in result
        assert "dna_comparison_table" in result
        assert "what_changed" in result
        assert "matching_characteristics" in result
        assert "differing_characteristics" in result

        # Check similarity score calculation
        sim = result["dna_similarity"]
        assert 0.0 <= sim["similarity_score_pct"] <= 100.0
        assert isinstance(sim["match_tier"], str) and len(sim["match_tier"]) > 0
        assert sim["cosine_distance"] >= 0.0

        # Check comparison table structure
        table = result["dna_comparison_table"]
        features_in_table = [row["feature"] for row in table]
        assert "Time" in features_in_table
        assert "Location" in features_in_table
        assert "Property" in features_in_table
        assert "Weapon" in features_in_table
        assert "Injury" in features_in_table
        assert "Crime" in features_in_table

        # Weapon changed from None to Handgun -> symbol should be △
        weapon_row = next(r for r in table if r["feature"] == "Weapon")
        assert weapon_row["result"] == "△"
        assert weapon_row["match_status"] == "DIFFER"

        # Property is Yes for both -> symbol should be ✓
        property_row = next(r for r in table if r["feature"] == "Property")
        assert property_row["result"] == "✓"
        assert property_row["match_status"] == "MATCH"

        # Check "What Changed?"
        wc = result["what_changed"]
        assert wc["differ_count"] > 0
        assert len(wc["escalations"]) > 0  # weapon escalated
        assert any("weapon" in esc.lower() for esc in wc["escalations"])

    def test_self_comparison_yields_exact_match(self, custom_theft_incident):
        """Comparing an incident to itself should produce 100% similarity and zero differences."""
        spec_a = {"label": "Incident A", "payload": custom_theft_incident}
        spec_b = {"label": "Incident A (Copy)", "payload": custom_theft_incident}

        result = comparison_service.compare(spec_a, spec_b)

        sim = result["dna_similarity"]
        assert pytest.approx(sim["similarity_score_pct"], abs=0.01) == 100.0
        assert "High" in sim["match_tier"]
        assert pytest.approx(sim["cosine_distance"], abs=0.001) == 0.0

        # All table rows should be MATCH
        for row in result["dna_comparison_table"]:
            assert row["result"] == "✓"
            assert row["match_status"] == "MATCH"

        # Differing characteristics should be empty
        assert len(result["differing_characteristics"]) == 0
        assert len(result["matching_characteristics"]) >= 5

        # What changed differ_count should be 0
        assert result["what_changed"]["differ_count"] == 0
        assert len(result["what_changed"]["escalations"]) == 0

    def test_custom_vs_historical_comparison(self, custom_violent_robbery_incident):
        """Test comparing a newly entered incident against a historical incident ID."""
        spec_a = {"label": "New Incident", "payload": custom_violent_robbery_incident}
        spec_b = {"label": "Historical Baseline", "incident_id": "INC_000001"}

        result = comparison_service.compare(spec_a, spec_b)

        assert result["incident_a"]["source_type"] in ["user_input", "new_input"]
        assert result["incident_b"]["source_type"] == "historical"
        assert result["incident_b"]["incident_id"] == "INC_000001"

        assert 0.0 <= result["dna_similarity"]["similarity_score_pct"] <= 100.0
        assert len(result["dna_comparison_table"]) >= 6

    def test_historical_vs_historical_comparison(self):
        """Test comparing two selected historical incidents."""
        spec_a = {"label": "Historical A", "incident_id": "INC_000001"}
        spec_b = {"label": "Historical B", "incident_id": "INC_000002"}

        result = comparison_service.compare(spec_a, spec_b)

        assert result["incident_a"]["source_type"] == "historical"
        assert result["incident_b"]["source_type"] == "historical"
        assert result["incident_a"]["incident_id"] == "INC_000001"
        assert result["incident_b"]["incident_id"] == "INC_000002"

        assert 0.0 <= result["dna_similarity"]["similarity_score_pct"] <= 100.0
        assert len(result["dna_comparison_table"]) >= 6

    def test_escalation_detection_weapon_and_injury(self, custom_theft_incident, custom_violent_robbery_incident):
        """Test that changes involving weapons and injuries are flagged as escalations in 'What Changed?'."""
        spec_a = {"label": "Unarmed Theft", "payload": custom_theft_incident}
        spec_b = {"label": "Armed Assault", "payload": custom_violent_robbery_incident}

        result = comparison_service.compare(spec_a, spec_b)
        wc = result["what_changed"]

        # Escalations should capture both weapon and injury
        escalation_text = " ".join(wc["escalations"]).lower()
        assert "weapon" in escalation_text
        assert "injury" in escalation_text or "harm" in escalation_text

    def test_dynamic_scoring_not_hardcoded(
        self, custom_theft_incident, custom_burglary_incident, custom_violent_robbery_incident
    ):
        """Scores must vary dynamically across distinct pairs and never be hardcoded constants."""
        res_theft_burglary = comparison_service.compare(
            {"payload": custom_theft_incident},
            {"payload": custom_burglary_incident}
        )
        res_theft_violent = comparison_service.compare(
            {"payload": custom_theft_incident},
            {"payload": custom_violent_robbery_incident}
        )

        sim1 = res_theft_burglary["dna_similarity"]["similarity_score_pct"]
        sim2 = res_theft_violent["dna_similarity"]["similarity_score_pct"]

        assert sim1 != sim2
        assert sim1 > sim2  # Residential theft is closer to residential burglary than violent armed commercial robbery

    def test_subprofile_domain_energies(self, custom_theft_incident, custom_burglary_incident):
        """Test subprofile domain comparison values."""
        result = comparison_service.compare(
            {"payload": custom_theft_incident},
            {"payload": custom_burglary_incident}
        )

        subprofiles = result.get("subprofile_comparison", [])
        assert len(subprofiles) > 0
        for sp in subprofiles:
            assert "group_name" in sp
            assert "energy_a" in sp
            assert "energy_b" in sp
            assert "delta" in sp
            assert "alignment" in sp

    def test_ethical_non_offender_attribution(self, custom_theft_incident, custom_burglary_incident):
        """Strict non-attribution requirement: No claims of same offender or guilt."""
        result = comparison_service.compare(
            {"payload": custom_theft_incident},
            {"payload": custom_burglary_incident}
        )

        advisory = result["ethical_advisory"]
        assert isinstance(advisory, str)
        assert len(advisory) > 30
        assert "NOT indicate the same offender" in advisory

        # Scan generated narrative and headline for prohibited affirmative claims
        narrative_text = " ".join([
            result["what_changed"]["headline"],
            result["what_changed"]["narrative"],
        ]).lower()

        prohibited = [
            "same offender",
            "same perpetrator",
            "same suspect",
            "guilty person",
            "will commit",
            "next crime",
        ]
        for term in prohibited:
            assert term not in narrative_text


class TestDnaComparisonApi:
    """FastAPI integration tests for DNA comparison endpoints."""

    def test_get_comparison_presets(self, client):
        """Test GET /api/compare/presets returns curated presets."""
        response = client.get("/api/compare/presets")
        assert response.status_code == 200

        data = response.json()
        assert "presets" in data
        assert "total_presets" in data
        assert data["total_presets"] >= 3

        first_preset = data["presets"][0]
        assert "id" in first_preset
        assert "title" in first_preset
        assert "description" in first_preset
        assert "incident_a" in first_preset
        assert "incident_b" in first_preset

    def test_post_compare_custom_vs_custom(self, client, custom_theft_incident, custom_burglary_incident):
        """Test POST /api/compare with custom incident payloads."""
        payload = {
            "incident_a": {
                "label": "Theft Inc A",
                "payload": custom_theft_incident
            },
            "incident_b": {
                "label": "Burglary Inc B",
                "payload": custom_burglary_incident
            }
        }

        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200

        body = response.json()
        assert "dna_similarity" in body
        assert "dna_comparison_table" in body
        assert "what_changed" in body
        assert "matching_characteristics" in body
        assert "differing_characteristics" in body

        # Table rows check
        table = body["dna_comparison_table"]
        features = [r["feature"] for r in table]
        assert "Time" in features
        assert "Location" in features
        assert "Property" in features
        assert "Weapon" in features
        assert "Injury" in features
        assert "Crime" in features

    def test_post_compare_preset_theft_vs_burglary(self, client):
        """Test POST /api/compare using preset definition."""
        presets_resp = client.get("/api/compare/presets")
        assert presets_resp.status_code == 200
        preset = presets_resp.json()["presets"][0]

        compare_req = {
            "incident_a": preset["incident_a"],
            "incident_b": preset["incident_b"]
        }

        response = client.post("/api/compare", json=compare_req)
        assert response.status_code == 200
        data = response.json()
        assert data["dna_similarity"]["similarity_score_pct"] > 0

    def test_post_compare_historical_pair(self, client):
        """Test POST /api/compare with two historical incident IDs."""
        payload = {
            "incident_a": {
                "label": "Historical 01",
                "incident_id": "INC_000001"
            },
            "incident_b": {
                "label": "Historical 02",
                "incident_id": "INC_000002"
            }
        }

        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["incident_a"]["incident_id"] == "INC_000001"
        assert data["incident_b"]["incident_id"] == "INC_000002"

    def test_post_compare_validation_error_missing_data(self, client):
        """Test POST /api/compare returns 400 when an incident specification is empty."""
        payload = {
            "incident_a": {
                "label": "Empty Spec A"
            },
            "incident_b": {
                "label": "Historical 01",
                "incident_id": "INC_000001"
            }
        }

        response = client.post("/api/compare", json=payload)
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "must provide either" in detail
