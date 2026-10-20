# CRIME DNA: Behavioral Pattern Fit & Novelty Detection

## 1. Overview & Purpose

In the CRIME DNA platform, **Novel Behavioral Pattern Detection** (Phase 9) assesses how well a submitted incident's **Behavioral DNA** aligns with the dominant behavioral patterns learned from the historical dataset.

Every incident entered by a user is evaluated in real time to answer two core analytical questions:
1. **Behavioral Pattern Fit**: How closely does this incident conform to established historical archetypes?
2. **Behavioral Novelty**: Does this incident represent a rare or previously unseen combination of modus operandi attributes?

If an incident exhibits an unusual behavioral combination, the platform flags it with the standardized alert:
> **⚠️ NOVEL BEHAVIORAL PATTERN**
> *"This incident contains a behavioral combination that does not closely match the major patterns learned from the historical dataset."*

---

## 2. Ethical Non-Offender Attribution Boundary

### Core Principles
- **Behavioral Combination vs. Individual Attribution**: Novelty refers strictly to the statistical rarity of a **feature combination** within the historical reference corpus.
- **Strictly Prohibited Terminology**: The platform and its algorithms **never** generate, suggest, or imply:
  - ❌ *suspicious person*
  - ❌ *dangerous person*
  - ❌ *criminal person*
  - ❌ *likely offender*
  - ❌ *future crime*
  - ❌ *high-risk individual*
- **Analytical Stance**: The system evaluates *what occurred* (the objective behavioral profile), not *who is responsible* or *what will occur in the future*.
- **Ethical Safeguard Shield**:
  > *"Novelty evaluation reflects the statistical rarity of this behavioral feature combination relative to the historical reference dataset. It does not evaluate individual criminality, person dangerousness, or future risk."*

---

## 3. Dual-Paradigm Scientific Methodology

Novelty is evaluated using the dual-paradigm unsupervised detection architecture developed and calibrated during Phase 9:

```
                            User Behavioral DNA
                        (70D Unit L2-Normalized Vector)
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
      Geometric Centroid Distance                 Structural Tree Isolation
        (Unit Hypersphere S^69)                       (Isolation Forest)
                 │                                           │
                 │ d_cent = 1 - ⟨v, c*⟩                      │ if_norm = 0.5 - 1.5 * raw_if
                 │                                           │
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                         Composite Novelty Score
                    S_novelty = 0.5 * d_cent + 0.5 * if_norm
                                       │
                                       ▼
                       Calibrated Quantile Tiers
                 (Standard | Moderate | High | Extreme)
```

### 1. Geometric Spherical Centroid Distance
The incident's unit vector $\mathbf{v} \in \mathbb{R}^{70}$ ($\|\mathbf{v}\|_2 = 1$) is projected against the centroid $\mathbf{c}^* \in \mathbb{R}^{70}$ of its nearest Spherical K-Means cluster archetype:
$$\text{dist}_{\text{cent}} = \max\left(0.0, 1.0 - \langle \mathbf{v}, \mathbf{c}^* \rangle\right)$$

### 2. Structural Tree Isolation Depth
The vector is passed through an ensemble of 100 Isolation Trees (trained on the historical corpus):
$$\text{norm\_if} = \max\left(0.0, \min\left(1.0, 0.5 - 1.5 \times \text{decision\_function}(\mathbf{v})\right)\right)$$

### 3. Calibrated Composite Novelty Score
$$\text{Novelty Score} = 0.5 \times \text{dist}_{\text{cent}} + 0.5 \times \text{norm\_if}$$
Bounded strictly in $[0.0, 1.0]$.

---

## 4. Documented Empirical Thresholds

Thresholds are **not arbitrary**; they are calibrated directly from the empirical quantile distribution of the 220,663 incident historical reference dataset (`anomaly_metadata.json`):

| Novelty Tier | Quantile Cutoff | Score Threshold | Population Proportion | Analytical Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Standard Behavioral Pattern** | Baseline ($< p_{95}$) | $< 0.4363$ | ~95.0% (209,630 incidents) | Conforms closely to known historical archetypes. Typical modus operandi. |
| **Moderate Behavioral Novelty** | Top 5% ($p_{95} - p_{99}$) | $[0.4363, 0.5985)$ | ~4.0% (8,827 incidents) | Noticeable variation from typical patterns; atypical feature pairing. |
| **High Behavioral Outlier** | Top 1% ($p_{99} - p_{99.9}$) | $[0.5985, 0.7383)$ | ~0.9% (1,985 incidents) | Significant behavioral divergence across multiple dimensions. |
| **Extreme Behavioral Outlier** | Top 0.1% ($\ge p_{99.9}$) | $\ge 0.7383$ | ~0.1% (221 incidents) | Extremely rare combination in the historical record. |

---

## 5. Behavioral Pattern Fit vs. Novelty

The platform reports two complementary perspectives for every incident:

| Metric | Scientific Basis | Normal Case | Novel Case |
| :--- | :--- | :--- | :--- |
| **Behavioral Pattern Fit** | $1.0 - \text{Novelty Score}$ combined with cosine alignment $\langle \mathbf{v}, \mathbf{c}^* \rangle \times 100$ | **High Fit** (e.g., $72.0\%-85.0\%$) | **Moderate Fit** or **Low Fit (Atypical)** |
| **Novelty Divergence** | Dual-paradigm composite score | **Standard Behavioral Pattern** ($< 0.4363$) | **Moderate / High / Extreme Novelty** ($\ge 0.4363$) |
| **Banner Status** | Standard vs. Alert | `STANDARD BEHAVIORAL PATTERN` | `⚠️ NOVEL BEHAVIORAL PATTERN` |

