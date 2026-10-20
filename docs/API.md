# CRIME DNA — Backend API Technical Manual & Reference
**Phase 11: Production-Grade RESTful API Architecture**

---

## 1. Overview & Architectural Design

The **CRIME DNA Backend API** is a high-performance RESTful service built with **FastAPI** and **Pydantic v2**. It wraps the entire machine learning pipeline—from the 70-dimensional Behavioral DNA fingerprint encoder to nearest-neighbor similarity search, unsupervised behavioral clustering, cross-crime pattern discovery, chronological evolution tracking, novelty/anomaly detection, and mathematically grounded explainability.

```
+------------------------------------------------------------------------------------+
|                                CRIME DNA FASTAPI                                   |
|                                                                                    |
|  +------------------+  +-------------------+  +------------------+  +-----------+  |
|  | Lifespan Startup |  | CORS & Middleware |  | Exception Router |  | OpenAPI   |  |
|  | Model Pre-load   |  | (Process-Time-Ms) |  | (Structured JSON)|  | & Swagger |  |
|  +--------+---------+  +---------+---------+  +--------+---------+  +-----+-----+  |
|           |                      |                     |                  |        |
|           +----------------------+----------+----------+------------------+        |
|                                             |                                      |
|                                   [ Global AppState ]                              |
|           +---------------------------------+--------------------------------+     |
|           |                                                                  |     |
|     +-----+------+  +-------------+  +-------------+  +------------+  +------+---+ |
|     | Similarity |  |  8 Clusters |  | Cross-Crime |  | Evolution  |  | Anomaly  | |
|     | KNN Index  |  |  Profiles   |  |  8 Patterns |  | Timeline   |  | Detector | |
|     |  (70-dim)  |  |  Centroids  |  |  Exemplars  |  |  & Shifts  |  | & Outliers| |
|     +-----+------+  +------+------+  +------+------+  +-----+------+  +------+---+ |
|           |                |                |               |                |     |
|           +----------------+----------------+---------------+----------------+     |
|                                             |                                      |
|                          [ Fast Incident Registry ]                                |
|                   220,663 Indexed Incidents (O(1) Hash Map)                        |
+------------------------------------------------------------------------------------+
```

### Core Architecture Highlights

1. **Lifespan Startup & Zero-Retraining Guarantee:**
   All machine learning artifacts (`knn_index.joblib`, `normalized_dna_matrix.npy`, `cluster_profiles.json`, `cross_crime_patterns.json`, `timeline_dashboard.json`, `isolation_forest.joblib`, and tabular indices) are loaded **once** at application startup via FastAPI's `@asynccontextmanager lifespan`. Incoming API requests **never retrain models or re-parse 100MB CSV files**.
2. **Sub-Millisecond Incident & DNA Lookups:**
   Incident identifiers are mapped to an in-memory row index hash table $O(1)$. Core metadata attributes, cluster assignments, anomaly scores, and 70-dimensional unit-norm Behavioral DNA vectors return in **under 1 millisecond** ($~0.05 \text{ ms}$ average).
3. **Nearest-Neighbor Retrieval:**
   Nearest-neighbor search across all 220,663 incident fingerprints runs in **under 35 milliseconds**, computing exact cosine distances and providing subprofile similarity breakdowns across the 7 behavioral domains.
4. **Environment-Aware & Zero Hardcoded Paths:**
   All paths are dynamically derived from the repository root via `Path(__file__).resolve().parent.parent.parent` and can be overridden through environment variables (`CRIME_DNA_WORKSPACE_ROOT`, `CRIME_DNA_DATA_DIR`, etc.).

---

## 2. Environment Configuration

