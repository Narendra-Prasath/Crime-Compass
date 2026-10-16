"""
CRIME DNA — API Tests: Novel Behavioral Patterns (Anomaly Detection)
"""

def test_get_anomaly_summary(client):
    response = client.get("/api/anomaly/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_incidents"] == 220663
    assert "Isolation Forest" in data["algorithm"]
    assert "thresholds" in data
    assert "tier_counts" in data

    stats = data["score_statistics"]
    assert 0.0 <= stats["min"] <= stats["mean"] <= stats["max"] <= 1.0


def test_get_top_outliers(client):
    response = client.get("/api/anomaly/outliers?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total_outliers_returned"] == 10
    outliers = data["outliers"]
    assert len(outliers) == 10

    first = outliers[0]
    assert "incident_id" in first
    assert "novelty_score" in first
    assert "unusual_features" in first
    assert len(first["unusual_features"]) > 0


def test_get_incident_anomaly_success(client):
    response = client.get("/api/anomaly/INC_136975")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "INC_136975"
    assert "novelty_score" in data
    assert "novelty_tier" in data
    assert "nearest_cluster_name" in data


def test_get_incident_anomaly_not_found(client):
    response = client.get("/api/anomaly/INC_DOES_NOT_EXIST")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "IncidentNotFoundError"
