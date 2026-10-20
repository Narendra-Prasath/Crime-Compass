# CRIME DNA — Hidden Behavioral Pattern Discovery System

## 1. Executive Overview

Statutory legal classifications (e.g., *Burglary*, *Theft*, *Robbery*, *Assault*) describe legal elements of criminal offenses rather than operational modus operandi. In reality, offenses cataloged under distinct statutory headers frequently share identical behavioral DNA, temporal rhythms, environmental settings, and victim-offender interaction dynamics.

The **Hidden Behavioral Pattern Discovery System** upgrades CRIME DNA's unsupervised clustering (Phase 6) and cross-crime pattern analysis (Phase 7) into a **user-facing real-time intelligence capability**. When a user submits an incident, the engine evaluates its 70-dimensional Behavioral DNA vector against empirical behavioral archetypes learned from the historical 220,663 incident corpus.

### Key Capabilities
- **Real-Time Association**: Evaluates cosine similarity to all 8 spherical cluster centroids.
- **Empirical Quantification**: Returns exact supporting historical incident counts, category counts, and cross-category representation percentages.
- **Salient Behavioral Formula**: Synthesizes a transparent 4-part behavioral signature (e.g., `Night + Residential + Property involved + No injury`).
- **Scientifically Grounded Confidence**: Tiers association strength using spherical cosine alignment rather than fabricated percentages.
- **Ethical Integrity**: Strictly bounds explanations to behavioral patterns and shared modus operandi, avoiding any claims regarding individual perpetrator identity.

---

## 2. Architectural Architecture

```
User Incident Input
       ↓
Input Bridge Feature Transformation (70D Unit Vector u)
       ↓
Hidden Behavioral Pattern Service (src/services/pattern_discovery.py)
       ↓
├── Evaluates Cosine Similarity against all 8 Empirical Cluster Centroids (Ck)
├── Identifies Primary Archetype (k* = argmax Sk) and Secondary Affinities
├── Extracts Dominant Behavioral Characteristics (Time + Location + Property + Harm)
├── Retrieves Empirical Incident Counts & Category Representation from Phase 7 Artifacts
└── Evaluates Association Confidence Tier (Strong, Moderate, Weak)
       ↓
Central Analysis Engine Response (src/services/analysis_engine.py)
       ↓
├── API Response Schema: hidden_behavioral_patterns (src/api/schemas.py)
└── Frontend UI: "🔗 BEHAVIORAL PATTERN DETECTED" (frontend/src/pages/InputAnalysisPage.tsx)
```

---

## 3. Mathematical Grounding & Association Scoring

### 3.1 Spherical Cosine Alignment to Empirical Centroids

Let $u \in \mathbb{R}^{70}$ be the unit $L_2$-normalized Behavioral DNA vector of the query incident ($\|u\|_2 = 1$).

From the unsupervised MiniBatch K-Means model trained during Phase 6, the corpus is partitioned into $K = 8$ spherical clusters with centroid vectors $c_k \in \mathbb{R}^{70}$. Normalizing each centroid yields the unit archetype direction:

$$C_k = \frac{c_k}{\|c_k\|_2}, \quad \forall k \in \{0, \dots, 7\}$$

The association score between query incident $u$ and pattern archetype $k$ is the cosine similarity:

$$S_k = u \cdot C_k = \sum_{j=1}^{70} u_j \cdot C_{kj} \in [-1, 1]$$

The primary associated behavioral pattern is:

$$k^* = \arg\max_{k \in \{0, \dots, 7\}} S_k$$

The spherical Euclidean distance to the archetype centroid is:

$$d(u, C_{k^*}) = 1.0 - S_{k^*}$$

### 3.2 Transparent Association Confidence Tiering

To prevent arbitrary or unscientific probability assertions, the system classifies $S_{k^*}$ into transparent, documented confidence tiers:

| Cosine Alignment ($S_{k^*}$) | Confidence Tier | Interpretation |
|---|---|---|
| **$S_{k^*} \ge 0.80$** | `Strong Association` | Strong behavioral alignment with the historical archetype centroid. |
| **$0.60 \le S_{k^*} < 0.80$** | `Moderate Association` | Moderate alignment; shares dominant modus operandi traits with minor divergence. |
| **$S_{k^*} < 0.60$** | `Weak Association` | Atypical or transitional behavioral pattern; higher novelty relative to baseline archetypes. |

