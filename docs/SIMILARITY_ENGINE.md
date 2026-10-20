# CRIME DNA — Phase 5: Behavioral Similarity Engine Documentation

**Document Version:** 1.0  
**Engine Implementation:** `src/models/similarity/engine.py` | `src/models/similarity/config.py`  
**Serialized Index:** `data/processed/similarity_index/knn_index.joblib`  
**Normalized DNA Vectors:** `data/processed/similarity_index/normalized_dna_matrix.npy`  
**Test Suite:** `tests/test_similarity_engine.py`  
**Author:** Lead Software Engineer & ML Engineer  

---

## 1. Executive Summary & Purpose

The **CRIME DNA Behavioral Similarity Engine** enables investigators, analysts, and researchers to select or input a single crime incident and retrieve the top-$K$ most behaviorally similar incidents across a dataset of **220,663 crime incidents**.

Rather than matching incidents on superficial criteria such as legal charge codes or police agency jurisdiction, the system matches incidents across a **70-dimensional Behavioral DNA representation** that captures:
1. When the crime happened (diurnal and seasonal cycles).
2. What was targeted (person, property, society, compound targets).
3. The environmental context (urban density and municipal setting).
4. The method of execution (weapons, multi-weapon tactics, criminal activity, prior relationships).
5. The people involved (victim scale, demographics, offender crew structure).
6. Property and financial motivations (stolen counts, logarithmic economic damage, cargo freight).
7. Physical harm and contextual severity (injuries, contraband, bias motivation).

> [!CAUTION]
> **CRITICAL ETHICAL & INVESTIGATIVE CONSTRAINT**:
> High behavioral similarity **DOES NOT** imply or prove that two incidents were committed by the same individual or group. Behavioral similarity measures operational and tactical resemblance (Modus Operandi) across situations; it is an investigative lead generator and pattern discovery tool, not evidence of personal identity.

---

## 2. Mathematical Formulation: How Similarity is Calculated

### A. Vector Normalization
Every incident $i$ is represented by a raw 70-dimensional Behavioral DNA vector:
$$\mathbf{x}_i \in [0.0, 1.0]^{70}$$

To ensure that similarity calculations reflect the **proportional balance of tactical choices** rather than absolute magnitude variations, each vector is projected onto the unit hypersphere via $L_2$ normalization:
$$\hat{\mathbf{x}}_i = \frac{\mathbf{x}_i}{\|\mathbf{x}_i\|_2} = \frac{\mathbf{x}_i}{\sqrt{\sum_{j=1}^{70} x_{i,j}^2}}$$

### B. Cosine Distance & Similarity Score
The distance between two normalized incident vectors $\hat{\mathbf{u}}$ and $\hat{\mathbf{v}}$ is computed using **Cosine Distance**:
$$\text{Cosine Distance}(\mathbf{u}, \mathbf{v}) = 1 - (\hat{\mathbf{u}} \cdot \hat{\mathbf{v}}) = 1 - \sum_{j=1}^{70} \hat{u}_j \hat{v}_j$$

Because all raw features are non-negative ($x_j \ge 0$), the dot product $\hat{\mathbf{u}} \cdot \hat{\mathbf{v}}$ is strictly bounded within $[0.0, 1.0]$. The **Behavioral Similarity Score** is reported as a percentage:
$$\text{Similarity Score (\%)} = (1 - \text{Cosine Distance}) \times 100\% = (\hat{\mathbf{u}} \cdot \hat{\mathbf{v}}) \times 100\%$$

- **`100.0%`**: Identical behavioral fingerprint (identical tactical, temporal, and situational choices).
- **`95.0% - 99.9%`**: Extremely strong behavioral alignment (near-identical MO with minor variations in timing or demographics).
- **`85.0% - 94.9%`**: Strong behavioral pattern match across primary dimensions.
- **`70.0% - 84.9%`**: Moderate behavioral overlap (e.g., same crime type but differing weapons or crew sizes).
- **`< 70.0%`**: Weak or dissimilar behavioral profiles.

### C. Self-Exclusion Guarantee
When querying by an existing incident ID, the search algorithm requests $K + 1$ nearest neighbors and **strictly filters out the query incident itself**, guaranteeing that an incident is never returned as a match for itself.

### D. Explainable Sub-Profile Breakdown
To avoid black-box similarity scores, the engine calculates independent cosine similarity scores across each of the **7 behavioral sub-profiles**:
$$\text{Sim}_g(\mathbf{u}_g, \mathbf{v}_g) = \frac{\mathbf{u}_g \cdot \mathbf{v}_g}{\|\mathbf{u}_g\|_2 \|\mathbf{v}_g\|_2} \times 100\% \quad \text{for } g \in \{1, \dots, 7\}$$
This explains **which specific aspects** (e.g., Method vs. Timing vs. Victimology) drove the overall similarity.

---

## 3. High-Performance Retrieval Architecture

