# EXPLORE PATTERNS: DISCOVERED BEHAVIORAL ARCHETYPES

## 1. Executive Summary & Design Philosophy

The **EXPLORE PATTERNS** interface allows investigators, analysts, and researchers to explore recurrent behavioral archetypes discovered across the **220,663 incident** historical dataset. 

Rather than overwhelming the user with a dashboard dense with confusing statistical charts or exposing raw 200+ engineered feature names, the system employs **clean, intuitive pattern cards** backed by empirical machine learning artifacts:

```text
PATTERN 01
Day + Small Town + Property + No Weapon
Multiple crime categories (3 categories) • 17,725 incidents (8.0%)

PATTERN 04
Night + Residential + Property + Covert Entry
Multiple crime categories (3 categories) • 18,175 incidents (8.2%)

PATTERN 08
Night + Street + Contraband + Armed / Arrest
Multiple crime categories (3 categories) • 47,842 incidents (21.7%)
```

Clicking any card opens a **dedicated detail view** explaining:
1. **Why this pattern exists**: The operational modus operandi rationale uniting disparate statutory offenses.
2. **Crime categories involved**: Exact empirical incident counts and proportions.
3. **Behavioral characteristics**: Aggregated metrics on timing, target type, weapon utilization, and injury rates.
4. **Behavioral evolution**: A simple 3-stage longitudinal timeline (Early, Middle, Later periods) reflecting how behavioral characteristics varied across the dataset's historical span.
5. **Supporting evidence**: Exemplar historical cases and mathematical inter-category cosine convergence.
6. **"View Analysis Details"**: An expandable, collapsible technical section isolating model weights, cluster divergences ($\Delta$), and high-dimensional geometry.

---

## 2. Machine Learning Ground Truth

Every card and metric is derived directly from the pre-trained, production-validated models without synthetic or hardcoded values:

| Pattern ID | Code | Discovered Archetype Name | Empirical Formula | Historical Incidents | % of Dataset | Dominant Timing | MO Convergence |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **PATTERN 01** | `CCP_00` | Small-City Property & Structure Theft | `Day + Small Town + Property + No Weapon` | 17,725 | 8.03% | Daytime (85.2% day) | 74.7% |
| **PATTERN 02** | `CCP_01` | Domestic & Interpersonal Violence | `Evening + Domestic/Person + Weapon + Bodily Injury` | 24,056 | 10.90% | Evening/Night (48.8% night) | 88.0% |
| **PATTERN 03** | `CCP_02` | Suburban Larceny & Vehicle Theft | `Day + Suburban + Property + No Weapon` | 28,103 | 12.74% | Daytime (76.8% day) | 77.1% |
| **PATTERN 04** | `CCP_03` | Residential Property Infiltration | `Night + Residential + Property + Covert Entry` | 18,175 | 8.24% | Nocturnal (86.1% night) | 76.5% |
| **PATTERN 05** | `CCP_04` | Public Order & Alcohol Incidents | `Night + Weekend + Public Order + High Arrest` | 28,506 | 12.92% | Night/Weekend (58.9% night) | 90.7% |
| **PATTERN 06** | `CCP_05` | Commercial & White-Collar Fraud | `Day + Commercial + Regulatory + No Weapon` | 31,691 | 14.36% | Business Hours (87.2% day) | 74.5% |
| **PATTERN 07** | `CCP_06` | Metro Core Shoplifting & Shoplifting | `Day + Metropolitan + Retail Property + No Weapon` | 24,565 | 11.13% | Business Hours (77.8% day) | 76.8% |
| **PATTERN 08** | `CCP_07` | Street Weapons & Proactive Enforcement | `Night + Street + Contraband + Armed / Arrest` | 47,842 | 21.68% | Night/Street (62.8% night) | 75.3% |
| **Total** | — | **8 Discovered Behavioral Archetypes** | — | **220,663** | **100.0%** | — | — |

---

## 3. Pattern Card Structure

The main Explore Patterns view renders high-visibility, scannable cards structured as follows:

```text
┌─────────────────────────────────────────────────────────────────┐
│ PATTERN 01   CCP_00                         17,725 incidents   │
│ Small-City Property & Structure Theft                           │
│                                                                 │
│  ✨ Day + Small Town + Property + No Weapon                     │
│                                                                 │
│ 📁 Multiple crime categories (3 categories)                     │
│ [Daytime] [Small Town] [Property] [No Weapon]                   │
│                                                                 │
│ ─────────────────────────────────────────────────────────────── │
│ 🕒 Daytime                           View Detail →              │
└─────────────────────────────────────────────────────────────────┘
```

### Visual & Informational Components:
1. **Pattern Identifier & Code**: Systematic labeling (`PATTERN 01` to `PATTERN 08`) with backend cross-crime code (`CCP_00` to `CCP_07`).
2. **Behavioral Formula**: Formulated in bold, intuitive syntax (`Factor 1 + Factor 2 + Factor 3 + Factor 4`).
3. **Volume & Share**: Exact count of incidents assigned to this archetype and percentage of the 220,663 incident corpus.
4. **Crime Categories Scope**: Clear indication that the pattern spans multiple legal crime categories (e.g., Larceny, Burglary, Motor Vehicle Theft).
5. **Time Information**: Empirical execution timing (e.g., Nocturnal vs. Daytime concentration).
6. **Similarity / Strength**: Empirical cosine convergence indicating how closely diverse offenses in this cluster align behaviorally.

