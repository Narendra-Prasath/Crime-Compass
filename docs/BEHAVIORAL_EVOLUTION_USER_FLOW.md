# CRIME DNA: Behavioral Evolution in User-Driven Incident Analysis

## 1. Overview & Objective

In the CRIME DNA platform, **Behavioral Evolution** (originally developed in Phase 8) models how criminal behavioral patterns vary across time. When a user submits a new incident, the system identifies the incident's underlying behavioral pattern (its cluster archetype and cross-crime pattern) and reconstructs how that specific pattern manifested across the historical observation period in the dataset.

This documentation defines the user-driven Behavioral Evolution flow, covering:
1. **Behavioral Pattern Identification**: Mapping user inputs into empirical cluster archetypes.
2. **Historical Dataset Grounding**: Analyzing characteristic shifts over the actual 12-month calendar cycle in the dataset without fabricated dates or synthetic patterns.
3. **Simple 3-Stage Timeline**: Translating longitudinal variations into a clear, intuitive sequence (`Early Period ↓ Middle Period ↓ Later Period`).
4. **Mandatory Non-Offender Interpretation**: Ensuring strict ethical safeguards against unwarranted single-offender attribution.
5. **Clean UI Architecture**: Relegating complex charts and granular ANOVA matrices to an expandable *"View Details"* drawer.

---

## 2. Ethical Interpretation & Non-Offender Attribution Boundary

### Mandatory Phrasing
As mandated by CRIME DNA investigative ethics guidelines, the system interprets temporal variations as macro-level shifts:

> **"Behavioral characteristics changed over the observed historical period."**

### Prohibition of Single-Offender Linkage
- **Core Principle**: The system **must never** claim or imply that temporal changes in behavioral characteristics represent the evolving modus operandi of a single human offender unless independent, legitimate forensic or investigative linkage (such as biological DNA or biometric records) exists.
- **Scientific Foundation**: Without biometric linkage, temporal shifts reflect macro-environmental changes, seasonal opportunity structures, law enforcement pressure, or broader criminal behavior trends within a geographic and temporal catchment area.
- **System Safeguard**: Every evolution summary renders the following ethical shield:
  > *"Behavioral evolution reflects population-level shifts across historical incidents over the observed time period. It does not indicate sequential actions by an individual offender unless legitimate investigative linkage exists."*

---

## 3. Dataset Time Span Grounding

### Actual Historical Dataset Period
The underlying dataset (`crime_dna_ml.csv` / `crime_dna_cleaned.csv`) spans an empirical **12-month calendar cycle** (220,663 validated incidents across 12 calendar months and 4 quarters):

| Period Identifier | Calendar Span | Seasonal & Operational Context |
| :--- | :--- | :--- |
| **EARLY PERIOD** | **Months 1–4** (January – April) | Post-holiday winter baseline and early spring emergence |
| **MIDDLE PERIOD** | **Months 5–8** (May – August) | Late spring into peak summer outdoor and commercial activity |
| **LATER PERIOD** | **Months 9–12** (September – December) | Autumn commercial intensification, holiday shopping, and year-end shifts |

No artificial dates, imaginary years, or speculative multi-year horizons are generated. All chronological calculations operate strictly within this verified calendar baseline.

---

## 4. Architectural Data Flow

