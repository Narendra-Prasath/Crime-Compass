# CRIME DNA — Incident DNA Comparison System (`Incident A vs Incident B`)

## 1. Overview & Architectural Scope

The **Crime DNA Comparison System** allows investigators, criminologists, and analytical users to perform rigorous, side-by-side comparative behavioral analysis between two incidents:

$$\text{Incident A} \quad \text{vs} \quad \text{Incident B}$$

Both incidents can originate from any combination of sources:
1. **Newly Entered Incident vs Newly Entered Incident** (e.g. testing hypothetical escalations or comparing two unindexed open cases)
2. **Newly Entered Incident vs Historical Indexed Incident** (e.g. comparing a fresh crime report against a known historical anchor such as `INC_000001`)
3. **Historical Incident vs Historical Incident** (e.g. comparing two historical case files across different crime categories or dates)

Crucially, **both incidents are transformed into the identical 70-dimensional Behavioral DNA vector representation** using the shared Phase 3 feature engineering pipeline and encoder (`BehavioralDNAEncoder`), ensuring zero divergence in mathematical scale or behavioral domain definitions.

```
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│           Incident A            │      │           Incident B            │
│ (Custom Payload / Historical ID)│      │ (Custom Payload / Historical ID)│
└────────────────┬────────────────┘      └────────────────┬────────────────┘
                 │                                        │
                 ▼                                        ▼
    Standardized Feature Extraction          Standardized Feature Extraction
                 │                                        │
                 ▼                                        ▼
    70D Unit L2 DNA Vector (v_A)             70D Unit L2 DNA Vector (v_B)
                 │                                        │
                 └───────────────┬────────────────────────┘
                                 │
                                 ▼
                     Behavioral Cosine Metric
                 S(A, B) = (v_A · v_B) × 100%
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     ▼                           ▼                           ▼
🧬 DNA Comparison Table   "What Changed?" Analysis    Matching / Differing
 (Feature Matrix ✓ / △)    (Escalations & Narrative)     Characteristics
```

---

## 2. Scientifically Valid DNA Similarity Representation

### 2.1 Vector Projection & Cosine Metric
Because each incident's Behavioral DNA vector $\mathbf{v} \in \mathbb{R}^{70}$ is projected into a unit hypersphere ($\|\mathbf{v}\|_2 = 1.0$), the similarity between Incident A and Incident B is computed via the dot product of their normalized vectors:

$$\text{Cosine Similarity} = \mathbf{v}_A \cdot \mathbf{v}_B = \sum_{i=1}^{70} v_{A,i} v_{B,i}$$

$$\text{Similarity Score (\%)} = \max\left(0.0, \, \min\left(100.0, \, (\mathbf{v}_A \cdot \mathbf{v}_B) \times 100\right)\right)$$

$$\text{Cosine Distance} = 1.0 - (\mathbf{v}_A \cdot \mathbf{v}_B)$$

### 2.2 Objective Tiering
The similarity percentage is mapped into objective behavioral affinity tiers:

| Similarity Score (%) | Match Tier | Analytical Interpretation |
|---|---|---|
| **90.0% – 100.0%** | **High Behavioral Convergence** | Near-identical modus operandi across temporal, spatial, target, and method dimensions. |
| **75.0% – 89.9%** | **Moderate-High Behavioral Alignment** | Strong alignment across primary behavioral dimensions with minor peripheral variations. |
| **55.0% – 74.9%** | **Moderate Behavioral Affinity** | Shared core characteristics (e.g., target type, diurnal pattern) accompanied by notable differences (e.g., weapon presence). |
| **35.0% – 54.9%** | **Partial / Low Behavioral Overlap** | Sparse behavioral overlap; predominant divergence across tactics and environmental contexts. |
| **0.0% – 34.9%** | **Divergent Behavioral Profiles** | Distinct modus operandi profiles with negligible behavioral commonality. |

*Note: Self-comparison (Incident A vs Incident A) mathematically guarantees $100.0\%$ similarity and $0.0$ cosine distance.*

---

## 3. DNA Comparison Table

The system presents a clean, feature-by-feature comparative matrix detailing primary behavioral dimensions:

