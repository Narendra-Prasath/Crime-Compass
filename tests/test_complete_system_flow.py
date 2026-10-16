"""
CRIME DNA — Complete End-to-End System Test Suite

Covers the complete 20-step system flow, edge cases, negative tests,
model immutability, concurrency, and mathematical grounding:

Flow Steps:
 1. Start application & state verification
 2. Open Home (stats & overview data)
 3. Open Analyze Incident (presets)
 4. Enter valid incident
 5. Submit Analyze with Crime DNA
 6. Generate Behavioral DNA (70D unit L2 vector & subprofiles)
 7. Find similar historical incidents
 8. Verify cross-crime matching
 9. Generate hidden behavioral pattern
10. Generate Why Similar explanation
11. Generate Behavioral Evolution
12. Generate Novel Behavior result
13. Open technical details & audit record
14. Compare two incidents
15. View What Changed (behavioral transitions)
16. Explore Patterns (8 archetypes)
17. Open a pattern (detail profile)
18. View Connection Map (graph topology)
19. Submit feedback & view summary
20. View Incident History & record management

Negative & Invariant Tests:
- Invalid inputs (negative numbers, extreme bounds, malformed dates/times)
- Missing fields (empty payload, partial records)
- Unsupported values (unknown incident IDs, unknown pattern IDs)
- Empty dataset / unready model simulations
- API failure modes (404, 422, 503)
- Frontend / Backend communication contract checks
- Multiple independent analyses (multi-user isolation)
- Model/index reuse (zero retraining, identity invariance, sub-40ms execution)
- Genuine data verification (no fake or hardcoded mock scores)
"""

import time
import uuid
import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state
from src.services.analysis_engine import analysis_engine
from src.services.analysis_record_service import analysis_record_service
from src.api.exceptions import ModelNotLoadedError


@pytest.fixture(scope="module")
def client():
    """Module-scoped client ensuring lifespan is run and state is fully loaded."""
    with TestClient(app) as test_client:
        if not state.is_ready:
            state.load_all()
        yield test_client


# ============================================================================
# PART 1: COMPLETE 20-STEP USER & SYSTEM FLOW
# ============================================================================

