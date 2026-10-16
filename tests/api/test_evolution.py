"""
CRIME DNA — API Tests: Behavioral Evolution Endpoints
"""

def test_get_evolution_timeline(client):
    response = client.get("/api/evolution/timeline")
    assert response.status_code == 200
    data = response.json()

    assert "metadata" in data
    assert "cluster_timeline" in data
    assert "feature_timeline" in data
    assert "significant_shifts" in data

    shifts = data["significant_shifts"]
    assert len(shifts) >= 4
    for s in shifts:
        assert "shift_id" in s
        assert "statistical_significance" in s


def test_get_significant_shifts(client):
    response = client.get("/api/evolution/shifts")
    assert response.status_code == 200
    data = response.json()
    assert data["total_shifts"] >= 4
    shifts = data["shifts"]
    assert len(shifts) >= 4

    first = shifts[0]
    assert first["shift_id"] == "SHIFT_01"
    assert "Temporal Dynamics" in first["domain"]
    assert "p < 0.001" in first["statistical_significance"]