### 🧬 DNA COMPARISON Table Specification

```
🧬 DNA COMPARISON

Feature              Incident A      Incident B      Result
Time                 Night           Night           ✓
Location             Residential     Residential     ✓
Property             Yes             Yes             ✓
Weapon               None            Handgun         △
Injury               No              No              ✓
Crime                Theft           Burglary        △
```

### Match Symbols & Criteria

- `✓` (**MATCH**): Dimensions exhibiting behavioral alignment (e.g., identical diurnal classification `Night` vs `Night`, or zero weapons in both incidents).
- `△` (**DIFFER / ESCALATION**): Dimensions exhibiting behavioral deviation or tactical shifts (e.g., `None` $\rightarrow$ `Handgun`, `Daytime` $\rightarrow$ `Night`, `No Injury` $\rightarrow$ `Injury`).
- `~` (**PARTIAL / ADAPTATION**): Dimensions exhibiting semantic proximity without full identity (e.g., related commercial vs retail location categories).

### Dimension Resolution Logic
1. **Time**: Normalized based on diurnal cycle (`Daytime` [06:00–19:59] vs `Night` [20:00–05:59]) and timestamp.
2. **Location**: Normalized into standard environment tiers (`Residential`, `Commercial / Retail`, `Open Space / Street`, `Public Transit`).
3. **Property**: Evaluated by property involvement flag and estimated economic value threshold.
4. **Weapon**: Evaluated by weapon involvement flag, weapon count, and tactical weapon classification (e.g., `None`, `Handgun / Firearm`, `Edged Weapon`).
5. **Injury**: Evaluated by physical harm flags, hospitalizations, or injury count.
6. **Crime**: Standardized high-level behavioral category (`Theft / Larceny`, `Burglary / Breaking & Entering`, `Robbery / Extortion`, `Assault / Violent Crime`).
7. **Victim Context**: Evaluated by victim count and target vulnerability profile.

---

## 4. Prominent "What Changed?" Behavioral Shift Analysis

A central requirement of the comparison engine is the prominent `"What Changed?"` diagnostic section. Rather than leaving the user to scan individual raw attributes, this section synthesizes high-level operational transitions:

### Components of "What Changed?"
1. **Executive Headline**: Dynamic summary encapsulating the primary behavioral delta (e.g., *"Behavioral transition in Time, Weapon: 3 matching dimensions, 3 shifted dimensions"*).
2. **Escalations**: Explicit detection of increased severity, violence, or tactical risk:
   - **Weapon Escalation**: Transition from unarmed to armed encounter (`None` $\rightarrow$ `Handgun`).
   - **Harm Escalation**: Transition from non-violent property theft to physical injury (`No Injury` $\rightarrow$ `Physical Injury Reported`).
   - **Economic Escalation**: Substantial increase in stolen property value.
   - **Victim Count Expansion**: Shift from solitary target to multiple victims.
3. **Tactical Transitions**: Non-escalatory modus operandi adaptations:
   - Temporal shifts (e.g., daytime opportunistic offense to nocturnal covert execution).
   - Spatial shifts (e.g., residential burglary to commercial robbery).
   - Method adaptations (e.g., stealth entry to confrontational demand).
4. **Narrative Synthesis**: Comprehensive English summary describing the strategic relationship between Incident A and Incident B.

---

## 5. Matching & Differing Characteristics

To aid investigative triage, all dimensions are distilled into two clear lists:

### MATCHING CHARACTERISTICS
- Items where both incidents exhibit identical behavioral vectors (e.g., *"Consistent diurnal timing (night execution)"*, *"Target environment remains residential"*, *"Shared property acquisition motive"*).

### DIFFERING CHARACTERISTICS
- Items where tactical decisions diverge (e.g., *"Weapon escalated from None in Incident A to Armed Encounter (Handgun) in Incident B"*, *"Crime category shifted from Theft to Burglary"*).

---

## 6. Subprofile Domain Energy Comparison

The 70 behavioral features are grouped into seven distinct domain subprofiles. The comparison engine computes the $L_2$ norm energy for each domain in Incident A and Incident B:

