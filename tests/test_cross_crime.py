"""
Unit and Integration Tests for CRIME DNA Phase 7 Cross-Crime Pattern Analysis
"""

import os
import json
import unittest
import numpy as np
import pandas as pd

from src.models.cross_crime.analyzer import CrossCrimeAnalyzer
from src.models.cross_crime.config import (
    CROSS_CRIME_DIR,
    PATTERNS_JSON_PATH,
    SUMMARY_JSON_PATH,
    MATRIX_CHART_PATH
)


class TestCrossCrimeAnalyzer(unittest.TestCase):
    """Unit tests for the Cross-Crime Pattern Analyzer pipeline."""

    def test_production_artifacts_exist(self):
        """Verify that precomputed production cross-crime artifacts exist and are non-empty."""
        self.assertTrue(os.path.exists(PATTERNS_JSON_PATH), f"Missing {PATTERNS_JSON_PATH}")
        self.assertTrue(os.path.exists(SUMMARY_JSON_PATH), f"Missing {SUMMARY_JSON_PATH}")
        self.assertTrue(os.path.exists(MATRIX_CHART_PATH), f"Missing {MATRIX_CHART_PATH}")

        with open(PATTERNS_JSON_PATH) as f:
            patterns = json.load(f)
        with open(SUMMARY_JSON_PATH) as f:
            summary = json.load(f)

        self.assertEqual(len(patterns), 8)
        self.assertEqual(len(summary), 8)

        total_incidents = sum(p["total_incidents"] for p in summary)
        self.assertEqual(total_incidents, 220663)

    def test_pattern_schema_and_cross_crime_evidence(self):
        """Verify that each pattern contains rigorous evidence and schema compliance."""
        with open(PATTERNS_JSON_PATH) as f:
            patterns = json.load(f)

        for pid, pattern in patterns.items():
            self.assertIn("pattern_id", pattern)
            self.assertIn("categories_represented", pattern)
            self.assertIn("dominant_behavioral_characteristics", pattern)
            self.assertIn("exemplar_incidents", pattern)
            self.assertIn("cross_crime_evidence", pattern)

            # Validate evidence
            evidence = pattern["cross_crime_evidence"]
            self.assertIn("categories_count", evidence)
            self.assertGreaterEqual(evidence["categories_count"], 2)
            self.assertIn("avg_inter_category_cosine_similarity", evidence)
            self.assertGreater(evidence["avg_inter_category_cosine_similarity"], 0.65)
            self.assertIn("shared_behavior_rationale", evidence)

            # Validate exemplars
            exemplars = pattern["exemplar_incidents"]
            self.assertGreaterEqual(len(exemplars), 2)
            for ex in exemplars:
                self.assertIn("incident_id", ex)
                self.assertIn("crime_category", ex)
                self.assertIn("incident_hour", ex)
                self.assertIn("has_weapon", ex)

    def test_cross_crime_incident_counts_positive(self):
        """Verify all clusters exhibit genuine cross-crime incident presence."""
        with open(SUMMARY_JSON_PATH) as f:
            summary = json.load(f)

        total_cross_crime = sum(p["cross_crime_incidents"] for p in summary)
        self.assertGreater(total_cross_crime, 8000)

        for p in summary:
            self.assertGreater(p["cross_crime_incidents"], 100)
            self.assertGreater(len(p["secondary_categories"]), 0)


if __name__ == "__main__":
    unittest.main()
