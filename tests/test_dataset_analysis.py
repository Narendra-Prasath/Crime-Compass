"""
Tests for CRIME COMPASS 🧭 Dataset Upload & Behavioral Analysis Feature
"""

import io
import json
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.dataset_service import dataset_service

client = TestClient(app)

# Sample Synthetic Fixtures strictly for automated testing (clearly identified as synthetic test fixtures)
SYNTHETIC_STANDARD_CSV = """incident_id,incident_date,incident_time,city_town,district,state_ut,crime_category,has_weapon,has_property,property_value,has_injury,victim_count,offender_count
TEST_001,2024-05-10,21:30,Bengaluru,Bengaluru Urban,Karnataka,person_property,1,1,45000,1,2,2
TEST_002,2024-05-11,22:15,Bengaluru,Bengaluru Urban,Karnataka,person_property,1,1,32000,1,1,2
TEST_003,2024-05-15,02:45,Bengaluru,Bengaluru Urban,Karnataka,property,0,1,120000,0,1,1
TEST_004,2024-06-01,03:10,Bengaluru,Bengaluru Urban,Karnataka,property,0,1,85000,0,1,1
TEST_005,2024-06-18,14:20,Mysuru,Mysuru,Karnataka,person,1,0,0,1,1,1
TEST_006,2024-06-25,16:00,Mysuru,Mysuru,Karnataka,person,1,0,0,1,2,1
"""

SYNTHETIC_MAPPED_CSV = """fir_no,event_date,occ_time,city_name,offense_type,weapon_used,theft_involved,loss_amount,hurt,num_victims
FIR_101,2024-01-12,23:00,Delhi,armed_robbery,handgun,yes,50000,yes,2
FIR_102,2024-01-15,22:30,Delhi,armed_robbery,knife,yes,35000,yes,1
FIR_103,2024-02-04,01:15,Delhi,burglary,none,yes,90000,no,1
FIR_104,2024-02-18,03:30,Noida,burglary,none,yes,60000,no,1
FIR_105,2024-03-05,19:45,Noida,assault,stick,no,0,yes,1
FIR_106,2024-03-22,20:10,Noida,assault,knife,no,0,yes,2
"""

SYNTHETIC_INSUFFICIENT_CSV = """student_id,math_score,physics_score,grade
STU_1,85,90,A
STU_2,72,68,B
STU_3,94,92,A
"""


def test_validate_empty_file_fails():
    """Empty files must be rejected gracefully."""
    response = client.post("/api/datasets/validate", files={"file": ("empty.csv", b"", "text/csv")})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_validate_binary_file_rejected():
    """Binary/executable files must be rejected for security."""
    binary_content = b"\x00\x01\x02\x03MZ\x90\x00"
    response = client.post("/api/datasets/validate", files={"file": ("malware.exe", binary_content, "application/octet-stream")})
    assert response.status_code == 400
    assert "binary" in response.json()["detail"].lower() or "prohibited" in response.json()["detail"].lower()


