"""
Unit and Integration Tests for CRIME DNA Phase 8 Behavioral Pattern Evolution
"""

import os
import json
import unittest
import numpy as np
import pandas as pd

from src.models.evolution.analyzer import BehavioralEvolutionAnalyzer
from src.models.evolution.config import (
    EVOLUTION_DIR,
    TEMPORAL_PROFILES_PATH,
    CLUSTER_EVOLUTION_PATH,
    FEATURE_TRENDS_PATH,
    SIGNIFICANT_SHIFTS_PATH,
    TIMELINE_DASHBOARD_PATH,
    EVOLUTION_CHART_PATH
)


class TestBehavioralEvolution(unittest.TestCase):
    """Unit and integration tests for Phase 8 temporal behavioral evolution analysis."""

    def test_production_artifacts_exist(self):
        """Verify all precomputed evolution artifacts exist on disk."""
        self.assertTrue(os.path.exists(TEMPORAL_PROFILES_PATH), f"Missing {TEMPORAL_PROFILES_PATH}")
        self.assertTrue(os.path.exists(CLUSTER_EVOLUTION_PATH), f"Missing {CLUSTER_EVOLUTION_PATH}")
        self.assertTrue(os.path.exists(FEATURE_TRENDS_PATH), f"Missing {FEATURE_TRENDS_PATH}")
        self.assertTrue(os.path.exists(SIGNIFICANT_SHIFTS_PATH), f"Missing {SIGNIFICANT_SHIFTS_PATH}")
        self.assertTrue(os.path.exists(TIMELINE_DASHBOARD_PATH), f"Missing {TIMELINE_DASHBOARD_PATH}")
        self.assertTrue(os.path.exists(EVOLUTION_CHART_PATH), f"Missing {EVOLUTION_CHART_PATH}")

    def test_temporal_profiles_schema(self):
        """Verify quarterly behavioral profiles schema and consistency."""
        with open(TEMPORAL_PROFILES_PATH) as f:
            profiles = json.load(f)

        self.assertEqual(len(profiles), 4)
        total_incidents = sum(p["total_incidents"] for p in profiles.values())
        self.assertEqual(total_incidents, 220663)

        for q_name, q_data in profiles.items():
            self.assertIn("dominant_behavioral_patterns", q_data)
            patterns = q_data["dominant_behavioral_patterns"]
            self.assertIn("temporal_patterns", patterns)
            self.assertIn("weapon_characteristics", patterns)
            self.assertIn("context_and_harm", patterns)
            self.assertGreater(patterns["temporal_patterns"]["mean_hour"], 0.0)

    def test_cluster_evolution_statistics(self):
        """Verify statistical integrity of cluster evolution crosstabs and tests."""
        with open(CLUSTER_EVOLUTION_PATH) as f:
            c_evo = json.load(f)

        self.assertIn("quarterly", c_evo)
        self.assertIn("monthly", c_evo)
        self.assertIn("clusters", c_evo)

        # Check Chi2 test
        self.assertGreater(c_evo["quarterly"]["chi2_statistic"], 0.0)
        self.assertTrue(c_evo["quarterly"]["statistically_significant"])
        self.assertLess(c_evo["quarterly"]["p_value"], 0.001)

        # Check clusters count
        self.assertEqual(len(c_evo["clusters"]), 8)

    def test_feature_trends_and_significant_shifts(self):
        """Verify feature trends, ANOVA p-values, and detected shifts."""
        with open(FEATURE_TRENDS_PATH) as f:
            trends = json.load(f)
        with open(SIGNIFICANT_SHIFTS_PATH) as f:
            shifts = json.load(f)

        self.assertIn("is_night", trends)
        self.assertIn("has_weapon", trends)
        self.assertIn("has_arrest", trends)

        self.assertEqual(len(trends["is_night"]["monthly_trajectory"]), 12)
        self.assertGreater(trends["is_night"]["anova_f_statistic"], 0.0)

        # Significant shifts
        self.assertGreaterEqual(len(shifts), 4)
        for s in shifts:
            self.assertIn("shift_id", s)
            self.assertIn("title", s)
            self.assertIn("delta_magnitude", s)
            self.assertIn("p_value", s)

    def test_timeline_dashboard_schema(self):
        """Verify timeline dashboard JSON format for frontend rendering."""
        with open(TIMELINE_DASHBOARD_PATH) as f:
            timeline = json.load(f)

        self.assertIn("metadata", timeline)
        self.assertIn("cluster_timeline", timeline)
        self.assertIn("feature_timeline", timeline)
        self.assertEqual(len(timeline["cluster_timeline"]["series"]), 8)
        self.assertEqual(len(timeline["cluster_timeline"]["months"]), 12)


if __name__ == "__main__":
    unittest.main()
