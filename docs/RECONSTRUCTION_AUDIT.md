# CRIME DNA — Reconstruction & Upgrade Audit
**System Status:** Production-Ready (Phases 1–15 Complete)  
**Target:** Upgrade to an Input-Driven Behavioral Analysis Platform  
**Audit Date:** October 2026  
**Safety Protocol:** Read-Only Audit. No application code, weights, indexes, or datasets altered.

---

## Executive Summary

CRIME DNA is currently a high-performance, validated machine learning and investigative analytics system trained on **220,663 NIBRS incident records**. It transforms complex statutory offenses into dense, 70-dimensional **Behavioral DNA fingerprints** across 7 behavioral sub-profiles. 

In its current Phase 15 state, the application is primarily **retrieval- and corpus-driven**: users explore discovered clusters, cross-crime patterns, temporal shifts, and lookup historical incidents (`INC_XXXXXX`) to inspect their Behavioral DNA and query nearest neighbors.

This audit evaluates the codebase across all 15 completed phases to establish a blueprint for upgrading CRIME DNA into an **Input-Driven Behavioral Analysis Platform**—enabling investigators and analysts to input novel, unindexed incident parameters (or hypothetical case scenarios), dynamically synthesize their 70D Behavioral DNA, and instantly execute real-time behavioral similarity matching, archetype assignment, anomaly quantification, and explainability against the 220,663 historical corpus.

---

## 1. Existing Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                    CRIME DNA ARCHITECTURE OVERVIEW                                  |
+----------------------------------------------------------------------------------------------------+

 [ Raw Dataset ]
       |
       v  (src/data/cleaner.py)
 [ Cleaned Dataset ] --------------> 220,663 records x 195 columns (data/processed/crime_dna_cleaned.csv)
       |
       v  (src/features/dna_encoder.py)
 [ Behavioral DNA ] ---------------> 220,663 records x 70 dimensions (crime_dna_behavioral_features.csv)
       |
       +--------------------+---------------------+--------------------+--------------------+
       |                    |                     |                    |                    |
       v                    v                     v                    v                    v
 [ Similarity Engine ] [ Clustering ]       [ Cross-Crime ]      [ Evolution ]        [ Anomaly ]
  NearestNeighbors       MiniBatchKMeans       Convergence          Quarterly/Monthly    IsolationForest
  Cosine Metric (k=5)    Spherical (k=8)       Matrix & Modality    ANOVA & Chi2 Trends  + Centroid Dist
  knn_index.joblib       kmeans_model.joblib   8 Discovered CCPs    Timeline & Shifts    Dual-Paradigm
       |                    |                     |                    |                    |
       +--------------------+---------------------+--------------------+--------------------+
                                                  |
                                                  v
                                     [ Explainability Engine ]
                                      Additive Cosine Attribution
                                      Feature-Level & Group-Level XAI
                                                  |
                                                  v
                                     [ FastAPI Backend Engine ]
                                      Lifespan Preloaded State (src/api/state.py)
                                      14 REST Endpoints across 8 Routers
                                      Host: 0.0.0.0:8000
                                                  |
                                                  v  (HTTP / Vite Proxy)
                                     [ React + Vite Dashboard ]
                                      TypeScript, Vanilla Design System
                                      8 Dedicated Investigative Analytics Pages
                                      Host: 0.0.0.0:5173
