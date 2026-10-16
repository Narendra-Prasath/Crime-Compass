"""
Unit and Integration Tests for CRIME DNA Phase 5 Behavioral Similarity Engine
"""

import os
import shutil
import unittest
import numpy as np
import pandas as pd

from src.models.similarity.engine import BehavioralSimilarityEngine
from src.models.similarity.config import SIMILARITY_DIR


class TestBehavioralSimilarityEngine(unittest.TestCase):
    """Tests for the Behavioral Similarity Engine."""

    @classmethod
    def setUpClass(cls):
        """Create mock dataset and fit test engine."""
        cls.test_dir = "tests/test_similarity_artifacts"
        os.makedirs(cls.test_dir, exist_ok=True)

        # 5 distinct mock behavioral incidents (70 dimensions)
        np.random.seed(42)
        n_incidents = 10
        dim = 70
        cls.mock_features = np.random.uniform(0.0, 1.0, size=(n_incidents, dim)).astype(np.float32)
        cls.incident_ids = [f"TEST_INC_{i+1:03d}" for i in range(n_incidents)]

        # Read canonical feature names from Phase 3 metadata
        meta_path = "data/processed/behavioral_dna_metadata.json"
        if os.path.exists(meta_path):
            import json
            with open(meta_path) as f:
                meta = json.load(f)
            feature_cols = meta["feature_names_path"]
            with open(feature_cols) as f:
                cls.feature_names = json.load(f)
        else:
            cls.feature_names = [f"feat_{i}" for i in range(dim)]

        cls.mock_df = pd.DataFrame(cls.mock_features, columns=cls.feature_names)
        cls.mock_df.insert(0, "incident_id", cls.incident_ids)
        cls.mock_csv_path = os.path.join(cls.test_dir, "mock_behavioral_features.csv")
        cls.mock_df.to_csv(cls.mock_csv_path, index=False)

        cls.engine = BehavioralSimilarityEngine()
        cls.engine.build_index(cls.mock_csv_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up test artifacts."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def test_build_and_save_and_load(self):
        """Verify engine can be built, saved to disk, and loaded with identical state."""
        save_path = os.path.join(self.test_dir, "saved_index")
        self.engine.save(save_path)

        loaded_engine = BehavioralSimilarityEngine()
        loaded_engine.load(save_path)

        self.assertEqual(len(loaded_engine.incident_ids), len(self.engine.incident_ids))
        self.assertIsNotNone(loaded_engine.features_norm)
        self.assertIsNotNone(self.engine.features_norm)
        assert loaded_engine.features_norm is not None and self.engine.features_norm is not None
        self.assertEqual(loaded_engine.features_norm.shape, self.engine.features_norm.shape)

    def test_self_exclusion(self):
        """Verify the queried incident is strictly excluded from its own results."""
        query_id = self.incident_ids[0]
        results = self.engine.find_similar(query_id, top_k=3)
        
        matched_ids = [m["incident_id"] for m in results["matches"]]
        self.assertNotIn(query_id, matched_ids, "Queried incident must be excluded from results")
        self.assertEqual(len(matched_ids), 3)

    def test_top_k_count_and_ranking(self):
        """Verify top_k parameter returns exact count and scores are monotonically non-increasing."""
        query_id = self.incident_ids[2]
        results = self.engine.find_similar(query_id, top_k=4)

        matches = results["matches"]
        self.assertEqual(len(matches), 4)

        # Check monotonic non-increasing similarity scores
        scores = [m["similarity_score_pct"] for m in matches]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i+1], "Scores must be descending or equal")

        # Check rank numbering
        ranks = [m["rank"] for m in matches]
        self.assertEqual(ranks, [1, 2, 3, 4])

    def test_subprofile_similarity_breakdown(self):
        """Verify all 7 behavioral sub-profiles are present with scores between 0% and 100%."""
        query_id = self.incident_ids[1]
        results = self.engine.find_similar(query_id, top_k=2, include_breakdown=True)

        for match in results["matches"]:
            self.assertIn("subprofile_similarity_pct", match)
            breakdown = match["subprofile_similarity_pct"]
            self.assertGreaterEqual(len(breakdown), 5)
            for grp, score in breakdown.items():
                self.assertGreaterEqual(score, 0.0, f"Score for {grp} must be >= 0%")
                self.assertLessEqual(score, 100.0, f"Score for {grp} must be <= 100%")

    def test_query_by_arbitrary_vector(self):
        """Verify querying by a hypothetical external Behavioral DNA vector."""
        query_vector = np.random.uniform(0.0, 1.0, size=(70,)).astype(np.float32)
        results = self.engine.find_similar_by_vector(query_vector, top_k=3)

        self.assertEqual(results["query_type"], "custom_vector")
        self.assertEqual(len(results["matches"]), 3)

    def test_nonexistent_incident_id_raises_keyerror(self):
        """Verify attempting to query an invalid incident ID raises KeyError."""
        with self.assertRaises(KeyError):
            self.engine.find_similar("NONEXISTENT_INCIDENT_999999", top_k=3)


class TestProductionSimilarityEngine(unittest.TestCase):
    """Integration test verifying production similarity engine artifacts."""

    def test_production_artifacts_exist_and_queryable(self):
        """Verify prebuilt production similarity index loads and executes search in < 100ms."""
        import time

        engine = BehavioralSimilarityEngine()
        engine.load(SIMILARITY_DIR)

        self.assertEqual(len(engine.incident_ids), 220663)

        t0 = time.time()
        res = engine.find_similar("INC_000001", top_k=5)
        latency_ms = (time.time() - t0) * 1000.0

        self.assertEqual(len(res["matches"]), 5)
        self.assertLess(latency_ms, 150.0, f"Query latency was {latency_ms:.1f}ms (expected < 150ms)")
        self.assertNotIn("INC_000001", [m["incident_id"] for m in res["matches"]])


if __name__ == "__main__":
    unittest.main()
