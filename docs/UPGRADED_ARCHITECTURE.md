# CRIME DNA — Upgraded Product Layer Architecture
**System:** CRIME DNA Input-Driven Behavioral Analysis Platform  
**Status:** Architecture & Design Specification (Phases 1–15 Preserved)  
**Document:** `docs/UPGRADED_ARCHITECTURE.md`  
**Execution Rule:** Architecture specification only. No implementation code or training executed.

---

## 1. Core Architectural Principles & Paradigm

CRIME DNA is expanding from an investigative retrospective search engine into a **real-time, input-driven behavioral analysis platform**.

### Primary Invariants:
1. **Preservation of Existing Phases 1–15:** The complete historical pipeline, preprocessed data, trained models, serialization artifacts, test suite (88/88 passing tests), and existing frontend dashboard pages are 100% preserved.
2. **Immutable Knowledge Base:** The historical dataset (`crime_dna_ml.csv` / `crime_dna_cleaned.csv`, $N=220,663$) and its 70D vector matrix remain an immutable reference ground truth.
3. **No Dynamic Model Retraining:** User-submitted incidents **never** mutate model weights or append to the historical index during operational analysis. Retraining for user requests is strictly forbidden.
4. **Single-Pipeline Feature Parity:** Newly submitted incident parameters pass through the exact same feature transformation mathematical logic and scaling boundaries as the historical corpus, ensuring strictly commensurate 70D vectors.
5. **Multi-Faceted Analytical Output:** A single user submission yields 8 synchronous analytical perspectives: Behavioral DNA, Cross-Crime Similarity, Similar Historical Incidents, Hidden Behavioral Patterns, Why Similar? (XAI), Behavioral Evolution Context, Novel Behavioral Patterns, and Direct DNA Comparison.
6. **Strict Ethical Guardrail:** Explicit disclaimer maintained across all interfaces:
   > *"CRIME DNA identifies behavioral similarity and patterns between crime incidents. It does not identify offenders, determine guilt, or establish that incidents were committed by the same person."*

---

## 2. High-Level System Architecture Diagram

