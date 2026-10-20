# Crime Compass 🧭 — Safe Application Upgrade Plan

**Document Version:** 1.0.0  
**Project:** Crime Compass 🧭 (formerly CRIME DNA)  
**Corpus Size:** 220,663 Historical Incidents  
**Behavioral DNA Dimensions:** 70 Dimensions across 7 Behavioral Domains  
**Status:** Pre-Upgrade Forensic Audit & Preservation Plan  

---

## 1. Executive Summary & Core Mandate

This document establishes the safe, additive, backward-compatible upgrade plan for the **Crime Compass 🧭** crime behavioral analysis platform. The platform has already completed all original 15 development phases (Dataset Audit, Cleaning, Behavioral DNA, EDA, Similarity Engine, Clustering, Cross-Crime Patterns, Behavioral Evolution, Novel Behavior Detection, Explainability, FastAPI Backend, React Dashboard, Integration, Testing, and Hackathon Polish).

### Preservation Principles
1. **Zero Retraining & Artifact Preservation:** All existing fitted models (`knn_index.joblib`, `kmeans_model.joblib`, `isolation_forest.joblib`), precomputed matrices (`normalized_dna_matrix.npy`), and metadata files are fully functional and will not be regenerated or overwritten.
2. **Schema & Feature Stability:** The 70-dimensional Behavioral DNA vector structure, 7 feature domain groupings, and input bridge transforms will remain strictly stable to ensure zero breakage of dependent ML inference.
3. **API Backward Compatibility:** Dual-routing architecture (canonical clean endpoints like `/analyze` alongside `/api/analyze` prefix) is preserved.
4. **Test Integrity:** All 218 existing unit and integration tests across 29 test suites must continue passing with zero regressions.
5. **Ethical Non-Attribution:** Strict preservation of neutral behavioral terminology (analyzing event *behavior* and *modus operandi*, never predicting offender identity, guilt, or demographic targeting).

---

## 2. Current Architecture & File Inventory