+----------------------------------------------------------------------------------------------------+
```

### Key Architectural Strengths:
- **Zero-Retraining In-Memory State (`src/api/state.py`):** At FastAPI server startup, all models, normalized matrices, and registries load into RAM in **~1.25–1.35 seconds**, delivering sub-20ms inference and lookup response times.
- **Statutory Decoupling:** Legal crime classifications (Assault, Burglary, Robbery) are segregated from operational behavioral signatures, allowing pure behavioral comparison.
- **Strict Ethical Boundaries:** The system strictly prohibits identity inference, offender linkage, or guilt determination, focusing purely on incident-level modus operandi similarities.

---

## 2. Existing ML Components

| Component | Class / Location | Algorithm / Methodology | Artifacts & Parameters |
|---|---|---|---|
| **Data Cleaner** | `PreprocessingPipeline` (`src/data/cleaner.py`) | Deterministic sanitization, zero-variance & collinear drop, sentinel handling | `data/processed/crime_dna_cleaned.csv` (195 cols, 220,663 rows) |
| **DNA Encoder** | `BehavioralDNAEncoder` (`src/features/dna_encoder.py`) | Non-linear bounded scaling, trigonometric cyclical encodings, log-transforms | `data/processed/crime_dna_behavioral_features.csv` (70 features) |
| **Similarity Engine** | `BehavioralSimilarityEngine` (`src/models/similarity/engine.py`) | Exact Cosine metric via `NearestNeighbors` (Brute/BallTree) on unit L2 vectors | `data/processed/similarity_index/knn_index.joblib`, `normalized_dna_matrix.npy` |
| **Clustering Engine** | `BehavioralClusterer` (`src/models/clustering/engine.py`) | Spherical `MiniBatchKMeans` on unit L2 hypersphere ($k=8$, random_state=42) | `data/processed/clusters/kmeans_model.joblib`, `cluster_profiles.json` |
| **Cross-Crime Analyzer** | `CrossCrimeAnalyzer` (`src/models/cross_crime/analyzer.py`) | Category-stratified cluster convergence, statutory breakdown, MO extraction | `data/processed/cross_crime/cross_crime_patterns.json`, `cross_crime_summary.json` |
| **Evolution Analyzer** | `BehavioralEvolutionAnalyzer` (`src/models/evolution/analyzer.py`) | Longitudinal ANOVA F-tests, Chi-square contingency, linear trend regressions | `data/processed/evolution/timeline_dashboard.json`, `significant_shifts.json` |
| **Anomaly Detector** | `BehavioralAnomalyDetector` (`src/models/anomaly/detector.py`) | Dual-Paradigm: $0.6 \times \text{CentroidDist} + 0.4 \times \text{IsolationForest}$ | `data/processed/anomaly/isolation_forest.joblib`, `top_behavioral_outliers.json` |
| **Explainer (XAI)** | `BehavioralSimilarityExplainer` (`src/models/explainability/explainer.py`) | Exact Additive Cosine Attribution: $c_j = u_j \cdot v_j$, $\sum c_j = \cos(u, v)$ | `data/processed/explainability/explanation_metadata.json`, `sample_explanations.json` |
| **System Evaluator** | `SystemEvaluator` (`src/validation/system_evaluator.py`) | Full-pipeline validation, perturbation testing, stability & metric benchmarking | `docs/validation_results.json` |

---

## 3. Existing Backend Endpoints

All endpoints are served via FastAPI on prefix `/api` with strict Pydantic schema validation.

| Router | Method | Path | Summary / Function | Current Capabilities |
|---|---|---|---|---|
| **Health** | `GET` | `/api/health` | System health & component readiness | Returns uptime, memory index status, incident count |
| **Stats** | `GET` | `/api/stats` | Dataset statistics & taxonomy | Incident volume, column counts, feature distributions |
| **Stats** | `GET` | `/api/dataset-stats` | Alias for `/api/stats` | Backward-compatible alias |
| **Incidents**| `GET` | `/api/incidents/search` | Paginated incident browser | Query by cluster, crime category, limit/offset |
| **Incidents**| `GET` | `/api/incidents/{incident_id}` | Incident contextual profile | Returns incident metadata, context flags, cluster, novelty |
| **Incidents**| `GET` | `/api/incidents/{incident_id}/dna` | Incident 70D Behavioral DNA | Returns 70D vector, group energies, active traits |
| **Similarity**| `GET` | `/api/similarity/similar/{incident_id}` | Top-K similar incidents by ID | Cosine nearest neighbors, excludes query incident itself |
| **Similarity**| `GET` | `/api/similarity/{incident_id}` | Alias for similar incidents | Direct ID lookup |
| **Similarity**| `POST`| `/api/similarity/search` | POST similar incidents by ID | Payload-driven ID lookup with custom top_k |
| **Similarity**| `POST`| `/api/similarity/vector` | Arbitrary vector search | **Queries index using arbitrary 70D array!** |
| **Clusters** | `GET` | `/api/clusters` | All 8 discovered cluster archetypes | High-level profiles, counts, macro-categories |
| **Clusters** | `GET` | `/api/clusters/{cluster_id}` | Detailed cluster archetype | Distinctive dimensions, dominant modalities |
| **Cross-Crime**| `GET`| `/api/cross-crime` | Discovered cross-crime patterns | All 8 cross-statutory behavioral patterns |
| **Cross-Crime**| `GET`| `/api/cross-crime/{pattern_id}` | Specific cross-crime pattern | Legal breakdown, MO, exemplars |
| **Evolution**| `GET` | `/api/evolution/timeline` | Longitudinal timeline data | Monthly cluster & feature trajectories |
| **Evolution**| `GET` | `/api/evolution/shifts` | Statistically significant shifts | 4 empirical shifts with ANOVA/Chi2 evidence |
| **Evolution**| `GET` | `/api/evolution/clusters` | Cluster monthly percentages | Longitudinal cluster shifts |
| **Evolution**| `GET` | `/api/evolution/features` | Feature trajectories & ANOVA | 12-month feature trend metrics |
| **Anomaly**  | `GET` | `/api/anomaly/outliers` | High & moderate behavioral outliers | Filter by tier (Extreme, High, Moderate) |
| **Anomaly**  | `GET` | `/api/anomaly/incident/{incident_id}` | Incident anomaly explanation | Nearest clusters, unusual feature deviations |
| **Anomaly**  | `GET` | `/api/anomaly/summary` | Novelty distribution metadata | Threshold quantiles (p95, p99), tier counts |
| **Explain**  | `GET` | `/api/explain/{id1}/{id2}` | Pairwise similarity explanation | Group contributions, matching features, differences |
| **Explain**  | `POST`| `/api/explain` | POST pairwise explanation | Explain via request body payload |

---

## 4. Existing Frontend Pages

The React 19 frontend (`frontend/src/`) is structured as a single-page application (SPA) with tab/hash routing:

1. **`OverviewPage` (`frontend/src/pages/OverviewPage.tsx`):**
   - High-level executive dashboard showing total indexed incidents (220,663), DNA dimensions (70), cluster count (8), cross-crime patterns (8), and high outliers (2,207).
   - Features KPI metric cards, system architecture badges, and recent incident quick-links.
2. **`IncidentAnalyzerPage` (`frontend/src/pages/IncidentAnalyzerPage.tsx`):**
   - Incident lookup by ID (`INC_XXXXXX`).
   - Displays incident contextual facts (hour, location, weapon, victim, property).
   - Plots interactive 7-axis DNA Radar chart and horizontal subprofile score bars.
   - Lists Top-5 behaviorally similar incidents with similarity percentages and one-click comparative actions.
3. **`SimilarityViewPage` (`frontend/src/pages/SimilarityViewPage.tsx`):**
   - Head-to-head comparison between a query incident and matched incidents.
   - Side-by-side metric tables, subprofile similarity delta bars, and shared characteristics.
4. **`WhySimilarPage` (`frontend/src/pages/WhySimilarPage.tsx`):**
   - Interpretable XAI explanation breakdown.
   - Renders exact additive contributions across 7 behavioral groups, top contributing features, and semantic differences (e.g. "Different crime category: Property vs Person").
5. **`BehavioralPatternsPage` (`frontend/src/pages/BehavioralPatternsPage.tsx`):**
   - Explores the 8 Spherical MiniBatchKMeans clusters.
   - Displays cluster cards, macro-category distribution, and deep-dive modal showing dominant operational modalities and distinctive mathematical dimensions.
6. **`CrossCrimePage` (`frontend/src/pages/CrossCrimePage.tsx`):**
   - Visualizes behavioral convergence across statutory boundaries.
   - Shows cross-category breakdown progress bars (e.g. Robbery + Assault sharing Burglary MO), shared operational modalities, and real exemplar incidents.
7. **`BehavioralEvolutionPage` (`frontend/src/pages/BehavioralEvolutionPage.tsx`):**
   - Longitudinal trend analysis across 12 months and 4 quarters.
   - Line charts for cluster prevalence and behavioral feature trajectories.
   - Detailed empirical shift cards documenting ANOVA $F$-statistics and $p$-values.
8. **`NovelBehaviorPage` (`frontend/src/pages/NovelBehaviorPage.tsx`):**
   - Dual-paradigm outlier browser.
   - Interactive tier filters (All Outliers, Moderate $p_{95}$, High/Extreme $p_{99}$).
   - Incident outlier cards detailing distance to nearest cluster centroids and top unusual feature deviations.

---

## 5. Existing Reusable Components

Located in `frontend/src/components/`:
- **`DNARadarChart.tsx`:** Highly reusable SVG radar chart rendering 7 normalized behavioral axes (`Time`, `Crime Complexity`, `Location`, `Method/Weapon`, `People`, `Property`, `Harm/Context`). Supports standalone vectors and overlay comparisons.
- **`SubprofileBars.tsx`:** Clean, responsive horizontal bar chart visualizing percentage scores (0–100%) for the 7 behavioral sub-profiles.
- **`ExplanationCard.tsx`:** Standardized card layout for explainability attributions, displaying group contribution cards, top positive matching features, and semantic contrast bullet points.
- **`StateViews.tsx`:** Standardized loading spinner (`LoadingView`), error state banner (`ErrorView`), and empty state handler (`EmptyView`) ensuring consistent UX across the application.
- **Global Design System (`frontend/src/index.css`):** Complete dark-themed CSS variable design token system (`--bg-main`, `--bg-card`, `--accent-blue`, `--accent-cyan`, `--accent-purple`, `--accent-amber`, `--accent-emerald`, typography, cards, badges, and layout utilities).

---

## 6. Existing Models, Indexes & Artifacts

All precomputed artifacts reside in `data/processed/`:

### Core Data & Features:
- `crime_dna_cleaned.csv`: 220,663 rows × 195 columns of cleaned NIBRS data.
- `crime_dna_behavioral_features.csv`: 220,663 rows × 71 columns (`incident_id` + 70 normalized features).
- `behavioral_dna_feature_names.json`: Ordered list of all 70 feature strings.
- `behavioral_dna_metadata.json`: Feature group definitions and scaling parameters.
- `cleaning_metadata.json`: Summary of dropped zero-variance and duplicate columns.

### Model Weights & Indices:
- `similarity_index/knn_index.joblib`: Serialized Scikit-Learn `NearestNeighbors` index (brute-force cosine distance).
- `similarity_index/normalized_dna_matrix.npy`: Memory-mapped $220,663 \times 70$ float32 unit L2-normalized matrix.
- `similarity_index/incident_ids.json`: Array mapping matrix row indices to `incident_id` strings.
- `clusters/kmeans_model.joblib`: Trained `MiniBatchKMeans` model ($k=8$ centroids).
- `clusters/cluster_profiles.json`: Statistical profiles and descriptive names for all 8 clusters.
- `clusters/incident_cluster_labels.csv`: Cluster assignment for each of the 220,663 incidents.
- `cross_crime/cross_crime_patterns.json`: 8 detailed cross-category patterns.
- `evolution/timeline_dashboard.json`: Monthly and quarterly longitudinal data.
- `evolution/significant_shifts.json`: Statistical documentation of the 4 verified behavioral shifts.
- `anomaly/isolation_forest.joblib`: Trained `IsolationForest` estimator.
- `anomaly/incident_anomaly_scores.csv`: Novelty scores and tiers for all incidents.
- `anomaly/top_behavioral_outliers.json`: Cached top 100 behavioral outliers.

---

## 7. Existing Feature Engineering

The feature engineering pipeline is implemented in `src/features/dna_encoder.py` (`BehavioralDNAEncoder`). It processes 195 raw cleaned columns and produces 70 strictly bounded $[0.0, 1.0]$ features across 7 domains:

1. **Temporal Dynamics (8 features):**
   - Diurnal cyclical encoding: $\sin(2\pi \cdot \text{hour}/24)$, $\cos(2\pi \cdot \text{hour}/24)$ mapped to $[0, 1]$.
   - Seasonal cyclical encoding: $\sin(2\pi (\text{month}-1)/12)$, $\cos(2\pi (\text{month}-1)/12)$.
   - Weekly cyclical encoding: $\sin(2\pi \cdot \text{weekday}/7)$, $\cos(2\pi \cdot \text{weekday}/7)$.
   - Discrete indicators: `time_is_weekend`, `time_is_night`.
2. **Crime Characteristics & Complexity (10 features):**
   - Statutory targets: Against Person, Against Property, Against Society, and compound categories (Person+Property, Person+Society, Property+Society, Person+Property+Society).
   - Offense volume & breadth: `offense_count` capped at 4.0; `offense_categories_count` capped at 3.0.
   - Attempt flag: `is_attempted`.
3. **Location & Environment (17 features):**
   - Setting complexity: `location_count` capped at 3.0.
   - Log-transformed population scale: $\ln(1 + \text{population}) / \ln(1 + 237092)$.
   - 14 one-hot population group tiers (small town, suburban county, core metropolitan).
   - Agency jurisdiction: State Police flag.
4. **Method & Weapon Modus Operandi (8 features):**
   - Weapon deployment: `has_weapon`, `weapon_count` (capped at 3), `weapon_types_count` (capped at 2), `is_multi_weapon`.
   - Organized criminal activity: `has_criminal_activity`, `criminal_activity_count` (capped at 3).
   - Interpersonal relationship: `has_relationship`, `relationship_count` (capped at 3).
5. **People & Demographics (15 features):**
   - Victimology: `victim_count` (capped at 5), `is_multi_victim`, `victim_age_known`, median-imputed scaled age ($\text{age}/100$), age spread ($\Delta \text{age}/40$), sex count, victim types count.
   - Offender group structure: `offender_count` (capped at 5), `is_co_offender`, `offender_age_known`, median-imputed scaled age ($\text{age}/100$), age spread ($\Delta \text{age}/30$), offender sexes count.
6. **Property & Economic Targeting (5 features):**
   - `has_property`, `property_record_count` (capped at 3), `has_stolen_property`, `stolen_count` (capped at 10), log-property value ($\text{value}_{\log} / 20.72$), cargo theft flag.
7. **Context, Harm & Resolution (7 features):**
   - Injury severity: `has_injury`, `injury_record_count` (capped at 3).
   - Substance involvement: `has_drug`, `suspected_drug_count` (capped at 3), log-drug quantity ($\ln(1 + \text{qty}) / \ln(1 + 1088620)$).
   - Bias motivation flag (`bias_count > 1`).
   - Immediate resolution: `has_arrest_on_scene`, `arrest_count` (capped at 3).

---

## 8. Existing Behavioral DNA Representation

Every crime incident is encoded as a **70-dimensional dense vector**:
$$\mathbf{x} = [x_1, x_2, \dots, x_{70}]^\top \in [0.0, 1.0]^{70}$$

Before indexing or similarity calculation, each vector is projected onto the unit $L_2$ hypersphere:
$$\mathbf{u} = \frac{\mathbf{x}}{\|\mathbf{x}\|_2}, \quad \|\mathbf{u}\|_2 = 1.0$$

### Subprofile Decomposition:
The 70 features are partitioned into 7 orthogonal behavioral subprofiles:
- Group 1: `temporal_dynamics` (8 features, indices 0–7)
- Group 2: `crime_characteristics` (10 features, indices 8–17)
- Group 3: `location_and_environment` (17 features, indices 18–34)
- Group 4: `method_and_activity` (8 features, indices 35–42)
- Group 5: `people_and_demographics` (15 features, indices 43–57)
- Group 6: `property_and_economics` (5 features, indices 58–62)
- Group 7: `context_harm_resolution` (7 features, indices 63–69)

This subprofile structure enables computing independent subprofile similarity scores ($0.0–100.0\%$) alongside global similarity.

---

## 9. Existing Similarity Implementation

Implemented in `src/models/similarity/engine.py`:
- **Model:** Scikit-Learn `NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')`.
- **Cos-Similarity Formula:**
  $$\text{Sim}(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v} = \sum_{j=1}^{70} u_j v_j \in [0.0, 1.0]$$
  Reported in UI as percentage: $\text{Sim}_{\%} = \text{round}(\text{Sim} \times 100, 2)\%$.