```
=================================================================================================================
                                     CRIME DNA PLATFORM ARCHITECTURE
=================================================================================================================

  +-----------------------------------------------------------------------------------------------------------+
  |                                     IMMUTABLE REFERENCE KNOWLEDGE BASE                                    |
  |                                                                                                           |
  |  Historical crime_dna_ml.csv (220,663 records)                                                            |
  |         ↓                                                                                                 |
  |  Existing Preprocessing (src/data/cleaner.py) -> crime_dna_cleaned.csv (195 cols)                         |
  |         ↓                                                                                                 |
  |  Existing Behavioral DNA Engine (src/features/dna_encoder.py) -> 70D features                             |
  |         ↓                                                                                                 |
  |  Existing Models, Indexes & Artifacts (data/processed/):                                                  |
  |  ├── Similarity Index: NearestNeighbors Cosine Index (knn_index.joblib, 220,663 x 70 matrix)              |
  |  ├── Clustering Engine: MiniBatchKMeans Spherical (kmeans_model.joblib, k=8 centroids)                   |
  |  ├── Anomaly Detector: IsolationForest (isolation_forest.joblib) + Centroid Distances                    |
  |  ├── Cross-Crime Engine: Discovered Cross-Category MO Convergences (cross_crime_patterns.json)            |
  |  ├── Evolution Engine: Longitudinal Trajectories & ANOVA Shift Baselines (timeline_dashboard.json)       |
  |  └── Explainer Engine: Additive Cosine Attribution Model (src/models/explainability/)                     |
  +-----------------------------------------------------------------------------------------------------------+
                                                      │
                                                      │ (Preloaded into memory at startup)
                                                      ▼
  +-----------------------------------------------------------------------------------------------------------+
  |                                     CRIME DNA ANALYSIS ENGINE (NEW PRODUCT LAYER)                         |
  |                                                                                                           |
  |  [ Application State & Model Registry (src/api/state.py) ] <--- In-Memory Fast Evaluation                 |
  +-----------------------------------------------------------------------------------------------------------+
                                                      ▲
                                                      │
  +---------------------------------------------------+-------------------------------------------------------+
  |                                          USER INPUT INGESTION PIPELINE                                    |
  |                                                                                                           |
  |  New User Incident Parameters (Form / JSON / Scenario Template)                                           |
  |         ↓                                                                                                 |
  |  Input Schema Validation (Pydantic IncidentInputRequest)                                                  |
  |         ↓                                                                                                 |
  |  Same Preprocessing & Empirical Scaling (src/features/input_bridge.py)                                    |
  |         ↓                                                                                                 |
  |  Same Behavioral DNA Representation (70D Bounded Vector on Unit Hypersphere)                              |
  +-----------------------------------------------------------------------------------------------------------+
                                                      │
                                                      ▼
  +-----------------------------------------------------------------------------------------------------------+
  |                                     UNIFIED REAL-TIME 8-POINT ANALYSIS                                    |
  |                                                                                                           |
  |  ├── 1. Behavioral DNA Fingerprint (70 dimensions, 7 sub-profile energy scores)                            |
  |  ├── 2. Cross-Crime Similarity (convergence against legally distinct crime categories)                    |
  |  ├── 3. Similar Historical Incidents (Top-K nearest neighbors from 220,663 records)                       |
  |  ├── 4. Hidden Behavioral Pattern (Spherical archetype assignment, distance to centroid)                 |
  |  ├── 5. "Why Similar?" Explanation (Exact additive feature & group cosine attributions)                   |
  |  ├── 6. Behavioral Evolution Context (historical seasonal/temporal baseline comparison)                  |
  |  ├── 7. Novel Behavioral Pattern (Dual-paradigm novelty score, outlier tier, unusual deviations)          |
  |  └── 8. Direct DNA Comparison (Side-by-side metric overlay against top matched historical case)           |
  +-----------------------------------------------------------------------------------------------------------+
                                                      │
                                                      ▼
  +-----------------------------------------------------------------------------------------------------------+
  |                                           PRESENTATION LAYER (REACT 19)                                   |
  |                                                                                                           |
  |  Interactive Case Input Studio -> Live Radar -> Archetype Badges -> Similar Incidents -> XAI Breakdown    |
  +-----------------------------------------------------------------------------------------------------------+
=================================================================================================================
```

---

## 3. ML Architecture

### 3.1 The Reference Knowledge Base vs. Runtime Query Vector
The machine learning architecture operates on a strict **dual-tier separation**:
- **Tier 1 (Reference Knowledge Base):** The 220,663 historical incidents mapped into 70D normalized vectors:
  $$\mathbf{M} \in \mathbb{R}^{220663 \times 70}, \quad \|\mathbf{M}_{i,*}\|_2 = 1.0 \quad \forall i$$
- **Tier 2 (Ad-Hoc Query Vector):** The user-submitted case parameter dictionary $\mathbf{D}_{\text{input}}$ transformed into:
  $$\mathbf{x}_{\text{raw}} \in [0.0, 1.0]^{70} \implies \mathbf{u}_{\text{input}} = \frac{\mathbf{x}_{\text{raw}}}{\|\mathbf{x}_{\text{raw}}\|_2} \in \mathbb{R}^{70}$$

### 3.2 The Preprocessing Bridge (`src/features/input_bridge.py`)
To prevent feature drift or dimension mismatch, an input adapter bridge translates human-friendly input forms into the exact 195-column input format expected by the existing `BehavioralDNAEncoder`:
1. **Explicit Inputs:** Direct mappings for specified fields (`incident_hour`, `incident_month`, `incident_weekday`, `has_weapon`, `victim_count`, `offender_count`, `property_value`, etc.).
2. **Deterministic Defaults:** For fields not specified by the investigator, the bridge uses empirical modes/medians calculated during the Phase 1 audit:
   - Population: $25,000$ (Small municipality tier)
   - Victims: $1$ (Average adult victim, age $38.0$)
   - Offenders: $1$ (Average offender, age $31.0$)
   - Weapon count: $1$ (if weapon present, otherwise $0$)
   - Zero-variance / dropped columns: strictly omitted.
