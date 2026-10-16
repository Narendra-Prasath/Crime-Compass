"""
CRIME DNA — API Tests: Behavioral Similarity Engine
"""

def test_get_similar_incidents_success(client):
    response = client.get("/api/similarity/similar/INC_136975?top_k=5&include_breakdown=true")
    assert response.status_code == 200
    data = response.json()
    assert data["query_incident_id"] == "INC_136975"
    assert data["top_k_requested"] == 5
    assert len(data["matches"]) == 5

    # Self-exclusion check
    match_ids = [m["incident_id"] for m in data["matches"]]
    assert "INC_136975" not in match_ids

    # Ranks & scores
    first = data["matches"][0]
    assert first["rank"] == 1
    assert 0.0 <= first["similarity_score_pct"] <= 100.0
    assert first["cosine_distance"] >= 0.0
    assert first["subprofile_similarity_pct"] is not None
    assert len(first["subprofile_similarity_pct"]) == 7
    assert first["primary_crime_category"] is not None
    assert first["cluster_name"] is not None


def test_post_similar_incidents_success(client):
    payload = {
        "incident_id": "INC_136975",
        "top_k": 3,
        "include_breakdown": True
    }
    response = client.post("/api/similarity/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) == 3
    assert data["matches"][0]["rank"] == 1


def test_similar_incidents_not_found(client):
    response = client.get("/api/similarity/similar/INC_FAKE_ID?top_k=5")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "IncidentNotFoundError"


def test_vector_similarity_success(client):
    # Valid 70D vector
    vec = [1.0 / (70.0 ** 0.5)] * 70
    payload = {
        "vector": vec,
        "top_k": 4
    }
    response = client.post("/api/similarity/vector", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["top_k_requested"] == 4
    assert len(data["matches"]) == 4
    assert data["matches"][0]["similarity_score_pct"] > 0.0


def test_vector_similarity_invalid_length(client):
    # Vector length 5 instead of 70
    payload = {
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "top_k": 5
    }
    response = client.post("/api/similarity/vector", json=payload)
    assert response.status_code == 422


def test_vector_similarity_zero_norm(client):
    # Zero vector
    payload = {
        "vector": [0.0] * 70,
        "top_k": 5
    }
    response = client.post("/api/similarity/vector", json=payload)
    assert response.status_code == 422
    assert "InvalidVectorError" in response.json()["error"]
