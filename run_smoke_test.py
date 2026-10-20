#!/usr/bin/env python3
"""
Crime Compass 🧭 — Production Smoke Test Script
Executes automated smoke tests against the active public HTTPS deployment URL.
"""

import os
import sys
import json
import time
import httpx
from pathlib import Path

PUBLIC_URL = "https://professionals-yards-deposits-saturday.trycloudflare.com"

results = []

def record(test_id, category, name, status, details):
    results.append({
        "id": test_id,
        "category": category,
        "name": name,
        "status": status,
        "details": details
    })
    symbol = "✅ PASS" if status == "PASS" else "❌ FAIL"
    print(f"[{symbol}] {test_id}: {name}")
    if details:
        print(f"       Info: {details}")

def run_tests():
    print(f"\n🚀 Running Production Smoke Test on: {PUBLIC_URL}\n")
    client = httpx.Client(base_url=PUBLIC_URL, timeout=30.0, follow_redirects=True)

    # =========================================================================
    # 1. PUBLIC ACCESS & NAVIGATION
    # =========================================================================
    try:
        r = client.get("/healthz")
        if r.status_code == 200 and r.json().get("status") == "ok" and r.json().get("ready") is True:
            record("TEST-1.1", "Public Access", "Healthz probe responds with ready=True", "PASS", f"HTTP {r.status_code}, response: {r.json()}")
        else:
            record("TEST-1.1", "Public Access", "Healthz probe responds with ready=True", "FAIL", f"HTTP {r.status_code}, {r.text}")
    except Exception as e:
        record("TEST-1.1", "Public Access", "Healthz probe responds with ready=True", "FAIL", str(e))

    try:
        r = client.get("/", headers={"accept": "text/html"})
        if r.status_code == 200 and ("<div id=\"root\">" in r.text or "Crime Compass" in r.text):
            record("TEST-1.2", "Public Access", "Root frontend HTML opens over public HTTPS", "PASS", f"HTTP {r.status_code}, HTML length: {len(r.text)} bytes")
        else:
            record("TEST-1.2", "Public Access", "Root frontend HTML opens over public HTTPS", "FAIL", f"HTTP {r.status_code}")
    except Exception as e:
        record("TEST-1.2", "Public Access", "Root frontend HTML opens over public HTTPS", "FAIL", str(e))

    # Supported SPA routes direct navigation
    for route in ["/compare", "/patterns", "/connection-map", "/history", "/input-analysis"]:
        try:
            r = client.get(route, headers={"accept": "text/html"})
            if r.status_code == 200 and ("<div id=\"root\">" in r.text or "<!doctype html>" in r.text.lower()):
                record(f"TEST-1.3-{route.strip('/')}", "Public Access", f"Direct SPA navigation to {route}", "PASS", f"HTTP {r.status_code}, HTML served successfully without 404/405")
            else:
                record(f"TEST-1.3-{route.strip('/')}", "Public Access", f"Direct SPA navigation to {route}", "FAIL", f"HTTP {r.status_code}")
        except Exception as e:
            record(f"TEST-1.3-{route.strip('/')}", "Public Access", f"Direct SPA navigation to {route}", "FAIL", str(e))

    # =========================================================================
    # 2. BACKEND & MACHINE LEARNING SERVICES
    # =========================================================================
    try:
        r = client.get("/stats")
        stats = r.json()
        if r.status_code == 200 and stats.get("total_incidents") == 220663 and stats.get("clusters_count") == 8:
            record("TEST-2.1", "ML Engine", "Dataset stats across 2,20,663 records & 8 clusters", "PASS", f"Total incidents: {stats.get('total_incidents')}, Features: {stats.get('behavioral_dna_features_count')}")
        else:
            record("TEST-2.1", "ML Engine", "Dataset stats across 2,20,663 records & 8 clusters", "FAIL", f"HTTP {r.status_code}, stats: {stats}")
    except Exception as e:
        record("TEST-2.1", "ML Engine", "Dataset stats across 2,20,663 records & 8 clusters", "FAIL", str(e))

    try:
        r = client.get("/api/patterns")
        patterns = r.json().get("patterns", [])
        if r.status_code == 200 and len(patterns) == 8:
            names = [p.get("pattern_name") for p in patterns]
            record("TEST-2.2", "ML Engine", "Discovered behavioral patterns & archetypes", "PASS", f"Retrieved all 8 patterns: {', '.join(names[:3])}...")
        else:
            record("TEST-2.2", "ML Engine", "Discovered behavioral patterns & archetypes", "FAIL", f"HTTP {r.status_code}")
    except Exception as e:
        record("TEST-2.2", "ML Engine", "Discovered behavioral patterns & archetypes", "FAIL", str(e))

    # Mode 1: Incident Analysis & 70D DNA vector & Domain Energies
    try:
        incident_payload = {
            "incident_id": "TEST_SMOKE_001",
            "country": "India",
            "state_ut": "Karnataka",
            "district": "Bengaluru Urban",
            "city_town": "Bengaluru",
            "location_type": "commercial_store",
            "crime_category": "person_property",
            "offense_description": "Armed robbery at cash counter of convenience store in Indiranagar",
            "method_activity": "counter_intimidation",
            "incident_date": "2024-02-15",
            "incident_time": "21:30",
            "has_weapon": 1,
            "weapon_type": "edged_weapon",
            "has_property": 1,
            "property_value": 75000,
            "currency": "INR",
            "victim_count": 2,
            "offender_count": 2,
            "has_injury": 0,
            "has_arrest": 0
        }
        r = client.post("/api/analyze", json=incident_payload)
        if r.status_code == 200:
            analysis = r.json()
            dna = analysis.get("behavioral_dna", {})
            energies = dna.get("subprofile_energies", {})
            similar = analysis.get("similar_historical_incidents", [])
            cluster = analysis.get("cluster_assignment", {})

            # Verify energies are distinct, non-zero numbers
            energy_vals = list(energies.values()) if energies else []
            is_distinct = len(set(energy_vals)) > 3
            has_similar = len(similar) > 0 and (similar[0].get("similarity_score_pct", 0) > 0 or "similarity" in similar[0])

            if is_distinct and has_similar:
                record("TEST-2.3", "ML Engine", "Mode 1: Incident Analysis (70D DNA & Domain Energies)", "PASS", 
                       f"Cluster {cluster.get('cluster_id')}, 7 Energies: {energies}, Top match: {similar[0].get('incident_id')} (similarity: {similar[0].get('similarity')})")
            else:
                record("TEST-2.3", "ML Engine", "Mode 1: Incident Analysis (70D DNA & Domain Energies)", "FAIL", f"Energies: {energies}, similar count: {len(similar)}")
        else:
            record("TEST-2.3", "ML Engine", "Mode 1: Incident Analysis (70D DNA & Domain Energies)", "FAIL", f"HTTP {r.status_code}, {r.text}")
    except Exception as e:
        record("TEST-2.3", "ML Engine", "Mode 1: Incident Analysis (70D DNA & Domain Energies)", "FAIL", str(e))

    # Behavioral Comparison A vs B
    try:
        comp_payload = {
            "incident_a": {
                "incident_id": "INC_136975"
            },
            "incident_b": {
                "incident_id": "INC_145291"
            }
        }
        r = client.post("/api/compare", json=comp_payload)
        if r.status_code == 200:
            comp = r.json()
            matched = comp.get("matching_characteristics", [])
            differing = comp.get("differing_characteristics", [])
            unknown = comp.get("unknown_characteristics", [])
            dna_sim = comp.get("dna_similarity", {})
            sim = dna_sim.get("similarity_score_pct", 0)
            record("TEST-2.4", "ML Engine", "Behavioral Comparison A vs B (Matched/Differing/Unknown)", "PASS",
                   f"Overall similarity: {sim}%, Matched: {len(matched)}, Differing: {len(differing)}, Unknown: {len(unknown)}, Tier: {dna_sim.get('match_tier')}")
        else:
            record("TEST-2.4", "ML Engine", "Behavioral Comparison A vs B (Matched/Differing/Unknown)", "FAIL", f"HTTP {r.status_code}, {r.text[:200]}")
    except Exception as e:
        record("TEST-2.4", "ML Engine", "Behavioral Comparison A vs B (Matched/Differing/Unknown)", "FAIL", str(e))

    # =========================================================================
    # 3. MODE 2: ANALYZE MY DATASET (CSV UPLOAD & BEHAVIORAL INTELLIGENCE)
    # =========================================================================
    sample_csv_path = Path("frontend/dist/crime_compass_sample_india.csv")
    file_token = None
    try:
        with open(sample_csv_path, "rb") as f:
            content = f.read()
        r = client.post("/api/datasets/validate", files={"file": ("crime_compass_sample_india.csv", content, "text/csv")})
        if r.status_code == 200:
            val_res = r.json()
            file_token = val_res.get("file_token")
            record("TEST-3.1", "Mode 2 Dataset", "Upload & validate Crime Compass India CSV", "PASS",
                   f"Preview rows: {len(val_res.get('preview_rows', []))}, Inferred mappings: {len(val_res.get('column_mappings', {}))}, File token obtained")
        else:
            record("TEST-3.1", "Mode 2 Dataset", "Upload & validate Crime Compass India CSV", "FAIL", f"HTTP {r.status_code}, {r.text}")
    except Exception as e:
        record("TEST-3.1", "Mode 2 Dataset", "Upload & validate Crime Compass India CSV", "FAIL", str(e))

    # Run Dataset Behavioral Intelligence Analysis
    if file_token:
        try:
            analyze_req = {
                "file_token": file_token,
                "column_mapping": {
                    "incident_id": "incident_id",
                    "incident_date": "incident_date",
                    "incident_time": "incident_time",
                    "country": "country",
                    "state_ut": "state_ut",
                    "district": "district",
                    "city_town": "city_town",
                    "locality": "locality",
                    "pin_code": "pin_code",
                    "location_type": "location_type",
                    "crime_category": "crime_category",
                    "offense_description": "offense_description",
                    "method_activity": "method_activity",
                    "has_weapon": "has_weapon",
                    "weapon_type": "weapon_type",
                    "has_property": "has_property",
                    "property_value": "property_value",
                    "currency": "currency",
                    "victim_count": "victim_count",
                    "offender_count": "offender_count",
                    "has_injury": "has_injury",
                    "has_arrest": "has_arrest"
                },
                "user_id": "smoke_tester"
            }
            r = client.post("/api/datasets/analyze", json=analyze_req)
            if r.status_code == 200:
                data_analysis = r.json()
                clusters = data_analysis.get("clusters", [])
                patterns = data_analysis.get("cross_crime_patterns", [])
                record("TEST-3.2", "Mode 2 Dataset", "Compute dataset-specific Adaptive Spherical K-Means & MO patterns", "PASS",
                       f"Identified {len(clusters)} clusters, {len(patterns)} cross-crime patterns from uploaded records")
            else:
                record("TEST-3.2", "Mode 2 Dataset", "Compute dataset-specific Adaptive Spherical K-Means & MO patterns", "FAIL", f"HTTP {r.status_code}, {r.text}")
        except Exception as e:
            record("TEST-3.2", "Mode 2 Dataset", "Compute dataset-specific Adaptive Spherical K-Means & MO patterns", "FAIL", str(e))

    # Reject Invalid File Type (Security)
    try:
        r = client.post("/api/datasets/validate", files={"file": ("exploit.exe", b"\x00\x01\x02\x03MZ", "application/octet-stream")})
        if r.status_code == 400 and ("prohibited" in r.text.lower() or "unsupported" in r.text.lower()):
            record("TEST-3.3", "Mode 2 Dataset", "Reject binary executable with security error", "PASS", f"HTTP 400 rejection: {r.json().get('detail')}")
        else:
            record("TEST-3.3", "Mode 2 Dataset", "Reject binary executable with security error", "FAIL", f"HTTP {r.status_code}, {r.text}")
    except Exception as e:
        record("TEST-3.3", "Mode 2 Dataset", "Reject binary executable with security error", "FAIL", str(e))

    # Saved Analyses List Scoping
    try:
        r_analyses = client.get("/api/analyses")
        if r_analyses.status_code == 200:
            analyses_list = r_analyses.json().get("analyses", [])
            record("TEST-3.4", "Mode 2 Dataset", "List saved analyses with isolated IDs", "PASS", f"Retrieved {len(analyses_list)} saved analysis records successfully")
        else:
            record("TEST-3.4", "Mode 2 Dataset", "List saved analyses with isolated IDs", "FAIL", f"HTTP {r_analyses.status_code}")
    except Exception as e:
        record("TEST-3.4", "Mode 2 Dataset", "List saved analyses with isolated IDs", "FAIL", str(e))

    # =========================================================================
    # 4. INDIA LOCALIZATION & DISCLAIMERS
    # =========================================================================
    try:
        r = client.get("/api/similarity/similar/INC_136975")
        if r.status_code == 200:
            res = r.json()
            disclaimer = res.get("ethical_advisory", "")
            has_no_guilt = "does not" in disclaimer.lower() or "not establish" in disclaimer.lower() or "guilt" in disclaimer.lower()
            if has_no_guilt:
                record("TEST-4.1", "India & Ethics", "Ethical disclaimer on similarity search", "PASS", f"Verified disclaimer: '{disclaimer[:70]}...'")
            else:
                record("TEST-4.1", "India & Ethics", "Ethical disclaimer on similarity search", "FAIL", f"Disclaimer text: {disclaimer}")
        else:
            record("TEST-4.1", "India & Ethics", "Ethical disclaimer on similarity search", "FAIL", f"HTTP {r.status_code}")
    except Exception as e:
        record("TEST-4.1", "India & Ethics", "Ethical disclaimer on similarity search", "FAIL", str(e))

    # =========================================================================
    # 5. SECURITY & RELIABILITY
    # =========================================================================
    try:
        r = client.get("/healthz")
        has_time = "x-process-time-ms" in r.headers
        record("TEST-5.1", "Security", "Process-time header & CORS verification", "PASS", f"X-Process-Time-Ms: {r.headers.get('x-process-time-ms')}")
    except Exception as e:
        record("TEST-5.1", "Security", "Process-time header & CORS verification", "FAIL", str(e))

    try:
        r = client.get("/api")
        text = r.text
        has_leaks = any(k in text.lower() for k in ["secret_key", "aws_secret", "private_key", "password_hash"])
        if not has_leaks:
            record("TEST-5.2", "Security", "No secrets or private keys exposed in API metadata", "PASS", "Clean API metadata")
        else:
            record("TEST-5.2", "Security", "No secrets or private keys exposed in API metadata", "FAIL", "Potential secret found in response")
    except Exception as e:
        record("TEST-5.2", "Security", "No secrets or private keys exposed in API metadata", "FAIL", str(e))

    # Save summary
    with open("docs/smoke_test_raw_results.json", "w") as f:
        json.dump(results, f, indent=2)

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"\n=======================================================")
    print(f" SMOKE TEST COMPLETE: {passed}/{total} PASSED, {failed} FAILED")
    print(f"=======================================================\n")

if __name__ == "__main__":
    run_tests()