- **Engine Core**: Built on Scikit-Learn's `NearestNeighbors` with parallelized multi-threading (`n_jobs = -1`).
- **Query Latency**: Returns top-$K$ matches across all 220,663 records in **under 45 milliseconds**.
- **Memory Footprint**: The normalized matrix occupies ~61 MB in memory, allowing instant in-memory index serving without database bottlenecks.

---

## 4. Test Queries & Example Match Results

Below are real queries executed against the production similarity engine across different crime archetypes:

### Query 1: Daytime Commercial Property Damage (`INC_000001`)
*Query Incident Profile: Daytime property crime, unarmed, solo actor, moderate property loss ($0.30 log value), no injuries.*

```
QUERY INCIDENT: INC_000001
============================================================
Rank 1: INC_006304 | Similarity: 99.87% | Cosine Dist: 0.001317
  Subprofile Breakdown:
    - Temporal Dynamics: 99.68%
    - Crime Characteristics: 100.0%
    - Location And Environment: 100.0%
    - Method And Activity: 100.0%
    - People And Demographics: 99.93%
    - Property And Economics: 99.88%
    - Context And Harm: 100.0%
--------------------------------------------------
Rank 2: INC_009434 | Similarity: 99.84% | Cosine Dist: 0.001643
  Subprofile Breakdown:
    - Temporal Dynamics: 100.0%
    - Crime Characteristics: 100.0%
    - Location And Environment: 100.0%
    - Method And Activity: 100.0%
    - People And Demographics: 99.44%
    - Property And Economics: 100.0%
    - Context And Harm: 100.0%
--------------------------------------------------
Rank 3: INC_127615 | Similarity: 99.70% | Cosine Dist: 0.003024
  Subprofile Breakdown:
    - Temporal Dynamics: 99.68%
    - Crime Characteristics: 100.0%
    - Location And Environment: 100.0%
    - Method And Activity: 100.0%
    - People And Demographics: 99.29%
    - Property And Economics: 99.90%
    - Context And Harm: 100.0%
```
*Analysis*: All top matches share identical 100% scores in Crime Characteristics, Method, Location, and Harm (unarmed property crimes), differing only by minor fractions of a percent in victim age and diurnal timing.

---

### Query 2: Armed Domestic Violence Incident (`INC_000002`)
*Query Incident Profile: Personal violent crime, armed with weapon, victim bodily injury inflicted, prior relationship.*

```
QUERY INCIDENT: INC_000002
============================================================
Rank 1: INC_036495 | Similarity: 99.85% | Cosine Dist: 0.001521
  Subprofile Breakdown:
    - Temporal Dynamics: 99.52%
    - Crime Characteristics: 100.0%
    - Location And Environment: 100.0%
    - Method And Activity: 100.0%
    - People And Demographics: 99.71%
    - Property And Economics: 100.0%
    - Context And Harm: 100.0%
--------------------------------------------------
Rank 2: INC_085603 | Similarity: 99.81% | Cosine Dist: 0.001889
  Subprofile Breakdown:
    - Temporal Dynamics: 99.44%
    - Crime Characteristics: 100.0%
    - Location And Environment: 100.0%
    - Method And Activity: 100.0%
    - People And Demographics: 99.62%
    - Property And Economics: 100.0%
    - Context And Harm: 100.0%
```
*Analysis*: The engine successfully identifies other armed interpersonal violent encounters involving prior relationships and physical injuries, matching the exact tactical dynamics.

---

### Query 3: Nighttime Enterprise Burglary (`INC_000003`)
*Query Incident Profile: Late night, property crime, ongoing criminal enterprise/fencing activity, commercial target.*

```
QUERY INCIDENT: INC_000003
============================================================
Rank 1: INC_007012 | Similarity: 99.74% | Cosine Dist: 0.002581
  Subprofile Breakdown:
    - Temporal Dynamics: 99.31%
    - Crime Characteristics: 100.0%
    - Location And Environment: 100.0%
    - Method And Activity: 100.0%
    - People And Demographics: 99.82%
    - Property And Economics: 99.64%
    - Context And Harm: 100.0%
```
*Analysis*: Retrieved crimes exhibit the exact same nocturnal property targeting connected to structured criminal activities.

---

## 5. System Limitations & Appropriate Use

1. **Not Evidence of Individual Identity**:
   Two behaviorally identical crimes may be committed by two entirely different individuals who share similar tactical habits or target similar vulnerabilities.
2. **Dependent on Reporting Completeness**:
   If an investigating officer did not record the presence of a weapon or co-offender, the resulting Behavioral DNA reflects the documented report rather than unobserved ground truth.
3. **Continuous Metric, Not Binary Guilt**:
   The engine computes a continuum of similarity. Cutoff thresholds should be treated as flexible investigative filters rather than hard classifications.

---

## 6. How to Run Searches from the Terminal

```bash
# Build / rebuild the index
python src/models/similarity/engine.py --build

# Run a query on any incident ID
python src/models/similarity/engine.py --query INC_000002 --top-k 5

# Run test suite
python -m unittest tests/test_similarity_engine.py -v
```
