# Behavioral Domain Energies & Data Coverage Technical Specification

**Project:** Crime Compass 🧭  
**Document:** `docs/BEHAVIORAL_DOMAIN_ENERGIES.md`  
**Classification:** Scientific Methodology & Architectural Audit  
**Date:** October 2024 (Baseline: 2024 FBI NIBRS Incident Corpus, Alabama State Benchmark, $N = 220,663$)

---

## Executive Summary & Audit Findings (Part A)

### 1. Investigation of the Prior "100%" Artifact
In previous user interface builds of Crime Compass, the overview card displayed:
- Temporal Dynamics: `100%`
- Crime Characteristics: `100%`
- Location and Environment: `100%`
- Method and Activity: `100%`

A rigorous source-code audit determined the root causes of this phenomenon:
1. **Frontend Clamping Bug (`CrimeDnaResultExperience.tsx` Line 363):**  
   The backend's `src/features/input_bridge.py` originally emitted subprofile energies computed as mean percentages (e.g., `10.3` for 10.3%). The frontend component executed:
   $$\text{pct} = \min(100, \max(0, \text{score} \times 100))$$
   Multiplying an already-percentage value by 100 yielded values $\ge 1000\%$ (e.g., $10.3 \times 100 = 1030\%$), which immediately clamped to `100%`.
2. **Empty Subprofile Defaulting (`src/similarity/engine.py` Line 277 & `src/services/analysis_engine.py` Line 190):**  
   When both query and historical incidents lacked specific activity (e.g., unarmed incidents having zero-norm subvectors for weapon types), the engine executed:
   ```python
   if nu == 0 and nv == 0:
       sub_sims[grp_key] = 100.0
   ```
   This assigned 100% similarity to unarmed crimes for the Method domain, conflating "absence of weapon" with 100% domain activity.
3. **Domain Truncation:**  
   The frontend UI previously executed `.slice(0, 4)` on the domain energy map, truncating the remaining domains and presenting an incomplete view of the schema.

### 2. Conceptual Disambiguation
Under Crime Compass 🧭, three mathematically distinct metrics are separated and never conflated:
1. **Behavioral Data Coverage (Completeness):** The percentage of schema-supported fields that contain valid, recorded observations.
2. **Subprofile Coordinate Magnitude (Vector Geometry):** The Euclidean norm $\|\mathbf{v}_g\|_2$ of a subprofile slice on the unit hypersphere $\mathbb{S}^{69}$, whose squared norms sum to $1.0$.
3. **Similarity Attribution (Decomposition):** The exact additive contribution $C_g = \mathbf{u}_g \cdot \mathbf{v}_g$ of a feature group to the overall cosine similarity score.

---

## Part B: Behavioral Data Coverage Specification

### 1. Schema Domain Organization
Behavioral characteristics are organized into six schema-supported domains matching the actual input schema (`src/api/schemas.py` & `src/features/input_bridge.py`):

| Domain Name | Domain Key | Supported Schema Fields | Prerequisite Rule / Applicability | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Temporal Dynamics** | `temporal_dynamics` | `incident_hour`, `incident_month`, `incident_weekday`, `is_weekend`, `is_night` (5 fields) | Always applicable | Incident timing, diurnal rhythms, and day-of-week patterns. |
| **Crime Characteristics** | `crime_characteristics` | `crime_category`, `is_attempted`, `offense_count` (3 fields) | Always applicable | Statutory category, attempt status, and offense count structure. |
| **Location and Environment** | `location_and_environment` | `population_setting`, `location_count`, `population` (3 fields) | Always applicable | Spatial density setting, location counts, and geographic operational context. |
| **Method and Activity** | `method_and_activity` | `has_weapon`, `weapon_count`, `has_criminal_activity` (2-3 fields) | `weapon_count` is applicable only if `has_weapon = True`. Unarmed incidents are not penalized for missing weapon counts. | Weapon deployment, weapon count, and criminal activity associations. |
| **People and Incident Context** | `people_and_context` | `victim_count`, `offender_count`, `has_injury`, `injury_record_count`, `has_relationship`, `has_arrest` (5-6 fields) | `injury_record_count` is applicable only if `has_injury = True`. | Victim/offender demographics, relationships, physical injury, and arrest context. |
| **Property and Impact** | `property_and_impact` | `has_property`, `property_record_count`, `property_value`, `is_cargo_theft` (2-4 fields) | `property_record_count` and `property_value` are applicable only if `has_property = True`. | Property loss status, stolen item counts, valuation, and cargo indicators. |

