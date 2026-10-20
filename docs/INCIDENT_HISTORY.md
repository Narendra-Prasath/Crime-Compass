# Crime Compass 🧭 — Incident History Architecture & Specification

## 1. Executive Summary & Overview

The **Incident History** section provides investigative analysts and system auditors with an immutable, privacy-preserving audit trail of all incident simulations evaluated through the **Crime Compass 🧭 Behavioral Analysis Engine**.

Each analyzed incident is fingerprinted into a **70-Dimensional Behavioral Fingerprint vector** ($\|\mathbf{x}\|_2 = 1.0$) and archived with structured analytical summaries covering Modus Operandi (MO), historical similarity, cluster archetype assignment, cross-crime behavioral links, and behavioral novelty.

---

## 2. Strict Architectural Separation

A core design requirement of Crime Compass 🧭 is maintaining an unambiguous, tamper-proof architectural boundary between the **Historical Reference Knowledge Base** and **User Analysis History**.

```
┌────────────────────────────────────────────────────────────────────────┐
│               CRIME COMPASS 🧭 ARCHITECTURAL BOUNDARY                  │
├──────────────────────────────────┬─────────────────────────────────────┤
│      HISTORICAL ML DATASET       │        USER ANALYSIS HISTORY        │
│    (Reference Knowledge Base)    │         (Audit Trail Store)         │
├──────────────────────────────────┼─────────────────────────────────────┤
│ • 220,663 Incident NIBRS Corpus  │ • Local User Session Records        │
│ • Namespace: INC_xxxxxx          │ • Namespace: ANALYSIS_xxxxxxxxxxxx  │
│ • Offline-Trained ML Embeddings  │ • Transient / Audit Records         │
│ • 8 K-Means Cluster Centroids    │ • Zero Model Retraining             │
│ • FAISS / Cosine KNN Indices     │ • Isolated SQLite Repository        │
│ • Read-Only Baseline Matrix      │ • Zero Contamination into ML Corpus │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### Key Separation Invariants:
1. **Zero Data Contamination:** User-submitted incident inputs are **never written** to `crime_dna_ml.csv`, **never merged** into the normalized feature matrix, and **never added** to nearest-neighbor index files.
2. **Zero Online Model Retraining:** Stored analyses never update K-Means centroids, Isolation Forest decision thresholds, or MO cross-crime definitions.
3. **Distinct Entity Namespaces:**
   - Historical Baseline Incidents: `INC_...` (e.g., `INC_136975`, `INC_145291`)
   - User Incident Analyses: `ANALYSIS_...` (e.g., `ANALYSIS_9F2A1E8C1234`)
4. **Reference Integrity:** In queries, user records are compared *against* the historical baseline; historical baseline records are never altered by user queries.

---

## 3. Privacy Protection & Zero PII Policy

The Incident History system strictly adheres to **Data Minimization** and **Zero Personally Identifiable Information (Zero PII)** standards:

- **Strictly Excluded Attributes:**
  - No names (neither victim, suspect, witness, nor reporting officer).
  - No contact details (no phone numbers, email addresses, or social identifiers).
  - No residential street addresses, postal street numbers, or exact geo-coordinates.
  - No government identifiers (no SSN, national ID, or driver's license numbers).
- **Stored Behavioral Attributes Only:**
  - Macro population setting (`metropolitan_core`, `large_city`, `mid_sized_city`, etc.).
  - Offense statutory category (`property`, `person`, `society`, `person_property`).
  - Quantitative behavioral counts (offenses, weapons, victims, suspects).
  - Binary modus operandi flags (`has_weapon`, `has_injury`, `has_property`, `has_relationship`).
  - Temporal dynamics (hour of day, day of week / weekend, month).
  - 70D Behavioral DNA vector and sub-profile energy distributions.

---

## 4. Persistent Storage & Schema

Incident history records are maintained in an isolated SQLite database at `data/analysis_records/analysis_records.db`.

### Table Schema: `analysis_records`

```sql
CREATE TABLE IF NOT EXISTS analysis_records (
    analysis_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    scenario_title TEXT,
    input_summary TEXT NOT NULL,
    behavioral_dna TEXT NOT NULL,
    similarity_summary TEXT NOT NULL,
    pattern_summary TEXT NOT NULL,
    novelty_summary TEXT NOT NULL,
    record_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rec_user ON analysis_records(user_id);
CREATE INDEX IF NOT EXISTS idx_rec_created ON analysis_records(created_at);
```

### JSON Schema: `AnalysisRecord`

```json
{
  "analysis_id": "ANALYSIS_7E81A02C3F1B",
  "user_id": "investigator_01",
  "timestamp": "2026-10-11T16:25:00Z",
  "input_summary": {
    "scenario_title": "Armed Convenience Store Robbery",
    "crime_category": "person_property",
    "population_setting": "mid_sized_city",
    "temporal_profile": { "hour": 21, "month": 11, "is_weekend": false, "is_night": true },
    "behavioral_flags": { "has_weapon": true, "has_injury": true, "has_property": true, "has_relationship": false },
    "incident_counts": { "offense_count": 2, "victim_count": 2, "offender_count": 2 }
  },
  "behavioral_dna": {
    "vector_dimension": 70,
    "subprofile_energies": {
      "temporal_dynamics": 0.21,
      "crime_characteristics": 0.35,
      "location_and_environment": 0.12,
      "method_and_activity": 0.42,
      "victim_and_offender": 0.28,
      "property_and_economics": 0.30,
      "harm_and_severity": 0.45
    },
    "top_active_traits": [
      { "feature": "weapon_firearm_flag", "value": 1.0 },
      { "feature": "property_stolen_flag", "value": 1.0 }
    ]
  },
  "similarity_summary": {
    "top_matched_incident_id": "INC_136975",
    "similarity_percentage": 89.4,
    "distance_metric": "Cosine Similarity on Unit L2 Hyper-Sphere",
    "category_relationship": "Cross-Category Link",
    "has_cross_crime_match": true,
    "k_neighbors_searched": 50
  },
  "pattern_summary": {
    "pattern_id": "PATTERN_00",
    "cluster_id": 0,
    "pattern_name": "Commercial Robbery Syndicate Archetype",
    "behavioral_formula": "High MO Energy + Night Commercial Target + Multi-Offender",
    "supporting_incident_count": 24890,
    "crime_categories_represented_count": 3,
    "association_strength_score": 92.4,
    "association_tier": "High Confidence"
  },
  "novelty_summary": {
    "novelty_score": 0.124,
    "novelty_tier": "Standard Behavioral Pattern",
    "is_novel": false,
    "pattern_fit_score": 93.8,
    "fit_description": "Strong alignment with known Commercial Robbery Cluster",
    "unusual_factors": []
  },
  "ethical_advisory": "CRIME DNA identifies behavioral similarity between crime incidents. It does not identify offenders or determine legal guilt."
}
```

---

## 5. API Endpoints Reference

### 1. List Clean Analysis Records
- **Endpoint:** `GET /api/analyze/records`
- **Query Parameters:**
  - `user_id` (optional, string): Scope query to a specific user or session identifier.
  - `search` (optional, string): Case-insensitive keyword filter across `analysis_id`, `scenario_title`, `crime_category`, or `pattern_name`.
  - `category` (optional, string): Filter by crime statutory category (e.g., `property`, `person`, `society`, `person_property`).
  - `limit` (optional, int, default: 50, max: 200): Maximum records per page.
  - `offset` (optional, int, default: 0): Record offset for pagination.
- **Headers:** `X-User-ID` (optional fallback for `user_id`).
- **Response Model:** `AnalysisRecordListResponse`
  ```json
  {
    "total_count": 42,
    "user_id": "investigator_01",
    "limit": 10,
    "offset": 0,
    "records": [ ... ]
  }
  ```

### 2. Get Stored Analysis Result by ID
- **Endpoint:** `GET /api/analyze/records/{analysis_id}`
- **Path Parameters:**
  - `analysis_id` (string): Unique identifier (e.g. `ANALYSIS_7E81A02C3F1B`).
- **Response Model:** `AnalysisRecord`
- **Error Codes:** `404 Not Found` if the analysis record does not exist.

### 3. Delete Analysis Record
- **Endpoint:** `DELETE /api/analyze/records/{analysis_id}`
- **Path Parameters:**
  - `analysis_id` (string): Unique identifier.
- **Query / Header:** `user_id` or `X-User-ID` (optional scoping).
- **Response:**
  ```json
  {
    "status": "success",
    "analysis_id": "ANALYSIS_7E81A02C3F1B",
    "message": "Analysis record successfully removed from user history."
  }
  ```

---

## 6. Frontend User Interface Specifications

The frontend implements the Incident History section in [`frontend/src/pages/IncidentHistoryPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/IncidentHistoryPage.tsx):