---

## 4. Behavioral Characteristics & Formula Synthesis

Rather than returning opaque cluster IDs, the system synthesizes a structured, human-readable behavioral signature chain representing the incident's salient behavioral dimensions:

```
🔗 BEHAVIORAL PATTERN DETECTED

Night
+
Residential
+
Property involved
+
No injury

Found across multiple crime categories.
```

### Synthesis Methodology

The 4-part formula is dynamically extracted from actual incident inputs and empirical pattern dimensions:

1. **Temporal Dimension**:
   - `Night`: Incident occurred between 20:00 and 06:00 or `is_night == True`.
   - `Daytime`: Incident occurred between 06:00 and 20:00.
2. **Location Dimension**:
   - `Residential`: Private dwelling, apartment, residential property.
   - `Commercial`: Store, retail establishment, business facility.
   - `Public Space`: Street, sidewalk, park, public access area.
   - `Transit / Vehicle`: Public transportation, vehicle, parking structure.
   - `Metropolitan Core` / `Small Municipality`: Jurisdiction density profile.
3. **Property / Contraband Dimension**:
   - `Property involved`: Physical property targeted, stolen, or damaged.
   - `Contraband / Drug involvement`: Illicit substances seized or involved.
   - `No property involved`: Interpersonal or regulatory incident without property loss.
4. **Harm / Weapon Dimension**:
   - `No injury`: No physical injury sustained by victims.
   - `Bodily injury`: Physical injury or trauma documented.
   - `Weapon displayed`: Firearms, cutting instruments, or force enhancers brandished.
   - `On-scene arrest`: Immediate custody effected by responding officers.

**Formula String**:
$$\text{Formula} = \text{Temporal} + \text{Location} + \text{Property} + \text{Harm}$$

---

## 5. Empirical Historical Grounding (Zero Hardcoding)

All metrics displayed in the user interface are sourced directly from precomputed, reproducible model artifacts (`cross_crime_patterns.json`, `cluster_profiles.json`, `cluster_metadata.json`):

| Pattern ID | Historical Archetype Name | Supporting Incidents | Categories Represented | Primary Dominant Traits |
|---|---|---|---|---|
| `CCP_00` | Small-City Property & Structure Theft | **17,725** | **3** | Daytime + Small Municipality + Property + No Weapon |
| `CCP_01` | Violent Armed Interpersonal & Domestic Assaults | **74,429** | **6** | Armed + Bodily Injury + Relationship Ties + Public/Home |
| `CCP_02` | Suburban & Mid-Sized Town Daytime Property Theft | **35,193** | **2** | Daytime + Commercial/Suburban + Property + No Injury |
| `CCP_03` | Nocturnal & Weekend Residential/Commercial Burglary | **33,335** | **3** | Night + Residential + Property + No Injury |
| `CCP_04` | Weekend Nightlife Vice & Public Order Enforcement | **8,656** | **7** | Night + Public Space + On-Scene Arrest + Society Offenses |
| `CCP_05` | Regulatory & Non-Drug Societal Enterprise Offenses | **8,096** | **6** | Daytime + Administrative/Society + Non-Drug + Citations |
| `CCP_06` | Metropolitan Core High-Density Larceny & Shoplifting | **25,542** | **3** | Daytime + Metropolitan Core + Retail Property + No Weapon |
| `CCP_07` | Narcotics Trafficking & Contraband Vice Operations | **17,687** | **4** | Contraband + Street/Vehicle + On-Scene Arrest + No Injury |

### Total Historical Corpus
$$\sum_{k=0}^{7} \text{Incidents}_k = 220,663 \quad \text{incidents}$$

---

## 6. Ethical Non-Offender Attribution Framework

### Mandatory Analytical Boundary

The pattern discovery system strictly identifies **behavioral patterns across incidents**, reflecting common environmental incentives, target opportunities, and modus operandi dynamics.

- **Prohibited Claims**: The system NEVER claims or implies that two or more incidents were committed by the same person, individual, or criminal syndicate.
- **Approved Wording**:
  > *"These crime categories share a similar behavioral profile."*
  > *"Found across multiple crime categories."*
- **Required Ethical Advisory**:
  > *"CRIME DNA detects behavioral patterns across incidents. These patterns indicate shared modus operandi and environmental factors, not that offenses were committed by the same individual."*