3. **Encoding & Cyclical Mapping:** Directly executes:
   - Diurnal cycle: $\sin(2\pi h / 24), \cos(2\pi h / 24) \in [0, 1]$
   - Annual cycle: $\sin(2\pi (m - 1) / 12), \cos(2\pi (m - 1) / 12) \in [0, 1]$
   - Weekly cycle: $\sin(2\pi w / 7), \cos(2\pi w / 7) \in [0, 1]$
   - Log-transformed population and property values bounded by empirical caps.

---

## 4. Model & Index Lifecycle

```
[ Application Launch ]
         │
         ▼
[ FastAPI Lifespan Handler: state.load_all() ]
         │
         ├─► Load knn_index.joblib + normalized_dna_matrix.npy (RAM memory-mapped)
         ├─► Load kmeans_model.joblib (8 centroids in float32)
         ├─► Load isolation_forest.joblib (150 decision trees)
         ├─► Load cross_crime_patterns.json & cluster_profiles.json
         ├─► Load timeline_dashboard.json & significant_shifts.json
         └─► Load incident registries & metadata JSONs
         │
         ▼ (Takes ~1.25 seconds total)
[ All Models Status: ONLINE ]
         │
         ▼
[ Incoming User Requests (Concurrent, Read-Only) ]
         │
         ├─► Thread 1: POST /api/analyze/input ──────┐
         ├─► Thread 2: GET  /api/clusters     ──────┼──► Query in-memory models (NO DISK I/O)
         └─► Thread 3: POST /api/analyze/input ──────┘
         │
         ▼
[ Zero State Mutation ] (Weights remain 100% immutable across all requests)
```

### Lifecycle Constraints:
1. **Startup Synchronization:** Models load strictly once during FastAPI server lifespan. No endpoint performs ad-hoc `joblib.load()` calls.
2. **Read-Only Concurrency:** The underlying Scikit-Learn estimators (`NearestNeighbors.kneighbors`, `MiniBatchKMeans.predict`, `IsolationForest.score_samples`) are thread-safe for inference (`read-only`).
3. **No Dynamic Model Re-fitting:** New inputs generate ephemeral vectors $\mathbf{u}_{\text{input}}$. They are never appended to `normalized_dna_matrix.npy` or serialized to disk.

---

## 5. Backend Architecture

### 5.1 Directory Layout for Upgrade
All existing files remain intact. New product capabilities are added modularly:

```
src/
├── api/
│   ├── routes/
│   │   ├── health.py             # Existing
│   │   ├── stats.py              # Existing
│   │   ├── incidents.py          # Existing
│   │   ├── similarity.py         # Existing
│   │   ├── clusters.py           # Existing
│   │   ├── cross_crime.py        # Existing
│   │   ├── evolution.py          # Existing
│   │   ├── anomaly.py            # Existing
│   │   ├── explain.py            # Existing
│   │   ├── analysis.py           # [NEW] Unified input analysis endpoints
│   │   └── history.py            # [NEW] Ephemeral user session analysis history
│   ├── schemas.py                # Enhanced with input & multi-point response schemas
│   ├── state.py                  # Enhanced with input-analysis coordinator
│   └── main.py                   # Mounts new routes
├── features/
│   ├── config.py                 # Existing
│   ├── dna_encoder.py            # Existing
│   └── input_bridge.py           # [NEW] Dict-to-features adaptation bridge
├── models/
│   ├── analysis_coordinator.py   # [NEW] Orchestrates the 8-point analysis
│   └── ... (existing models untouched)
```

