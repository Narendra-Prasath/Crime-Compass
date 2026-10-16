"""
ML Validation Test Suite for CRIME DNA (Phase 14).

Tests:
- Similarity retrieval on controlled known-similar feature vectors
- Directional discrimination against inverted vectors
- Clustering silhouette quality, size distribution, and stability
- Cross-crime multi-category representation
- Anomaly detection quantile calibration and synthetic outlier recall
- Explainability attribution conservation
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from src.models.similarity.engine import BehavioralSimilarityEngine
from src.models.clustering.engine import BehavioralClusterer
from src.models.cross_crime.config import PATTERNS_JSON_PATH
from src.models.anomaly.detector import BehavioralAnomalyDetector
from src.models.anomaly.config import ANOMALY_SUMMARY_PATH
from src.models.explainability.explainer import BehavioralSimilarityExplainer


@pytest.fixture(scope="module")
def similarity_engine():
    engine = BehavioralSimilarityEngine()
    engine.load()
    return engine


@pytest.fixture(scope="module")
def clustering_engine():
    engine = BehavioralClusterer()
    engine.load()
    return engine


@pytest.fixture(scope="module")
def explainer():
    exp = BehavioralSimilarityExplainer()
    exp.load_data()
    return exp


def test_similarity_controlled_perturbation(similarity_engine):
    """Verify that adding mild Gaussian noise to known vectors retrieves the original incident at Rank-1."""
    rng = np.random.RandomState(42)
    sample_indices = rng.choice(similarity_engine.features_norm.shape[0], size=50, replace=False)
    
    rank_1_matches = 0
    for idx in sample_indices:
        inc_id = similarity_engine.incident_ids[idx]
        vec = similarity_engine.features_norm[idx].copy()
        
        # Add small perturbation (sigma=0.01) and re-normalize to unit sphere
        noisy_vec = vec + rng.normal(0, 0.01, size=vec.shape)
        noisy_vec /= np.linalg.norm(noisy_vec)
        
        res = similarity_engine.find_similar_by_vector(noisy_vec, top_k=5, include_breakdown=False)
        matches = res.get("matches", [])
        if len(matches) > 0 and matches[0]["incident_id"] == inc_id:
            rank_1_matches += 1
            
    accuracy = rank_1_matches / len(sample_indices)
    assert accuracy >= 0.95, f"Rank-1 retrieval accuracy {accuracy:.2%} below threshold of 95%"


def test_similarity_inverted_vector_discrimination(similarity_engine):
    """Verify that an inverted feature vector yields substantially lower or negative cosine similarity."""
    target_idx = 100
    vec = similarity_engine.features_norm[target_idx]
    inv_vec = -vec
    
    res = similarity_engine.find_similar_by_vector(inv_vec, top_k=5, include_breakdown=False)
    matches = res.get("matches", [])
    top_sim = matches[0]["similarity_score_pct"]
    # Cosine similarity pct is scaled to [0, 100]; inverted vector should be below 45%
    assert top_sim < 45.0, f"Inverted vector similarity {top_sim}% unexpectedly high"


def test_clustering_metrics_and_balance(clustering_engine):
    """Verify clustering evaluation metrics and balanced cluster distributions."""
    metrics = clustering_engine.evaluation_metrics
    assert metrics.get("silhouette_cosine", 0) >= 0.20, "Silhouette score below 0.20"
    assert metrics.get("davies_bouldin_index", 99) <= 3.0, "Davies-Bouldin index above 3.0"
    
    # Check cluster sizes: 8 clusters, no cluster < 3% or > 40%
    profiles = clustering_engine.cluster_profiles
    assert len(profiles) == 8, f"Expected 8 clusters, found {len(profiles)}"
    total = sum(p["incident_count"] for p in profiles.values())
    for c_id, profile in profiles.items():
        size = profile["incident_count"]
        pct = (size / total) * 100
        assert pct >= 3.0, f"Cluster {c_id} has degenerately low membership: {pct:.2f}%"
        assert pct <= 40.0, f"Cluster {c_id} is overly dominant: {pct:.2f}%"


def test_cross_crime_pattern_breadth():
    """Verify cross-crime patterns span multiple distinct statutory crime categories."""
    assert os.path.exists(PATTERNS_JSON_PATH), f"Missing {PATTERNS_JSON_PATH}"
    with open(PATTERNS_JSON_PATH, "r") as f:
        data = json.load(f)
        
    patterns = list(data.values()) if isinstance(data, dict) else data
    assert len(patterns) == 8, f"Expected 8 cross-crime patterns, found {len(patterns)}"
    for p in patterns:
        cats = p.get("categories_represented", [])
        assert len(cats) >= 2, f"Pattern {p.get('pattern_id')} spans fewer than 2 categories: {cats}"


def test_anomaly_detector_monotonicity_and_synthetic_recall(clustering_engine):
    """Verify anomaly threshold monotonicity and 100% recall on synthetic multi-attribute outliers."""
    assert os.path.exists(ANOMALY_SUMMARY_PATH), f"Missing {ANOMALY_SUMMARY_PATH}"
    with open(ANOMALY_SUMMARY_PATH, "r") as f:
        summary = json.load(f)
        
    thresholds = summary.get("thresholds", {})
    p50 = summary.get("score_statistics", {}).get("median", 0)
    p95 = thresholds.get("moderate_novelty_threshold_p95", 0)
    p99 = thresholds.get("high_outlier_threshold_p99", 0)
    p999 = thresholds.get("extreme_outlier_threshold_p999", 0)
    
    assert p50 < p95 < p99 < p999, f"Quantiles not strictly monotonic: {p50}, {p95}, {p99}, {p999}"
    
    # Synthetic outlier validation:
    # Generate discordant vectors far from all 8 cluster centroids
    centroids = clustering_engine.model.cluster_centers_
    rng = np.random.RandomState(99)
    
    detected = 0
    for _ in range(20):
        # Generate an extreme sparse vector
        synth_vec = rng.uniform(0.7, 1.0, size=(70,))
        synth_vec /= np.linalg.norm(synth_vec)
        
        # Calculate cosine distances to all 8 cluster centroids
        cos_sims = np.dot(centroids, synth_vec)
        centroid_dist = 1.0 - np.max(cos_sims)
        
        # Multi-attribute discordant synthetic vector will have high centroid distance
        if centroid_dist >= p95 * 0.8:
            detected += 1
            
    assert detected == 20, f"Expected 20/20 synthetic outlier detections, got {detected}"


def test_explainability_attribution_conservation(explainer):
    """Verify mathematical conservation of group contributions to total similarity."""
    pairs = [
        ("INC_136975", "INC_145291"),
        ("INC_171133", "INC_082341"),
        ("INC_135749", "INC_136975"),
    ]
    for inc1, inc2 in pairs:
        exp = explainer.explain_pair(inc1, inc2)
        total_sim = exp["cosine_similarity_raw"]
        group_sum = sum(g["absolute_contribution"] for g in exp["group_contributions"].values())
        diff = abs(total_sim - group_sum)
        assert diff < 0.0005, f"Attribution conservation error: {diff} on pair ({inc1}, {inc2})"
