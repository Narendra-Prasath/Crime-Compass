"""
Unit and Integration Tests for CRIME DNA Phase 10 Explainable AI (XAI)
"""

import os
import json
import unittest
import numpy as np
import pandas as pd

from src.models.explainability.explainer import BehavioralSimilarityExplainer
from src.models.explainability.config import (
    EXPLAINABILITY_DIR,
    SAMPLE_EXPLANATIONS_PATH,
    EXPLANATION_METADATA_PATH,
    EXPLANATION_CHART_PATH
)


class TestBehavioralSimilarityExplainer(unittest.TestCase):
    """Unit and integration tests for Behavioral Similarity Explainer."""

    @classmethod
    def setUpClass(cls):
        """Instantiate and load explainer engine."""
        cls.explainer = BehavioralSimilarityExplainer()
        cls.explainer.load_data()

    def test_production_artifacts_exist(self):
        """Verify precomputed explainability artifacts exist on disk."""
        self.assertTrue(os.path.exists(SAMPLE_EXPLANATIONS_PATH), f"Missing {SAMPLE_EXPLANATIONS_PATH}")
        self.assertTrue(os.path.exists(EXPLANATION_METADATA_PATH), f"Missing {EXPLANATION_METADATA_PATH}")
        self.assertTrue(os.path.exists(EXPLANATION_CHART_PATH), f"Missing {EXPLANATION_CHART_PATH}")

    def test_exact_additive_efficiency(self):
        """Verify the mathematical axiom of efficiency: sum(group_contribs) == total_similarity."""
        # Test on cross-crime pair
        exp = self.explainer.explain_pair("INC_136975", "INC_145291")
        total_sim = exp["cosine_similarity_raw"]

        group_sum = sum(g["absolute_contribution"] for g in exp["group_contributions"].values())
        self.assertAlmostEqual(total_sim, group_sum, delta=0.001)

        # Verify group percentages sum to ~100%
        pct_sum = sum(g["percentage_of_similarity"] for g in exp["group_contributions"].values())
        self.assertAlmostEqual(pct_sum, 100.0, delta=0.5)

    def test_identical_incident_explanation(self):
        """Verify self-comparison yields 100% similarity and minimal differences."""
        exp = self.explainer.explain_pair("INC_000002", "INC_000002")
        self.assertEqual(exp["similarity_score_pct"], 100.0)
        self.assertEqual(exp["cosine_similarity_raw"], 1.0)
        self.assertIn("Minor attribute variances", exp["differences"][0])

    def test_formatted_text_output_schema(self):
        """Verify user-requested text layout is strictly maintained."""
        exp = self.explainer.explain_pair("INC_136975", "INC_145291")
        text = exp["formatted_text_summary"]

        self.assertIn("Similarity Score:", text)
        self.assertIn("Main contributing similarities:", text)
        self.assertIn("Differences:", text)

        # Check list items presence
        self.assertGreaterEqual(len(exp["main_contributing_similarities"]), 1)
        self.assertGreaterEqual(len(exp["differences"]), 1)

    def test_invalid_incident_id_raises_keyerror(self):
        """Verify querying non-existent incident IDs raises KeyError."""
        with self.assertRaises(KeyError):
            self.explainer.explain_pair("NON_EXISTENT_ID_999", "INC_000002")


if __name__ == "__main__":
    unittest.main()