All configurations can be controlled via environment variables or `.env` files:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `CRIME_DNA_HOST` | `0.0.0.0` | Network interface to bind the API server |
| `CRIME_DNA_PORT` | `8000` | Port to expose the FastAPI service |
| `CRIME_DNA_DEBUG` | `false` | Enables debug logging and verbose tracebacks |
| `CRIME_DNA_CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins |
| `CRIME_DNA_WORKSPACE_ROOT` | *(Workspace Directory)* | Root directory of the CRIME-DNA project |
| `CRIME_DNA_DATA_DIR` | `$WORKSPACE/data` | Master data directory |
| `CRIME_DNA_PROCESSED_DIR` | `$DATA/processed` | Processed features and artifacts directory |
| `CRIME_DNA_SIMILARITY_DIR` | `$PROCESSED/similarity_index` | Pre-built KNN index and normalized vectors |
| `CRIME_DNA_CLUSTERS_DIR` | `$PROCESSED/clusters` | K-Means model, cluster profiles, and labels |
| `CRIME_DNA_CROSS_CRIME_DIR`| `$PROCESSED/cross_crime` | Discovered cross-crime patterns and summaries |
| `CRIME_DNA_EVOLUTION_DIR` | `$PROCESSED/evolution` | Timeline dashboard and shift reports |
| `CRIME_DNA_ANOMALY_DIR` | `$PROCESSED/anomaly` | Isolation forest model and outlier tables |
| `CRIME_DNA_EXPLAIN_DIR` | `$PROCESSED/explainability` | Explanation metadata and sample scenarios |

---

---

## 3. Canonical Product APIs & Endpoints Catalog

The upgraded **CRIME DNA Product API layer** exposes 11 canonical, clean endpoints representing the core product capabilities. All endpoints are mounted both at the **root path** (`/endpoint`) for clean REST access and under the `/api` prefix (`/api/endpoint`) to ensure **100% backward compatibility** for existing API consumers and test suites.

### Canonical CRIME DNA Product Endpoints (Expected Capabilities)

| # | Method | Canonical Endpoint | Legacy / Backward Path | Capability & Purpose |
| :---: | :---: | :--- | :--- | :--- |
| **1** | `GET` | `/health` | `/api/health` | **System Health & Readiness:** Real-time health probe, component status, indexed incident count ($220,663$), and 70D vector dimension. |
| **2** | `GET` | `/stats` | `/api/stats` | **Corpus & Pipeline Statistics:** Benchmark dataset counts, feature taxonomy distributions, clustering summaries, and novelty tiers. |
| **3** | `POST` | `/analyze` | `/api/analyze`, `/api/analyze/input` | **Analyze Incident with CRIME DNA:** Encodes submitted incident into 70D DNA vector and returns 8 analytical perspectives in real time. |
| **4** | `GET` | `/analysis/{analysis_id}` | `/api/analysis/{analysis_id}`, `/api/analyze/records/{id}` | **Get Specific Incident Analysis:** Retrieves immutable, privacy-preserving stored analysis record by ID. Returns 404 if not found. |
| **5** | `GET` | `/analyses` | `/api/analyses`, `/api/analyze/records` | **Incident History & Analyses:** Paginated list of user-submitted analysis records with optional user ID, search, and category filters. |
| **6** | `GET` | `/patterns` | `/api/patterns` | **Explore Discovered Patterns:** Catalog of all 8 empirical behavioral archetypes with concise MO formulas and incident counts. |
| **7** | `GET` | `/patterns/{pattern_id}` | `/api/patterns/{pattern_id}` | **Pattern Profile & Details:** In-depth profile for a pattern (`0`-`7`, `CCP_00`-`CCP_07`, `PATTERN 01`-`08`), including crime categories and characteristics. Returns 404 if invalid. |
| **8** | `POST` | `/compare` | `/api/compare` | **Side-by-Side DNA Comparison:** Compares Incident A vs Incident B (custom or historical), computing DNA similarity and "What Changed?" analysis. Returns 400/422 on invalid input. |
| **9** | `GET` | `/evolution/{pattern_id}` | `/api/evolution/{pattern_id}` | **Pattern Longitudinal Evolution:** 3-stage temporal evolution (Early, Middle, Later) for the specified pattern archetype. Returns 404 if invalid. |
| **10**| `POST` | `/feedback` | `/api/feedback` | **Investigator Feedback:** Records human-in-the-loop evaluation data without modifying ML models. |
| **11**| `GET` | `/connection-map` | `/api/connection-map`, `/api/patterns/connection-map` | **Behavioral Connection Map:** Complete computed graph topology of Crime Categories and Behavioral Patterns. |

---

### Additional / Specialized ML Endpoints (Preserved for Deep Diagnostics)

| Method | Endpoint | Capability |
| :--- | :--- | :--- |
| `GET` | `/api/incidents/{incident_id}` | Full incident record from the 220,663 historical corpus |
| `GET` | `/api/incidents/{incident_id}/dna` | Unit L2-normalized 70D vector and subprofile energies |
| `GET` | `/api/similarity/similar/{incident_id}` | Nearest neighbors for a historical incident ID |
| `POST` | `/api/similarity/search` | Nearest neighbors query with custom parameters |
| `POST` | `/api/similarity/vector` | Nearest neighbors query with arbitrary 70D vector |
| `GET` | `/api/clusters` | Full unsupervised clustering metadata and centroids |
| `GET` | `/api/clusters/{cluster_id}` | Detailed cluster centroid and distinctive features |
| `GET` | `/api/cross-crime` | Full cross-crime pattern registry metadata |
| `GET` | `/api/cross-crime/{pattern_id}` | Exemplar pairs and inter-category similarity metrics |
| `GET` | `/api/evolution/timeline` | Global multi-cluster temporal distribution timeline |
| `GET` | `/api/evolution/shifts` | Statistically significant population-level behavioral shifts |
| `GET` | `/api/anomaly/summary` | Global anomaly score distributions and model configuration |
| `GET` | `/api/anomaly/outliers` | Paginated top outliers from historical corpus |
| `GET` | `/api/anomaly/{incident_id}` | Anomaly score and tier for a specific historical incident |
| `GET` | `/api/explain/{incident_1}/{incident_2}` | Direct contrastive SHAP-style attribution between two incidents |
| `POST` | `/api/explain` | Contrastive attribution via POST payload |
| `GET` | `/compare/presets` | Curated demonstrative comparison presets |
| `GET` | `/analyze/presets` | Curated demonstrative incident analysis presets |
| `GET` | `/feedback/summary` | Aggregate investigator feedback statistics |

---

## 4. Endpoint Specifications & Examples

### 1. Health and Readiness Check

#### `GET /api/health`
Checks whether all model artifacts are loaded in memory and ready to serve traffic.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "uptime_seconds": 142.35,
  "components_status": {
    "similarity_engine": "online",
    "clustering": "online",
    "cross_crime": "online",
    "evolution": "online",
    "anomaly_detection": "online",
    "explainability": "online",
    "incident_registry": "online"
  },
  "indexed_incidents": 220663,
  "vector_dimension": 70
}
```

