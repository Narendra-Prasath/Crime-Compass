# CRIME DNA — User Input Schema & Behavioral Feature Mapping Manifesto

This document provides the definitive architectural specification for the **CRIME DNA Incident Input System**. It details how human-interpretable incident parameters entered through the interface or API are strictly mapped into the 70-dimensional unit $L_2$-normalized Behavioral DNA vector space without modifying historical data or altering established preprocessing distributions.

---

## 1. Core Principles

1. **Zero Data Distortion:** The underlying historical repository (`crime_dna_ml.csv` with 220,663 records) remains the unmutated reference corpus. User-submitted incidents never alter pre-computed cluster centroids, novelty thresholds, or nearest-neighbor indices.
2. **Strict Dimensional Alignment:** Every single input field translates exclusively into one or more of the 70 engineered features present in `data/processed/behavioral_dna_feature_names.json`. No artificial or unmapped fields exist.
3. **Information Abstraction:** The user is never exposed to raw one-hot column names (e.g. `population_group_desc_cities_from_10,000_thru_24,999`) or empirical min-max bounds. Instead, clear intuitive dropdowns, standard ISO date/time selectors, and plain-English descriptors are presented.
4. **Unit $L_2$ Normalization:** All 70 features are transformed to $[0.0, 1.0]$, assembled into an ordered float32 vector $\mathbf{x}_{\text{raw}} \in \mathbb{R}^{70}$, and projected to the unit hypersphere:
   $$\mathbf{x}_{\text{norm}} = \frac{\mathbf{x}_{\text{raw}}}{\|\mathbf{x}_{\text{raw}}\|_2}$$

---

## 2. Comprehensive Field-by-Field Mapping Matrix

The user-facing system exposes **18 clean operational fields** organized into 6 logical domain cards. The matrix below defines each field and its direct 1-to-1 mapping into the 70D feature pipeline:

| # | User-Facing Field | Input Type / Control | Options / Format | Default | 70D Behavioral DNA Feature(s) | Transformation Applied |
|---|---|---|---|---|---|---|
| **1** | **Scenario Title** | Text input | Free text | `"Simulated Incident"` | *Metadata only* | Carried into report and comparisons |
| **2** | **Target Domain** | Dropdown | `property`, `person`, `society`, `person_property`, `person_society`, `property_society`, `person_property_society` | `property` | • `crime_against_person`<br>• `crime_against_property`<br>• `crime_against_society`<br>• `crime_against_person_property`<br>• `crime_against_person_society`<br>• `crime_against_property_society`<br>• `crime_against_person_property_society` | Binary indicators matching target statutory domain |
| **3** | **Execution State** | Dropdown | `completed`, `attempted` | `completed` | • `is_attempted` | `1.0` if attempted, else `0.0` |
| **4** | **Offense Count** | Number input | $1 \le n \le 20$ | `1` | • `offense_count_scaled` | $\min(n - 1, 4) / 4.0$ (Capped at 5 offenses) |
| **5** | **Incident Date** | Date picker | ISO `YYYY-MM-DD` | Current Date | • `time_month_sin`<br>• `time_month_cos`<br>• `time_weekday_sin`<br>• `time_weekday_cos`<br>• `time_is_weekend` | • $\frac{\sin(2\pi(m-1)/12) + 1}{2}$<br>• $\frac{\cos(2\pi(m-1)/12) + 1}{2}$<br>• $\frac{\sin(2\pi w/7) + 1}{2}$<br>• $\frac{\cos(2\pi w/7) + 1}{2}$<br>• `1.0` if Sat/Sun |
| **6** | **Incident Time** | Time picker | ISO `HH:MM` | `21:30` | • `time_hour_sin`<br>• `time_hour_cos`<br>• `time_is_night` | • $\frac{\sin(2\pi h/24) + 1}{2}$<br>• $\frac{\cos(2\pi h/24) + 1}{2}$<br>• `1.0` if $h \ge 20$ or $h < 6$ |
| **7** | **Jurisdiction Profile** | Dropdown | `metropolitan_core`, `large_city`, `mid_sized_city`, `small_city`, `small_town`, `rural_community`, `state_police` | `mid_sized_city` | • `population_log_scaled`<br>• 14 Population Group one-hot flags<br>• `agency_is_state_police` | Activates exact FBI UCR population stratum one-hot flag and scales population logarithmically: $\frac{\ln(1 + \text{pop})}{\ln(1 + 10^7)}$ |
| **8** | **Premises / Scenes** | Number input | $1 \le n \le 10$ | `1` | • `location_count_scaled` | $\min(n - 1, 4) / 4.0$ (Capped at 5 locations) |
| **9** | **Weapon Deployed** | Toggle switch | True / False | False | • `has_weapon` | `1.0` if true, `0.0` if false |
| **10** | **Weapons Count** | Number input | $0 \le n \le 10$ | `0` | • `weapon_count_scaled`<br>• `weapon_types_count_scaled`<br>• `is_multi_weapon` | • $\min(n, 4) / 4.0$<br>• `1.0` if $n > 1$ |
| **11** | **Syndicate Activity** | Toggle switch | True / False | False | • `has_criminal_activity`<br>• `criminal_activity_count_scaled` | `1.0` if true |
| **12** | **Interpersonal Relation** | Toggle switch | True / False | False | • `has_relationship`<br>• `relationship_count_scaled` | `1.0` if true (prior relationship between victim & offender) |
| **13** | **Victim Count** | Number input | $0 \le n \le 50$ | `1` | • `victim_count_scaled`<br>• `is_multi_victim`<br>• `victim_types_count_scaled` | • $\min(n, 5) / 5.0$<br>• `1.0` if $n > 1$ |
| **14** | **Avg Victim Age** | Number input | $0 \le \text{age} \le 120$ | `35` | • `victim_age_known`<br>• `victim_avg_age_scaled` | • `1.0` if provided<br>• $\min(\text{age}, 100) / 100.0$ |
| **15** | **Offender Count** | Number input | $0 \le n \le 50$ | `1` | • `offender_count_scaled`<br>• `is_co_offender` | • $\min(n, 5) / 5.0$<br>• `1.0` if $n > 1$ |
| **16** | **Avg Offender Age** | Number input | $0 \le \text{age} \le 120$ | `25` | • `offender_age_known`<br>• `offender_avg_age_scaled` | • `1.0` if provided<br>• $\min(\text{age}, 100) / 100.0$ |
| **17** | **Property Involved** | Toggle switch | True / False | True | • `has_property`<br>• `has_stolen_property`<br>• `property_record_count_scaled` | `1.0` if true |
| **18** | **Property Value (USD)** | Currency input | $\$0 \le v$ | $\$2,500$ | • `property_value_log_scaled` | $\min(1.0, \frac{\ln(1 + v)}{\ln(1 + 100,000)})$ (99th percentile cap) |
| **19** | **Physical Injury** | Toggle switch | True / False | False | • `has_injury`<br>• `injury_record_count_scaled` | `1.0` if true |
| **20** | **Narcotics Involved** | Toggle switch | True / False | False | • `has_drug`<br>• `suspected_drug_count_scaled` | `1.0` if true |
| **21** | **On-Scene Arrest** | Toggle switch | True / False | False | • `has_arrest_on_scene`<br>• `arrest_count_scaled` | `1.0` if true |
| **22** | **Hate / Bias Motivation**| Toggle switch | True / False | False | • `has_bias_motivation` | `1.0` if true |

---

## 3. Subprofile Energy Aggregations

After assembling and normalizing the 70D vector, the system computes the $L_2$ energy share for each of the 7 Behavioral DNA subprofiles:

$$\text{Energy}_g = 100.0 \times \left( \frac{1}{|g|} \sum_{i \in g} x_{\text{norm}, i}^2 \right)^{1/2}$$

1. **Temporal Dynamics** (8 features)
2. **Crime Characteristics** (10 features)
3. **Location & Setting** (17 features)
4. **Method & Weaponry** (8 features)
5. **People & Demographics** (13 features)
6. **Property & Economics** (6 features)
7. **Context, Harm & Resolution** (8 features)

---

## 4. Architectural Verification

- **Pydantic Validation:** `IncidentInputRequest` in `src/api/schemas.py` validates all ranges, types, and required fields.
- **Unit Testing:** `tests/test_input_bridge.py` verifies vector dimension (`70`), unit magnitude ($\|\mathbf{x}\|_2 = 1.0$), cyclical bounds, and setting mappings.
- **Integration Testing:** `tests/api/test_input_analysis.py` asserts complete end-to-end evaluation across all 8 intelligence views with sub-50ms execution times.
