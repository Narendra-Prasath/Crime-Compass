# Crime Compass 🧭 — User Dataset Upload & Behavioral Analysis Specification

**Document:** `docs/CRIME_COMPASS_DATASET_ANALYSIS.md`  
**Classification:** System Architecture, Mathematical Methodology & Operational Guide  
**Status:** Implemented & Verified  

---

## 1. Architectural Overview

Crime Compass 🧭 provides an additive, user-driven dataset upload and behavioral intelligence experience within **Analyze Incident**. Users can upload CSV incident records from any city, district, state, locality, police jurisdiction, or custom time period and discover patterns, connections, similarities, and shifts within that dataset.

```
User Upload (CSV)
      │
      ▼
Step 1: File Validation (Size ≤ 15MB, non-binary, syntax parsing, duplicates, missingness)
      │
      ▼
Step 2: Interactive Preview (First 5 rows table, column stats, sample values)
      │
      ▼
Step 3: Dynamic Column Mapping (Intelligent auto-suggestions, required vs optional indicators)
      │
      ▼
Step 4: Quality & Integrity Verification (Missing data policy: no artificial zeros imputed)
      │
      ▼
Step 5: Scope & Filter Configuration (Independent analysis vs reference comparison, area & time filters)
      │
      ▼
Step 6: Real Behavioral ML Pipeline (70D unit vectors on S^69, Adaptive Spherical K-Means, cosine matrix)
      │
      ▼
Step 7: Comprehensive Results View (10 analytical sections, export to JSON/CSV, secure deletion)
```

---

## 2. Seven-Step Analysis Workflow

### Step 1 — Select File
- **Accepted Format:** CSV (Comma-Separated Values) with support for UTF-8, UTF-8-BOM, and Latin-1 encodings.
- **Enforced Safety Bounds:**
  - Maximum upload size: 15 MB.
  - Maximum row limit: 50,000 incident rows (for real-time in-memory responsiveness).
  - Malicious / executable content guard: Null-byte and binary header detection rejects `.exe`, `.bin`, `.py`, and non-text files gracefully.
- **Feedback Displayed:** Filename, size in KB/MB, total parsed records, total columns, duplicate rows count, missing data percentage, initial validity status.

### Step 2 — Preview
- Displays the first 5 records in an interactive table with explicit representation of `null` / unrecorded fields.
- Provides per-column summary metrics: inferred data type, non-null counts, null counts, and 3 distinct sample values.
- Flags validation observations: duplicate column headers, blank column names, high missing cell ratios (>40%), and duplicate incident rows.

### Step 3 — Map Columns
Crime Compass automatically suggests column mappings using an alias dictionary matching standard Behavioral DNA dimensions:
- **Core / Identifier:** `incident_id` (e.g. `fir_no`, `case_id`, `record_id`).
- **Temporal:** `incident_date` (e.g. `event_date`, `occ_date`), `incident_time` (e.g. `occ_time`, `crime_time`).
- **Location:** `country`, `state_ut`, `district`, `city_town`, `locality`, `pin_code`.
- **Behavioral & Modus Operandi:** `crime_category` (required), `is_attempted`, `population_setting`, `has_weapon`, `weapon_count`, `has_criminal_activity`, `has_relationship`.
- **People & Demographics:** `victim_count`, `victim_avg_age`, `offender_count`, `offender_avg_age`.
- **Economic & Outcomes:** `has_property`, `has_stolen_property`, `property_value`, `has_injury`, `has_drug`, `has_arrest`, `currency`.

**Dynamic Mapping Rules:**
- Unmapped optional columns are allowed and preserved as unobserved traits.
- The user is never forced to map irrelevant columns.
- Required fields (`crime_category`) are prominently tagged with status badges.
- Ambiguous mappings prompt user confirmation.

### Step 4 — Data Validation
- Enforces strict missing value semantics:
  - Missing weapon cells do **not** mean unarmed; they are treated as unobserved.
  - Missing injury cells do **not** mean uninjured; they are treated as unobserved.
  - Missing numeric values are **never** replaced with artificial zeros unless zero is genuinely meaningful.
- Verifies behavioral sufficiency: At least 1 category/description field and behavioral or temporal characteristics must exist.

### Step 5 — Choose Analysis Scope
- **Independent Analysis:** Analyzes the uploaded dataset strictly using its own empirical internal distributions.
- **Comparison with Historical Reference Baseline (Optional):** Evaluates discovered dataset clusters against the 8 pre-trained empirical cluster centroids from the 220,663 incident Alabama 2024 NIBRS reference model.
- **Geographic Filtering:** Allows filtering by specific City, District, State, or Locality dynamically discovered from the uploaded CSV.
- **Time Range Filtering:** Allows narrowing analysis to specific start and end dates.