---

### 2. Dataset & Pipeline Statistics

#### `GET /api/stats`
Returns global counts, cleaning transformations, feature taxonomy distribution, and novelty tier totals.

**Response `200 OK`:**
```json
{
  "dataset_name": "CRIME DNA Master Behavioral Corpus",
  "total_incidents": 220663,
  "raw_columns_count": 210,
  "cleaned_features_count": 196,
  "behavioral_dna_features_count": 70,
  "feature_taxonomy_counts": {
    "temporal_features": 7,
    "behavioral_offense_features": 15,
    "victimology_demographics": 11,
    "offender_demographics": 11,
    "weapon_violence_features": 3,
    "property_contraband_features": 13,
    "environmental_geographic_features": 128,
    "post_incident_outcomes": 6
  },
  "behavioral_groups_count": 7,
  "clusters_count": 8,
  "cross_crime_patterns_count": 8,
  "novelty_tier_counts": {
    "Standard Behavioral Pattern": 209629,
    "Moderate Behavioral Novelty": 8827,
    "High Behavioral Outlier": 2207
  }
}
```

---

### 3. Incident Lookup

#### `GET /api/incidents/{incident_id}`
Returns complete contextual attributes, cluster membership, and novelty assessment for an incident.

**Path Parameters:**
- `incident_id` (string, required): e.g. `INC_136975`

