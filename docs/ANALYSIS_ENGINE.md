# CRIME DNA — Central Behavioral Intelligence Analysis Engine

## 1. Overview & Architecture

The **Central CRIME DNA Analysis Engine** (`src/services/analysis_engine.py`) is a reusable backend service that accepts a validated crime incident entered by a user and performs comprehensive multi-perspective behavioral intelligence analysis in real time.

It orchestrates the pre-trained machine learning models, statistical baselines, and nearest-neighbor indices created during Phases 3 through 10. It operates **strictly in-memory**, performing sub-second inference **without retraining models, modifying historical reference data, or attempting predictive forecasting**.

```
                           ┌───────────────────────────────┐
                           │      User Incident Input      │
                           │   (Pydantic Schema Validated) │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │        Behavioral DNA         │
                           │  - 70D Unit L2 Feature Vector │
                           │  - Dynamic Human Fingerprint  │
                           │  - 7 Subprofile Energy Norms  │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │    Phase 5: Similarity Engine │
                           │  - Cosine KNN (k=5 Neighbors) │
                           │  - Real Cosine Distances      │
                           │  - Subprofile Match Energies  │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │ Phase 6: Clustering & Patterns│
                           │  - Spherical K-Means Centroid │
                           │  - Cluster Archetype Profile  │
                           │  - Centroid Distance Metric   │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │  Phase 7: Cross-Crime Patterns│
                           │  - Cross-Category Modus Oper. │
                           │  - Statistically Shared MOs   │
                           │  - Cross-Category Top Matches │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │  Phase 8: Behavioral Evolution│
                           │  - Longitudinal Temporal Drift│
                           │  - Seasonal Baseline Shifts   │
                           │  - Quarterly Trend Comparison │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │    Phase 9: Novelty / Outlier │
                           │  - Dual-Paradigm Metric       │
                           │  - Isolation Forest + Spheric │
                           │  - Empirical Quantile Tiers   │
                           │  - Directional Feature Shifts │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │   Phase 10: Explainability    │
                           │  - Exact Additive Attribution │
                           │  - 7-Group Share Percentages  │
                           │  - Top Feature Alignments     │
                           │  - Contextual Semantic Diffs  │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │    Unified Analysis Result    │
                           │ (10 Canonical Analytical Keys)│
                           └───────────────────────────────┘
```

---

## 2. Core Architectural Principles

### 2.1 Reusable Backend Service
The service is encapsulated in the `CrimeDnaAnalysisEngine` class and exposed as a thread-safe singleton `analysis_engine` in `src/services/analysis_engine.py`. Any backend endpoint, background job, CLI script, or testing suite can execute full behavioral evaluations with a single call:
```python
from src.services.analysis_engine import analysis_engine

result = analysis_engine.analyze(user_incident_dict)
```

### 2.2 Complete Reuse of Phase 5–10 Implementations
Rather than re-implementing algorithms or maintaining duplicate logic, the engine binds directly to the pre-loaded model state registered in `ApplicationState` (`src/api/state.py`):
- **Phase 5**: `state.similarity_engine.model` (`NearestNeighbors` with cosine metric over 220,663 records)
- **Phase 6**: `state.clusterer.predict_cluster` (`Spherical K-Means` centroids)
- **Phase 7**: `state.cross_crime_patterns` & `state.cross_crime_summary`
- **Phase 8**: `state.timeline_dashboard` & `state.significant_shifts`
- **Phase 9**: `state.isolation_forest` decision scores and calibrated quantile thresholds
- **Phase 10**: Exact additive cosine attribution:
  $$\text{sim}(\mathbf{u}, \mathbf{v}) = \sum_{j=1}^{70} u_j v_j$$

### 2.3 Zero Retraining & Zero Data Pollution
User incidents are treated strictly as **queries** against the static historical knowledge base:
- No new model weights are fitted.
- Cluster centroids remain strictly immutable:
  $$\mathbf{C}_{\text{after}} \equiv \mathbf{C}_{\text{before}}$$
- The historical index remains fixed at 220,663 incidents.
- No user-submitted incident becomes training data.

### 2.4 Strictly Observational (No Predictive Policing)
CRIME DNA makes **zero future predictions** and does **not** evaluate offender identity, recidivism probability, or legal culpability. It quantifies **behavioral modus operandi similarity** between historical incidents. Every analysis response includes the formal ethical advisory:
> *"CRIME DNA identifies behavioral similarity and patterns between crime incidents. It does not identify offenders, determine guilt, or establish that incidents were committed by the same person."*

### 2.5 Real Model Results (Never Hardcoded)
Every score, percentage, distance, and attribution is computed live from the query vector and trained model outputs. Canned mock percentages (e.g. 91%, 88%, 84%) are forbidden.

---

## 3. Analysis Pipeline Flow

### Stage 1: Incident Summary Generation
The engine synthesizes a structured summary of the user's input across temporal, statutory, environmental, force/weapon, demographic, economic, and legal harm dimensions.