### 5.2 The Analysis Coordinator (`src/models/analysis_coordinator.py`)
Coordinates the 8 analytical perspectives synchronously in memory:
1. Calls `input_bridge.encode(input_data)` $\to \mathbf{u}_{\text{input}} \in \mathbb{R}^{70}$.
2. Calls `state.similarity_engine.find_similar_by_vector(\mathbf{u}_{\text{input}}, top_k=5)`.
3. Calls `state.clusterer.predict_cluster(\mathbf{u}_{\text{input}})`.
4. Evaluates `cross_crime` convergence relative to assigned cluster.
5. Evaluates `novelty_detector.score_vector(\mathbf{u}_{\text{input}})`.
6. Computes exact additive attribution of $\mathbf{u}_{\text{input}}$ against the #1 matched historical incident.
7. Contextualizes the input against longitudinal behavioral shifts (e.g. night surge, seasonal trends).
8. Formats the unified response payload in $< 25\text{ ms}$.

---

## 6. API Flow & Endpoints

### 6.1 New Endpoints

| Method | Endpoint | Purpose | Request Body | Response Body |
|---|---|---|---|---|
| `POST` | `/api/analyze/input` | Execute full 8-point behavioral analysis on user input | `IncidentInputRequest` | `InputAnalysisResponse` |
| `GET` | `/api/analyze/presets` | Retrieve predefined scenario templates | None | `List[ScenarioPreset]` |
| `POST` | `/api/analyze/compare` | Direct comparison between inputted incident and specific historical ID | `InputCompareRequest` | `ComparisonResponse` |
| `GET` | `/api/history` | Retrieve current session's recent analyses | Query: `session_id` | `List[HistoryItemSummary]` |
| `DELETE`| `/api/history/{id}` | Clear an item from session history | Path: `history_id` | `SuccessResponse` |

### 6.2 Sequence Flow for `POST /api/analyze/input`

```
Client (Browser)             FastAPI Router           InputBridge          Memory Models (State)
      │                            │                       │                        │
      ├── POST /api/analyze/input ─►│                       │                        │
      │   (JSON input params)      ├─ Validate Schema      │                        │
      │                            ├──────────────────────►│                        │
      │                            │  Convert Dict         │                        │
      │                            │  Apply Normalization  │                        │
      │                            │◄─ Return 70D Vector ──┘                        │
      │                            │                                                │
      │                            ├─ kneighbors(u_input) ─────────────────────────►│ (NearestNeighbors)
      │                            │◄─ Top-5 Matches + Subprofiles ─────────────────┤
      │                            │                                                │
      │                            ├─ predict(u_input) ────────────────────────────►│ (MiniBatchKMeans)
      │                            │◄─ Cluster Centroid & Distance ─────────────────┤
      │                            │                                                │
      │                            ├─ score_samples(u_input) ──────────────────────►│ (IsolationForest)
      │                            │◄─ Novelty Score & Tier ────────────────────────┤
      │                            │                                                │
      │                            ├─ Compute Additive Attribution (u_input * v_top)│ (Explainer)
      │                            ├─ Assemble 8-Point Analysis JSON                │
      │◄── 200 OK (Full Analysis) ─┤                                                │
```

---

## 7. User Input Flow & Preprocessing Bridge

The user inputs natural case characteristics without needing to understand machine learning vectors or feature indices.

### Input Form Categorization:
```
[ INVESTIGATOR INPUT STUDIO ]
├── 1. Temporal Parameters
│   ├── Hour of Day (0–23 slider)
│   ├── Month of Year (1–12 dropdown)
│   ├── Day of Week (Monday–Sunday)
│   └── Indicators: Weekend (auto/toggle), Nocturnal execution (auto/toggle)
├── 2. Crime Type & Complexity
│   ├── Statutory Target Violation: Person, Property, Society, or Compound
│   ├── Total Offenses Count (1–4+)
│   └── Offense Status: Completed vs. Attempted
├── 3. Location & Scene Context
│   ├── Environment / Urban Density Tier (Small Town, Suburban, Metropolitan Core)
│   ├── Jurisdiction: Municipal Police vs. County Sheriff vs. State Police
│   └── Location Breadth: Single Location vs. Multiple Scenes
├── 4. Method, Weapons & MO
│   ├── Weapon Presence: Unarmed vs. Armed
│   ├── Weapon Type Count & Multi-Weapon Flag
│   ├── Criminal Enterprise / Gang Activity Indicator
│   └── Relationship Dynamics: Stranger vs. Known Relationship
├── 5. People & Demographics
│   ├── Victim Count (1–5+) & Average Age (or Unknown)
│   └── Offender Count (Solo vs. Co-Offenders) & Average Age (or Unknown)
├── 6. Property & Economic Targeting
│   ├── Property Involved (Yes/No)
│   ├── Stolen Property Count
│   └── Estimated Property Value ($)
└── 7. Context, Harm & Resolution
    ├── Physical Injury (Yes/No)
    ├── Substance / Suspected Narcotics Involvement (Yes/No)
    ├── Apparent Bias / Hate Motivation (Yes/No)
    └── Resolution: Immediate On-Scene Arrest vs. Fled Scene
```

