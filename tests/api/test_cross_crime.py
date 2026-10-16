"""
CRIME DNA — API Tests: Cross-Crime Behavioral Patterns
"""

def test_list_cross_crime_patterns(client):
    response = client.get("/api/cross-crime")
    assert response.status_code == 200
    data = response.json()
    assert data["total_patterns"] == 8
    patterns = data["patterns"]
    assert len(patterns) == 8

    # Check pattern summary
    p0 = patterns[0]
    assert p0["pattern_id"] == "CCP_00"
    assert "categories_represented" in p0
    assert len(p0["categories_represented"]) >= 2


def test_get_cross_crime_detail_success(client):
    response = client.get("/api/cross-crime/CCP_00")
    assert response.status_code == 200
    data = response.json()
    assert data["pattern_id"] == "CCP_00"
    assert data["cluster_id"] == 0
    assert data["total_incidents"] > 0

    # Cross-crime categories
    cats = data["categories_represented"]
    assert len(cats) >= 2

    # Exemplars
    exemplars = data["exemplar_incidents"]
    assert len(exemplars) >= 2
    for e in exemplars:
        assert "incident_id" in e
        assert "crime_category" in e

    # Pairwise similarities
    similarities = data["exemplar_pairwise_similarities"]
    assert len(similarities) > 0


def test_get_cross_crime_detail_not_found(client):
    response = client.get("/api/cross-crime/CCP_INVALID_99")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "PatternNotFoundError"