### 2.1 Backend Architecture (`src/`)
- **API Entrypoint & Configuration:**
  - [`src/api/main.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/api/main.py): FastAPI initialization, lifespan model preloading into `ApplicationState`, CORS, process timing headers, root endpoint, and dual-router registration (`/` and `/api`).
  - [`src/api/config.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/api/config.py): Environment-aware path resolution, server port/host settings, query constraints (`DEFAULT_TOP_K=5`, `MAX_TOP_K=50`).
  - [`src/api/state.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/api/state.py): Singleton memory cache holding preloaded ML models, normalized DNA matrix, incident ID lookups, cluster profiles, and anomaly metadata.
  - [`src/api/schemas.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/api/schemas.py): Pydantic request and response contracts.
  - [`src/api/exceptions.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/api/exceptions.py): Custom domain exceptions (`IncidentNotFoundError`, `ModelNotLoadedError`, etc.).

- **API Route Modules (`src/api/routes/`):**
  - `health.py`: Health probes and component readiness.
  - `stats.py`: Corpus statistics (220,663 incidents, 196 cleaned features, 70 DNA dimensions).
  - `incidents.py`: Historical incident profile retrieval (`/incidents/{id}`) and 70D DNA vector retrieval (`/incidents/{id}/dna`).
  - `similarity.py`: Fast k-NN similarity lookup (`/similarity/similar/{id}`) and custom vector search.
  - `clusters.py`: K-Means cluster archetypes summary and profiles.
  - `cross_crime.py`: 8 cross-crime behavioral pattern profiles.
  - `evolution.py`: Chronological timeline and ANOVA significant shifts.
  - `anomaly.py`: Isolation Forest anomaly metadata and top behavioral outliers.
  - `explain.py`: Pairwise similarity explainer (SHAP-style cosine decomposition).
  - `analysis.py`: Real-time incident evaluation, presets, and analysis record management.
  - `comparison.py`: Side-by-side DNA comparison (`/compare`) and comparison presets.
  - `patterns.py`: Discovered behavioral patterns cards and bipartite connection map.
  - `feedback.py`: Human-in-the-loop investigator feedback submission and aggregation.

- **Analytical Services (`src/services/`):**
  - `analysis_engine.py`: Coordinates real-time incident input evaluation across 8 analytical perspectives.
  - `analysis_record_service.py`: SQLite repository (`data/analysis_records/analysis_records.db`) with zero-PII audit logging.
  - `behavioral_graph_service.py`: Computes empirical bipartite relationship graph between 7 crime categories and 8 behavioral patterns.
  - `comparison_service.py`: Full pairwise behavioral comparison (custom vs historical).
  - `pattern_exploration_service.py`: Detailed pattern cards, formulas, and cluster profiles.
  - `feedback_service.py`: Persistent SQLite investigator feedback repository (`data/feedback/`).
  - `evolution_service.py`, `novelty_service.py`, `pattern_discovery.py`: Auxiliary analytics engines.

- **Feature Engineering & Preprocessing (`src/features/`):**
  - `config.py`: Definitive list of 70 Behavioral DNA dimensions across 7 feature groups, feature scaling caps, and plain-language descriptions.
  - `dna_encoder.py`: Batch transformer converting tabular data into 70D Behavioral DNA matrix.
  - `input_bridge.py`: Microsecond-latency encoder converting investigator form inputs into unit L2-normalized 70D vector.

- **Core ML Model Packages (`src/models/`):**
  - `similarity/engine.py`: `BehavioralSimilarityEngine` with fitted `NearestNeighbors` (metric='cosine').
  - `clustering/engine.py`: `BehavioralClusterer` with fitted `KMeans` (k=8).
  - `anomaly/detector.py`: `BehavioralAnomalyDetector` with fitted `IsolationForest`.
  - `explainability/explainer.py`: `BehavioralSimilarityExplainer` with mathematical subprofile decomposition.
  - `cross_crime/matcher.py`: Cross-crime behavioral matcher across statutory crime titles.
  - `evolution/analyzer.py`: Chronological drift and ANOVA regression analyzer.

### 2.2 Frontend Architecture (`frontend/src/`)
- **Build & Framework:** Vite 8, React 19, TypeScript, Vanilla CSS design system with CSS custom properties.
- **Routing & State:** `App.tsx` handles normalized tab navigation across 13 views.
- **Client Layer:** `api.ts` with structured error handling (`ApiError`), timeout controller, and zero mock fallbacks.
- **Pages:**
  1. `HomePage.tsx`: Landing view with platform overview, key metrics, and navigation paths.
  2. `InputAnalysisPage.tsx`: Interactive incident evaluation form with scenario presets and real-time execution.
  3. `BehavioralPatternsPage.tsx`: Explorer for 8 empirical behavioral patterns with formula tags and detail views.
  4. `IncidentHistoryPage.tsx`: Historical analysis records audit log with search, filters, and deletion.
  5. `DnaComparisonPage.tsx`: Incident A vs Incident B comparison with radar overlay and trait divergence.
  6. `BehavioralConnectionMapPage.tsx`: Interactive bipartite SVG graph connecting crime categories to behavioral patterns.
  7. `CrossCrimePage.tsx`: Analysis of shared modus operandi across differing legal offenses.
  8. `BehavioralEvolutionPage.tsx`: Chronological shift analysis and trend curves.
  9. `NovelBehaviorPage.tsx`: Anomaly distribution grid and top behavioral outlier table.
  10. `IncidentAnalyzerPage.tsx`: Historical incident profile and DNA vector inspector.
  11. `SimilarityViewPage.tsx`: Pairwise similarity inspector between historical incidents.
  12. `WhySimilarPage.tsx`: Explainable AI decomposition card with feedback widget.
  13. `OverviewPage.tsx`: High-level summary of model archetypes and operational metrics.
- **Components:**
  - `CrimeDnaResultExperience.tsx`: Comprehensive analytical results viewer with Evidence Triad (Fact / ML Finding / Interpretation).
  - `DNARadarChart.tsx`: 7-axis SVG spider radar chart with support for dual incident overlay.
  - `SubprofileBars.tsx`: Color-coded domain energy progress bars.
  - `ExplanationCard.tsx`: Visual breakdown of similarity drivers and trait differences.
  - `FeedbackWidget.tsx`: Star rating and feedback submission modal.
  - `StateViews.tsx`: Standardized loading, empty, and error state components.

---

## 3. Existing Feature Inventory & ML Implementation Status

| Feature | Primary Files | ML Implementation Status | Data Source |
| :--- | :--- | :--- | :--- |
| **Corpus Knowledge Base** | `src/api/state.py`, `src/api/routes/incidents.py` | Real (Preloaded into memory) | 220,663 incidents in `crime_dna_cleaned.csv` |
| **Behavioral DNA (70D)** | `src/features/config.py`, `input_bridge.py` | Real (Empirical transforms, L2 normalized) | Precomputed matrix `normalized_dna_matrix.npy` |
| **Similarity Engine** | `src/models/similarity/engine.py`, `similarity.py` | Real (Fitted k-NN, cosine distance) | `knn_index.joblib` (61.8 MB) |
| **8 Behavioral Patterns** | `src/models/clustering/engine.py`, `patterns.py` | Real (Fitted K-Means k=8) | `kmeans_model.joblib`, `cluster_profiles.json` |
| **Cross-Crime Patterns** | `src/models/cross_crime/matcher.py`, `cross_crime.py`| Real (Cosine alignment across legal codes) | `cross_crime_patterns.json` |
| **Behavioral Evolution** | `src/models/evolution/analyzer.py`, `evolution.py` | Real (ANOVA F-tests, regression trends) | `timeline_dashboard.json`, `significant_shifts.json` |
| **Novelty Detection** | `src/models/anomaly/detector.py`, `anomaly.py` | Real (Isolation Forest + Centroid distance) | `isolation_forest.joblib` (2.4 MB) |
| **Explainability (XAI)** | `src/models/explainability/explainer.py`, `explain.py`| Real (Subprofile cosine decomposition) | Exact dot product & feature difference |
| **DNA Comparison** | `src/services/comparison_service.py`, `comparison.py`| Real (Dual-input vector comparison) | Real-time unit vector subtraction & alignment |
| **Connection Map** | `src/services/behavioral_graph_service.py` | Real (Empirical category-to-pattern edges) | Computed from 220,663 incident assignments |
| **Incident History** | `src/services/analysis_record_service.py` | Real (Persistent SQLite storage) | `data/analysis_records/analysis_records.db` |
| **Investigator Feedback** | `src/services/feedback_service.py` | Real (Persistent SQLite storage) | `data/feedback/feedback.db` |

---

## 4. Behavioral Domain Energy: Calculation & Display Logic

### 4.1 The 7 Behavioral Domains
The 70 Behavioral DNA dimensions are partitioned into 7 domains:
1. `temporal_dynamics` (8 features): Diurnal rhythms (`time_hour_sin/cos`), seasonality (`time_month_sin/cos`), day of week (`time_weekday_sin/cos`), `is_weekend`, `is_night`.
2. `crime_characteristics` (10 features): Person, property, society indicators, compound combinations, offense counts, attempt status.
3. `location_and_environment` (17 features): Scene count, log population, 14 population tier indicators, state police agency flag.
4. `method_and_activity` (8 features): Weapon involvement, weapon count, weapon types count, multi-weapon flag, criminal activity indicators, relationship flags.
5. `people_and_demographics` (13 features): Victim counts, victim age, age spread, sex counts, co-offender status, offender count, offender age, offender sex counts.
6. `property_and_economics` (6 features): Property involvement, record count, stolen count, log property value, cargo theft.
7. `context_and_harm` (8 features): Victim injury, injury count, drug presence, suspected drug count, log drug quantity, bias motivation, on-scene arrest, arrest count.

### 4.2 Mathematical Calculation
- **In `src/api/state.py` (`get_incident_dna`):**
  $$\text{Energy}_g = \|\mathbf{v}_g\|_2 = \sqrt{\sum_{j \in G_g} v_j^2}$$
  Computed as the Euclidean L2 norm of the subvector slice, yielding a value in $[0.0, 1.0]$.
- **In `src/features/input_bridge.py` (`encode`) and `analysis_engine.py`:**
  $$\text{SubprofileEnergy}_g = \text{round}\left(100.0 \times \frac{1}{|G_g|} \sum_{j \in G_g} v_j, 1\right)$$
  Computed as the mean percentage activation of the subprofile slice, yielding a value in $[0.0, 100.0\%]$.
- **In `src/services/comparison_service.py` (`_extract_features_and_vector`):**
  Computed via L2 norm of the subprofile slice.

### 4.3 Display Logic in Frontend
- **Spider/Radar Chart (`DNARadarChart.tsx`):**
  Accepts arbitrary domain values. Normalizes scales seamlessly:
  `const normValue = value > 1.0 ? Math.min(1.0, value / 100.0) : Math.max(0.0, Math.min(1.0, value));`
  Renders an SVG polygon with radial axes and background rings at 25%, 50%, 75%, and 100%. Supports overlaid comparison polygons.
- **Subprofile Progress Bars (`SubprofileBars.tsx`):**
  Renders colored horizontal progress bars for each domain with dedicated palette tokens:
  - Temporal Dynamics: `#0ea5e9` (Cyan)
  - Crime Characteristics: `#f43f5e` (Rose)
  - Location & Environment: `#10b981` (Emerald)
  - Method & Weapon: `#f59e0b` (Amber)
  - People & Demographics: `#a855f7` (Purple)
  - Property & Economics: `#06b6d4` (Sky)
  - Harm & Enforcement: `#ec4899` (Pink)

---

## 5. Audit Findings & Areas for Improvement

1. **Branding & Identity Alignment:** The platform has been upgraded to "Crime Compass 🧭", but headers, titles, and documentation refer exclusively to "CRIME DNA". The UI and API should adopt "Crime Compass 🧭 — Behavioral DNA Intelligence" without breaking backward compatibility.
2. **Terminology Clean-Up ("Simulation" vs "Incident Analysis"):** `IncidentHistoryPage.tsx` frequently refers to "Simulate New Incident", "Simulated Incident", and "Incident Simulator". For investigator trust and scientific clarity, these should be consistently labeled as "Analyze Incident" / "Incident Audit Records".
3. **Domain Energy Metric Standardization:** While `DNARadarChart` handles both 0–1.0 (L2 norm) and 0–100% (activation percentage), responses should clearly document whether a field represents L2 vector magnitude or mean percentage activation.
4. **Fallback Label Discrepancy in `stats.py`:** `src/api/routes/stats.py` has a hardcoded fallback dictionary with `"Moderate Novelty"` and `"High Novelty"`, whereas `anomaly_metadata.json` uses `"Moderate Behavioral Novelty"` and `"High Behavioral Outlier"`. The fallback should align with the real JSON artifact.
5. **Clear Differentiation Between Live Evaluation & Historical Audit:** Clarify the distinction in the navigation menu between `InputAnalysisPage` (evaluating new or simulated incident inputs) and `IncidentAnalyzerPage` (inspecting existing historical records from the 220,663 incident database).

---

## 6. Implementation Strategy & File Modification Plan

### 6.1 Files to Modify (Preserving All Logic)
1. **`src/api/config.py`**:
   - Update `API_TITLE` to `"Crime Compass 🧭 — Behavioral Pattern Analyzer API"`.
   - Preserve all existing environment variable names and path defaults.
2. **`src/api/routes/stats.py`**:
   - Align fallback dictionary keys for `novelty_tier_counts` to match `anomaly_metadata.json` canonical strings.
3. **`frontend/src/App.tsx`**:
   - Update header brand title to **Crime Compass 🧭** with subtitle `Behavioral DNA Intelligence`.
   - Maintain all existing navigation routes, IDs, and query parameter handlers.
4. **`frontend/src/pages/HomePage.tsx`**:
   - Update Hero banner title to **CRIME COMPASS 🧭**, maintaining the `Behavioral DNA` badge and all quick-action cards.
5. **`frontend/src/pages/IncidentHistoryPage.tsx`**:
   - Replace user-facing "Simulate / Simulation" labels with "Analyze / Incident Evaluation Record".
   - Keep data structures, SQLite table columns, and API parameters completely identical.

### 6.2 New Endpoints & Files (Additive Only)
- No breaking schema changes will be introduced.
- Existing endpoints will remain 100% intact with dual-route support (`/` and `/api`).

---

## 7. Risks & Backward-Compatibility Verification

| Risk | Mitigation Measure |
| :--- | :--- |
| Breaking pre-trained model input shapes | Strictly preserve all 70 feature names, ordering, and scaling functions in `src/features/config.py`. |
| Breaking frontend API calls | Maintain existing `/api` prefix and root route aliases in `src/api/main.py`. |
| Test suite regressions | Continuously run `python3 -m pytest tests/ -q` to guarantee all 218 tests remain green. |
| Client-side TypeScript compilation errors | Run `npm run build` after any UI changes to guarantee 0 build errors. |

---

## 8. Verification & Testing Plan

1. **Full Backend Test Suite Execution:**
   ```bash
   python3 -m pytest tests/ -q
   # Expected result: 218 passed
   ```
2. **Frontend Type Checking & Bundle Verification:**
   ```bash
   cd frontend && npm run build
   # Expected result: Clean build with zero TypeScript errors
   ```
3. **End-to-End API Health Probe:**
   - Verify `GET /health` and `GET /api/health` return status `"healthy"`.
   - Verify `GET /stats` returns `total_incidents: 220663`.
   - Verify `POST /analyze` processes incident payloads into 70D DNA vectors with subprofile energies and similarity matches.