- **Exclusion of Self:** When querying by `incident_id`, the engine queries $k+1$ neighbors and drops the query incident from the result set.
- **Vector Query Method:** `find_similar_by_vector(query_vector, top_k=5)` already exists in Python and in the API (`POST /api/similarity/vector`). It accepts any 70D array, normalizes it, and returns the top-K matches with subprofile breakdowns.

---

## 10. Existing Clustering Implementation

Implemented in `src/models/clustering/engine.py`:
- **Model:** `MiniBatchKMeans(n_clusters=8, batch_size=2048, random_state=42, n_init=10)`.
- **Spherical Metric:** Executed on $L_2$-normalized vectors, ensuring Euclidean cluster distance corresponds monotonically to Cosine Distance:
  $$\|\mathbf{u} - \mathbf{c}\|_2^2 = \|\mathbf{u}\|_2^2 + \|\mathbf{c}\|_2^2 - 2(\mathbf{u} \cdot \mathbf{c}) = 2(1 - \cos(\mathbf{u}, \mathbf{c}))$$
- **Centroids:** 8 cluster centroids $\mathbf{c}_0, \dots, \mathbf{c}_7 \in \mathbb{R}^{70}$.
- **8 Established Archetypes:**
  - Cluster 0: Small-City Property & Structure Theft ($N=17,725$)
  - Cluster 1: Violent Armed Interpersonal & Domestic Assaults ($N=74,443$)
  - Cluster 2: Commercial & Structural Burglary ($N=20,111$)
  - Cluster 3: Suburban Juvenile & Unarmed Vandalism ($N=26,577$)
  - Cluster 4: Vehicle & Transit-Associated Thefts ($N=21,585$)
  - Cluster 5: Substance-Involved Narcotics & Public Order Offenses ($N=22,586$)
  - Cluster 6: Metropolitan Core Retail Larceny & Shoplifting ($N=22,763$)
  - Cluster 7: Rural / Non-Metro Weapon & Trespass Incidents ($N=14,873$)