---

## 4. Interactive Pattern Detail View

When a user clicks any pattern card, the view expands to a dedicated investigation dossier displaying:

### 4.1 Why This Pattern Exists
A plain-English operational explanation describing the modus operandi logic that links diverse crimes together. For instance:
> *"Incidents in this pattern converge on consistent environmental and behavioral modus operandi parameters: Night + Residential + Property + Covert Entry. The Behavioral DNA engine identifies underlying behavioral alignment across statutory categories."*

### 4.2 Crime Categories Involved
Displays the statutory crime categories participating in the archetype with precise incident counts and percentages:
- Category Name (e.g., *Burglary / Breaking & Entering*)
- Historical Incidents (e.g., *14,204 incidents*)
- Representation Share (e.g., *78.2%*)

### 4.3 Behavioral Characteristics
Organized into intuitive, clean operational groupings without 200+ raw variable names:
- **Temporal Patterns**: Nighttime percentage, weekend distribution.
- **Location Context**: Residential vs. commercial vs. open public spaces.
- **Property Involvement**: Physical loss rate, average economic scale.
- **Weapons & Harm**: Weapon presence, firearm utilization, injury rate.
- **Enforcement Context**: On-scene arrest rate.

### 4.4 Behavioral Evolution Timeline
Integrates empirical longitudinal dynamics across the historical dataset into a clean 3-stage timeline:

```text
EARLY PERIOD (Jan – Apr)
Night + Residential + Property + No Weapon
Baseline nocturnal residential entry without weapon presence.

       ↓

MIDDLE PERIOD (May – Aug)
Night + Residential + Property + Covert Tooling
Increased prevalence of specialized entry tools during warmer months.

       ↓

LATER PERIOD (Sep – Dec)
Night + Mixed Structure + Property + Expedited Egress
Shift toward expedited egress with higher proportion of commercial structures.
```

### 4.5 Supporting Empirical Evidence
- **Inter-Category Cosine Similarity**: Average pairwise similarity between distinct statutory categories sharing this archetype.
- **Shannon Entropy & Simpson Diversity**: Quantifies behavioral distribution breadth across statutory boundaries.
- **Exemplar Incidents**: Real historical incident IDs matching the cluster centroid.

### 4.6 "View Analysis Details" (Collapsible Technical Drawer)
For criminologists and data scientists requiring technical audits:
- Vector dimension: 70-dimensional behavioral embedding.
- Algorithm: MiniBatch Spherical K-Means ($k=8$).
- Top distinctive feature divergences: Z-score deltas showing exact differences between cluster mean and global dataset mean ($\Delta$).

---

## 5. Mandatory Ethical & Investigative Neutrality

In accordance with system-wide ethics standards, the Explore Patterns page enforces strict guidelines:

1. **No Perpetrator Attribution**: The system never claims or implies that a pattern represents an individual offender or organized criminal group.
2. **Behavioral Archetypes Only**: Patterns represent recurrent environmental opportunities and operational behaviors across the historical corpus.
3. **Transparent Advisory**: Every detail view displays a permanent, highlighted advisory:
   > *"Advisory: Behavioral patterns represent recurrent operational dynamics and environmental opportunities discovered across the historical incident dataset. They do NOT establish that offenses were committed by the same individual or common perpetrator."*

---

## 6. API Endpoints

### 6.1 List All Discovered Pattern Cards
```http
GET /api/patterns
```
**Response:**
```json
{
  "total_patterns": 8,
  "corpus_incident_count": 220663,
  "patterns": [
    {
      "pattern_id": "PATTERN 01",
      "cluster_id": 0,
      "pattern_code": "CCP_00",
      "pattern_name": "Small-City Property & Structure Theft",
      "behavioral_formula": "Day + Small Town + Property + No Weapon",
      "key_characteristics": ["Daytime", "Small Town", "Property", "No Weapon"],
      "supporting_incident_count": 17725,
      "percentage_of_total": 8.03,
      "crime_categories_summary": "Multiple crime categories (3 categories)",
      "top_crime_categories": ["Larceny/Theft (72.4%)", "Burglary (18.1%)", "Motor Vehicle Theft (9.5%)"],
      "time_information": "Daytime (85.2% day, 26.5% weekend)",
      "similarity_strength_score": 74.7,
      "similarity_strength_label": "High Modus Operandi Convergence (0.747)",
      "summary": "Property crimes occurring primarily during daylight hours in smaller jurisdictions."
    }
  ]
}
```

### 6.2 Get Pattern Detail View
```http
GET /api/patterns/{pattern_id}
```
Accepts integer indices (`0`–`7`), pattern identifiers (`PATTERN 01`), or cross-crime codes (`CCP_00`). Returns the complete dossier with evolution timeline, categories breakdown, supporting evidence, and analysis details.

---

## 7. Verification & Testing

The pattern exploration module is thoroughly validated:
- `tests/test_explore_patterns.py`: Validates that all 8 pattern cards return non-zero empirical counts matching 220,663 incidents, verifies resolution of all identifier formats, tests the 3-stage evolution timeline, and asserts the presence of the mandatory non-offender advisory.
- Full regression suite: **163 passed tests** across backend test suites.
- Frontend compilation: Clean production build via TypeScript (`tsc -b`) and Vite (`vite build`) with **0 errors**.
