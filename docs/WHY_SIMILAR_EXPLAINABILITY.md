# "WHY SIMILAR?" Explainable AI (XAI) System

## 1. Operational Rationale & Philosophy

In criminal behavioral analysis, returning an opaque similarity score (such as **"Similarity = 91%"**) is operationally insufficient and dangerous for decision-making. Investigators, analysts, and domain experts require transparent, verifiable answers to three fundamental questions:

1. **Why** are these two incidents or crime categories considered behaviorally similar?
2. **Which specific dimensions** of conduct, timing, environment, or target selection account for that alignment?
3. **Where do they diverge**, preventing false assumptions of uniform modus operandi?

**CRIME DNA** implements an **exact additive attribution system** grounded directly in linear algebra. It decomposes cosine similarity across 70 continuous behavioral dimensions into human-understandable behavioral domains without fabricating importance weights or using arbitrary heuristic percentages.

---

## 2. Mathematical Foundation: Additive Inner-Product Decomposition

### 2.1 The Axiom of Efficiency

Every incident in CRIME DNA is represented by a unit vector $u \in \mathbb{R}^{70}$ on the $L_2$ hypersphere ($\|u\|_2 = 1, \|v\|_2 = 1$). The cosine similarity between any two incidents $u$ and $v$ is their dot product:

$$\text{Sim}(u, v) = u^\top v = \sum_{j=1}^{70} u_j \cdot v_j$$

Because the dot product is strictly bilinear and additive, the total similarity score is exactly equal to the sum of feature-level inner products:

$$c_j = u_j \cdot v_j$$

### 2.2 Group-Level Additive Attribution

Let $\mathcal{G} = \{G_1, G_2, \dots, G_K\}$ represent a partition of the 70 features into distinct behavioral domains. The exact additive contribution of behavioral group $G_k$ is:

$$C_{G_k} = \sum_{j \in G_k} u_j \cdot v_j$$

Because $\bigcup_{k=1}^K G_k = \{1, \dots, 70\}$ and $G_k \cap G_m = \emptyset$, the conservation law holds exactly:

$$\sum_{k=1}^K C_{G_k} = \text{Sim}(u, v)$$

The share percentage of total similarity contributed by group $G_k$ is:

$$P_{G_k} = \frac{C_{G_k}}{\text{Sim}(u, v)} \times 100\% \quad \left(\text{where } \sum_{k=1}^K P_{G_k} = 100\%\right)$$

Zero feature importance values are fabricated; every attribution is an exact projection of the underlying 70D vector math.

---

## 3. Understandable Behavioral Domains

Features are grouped into 7 human-interpretable operational domains:

| Behavioral Domain | Group Key | Included Dimensions | Example Features |
|:---|:---|:---:|:---|
| **Time** | `temporal_dynamics` | 6 | Hour cyclical sine/cosine, month cyclical sine/cosine, weekend flag, day of week |
| **Location** | `location_and_environment` | 7 | Population tiers (Metropolitan Core, Large City, Small City, Town, Rural, State Police) |
| **Crime Context** | `crime_characteristics` | 7 | Offense counts, statutory categories, attempt status |
| **Method / Weapon** | `method_and_activity` | 6 | Weapon present flag, total weapons count, weapon types count, syndicate activity |
| **People / Victim-Offender** | `people_and_demographics` | 9 | Victim count, average victim age, victim sexes count, offender count, group size, relationship |
| **Property** | `property_and_economics` | 10 | Property involved, property records, stolen count, log-scaled property value, cargo theft |
| **Activity & Context** | `context_and_harm` | 9 | Physical injury, injury count, narcotics involvement, suspected drug types, on-scene arrest |

---

## 4. Transparent Match Tiers & Status Indicators

Rather than generating arbitrary heuristic percentages for each subprofile, the system evaluates the **normalized subprofile cosine alignment**:

$$S_{G_k} = \frac{\sum_{j \in G_k} u_j v_j}{\|u_{G_k}\|_2 \cdot \|v_{G_k}\|_2}$$

Based on $S_{G_k}$ and contribution sign $C_{G_k}$, the system assigns transparent qualitative tiers:

| Subprofile Alignment ($S_G$) | Match Tier | Status | Indicator | Example User Label |
|:---:|:---:|:---:|:---:|:---|
| $S_G \ge 0.70$ ($C_G \ge 0$) | **Strong match** | `match` | **✓** | `✓ Same time pattern` / `✓ Similar location context` |
| $0.40 \le S_G < 0.70$ ($C_G \ge 0$) | **Moderate match** | `match` | **✓** | `✓ Similar method / weapon context` |
| $S_G < 0.40$ or $C_G < 0$ | **Weak match** | `divergence` | **△** | `△ Different weapon context` / `△ Different property context` |

### User Interface Presentation Format

```
WHY SIMILAR?

✓ Same time pattern               [Strong match] (35.0% share)
✓ Similar location context        [Strong match] (23.2% share)
✓ Similar property context        [Strong match] (27.0% share)
△ Different weapon context        [Weak match]   ( 0.0% share)

Plain-English Behavioral Explanation:
"The strongest behavioral similarities are the time pattern, location context, and property involvement."
```