- **Prediction Method:** `predict_cluster(vector)` already exists in `BehavioralClusterer`. It assigns any 70D vector to its nearest centroid and calculates distance to centroid.

---

## 11. Existing Cross-Crime Implementation

Implemented in `src/models/cross_crime/analyzer.py`:
- Maps behavioral cluster assignments back to statutory crime categories (e.g. Person, Property, Society).
- Identifies that certain behavioral clusters contain up to 4 legally distinct crime categories sharing the exact same modus operandi.
- Discovered 8 verified Cross-Crime Patterns (`CCP_00` to `CCP_07`), quantifying statutory proportions, mean execution hours, weapon prevalence, and representative exemplar incident IDs.

---

## 12. Existing Evolution Implementation

Implemented in `src/models/evolution/analyzer.py`:
- Analyzes population-level temporal behavioral shifts across 12 calendar months and 4 quarters.
- Statistical significance is validated through:
  - **ANOVA $F$-tests:** Across monthly feature distributions.
  - **Chi-Square Contingency Tests:** Across quarterly cluster distributions ($\chi^2 = 28.4$, $p < 0.001$).
  - **Linear Trend Regressions:** Monthly percentage slopes and Pearson $r$.
- Identified 4 verified empirical shifts:
  1. Summer Nocturnal Surge (July/August $+3.92\%$ nighttime increase).
  2. Warm-Weather Interpersonal Violence Peak (Cluster 1 $+1.42\%$ surge in Q2/Q3).
  3. Q4 Holiday Retail Larceny Surge (Cluster 6 $+2.3\%$ surge in Oct–Dec).
  4. On-Scene Arrest Rate Decline (Spring to Autumn $-3.39\%$ shift).