**Response `200 OK`:**
```json
{
  "incident_id": "INC_136975",
  "cluster": {
    "cluster_id": 1,
    "cluster_name": "Violent Armed Interpersonal & Domestic Assaults"
  },
  "novelty": {
    "novelty_score": 0.1784,
    "novelty_tier": "Standard Behavioral Pattern",
    "nearest_cluster_id": 1,
    "nearest_cluster_name": "Violent Armed Interpersonal & Domestic Assaults",
    "distance_to_nearest_cluster": 0.2814
  },
  "context": {
    "incident_hour": 22,
    "incident_month": 7,
    "incident_weekday": 5,
    "is_weekend": true,
    "is_night": true,
    "population": 125000.0,
    "offense_count": 1,
    "victim_count": 1,
    "offender_count": 1,
    "property_value": 0.0,
    "has_weapon": true,
    "has_injury": true,
    "has_property": false,
    "has_drug": false,
    "has_arrest": true,
    "has_relationship": true,
    "crime_against_person": true,
    "crime_against_property": false,
    "crime_against_society": false,
    "primary_crime_category": "Crimes Against Persons"
  }
}
```

---

### 4. Behavioral DNA Fingerprint

#### `GET /api/incidents/{incident_id}/dna`
Retrieves the 70-dimensional unit $L_2$-norm feature vector, subprofile group energies, and top active behavioral traits.

**Response `200 OK`:**
```json
{
  "incident_id": "INC_136975",
  "vector_dimension": 70,
  "feature_vector": {
    "time_hour_sin": 0.0415,
    "time_hour_cos": 0.2418,
    "time_month_sin": 0.2833,
    "time_month_cos": 0.1417,
    "time_is_weekend": 0.2833,
    "crime_against_person": 0.2833,
    "weapon_personal_weapons_flag": 0.2833,
    "has_relationship": 0.2833,
    "has_injury": 0.2833,
    "has_arrest": 0.2833
  },
  "group_energies": {
    "temporal_dynamics": 0.4998,
    "crime_characteristics": 0.2833,
    "location_and_environment": 0.2833,
    "method_and_activity": 0.4007,
    "people_and_demographics": 0.4007,
    "property_and_economics": 0.0,
    "context_and_harm": 0.4007
  },
  "top_active_traits": [
    {"feature": "time_month_sin", "value": 0.2833},
    {"feature": "time_is_weekend", "value": 0.2833},
    {"feature": "crime_against_person", "value": 0.2833},
    {"feature": "has_relationship", "value": 0.2833},
    {"feature": "has_injury", "value": 0.2833},
    {"feature": "has_arrest", "value": 0.2833}
  ]
}
```

---

### 5. Behavioral Similarity Search

#### `GET /api/similarity/similar/{incident_id}?top_k=5&include_breakdown=true`
Retrieves the top $K$ nearest neighbors in 70D space. Excludes the query incident from its own results.

**Query Parameters:**
- `top_k` (int, default=5, min=1, max=50): Number of matches to return.
- `include_breakdown` (bool, default=true): Includes independent cosine similarity scores across the 7 sub-profiles.