---

## 6. Identifying Unusual Supported Behavioral Factors

When an incident deviates from its nearest cluster baseline, the system isolates the specific behavioral features that drive the divergence:

### Mathematical Derivation
For each feature $j \in \{1 \dots 70\}$:
$$\Delta_j = v_j - c^*_j$$
Features are ranked by magnitude $|\Delta_j|$, filtering for meaningful deviations ($|\Delta_j| \ge 0.08$).

### Supported Human-Readable Behavioral Factors

| Raw Feature Column | Human-Readable Factor Label | Directional Impact |
| :--- | :--- | :--- |
| `has_weapon` / `weapon_count_scaled` | **Weapon Utilization** | *Elevated* (Weapon introduced where baseline is unarmed) |
| `is_multi_weapon` | **Multiple Weapon Arsenal** | *Elevated* (Coordinated multi-weapon tactical display) |
| `has_injury` / `injury_record_count_scaled`| **Physical Injury Infliction** | *Elevated* (Harm inflicted contrary to non-violent archetype) |
| `time_is_night` | **Nighttime Execution** | *Elevated* (Nocturnal timing in typically daytime pattern) |
| `time_is_weekend` | **Weekend Timing** | *Elevated* / *Suppressed* (Calendar day anomaly) |
| `property_value_log_scaled` | **High-Value Economic Impact** | *Elevated* (Extreme financial target magnitude) |
| `has_drug` / `suspected_drug_count_scaled` | **Narcotics Connection** | *Elevated* (Drug trade involvement in general crime) |
| `victim_count_scaled` / `is_multi_victim` | **Multiple Victims Targeted** | *Elevated* (Mass or group targeting) |
| `offender_count_scaled` / `is_co_offender` | **Co-Offender Coordination** | *Elevated* (Group syndicate vs. lone actor) |
| `has_criminal_activity` | **Associated Criminal Enterprise** | *Elevated* (Organized crime indicator) |
| `crime_against_person` | **Direct Interpersonal Focus** | *Elevated* (Violent element in property crime) |

---

## 7. Architecture & Code Integration

```
User Incident Submission
          ↓
Preprocessing & Behavioral DNA Encoding (src/features/input_bridge.py)
          ↓
BehavioralNoveltyService (src/services/novelty_service.py)
   ├── Unit Spherical Projection: cos_to_cent = ⟨v_unit, cent_unit⟩
   ├── Centroid Distance: dist_cent = max(0, 1 - cos_to_cent)
   ├── Isolation Forest Tree Depth: norm_if_score
   ├── Composite Score: composite_novelty = 0.5 * dist_cent + 0.5 * norm_if_score
   ├── Pattern Fit Assessment: pattern_fit_score = 1.0 - composite_novelty
   ├── Quantile Threshold Evaluation: p95 (0.4363), p99 (0.5985), p99.9 (0.7383)
   ├── Banner Generator: "⚠️ NOVEL BEHAVIORAL PATTERN" if novel
   ├── Factor Deviation Decomposer: Δ_j = v_j - c*_j mapped to Factor Names
   └── Ethical Non-Offender Shield Injection
          ↓
CrimeDnaAnalysisEngine (src/services/analysis_engine.py)
          ↓
FastAPI Response: POST /api/analyze/input (src/api/schemas.py)
          ↓
React Dashboard: InputAnalysisPage.tsx
   ├── Status Badge: Standard (Green) vs Outlier/Novel (Red)
   ├── Warning Banner: ⚠️ NOVEL BEHAVIORAL PATTERN (if unusual)
   ├── Dual Score Cards: Behavioral Pattern Fit vs Novelty Divergence
   ├── Most Unusual Supported Behavioral Factors Grid
   └── Ethical Attribution Safeguard Box
```

---

## 8. Test Suite Verification

Comprehensive test suites validate both normal and novel scenarios across backend services and HTTP endpoints:

| Test File | Test Case | Expected Behavior | Status |
| :--- | :--- | :--- | :--- |
| `tests/test_novel_behavior_user_flow.py` | `test_normal_incident_pattern_fit_and_novelty` | Shoplifting incident: Score $< 0.4363$, "Standard Behavioral Pattern", High Fit, no warning banner. | **PASSED** |
| `tests/test_novel_behavior_user_flow.py` | `test_novel_incident_triggers_warning_banner_and_factors` | Multi-weapon compound burglary: Score $\ge 0.4363$, "Moderate/High Novelty", triggers `⚠️ NOVEL BEHAVIORAL PATTERN`, extracts unusual factors. | **PASSED** |
| `tests/test_novel_behavior_user_flow.py` | `test_ethical_non_offender_language_guidelines` | Strictly asserts absence of prohibited personal terms (`suspicious person`, `future crime`, etc.). | **PASSED** |
| `tests/test_novel_behavior_user_flow.py` | `test_documented_empirical_thresholds` | Validates thresholds match Phase 9 exact cutoffs (`0.4363`, `0.5985`, `0.7383`). | **PASSED** |
| `tests/test_novel_behavior_user_flow.py` | `test_api_endpoint_serializes_novelty_result` | Validates full JSON serialization through `POST /api/analyze/input`. | **PASSED** |
| `tests/test_anomaly.py` | Phase 9 offline anomaly tests | Model artifact existence, score distributions, and dataset metadata. | **PASSED** |
| `tests/` | Full repository test suite | 140 automated tests across all 10 analytical modules. | **140 PASSED** |
