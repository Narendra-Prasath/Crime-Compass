# Cross-Crime Behavioral DNA Matching Engine

## 1. Overview & System Rationale

Traditional criminal intelligence systems rely almost exclusively on **statutory penal codes** (e.g., California Penal Code, FBI UCR offense classifications) to index and search incident records. Under conventional paradigms, if an analyst inspects a **Theft** incident, database queries are partitioned strictly to other thefts; similarly, **Burglary** queries are isolated from **Robbery** or **Aggravated Assault**.

However, criminal modus operandi and behavioral patterns routinely transcend legal statutory boundaries:
- A nocturnal armed confrontation in an urban alley may be legally classified as **Aggravated Assault** if no property was successfully taken, but as **Armed Robbery** if a wallet was seized, or as **Burglary** if the confrontation began on private curtilage.
- An offender executing systematic reconnaissance, silent forced entry, and high-value target selection shares identical behavioral DNA whether the charge is statutory **Commercial Burglary**, **Grand Larceny**, or **Cargo Theft**.

**CRIME DNA** resolves this fundamental flaw by decoupling mathematical similarity from legal labeling. The system represents every incident as a **70-dimensional continuous Behavioral DNA vector** on a unit $L_2$ hypersphere and executes nearest-neighbor retrieval across the **global 220,663 incident index** without statutory pre-filtering.

---

## 2. Mathematical Foundation: Category Non-Dominance

### 2.1 Dimensional Distribution in 70D Behavioral Space

The 70-dimensional Behavioral DNA vector balances comprehensive operational dimensions across eight distinct subprofiles:

| Subprofile Domain | Dimensions | Description & Primary Features |
|:---|:---:|:---|
| **Temporal Profile** | 6 | Hour cyclical sine/cosine, month cyclical sine/cosine, weekend flag, day-of-week |
| **Spatial / Urban Context** | 7 | Population tiers (Metropolitan, Large City, Mid-Sized, Small City, Town, Rural, State Highway) |
| **Weapons & Operational Method** | 6 | Weapon present flag, total weapon count, weapon types count, syndicate activity, prior relationship |
| **Victimology & Demographics** | 9 | Victim count, average victim age, victim sexes count, victim types, vulnerable victim flag |
| **Perpetrator Demographics** | 9 | Offender count, co-offender group flag, average offender age, offender sexes count |
| **Property & Economic Impact** | 10 | Property involved, property record count, stolen count, log-scaled property value, cargo theft |
| **Context, Harm & Narcotics** | 9 | Injury sustained, injury count, drug involvement, suspected drug count, arrest on scene |
| **Statutory Classification** | 7 | Person, Property, Society, Person & Property, Person & Society, Property & Society, All-Three |
| **Aggression Index** | 7 | Synthesized escalation vector |

### 2.2 Mathematical Proof of Non-Dominance

Statutory category flags occupy only **7 out of 70 dimensions** ($\sim 10\%$ of dimensions). Because every vector $x \in \mathbb{R}^{70}$ is normalized to unit Euclidean length ($\|x\|_2 = 1$), the cosine similarity between two incidents $u$ and $v$ is given by the inner product:

$$\text{Sim}(u, v) = u^\top v = \sum_{i=1}^{70} u_i v_i = \sum_{i \in \text{Behavioral}} u_i v_i + \sum_{j \in \text{Category}} u_j v_j$$

When two incidents share an identical operational signature (e.g., nocturnal timing, metropolitan core, lethal weapon deployment, group co-offenders, victim injury, and commercial property loss) but bear differing statutory labels (e.g., $u$ marked as `Crimes Against Persons` and $v$ marked as `Property Crime`):

$$\sum_{j \in \text{Category}} u_j v_j \approx 0 \quad \text{while} \quad \sum_{i \in \text{Behavioral}} u_i v_i \ge 0.75$$

Consequently, the overall similarity score reaches **$75\%$ to $85\%$**, ensuring that genuine behavioral affinities are surfaced even when statutory labels diverge.

---

## 3. Result Grouping & Representation

### 3.1 `SIMILAR BEHAVIORAL INCIDENTS` Grouping Structure

To provide clear operational clarity for criminal intelligence analysts, search results are explicitly categorized under:

```json
{
  "title": "SIMILAR BEHAVIORAL INCIDENTS",
  "query_crime_category": "Person",
  "cross_crime_indicator": "Similar behavioral characteristics were found across different crime categories.",
  "has_cross_crime_matches": true,
  "same_category_count": 3,
  "cross_category_count": 2,
  "matches": [
    {
      "rank": 1,
      "incident_id": "INC_134151",
      "crime_category": "Crimes Against Persons (Assault/Violence)",
      "similarity": "76.4%",
      "similarity_score_pct": 76.4,
      "cosine_distance": 0.236,
      "is_cross_crime_match": false,
      "category_relationship": "Same Crime Category",
      "relevant_behavioral_characteristics": [
        "🌙 Nocturnal execution (03:00)",
        "🔫 Armed encounter (weapon deployed)",
        "🏙️ Commercial / Urban jurisdiction",
        "👤 Solo victim targeted",
        "👥 Co-offender group (3 perpetrators)"
      ]
    },
    {
      "rank": 2,
      "incident_id": "INC_000590",
      "crime_category": "Property Crime (Theft/Burglary)",
      "similarity": "75.5%",
      "similarity_score_pct": 75.5,
      "cosine_distance": 0.245,
      "is_cross_crime_match": true,
      "category_relationship": "Different Crime Category",
      "cross_crime_indicator": "⚡ Cross-Crime Match: Shares behavioral characteristics with Property Crime (Theft/Burglary)",
      "relevant_behavioral_characteristics": [
        "🌙 Nocturnal execution (23:00)",
        "🔫 Armed encounter (weapon deployed)",
        "🏙️ Commercial / Urban jurisdiction",
        "👥 Multiple victims (3 victims)",
        "👥 Co-offender group (6 perpetrators)"
      ]
    },
    {
      "rank": 3,
      "incident_id": "INC_022743",
      "crime_category": "Person & Property Crime (Robbery/Extortion)",
      "similarity": "75.5%",
      "similarity_score_pct": 75.5,
      "cosine_distance": 0.245,
      "is_cross_crime_match": true,
      "category_relationship": "Different Crime Category",
      "cross_crime_indicator": "⚡ Cross-Crime Match: Shares behavioral characteristics with Person & Property Crime (Robbery/Extortion)",
      "relevant_behavioral_characteristics": [
        "🌙 Nocturnal execution (01:00)",
        "🔫 Armed encounter (weapon deployed)",
        "🏙️ Commercial / Urban jurisdiction",
        "👤 Solo victim targeted",
        "👥 Co-offender group (3 perpetrators)"
      ]
    }
  ],
  "grouped_by_category_relationship": {
    "same_crime_category": [...],
    "different_crime_categories": [...]
  },
  "ethical_advisory": "CRIME DNA detects behavioral similarity only. It does not establish offender identity, common perpetrator, criminal group association, or legal guilt."
}
```

### 3.2 Required Cross-Crime Indicator

When any of the top-$k$ nearest neighbors belong to a statutory category different from the query incident, the system issues the exact standardized indicator:

> **"Similar behavioral characteristics were found across different crime categories."**

In the user interface, this manifests as:
- A highlighted violet callout banner with network icon (`Network`)
- Distinctive category relationship badges:
  - `Cross-Crime Match` (Violet badge `#c084fc` on `rgba(168, 85, 247, 0.15)`)
  - `Same Crime Category` (Slate badge `#94a3b8` on `rgba(148, 163, 184, 0.10)`)
- Clear behavioral traits chips explaining *why* the cross-category alignment occurred (e.g., nocturnal timing, armed encounter, co-offender group size).

---

## 4. Ethical Boundaries & Responsible AI Principles

CRIME DNA strictly adheres to ethical intelligence standards:

1. **Behavioral Similarity Only**:
   The engine calculates mathematical proximity in feature space. It identifies overlapping patterns of conduct, operational timing, target selection, and force deployment.
2. **Strict Prohibition on Identity Claims**:
   The system **NEVER claims**:
   - Same offender
   - Same person
   - Same criminal group
   - Offender identity
   - Legal guilt or culpability
3. **Mandatory Advisory Notice**:
   Every response payload, API route, and user interface card includes the explicit disclaimer:
   > *"CRIME DNA detects behavioral similarity only. It does not establish offender identity, common perpetrator, criminal group association, or legal guilt."*

---

## 5. Verification & Automated Tests

Comprehensive integration tests in [`tests/test_cross_crime_matching.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/test_cross_crime_matching.py) validate all cross-crime capabilities:

1. `test_cross_category_retrieval_supported_by_data`:
   Proves an armed violent extortion incident successfully retrieves matches spanning Person, Property, and Person & Property (Robbery) categories simultaneously.
2. `test_similarity_engine_searches_global_index`:
   Confirms the underlying `NearestNeighbors` index queries all 220,663 records globally without statutory filters.
3. `test_crime_category_does_not_dominate_similarity`:
   Demonstrates two incidents with identical behavioral MO but differing category flags maintain $>70\%$ cosine similarity.
4. `test_similar_behavioral_incidents_grouping_structure`:
   Validates the presence of `Rank`, `Crime Category`, `Similarity`, and `Relevant behavioral characteristics`.
5. `test_cross_crime_indicator_wording`:
   Confirms exact wording: *"Similar behavioral characteristics were found across different crime categories."*
6. `test_same_and_different_category_grouping`:
   Verifies partitioning into `same_crime_category` and `different_crime_categories`.
7. `test_ethical_boundary_compliance`:
   Ensures no assertions of offender identity, common gang, or guilt are made.
8. `test_api_endpoint_returns_cross_crime_grouping`:
   Tests `POST /api/analyze/input` serialization over HTTP.
9. `test_api_vector_similarity_returns_cross_crime_enrichment`:
   Tests `POST /api/similarity/vector` nearest-neighbor enrichment.

All 9 tests pass with 100% verification rate alongside the 106 existing repository tests (total: 115 passing tests).