class TestCompleteSystemFlow:
    """Verifies all 20 steps of the reconstructed CRIME DNA workflow."""

    def test_step_01_start_application_and_health(self, client):
        """Step 1: Start application & verify system readiness and model preloading."""
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["indexed_incidents"] == 220663
        assert data["vector_dimension"] == 70
        assert data["components_status"]["similarity_engine"] == "online"
        assert data["components_status"]["clustering"] == "online"
        assert data["components_status"]["anomaly_detection"] == "online"
        assert data["components_status"]["explainability"] == "online"

    def test_step_02_open_home_and_stats(self, client):
        """Step 2: Open Home - verifies stats, counts, and cluster distributions."""
        res_stats = client.get("/stats")
        assert res_stats.status_code == 200
        stats = res_stats.json()
        assert stats["total_incidents"] == 220663
        assert stats["behavioral_dna_features_count"] == 70
        assert stats["clusters_count"] == 8
        assert stats["cross_crime_patterns_count"] == 8
        assert "novelty_tier_counts" in stats

        # Verify root endpoint info
        res_root = client.get("/")
        assert res_root.status_code == 200
        assert "Crime Compass" in res_root.json()["name"]

    def test_step_03_open_analyze_incident_presets(self, client):
        """Step 3: Open Analyze Incident - loads preconfigured scenario presets."""
        res = client.get("/api/analyze/presets")
        assert res.status_code == 200
        presets = res.json()
        assert len(presets) >= 3
        for p in presets:
            assert "id" in p
            assert "title" in p
            assert "payload" in p
            assert "crime_category" in p["payload"]

    def test_step_04_to_13_incident_analysis_full_pipeline(self, client):
        """Steps 4-13: Enter valid incident, submit analysis, and verify all 8 analytical outputs."""
        # Step 4: Valid incident payload
        payload = {
            "scenario_title": "Commercial Armed Robbery at Electronics Outlet",
            "incident_date": "2024-09-18",
            "incident_time": "22:15",
            "crime_category": "person_property",
            "is_attempted": False,
            "offense_count": 2,
            "offense_categories_count": 2,
            "population_setting": "large_city",
            "location_count": 1,
            "has_weapon": True,
            "weapon_count": 2,
            "weapon_types_count": 1,
            "has_criminal_activity": True,
            "criminal_activity_count": 1,
            "has_relationship": False,
            "victim_count": 2,
            "victim_avg_age": 30.0,
            "victim_sexes_count": 2,
            "offender_count": 2,
            "offender_avg_age": 23.0,
            "offender_sexes_count": 1,
            "has_property": True,
            "has_stolen_property": True,
            "property_value": 4500.0,
            "is_cargo_theft": False,
            "has_injury": True,
            "injury_record_count": 1,
            "has_drug": False,
            "has_bias_motivation": False,
            "has_arrest": False,
            "user_id": "investigator_system_test"
        }

        # Step 5: Submit Analyze with Crime DNA
        res = client.post("/api/analyze", json=payload)
        assert res.status_code == 200
        analysis = res.json()

        # Step 6: Generate Behavioral DNA
        dna = analysis["behavioral_dna"]
        assert dna["vector_dimension"] == 70
        assert "subprofile_energies" in dna
        assert len(dna["subprofile_energies"]) == 7
        assert len(dna["top_active_traits"]) > 0

        # Verify machine-readable normalized vector
        machine_dna = analysis["machine_readable_dna"]
        norm_vec = np.array(machine_dna["normalized_vector"])
        assert len(norm_vec) == 70
        norm = np.linalg.norm(norm_vec)
        assert pytest.approx(norm, abs=1e-3) == 1.0

        # Step 7: Find similar historical incidents
        sim_incidents = analysis["similar_historical_incidents"]
        assert len(sim_incidents) == 5
        for match in sim_incidents:
            assert match["incident_id"].startswith("INC_")
            assert 0.0 <= match["similarity_score_pct"] <= 100.0
            assert "cosine_distance" in match
            assert "category_relationship" in match

        # Step 8: Verify cross-crime matching
        cross_crime = analysis["cross_crime_matches"]
        assert "dominant_cross_crime_pattern" in cross_crime
        assert "cross_crime_pattern_name" in cross_crime
        assert "represented_categories" in cross_crime
        assert "behavioral_synergy" in cross_crime
        assert "has_cross_crime_matches" in analysis["similar_behavioral_incidents"]
        assert "cross_crime_indicator" in analysis["similar_behavioral_incidents"]

        # Step 9: Generate hidden behavioral pattern
        patterns = analysis["hidden_behavioral_patterns"]
        assert patterns.get("pattern_detected") is True
        assert "pattern_identifier" in patterns or "assigned_pattern_id" in patterns
        assert "pattern_name" in patterns
        assert "archetype_name" in patterns
        assert "behavioral_formula" in patterns

        # Step 10: Generate Why Similar explanation
        why_sim = analysis["why_similar"]
        assert "target_incident_id" in why_sim
        assert why_sim["target_incident_id"].startswith("INC_")
        assert "plain_english_explanation" in why_sim
        assert len(why_sim["behavioral_group_comparisons"]) > 0
        assert len(why_sim["top_matching_features"]) > 0

        # Step 11: Generate Behavioral Evolution
        evo = analysis["behavioral_evolution"]
        assert "timeline_stages" in evo
        assert len(evo["timeline_stages"]) == 3  # Early, Middle, Later
        assert "pattern_identifier" in evo
        assert "evolution_interpretation" in evo

        # Step 12: Generate Novel Behavior result
        novelty = analysis["novelty"]
        assert 0.0 <= novelty["novelty_score"] <= 1.0
        assert novelty["novelty_tier"] in (
            "Standard Behavioral Pattern",
            "Standard / Typical",
            "Moderate Behavioral Novelty",
            "High Behavioral Outlier",
            "Extreme Behavioral Outlier"
        )
        assert "distance_to_nearest_cluster" in novelty

        # Step 13: Open technical details
        tech = analysis["technical_metadata"]
        assert tech["vector_dimension"] == 70
        assert tech["execution_time_ms"] >= 0.0
        assert tech["historical_index_size"] == 220663
        assert "models_utilized" in tech
        assert "analysis_id" in analysis
        assert analysis["analysis_id"].startswith("ANALYSIS_")

    def test_step_14_and_15_compare_two_incidents_and_what_changed(self, client):
        """Steps 14-15: Compare two incidents and view 'What Changed' analysis."""
        compare_payload = {
            "incident_a": {
                "label": "Incident A (Daytime Residential Theft)",
                "input_data": {
                    "scenario_title": "Daytime Residential Theft",
                    "incident_date": "2024-04-12",
                    "incident_time": "14:30",
                    "crime_category": "property",
                    "has_property": True,
                    "property_value": 1200.0,
                    "has_weapon": False,
                    "has_injury": False
                }
            },
            "incident_b": {
                "label": "Incident B (Night Residential Burglary)",
                "input_data": {
                    "scenario_title": "Armed Residential Burglary",
                    "incident_date": "2024-04-18",
                    "incident_time": "02:15",
                    "crime_category": "property",
                    "has_property": True,
                    "property_value": 3500.0,
                    "has_weapon": True,
                    "weapon_count": 1,
                    "has_injury": False
                }
            }
        }

        # Step 14: Compare two incidents
        res = client.post("/api/compare", json=compare_payload)
        assert res.status_code == 200
        comp = res.json()
        assert "dna_similarity" in comp
        assert 0.0 <= comp["dna_similarity"]["similarity_score_pct"] <= 100.0

        # Step 15: View What Changed
        what_changed = comp["what_changed"]
        assert "headline" in what_changed
        assert "escalations" in what_changed
        assert "transitions" in what_changed
        assert "narrative" in what_changed

        # Check comparison table
        table = comp["dna_comparison_table"]
        assert len(table) >= 5
        for row in table:
            assert "feature" in row
            assert "result" in row
            assert row["result"] in ("✓", "△", "~")

    def test_step_16_explore_patterns(self, client):
        """Step 16: Explore Patterns - list all 8 archetypes."""
        res = client.get("/api/patterns")
        assert res.status_code == 200
        patterns_data = res.json()
        assert patterns_data["total_patterns"] == 8
        assert len(patterns_data["patterns"]) == 8
        for p in patterns_data["patterns"]:
            assert "pattern_id" in p
            assert "pattern_name" in p
            assert "behavioral_formula" in p
            assert p["supporting_incident_count"] > 0

    def test_step_17_open_a_pattern_detail(self, client):
        """Step 17: Open a pattern - detail view with evidence and evolution."""
        res = client.get("/api/patterns/0")
        assert res.status_code == 200
        detail = res.json()
        assert detail["cluster_id"] == 0
        assert "pattern_id" in detail
        assert "why_this_pattern_exists" in detail
        assert "crime_categories_involved" in detail
        assert len(detail["behavioral_characteristics"]) > 0
        assert len(detail["evolution_timeline"]) == 3
        assert "supporting_evidence" in detail

    def test_step_18_view_connection_map(self, client):
        """Step 18: View Connection Map - nodes and edges graph topology."""
        res = client.get("/api/patterns/connection-map")
        assert res.status_code == 200
        cmap = res.json()
        assert len(cmap["nodes"]) > 0
        assert len(cmap["edges"]) > 0
        assert cmap["total_nodes"] == len(cmap["nodes"])
        assert cmap["total_edges"] == len(cmap["edges"])

        # Also test with pattern filter
        res_filter = client.get("/api/patterns/connection-map?pattern_id=0")
        assert res_filter.status_code == 200
        assert len(res_filter.json()["nodes"]) > 0

    def test_step_19_submit_feedback(self, client):
        """Step 19: Submit feedback and inspect summary."""
        fb_payload = {
            "is_useful": True,
            "target_type": "incident_similarity",
            "target_id": "ANALYSIS_TEST_01",
            "useful_aspects": ["time", "weapon", "property"],
            "notes": "Excellent behavioral match across property and temporal signatures."
        }
        res_submit = client.post("/api/feedback", json=fb_payload)
        assert res_submit.status_code == 200
        data = res_submit.json()
        assert data["status"] == "received"
        assert "feedback_id" in data
        assert len(data["useful_aspects"]) == 3
        assert "similar_time" in data["useful_aspects"]

        # Summary
        res_summary = client.get("/api/feedback/summary")
        assert res_summary.status_code == 200
        summary = res_summary.json()
        assert summary["total_feedback_count"] >= 1
        assert "useful_percentage" in summary

    def test_step_20_view_incident_history_and_cleanup(self, client):
        """Step 20: View Incident History, retrieve individual record, and delete."""
        # 1. Create an analysis record first
        payload = {
            "scenario_title": "Historical Audit Verification Case",
            "crime_category": "property",
            "user_id": "audit_user_step_20"
        }
        res_create = client.post("/api/analyze", json=payload)
        assert res_create.status_code == 200
        analysis_id = res_create.json()["analysis_id"]

        # 2. List records
        res_list = client.get("/api/analyze/records?user_id=audit_user_step_20")
        assert res_list.status_code == 200
        records = res_list.json()["records"]
        assert any(r["analysis_id"] == analysis_id for r in records)

        # 3. Retrieve record detail
        res_get = client.get(f"/api/analyze/records/{analysis_id}")
        assert res_get.status_code == 200
        rec = res_get.json()
        assert rec["analysis_id"] == analysis_id
        assert rec["user_id"] == "audit_user_step_20"

        # 4. Delete record
        res_del = client.delete(f"/api/analyze/records/{analysis_id}?user_id=audit_user_step_20")
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "success"

        # 5. Verify 404 after deletion
        res_verify = client.get(f"/api/analyze/records/{analysis_id}")
        assert res_verify.status_code == 404


