# NEW USER INCIDENT → BEHAVIORAL DNA PIPELINE

## 1. Executive Summary

The **User Incident → Behavioral DNA Pipeline** bridges ad-hoc user-submitted crime incidents with the existing **CRIME DNA ML Engine**. It guarantees that newly entered incident scenarios pass through the **exact same compatible preprocessing and feature transformation logic** developed during Phase 3, without retraining the main historical reference models or creating an incompatible preprocessing divergent path.

```
                    ┌──────────────────────────────────────────────┐
                    │               User Input Form                │
                    │   (Incident Input Schema & Behavioral UI)    │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Pydantic 422 Validation             │
                    │ (Bounds, Enum Constraints, Positive Values)  │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │       Existing Preprocessing Alignment       │
                    │  (IncidentInputBridge.to_cleaned_dataframe)  │
                    │   - Sentinels & Missing Value Alignment      │
                    │   - Column Categorization Matching Phase 2   │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │     Phase 3 BehavioralDNAEncoder.transform   │
                    │   - 7 Subprofile Feature Transformations     │
                    │   - Exact 70-Dimensional Feature Taxonomy    │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │         Behavioral DNA Representation        │
                    │  1. Human-Readable Fingerprint (Dynamic)     │
                    │  2. Machine-Readable Vector (70D Unit L2)    │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │         Downstream ML Analysis Engine        │
                    │  ├── Cosine KNN Similarity (Top-K Matches)   │
                    │  ├── Spherical K-Means (Cluster Archetype)   │
                    │  ├── Cross-Crime Behavioral Bridges          │
                    │  ├── Behavioral Evolution & Drift Tracking   │
                    │  ├── Isolation Forest Anomaly Detection      │
                    │  └── SHAP/Additive Similarity Attribution    │
                    └──────────────────────────────────────────────┘
```

---

## 2. No Divergence: Reusing Existing Preprocessing & Transformation

### 2.1 The Core Design Constraint
A critical requirement of the CRIME DNA architecture is:
> **Do NOT create a separate incompatible preprocessing pipeline.**

In Phase 3, the historical reference knowledge base (`data/raw/crime_dna_ml.csv`) was cleaned into `data/processed/crime_dna_cleaned.csv` and transformed into 70 behavioral features by `BehavioralDNAEncoder` in `src/features/dna_encoder.py`.

The input bridge (`src/features/input_bridge.py`) directly instantiates and reuses the production `BehavioralDNAEncoder`:
```python
from src.features.dna_encoder import (
    BehavioralDNAEncoder,
    ORDERED_FEATURE_NAMES,
    FEATURE_GROUPS,
)

class IncidentInputBridge:
    def __init__(self):
        self.dna_encoder = BehavioralDNAEncoder()
        ...
```

### 2.2 Dataframe Bridge Architecture
When a user submits an incident payload, `to_cleaned_dataframe(data)` constructs a 1-row `pandas.DataFrame` that conforms identically to the schema of `crime_dna_cleaned.csv`:
1. **Identifiers**: Assigns a deterministic query identifier `USR-INPUT-LIVE`.
2. **Temporal Features**: Maps `incident_date` to `incident_year`, `incident_month`, `incident_day`, and derives `day_of_week`. Maps `incident_time` into `incident_hour` ($0 \dots 23$) and `incident_minute` ($0 \dots 59$).
3. **Categorical Alignments**: Maps human-selected population settings (`mid_sized_city`, `rural_suburban`, etc.) to the exact FBI UCR population group codes (`1A`, `2`, `3`, `7`, etc.) present in the reference dataset.
4. **Behavioral Flags & Metrics**: Populates numeric and binary fields (`weapon_count`, `victim_count`, `offender_count`, `property_value`, `has_injury`, `has_arrest`, etc.) adhering to the cleaning rules from Phase 2.

The DataFrame is then passed into:
```python
dna_df = self.dna_encoder.transform(cleaned_df)
```
This guarantees that **every single one of the 70 feature calculations** (sinusoidal cyclical time, ratio bounds, one-hot category expansions, weapon indicators, property transformations) executes through the exact same logic.

---

## 3. Behavioral DNA Representations

The backend produces both human-readable and machine-readable representations simultaneously:

### 3.1 Human-Readable Behavioral DNA Fingerprint

Rather than displaying raw numeric float vectors to an investigator, the system translates the submitted behavioral profile into an intuitive, dynamic fingerprint.