### Stage 2: Behavioral DNA Encoding
1. Converts the validated input payload into a 1-row cleaned DataFrame conforming to `crime_dna_cleaned.csv`.
2. Passes it through Phase 3 `BehavioralDNAEncoder.transform()`.
3. Orders columns into the 70 standard features and computes unit $L_2$ normalization:
   $$\|\mathbf{v}_{\text{norm}}\|_2 = 1.0 \pm 10^{-5}$$
4. Computes the 7 subprofile energy values:
   $$E_g = \sqrt{\sum_{j \in g} v_{\text{norm}, j}^2}$$
5. Generates the human-readable fingerprint (`🌙 Night`, `🏢 Setting`, `🔫 Armed`, `👥 Victims`, `📦 Property`, `🩹 Injury`).

### Stage 3: DNA Similarity & Historical Retrieval
1. Queries the pre-loaded Nearest Neighbors model:
   ```python
   distances, indices = state.similarity_engine.model.kneighbors(norm_vec.reshape(1, -1), n_neighbors=5)
   ```
2. Computes the exact cosine similarity percentage:
   $$\text{sim\_pct}_i = \text{round}\big((1.0 - d_i) \times 100.0, 2\big)$$
3. Retrieves historical metadata for each match from `state.get_incident_profile(matched_id)`.
4. Computes pairwise subprofile similarity across all 7 feature domains.

### Stage 4: Hidden Behavioral Patterns (Cluster Archetype)
1. Projects the query vector onto the 8 Spherical K-Means centroids:
   $$k^* = \arg\max_k \langle \mathbf{v}_{\text{norm}}, \mathbf{c}_k \rangle$$
2. Extracts cluster metadata: archetype ID ($0 \dots 7$), name, macro category, centroid distance, and archetypal summary narrative.

### Stage 5: Cross-Crime Pattern Mapping
1. Maps the assigned cluster archetype to its cross-crime signature `CCP_{k^*:02d}`.
2. Identifies instances in the top-5 historical matches that cross legal statutory boundaries (e.g. an incident classified as "Property" matching a historical "Person / Robbery" incident due to shared weapons, timing, and co-offenders).

### Stage 6: Behavioral Evolution Timeline (Phase 8 Grounding)
1. Invokes `BehavioralEvolutionService` ([evolution_service.py](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/services/evolution_service.py)) to map the detected pattern to its historical temporal trajectory over the actual 12-month calendar dataset period.
2. Generates an intuitive 3-stage timeline (`Early Period ↓ Middle Period ↓ Later Period`) with behavioral formulas (e.g. `Night + Residential + No Weapon`), stage characteristics, and empirical volume/proportions.
3. Aligns the incident with Phase 8 statistically significant longitudinal shifts (`SHIFT_01` Summer Nocturnal Surge, etc.) via ANOVA test results.
4. Enforces strict ethical non-offender attribution guidelines and mandates the phrasing: *"Behavioral characteristics changed over the observed historical period."* (See [BEHAVIORAL_EVOLUTION_USER_FLOW.md](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/docs/BEHAVIORAL_EVOLUTION_USER_FLOW.md)).

### Stage 7: Behavioral Pattern Fit & Novelty Assessment (Phase 9 Grounding)
1. Invokes `BehavioralNoveltyService` ([novelty_service.py](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/services/novelty_service.py)) to assess how well the incident's Behavioral DNA fits historical patterns.
2. Computes the dual-paradigm composite novelty score:
   $$\text{dist}_{\text{cent}} = 1.0 - \langle \mathbf{v}_{\text{norm}}, \mathbf{c}_{\text{unit}} \rangle$$
   $$\text{raw\_if} = \text{decision\_function}(\mathbf{v}_{\text{norm}})$$
   $$\text{Novelty Score} = 0.5 \times \text{dist}_{\text{cent}} + 0.5 \times \text{norm\_if}$$
3. Evaluates **Behavioral Pattern Fit** ($\text{Pattern Fit Score} = 1.0 - \text{Novelty Score}$, categorized as *High Fit*, *Moderate Fit*, or *Low Fit (Atypical Combination)*).
4. Categorizes into empirical novelty tiers based on Phase 9 calibrated quantiles:
   - **Standard Behavioral Pattern** ($< 0.4363$, Bottom 95%)
   - **Moderate Behavioral Novelty** ($[0.4363, 0.5985)$, Top 5%)
   - **High Behavioral Outlier** ($[0.5985, 0.7383)$, Top 1%)
   - **Extreme Behavioral Outlier** ($\ge 0.7383$, Top 0.1%)