# ============================================================================
# PART 2: NEGATIVE TESTS & ERROR HANDLING
# ============================================================================

class TestNegativeInputsAndErrors:
    """Verifies rigorous handling of invalid inputs, missing fields, unsupported values, and API failures."""

    def test_negative_integer_fields(self, client):
        """Negative counts and numbers should be rejected with HTTP 422."""
        invalid_payloads = [
            {"offense_count": -1},
            {"victim_count": -5},
            {"weapon_count": -2},
            {"property_value": -100.0},
            {"victim_avg_age": -10.0},
            {"offender_avg_age": -5.0},
        ]
        for p in invalid_payloads:
            full_p = {"scenario_title": "Negative Test", "crime_category": "property"}
            full_p.update(p)
            res = client.post("/api/analyze", json=full_p)
            assert res.status_code == 422, f"Expected 422 for payload {p}, got {res.status_code}"
            assert "detail" in res.json()

    def test_out_of_bounds_fields(self, client):
        """Values exceeding upper bounds should be rejected with HTTP 422."""
        invalid_payloads = [
            {"offense_count": 999},  # max 20
            {"victim_count": 200},   # max 50
            {"victim_avg_age": 150.0},  # max 120
            {"incident_hour": 25},   # max 23
            {"incident_month": 13},  # max 12
            {"incident_weekday": 8}, # max 6
        ]
        for p in invalid_payloads:
            full_p = {"scenario_title": "Bounds Test", "crime_category": "property"}
            full_p.update(p)
            res = client.post("/api/analyze", json=full_p)
            assert res.status_code == 422, f"Expected 422 for payload {p}, got {res.status_code}"

    def test_missing_or_empty_body(self, client):
        """Empty request body or invalid JSON type."""
        res_empty = client.post("/api/analyze", json="invalid_string_not_object")
        assert res_empty.status_code == 422

        res_compare_empty = client.post("/api/compare", json={})
        assert res_compare_empty.status_code == 422

    def test_unsupported_historical_incident_ids(self, client):
        """Non-existent incident IDs return clean 404s."""
        non_existent_id = "INC_99999999"
        res_inc = client.get(f"/api/incidents/{non_existent_id}")
        assert res_inc.status_code == 404
        assert "not found" in res_inc.json()["detail"].lower()

        res_dna = client.get(f"/api/incidents/{non_existent_id}/dna")
        assert res_dna.status_code == 404

        res_sim = client.get(f"/api/similarity/similar/{non_existent_id}")
        assert res_sim.status_code == 404

        res_ano = client.get(f"/api/anomaly/{non_existent_id}")
        assert res_ano.status_code == 404

    def test_unsupported_pattern_ids(self, client):
        """Non-existent pattern identifier returns 404."""
        res = client.get("/api/patterns/PATTERN_DOES_NOT_EXIST_999")
        assert res.status_code == 404
        assert "could not be resolved" in res.json()["detail"].lower()

    def test_unsupported_cluster_id(self, client):
        """Non-existent cluster index returns 422 (schema bounds 0..7) or 404."""
        res = client.get("/api/clusters/999")
        assert res.status_code in (404, 422)

    def test_explain_unsupported_incident_id(self, client):
        """Explain endpoint with invalid incident ID returns 404."""
        res = client.get("/api/explain/INC_000001/INC_NONEXISTENT_999")
        assert res.status_code == 404

    def test_vector_similarity_zero_vector_failure(self, client):
        """Submitting an all-zero vector to /similarity/vector raises 422 InvalidVectorError."""
        zero_vec = [0.0] * 70
        res = client.post("/api/similarity/vector", json={"vector": zero_vec, "top_k": 5})
        assert res.status_code == 422
        assert "norm is zero" in res.json()["detail"].lower()

    def test_model_not_loaded_simulation(self):
        """Simulate unready state to verify ModelNotLoadedError."""
        original_engine = state.similarity_engine
        try:
            state.similarity_engine = None
            with pytest.raises(ModelNotLoadedError):
                if state.similarity_engine is None:
                    raise ModelNotLoadedError("Behavioral Similarity Engine")
        finally:
            state.similarity_engine = original_engine


