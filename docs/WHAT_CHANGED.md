# CRIME DNA — "WHAT CHANGED?" Explanation Layer

## 1. Overview & Objective

The **"WHAT CHANGED?"** explanation layer translates complex 70-dimensional mathematical vector comparisons into plain, intuitive, non-technical explanations. 

When a user compares **Incident A** vs **Incident B**, a single score such as **74.4% DNA Similarity** is insufficient for investigative action. Non-technical users—including detectives, supervisors, intelligence analysts, and legal practitioners—need to understand immediately:
1. *What operational behaviors matched between the two incidents?*
2. *What tactical decisions differed or escalated?*
3. *Are the incidents statutory peers or cross-category matches?*
4. *What factors most strongly supported the similarity score?*
5. *What factors most meaningfully accounted for the score divergence?*

---

## 2. The 5 Core Pillars

```
┌────────────────────────────────────────────────────────────────────────┐
│                   "WHAT CHANGED?" EXPLANATION ENGINE                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
1. MATCHING CHARACTERISTICS   2. DIFFERENT CHARACTERISTICS   3. CRIME CATEGORY
   ✓ Night                       △ Crime category               Same vs Different
   ✓ Residential                 △ Weapon context               Statutory Context
   ✓ Property
   ✓ No injury
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
        4. STRONGEST SIMILARITIES       5. MEANINGFUL DIFFERENCES
           (Why DNA Score Matched)         (Why DNA Score Diverged)
```

### Pillar 1: Matching Behavioral Characteristics
Dynamic identification of operational dimensions where both incidents shared execution characteristics. Represented as clean, readable labels with the `✓` symbol.

### Pillar 2: Different Behavioral Characteristics
Dynamic identification of dimensions where operational divergence, tactical change, or escalations took place. Represented with the `△` symbol.

### Pillar 3: Same Crime Category vs Different Crime Category
Explicit classification of whether the comparison evaluates:
- **Same Crime Category**: Modus operandi comparison within statutory peers (e.g., Residential Theft vs Commercial Theft).
- **Different Crime Category**: Cross-category behavioral link (e.g., Residential Theft vs Night Residential Burglary, or Robbery vs Assault). Explains that the Behavioral DNA engine measures shared operational habits independent of legal statutory labels.

### Pillar 4: Strongest Similarities
Ranked plain-English explanations identifying the primary drivers that positively contributed to the similarity score.

### Pillar 5: Most Meaningful Differences
Ranked plain-English explanations identifying the primary operational deviations, escalations, or de-escalations that reduced the similarity score.

---

## 3. Non-Technical Presentation Layout

The user interface presents this layer in an accessible format:

```text
4 behavioral characteristics match.
2 behavioral characteristics differ.

MATCH:
✓ Night
✓ Residential
✓ Property
✓ No injury

DIFFER:
△ Crime category
△ Weapon context
```

### Contextual Detail Panels

#### Crime Category Context
> **Different Crime Category:** Incident A is classified as *Property / Theft* whereas Incident B is classified as *Burglary / Breaking & Entering*. Behavioral DNA establishes operational similarity across categories.

#### Strongest Similarities (Why the DNA Score Matched)
- • **Consistent diurnal timing:** Both offenses occurred during night hours.
- • **Identical setting:** Both incidents targeted residential environments.
- • **Target property motive:** Both incidents sought tangible property acquisition.
- • **Zero physical harm:** No victim injuries occurred in either offense.

#### Most Meaningful Differences (Why the DNA Score Diverged)
- • **Weapon escalation:** Incident A was unarmed while Incident B introduced a firearm (handgun).
- • **Statutory crime category shifted:** Theft vs Burglary.

---

## 4. Dimensional Evaluation & Dynamic Generation

Every explanation is generated dynamically from the actual attributes and 70D DNA vectors of Incident A and Incident B. **Results are never hardcoded.**

| Dimension | Match Condition | MATCH Display (`✓`) | DIFFER Display (`△`) | Impact on Score |
|---|---|---|---|---|
| **Time** | Same diurnal cycle (`Night` vs `Night` or `Daytime` vs `Daytime`) | `Night` / `Daytime` | `Timing / diurnal pattern` | Affects Temporal subprofile |
| **Location** | Same environmental setting (e.g., Residential, Commercial) | `Residential` / `Commercial` / etc. | `Location context` | Affects Spatial subprofile |
| **Property** | Same property involvement state (`Yes`/`Yes` or `No`/`No`) | `Property` / `No property` | `Property involvement` | Affects MO / Target subprofile |
| **Weapon** | Same weapon state (unarmed vs armed) | `No weapon` / `Weapon present` | `Weapon context` | Major impact on Weapon subprofile |
| **Injury** | Same victim injury state (`No`/`No` or `Injured`/`Injured`) | `No injury` / `Physical injury` | `Injury / physical harm` | Major impact on Harm subprofile |
| **Crime Category** | Same primary statutory classification | `Crime category (<name>)` | `Crime category` | Cross-crime contextual indicator |
| **Victim Count** | Identical victim headcount | `Victim headcount (<N>)` | `Victim headcount` | Target vulnerability subprofile |