5. Triggers warning banner if unusual: **`⚠️ NOVEL BEHAVIORAL PATTERN`** (*"This incident contains a behavioral combination that does not closely match the major patterns learned from the historical dataset."*).
6. Identifies the most unusual supported behavioral factors ($|\Delta_j| \ge 0.08$) with human-readable labels, baseline comparisons, and directional indicators (`Elevated` vs `Suppressed`).
7. Strictly enforces non-offender attribution guidelines (see [NOVEL_BEHAVIOR.md](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/docs/NOVEL_BEHAVIOR.md)).

### Stage 8: Explainability (Exact Additive Attribution)
1. Decomposes the cosine similarity against the top matched historical incident:
   $$\text{sim}(\mathbf{u}, \mathbf{v}) = \sum_{j=1}^{70} u_j v_j$$
2. Sums contributions across each of the 7 feature groups and computes percentage share:
   $$\text{share}_g = \frac{\sum_{j \in g} u_j v_j}{\text{sim}(\mathbf{u}, \mathbf{v})} \times 100\%$$
3. Identifies the top positive contributing features with human-readable descriptions.
4. Highlights contextual semantic differences (operational timing delta, weapon presence contrast, statutory category discrepancy).

### Stage 9: DNA Comparison & Subprofile Radar
Extracts the 7 subprofile energy dimensions for both the user incident and the top historical match to power radar overlay visualizations.

### Stage 10: Technical Metadata & Response Assembly
Measures precise execution latency in milliseconds and returns the unified analysis payload containing all canonical and frontend-compatible keys.

---

## 4. Structured Analysis Response Schema

The backend returns a unified JSON dictionary containing the **10 standard analytical sections**:

| Section Key | Description | Key Contents |
| :--- | :--- | :--- |
| `incident_summary` | Human-readable synthesis of submitted inputs | Scenario title, temporal, classification, environmental, force, demographics, economics, harm |
| `behavioral_dna` | Dual-representation Behavioral DNA | 70D unit $L_2$ vector, 7 subprofile energy values, active traits, dynamic human fingerprint |
| `dna_similarity` | Aggregate similarity metrics | Top match %, mean top-5 %, min top-5 %, closest incident ID, metric name |
| `similar_historical_incidents` | Top-5 nearest historical neighbors | Rank, incident ID, similarity %, cosine distance, category, cluster, subprofile similarities |
| `cross_crime_matches` | Shared modus operandi across statutory classes | Dominant cross-crime pattern ID, pattern name, represented categories, cross-category matches |
| `hidden_behavioral_patterns` | Cluster archetype assignment | Cluster ID ($0 \dots 7$), name, macro category, distance to centroid, cluster summary |
| `why_similar` | Exact additive explainability attribution | Group contributions & % shares, top contributing features, semantic differences |
| `behavioral_evolution` | Temporal baseline alignment | Calendar month, quarter, hour, aligned longitudinal shifts, baseline interpretation |
| `novelty` | Unsupervised anomaly evaluation | Novelty score, novelty tier, percentile description, distance to centroid, unusual features |
| `technical_metadata` | Engine performance & integrity metadata | Version, analysis ID, execution time (ms), vector dimension (70), index size (220,663) |

---

## 5. Verification & Test Suite

The engine is validated by automated test suites in `tests/test_analysis_engine.py` and `tests/test_user_to_dna.py`:

```bash
.venv/bin/pytest tests/test_analysis_engine.py -v
```

### Key Automated Proofs:
1. **Pipeline Completeness (`test_complete_analysis_pipeline_structure`)**:
   - Confirms that all 10 canonical sections are present and populated.
   - Verifies mathematical identity between cosine distance and similarity: $\text{sim} = (1 - d) \times 100$.
   - Verifies exact additive attribution efficiency: $\sum \text{share}_g \approx 100\%$.
2. **Dynamic Non-Hardcoded Results (`test_real_model_results_not_hardcoded`)**:
   - Proves that distinct incident inputs (e.g. Armed Commercial Robbery vs Daytime Bicycle Theft) produce different similarity percentages, different matched incident IDs, different cluster archetypes, and different novelty scores.
3. **Immutability & Zero Retraining (`test_models_are_not_retrained_per_request`)**:
   - Compares cluster center matrices before and after repeated analysis calls: $\mathbf{C}_{\text{after}} \equiv \mathbf{C}_{\text{before}}$.
   - Confirms historical index size remains fixed.
4. **API Endpoint Integration (`test_api_endpoint_integration`)**:
   - Validates that `POST /api/analyze/input` wraps `CrimeDnaAnalysisEngine` and returns HTTP 200 with the full schema.

---

## 6. Full Test Suite Results

All **106 tests** across the entire repository pass with zero errors:
```
tests/test_analysis_engine.py::test_complete_analysis_pipeline_structure PASSED
tests/test_analysis_engine.py::test_real_model_results_not_hardcoded PASSED
tests/test_analysis_engine.py::test_models_are_not_retrained_per_request PASSED
tests/test_analysis_engine.py::test_api_endpoint_integration PASSED
...
======================= 106 passed, 2 warnings in 13.45s =======================
```