---

## 7. Service Implementation & API Schema

### Service Layer: `src/services/pattern_discovery.py`

Exposes `HiddenBehavioralPatternService` with primary method:

```python
def identify_patterns(
    self,
    norm_vec: np.ndarray,
    input_data: Dict[str, Any],
    state: ApplicationState
) -> Dict[str, Any]:
    ...
```

### Pydantic Schema: `HiddenBehavioralPatternResult`

```python
class HiddenBehavioralPatternResult(BaseModel):
    pattern_detected: bool = True
    pattern_identifier: str = Field(..., examples=["CCP_03"])
    pattern_name: str = Field(..., examples=["Cross-Crime: Nocturnal & Weekend Residential/Commercial Burglary"])
    archetype_name: str = Field(..., examples=["Nocturnal & Weekend Residential/Commercial Burglary"])
    behavioral_characteristics: List[str] = Field(..., examples=[["Night", "Residential", "Property involved", "No injury"]])
    behavioral_formula: str = Field(..., examples=["Night + Residential + Property involved + No injury"])
    number_of_supporting_historical_incidents: int = Field(..., examples=[33335])
    number_of_crime_categories_represented: int = Field(..., examples=[3])
    relevant_crime_categories: List[CategoryRepresentation]
    association_strength: AssociationStrengthDetail
    is_cross_crime_pattern: bool = True
    cross_crime_summary: str = "Found across multiple crime categories."
    shared_profile_text: str = "These crime categories share a similar behavioral profile."
    associated_patterns: Optional[List[AssociatedPatternItem]] = None
    inter_category_similarities: Optional[Dict[str, Any]] = None
    cross_crime_evidence: Optional[Dict[str, Any]] = None
    ethical_advisory: str
    cluster_id: int
    cluster_name: str
    macro_category: str
    distance_to_centroid: float
    cluster_summary: str
    archetype_details: Optional[Dict[str, Any]] = None
```

---

## 8. Frontend User Experience

The user interface in `frontend/src/pages/InputAnalysisPage.tsx` displays the pattern discovery card prominently upon submission:

1. **Header Banner**:
   - `🔗 BEHAVIORAL PATTERN DETECTED` badge with pulsing amber accent.
   - Pattern Identifier chip (`CCP_03`).
   - Confidence Tier Pill (`Moderate Association (72.9%)`).
2. **Behavioral Formula Block**:
   - Visually distinct chips chained with `+` connectors:
     `● Night` + `● Residential` + `● Property involved` + `● No injury`
3. **Cross-Category Modus Operandi Banner**:
   - `"Found across 3 crime categories. These crime categories share a similar behavioral profile."`
4. **Empirical Supporting Metrics**:
   - Supporting Historical Incidents: `33,335 incidents`
   - Statutory Crime Categories: `3 Distinct Categories`
   - Category Breakdown: `Property (99.2% • 33,065 incidents)`, `Person + Property (0.7% • 238 incidents)`, `Person (0.1% • 31 incidents)`.
5. **Ethical Compliance Footer**:
   - Green Shield icon with explicit non-offender advisory statement.

---

## 9. Verification & Automated Test Suite

A dedicated automated test suite (`tests/test_hidden_behavioral_patterns.py`) verifies:

1. `test_hidden_pattern_detection_structure`: Complete schema integrity and required fields.
2. `test_values_come_from_actual_model_and_not_hardcoded`: Burglary vs. Assault discrimination, verifying counts match `cross_crime_patterns.json`.
3. `test_behavioral_characteristics_formula_synthesis`: Correct decomposition of formula components matching query attributes.
4. `test_cross_crime_text_and_shared_profile_wording`: Phrasing compliance across statutory categories.
5. `test_ethical_non_offender_guidelines`: Explicit enforcement of non-offender attribution.
6. `test_multi_pattern_associated_patterns_ranking`: Ordered ranking of all 8 pattern archetypes by cosine similarity.
7. `test_api_endpoint_serializes_hidden_behavioral_patterns`: Full HTTP integration test on `/api/analyze/input`.

**Execution Result**:
```bash
.venv/bin/python -m pytest tests/test_hidden_behavioral_patterns.py -v
# 7 passed in 3.80s
# Total suite: 131 passed in 20.47s
```