---

## 5. Tactical Escalation Detection

In addition to static differences, the layer flags **directional escalations**:

1. **Weapon Escalation (`None` $\rightarrow$ `Armed`)**:
   - Flagged when Incident B introduces a weapon not present in Incident A.
   - Identified in `escalations` list and prominently highlighted in the UI.
2. **Harm Escalation (`No Injury` $\rightarrow$ `Physical Injury Inflicted`)**:
   - Flagged when Incident B involves victim injuries while Incident A was non-injurious.
3. **Weapon De-escalation (`Armed` $\rightarrow$ `Unarmed`)**:
   - Flagged when Incident B shows a reduction in lethal force compared to Incident A.

---

## 6. API Data Contract (`WhatChangedDetail`)

The backend returns the complete explanation layer under the `what_changed` key of [`DnaComparisonResponse`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/src/api/schemas.py):

```json
{
  "what_changed": {
    "headline": "Behavioral Transition in Weapon, Crime: 5 dimensions matched, 2 diverged.",
    "match_count": 5,
    "differ_count": 2,
    "total_dimensions_compared": 7,
    "summary_match_line": "5 behavioral characteristics match.",
    "summary_differ_line": "2 behavioral characteristics differ.",
    "summary_text": "5 behavioral characteristics match.\n\n2 behavioral characteristics differ.",
    "match_items": [
      "Night",
      "Residential",
      "Property",
      "No injury",
      "Victim headcount (1)"
    ],
    "differ_items": [
      "Weapon context",
      "Crime category"
    ],
    "same_crime_category": false,
    "crime_category_status": "Different Crime Category",
    "crime_category_detail": "Different crime categories: Incident A is Property / Theft while Incident B is Burglary. The DNA engine evaluates behavioral MO alignment despite different legal labels.",
    "strongest_similarities": [
      "Consistent timing: both offenses occurred during night hours.",
      "Identical setting: both incidents targeted residential environments.",
      "Target property motive: both incidents sought tangible property acquisition.",
      "Zero physical harm: no victim injuries occurred in either offense.",
      "Equal victim headcount (1)."
    ],
    "most_meaningful_differences": [
      "Weapon escalation: Incident A was unarmed while Incident B introduced handgun.",
      "Statutory crime category shifted from Property / Theft to Burglary."
    ],
    "escalations": [
      "Weapon Escalation: Transitioned from unarmed to armed encounter."
    ],
    "transitions": [
      "Weapon deployment changed from None to Handgun",
      "Statutory category shifted from Property / Theft to Burglary"
    ],
    "narrative": "Weapon Escalation: Transitioned from unarmed to armed encounter. Key operational shifts observed: Weapon deployment changed from None to Handgun; Statutory category shifted from Property / Theft to Burglary. Underlying behavioral continuity remains rooted in consistent diurnal timing (night execution)."
  }
}
```

---

## 7. Frontend User Experience

In [`DnaComparisonPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/DnaComparisonPage.tsx), the "WHAT CHANGED?" section is rendered with clear visual hierarchy:

1. **Top Badge Bar**:
   - Green pill: `"5 behavioral characteristics match."`
   - Amber pill: `"2 behavioral characteristics differ."`
   - Purple/Blue pill: `"[Different Crime Category]"` or `"[Same Crime Category]"`
2. **MATCH vs DIFFER Side-by-Side Cards**:
   - **MATCH card**: Green header with checkmarks (`✓ Night`, `✓ Residential`, `✓ Property`, `✓ No injury`).
   - **DIFFER card**: Amber header with delta symbols (`△ Weapon context`, `△ Crime category`).
3. **Crime Category Context Box**:
   - Plain-English explanation explaining why categories differ and how the Behavioral DNA connects them.
4. **Why DNA Matched vs Why DNA Diverged Panels**:
   - Bulleted list of strongest similarities.
   - Bulleted list of most meaningful differences.
5. **Tactical Escalation Alert**:
   - Red callout box if weapons or injuries escalated.

---

## 8. Ethical Attribution Principles

> [!IMPORTANT]
> **EXPLANATION OF MODUS OPERANDI, NOT OFFENDER IDENTITY**
> 
> The "WHAT CHANGED?" explanation layer describes similarities and shifts in **incident circumstances and behavior**.
> - It does **NOT** claim or imply that the same individual committed both crimes.
> - Behavioral evolution across incidents (e.g. unarmed theft $\rightarrow$ armed burglary) may reflect unrelated individuals adopting common opportunistic patterns in a geographic area.
> - Conclusive offender linkage requires physical forensic evidence (DNA, fingerprints, ballistic matching, or digital tracking).