**Response `200 OK`:**
```json
{
  "query_incident_id": "INC_136975",
  "top_k_requested": 3,
  "total_matches_returned": 3,
  "matches": [
    {
      "rank": 1,
      "incident_id": "INC_135749",
      "similarity_score_pct": 99.86,
      "cosine_distance": 0.0014,
      "subprofile_similarity_pct": {
        "temporal_dynamics": 100.0,
        "crime_characteristics": 100.0,
        "location_and_environment": 100.0,
        "method_and_activity": 100.0,
        "people_and_demographics": 99.42,
        "property_and_economics": 100.0,
        "context_and_harm": 100.0
      },
      "primary_crime_category": "Crimes Against Persons",
      "cluster_name": "Violent Armed Interpersonal & Domestic Assaults"
    },
    {
      "rank": 2,
      "incident_id": "INC_168892",
      "similarity_score_pct": 98.71,
      "cosine_distance": 0.0129,
      "subprofile_similarity_pct": {
        "temporal_dynamics": 96.4,
        "crime_characteristics": 100.0,
        "location_and_environment": 100.0,
        "method_and_activity": 100.0,
        "people_and_demographics": 100.0,
        "property_and_economics": 100.0,
        "context_and_harm": 100.0
      },
      "primary_crime_category": "Crimes Against Persons",
      "cluster_name": "Violent Armed Interpersonal & Domestic Assaults"
    }
  ]
}
```

#### `POST /api/similarity/vector`
Enables custom vector search using an arbitrary 70-dimensional array.

**Request Body:**
```json
{
  "vector": [0.0415, 0.2418, 0.2833, ...],
  "top_k": 5
}
```

---

### 6. Behavioral Clustering

#### `GET /api/clusters`
Returns summaries of all 8 discovered clusters.

#### `GET /api/clusters/{cluster_id}`
Returns dominant behavioral profiles and distinctive features against global population means.

**Response `200 OK`:**
```json
{
  "cluster_id": 0,
  "name": "Small-City Property & Structure Theft",
  "macro_category": "Property",
  "summary": "Opportunistic property and structure offenses occurring predominantly in small municipal jurisdictions (10k-25k population). Characterized by daylight and afternoon occurrences, low violence rates, and moderate property values.",
  "incident_count": 17725,
  "percentage_of_total": 8.03,
  "dominant_patterns": {
    "temporal": "Daytime/afternoon peak (11:00-16:00), balanced weekday distribution",
    "location": "Small municipal jurisdictions (10k-25k population), residential structures",
    "crime": "Larceny-theft, burglary, property destruction",
    "weapon": "Unarmed / No weapons present (>96%)",
    "property": "Stolen property reported in 84.2% of incidents, median value $420",
    "harm": "Low physical injury rate (<2.1%), arrest at scene in 18.4%"
  },
  "top_distinctive_features": [
    {
      "feature": "population_group_desc_cities_from_10,000_thru_24,999",
      "cluster_mean": 1.0,
      "global_mean": 0.0803,
      "difference": 0.9197
    },
    {
      "feature": "crime_against_property",
      "cluster_mean": 0.992,
      "global_mean": 0.612,
      "difference": 0.380
    }
  ]
}
```

---

### 7. Cross-Crime Behavioral Patterns

#### `GET /api/cross-crime`
Returns all 8 cross-crime patterns showing shared behavior across different statutory categories.

#### `GET /api/cross-crime/{pattern_id}`
Retrieves complete cross-crime evidence, category breakdown, and exemplar incidents.

**Response `200 OK`:**
```json
{
  "pattern_id": "CCP_00",
  "cluster_id": 0,
  "pattern_name": "Cross-Crime: Small-City Property & Structure Theft",
  "total_incidents": 17725,
  "categories_represented": [
    {"category_name": "Property", "incident_count": 17583, "percentage": 99.2},
    {"category_name": "Society", "incident_count": 128, "percentage": 0.72},
    {"category_name": "Person", "incident_count": 14, "percentage": 0.08}
  ],
  "dominant_behavioral_characteristics": {
    "temporal_signature": "Daytime/afternoon concentration, weekday uniformity",
    "spatial_signature": "Small-city municipal environments (10,000-24,999 pop)",
    "method_signature": "Unarmed, low structural force, opportunistic access",
    "outcome_signature": "Stolen goods, property loss, low immediate arrest"
  },
  "inter_category_similarities": {
    "Property vs Society": 0.8124,
    "Property vs Person": 0.6941,
    "Society vs Person": 0.6812
  },
  "exemplar_incidents": [
    {
      "incident_id": "INC_171133",
      "crime_category": "Property",
      "category_description": "Property Offense",
      "behavioral_highlights": {
        "hour": 14,
        "is_night": false,
        "population_bracket": "10,000 to 24,999",
        "weapon": "Unarmed",
        "property_value": 350.0
      }
    }
  ],
  "exemplar_pairwise_similarities": {
    "INC_171133 (Property) <-> INC_042891 (Society)": 0.8214,
    "INC_171133 (Property) <-> INC_097111 (Person)": 0.6941
  },
  "cross_crime_evidence": {
    "finding": "Offenses classified under statutory Society or Person labels share the exact operational environment, temporal timing, and low-force methods of property crimes.",
    "investigative_utility": "Helps analysts connect incidents across department silos that would otherwise never be linked by offense type."
  }
}
```