---

## 8. Comprehensive 8-Point Analysis Flow

When `POST /api/analyze/input` is invoked, the engine generates:

1. **Behavioral DNA Fingerprint:**
   - 70-dimensional unit vector $\mathbf{u}_{\text{input}}$.
   - 7 Sub-profile Energy Scores ($0.0–100.0\%$): Temporal, Crime Characteristics, Location Setting, Method & Weapon, People, Property, Context/Harm.
   - Top-5 Most Active Behavioral Traits.
2. **Cross-Crime Similarity Mapping:**
   - Evaluates whether the inputted MO aligns with historical crimes across different legal categories.
   - Shows cross-category convergence percentages (e.g., *"This Property-classified case shares an 88% operational MO with Armed Robberies against Persons"*).
3. **Similar Historical Incidents Retrieval:**
   - Top-5 nearest neighbors from the 220,663 indexed records.
   - Exact Cosine Similarity percentage ($0.0–100.0\%$).
   - Cosine distance, statutory category, and archetype for each match.
   - Independent subprofile similarity scores for each match.
4. **Hidden Behavioral Pattern Discovery:**
   - Assignment to one of the 8 discovered Spherical MiniBatchKMeans clusters.
   - Distance to cluster centroid on unit hypersphere.
   - Descriptive archetype summary (e.g., *"Cluster 2: Commercial & Structural Burglary"*).
5. **"Why Similar?" Explainability (XAI):**
   - Exact additive feature attributions ($c_j = u_j \cdot v_j$) against the #1 matched historical incident.
   - Group-level contribution shares summing to $100\%$.
   - Semantic differences list highlighting contrasting elements (e.g., different hour, different property status).
6. **Behavioral Evolution & Temporal Context:**
   - Contextualizes the input against the historical timeline (e.g., *"Nocturnal incidents like this exhibit a 3.92% surge during summer months in the historical baseline"*).
7. **Novel Behavioral Pattern (Anomaly / Outlier Evaluation):**
   - Composite novelty score: $0.6 \cdot D_{\text{centroid}} + 0.4 \cdot S_{\text{isolation}}$.
   - Tier Classification: Baseline ($< 95\text{th}$ percentile), Moderate Novelty ($95\text{th}–99\text{th}$ percentile), or High Behavioral Outlier ($\ge 99\text{th}$ percentile).
   - Top unusual feature deviations relative to the assigned cluster centroid.
8. **DNA Comparison:**
   - Side-by-side radar overlay comparing the input's Behavioral DNA with the nearest historical incident's DNA.

---

## 9. Concrete Result Data Structure

### 9.1 Request Schema (`IncidentInputRequest`)
```json
{
  "scenario_name": "Nocturnal Armed Commercial Burglary",
  "temporal": {
    "incident_hour": 2,
    "incident_month": 7,
    "incident_weekday": 5,
    "is_weekend": true,
    "is_night": true
  },
  "crime": {
    "crime_category": "Property",
    "offense_count": 2,
    "is_attempted": false
  },
  "location": {
    "population_tier": "cities_from_25,000_thru_49,999",
    "location_count": 1,
    "is_state_police": false
  },
  "method": {
    "has_weapon": true,
    "weapon_count": 1,
    "is_multi_weapon": false,
    "has_criminal_activity": false,
    "has_relationship": false
  },
  "people": {
    "victim_count": 1,
    "victim_age": 42.0,
    "offender_count": 2,
    "offender_age": 28.0
  },
  "property": {
    "has_property": true,
    "has_stolen_property": true,
    "stolen_count": 3,
    "property_value": 4500.0,
    "is_cargo_theft": false
  },
  "context": {
    "has_injury": false,
    "has_drug": false,
    "has_bias": false,
    "has_arrest_on_scene": false
  }
}
```