---

## 13. Existing Novelty / Anomaly Implementation

Implemented in `src/models/anomaly/detector.py`:
- **Dual-Paradigm Ensemble Formulation:**
  $$\text{NoveltyScore}(\mathbf{x}) = 0.6 \cdot D_{\text{centroid}}(\mathbf{x}) + 0.4 \cdot S_{\text{isolation}}(\mathbf{x})$$
  where:
  - $D_{\text{centroid}}(\mathbf{x}) = 1.0 - \max_k (\mathbf{u} \cdot \mathbf{c}_k)$ (Cosine distance to nearest cluster centroid).
  - $S_{\text{isolation}}(\mathbf{x})$ is the normalized decision function score from an `IsolationForest(n_estimators=150, max_samples=1024, contamination=0.01)`.
- **Calibrated Thresholds:**
  - Baseline: $< 95\text{th}$ percentile ($< 0.542$) — $95.0\%$ of corpus.
  - Moderate Novelty: $95\text{th} \le \text{Score} < 99\text{th}$ percentile ($[0.542, 0.641]$) — $4.0\%$ of corpus ($N=8,827$).
  - High Behavioral Outlier: $\ge 99\text{th}$ percentile ($\ge 0.641$) — $1.0\%$ of corpus ($N=2,207$).
- **Explanation Method:** `explain_incident(incident_id)` calculates feature-level deviations relative to the nearest centroid.