---

## 5. Dynamic Plain-English Explanation Synthesis

The explanation is **never hardcoded or pre-canned**. It is synthesized dynamically from the top contributing matching groups:

1. Groups with `status == "match"` and $C_G > 0$ are ranked by absolute inner-product contribution $C_G$.
2. The top 2 or 3 matching domains are converted into grammatical noun phrases:
   - `temporal_dynamics` $\to$ **"time pattern"**
   - `location_and_environment` $\to$ **"location context"**
   - `property_and_economics` $\to$ **"property involvement"**
   - `method_and_activity` $\to$ **"weapon and operational method"**
   - `people_and_demographics` $\to$ **"victim-offender dynamics"**
   - `crime_characteristics` $\to$ **"crime context"**
   - `context_and_harm` $\to$ **"activity and enforcement context"**
3. The core sentence is synthesized:
   > *"The strongest behavioral similarities are the time pattern, location context, and property involvement."*
4. If a prominent divergence exists (e.g. `Different weapon context` due to Armed vs Unarmed encounter), a contrastive statement is appended:
   > *"However, there is a divergence in weapon context."*

---

## 6. Schema & API Integration

### 6.1 `why_similar_explanation` Response Object

Returned by both `POST /api/analyze/input` (for real-time user incidents) and `GET /api/explain/{id1}/{id2}` / `POST /api/explain` (for historical incident pairs):

```json
{
  "target_incident_id": "INC_022325",
  "overall_similarity_pct": 92.3,
  "plain_english_explanation": "The strongest behavioral similarities are the time pattern, property involvement, and location context.",
  "behavioral_group_comparisons": [
    {
      "group_key": "temporal_dynamics",
      "group_name": "Time",
      "status": "match",
      "indicator": "✓",
      "label": "✓ Same time pattern",
      "raw_label": "Same time pattern",
      "match_tier": "Strong match",
      "similarity_score": 0.9796,
      "contribution_score": 0.2842,
      "share_percentage": 35.0,
      "details": "Operating hours and diurnal cycle alignment"
    },
    {
      "group_key": "property_and_economics",
      "group_name": "Property",
      "status": "match",
      "indicator": "✓",
      "label": "✓ Same property context",
      "raw_label": "Same property context",
      "match_tier": "Strong match",
      "similarity_score": 0.9997,
      "contribution_score": 0.2195,
      "share_percentage": 27.0,
      "details": "Targeted property records and economic valuation"
    },
    {
      "group_key": "location_and_environment",
      "group_name": "Location",
      "status": "match",
      "indicator": "✓",
      "label": "✓ Same location context",
      "raw_label": "Same location context",
      "match_tier": "Strong match",
      "similarity_score": 1.0,
      "contribution_score": 0.1884,
      "share_percentage": 23.2,
      "details": "Jurisdictional population density and environment tier"
    },
    {
      "group_key": "method_and_activity",
      "group_name": "Method / Weapon",
      "status": "divergence",
      "indicator": "△",
      "label": "△ Different weapon context",
      "raw_label": "Different weapon context",
      "match_tier": "Weak match",
      "similarity_score": 0.0,
      "contribution_score": 0.0,
      "share_percentage": 0.0,
      "details": "Weaponry, lethal force, and operational execution method"
    }
  ],
  "group_attributions": [
    {
      "group_key": "temporal_dynamics",
      "display_name": "Time",
      "absolute_contribution": 0.2842,
      "share_percentage": 35.0
    }
  ],
  "top_matching_features": [
    {
      "feature_name": "hour_sin",
      "contribution": 0.1412,
      "input_value": 0.5,
      "match_value": 0.5,
      "description": "Cyclical time-of-day harmonic coordinate (sine)"
    }
  ]
}
```

---

## 7. Verification & Automated Test Coverage

Automated tests in [`tests/test_why_similar.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_why_similar.py) and [`tests/test_explainability.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_explainability.py) verify all specifications:

1. `test_why_similar_not_just_single_number`:
   Verifies that responses contain structured comparisons, top matching features, and plain-English sentences rather than just a single percentage.
2. `test_behavioral_groups_coverage`:
   Verifies that Time, Location, Crime Context, Method / Weapon, Property, People, and Activity are completely represented.
3. `test_no_invented_feature_importance_or_fake_percentages`:
   Mathematically proves exact inner-product efficiency ($\sum_G C_G = \text{Sim}(u, v)$) and verifies transparent qualitative tiers.
4. `test_group_comparison_indicators_and_labels`:
   Verifies checkmark (`✓`) and divergence marker (`△`) formatting.
5. `test_plain_english_explanation_generated_from_analysis`:
   Verifies natural language sentence synthesis format.
6. `test_contrastive_divergences_identified`:
   Proves armed vs unarmed comparisons correctly flag Method / Weapon as divergent (`△ Different weapon context`).
7. `test_api_analyze_input_returns_why_similar`:
   Validates serialization across the FastAPI `/api/analyze/input` endpoint.
8. `test_api_explain_endpoint_returns_why_similar`:
   Validates serialization across `/api/explain/{id1}/{id2}`.