### 9.2 Response Schema (`InputAnalysisResponse`)
```json
{
  "analysis_id": "ANALYSIS_20261008_9F4B1A",
  "timestamp": "2026-10-08T21:40:00Z",
  "scenario_name": "Nocturnal Armed Commercial Burglary",
  "behavioral_dna": {
    "vector_dimension": 70,
    "subprofile_energies": {
      "temporal_dynamics": 88.5,
      "crime_characteristics": 65.2,
      "location_and_environment": 72.0,
      "method_and_activity": 81.4,
      "people_and_demographics": 54.3,
      "property_and_economics": 92.1,
      "context_harm_resolution": 30.0
    },
    "top_active_traits": [
      { "feature": "time_is_night", "value": 1.0, "description": "Nighttime execution" },
      { "feature": "has_weapon", "value": 1.0, "description": "Weapon deployed" },
      { "feature": "is_co_offender", "value": 1.0, "description": "Multiple offenders acting in concert" }
    ]
  },
  "cluster_assignment": {
    "cluster_id": 2,
    "cluster_name": "Commercial & Structural Burglary",
    "macro_category": "Property",
    "distance_to_centroid": 0.2841,
    "cluster_summary": "Nighttime forced-entry structural burglaries targeting commercial facilities."
  },
  "cross_crime_mapping": {
    "dominant_cross_crime_pattern": "CCP_02",
    "cross_crime_pattern_name": "Cross-Category Commercial Exploitation",
    "represented_categories": ["Property (92.4%)", "Person (6.2%)", "Society (1.4%)"],
    "behavioral_synergy": "Shares core entry and weapon modalities with commercial armed robbery."
  },
  "novelty_assessment": {
    "novelty_score": 0.412,
    "novelty_tier": "Baseline Behavior",
    "percentile": "72nd percentile",
    "distance_to_nearest_cluster": 0.2841,
    "nearest_cluster_name": "Commercial & Structural Burglary",
    "unusual_features": []
  },
  "similar_historical_incidents": [
    {
      "rank": 1,
      "incident_id": "INC_084321",
      "similarity_score_pct": 94.6,
      "cosine_distance": 0.054,
      "primary_crime_category": "Property",
      "cluster_name": "Commercial & Structural Burglary",
      "subprofile_similarity_pct": {
        "temporal_dynamics": 96.2,
        "crime_characteristics": 91.0,
        "location_and_environment": 95.4,
        "method_and_activity": 93.8,
        "people_and_demographics": 90.5,
        "property_and_economics": 98.1,
        "context_harm_resolution": 99.0
      }
    }
  ],
  "why_similar_explanation": {
    "target_incident_id": "INC_084321",
    "overall_similarity_pct": 94.6,
    "group_attributions": [
      { "group": "property_and_economics", "display_name": "Property & Economics", "share_pct": 32.4 },
      { "group": "temporal_dynamics", "display_name": "Temporal Dynamics", "share_pct": 28.1 }
    ],
    "main_contributing_similarities": ["Similar property & economics", "Similar temporal dynamics"],
    "semantic_differences": ["Slightly higher stolen property volume in INC_084321"]
  },
  "evolutionary_context": {
    "seasonal_note": "Nocturnal property offenses peak in Q3 (summer) and holiday periods.",
    "longitudinal_shift_alignment": "Aligns with Shift 03 (Commercial Retail and Storage Surge)."
  }
}
```

---

## 10. Frontend Architecture

### 10.1 Page Integration: `InputAnalysisPage.tsx`
A dedicated top-level page mounted in `App.tsx` alongside existing pages:

```
[ Nav Header: CRIME DNA ]
├── Overview Dashboard
├── [NEW] Case Simulator / Input Studio  <--- (Primary New Product Entry Point)
├── Incident Analyzer (Historical Archive)
├── Similarity View
├── Why Similar?
├── Behavioral Patterns
├── Cross-Crime Links
├── Behavioral Evolution
└── Novel Behavior
```

### 10.2 Component Hierarchy for Input Studio
```
InputAnalysisPage.tsx
├── Header: Ethical Advisory Banner & Title
├── ScenarioPresetBar.tsx (Quick-load: Armed Robbery, Burglary, Domestic Assault, Shoplifting)
├── Two-Column Layout:
│   ├── Left Column: Case Parameter Studio
│   │   ├── AccordionSection: Temporal & Diurnal Settings (Sliders & Toggles)
│   │   ├── AccordionSection: Crime Type & Statutory Violations
│   │   ├── AccordionSection: Setting & Urban Population Tier
│   │   ├── AccordionSection: Method, Weapons & Relationship Dynamics
│   │   ├── AccordionSection: People & Demographics (Victims & Offenders)
│   │   ├── AccordionSection: Property & Economic Impact
│   │   └── AccordionSection: Context, Harm & Resolution
│   │   └── Action: [ Run Real-Time Behavioral Analysis ] (or Live Auto-Update toggle)
│   │
│   └── Right Column: Live Multi-Point Behavioral Intelligence Dashboard
│       ├── KPI Bar: Cluster Archetype Badge | Novelty Tier Pill | Match Confidence %
│       ├── Visual Panel:
│       │   ├── DNARadarChart.tsx (Inputted 70D DNA vs Top Match Overlay)
│       │   └── SubprofileBars.tsx (7 Bounded Behavioral Energy Scores)
│       ├── Section: Top-5 Similar Historical Cases Feed (with one-click "Deep Compare")
│       ├── Section: Cross-Crime Convergence Alert (Cross-statutory MO detection)
│       ├── Section: "Why Similar?" Additive Feature Attribution Cards
│       └── Section: Scenario Sensitivity Tweaker ("What-If" instant parameter tuning)
```

---

## 11. Multi-User Handling & Concurrency

1. **Stateless Backend Processing:**
   - Every `POST /api/analyze/input` request is completely stateless and self-contained.
   - The server maintains zero session-specific mutated model state.
2. **Asynchronous Non-Blocking Execution:**
   - Built on FastAPI (`asyncio`) running on Uvicorn.
   - CPU-bound vector algebra (NumPy matrix dot products, SciPy distances) releases GIL where applicable and runs in $< 20\text{ ms}$, effortlessly supporting hundreds of concurrent analysis requests on standard hardware.
3. **No Lock Contention:**
   - The memory-mapped vector matrix and Scikit-Learn tree models are accessed concurrently via pure read operations (`no threading locks required`).
4. **Rate Limiting & DoS Protection:**
   - Standard IP-based rate limiting (e.g. 60 requests/minute per client) to protect CPU against automated brute-force scraping.

---

## 12. Analysis History Strategy

### 12.1 Ephemeral Session Storage (Client-Side Primary)
- **Primary Mechanism:** Browser `localStorage` / `sessionStorage`.
- Stores the last 20 user analyses locally on the investigator's device.
- Eliminates GDPR/privacy concerns and multi-tenant data contamination: case parameters never linger in a shared server database unless explicitly saved.

### 12.2 Server-Side Ephemeral Cache (Optional Fallback)
- In-memory `LRUCache(maxsize=1000)` indexed by `analysis_id`.
- Automatically evicts after 2 hours.
- Enables sharing an analysis link with a mentor or peer (e.g. `http://.../#/analysis?id=ANALYSIS_9F4B1A`).

### 12.3 Export Capabilities
- Built-in one-click **"Export Case Assessment Report"**:
  - Download as machine-readable JSON.
  - Printable / PDF-friendly summary view with DNA radar, cluster assignment, and nearest historical references.

---

## 13. Caching & Performance Optimization Strategy

1. **Pre-Normalized Historical Matrix:**
   - The 220,663 incident vectors are pre-normalized to unit $L_2$ norm at startup.
   - Nearest-neighbor search performs direct dot products without recomputing norms for historical vectors.