### 2. Documented Coverage Formula
For each domain $d$, the Behavioral Data Coverage $\text{Coverage}_d$ is defined as:
$$\text{Coverage}_d = \frac{N_{\text{valid, applicable}}(d)}{N_{\text{applicable}}(d)} \times 100\%$$

Where:
- $N_{\text{valid, applicable}}(d)$ is the count of fields within domain $d$ that have non-null, validly specified values and whose prerequisite condition is met.
- $N_{\text{applicable}}(d)$ is the total number of fields in domain $d$ whose prerequisite conditions are satisfied.
- Fields whose prerequisite condition is not satisfied (e.g., `weapon_count` when `has_weapon = False`) are designated as **Not Applicable** (`not_applicable`) and do not reduce domain coverage.

**Overall Data Coverage:**
$$\text{Coverage}_{\text{overall}} = \frac{\sum_d N_{\text{valid, applicable}}(d)}{\sum_d N_{\text{applicable}}(d)} \times 100\%$$

### 3. Ethical and Interpretive Boundary
- **Data Completeness, Not Risk:** Coverage reflects how thoroughly an incident was documented in the police report or intake form.
- **Missing Data Is Not Negative Evidence:** An unspecified field indicates lack of observation, not evidence that the behavior was absent.
- **No Probability Inference:** Coverage cannot be interpreted as crime risk, behavioral intensity, model confidence, or recidivism probability.

---

## Part C: Compact Behavioral Fingerprint

The Compact Behavioral Fingerprint provides an immediate operational summary using only observed, verified incident traits.

### 1. Discrete Status Categories
Every trait must be assigned one of four mutually exclusive statuses:
- **`Yes`**: Confirmed positive finding in the incident record.
- **`No`**: Confirmed negative finding (e.g., `has_weapon = False`, `has_injury = False`).
- **`Unknown`**: Field was omitted, null, or left unspecified in the report.
- **`Not applicable`**: Prerequisite condition was not met (e.g., weapon type for an unarmed crime).

### 2. Standardized Fingerprint Traits
1. **Diurnal Timing:** `Nighttime` (20:00–05:59) vs `Daytime` (06:00–19:59).
2. **Weekend Occurrence:** `Weekend` (Saturday/Sunday) vs `Weekday` (Monday–Friday).
3. **Setting / Environment:** Urban, Suburban, or Rural population tier.
4. **Property Focus:** Property loss or stolen assets involved (`Yes` / `No`).
5. **Person Focus:** Direct human victim or interpersonal crime category (`Yes` / `No`).
6. **Weapon Deployment:** Weapon reported (`Yes`), unarmed approach (`No`), or unspecified (`Unknown`).
7. **Physical Injury:** Injury documented (`Yes`), no injury (`No`), or unspecified (`Unknown`).
8. **Arrest Effectuated:** Arrest made at scene (`Yes`), no arrest (`No`), or unspecified (`Unknown`).

---

## Part D: Similarity Engine Architecture & Geometry

### 1. Hyperspherical Normalization
Every incident is transformed into a 70-dimensional feature vector $\mathbf{x} \in \mathbb{R}^{70}$ using identical preprocessing pipelines across historical reference data and incoming queries.
To eliminate bias from variable count scales and disparate dimensional ranges, each vector is projected onto the unit hypersphere $\mathbb{S}^{69}$:
$$\mathbf{v} = \frac{\mathbf{x}}{\|\mathbf{x}\|_2}, \quad \|\mathbf{v}\|_2 = 1.000$$

### 2. Subprofile Coordinate Magnitudes (Subprofile Energies)
For each behavioral group $g \subseteq \{1, \dots, 70\}$, the subprofile energy $E_g$ is defined as the Euclidean L2 norm of the subvector slice:
$$E_g = \|\mathbf{v}_g\|_2 = \sqrt{\sum_{i \in g} v_i^2}$$