### Display Layouts:
1. **Clean Table View:**
   - **Analysis ID:** Monospace badge with one-click copy button.
   - **Date / Time:** Formatted timestamp with humanized relative time ("2 hours ago", "Yesterday").
   - **Crime Category:** Color-coded statutory badge (Property: blue, Violent: rose, Society: purple, Robbery: amber).
   - **Behavioral Pattern:** Archetype name, cluster ID badge, and association confidence tier.
   - **Similarity Summary:** Top matched historical incident ID (`INC_...`), percentage match score, and cross-crime badge.
   - **Novelty Summary:** Novelty status badge (`Standard Pattern` vs `Novel Outlier`), novelty score, and pattern fit percentage.
   - **Actions:** Quick "Open" button and delete button.
2. **Card Grid View:**
   - Responsive multi-column grid layout for visual inspection with hover elevation and highlights.
3. **Stored Analysis Result Inspector Modal:**
   - Clicking any analysis row or card opens a full modal view displaying:
     - Architectural disclaimer confirming zero model contamination.
     - 4-card quick metrics bar (Match %, Cluster Archetype, Novelty Tier, 70D Vector Dimension).
     - Behavioral Pattern Formula breakdown.
     - 5 Sub-profile DNA energy distribution gauges and active trait chips.
     - Zero PII simulated parameters overview.
     - Direct button to **"Open in Simulator"** to load the scenario into the interactive Simulator.
     - Direct link to **"View Matched Incident"** (`INC_...`) opening the Incident Analyzer.
