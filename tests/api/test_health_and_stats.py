"""
CRIME DNA — API Tests: Health Check and Dataset Statistics
"""

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "/docs" in data["documentation"]
    assert len(data["endpoints"]) >= 10


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["indexed_incidents"] == 220663
    assert data["vector_dimension"] == 70
    assert data["uptime_seconds"] >= 0.0

    # Ensure all pipeline components are reported online
    components = data["components_status"]
    assert components["similarity_engine"] == "online"
    assert components["clustering"] == "online"
    assert components["cross_crime"] == "online"
    assert components["evolution"] == "online"
    assert components["anomaly_detection"] == "online"
    assert components["explainability"] == "online"
    assert components["incident_registry"] == "online"


def test_dataset_stats(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_incidents"] == 220663
    assert data["cleaned_features_count"] == 196
    assert data["behavioral_dna_features_count"] == 70
    assert data["clusters_count"] == 8
    assert data["cross_crime_patterns_count"] == 8

    # Taxonomy counts
    taxonomy = data["feature_taxonomy_counts"]
    assert "temporal_features" in taxonomy
    assert "victimology_demographics" in taxonomy
    assert "weapon_violence_features" in taxonomy

    # Novelty tier distribution
    tier_counts = data["novelty_tier_counts"]
    assert "Standard Behavioral Pattern" in tier_counts
    assert "High Behavioral Outlier" in tier_counts or "Extreme Outlier" in tier_counts
    assert tier_counts["Standard Behavioral Pattern"] > 200000