#### Dynamic Generation Guarantee
**No labels or emojis are hardcoded.** Every trait and chip is derived directly from the actual submitted inputs:

- **Temporal / Diurnal Cycle**:
  - `🌙 Night (22:30)` if hour $\ge 20$ or $< 6$
  - `☀️ Daytime (14:15)` if $6 \le \text{hour} < 20$
  - `📅 Weekend (Saturday)` vs `🗓️ Weekday (Tuesday)`
- **Environmental Context**:
  - `🏢 Metropolitan Core`, `🏙️ Commercial / Urban Area`, `🏠 Residential / Suburban`, or `🌾 Rural Jurisdiction` based on `population_setting`.
- **Force & Weaponry**:
  - `🔫 Armed Encounter (1 weapon)` vs `🚫 No Weapon (Unarmed)`
- **Victim Impact**:
  - `👤 1 Victim (age 34)` vs `👥 3 Victims (avg age 28)`
- **Offender Dynamic**:
  - `👤 Solo Perpetrator` vs `👥 2 Co-Offenders (avg age 22)`
- **Property Loss**:
  - `📦 Property Involved ($4,500 value)` vs `🚫 No Property Involved`
- **Harm & Legal Context**:
  - `🩹 Physical Injury Sustained` vs `🛡️ No Injury Reported`
  - `⚖️ Immediate On-Scene Arrest` vs `🏃 Offender Fled (No Arrest)`

#### Presentation Schema
```json
{
  "title": "BEHAVIORAL DNA",
  "summary_chips": [
    "🌙 Night",
    "🏢 Metropolitan Core",
    "🔫 Armed",
    "👥 2 Victims",
    "📦 Property involved",
    "🩹 Injury sustained",
    "📅 Weekend"
  ],
  "traits": [
    {
      "category": "Temporal Pattern",
      "icon": "🌙",
      "label": "Night (22:30)",
      "description": "Incident occurred during nighttime hours on a Weekend"
    },
    {
      "category": "Environmental Setting",
      "icon": "🏢",
      "label": "Metropolitan Core",
      "description": "Jurisdiction classified as Metropolitan Core"
    },
    {
      "category": "Weapon Utilization",
      "icon": "🔫",
      "label": "Armed Encounter",
      "description": "Perpetrator armed with 1 weapon"
    },
    {
      "category": "Victim Dynamics",
      "icon": "👥",
      "label": "2 Victims",
      "description": "Targeted 2 individual(s), average age 34"
    },
    {
      "category": "Property & Economics",
      "icon": "📦",
      "label": "Property Involved",
      "description": "Property affected with estimated value of $4,500"
    },
    {
      "category": "Physical Harm",
      "icon": "🩹",
      "label": "Physical Injury",
      "description": "Physical injuries were sustained during the incident"
    }
  ],
  "plain_text": "BEHAVIORAL DNA\n\n🌙 Night (22:30)\n🏢 Metropolitan Core\n🔫 Armed Encounter (1 weapon)\n👥 2 Victims (avg age 34)\n📦 Property Involved ($4,500 value)\n🩹 Physical Injury Sustained\n📅 Weekend"
}
```

---

### 3.2 Machine-Readable ML Representation

The machine-readable payload contains the mathematical vectors and subprofile activations consumed by downstream ML models:

```json
{
  "vector_dimension": 70,
  "feature_names": [
    "temporal_hour_sin",
    "temporal_hour_cos",
    "temporal_month_sin",
    "temporal_month_cos",
    "temporal_is_weekend",
    "temporal_is_night",
    ...
  ],
  "raw_vector": [0.3826, 0.9238, 0.5, 0.866, 1.0, 1.0, ...],
  "normalized_vector": [0.0821, 0.1983, 0.1073, 0.1859, 0.2146, ...],
  "subprofile_energies": {
    "temporal": 0.3842,
    "spatial_environmental": 0.2915,
    "modus_operandi": 0.5120,
    "victim_selection": 0.4287,
    "offender_grouping": 0.3811,
    "economic_target": 0.6124,
    "aggression_risk": 0.4912
  },
  "active_traits": [
    {
      "feature": "temporal_is_night",
      "value": 1.0,
      "energy": 0.2146,
      "subprofile": "temporal"
    },
    {
      "feature": "mo_weapon_present",
      "value": 1.0,
      "energy": 0.2146,
      "subprofile": "modus_operandi"
    }
  ],
  "feature_vector_dict": {
    "temporal_is_night": 1.0,
    "mo_weapon_present": 1.0,
    ...
  }
}
```