---

## 14. Existing Explainability Implementation

Implemented in `src/models/explainability/explainer.py`:
- **Mathematical Foundation:** Exact Additive Cosine Attribution.
  Because $\text{Sim}(\mathbf{u}, \mathbf{v}) = \sum_{j=1}^{70} u_j v_j$, each individual feature $j$ contributes exactly $c_j = u_j \cdot v_j$ to the total similarity.
- **Group Aggregation:**
  $$C_G = \sum_{j \in G} c_j, \quad \text{Share}_G = \frac{C_G}{\text{Sim}(\mathbf{u}, \mathbf{v})} \times 100\%$$
- **Semantic Contrast Generation:** Compares raw metadata attributes (crime category, weapon, injury, property, time of day) between two incidents to explain differences in plain English (e.g. "Similar location setting and nocturnal timing; Different statutory classification: Robbery vs Assault").

---

## 15. Existing Tests

The automated test suite in `tests/` contains **88 tests across 19 test modules**, all passing with 100% success rate:
- `tests/test_data_cleaning.py`: Pipeline sanitization, sentinel replacement, deduplication.
- `tests/test_data_validation.py`: Data distributions, L2-normalization matrix bounds, preprocessing reproducibility.
- `tests/test_behavioral_dna.py`: Cyclical encodings, 70D dimension bounds, group assignments.
- `tests/test_similarity_engine.py`: Cosine metric verification, self-exclusion, arbitrary vector querying, subprofile breakdowns.
- `tests/test_clustering.py`: MiniBatchKMeans fitting, cluster profile generation, vector prediction.
- `tests/test_cross_crime.py`: Cross-statutory cluster overlap, pattern artifact integrity.
- `tests/test_behavioral_evolution.py`: ANOVA $F$-tests, Chi-square calculations, longitudinal timelines.
- `tests/test_anomaly.py`: Isolation Forest calibration, threshold quantiles, outlier retrieval.
- `tests/test_explainability.py`: Exact additive attribution efficiency, pairwise explanation schemas.
- `tests/test_ml_validation.py`: Controlled perturbation tests, inverted vector discrimination, attribution conservation.
- `tests/api/test_*.py` (9 modules): Comprehensive endpoint testing covering all FastAPI routes, parameter validation, and 404/422 error handling.

---

## 16. What Can Be Reused

Virtually the **entire existing ML pipeline and artifact registry can be reused without modification**:

1. **`BehavioralDNAEncoder` (`src/features/dna_encoder.py`):**
   - The exact mathematical logic and empirical scaling parameters (`SCALING_PARAMS`) can transform any new input record or dictionary into the standardized 70D vector.
2. **`knn_index.joblib` and `normalized_dna_matrix.npy`:**
   - The 220,663 pre-indexed historical incident matrix is ready for instant nearest-neighbor retrieval.
3. **`BehavioralSimilarityEngine.find_similar_by_vector`:**
   - Already takes a 70D vector and returns top matches with subprofile breakdowns.
4. **`BehavioralClusterer.predict_cluster`:**
   - Already takes a 70D vector and predicts nearest cluster and centroid distance.
5. **`IsolationForest` Model & Centroids:**
   - Already capable of scoring a new vector for novelty against the established background distribution.
