"""
CRIME DNA — "WHAT CHANGED?" Explanation Layer Tests

Validates:
1. Clear identification of matching behavioral characteristics (match_items, match_count, summary_match_line).
2. Clear identification of different behavioral characteristics (differ_items, differ_count, summary_differ_line).
3. Explicit classification of same crime category vs different crime category (same_crime_category, crime_category_status, crime_category_detail).
4. Ranked identification of strongest similarities (why the DNA score is high).
5. Ranked identification of most meaningful differences (why the DNA score diverged).
6. Non-technical, extremely simple presentation:
   Example:
   4 behavioral characteristics match.
   2 behavioral characteristics differ.
   MATCH:
   ✓ Night
   ✓ Residential
   ✓ Property
   ✓ No injury
   DIFFER:
   △ Crime category
   △ Weapon context
7. Dynamic calculation across distinct incident scenarios (never hardcoded).
8. Full integration with FastAPI POST /api/compare endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from src.services.comparison_service import comparison_service
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
def night_residential_theft():
    """Nighttime unarmed residential theft."""
    return {
        "scenario_title": "Night Residential Theft",
        "incident_date": "2024-05-10",
        "incident_time": "23:30",
        "crime_category": "theft",
        "has_property": True,
        "has_weapon": False,
        "weapon_count": 0,
        "weapon_types": [],
        "has_injury": False,
        "injury_count": 0,
        "location_type": "residence_home",
        "victim_count": 1,
    }


@pytest.fixture
def night_residential_burglary_armed():
    """Nighttime armed residential burglary with handgun."""
    return {
        "scenario_title": "Night Residential Burglary with Firearm",
        "incident_date": "2024-05-12",
        "incident_time": "02:15",
        "crime_category": "burglary",
        "has_property": True,
        "has_weapon": True,
        "weapon_count": 1,
        "weapon_types": ["handgun"],
        "has_injury": False,
        "injury_count": 0,
        "location_type": "residence_home",
        "victim_count": 1,
    }


@pytest.fixture
def day_commercial_robbery_injured():
    """Daytime armed commercial robbery with physical injuries."""
    return {
        "scenario_title": "Daytime Armed Commercial Robbery with Assault",
        "incident_date": "2024-06-01",
        "incident_time": "14:00",
        "crime_category": "robbery",
        "has_property": True,
        "has_weapon": True,
        "weapon_count": 1,
        "weapon_types": ["handgun"],
        "has_injury": True,
        "injury_count": 1,
        "location_type": "commercial_retail",
        "victim_count": 2,
    }


class TestWhatChangedExplanationLayer:
    """Tests for the 'WHAT CHANGED?' explanation generation."""

    def test_theft_vs_burglary_matches_and_differences(
        self, night_residential_theft, night_residential_burglary_armed
    ):
        """
        Validates the classic comparison:
        Night, Residential, Property, No injury, Victim headcount match (5 matches).
        Crime category (theft vs burglary) and Weapon context (none vs handgun) differ (2 differences).
        """
        spec_a = {"label": "Incident A (Theft)", "payload": night_residential_theft}
        spec_b = {"label": "Incident B (Burglary)", "payload": night_residential_burglary_armed}

        result = comparison_service.compare(spec_a, spec_b)
        wc = result["what_changed"]

        # 1. Matching characteristics
        assert wc["match_count"] >= 4
        assert "Night" in wc["match_items"]
        assert "Residential" in wc["match_items"]
        assert "Property" in wc["match_items"]
        assert "No injury" in wc["match_items"]

        # 2. Differing characteristics
        assert wc["differ_count"] >= 2
        assert "Crime category" in wc["differ_items"]
        assert "Weapon context" in wc["differ_items"]

        # 3. Summary text matches example requirement
        assert "match" in wc["summary_match_line"].lower()
        assert "differ" in wc["summary_differ_line"].lower()
        assert str(wc["match_count"]) in wc["summary_match_line"]
        assert str(wc["differ_count"]) in wc["summary_differ_line"]

        # 4. Same crime category vs different category
        assert wc["same_crime_category"] is False
        assert wc["crime_category_status"] == "Different Crime Category"
        assert "cross-category" in wc["crime_category_detail"].lower() or "different crime" in wc["crime_category_detail"].lower()

        # 5. Strongest similarities
        assert len(wc["strongest_similarities"]) >= 3
        similarities_text = " ".join(wc["strongest_similarities"]).lower()
        assert "timing" in similarities_text or "night" in similarities_text
        assert "setting" in similarities_text or "residential" in similarities_text
        assert "property" in similarities_text

        # 6. Most meaningful differences
        assert len(wc["most_meaningful_differences"]) >= 2
        differences_text = " ".join(wc["most_meaningful_differences"]).lower()
        assert "weapon" in differences_text
        assert "crime" in differences_text or "category" in differences_text

    def test_same_crime_category_scenario(self, night_residential_theft):
        """When two incidents share the exact same crime category, it must be reported accurately."""
        theft_2 = dict(night_residential_theft)
        theft_2["scenario_title"] = "Second Residential Theft"
        theft_2["incident_time"] = "22:00"

        result = comparison_service.compare(
            {"payload": night_residential_theft},
            {"payload": theft_2}
        )
        wc = result["what_changed"]

        assert wc["same_crime_category"] is True
        assert wc["crime_category_status"] == "Same Crime Category"
        assert any("crime category" in item.lower() for item in wc["match_items"])
        assert "Crime category" not in wc["differ_items"]
        assert "same statutory" in wc["crime_category_detail"].lower()

    def test_identical_incidents_zero_differences(self, night_residential_theft):
        """Comparing an incident to itself must show all dimensions matching and zero differences."""
        result = comparison_service.compare(
            {"payload": night_residential_theft},
            {"payload": night_residential_theft}
        )
        wc = result["what_changed"]

        assert wc["differ_count"] == 0
        assert len(wc["differ_items"]) == 0
        assert wc["match_count"] == wc["total_dimensions_compared"]
        assert "0 behavioral characteristics differ" in wc["summary_differ_line"]
        assert wc["same_crime_category"] is True
        assert "zero behavioral differences" in wc["most_meaningful_differences"][0].lower()

    def test_major_escalation_meaningful_differences(
        self, night_residential_theft, day_commercial_robbery_injured
    ):
        """Testing wide operational divergence: time, location, weapon, injury, crime category."""
        result = comparison_service.compare(
            {"payload": night_residential_theft},
            {"payload": day_commercial_robbery_injured}
        )
        wc = result["what_changed"]

        # Multiple differing dimensions
        assert wc["differ_count"] >= 4
        assert "Timing / diurnal pattern" in wc["differ_items"]
        assert "Location context" in wc["differ_items"]
        assert "Weapon context" in wc["differ_items"]
        assert "Injury / physical harm" in wc["differ_items"]
        assert "Crime category" in wc["differ_items"]

        # Meaningful differences must highlight injury and weapon escalation
        diffs_text = " ".join(wc["most_meaningful_differences"]).lower()
        assert "weapon" in diffs_text
        assert "harm" in diffs_text or "injury" in diffs_text

    def test_dynamic_generation_no_hardcoding(
        self, night_residential_theft, night_residential_burglary_armed, day_commercial_robbery_injured
    ):
        """Changing input attributes must dynamically change match_items and differ_items."""
        res_pair1 = comparison_service.compare(
            {"payload": night_residential_theft},
            {"payload": night_residential_burglary_armed}
        )
        res_pair2 = comparison_service.compare(
            {"payload": night_residential_theft},
            {"payload": day_commercial_robbery_injured}
        )

        wc1 = res_pair1["what_changed"]
        wc2 = res_pair2["what_changed"]

        assert wc1["match_count"] != wc2["match_count"]
        assert wc1["differ_count"] != wc2["differ_count"]
        assert wc1["match_items"] != wc2["match_items"]
        assert wc1["differ_items"] != wc2["differ_items"]

    def test_api_endpoint_what_changed_structure(
        self, client, night_residential_theft, night_residential_burglary_armed
    ):
        """Test POST /api/compare returns the complete explanation layer matching the schema."""
        payload = {
            "incident_a": {"label": "Theft Inc A", "payload": night_residential_theft},
            "incident_b": {"label": "Burglary Inc B", "payload": night_residential_burglary_armed}
        }

        response = client.post("/api/compare", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "what_changed" in data
        wc = data["what_changed"]

        # Verify all 5 pillars in the API payload
        assert "match_items" in wc and isinstance(wc["match_items"], list)
        assert "differ_items" in wc and isinstance(wc["differ_items"], list)
        assert "same_crime_category" in wc and isinstance(wc["same_crime_category"], bool)
        assert "crime_category_status" in wc
        assert "crime_category_detail" in wc
        assert "strongest_similarities" in wc and isinstance(wc["strongest_similarities"], list)
        assert "most_meaningful_differences" in wc and isinstance(wc["most_meaningful_differences"], list)
        assert "summary_match_line" in wc
        assert "summary_differ_line" in wc
