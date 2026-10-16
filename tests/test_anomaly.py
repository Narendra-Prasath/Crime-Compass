"""
Unit and Integration Tests for CRIME DNA Phase 9 Behavioral Anomaly & Novelty Detection
"""

import os
import json
import unittest
import numpy as np
import pandas as pd

from src.models.anomaly.detector import BehavioralAnomalyDetector
from src.models.anomaly.config import (
    ANOMALY_DIR,
    MODEL_PATH,
    SCORES_CSV_PATH,
    TOP_OUTLIERS_JSON_PATH,
    ANOMALY_SUMMARY_PATH,
    ANOMALY_CHART_PATH,
    ANOMALY_TIER_LABELS
)


class TestBehavioralAnomalyDetector(unittest.TestCase):
    """Unit and integration tests for Phase 9 anomaly and novelty detection."""

    def test_production_artifacts_exist(self):
        """Verify all precomputed production anomaly artifacts exist on disk."""
        self.assertTrue(os.path.exists(MODEL_PATH), f"Missing {MODEL_PATH}")
        self.assertTrue(os.path.exists(SCORES_CSV_PATH), f"Missing {SCORES_CSV_PATH}")
        self.assertTrue(os.path.exists(TOP_OUTLIERS_JSON_PATH), f"Missing {TOP_OUTLIERS_JSON_PATH}")
        self.assertTrue(os.path.exists(ANOMALY_SUMMARY_PATH), f"Missing {ANOMALY_SUMMARY_PATH}")
        self.assertTrue(os.path.exists(ANOMALY_CHART_PATH), f"Missing {ANOMALY_CHART_PATH}")

    def test_scores_dataframe_integrity(self):
        """Verify anomaly scores CSV has 220,663 records with valid score bounds."""
        df = pd.read_csv(SCORES_CSV_PATH)
        self.assertEqual(len(df), 220663)

        expected_cols = [
            "incident_id", "novelty_score", "novelty_tier",
            "nearest_cluster_id", "nearest_cluster_name", "distance_to_nearest_cluster",
            "second_nearest_cluster_id", "second_nearest_cluster_name",
            "distance_to_second_cluster", "isolation_forest_raw_score"
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns)

        # Check score bounds
        self.assertGreaterEqual(df["novelty_score"].min(), 0.0)
        self.assertLessEqual(df["novelty_score"].max(), 1.0)
        self.assertGreaterEqual(df["distance_to_nearest_cluster"].min(), 0.0)

    def test_threshold_quantiles_and_tier_proportions(self):
        """Verify threshold calibration follows the exact 95% / 99% empirical quantiles."""
        with open(ANOMALY_SUMMARY_PATH) as f:
            metadata = json.load(f)

        self.assertIn("thresholds", metadata)
        self.assertIn("tier_counts", metadata)

        tiers = metadata["tier_counts"]
        total = metadata["total_incidents"]
        self.assertEqual(total, 220663)

        high_count = tiers[ANOMALY_TIER_LABELS["high"]]
        mod_count = tiers[ANOMALY_TIER_LABELS["moderate"]]
        std_count = tiers[ANOMALY_TIER_LABELS["standard"]]

        # 99th percentile => ~1% (approx 2,207)
        self.assertAlmostEqual(high_count / total, 0.01, places=2)
        # 95th percentile => ~4% moderate + 1% high = 5%
        self.assertAlmostEqual(mod_count / total, 0.04, places=2)
        self.assertAlmostEqual(std_count / total, 0.95, places=2)

    def test_top_outliers_schema_and_explanations(self):
        """Verify top outliers JSON schema contains feature deviation explanations."""
        with open(TOP_OUTLIERS_JSON_PATH) as f:
            outliers = json.load(f)

        self.assertGreaterEqual(len(outliers), 50)
        for out in outliers[:10]:
            self.assertIn("incident_id", out)
            self.assertIn("novelty_score", out)
            self.assertIn("novelty_tier", out)
            self.assertIn("nearest_cluster", out)
            self.assertIn("unusual_features", out)

            unusual = out["unusual_features"]
            self.assertGreaterEqual(len(unusual), 3)
            for feat in unusual:
                self.assertIn("feature_name", feat)
                self.assertIn("incident_value", feat)
                self.assertIn("cluster_centroid_value", feat)
                self.assertIn("deviation_delta", feat)
                self.assertIn("direction", feat)

    def test_explain_incident_lookup(self):
        """Verify explain_incident provides exact attribute breakdown."""
        detector = BehavioralAnomalyDetector()
        detector.scores_df = pd.read_csv(SCORES_CSV_PATH)
        detector.incident_ids = detector.scores_df["incident_id"].tolist()
        with open(TOP_OUTLIERS_JSON_PATH) as f:
            detector.top_outliers = json.load(f)

        top_id = detector.top_outliers[0]["incident_id"]
        explanation = detector.explain_incident(top_id)

        self.assertEqual(explanation["incident_id"], top_id)
        self.assertIn("novelty_score", explanation)
        self.assertIn("unusual_features", explanation)

        # Invalid ID should raise KeyError
        with self.assertRaises(KeyError):
            detector.explain_incident("INVALID_INCIDENT_999999")


if __name__ == "__main__":
    unittest.main()