### Step 6 — Machine Learning Pipeline Execution
1. **Behavioral DNA Encoding:** Every mapped row is transformed into a 70-dimensional normalized unit vector on the hypersphere $\mathbb{S}^{69}$ using `src/features/input_bridge.py`.
2. **Adaptive Spherical K-Means Clustering:**
   - Real clustering executed directly on uploaded incident vectors.
   - Adaptive cluster count $k \in [2, 6]$ based on dataset volume $N$ and unique category diversity:
     $$k = \begin{cases} 1 & N < 4 \\ \min(3, \max(2, |\text{categories}|)) & 4 \le N < 20 \\ \min(5, \max(2, \lfloor N / 15 \rfloor)) & 20 \le N < 100 \\ \min(6, \max(3, |\text{categories}|)) & N \ge 100 \end{cases}$$
   - Centroids normalized to unit norm $\|\mathbf{c}_k\|_2 = 1.0$ on $\mathbb{S}^{69}$.
   - Pattern titles and descriptions derived dynamically from top positive feature dimensions and category concentrations.
3. **Pairwise Similarity Search (with Query Self-Exclusion):**
   - Pairwise cosine similarity matrix $\mathbf{S} = \mathbf{V} \mathbf{V}^T \in [-1, 1]^{N \times N}$.
   - Nearest neighbors retrieved with strict query self-exclusion: $i \neq j$.
   - Matching and differing observed characteristics extracted.
4. **Cross-Crime Modus Operandi Discovery:**
   - Computes category centroids and cross-category cosine alignment.
   - Non-offender disclaimer enforced: *"Shared behavioral characteristics reflect common situational patterns or modus operandi traits and DO NOT imply incidents were committed by the same individual."*
5. **Location-Specific Distribution:**
   - Incident counts and category proportions by jurisdiction.
   - Neutral disclaimer: *"Incident counts reflect raw reporting numbers in the uploaded dataset. They must not be interpreted as crime rates without appropriate population denominators."*
6. **Temporal Evolution:**
   - Monthly and hourly frequency breakdowns with reporting disclaimers.
7. **Unusual Behavioral Combinations:**
   - Distance to cluster centroid: $d_i = 1.0 - (\mathbf{v}_i \cdot \mathbf{c}_{k})$.
   - Top atypical records classified neutrally as "Unusual Combination" or "Less Common Combination" (no risk forecasting).

### Step 7 — Results Presentation & Export
Presents 10 distinct analytical sections:
1. Dataset Summary
2. Discovered Behavioral Patterns
3. Pairwise Similar Incidents
4. Cross-Crime Patterns
5. Location-Specific Distribution
6. Temporal Timeline Distribution
7. Unusual Behavioral Configurations
8. Historical Reference Comparison
9. Analytical Transparency ("Why These Results?")
10. Technical Specifications (Expandable)

**Export & Deletion:**
- 1-Click JSON export (`GET /api/datasets/analyses/{id}/export?format=json`).
- 1-Click CSV pattern export (`GET /api/datasets/analyses/{id}/export?format=csv`).
- 1-Click permanent deletion (`DELETE /api/datasets/analyses/{id}`).

---

## 3. Multi-User Safety & Data Isolation (Part C & D)

1. **Unique Analysis Isolation:** Every analysis receives a unique identifier `DATASET_ANALYSIS_{UUID12}`.
2. **Zero Model Pollution:** Uploaded records are strictly isolated; they are never injected into the historical reference training dataset or used to retrain historical models.
3. **Data Minimization & Privacy:** No personal identifiable information (PII) such as victim names, addresses, or phone numbers is accepted or recorded.
4. **Storage Cleanup:** Completed analyses are saved in `data/dataset_analyses/{analysis_id}.json` and can be purged immediately by the investigator. Temporary file caches are evicted automatically.

---

## 4. API Reference

| Endpoint | Method | Request Payload | Description |
| :--- | :--- | :--- | :--- |
| `/api/datasets/validate` | `POST` | Multipart `file` or Form `csv_text` | Validates CSV, checks data quality, returns preview and auto-mapping suggestions. |
| `/api/datasets/analyze` | `POST` | JSON `DatasetAnalyzeRequest` or Multipart Form | Executes full behavioral machine learning analysis on mapped data. |
| `/api/datasets/analyses/{id}` | `GET` | — | Retrieves a previously computed dataset analysis by its unique ID. |
| `/api/datasets/analyses/{id}` | `DELETE` | — | Permanently deletes an analysis and cleans up disk cache. |
| `/api/datasets/analyses/{id}/export` | `GET` | Query param `format=json\|csv` | Downloads analysis report or pattern summary file. |