2. **Unit Norm Invariant for Query Vectors:**
   - Input vectors are normalized once at the boundary:
     $$\mathbf{u}_{\text{input}} = \frac{\mathbf{x}_{\text{input}}}{\|\mathbf{x}_{\text{input}}\|_2}$$
   - Cosine distances to all 8 cluster centroids computed in $< 0.1\text{ ms}$ via single matrix multiplication:
     $$\mathbf{d} = 1.0 - (\mathbf{C} \cdot \mathbf{u}_{\text{input}}), \quad \mathbf{C} \in \mathbb{R}^{8 \times 70}$$
3. **Sub-profile Slicing via Index Arrays:**
   - Group feature indices are pre-indexed integer lists (`state.group_indices`), enabling sliced dot products without string lookups.
4. **Target Response Latency:**
   - End-to-end API response time: **15–25 milliseconds**.

---

## 14. Error Handling & Validation Matrix

| Input Scenario | Validation Rule | Error / Handling Response |
|---|---|---|
| `incident_hour` out of bounds | $0 \le \text{hour} \le 23$ | `422 Unprocessable Entity`: `"incident_hour must be between 0 and 23"` |
| `incident_month` out of bounds | $1 \le \text{month} \le 12$ | `422 Unprocessable Entity`: `"incident_month must be between 1 and 12"` |
| Unspecified optional fields | Any missing demographic or economic field | Handled smoothly: Imputes empirical baseline defaults (mode/median) |
| Negative counts or values | Count $\ge 0$, Value $\ge 0$ | `422 Unprocessable Entity`: `"Counts and monetary values cannot be negative"` |
| Zero-Norm Vector (All features = 0) | $\|\mathbf{x}\|_2 = 0$ | Handled smoothly: Falls back to uniform baseline distribution |
| High-Concurrency Spike | Server saturated | Standard non-blocking async queue; returns standard 503 if timeout exceeded |

---

## 15. Strict Ethical & Investigative Guardrails

The upgraded architecture embeds explicit ethical constraints at both code and presentation levels:

1. **Mandatory Disclaimer Enforcement:**
   Every API response from `/api/analyze/input` includes the static metadata field:
   ```json
   {
     "ethical_advisory": "CRIME DNA identifies behavioral similarity and patterns between crime incidents. It does not identify offenders, determine guilt, or establish that incidents were committed by the same person."
   }
   ```
2. **Terminology Sanitization:**
   - Predictions are labeled **"Behavioral Archetype Assignment"**, NOT *"Criminal Profiling"*.
   - Outliers are labeled **"Novel Behavioral Pattern"** or **"Behavioral Outlier"**, NOT *"Suspicious Person"* or *"Guilty Individual"*.
3. **No Identity Ingestion:**
   The input schema strictly rejects any Personally Identifiable Information (PII) such as suspect names, addresses, social security numbers, or biometric data. The schema accepts only behavioral, temporal, and situational attributes.

---

## Summary of Upgrade Scope

| Phase / Component | Current State (Phases 1–15) | Upgraded Product Layer |
|---|---|---|
| **Primary Interaction** | Browse archives & search historical IDs | Input novel case parameters & simulate scenarios |
| **DNA Generation** | Precomputed for 220,663 records | Real-time dynamic synthesis for any input |
| **Similarity Matching** | ID-to-ID lookup | Dynamic Query Vector to 220,663 Reference Base |
| **Clustering** | Static exploration of 8 clusters | Real-time archetype classification of new cases |
| **Anomaly Detection** | Precomputed list of 100 outliers | Real-time novelty scoring & tier classification |
| **Explainability (XAI)** | Historical ID pairs only | Input-to-Historical pair additive attribution |
| **Frontend Experience** | Retrospective analytics dashboard | Interactive Investigative Studio & Simulator |
| **Model Weights & Base** | Immutable | **100% Immutable (Zero Retraining)** |

The architecture is complete, modular, non-destructive, and ready for systematic implementation upon your approval.