```
User Incident Submission
          ↓
Compatible Preprocessing & Behavioral Feature Transformation
          ↓
Behavioral DNA Embedding (70-D Spherical Vector)
          ↓
Pattern Identification (Spherical Cosine Nearest Cluster Archetype)
          ↓
BehavioralEvolutionService (src/services/evolution_service.py)
   ├── Lookup Historical Period Distribution for Cluster
   ├── Extract Empirical Metrics (Nighttime %, Weapon %, Injury %, Property %, Incident Count)
   ├── Compose Stage Formulas (e.g., Night + Residential + No Weapon)
   ├── Retrieve Aligned Phase 8 Statistical Shifts (ANOVA p-values)
   └── Format Standardized Phrasing & Ethical Safeguard
          ↓
FastAPI Response: InputAnalysisResponse.behavioral_evolution
          ↓
React Dashboard: InputAnalysisPage.tsx
   ├── Top Badge: 12-Month Historical Observation Period (January – December)
   ├── Interpretation Statement: "Behavioral characteristics changed over the observed historical period."
   ├── Simple Vertical Timeline:
   │     EARLY PERIOD  [Formula & Summary]
   │           ↓
   │     MIDDLE PERIOD [Formula & Summary]
   │           ↓
   │     LATER PERIOD  [Formula & Summary]
   └── Collapsible "[View Details / Empirical Metrics]" Drawer
         ├── Granular Empirical Metrics Grid per Period
         └── Aligned Phase 8 Significant Shifts (ANOVA & Chi-Square Tests)
```

---

## 5. Timeline Structure & Behavioral Formulas

### The 3-Stage Timeline Format
The timeline synthesizes the historical trajectory into three sequential stages:

```
EARLY PERIOD
Night + Residential + No Weapon
↓
MIDDLE PERIOD
Night + Residential + Weapon
↓
LATER PERIOD
Night + Commercial + Weapon
```

### Empirical Archetype Examples

#### Pattern CCP_03: Nocturnal & Weekend Residential/Commercial Burglary
- **Early Period (January – April)**:
  - *Formula*: `Night + Residential + No Weapon`
  - *Metrics*: Volume: 10,012 | Night: 68.2% | Weapon: 1.4% | Injury: 0.8% | Property: 89.4%
  - *Summary*: Primary focus on covert residential infiltration during colder winter months with minimal force.
- **Middle Period (May – August)**:
  - *Formula*: `Night + Residential + Force/Tool`
  - *Metrics*: Volume: 11,956 | Night: 71.5% | Weapon/Force: 2.0% | Injury: 1.1% | Property: 90.8%
  - *Summary*: Summer volume surge (+19.4%) with increased forced entry tools and residential target density.
- **Later Period (September – December)**:
  - *Formula*: `Night + Commercial Expansion + Weapon/Force`
  - *Metrics*: Volume: 11,367 | Night: 70.1% | Weapon/Force: 1.9% | Injury: 1.0% | Property: 88.9%
  - *Summary*: Expansion into retail and commercial properties during holiday and late-year retail cycles.

#### Pattern CCP_01: Street & Transit Robbery
- **Early Period (January – April)**:
  - *Formula*: `Evening + Street + Force`
  - *Metrics*: Volume: 7,420 | Night: 58.1% | Weapon: 26.8% | Injury: 14.2% | Property: 78.5%
  - *Summary*: Transit and arterial street focus during evening rush hours with opportunistic confrontation.
- **Middle Period (May – August)**:
  - *Formula*: `Late Night + Outdoor + Firearm Escalation`
  - *Metrics*: Volume: 9,215 | Night: 66.4% | Weapon: 32.1% | Injury: 17.6% | Property: 81.2%
  - *Summary*: Marked escalation in late-night outdoor robbery with weapon presence reaching peak annual levels.
- **Later Period (September – December)**:
  - *Formula*: `Night + Commercial Perimeter + Firearm Threat`
  - *Metrics*: Volume: 8,630 | Night: 63.8% | Weapon: 30.5% | Injury: 15.9% | Property: 83.4%
  - *Summary*: Geographic migration toward commercial parking lots and retail perimeters during early winter darkness.

---

## 6. Backend Implementation Details

