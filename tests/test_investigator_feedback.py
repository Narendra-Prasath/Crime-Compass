"""
Unit and Integration Tests for Human-In-The-Loop Investigator Feedback
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.feedback_service import feedback_service, JSONL_PATH, DB_PATH


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_submit_positive_feedback(client):
    """Test submitting positive feedback with specific useful aspects."""
    payload = {
        "is_useful": True,
        "target_type": "incident_analysis",
        "target_id": "INC_136975",
        "useful_aspects": ["similar_time", "similar_location", "similar_property"],
        "notes": "Strong correlation on residential nocturnal timing."
    }
    res = client.post("/api/feedback", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "received"
    assert data["feedback_id"].startswith("FB_")
    assert data["is_useful"] is True
    assert set(data["useful_aspects"]) == {"similar_time", "similar_location", "similar_property"}
    assert "not currently utilized for automatic model retraining" in data["disclaimer"]


def test_submit_negative_feedback(client):
    """Test submitting negative feedback with operational notes."""
    payload = {
        "is_useful": False,
        "target_type": "similarity_match",
        "target_id": "INC_099123",
        "useful_aspects": ["other"],
        "notes": "Weapon context differed significantly."
    }
    res = client.post("/api/feedback", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "received"
    assert data["is_useful"] is False
    assert data["useful_aspects"] == ["other"]


def test_aspects_sanitization(client):
    """Test that unauthorized aspect keys are safely filtered out."""
    payload = {
        "is_useful": True,
        "useful_aspects": ["similar_method", "INVALID_ASPECT_KEY", "similar_time", "hack_attempt"]
    }
    res = client.post("/api/feedback", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Only similar_method and similar_time should be retained
    assert set(data["useful_aspects"]) == {"similar_method", "similar_time"}


def test_feedback_summary_statistics(client):
    """Test retrieving aggregated feedback metrics and breakdowns."""
    res = client.get("/api/feedback/summary")
    assert res.status_code == 200
    data = res.json()

    assert data["total_feedback_count"] >= 3
    assert data["useful_count"] >= 2
    assert 0.0 <= data["useful_percentage"] <= 100.0
    assert "similar_time" in data["aspects_breakdown"]
    assert "similar_location" in data["aspects_breakdown"]
    assert "similar_property" in data["aspects_breakdown"]
    assert "similar_method" in data["aspects_breakdown"]
    assert "other" in data["aspects_breakdown"]
    assert "not currently utilized for automatic model retraining" in data["disclaimer"]
    assert len(data["recent_feedback"]) >= 1


def test_storage_files_integrity():
    """Verify that SQLite and JSONL files exist and contain audit logs."""
    assert DB_PATH.exists()
    assert JSONL_PATH.exists()

    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) >= 3

    last_record = json.loads(lines[-1])
    assert "feedback_id" in last_record
    assert "created_at" in last_record
    assert "is_useful" in last_record