---

### 8. Behavioral Evolution

#### `GET /api/evolution/timeline`
Returns chronological trajectories of cluster proportions and behavioral features across months and years.

#### `GET /api/evolution/shifts`
Returns statistically validated behavioral shifts across chronological epochs.

**Response `200 OK`:**
```json
{
  "total_shifts": 4,
  "shifts": [
    {
      "shift_id": "SHIFT_01",
      "domain": "Temporal Dynamics",
      "title": "Summer Nocturnal Behavioral Surge",
      "baseline_period": "February (24.24%)",
      "peak_period": "July (28.16%)",
      "delta_magnitude": "+3.92%",
      "statistical_test": "ANOVA F-Test across 12 months",
      "test_statistic": "F=12.64",
      "p_value": 2.54e-24,
      "statistical_significance": "Extremely Significant (p < 0.001)",
      "behavioral_explanation": "Nocturnal crime activity increases by nearly 4 percentage points during peak summer months (July/August), driven by elevated outdoor evening activity, longer daylight socializing, and nightlife concentration."
    }
  ]
}
```

---

### 9. Novel Behavioral Patterns (Anomaly Detection)

#### `GET /api/anomaly/summary`
Returns detector specifications and score thresholds.

#### `GET /api/anomaly/outliers?limit=50&offset=0`
Retrieves top behavioral outliers with unusual feature deviations.

**Response `200 OK`:**
```json
{
  "total_outliers_returned": 2,
  "total_extreme_outliers": 221,
  "outliers": [
    {
      "incident_id": "INC_082341",
      "novelty_score": 0.8912,
      "novelty_tier": "Extreme Outlier",
      "nearest_cluster": {
        "cluster_id": 1,
        "name": "Violent Armed Interpersonal & Domestic Assaults",
        "distance": 0.7412
      },
      "second_nearest_cluster": {
        "cluster_id": 4,
        "name": "Weekend Nightlife Vice & Public Order Enforcement",
        "distance": 0.8124
      },
      "unusual_features": [
        {
          "feature": "victim_count",
          "incident_value": 14.0,
          "population_mean": 1.08,
          "deviation_z_score": 12.4
        },
        {
          "feature": "weapon_firearm_flag",
          "incident_value": 1.0,
          "population_mean": 0.14
        }
      ],
      "behavioral_summary": "Extreme mass-casualty interpersonal incident involving 14 victims and multiple firearms, diverging severely from standard single-victim assault patterns."
    }
  ]
}
```

---

### 10. Similarity Explainability Engine

#### `GET /api/explain/{incident_id_1}/{incident_id_2}`
#### `POST /api/explain`
Calculates exact mathematical group contributions and contrastive differences for any pair of incidents.

**Request Body (POST):**
```json
{
  "incident_id_1": "INC_136975",
  "incident_id_2": "INC_145291"
}
```

