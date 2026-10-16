"""
CRIME DNA — API Tests: Incident Lookup and Behavioral DNA
"""

def test_get_incident_profile_success(client):
    response = client.get("/api/incidents/INC_136975")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "INC_136975"

    # Cluster verification
    cluster = data["cluster"]
    assert "cluster_id" in cluster
    assert "cluster_name" in cluster
    assert 0 <= cluster["cluster_id"] <= 7

    # Novelty verification
    novelty = data["novelty"]
    assert "novelty_score" in novelty
    assert "novelty_tier" in novelty
    assert 0.0 <= novelty["novelty_score"] <= 1.0

    # Context verification
    ctx = data["context"]
    assert "incident_hour" in ctx
    assert "is_night" in ctx
    assert "is_weekend" in ctx
    assert "primary_crime_category" in ctx


def test_get_incident_profile_not_found(client):
    response = client.get("/api/incidents/INC_NONEXISTENT_999999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "IncidentNotFoundError"
    assert "INC_NONEXISTENT_999999" in data["detail"]


def test_get_incident_dna_success(client):
    response = client.get("/api/incidents/INC_136975/dna")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "INC_136975"
    assert data["vector_dimension"] == 70

    # Feature vector checks
    vec = data["feature_vector"]
    assert len(vec) == 70
    assert "time_hour_sin" in vec
    assert "time_hour_cos" in vec

    # Group energies
    energies = data["group_energies"]
    assert len(energies) == 7
    assert "temporal_dynamics" in energies
    assert "crime_characteristics" in energies

    # Top active traits
    traits = data["top_active_traits"]
    assert len(traits) > 0
    assert all("feature" in t and "value" in t for t in traits)


def test_get_incident_dna_not_found(client):
    response = client.get("/api/incidents/INC_DOES_NOT_EXIST/dna")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "IncidentNotFoundError"