4. **State Handling:**
   - **Loading State:** Shimmering skeleton rows with loading indicator.
   - **Empty State:** Friendly empty state with one-click CTA to launch the Incident Simulator.
   - **Filtered Empty State:** Prompt with one-click "Clear Filters" button when search finds no results.
   - **Error State:** Alert notification with a "Try Again" retry action.
   - **Pagination:** Compact footer showing range, page numbers, and page size selector (10, 25, 50).

---

## 7. Verification & Automated Testing

Automated test coverage is provided in [`tests/test_incident_history.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_incident_history.py):

| Test Case | Description | Verification Target |
|---|---|---|
| `test_incident_history_record_structure_and_layout` | Validates layout fields in history | Analysis ID, Date/Time, Category, Pattern, Similarity, Novelty |
| `test_clicking_analysis_opens_stored_analysis_result` | Opens stored record by Analysis ID | Complete analysis details, 70D DNA, and analytical context |
| `test_zero_pii_and_data_minimization` | Verifies zero PII in database | Prohibits names, phones, emails, SSNs, personal addresses |
| `test_strict_dataset_separation_historical_vs_user_history` | Verifies reference dataset immutability | Historical incident count (220,663) and feature matrix are unchanged |
| `test_pagination` | Verifies pagination functionality | Limit, offset, and total_count verification |
| `test_search_and_filter` | Verifies search keywords and category filters | Keyword matching, category filtering, empty query handling |
| `test_record_deletion_and_error_handling` | Tests deletion and 404 handling | DELETE endpoint, nonexistent ID handling (404) |
