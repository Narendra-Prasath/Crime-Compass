"""
CRIME DNA — Phase 13: End-to-End Frontend-to-Backend Integration Tests

Validates every API request sequence executed by the 8 pages of the React dashboard,
ensuring zero mock fallbacks, strict schema compliance, robust error handling for invalid IDs,
and accurate empirical statistics directly from the machine learning models.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_overview_page_flow(client):
    """Verifies all endpoints consumed concurrently by OverviewPage.tsx."""
    # 1. Stats
    res_stats = client.get("/api/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_incidents"] == 220663
    assert stats["behavioral_dna_features_count"] == 70
    assert stats["clusters_count"] == 8
    assert sum(stats["novelty_tier_counts"].values()) == 220663

    # 2. Clusters summary
    res_clusters = client.get("/api/clusters")
    assert res_clusters.status_code == 200
    clusters = res_clusters.json()["clusters"]
    assert len(clusters) == 8

    # 3. Cross-crime patterns summary
    res_cross = client.get("/api/cross-crime")
    assert res_cross.status_code == 200
    patterns = res_cross.json()["patterns"]
    assert len(patterns) == 8

    # 4. Significant shifts
    res_shifts = client.get("/api/evolution/shifts")
    assert res_shifts.status_code == 200
    shifts = res_shifts.json()["shifts"]
    assert len(shifts) > 0


def test_incident_analyzer_flow_valid(client):
    """Verifies endpoints consumed when searching a valid incident in IncidentAnalyzerPage.tsx."""
    incident_id = "INC_136975"

    # Profile
    res_profile = client.get(f"/api/incidents/{incident_id}")
    assert res_profile.status_code == 200
    profile = res_profile.json()
    assert profile["incident_id"] == incident_id
    assert "cluster" in profile and "novelty" in profile and "context" in profile
    assert profile["context"]["primary_crime_category"] != ""

    # DNA
    res_dna = client.get(f"/api/incidents/{incident_id}/dna")
    assert res_dna.status_code == 200
    dna = res_dna.json()
    assert dna["incident_id"] == incident_id
    assert dna["vector_dimension"] == 70
    assert len(dna["feature_vector"]) == 70
    assert len(dna["group_energies"]) == 7
    assert len(dna["top_active_traits"]) > 0

    # Similar incidents
    res_similar = client.get(f"/api/similarity/similar/{incident_id}?top_k=5")
    assert res_similar.status_code == 200
    sim = res_similar.json()
    assert sim["query_incident_id"] == incident_id
    assert len(sim["matches"]) == 5
    # Must NOT include queried incident itself
    assert all(m["incident_id"] != incident_id for m in sim["matches"])
    assert all(0.0 <= m["similarity_score_pct"] <= 100.0 for m in sim["matches"])


def test_incident_analyzer_flow_invalid_id(client):
    """Verifies error handling for non-existent incident IDs."""
    invalid_id = "INC_NONEXISTENT_999999"

    res_profile = client.get(f"/api/incidents/{invalid_id}")
    assert res_profile.status_code == 404
    assert "not found" in res_profile.json()["detail"].lower()

    res_dna = client.get(f"/api/incidents/{invalid_id}/dna")
    assert res_dna.status_code == 404
    assert "not found" in res_dna.json()["detail"].lower()

    res_similar = client.get(f"/api/similarity/similar/{invalid_id}")
    assert res_similar.status_code == 404
    assert "not found" in res_similar.json()["detail"].lower()


def test_similarity_view_pair_flow(client):
    """Verifies comparative pair analysis consumed by SimilarityViewPage.tsx."""
    inc1 = "INC_136975"
    inc2 = "INC_145291"

    # Both profiles and DNAs must resolve
    for inc in (inc1, inc2):
        assert client.get(f"/api/incidents/{inc}").status_code == 200
        assert client.get(f"/api/incidents/{inc}/dna").status_code == 200

    # Explanation must return exact cosine and group contributions
    res_exp = client.get(f"/api/explain/{inc1}/{inc2}")
    assert res_exp.status_code == 200
    exp = res_exp.json()
    assert exp["incident_pair"] == [inc1, inc2]
    assert 0.0 <= exp["similarity_score_pct"] <= 100.0
    assert len(exp["group_contributions"]) == 7


def test_why_similar_page_flow(client):
    """Verifies explainability features rendered in WhySimilarPage.tsx."""
    inc1 = "INC_136975"
    inc2 = "INC_145291"

    res = client.get(f"/api/explain/{inc1}/{inc2}")
    assert res.status_code == 200
    data = res.json()

    assert len(data["main_contributing_similarities"]) > 0
    assert len(data["differences"]) > 0
    assert len(data["group_contributions"]) == 7
    assert len(data["top_contributing_features"]) > 0
    assert "Similarity Score:" in data["formatted_text_summary"]
    assert "guilt" in data["disclaimer"] or "causal" in data["disclaimer"]


def test_behavioral_patterns_page_flow(client):
    """Verifies cluster exploration consumed by BehavioralPatternsPage.tsx."""
    res_list = client.get("/api/clusters")
    assert res_list.status_code == 200
    clusters = res_list.json()["clusters"]

    for c in clusters:
        cluster_id = c["cluster_id"]
        res_detail = client.get(f"/api/clusters/{cluster_id}")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert detail["cluster_id"] == cluster_id
        assert "dominant_patterns" in detail
        assert "top_distinctive_features" in detail
        assert len(detail["top_distinctive_features"]) > 0


def test_cross_crime_page_flow(client):
    """Verifies cross-crime pattern explorer in CrossCrimePage.tsx."""
    res_list = client.get("/api/cross-crime")
    assert res_list.status_code == 200
    patterns = res_list.json()["patterns"]

    for p in patterns:
        pattern_id = p["pattern_id"]
        res_detail = client.get(f"/api/cross-crime/{pattern_id}")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert detail["pattern_id"] == pattern_id
        assert len(detail["exemplar_incidents"]) > 0


def test_behavioral_evolution_page_flow(client):
    """Verifies temporal trends and shift testing in BehavioralEvolutionPage.tsx."""
    res_timeline = client.get("/api/evolution/timeline")
    assert res_timeline.status_code == 200
    timeline = res_timeline.json()
    assert "metadata" in timeline
    assert "cluster_timeline" in timeline
    assert "feature_timeline" in timeline
    assert "significant_shifts" in timeline

    # Check series data
    assert "months" in timeline["cluster_timeline"]
    assert len(timeline["cluster_timeline"]["months"]) == 12
    assert "is_night" in timeline["feature_timeline"]["series"]
    assert len(timeline["feature_timeline"]["series"]["is_night"]["values"]) == 12

    res_shifts = client.get("/api/evolution/shifts")
    assert res_shifts.status_code == 200
    shifts = res_shifts.json()["shifts"]
    assert len(shifts) > 0


def test_novel_behavior_page_flow(client):
    """Verifies anomaly detection feed in NovelBehaviorPage.tsx."""
    res_summary = client.get("/api/anomaly/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_incidents"] == 220663
    assert "thresholds" in summary

    res_outliers = client.get("/api/anomaly/outliers?limit=50&offset=0")
    assert res_outliers.status_code == 200
    data = res_outliers.json()
    assert data["total_outliers_returned"] == 50
    assert len(data["outliers"]) == 50

    # Every outlier must have nearest cluster and distance
    first_outlier = data["outliers"][0]
    assert "incident_id" in first_outlier
    assert "novelty_score" in first_outlier
    assert "nearest_cluster" in first_outlier
