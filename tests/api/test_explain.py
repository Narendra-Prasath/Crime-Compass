"""
CRIME DNA — API Tests: Similarity Explainability Endpoints
"""

def test_explain_pair_get_success(client):
    response = client.get("/api/explain/INC_136975/INC_145291")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_pair"] == ["INC_136975", "INC_145291"]
    assert 0.0 <= data["similarity_score_pct"] <= 100.0
    assert 0.0 <= data["cosine_similarity_raw"] <= 1.0

    # Main contributing similarities and differences
    assert len(data["main_contributing_similarities"]) > 0
    assert len(data["differences"]) > 0

    # Group contributions
    groups = data["group_contributions"]
    assert len(groups) == 7
    total_pct = sum(g["percentage_of_similarity"] for g in groups)
    assert round(total_pct, 0) == 100.0

    # Top contributing features
    top_features = data["top_contributing_features"]
    assert len(top_features) > 0
    assert all("feature_name" in f and "contribution" in f for f in top_features)

    # Formatted template text check
    summary_text = data["formatted_text_summary"]
    assert "Similarity Score:" in summary_text
    assert "Main contributing similarities:" in summary_text
    assert "Differences:" in summary_text

    # Disclaimer check
    assert "causal relationships" in data["disclaimer"]


def test_explain_pair_post_success(client):
    payload = {
        "incident_id_1": "INC_136975",
        "incident_id_2": "INC_145291"
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["incident_pair"] == ["INC_136975", "INC_145291"]
    assert "Similarity Score:" in data["formatted_text_summary"]


def test_explain_pair_not_found(client):
    response = client.get("/api/explain/INC_136975/INC_FAKE_999999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "IncidentNotFoundError"