$$\text{Energy}(D) = \|\mathbf{v}_D\|_2 = \sqrt{\sum_{j \in D} v_j^2}$$

$$\Delta\text{Energy}(D) = \text{Energy}_B(D) - \text{Energy}_A(D)$$

Domains compared:
1. **Temporal Patterns**: Diurnal, hourly, and weekend cyclical tendencies.
2. **Spatial & Environmental**: Location type, urban density, and spatial vulnerability.
3. **Target Selection**: Unoccupied property vs populated settings, victim count.
4. **Modus Operandi / Method**: Planning level, forced entry, opportunistic behavior.
5. **Weapon Selection**: Unarmed vs firearm, blunt, or edged weapons.
6. **Harm & Violence**: Physical assault, officer confrontation, victim injuries.
7. **Context & Co-factors**: Narcotics indicators, arrest outcomes, property loss scale.

---

## 7. Backend Endpoints & Data Contracts

### 7.1 `POST /api/compare`
Executes complete comparative DNA analysis between two incidents.

#### Request Schema (`DnaComparisonRequest`)
```json
{
  "incident_a": {
    "label": "Incident A (Daytime Residential Theft)",
    "payload": {
      "scenario_title": "Daytime Residential Theft",
      "incident_date": "2024-05-10",
      "incident_time": "14:30",
      "crime_category": "theft",
      "has_property": true,
      "has_weapon": false,
      "has_injury": false,
      "location_type": "residence_home",
      "victim_count": 0
    }
  },
  "incident_b": {
    "label": "Incident B (Night Residential Burglary)",
    "payload": {
      "scenario_title": "Night Residential Burglary with Firearm",
      "incident_date": "2024-05-12",
      "incident_time": "02:15",
      "crime_category": "burglary",
      "has_property": true,
      "has_weapon": true,
      "weapon_types": ["handgun"],
      "has_injury": false,
      "location_type": "residence_home",
      "victim_count": 1
    }
  }
}
```

#### Response Schema (`DnaComparisonResponse`)
```json
{
  "comparison_title": "🧬 CRIME DNA COMPARISON",
  "incident_a": {
    "label": "Incident A (Daytime Residential Theft)",
    "incident_id": null,
    "source_type": "new_input"
  },
  "incident_b": {
    "label": "Incident B (Night Residential Burglary)",
    "incident_id": null,
    "source_type": "new_input"
  },
  "dna_similarity": {
    "similarity_score_pct": 74.38,
    "cosine_distance": 0.2562,
    "match_tier": "Moderate Behavioral Affinity",
    "affinity_summary": "Shared modus operandi characteristics with distinct elements."
  },
  "dna_comparison_table": [
    {
      "feature": "Time",
      "incident_a": "Daytime",
      "incident_b": "Night",
      "result": "△",
      "match_status": "DIFFER",
      "details": "Incident A: Daytime (14:30) vs Incident B: Night (02:15)"
    },
    {
      "feature": "Location",
      "incident_a": "Residential",
      "incident_b": "Residential",
      "result": "✓",
      "match_status": "MATCH",
      "details": "Both incidents targeted residential environments."
    },
    {
      "feature": "Property",
      "incident_a": "Yes",
      "incident_b": "Yes",
      "result": "✓",
      "match_status": "MATCH",
      "details": "Both incidents involved target property theft."
    },
    {
      "feature": "Weapon",
      "incident_a": "None",
      "incident_b": "Handgun",
      "result": "△",
      "match_status": "DIFFER",
      "details": "Incident A: None vs Incident B: Armed Encounter (Handgun)"
    },
    {
      "feature": "Injury",
      "incident_a": "No",
      "incident_b": "No",
      "result": "✓",
      "match_status": "MATCH",
      "details": "Zero physical injuries recorded in either incident."
    },
    {
      "feature": "Crime",
      "incident_a": "Theft",
      "incident_b": "Burglary",
      "result": "△",
      "match_status": "DIFFER",
      "details": "Cross-category comparison: Theft vs Burglary."
    }
  ],
  "matching_characteristics": [
    "Consistent residential location profile",
    "Property theft acquisition motive present in both incidents",
    "No physical victim injuries reported in either incident"
  ],
  "differing_characteristics": [
    "Diurnal shift: Incident A occurred in daytime, Incident B occurred at night",
    "Weapon escalation: Incident A was unarmed, Incident B involved a firearm",
    "Crime category transitioned from Theft to Burglary"
  ],
  "what_changed": {
    "headline": "Behavioral transition in Time, Weapon, Crime: 3 matching, 3 differing dimensions",
    "escalations": [
      "Weapon escalated from None to Armed Encounter (Handgun)"
    ],
    "transitions": [
      "Timing transitioned from Daytime to Night",
      "Crime category shifted from Theft to Burglary"
    ],
    "narrative": "Incidents share residential property targeting with zero victim injury, but diverge sharply in operational tactics: Incident B introduced nocturnal timing and a firearm.",
    "match_count": 3,
    "differ_count": 3,
    "total_dimensions_compared": 6
  },
  "subprofile_comparison": [
    {
      "group_name": "Temporal Patterns",
      "energy_a": 0.35,
      "energy_b": 0.42,
      "delta": 0.07,
      "alignment": "Aligned"
    },
    {
      "group_name": "Weapon Selection",
      "energy_a": 0.00,
      "energy_b": 0.68,
      "delta": 0.68,
      "alignment": "Elevated in B"
    }
  ],
  "ethical_advisory": "Behavioral similarity reflects shared modus operandi characteristics between incidents. It does NOT indicate the same offender or establish investigative linkage without physical forensic evidence."
}
```

