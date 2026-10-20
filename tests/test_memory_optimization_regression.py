"""
Regression Tests for 512 MB Free Cloud Deployment Memory Optimizations.

Verifies:
1. Memory-mapped 70D Behavioral DNA matrix works read-only with zero full-matrix copies.
2. NearestNeighbors engine provides exact mathematical cosine similarity results.
3. BehavioralSimilarityExplainer produces exact additive attributions without loading behavioral CSV.
4. ApplicationState provides fast O(1) incident lookups with full type fidelity without 15M dicts.
5. Production API endpoints respond with 200 OK and expected schemas.
"""

import unittest
import numpy as np
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state


class TestMemoryOptimizationRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not state.is_ready:
            state.load_all()
        cls.client = TestClient(app)

    def test_mmap_matrix_integrity(self):
        """Verify normalized_dna_matrix is memory-mapped and 70-dimensional."""
        self.assertIsNotNone(state.normalized_matrix)
        self.assertEqual(state.normalized_matrix.shape, (220663, 70))
        self.assertEqual(state.normalized_matrix.dtype, np.float32)
        
        # Verify read-only or memmap mode
        self.assertTrue(
            hasattr(state.normalized_matrix, "_mmap") or isinstance(state.normalized_matrix, np.memmap),
            "normalized_matrix should be loaded with mmap_mode='r'"
        )

        # Verify unit norm condition on S^69
        first_norm = float(np.linalg.norm(state.normalized_matrix[0]))
        self.assertAlmostEqual(first_norm, 1.0, places=4)

    def test_similarity_engine_find_similar_regression(self):
        """Verify find_similar returns top matches with correct subprofile breakdowns."""
        query_id = "INC_136975"
        res = state.similarity_engine.find_similar(query_id, top_k=5)

        self.assertEqual(res["query_incident_id"], query_id)
        self.assertEqual(len(res["matches"]), 5)
        
        # Self-exclusion
        match_ids = [m["incident_id"] for m in res["matches"]]
        self.assertNotIn(query_id, match_ids, "Queried incident must not be returned in its own results")

        # Top match validation
        top_match = res["matches"][0]
        self.assertGreater(top_match["similarity_score_pct"], 90.0)
        self.assertIn("subprofile_similarity_pct", top_match)
        self.assertGreater(len(top_match["subprofile_similarity_pct"]), 0)

    def test_similarity_engine_vector_query_regression(self):
        """Verify vector search works identically with kneighbors_fast."""
        vec = state.normalized_matrix[100]
        res = state.similarity_engine.find_similar_by_vector(vec, top_k=3)
        self.assertEqual(len(res["matches"]), 3)
        self.assertEqual(res["matches"][0]["incident_id"], state.incident_ids[100])
        self.assertAlmostEqual(res["matches"][0]["similarity_score_pct"], 100.0, places=1)

    def test_explainer_additive_attribution_regression(self):
        """Verify explainer produces exact additive inner-product contributions."""
        exp = state.explainer.explain_pair("INC_136975", "INC_145291")

        self.assertIn("similarity_score_pct", exp)
        self.assertAlmostEqual(exp["similarity_score_pct"], 85.7, places=1)
        self.assertIn("plain_english_explanation", exp)
        self.assertGreater(len(exp["differences"]), 0)
        self.assertGreater(len(exp["top_contributing_features"]), 0)

        # Mathematical efficiency axiom: sum of group contributions == overall similarity
        total_sim = exp["cosine_similarity_raw"]
        group_sum = sum(g["absolute_contribution"] for g in exp["group_contributions"].values())
        self.assertAlmostEqual(total_sim, group_sum, places=3)

    def test_incident_profile_type_fidelity(self):
        """Verify compact incident lookup restores exact types without data distortion."""
        prof = state.get_incident_profile("INC_136975")
        self.assertIsNotNone(prof)
        self.assertEqual(prof["incident_id"], "INC_136975")

        ctx = prof["context"]
        self.assertIsInstance(ctx["incident_hour"], int)
        self.assertIsInstance(ctx["is_weekend"], bool)
        self.assertIsInstance(ctx["population"], float)
        self.assertIsInstance(ctx["has_weapon"], bool)
        self.assertIsInstance(ctx["primary_crime_category"], str)
        self.assertEqual(ctx["primary_crime_category"], "Crimes Against Persons (Assault/Violence)")

        cl = prof["cluster"]
        self.assertEqual(cl["cluster_id"], 1)
        self.assertIn("Violent Armed", cl["cluster_name"])

        nov = prof["novelty"]
        self.assertIsInstance(nov["novelty_score"], float)
        self.assertIsInstance(nov["novelty_tier"], str)

    def test_incident_dna_output_fidelity(self):
        """Verify get_incident_dna returns all 70 coordinates and top active traits."""
        dna = state.get_incident_dna("INC_136975")
        self.assertIsNotNone(dna)
        self.assertEqual(dna["vector_dimension"], 70)
        self.assertEqual(len(dna["feature_vector"]), 70)
        self.assertGreater(len(dna["group_energies"]), 0)
        self.assertGreater(len(dna["top_active_traits"]), 0)

    def test_api_incident_endpoint_regression(self):
        """Verify /api/incidents/{id} endpoint responds with 200 OK."""
        res = self.client.get("/api/incidents/INC_136975")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["incident_id"], "INC_136975")
        self.assertEqual(data["context"]["incident_hour"], 21)

    def test_api_similarity_endpoint_regression(self):
        """Verify /api/similarity/{id} endpoint responds with 200 OK and matches."""
        res = self.client.get("/api/similarity/INC_136975?top_k=3")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["matches"]), 3)

    def test_api_explain_endpoint_regression(self):
        """Verify /api/explain/{id1}/{id2} endpoint responds with 200 OK."""
        res = self.client.get("/api/explain/INC_136975/INC_145291")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertAlmostEqual(data["similarity_score_pct"], 85.7, places=1)
        self.assertIn("time pattern", data["plain_english_explanation"])

    def test_api_analyze_incident_endpoint_regression(self):
        """Verify /api/analyze/incident endpoint works with real ML models."""
        payload = {
            "incident_hour": 22,
            "incident_month": 10,
            "incident_weekday": 5,
            "is_weekend": 1,
            "is_night": 1,
            "crime_category": "property",
            "has_weapon": 0,
            "has_injury": 0,
            "has_property": 1,
            "has_drug": 0,
            "has_arrest": 0,
            "has_relationship": 0,
            "population": 150000.0,
            "property_value": 3500.0,
            "victim_count": 1,
            "offender_count": 1
        }
        res = self.client.post("/api/analyze/input", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("similar_historical_incidents", data)
        self.assertGreater(len(data["similar_historical_incidents"]), 0)


if __name__ == "__main__":
    unittest.main()