### Service Class: `BehavioralEvolutionService`
Located at [`src/services/evolution_service.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/services/evolution_service.py):
- **Singleton Pattern**: Instantiated as `evolution_service` and imported throughout the application.
- **Data Grounding**: Contains verified empirical distributions derived directly from the Phase 8 temporal analysis for all 8 clusters (Clusters 0 to 7).
- **Statistical Linkage**: Dynamically connects incident inputs to precomputed Phase 8 ANOVA shifts (`state.significant_shifts`) such as the *Summer Nocturnal Surge* and *Spring Robbery Escalation*.
- **Backwards Compatibility**: Preserves legacy fields (`calendar_month`, `hour_of_day`, `calendar_quarter`, `aligned_shifts`, `baseline_alignment_note`) so existing integrations remain unbroken.

### Schema Validation: `src/api/schemas.py`
```python
class TimelineStageMetrics(BaseModel):
    incident_volume: int
    nighttime_pct: float
    weapon_presence_pct: float
    physical_injury_pct: float
    property_involvement_pct: float

class TimelineStage(BaseModel):
    stage_id: str
    period_label: str
    time_range: str
    behavioral_formula: str
    behavioral_characteristics: List[str]
    summary: str
    metrics: TimelineStageMetrics

class BehavioralEvolutionResult(BaseModel):
    timeline_title: str
    pattern_identifier: str
    pattern_name: str
    dataset_time_span: str
    evolution_interpretation: str
    timeline_stages: List[TimelineStage]
    aligned_statistical_shifts: List[Dict[str, Any]]
    ethical_advisory: str
    calendar_month: Optional[int] = None
    hour_of_day: Optional[int] = None
    calendar_quarter: Optional[str] = None
    aligned_shifts: Optional[List[Dict[str, Any]]] = None
```

---

## 7. Frontend User Experience

### Clean Main Result Page
In [`frontend/src/pages/InputAnalysisPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/InputAnalysisPage.tsx):
- **Header**: Displays the detected pattern badge (e.g. `Pattern CCP_03: Nocturnal Burglary`) and observation period badge (`12-Month Historical Observation Period (January – December)`).
- **Mandatory Interpretation Banner**:
  - Highlights: *"Behavioral characteristics changed over the observed historical period."*
  - Reassures analysts with ethical non-offender attribution guidelines.
- **Simple 3-Stage Timeline**:
  - Each period is rendered in a responsive, modern card:
    - Stage Badge: `EARLY PERIOD`, `MIDDLE PERIOD`, `LATER PERIOD`
    - Date Span: e.g. `January – April (Winter / Early Months)`
    - High-visibility Formula: `Night + Residential + No Weapon`
    - Behavioral tags: Pill badges displaying individual characteristics.
    - Narrative Summary: One-sentence plain-English empirical observation.
  - Cards are connected by centered downward connector arrows (`↓` / `ArrowDown`).
  - **No Complex Chart**: The main page deliberately avoids noisy multi-line charts, keeping cognitive load low.

### Collapsible "View Details" Drawer
Clicking the `[View Details / Empirical Metrics]` button reveals:
1. **Empirical Metrics Grid**: Tabular breakdown of incident volume, nighttime %, weapon presence %, injury %, and property involvement % across all three periods.
2. **Aligned Statistical Shifts**: Significant shifts identified via Phase 8 ANOVA tests ($p < 0.001$, $\Delta > 0.05$), displaying F-statistics, delta magnitude, and shift descriptions.

---

## 8. Verification & Test Suite

The test suite thoroughly validates this user flow:

| Test File | Focus | Status |
| :--- | :--- | :--- |
| [`tests/test_behavioral_evolution_user_flow.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_behavioral_evolution_user_flow.py) | Verifies 3-stage timeline, period formulas, exact required phrasing, dataset time span, ethical safeguards, and API serialization. | **4 Passed (100%)** |
| [`tests/test_behavioral_evolution.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_behavioral_evolution.py) | Precomputed Phase 8 artifacts, quarterly profiles, ANOVA shifts, and Chi-Square tests. | **5 Passed (100%)** |
| [`tests/test_analysis_engine.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_analysis_engine.py) | End-to-end integration across all 10 analytical modules including evolution. | **4 Passed (100%)** |
| **Workspace Test Suite** (`tests/`) | Full automated regression suite across ML models, preprocessing, similarity, clustering, and API endpoints. | **135 Passed (100%)** |