Key mathematical properties:
1. **Unit $L_2$ Normalization**: $\|\mathbf{v}_{\text{norm}}\|_2 = 1.0 \pm 10^{-5}$, enabling direct cosine distance computation:
   $$\text{Cosine Distance}(\mathbf{u}, \mathbf{v}) = 1 - \langle \mathbf{u}, \mathbf{v} \rangle$$
2. **Subprofile Energy**: Quantifies the normalized magnitude across the 7 behavioral subprofiles:
   $$E_g = \sqrt{\sum_{j \in g} v_{\text{norm}, j}^2}$$

---

## 4. Integration with Existing ML Components

The generated 70D unit vector $\mathbf{v}_{\text{norm}}$ feeds directly into the 6 core ML engines:

| ML Component | Input | Action | Compatibility Status |
| :--- | :--- | :--- | :--- |
| **Similarity Engine** (`BehavioralSimilarityEngine`) | $\mathbf{v}_{\text{norm}} \in \mathbb{R}^{70}$ | Exact Cosine KNN nearest neighbor query against 11,061 indexed historical records. Returns Top-K similar cases with similarity scores and subprofile breakdowns. | **100% Compatible** |
| **Clustering Model** (`BehavioralClusterer`) | $\mathbf{v}_{\text{norm}} \in \mathbb{R}^{70}$ | Spherical K-Means centroid projection. Assigns cluster archetype ($k \in [0, 7]$), calculates distance to centroid, and returns archetype profile. | **100% Compatible** |
| **Cross-Crime Engine** (`CrossCrimeAnalyzer`) | Top matches & $\mathbf{v}_{\text{norm}}$ | Identifies non-obvious behavioral parallels across different legal categories sharing modus operandi. | **100% Compatible** |
| **Temporal Evolution** (`BehavioralEvolutionAnalyzer`) | $\mathbf{v}_{\text{norm}}$ & Assigned Cluster | Measures behavioral drift and longitudinal alignment relative to temporal baseline epochs. | **100% Compatible** |
| **Anomaly Detection** (`IsolationForest`) | $\mathbf{v}_{\text{norm}}$ | Computes decision function score and anomaly tier (Typical, Moderate Outlier, High Outlier, Extreme Novelty). | **100% Compatible** |
| **Explainability Engine** (`BehavioralSimilarityExplainer`) | $\mathbf{v}_{\text{norm}} \times \mathbf{u}_{\text{hist}}$ | Exact additive attribution: $\text{contrib}_i = u_i \cdot v_i$. Explains *why* the input matches historical incidents. | **100% Compatible** |

---

## 5. Verification and Test Proofs

The pipeline is validated by automated tests in `tests/test_user_to_dna.py` and `tests/test_input_bridge.py`:

```bash
.venv/bin/pytest tests/test_user_to_dna.py tests/test_input_bridge.py -v
```

### Verified Test Cases:
1. **`test_dna_generation_valid_input`**:
   - Confirms vector dimension is exactly 70.
   - Proves unit $L_2$ norm: $\|\mathbf{v}\|_2 = 1.0$.
   - Confirms all values lie within $[0.0, 1.0]$.
   - Validates dynamic generation of human-readable labels matching input values (`🌙 Night (21:45)`, `🔫 Armed Encounter (2 weapons)`, `👥 2 Victims`, etc.).
2. **`test_dna_generation_dynamic_labels_daytime_unarmed`**:
   - Proves labels are dynamic and not hardcoded: a daytime unarmed scenario emits `☀️ Daytime (14:15)`, `🚫 No Weapon (Unarmed)`, and contains **no** references to `🌙 Night` or `🔫 Armed`.
3. **`test_compatibility_with_existing_ml_components`**:
   - Queries `state.similarity_engine.model.kneighbors()`: validates shape `(1, 5)` and distance bounds $[0.0, 2.0]$.
   - Predicts cluster via `state.clusterer.predict_cluster()`: returns cluster ID $0 \le k < 8$ with valid centroid distance.
   - Evaluates `state.isolation_forest.decision_function()`: produces finite real decision scores.
4. **`test_no_fake_or_unmapped_features`**:
   - Confirms that feature columns produced by the bridge match `ORDERED_FEATURE_NAMES` with zero unknown or fabricated features.
5. **`test_invalid_input_rejection`**:
   - Submits negative victim counts, negative property values, and invalid hour values ($25$).
   - Verifies that FastAPI and Pydantic reject the request with HTTP `422 Unprocessable Entity`.