### 7.2 `GET /api/compare/presets`
Returns demonstrative comparison scenarios for immediate exploration:
- **Preset 1**: Unarmed Residential Theft vs Armed Residential Burglary (escalation demo)
- **Preset 2**: New User Incident vs Historical Anchor (`INC_000001`)
- **Preset 3**: Historical Pair (`INC_000001` vs `INC_000002`)

---

## 8. Frontend Implementation (`DnaComparisonPage.tsx`)

The frontend workbench provides an intuitive dual-column layout:

1. **Incident Configuration Workbench**:
   - Independent toggles for Incident A and Incident B between **Custom Input** and **Historical Incident ID**.
   - Input forms for date, time, category, location, weapons, property, and injuries.
   - Quick Preset Selection bar with instant autofill.
2. **Interactive DNA Comparison Header**:
   - Displays the computed DNA similarity score percentage with a visual progression bar.
   - Match tier badge and cosine distance indicator.
3. **DNA Comparison Table (`🧬 DNA COMPARISON`)**:
   - Clean columns: `Feature`, `Incident A`, `Incident B`, `Result`.
   - Distinct badges for `✓ MATCH` and `△ DIFFER`.
4. **Prominent "What Changed?" Card**:
   - Highlights escalations with alert badges (firearm introductions, injury escalations).
   - Displays transition chips and plain-English investigative narrative.
5. **Matching & Differing Characteristics Cards**:
   - Dual-card layout listing confirmed alignments and divergence points.
6. **Subprofile Domain Energies Grid**:
   - Interactive radar / bar energy comparison showing domain-specific shifts (e.g. Weapon vs Temporal).
7. **Investigative Advisory Banner**:
   - Prominently displays the ethical attribution boundary.

---

## 9. Ethical & Legal Safeguards (Attribution Boundary)

The Crime DNA system strictly enforces the following investigative principles:

> [!IMPORTANT]
> **BEHAVIORAL SIMILARITY DOES NOT EQUAL OFFENDER IDENTITY**
> 
> High DNA similarity indicates that two incidents share overlapping modus operandi patterns (such as commercial targeting, nighttime execution, or forced entry methods). It **does not** prove, imply, or suggest that the crimes were committed by the same individual, ring, or suspect.
> 
> The system **never**:
> - Generates suspect names, likelihood of guilt, or recidivism scores.
> - Uses inflammatory phrases such as *"same suspect"*, *"likely offender"*, or *"dangerous individual"*.
> - Substitutes for forensic evidence (e.g., biological DNA, fingerprints, ballistics, or verified video surveillance).