6. **`BehavioralSimilarityExplainer` Additive Attribution Logic:**
   - Can directly compute feature- and group-level attributions between an input vector and any historical match.
7. **Frontend Design System & Components:**
   - `DNARadarChart`, `SubprofileBars`, `ExplanationCard`, and CSS tokens are directly usable for displaying inputted incident results.
8. **FastAPI Lifespan State Architecture (`src/api/state.py`):**
   - Preloads models in ~1.3 seconds, ensuring high-speed inference without reloading from disk.

---

## 17. What Needs Modification

To transform the platform from lookup-only to input-driven, the following areas require focused enhancement:

1. **`BehavioralDNAEncoder` Input Flexibility:**
   - Currently, `transform(df)` expects a full pandas DataFrame matching the 195-column cleaned schema.
   - *Modification needed:* Add a method (e.g. `encode_incident_dict(data: dict) -> np.ndarray`) that accepts a structured dictionary of user-provided incident facts (e.g., hour, month, day, weapon, victims, property value, population) with sensible baseline defaults for unspecified fields, producing the exact 70D vector.
2. **Anomaly Detector Scoring for Arbitrary Vectors:**
   - Currently, `explain_incident` only operates on existing `incident_id` values in `incident_anomaly_scores.csv`.
   - *Modification needed:* Add `score_vector(vector: np.ndarray) -> dict` in `BehavioralAnomalyDetector` to compute $0.6 \cdot D_{\text{centroid}} + 0.4 \cdot S_{\text{isolation}}$ on arbitrary query vectors in real time.
3. **Explainer Support for Vector-to-Incident Pairs:**
   - Currently, `explain_pair(id1, id2)` requires both incident IDs to exist in the database.
   - *Modification needed:* Add `explain_vector_to_incident(query_vector, target_incident_id, query_context)` in `BehavioralSimilarityExplainer` so users can see *why* their inputted scenario matches a historical incident.
4. **FastAPI State & Routes:**
   - Expose a dedicated, unified analysis endpoint that receives input parameters and returns the complete behavioral assessment in a single round-trip.
5. **Frontend Navigation & Routing:**
   - Add a prominent **"Case Simulator / Input Analyzer"** navigation tab to `App.tsx` alongside existing historical views.

---

## 18. What Needs to Be Newly Added

To complete the upgrade cleanly without breaking existing functionality:

1. **New Backend Schema & Endpoint (`src/api/routes/analysis.py`):**
   - **Endpoint:** `POST /api/analyze/input`
   - **Request Schema (`IncidentInputRequest`):**
     - Structured parameters: `incident_hour` (0–23), `incident_month` (1–12), `incident_weekday` (0–6), `is_weekend` (bool), `is_night` (bool).
     - Target: `crime_category` (Person, Property, Society, or Compound).
     - Environment: `population` (int) or population tier dropdown.
     - Method: `has_weapon` (bool), `weapon_count` (int), `is_multi_weapon` (bool), `has_criminal_activity` (bool), `has_relationship` (bool).
     - Demographics: `victim_count` (int), `victim_avg_age` (float), `offender_count` (int), `offender_avg_age` (float).
     - Economics: `has_property` (bool), `property_value` (float), `has_stolen_property` (bool).
     - Context: `has_injury` (bool), `has_drug` (bool), `has_arrest` (bool).
   - **Response Schema (`InputAnalysisResponse`):**
     - Generated 70D Behavioral DNA vector and 7-subprofile energy scores.
     - Assigned cluster archetype and centroid distance.
     - Novelty score, novelty tier (Baseline / Moderate / High), and unusual feature deviations.
     - Matched cross-crime pattern (if applicable).
     - Top-5 most behaviorally similar historical incidents with cosine similarity percentages and subprofile breakdowns.
     - Immediate XAI explanation of similarity against the top matched historical incident.
2. **Preset Scenario Templates:**
   - Quick-load templates for common investigative scenarios (e.g. "Nocturnal Armed Commercial Robbery", "Suburban Daytime Residential Burglary", "Domestic Warm-Weather Interpersonal Dispute", "Metropolitan Retail Shoplifting").
3. **New Frontend Page (`frontend/src/pages/InputAnalysisPage.tsx`):**
   - **Interactive Form:** Tabbed or accordion input sections (Time, Scene/Location, Method & Weapons, People, Property, Context).
   - **Preset Loader:** Dropdown to load realistic templates in 1 click.
   - **Live Results Dashboard:**
     - Left Column: Synthesized DNA Radar Chart + Subprofile Scores + Archetype & Novelty badges.
     - Right Column: Top Similar Historical Incidents list + XAI "Why Similar?" breakdown.
     - "What-If" Sensitivity Simulator: Toggling weapon or time instantly updates similarity rankings and radar shape.
