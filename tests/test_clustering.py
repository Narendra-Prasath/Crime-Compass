"""
Unit and Integration Tests for CRIME DNA Phase 6 Behavioral Clustering Engine
"""

import os
import shutil
import unittest
import numpy as np
import pandas as pd

from src.models.clustering.engine import BehavioralClusterer
from src.models.clustering.config import CLUSTERS_DIR, CLUSTER_ARCHETYPES


class TestBehavioralClusterer(unittest.TestCase):
    """Unit tests for the Behavioral Clustering pipeline."""

    @classmethod
    def setUpClass(cls):
        """Create mock Behavioral DNA dataset and fit test clusterer."""
        cls.test_dir = "tests/test_clustering_artifacts"
        os.makedirs(cls.test_dir, exist_ok=True)

        # 30 mock incidents across 70 features
        np.random.seed(42)
        n_incidents = 30
        dim = 70
        features = np.random.uniform(0.0, 1.0, size=(n_incidents, dim)).astype(np.float32)
        incident_ids = [f"TEST_INC_{i+1:03d}" for i in range(n_incidents)]

        import json
        with open("data/processed/behavioral_dna_feature_names.json") as f:
            feature_names = json.load(f)

        cls.mock_df = pd.DataFrame(features, columns=feature_names)
        cls.mock_df.insert(0, "incident_id", incident_ids)
        cls.mock_csv_path = os.path.join(cls.test_dir, "mock_features.csv")
        cls.mock_df.to_csv(cls.mock_csv_path, index=False)

        cls.clusterer = BehavioralClusterer({"n_clusters": 4, "batch_size": 16, "random_state": 42, "n_init": 2, "max_iter": 50})
        cls.clusterer.fit(cls.mock_csv_path, n_clusters=4)

    @classmethod
    def tearDownClass(cls):
        """Clean up test artifacts."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_fit_and_profiles(self):
        """Verify clusterer produces correct number of clusters and profiles."""
        self.assertEqual(len(self.clusterer.cluster_profiles), 4)
        for cl_id, profile in self.clusterer.cluster_profiles.items():
            self.assertIn("name", profile)
            self.assertIn("dominant_patterns", profile)
            self.assertIn("top_distinctive_features", profile)

    def test_save_and_load(self):
        """Verify model serialization and deserialization."""
        save_path = os.path.join(self.test_dir, "saved_clusterer")
        self.clusterer.save(save_path)

        loaded = BehavioralClusterer()
        loaded.load(save_path)
        self.assertEqual(len(loaded.cluster_profiles), 4)

    def test_predict_single_vector(self):
        """Verify predicting cluster assignment for a single vector."""
        vec = np.random.uniform(0.0, 1.0, size=(70,)).astype(np.float32)
        res = self.clusterer.predict_cluster(vec)
        self.assertIn("assigned_cluster_id", res)
        self.assertIn(res["assigned_cluster_id"], range(4))
        self.assertGreaterEqual(res["distance_to_centroid"], 0.0)


class TestProductionClusterIntegrity(unittest.TestCase):
    """Integration test verifying precomputed production cluster files."""

    def test_production_artifacts_exist(self):
        """Verify production clustering model, labels, and profiles exist."""
        clusterer = BehavioralClusterer()
        clusterer.load(CLUSTERS_DIR)

        self.assertEqual(len(clusterer.cluster_profiles), 8)
        self.assertIn("silhouette_cosine", clusterer.evaluation_metrics)
        self.assertGreater(clusterer.evaluation_metrics["silhouette_cosine"], 0.15)

        # Check labels file
        labels_df = pd.read_csv(os.path.join(CLUSTERS_DIR, "incident_cluster_labels.csv"))
        self.assertEqual(len(labels_df), 220663)
        self.assertEqual(labels_df["cluster_id"].nunique(), 8)


if __name__ == "__main__":
    unittest.main()