**Response `200 OK`:**
```json
{
  "incident_pair": ["INC_136975", "INC_145291"],
  "similarity_score_pct": 85.7,
  "cosine_similarity_raw": 0.857,
  "main_contributing_similarities": [
    "Similar time pattern",
    "Similar people & demographic context",
    "Similar method & weapon context",
    "Similar location context",
    "Similar harm, injury & enforcement context"
  ],
  "differences": [
    "Different crime category (INC_136975: Person vs INC_145291: Society)",
    "Different property involvement (INC_136975: No Property vs INC_145291: Property Involved)",
    "Different crime against person"
  ],
  "group_contributions": [
    {
      "group_key": "temporal_dynamics",
      "display_name": "Time Pattern",
      "absolute_contribution": 0.2498,
      "percentage_of_similarity": 29.1
    },
    {
      "group_key": "people_and_demographics",
      "display_name": "People & Demographics",
      "absolute_contribution": 0.1876,
      "percentage_of_similarity": 21.9
    },
    {
      "group_key": "method_and_activity",
      "display_name": "Method & Weapon Context",
      "absolute_contribution": 0.1859,
      "percentage_of_similarity": 21.7
    },
    {
      "group_key": "location_and_environment",
      "display_name": "Location Context",
      "absolute_contribution": 0.1501,
      "percentage_of_similarity": 17.5
    },
    {
      "group_key": "context_and_harm",
      "display_name": "Harm & Injury Context",
      "absolute_contribution": 0.0840,
      "percentage_of_similarity": 9.8
    }
  ],
  "top_contributing_features": [
    {
      "feature_name": "has_relationship",
      "contribution": 0.0753,
      "incident_1_value": 0.283,
      "incident_2_value": 0.266,
      "description": "Offender had an established prior relationship with the victim."
    },
    {
      "feature_name": "time_is_weekend",
      "contribution": 0.0753,
      "incident_1_value": 0.283,
      "incident_2_value": 0.266,
      "description": "Occurred during weekend hours."
    }
  ],
  "formatted_text_summary": "Similarity Score: 85.7%\n\nMain contributing similarities:\n- Similar time pattern\n- Similar people & demographic context\n- Similar method & weapon context\n- Similar location context\n- Similar harm, injury & enforcement context\n\nDifferences:\n- Different crime category (INC_136975: Person vs INC_145291: Society)\n- Different property involvement (INC_136975: No Property vs INC_145291: Property Involved)\n- Different crime against person",
  "disclaimer": "Explanations represent mathematical feature-space attribution. They do NOT imply causal relationships or common offender identity."
}
```

---

## 5. Error Handling & Status Codes

All errors return a consistent structured JSON payload:

```json
{
  "error": "IncidentNotFoundError",
  "detail": "Incident 'INC_999999' not found in the CRIME DNA database.",
  "status_code": 404
}
```

| Status Code | Exception Class | Scenario |
| :---: | :--- | :--- |
| `404 Not Found` | `IncidentNotFoundError` | Querying an incident ID that does not exist |
| `404 Not Found` | `ClusterNotFoundError` | Requesting a cluster outside range `0..7` |
| `404 Not Found` | `PatternNotFoundError` | Requesting a cross-crime pattern ID not in `CCP_00..CCP_07` |
| `422 Unprocessable Content` | `InvalidVectorError` | Vector has wrong length ($\ne 70$) or has zero norm |
| `422 Unprocessable Content` | `RequestValidationError` | Pydantic validation failure on parameters or body |
| `503 Service Unavailable` | `ModelNotLoadedError` | Required ML model failed to load during startup |
| `500 Internal Server Error`| `InternalServerError` | Uncaught server exception |

---

## 6. Interactive Documentation & How to Run

### Interactive UI Docs
When the server is running, interactive API documentation is automatically accessible at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

### Running the API Locally

```bash
# Start development server with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or run in production mode with multiple Uvicorn workers
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Running Automated Test Suite

```bash
# Run API test suite
pytest tests/api/ -v

# Run full project test suite (69 tests)
pytest tests/ -v
```

All 69 unit and integration tests execute and pass in under 4 seconds.