4. **Automated Test Suite for Input Pipeline (`tests/api/test_input_analysis.py`):**
   - Unit tests verifying:
     - Full and partial input dictionaries produce valid 70D vectors with unit norm.
     - `POST /api/analyze/input` returns 200 with all required sections.
     - Invalid inputs (e.g. `hour=25`) return 422 validation errors.
     - Inputted cases with extreme values receive higher novelty scores.

---

## 19. Potential Conflicts & Mitigations

| Potential Conflict | Risk | Mitigation |
|---|---|---|
| **Feature Dimension Mismatch** | Custom inputs producing $\ne 70$ features would break Scikit-Learn `NearestNeighbors` and `KMeans`. | The input encoder will map user inputs strictly through the ordered `FEATURE_NAMES` list, applying exact `SCALING_PARAMS` from `config.py` with zero-padding for non-applicable one-hot tiers. |
| **Missing Fields in User Input** | Users might only provide 3 or 4 fields (e.g. "Armed robbery at 2 AM"), leaving demographics or property unspecified. | The input encoder will utilize empirical median/mode defaults derived in the Phase 1 audit (e.g. median victim age 38, population 25,000, 1 victim, 1 offender). |
| **Breaking Existing Routes** | Modifying existing `/similarity` or `/incidents` endpoints could break existing pages. | **Zero changes to existing endpoints.** The input functionality will be placed in a dedicated router (`src/api/routes/analysis.py`) and integrated seamlessly. |
| **Performance Degradation** | Dynamic vector encoding and nearest-neighbor search taking too long on API requests. | Vector encoding of a single dictionary takes $< 1\text{ ms}$; nearest-neighbor query over 220,663 records takes $\approx 12\text{ ms}$. Total round-trip remains $< 25\text{ ms}$. |
| **Ethical Misinterpretation** | Users might think inputting case details links a specific person or predicts future guilt. | The dedicated input page will prominently feature the mandatory disclaimer: *"CRIME DNA identifies behavioral similarity and patterns between crime incidents. It does not identify offenders, determine guilt, or establish that incidents were committed by the same person."* |

---

## 20. Recommended Upgrade Architecture

The proposed upgrade adds a lightweight, unified **Input-Driven Analysis Subsystem** layered directly on top of the existing components:

```
+--------------------------------------------------------------------------------------------------------+
|                                  UPGRADED PLATFORM ARCHITECTURE                                        |
+--------------------------------------------------------------------------------------------------------+

  USER INPUT (Frontend Form / API Client)
    |
    |  POST /api/analyze/input
    v
  +----------------------------------------------------------------------------------------------------+
  |  src/api/routes/analysis.py                                                                        |
  |                                                                                                    |
  |  1. Input Validator (Pydantic IncidentInputRequest)                                                |
  |  2. Dynamic Behavioral DNA Encoder (src/features/dna_encoder.py)                                   |
  |     Maps form inputs -> 70D normalized vector u_input                                              |
  |                                                                                                    |
  |  3. Parallel Evaluation via Preloaded Memory State (src/api/state.py):                            |
  |     a. NearestNeighbors -> Top-K similar historical incidents & subprofiles                         |
  |     b. MiniBatchKMeans  -> Archetype assignment, centroid distance                                 |
  |     c. IsolationForest  -> Dual-paradigm novelty score & tier                                      |
  |     d. Explainer Engine -> Additive cosine attribution vs Top-1 match                              |
  +----------------------------------------------------------------------------------------------------+
    |
    v  InputAnalysisResponse JSON
  +----------------------------------------------------------------------------------------------------+
  |  frontend/src/pages/InputAnalysisPage.tsx                                                          |
  |                                                                                                    |
  |  - Scenario Presets (Armed Robbery, Burglary, Domestic Assault, Shoplifting)                        |
  |  - Interactive Parameter Sliders & Toggles                                                         |
  |  - Live DNA Radar & Subprofile Breakdown                                                           |
  |  - Matched Historical Incidents Feed with 1-click comparison                                       |
  |  - Dynamic "Why Similar?" Feature Contribution Card                                                |
  +----------------------------------------------------------------------------------------------------+
```

### Key Technical Characteristics of Upgraded System:
1. **Completely Non-Destructive:** Retains all 8 existing pages, all 14 existing endpoints, all 88 passing tests, and all precomputed data artifacts.
2. **Instantaneous Real-Time Feedback:** No background batch training or disk writes required during analysis.
3. **Rigorous Scientific Continuity:** Uses the identical 70D taxonomy, identical empirical scaling parameters, and identical cosine distance metric established in Phases 1–15.
4. **Hackathon & Production Impact:** Transforms the platform from a static archive browser into an interactive, real-time investigative decision-support instrument.

---

## Conclusion & Readiness

The CRIME DNA codebase is completely intact, highly modular, well-documented, and fully verified (88/88 tests passing). The architecture cleanly separates feature encoding, indexing, clustering, anomaly detection, API routing, and frontend rendering.

We are ready to proceed with implementation upon your approval.