def test_validate_standard_csv():
    """Valid CSV should return summary, preview, and high-confidence suggestions."""
    response = client.post(
        "/api/datasets/validate",
        files={"file": ("synthetic_crimes.csv", SYNTHETIC_STANDARD_CSV.encode("utf-8"), "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 6
    assert data["total_columns"] == 13
    assert len(data["preview_rows"]) == 5
    assert data["file_token"].startswith("TOKEN_")
    assert "crime_category" in data["suggested_mapping"]
    assert "Bengaluru" in data["available_locations"]["cities"]
    assert data["date_range"]["min_date"] == "2024-05-10"


def test_validate_nonstandard_column_aliases():
    """Nonstandard column names like fir_no, event_date, offense_type should be auto-mapped via aliases."""
    response = client.post(
        "/api/datasets/validate",
        files={"file": ("police_records.csv", SYNTHETIC_MAPPED_CSV.encode("utf-8"), "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    mapping = data["suggested_mapping"]
    assert mapping.get("incident_id") == "fir_no"
    assert mapping.get("incident_date") == "event_date"
    assert mapping.get("crime_category") == "offense_type"
    assert mapping.get("has_weapon") == "weapon_used"
    assert mapping.get("property_value") == "loss_amount"


def test_validate_insufficient_behavioral_data():
    """Files lacking any behavioral columns should trigger warning/notes."""
    response = client.post(
        "/api/datasets/validate",
        files={"file": ("grades.csv", SYNTHETIC_INSUFFICIENT_CSV.encode("utf-8"), "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert any("behavioral" in w.lower() for w in data["warnings"])


def test_analyze_dataset_end_to_end():
    """Complete behavioral intelligence analysis on synthetic incident dataset."""
    # 1. Validate
    val_resp = client.post(
        "/api/datasets/validate",
        files={"file": ("synthetic_crimes.csv", SYNTHETIC_STANDARD_CSV.encode("utf-8"), "text/csv")}
    )
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    token = val_data["file_token"]
    mapping = val_data["suggested_mapping"]

    # 2. Analyze
    analyze_payload = {
        "file_token": token,
        "filename": "synthetic_crimes.csv",
        "column_mapping": mapping,
        "scope": {
            "compare_with_reference": True
        },
        "user_id": "test_user_alpha"
    }

    resp = client.post("/api/datasets/analyze", json=analyze_payload)
    assert resp.status_code == 200
    res = resp.json()

    # Verify Analysis Sections
    assert res["analysis_id"].startswith("DATASET_ANALYSIS_")
    assert res["dataset_summary"]["total_records"] == 6

    # Verify Behavioral Patterns (Dataset-Specific, not hardcoded 8 reference clusters)
    patterns = res["behavioral_patterns"]
    assert len(patterns) >= 1
    for pat in patterns:
        assert pat["pattern_id"].startswith("DP_")
        assert len(pat["title"]) > 0
        assert pat["incident_count"] > 0
        assert len(pat["sample_incident_ids"]) > 0

    # Verify Similar Incidents & Query Self-Exclusion (source != target)
    similars = res["similar_incidents"]
    for pair in similars:
        assert pair["source_id"] != pair["target_id"], "Query record cannot be in its own nearest neighbors!"
        assert pair["similarity_score"] <= 1.0001
        assert len(pair["matching_characteristics"]) >= 0

    # Verify Cross-Crime Patterns
    cross_crime = res["cross_crime_patterns"]
    for cc in cross_crime:
        assert "non_offender_disclaimer" in cc
        assert "DO NOT imply" in cc["non_offender_disclaimer"]

    # Verify Location Insights
    loc_insights = res["location_insights"]
    assert loc_insights["is_available"] is True
    assert len(loc_insights["areas"]) > 0
    assert "crime rates" in loc_insights["disclaimer"].lower()

    # Verify Temporal Evolution
    temp = res["temporal_evolution"]
    assert temp["is_available"] is True
    assert len(temp["period_breakdown"]) > 0
    assert "disclaimer" in temp

    # Verify Unusual Combinations
    unusual = res["unusual_combinations"]
    assert len(unusual) > 0
    for u in unusual:
        assert u["novelty_label"] in ("Unusual Combination", "Less Common Combination")
        assert len(u["contributing_features"]) > 0

    # Verify Reference Comparison
    ref_comp = res["reference_comparison"]
    assert ref_comp is not None
    assert ref_comp["status"] == "completed"

    # Verify Why These Results & Technical Details
    assert len(res["why_these_results"]["observed_facts"]) > 0
    assert len(res["why_these_results"]["algorithm_findings"]) > 0
    assert res["technical_details"]["records_analyzed"] == 6

    # 3. Retrieve Analysis by ID
    get_resp = client.get(f"/api/datasets/analyses/{res['analysis_id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["analysis_id"] == res["analysis_id"]

    # 4. Export Analysis (JSON and CSV)
    json_export = client.get(f"/api/datasets/analyses/{res['analysis_id']}/export?format=json")
    assert json_export.status_code == 200
    assert json_export.headers["content-type"] == "application/json"

    csv_export = client.get(f"/api/datasets/analyses/{res['analysis_id']}/export?format=csv")
    assert csv_export.status_code == 200
    assert "text/csv" in csv_export.headers["content-type"]

    # 5. Delete Analysis
    del_resp = client.delete(f"/api/datasets/analyses/{res['analysis_id']}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True

    # 6. Verify Deleted
    get_after_del = client.get(f"/api/datasets/analyses/{res['analysis_id']}")
    assert get_after_del.status_code == 404


def test_analyze_with_location_scope_filter():
    """Testing location-based scope filtering on uploaded dataset."""
    val_resp = client.post(
        "/api/datasets/validate",
        files={"file": ("synthetic_crimes.csv", SYNTHETIC_STANDARD_CSV.encode("utf-8"), "text/csv")}
    )
    token = val_resp.json()["file_token"]
    mapping = val_resp.json()["suggested_mapping"]

    # Filter to only Mysuru (2 records out of 6)
    analyze_payload = {
        "file_token": token,
        "filename": "synthetic_crimes.csv",
        "column_mapping": mapping,
        "scope": {
            "filter_city": "Mysuru"
        }
    }

    resp = client.post("/api/datasets/analyze", json=analyze_payload)
    assert resp.status_code == 200
    res = resp.json()
    assert res["dataset_summary"]["total_records"] == 2
    assert res["dataset_summary"]["initial_records_count"] == 6
    assert res["dataset_summary"]["excluded_by_scope"] == 4