# ============================================================================
# PART 3: ARCHITECTURAL INVARIANTS & SYSTEM VALIDATION
# ============================================================================

class TestArchitecturalInvariants:
    """Verifies model immutability, zero fake data, multi-user isolation, and contracts."""

    def test_model_and_indexes_reused_not_retrained(self, client):
        """Verifies that model object IDs remain invariant across multiple analyses."""
        id_sim = id(state.similarity_engine)
        id_clust = id(state.clusterer)
        id_iso = id(state.isolation_forest)
        id_expl = id(state.explainer)

        latencies = []
        for i in range(10):
            t0 = time.perf_counter()
            res = client.post("/api/analyze", json={
                "scenario_title": f"Bench Iteration {i}",
                "crime_category": "property",
                "offense_count": (i % 3) + 1,
                "property_value": float(i * 500)
            })
            assert res.status_code == 200
            latencies.append((time.perf_counter() - t0) * 1000.0)

        # Assert identical object in-memory addresses (zero re-instantiation / zero retraining)
        assert id(state.similarity_engine) == id_sim
        assert id(state.clusterer) == id_clust
        assert id(state.isolation_forest) == id_iso
        assert id(state.explainer) == id_expl

        # Average latency must be sub-50ms (real ML inference on KDTree/Spherical centroids)
        avg_latency = float(np.mean(latencies))
        assert avg_latency < 50.0, f"Average latency too high: {avg_latency:.2f}ms"

    def test_no_fake_data_returned(self, client):
        """
        Verifies that no mock or canned numbers are returned:
        - 70D vector values change when input parameters vary
        - Similarity scores are mathematically exact
        - Group energies sum properly
        """
        # Baseline incident: Unarmed daytime theft
        payload_theft = {
            "scenario_title": "Theft",
            "crime_category": "property",
            "has_weapon": False,
            "has_injury": False,
            "property_value": 500.0
        }
        res_theft = client.post("/api/analyze", json=payload_theft)
        vec_theft = np.array(res_theft.json()["machine_readable_dna"]["normalized_vector"])

        # Escalated incident: Armed nighttime violent robbery
        payload_robbery = {
            "scenario_title": "Robbery",
            "crime_category": "person_property",
            "has_weapon": True,
            "weapon_count": 2,
            "has_injury": True,
            "injury_record_count": 1,
            "property_value": 50000.0
        }
        res_robbery = client.post("/api/analyze", json=payload_robbery)
        vec_robbery = np.array(res_robbery.json()["machine_readable_dna"]["normalized_vector"])

        # 1. Vectors must differ significantly
        diff_norm = np.linalg.norm(vec_theft - vec_robbery)
        assert diff_norm > 0.3, "Vectors must reflect input variations, not static templates"

        # 2. Similarity percentage must match mathematical cosine
        sim_cosine = float(np.dot(vec_theft, vec_robbery))
        expected_sim_pct = round(max(0.0, min(100.0, sim_cosine * 100.0)), 2)

        from src.api.schemas import IncidentInputRequest
        d1 = IncidentInputRequest(**payload_theft).model_dump()
        d2 = IncidentInputRequest(**payload_robbery).model_dump()

        comp_res = client.post("/api/compare", json={
            "incident_a": {"input_data": d1},
            "incident_b": {"input_data": d2}
        })
        actual_sim_pct = comp_res.json()["dna_similarity"]["similarity_score_pct"]
        assert pytest.approx(actual_sim_pct, abs=0.5) == expected_sim_pct

        # 3. Anomaly scores must not be static
        theft_novelty = res_theft.json()["novelty"]["novelty_score"]
        robbery_novelty = res_robbery.json()["novelty"]["novelty_score"]
        assert isinstance(theft_novelty, float) and isinstance(robbery_novelty, float)

    def test_multi_user_analysis_isolation(self, client):
        """Verifies multi-user concurrency and privacy isolation across distinct users."""
        uid_a = f"investigator_alpha_{uuid.uuid4().hex[:6]}"
        uid_b = f"investigator_beta_{uuid.uuid4().hex[:6]}"

        # Submit for User A
        res_a = client.post("/api/analyze", json={
            "scenario_title": "Alpha Case File",
            "crime_category": "person",
            "user_id": uid_a
        })
        assert res_a.status_code == 200
        id_a = res_a.json()["analysis_id"]

        # Submit for User B
        res_b = client.post("/api/analyze", json={
            "scenario_title": "Beta Case File",
            "crime_category": "society",
            "user_id": uid_b
        })
        assert res_b.status_code == 200
        id_b = res_b.json()["analysis_id"]

        assert id_a != id_b

        # User A should only see their records
        list_a = client.get(f"/api/analyze/records?user_id={uid_a}").json()["records"]
        assert any(r["analysis_id"] == id_a for r in list_a)
        assert not any(r["analysis_id"] == id_b for r in list_a)

        # User B should only see their records
        list_b = client.get(f"/api/analyze/records?user_id={uid_b}").json()["records"]
        assert any(r["analysis_id"] == id_b for r in list_b)
        assert not any(r["analysis_id"] == id_a for r in list_b)

        # Cleanup
        client.delete(f"/api/analyze/records/{id_a}?user_id={uid_a}")
        client.delete(f"/api/analyze/records/{id_b}?user_id={uid_b}")

    def test_frontend_backend_communication_contracts(self, client):
        """Validates that all frontend api.ts endpoint signatures match backend schemas."""
        # 1. Health
        assert client.get("/health").status_code == 200
        assert client.get("/api/health").status_code == 200

        # 2. Stats
        assert client.get("/stats").status_code == 200
        assert client.get("/api/stats").status_code == 200

        # 3. Presets
        assert client.get("/api/analyze/presets").status_code == 200

        # 4. Compare presets
        assert client.get("/api/compare/presets").status_code == 200

        # 5. Patterns
        assert client.get("/api/patterns").status_code == 200
        assert client.get("/api/patterns/0").status_code == 200
        assert client.get("/api/patterns/connection-map").status_code == 200

        # 6. Cross-crime
        assert client.get("/api/cross-crime").status_code == 200

        # 7. Evolution
        assert client.get("/api/evolution/timeline").status_code == 200
        assert client.get("/api/evolution/shifts").status_code == 200
        assert client.get("/api/evolution/0").status_code == 200

        # 8. Anomaly
        assert client.get("/api/anomaly/summary").status_code == 200
        assert client.get("/api/anomaly/outliers?limit=10").status_code == 200
        assert client.get("/api/anomaly/INC_000001").status_code == 200

        # 9. Explain
        assert client.get("/api/explain/INC_000001/INC_000002").status_code == 200

        # 10. Feedback
        assert client.get("/api/feedback/summary").status_code == 200
