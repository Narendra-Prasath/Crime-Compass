"""
CRIME DNA — API Tests: Behavioral Clustering Endpoints
"""

def test_list_clusters(client):
    response = client.get("/api/clusters")
    assert response.status_code == 200
    data = response.json()
    assert data["total_clusters"] == 8
    clusters = data["clusters"]
    assert len(clusters) == 8

    # Validate schema of cluster summaries
    for c in clusters:
        assert "cluster_id" in c
        assert "name" in c
        assert "macro_category" in c
        assert "summary" in c
        assert c["incident_count"] > 0
        assert c["percentage_of_total"] > 0.0


def test_get_cluster_detail_success(client):
    response = client.get("/api/clusters/0")
    assert response.status_code == 200
    data = response.json()
    assert data["cluster_id"] == 0
    assert "Small-City" in data["name"]
    assert data["macro_category"] == "Property"

    # Dominant patterns
    dom = data["dominant_patterns"]
    assert isinstance(dom, dict)
    assert len(dom) > 0

    # Top distinctive features
    features = data["top_distinctive_features"]
    assert len(features) > 0
    first_feat = features[0]
    assert "feature" in first_feat
    assert "cluster_mean" in first_feat
    assert "global_mean" in first_feat


def test_get_cluster_detail_invalid_id(client):
    # Cluster 99 is out of range 0..7
    response = client.get("/api/clusters/99")
    assert response.status_code in (404, 422)