Because $\mathbf{v}$ is normalized to unit length, the sum of squared subprofile energies equals unity:
$$\sum_{g=1}^G E_g^2 = \sum_{g=1}^G \sum_{i \in g} v_i^2 = \|\mathbf{v}\|_2^2 = 1.000$$
These values represent the geometric distribution of coordinate mass across behavioral domains. They do not represent feature importance, model confidence, or investigative certainty.

### 3. Metric & Score Transformation
The similarity between query incident $\mathbf{u} \in \mathbb{S}^{69}$ and historical incident $\mathbf{v} \in \mathbb{S}^{69}$ is computed via the cosine dot product:
$$S(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^{70} u_i v_i$$
Cosine distance is defined as:
$$D_{\text{cos}}(\mathbf{u}, \mathbf{v}) = 1 - S(\mathbf{u}, \mathbf{v})$$
The display similarity percentage is transformed linearly:
$$\text{Similarity Score (\%)} = \frac{1 + S(\mathbf{u}, \mathbf{v})}{2} \times 100\%$$

### 4. Query Self-Exclusion Guarantee
To prevent trivial circular matches when a query incident matches a historical ID, the similarity search executes:
```python
search_k = min(len(state.incident_ids), top_k + 5)
distances, indices = state.knn_index.kneighbors([query_vec], n_neighbors=search_k)
for dist, idx in zip(distances[0], indices[0]):
    matched_id = state.incident_ids[idx]
    if matched_id == query_inc_id:
        continue  # Strict self-exclusion
    # Append valid match
```

### 5. Ethical Non-Offender Attribution Rule
**Mandatory Rule:** A similarity score measures abstract modus operandi alignment. It must **NEVER** be described as the probability that two incidents were committed by the same individual or crime syndicate.

---

## Part E: "Why Are These Incidents Similar?" Explanation Architecture

### 1. Transparent Observed Feature Comparison
Rather than manufacturing pseudo-SHAP values for nearest-neighbor lookups, Crime Compass provides a rule-based comparison across the five core operational domains:
- **Time Dynamics:** Similar if both occurred during the same diurnal window (e.g., both night) and weekend alignment matches.
- **Location Setting:** Similar if population density tier and premise count align.
- **Crime Characteristics:** Similar if statutory crime categories match; Different if cross-crime match.
- **Method & Activity:** Similar if weapon presence, weapon counts, and criminal activity flags match.
- **Property & Context:** Similar if property involvement and injury flags match.

### 2. Exact Dot-Product Decomposition
Because cosine similarity is an inner product over unit vectors, the overall similarity decomposes additively across behavioral feature groups:
$$S(\mathbf{u}, \mathbf{v}) = \sum_{g=1}^G C_g, \quad C_g = \mathbf{u}_g \cdot \mathbf{v}_g = \sum_{i \in g} u_i v_i$$
The percentage contribution (share) of group $g$ is:
$$\text{Share}_g = \frac{C_g}{\sum_{j=1}^G C_j} \times 100\%$$

### 3. Cross-Crime Match Rationale
When $\text{Category}(\mathbf{u}) \neq \text{Category}(\mathbf{v})$, the engine produces an explicit operational rationale explaining why the cross-crime match occurred (e.g., nocturnal commercial entry with weapon intimidation matches between Robbery and Burglary despite statutory classification differences).

---

## Part F: Cross-Crime Pattern Discovery (8 Archetypes)

The eight cross-crime behavioral archetypes are preserved as discovered via spherical $k$-means ($k=8$) on the 220,663 baseline corpus:
1. **Commercial Robbery Syndicate Archetype:** High MO energy, night commercial premises, coordinated multi-actor dynamics.
2. **Opportunistic Residential Acquisitive Archetype:** Daytime residential entry, unarmed approach, singular actor dynamics.
3. **Interpersonal Dispute / Domestic Harm Archetype:** Strong relationship indicators, residential setting, physical injury documented.
4. **Vehicular & Transit Theft Archetype:** Public parking / roadway spatial setting, property loss, rapid transit execution.
5. **Substance-Involved Street Activity Archetype:** Suspected drug indicators, high population urban density, weapon presence.
6. **Commercial Shoplifting & Organized Retail Theft:** Daytime retail premises, zero injury, high stolen count volume.
7. **Nocturnal Structure Burglary Archetype:** Deep nocturnal timing, commercial/unoccupied structure entry, property valuation focus.
8. **Public Order & Societal Disturbance Archetype:** Non-property focus, public thoroughfare setting, arrest effectuated at scene.

**Constraint:** Clusters represent recurring operational methods observed across populations. They do NOT represent crime rings, serial offenders, or linked perpetrators.

---

## Part G: Behavioral Evolution & Longitudinal Baseline

1. **Time Period Analyzed:** Calendar Year 2024 (January 1 – December 31, 2024).
2. **Corpus Volume:** 220,663 validated historical events.
3. **Metric Nature:** Hourly distribution proportions ($p(h) = \frac{N(h)}{N_{\text{total}}}$) and normalized monthly seasonal rates.
4. **Complete Period Coverage:** Covers the full 12-month calendar cycle to prevent seasonal bias.
5. **Longitudinal Caution:** Evolution trends reflect administrative reporting practices, police staffing shifts, and seasonal weather patterns across the complete dataset, not the behavioral development of an individual offender.

---

## Part H: Novel Behavioral Pattern Detection

Novelty is evaluated using a dual-paradigm architecture:
1. **Spherical K-Means Centroid Distance:** $d_{\text{centroid}} = 1 - \mathbf{v} \cdot \mathbf{c}_{\text{nearest}}$
2. **Isolation Forest Tree Ensemble:** Evaluated across the 70D unit feature space.

### Neutral Tier Labels & Descriptions
- **Commonly Observed Combination:** Operational traits align closely with dense historical clusters ($d_{\text{centroid}} \le 0.35$).
- **Less Common Combination:** Minor operational divergence from cluster centroids ($0.35 < d_{\text{centroid}} \le 0.50$).
- **Unusual Combination:** Significant multidimensional deviation from historical baselines ($d_{\text{centroid}} > 0.50$ or Isolation Forest anomaly flag).
- **Insufficient Information:** Incident data coverage is below 50%, precluding reliable density assessment.

**Scientific Rule:** Novelty designates statistical rarity within the historical corpus. It does NOT denote danger, guilt, risk, or a new offender.

---

## Part I: Incident Comparison & Network Connection Map

1. **Explicit Tri-State Comparison:**
   - **Matching Characteristics:** Confirmed positive or confirmed negative alignments.
   - **Differing Characteristics:** Divergent observed traits.
   - **Unknown Characteristics:** Fields where at least one incident is unspecified.
2. **Strict Exclusion of Unknowns:** Unknown fields are **never** counted as matches.
3. **Network Connection Map Disclaimer:** In graph visualizations, nodes represent legal crime categories and unsupervised behavioral archetypes, not identified persons or suspects.

---

## Verification & Test Matrix (Part J)

All requirements are verified in the automated test suite:
- `tests/test_domain_coverage.py`:
  - `test_domain_coverage_calculation`: Formula correctness across all 6 domains.
  - `test_not_applicable_prerequisites`: Non-applicable fields are not penalized.
  - `test_compact_behavioral_fingerprint`: Explicit Yes/No/Unknown/Not applicable statuses.
  - `test_similarity_query_self_exclusion`: Query incident never returns itself.
  - `test_observed_feature_comparison_domains`: 5 domain comparisons and cross-crime rationales.
  - `test_novelty_neutral_labels`: Neutral label assignment without danger/risk claims.
  - `test_comparison_unknown_fields_not_counted_as_matches`: Strict exclusion of unknown fields from matches.
- `tests/test_user_to_dna.py`: 5 passed.
- `tests/test_dna_comparison.py`: 13 passed.
- Frontend TypeScript Build (`npm run build`): Clean build, 0 errors.

---
*Crime Compass 🧭 — Different Incidents. Shared Behavioral Patterns.*
