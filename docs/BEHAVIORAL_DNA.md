# CRIME DNA — Phase 3: Behavioral DNA Specification & Feature Dictionary

**Document Version:** 1.0  
**Dataset:** `data/processed/crime_dna_behavioral_features.csv` (220,663 records × 71 columns)  
**Feature Names Registry:** `data/processed/behavioral_dna_feature_names.json`  
**Metadata Manifest:** `data/processed/behavioral_dna_metadata.json`  
**Pipeline Code:** `src/features/dna_encoder.py` | `src/features/config.py`  
**Test Suite:** `tests/test_behavioral_dna.py`  
**Author:** Lead Software Engineer & ML Engineer  

---

## 1. Executive Summary & Behavioral DNA Philosophy

Traditional criminal justice classification systems categorize offenses by statutory legal penal codes (e.g., "Theft", "Assault", "Trespassing"). However, two incidents filed under the exact same penal code often exhibit completely different tactical executions, while two crimes filed under different legal labels may share an identical operational modus operandi (MO).

**CRIME DNA** constructs a dense, normalized numerical vector—a **Behavioral Fingerprint**—for every crime incident. Rather than representing an individual's personal identity or biological DNA, the Behavioral DNA captures the **incident-level situational, tactical, and environmental signature** of how the crime was executed.

### Core Mathematical Properties:
- **Total Behavioral Dimensions**: **70 continuous numerical features** (plus primary key `incident_id`).
- **Strict Bounding**: Every single feature is strictly bounded within $[0.0, 1.0]$.
- **Zero Missingness**: 0 NaN values across all 220,663 incident vectors.
- **Metric Compatibility**: Compatible with **Cosine Similarity**, **Euclidean Distance**, **UMAP/t-SNE**, **Autoencoders**, and **Density-Based Clustering (HDBSCAN / K-Means)**.

---

## 2. Behavioral DNA Feature Group Breakdown

The 70 dimensions are organized into 7 distinct behavioral sub-profiles:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   INCIDENT BEHAVIORAL DNA (70 DIMENSIONS)              │
├──────────────────┬──────────────────┬──────────────────┬───────────────┤
│ 1. Time (8)      │ 2. Crime (10)    │ 3. Location (17) │ 4. Method (8) │
│  - Diurnal cycle │  - Target type   │  - Spatial scale │  - Weapons    │
│  - Seasonal cycle│  - Multi-offense │  - Urban density │  - Enterprise │
│  - Night/Weekend │  - Thwarted/Att. │  - State police  │  - Ties/Rel.  │
├──────────────────┴┬─────────────────┴┬─────────────────┴───────────────┤
│ 5. People (13)    │ 6. Property (6)  │ 7. Context & Harm (8)           │
│  - Victim scale   │  - Theft scale   │  - Physical injury              │
│  - Victimology    │  - Value log     │  - Narcotics profile            │
│  - Offender crew  │  - Cargo target  │  - Bias motivation & resolution │
└───────────────────┴──────────────────┴─────────────────────────────────┘
```

| Group # | Behavioral Group Name | Feature Count | Behavioral Focus |
| :--- | :--- | :--- | :--- |
| **Group 1** | **Temporal Dynamics** | `8` | 24-hour diurnal rhythms, annual seasonality, and nocturnal/weekend execution. |
| **Group 2** | **Crime Characteristics** | `10` | Fundamental target taxonomy (Person, Property, Society), complexity, and completion. |
| **Group 3** | **Location & Environment** | `17` | Multi-scene geography, jurisdictional population density, and municipal scale tiers. |
| **Group 4** | **Method & Activity** | `8` | Tactical armament, weapons diversity, organized criminal activity, and relational access. |
| **Group 5** | **People & Demographics** | `13` | Victim volume, age diversity, offender crew size (solo vs pack), and demographic spread. |
| **Group 6** | **Property & Economics** | `6` | Financial motivation, logarithmic property valuation, theft volume, and freight targeting. |
| **Group 7** | **Context & Harm** | `8` | Bodily violence inflicted, illicit substance presence, bias motivation, and on-scene arrest. |
| **Total** | **All Groups Combined** | **`70`** | Complete Behavioral Fingerprint |

---

## 3. Comprehensive Feature Dictionary (Plain-Language Explanation)

Every feature in the 70-dimensional Behavioral DNA vector is explained below:

### Group 1: Temporal Dynamics (8 Features)
1. **`time_hour_sin`**: The sine component of the 24-hour clock. Ensures 23:00 (11 PM) and 01:00 (1 AM) are recognized as 2 hours apart rather than 22 hours apart.
2. **`time_hour_cos`**: The cosine component of the 24-hour clock. Paired with `time_hour_sin` to form a circular clock representation.
3. **`time_month_sin`**: The sine component of the 12-month calendar, capturing annual cyclicality and seasonal shifts in criminal behavior.
4. **`time_month_cos`**: The cosine component of the calendar month, capturing summer-vs-winter crime patterns.
5. **`time_weekday_sin`**: Cyclical sine transformation of the day of the week (Monday through Sunday).
6. **`time_weekday_cos`**: Cyclical cosine transformation of the day of the week.
7. **`time_is_weekend`**: `1.0` if the crime occurred on Saturday or Sunday; `0.0` on weekdays. Differentiates weekend night nightlife crime from weekday workday crime.
8. **`time_is_night`**: `1.0` if the offense was committed during nighttime hours (predominantly 20:00 to 06:00); `0.0` during daylight. Captures stealth and nocturnal tactical choices.

### Group 2: Crime Characteristics (10 Features)
9. **`crime_against_person`**: `1.0` if human beings were the direct target (violent crime, assault, homicide, robbery).
10. **`crime_against_property`**: `1.0` if property was targeted (burglary, larceny, motor vehicle theft, vandalism).
11. **`crime_against_society`**: `1.0` if public order or regulatory laws were violated (narcotics, weapons possession, gambling).
12. **`crime_against_person_property`**: `1.0` for compound offenses violating both personal safety and property (e.g., armed home invasion robbery).
13. **`crime_against_person_society`**: `1.0` for dual violations involving personal violence and societal infractions.
14. **`crime_against_property_society`**: `1.0` for dual violations involving property destruction/theft and contraband.
15. **`crime_against_person_property_society`**: `1.0` for rare, complex triple-target crimes spanning all three domains simultaneously.
16. **`offense_count_scaled`**: Scaled volume of distinct statutory violations committed in the incident (ranges from single offense up to 4+ offenses). Measures multi-offense escalation.
17. **`offense_categories_count_scaled`**: Measures how many distinct crime categories were breached in a single spree or encounter.
18. **`is_attempted`**: `1.0` if the crime was thwarted, interrupted, or remained an attempt; `0.0` if completed. Differentiates successful execution from interrupted MOs.

### Group 3: Location & Environmental Context (17 Features)
19. **`location_count_scaled`**: `0.0` for single-scene incidents; higher values when the crime spanned multiple physical locations or transit scenes.
20. **`population_log_scaled`**: Logarithmically scaled population of the jurisdiction where the offense occurred. Differentiates major metropolitan density from rural quiet settings.
21–33. **`population_group_desc_*` (13 dummy features)**: Captures the municipal hierarchy:
    - `cities_100k_thru_249k`: Major urban city center.
    - `cities_50k_thru_99k`: Large suburban/mid-size municipality.
    - `cities_25k_thru_49k`: Mid-size town.
    - `cities_10k_thru_24k`: Small city.
    - `cities_2.5k_thru_9.9k`: Small town.
    - `cities_under_2500`: Rural hamlet.
    - `msa_counties_*`: Metropolitan fringe and county jurisdictions of varying population brackets.
    - `non_msa_counties_*`: Rural, non-metropolitan counties.
34. **`agency_is_state_police`**: `1.0` if investigated by state police. Identifies highway corridors, interstate transit, state facilities, or inter-jurisdictional incidents.

### Group 4: Method & Activity (8 Features)
35. **`has_weapon`**: `1.0` if any weapon was deployed or brandished during the offense; `0.0` if completely unarmed.
36. **`weapon_count_scaled`**: Relative number of weapons present during the crime (scaled up to 3+ weapons).
37. **`weapon_types_count_scaled`**: Diversity of weapon classes involved (e.g., firearm combined with edged weapon or blunt instrument).
38. **`is_multi_weapon`**: `1.0` if multiple weapons were deployed, reflecting tactical escalation and deliberate armed preparation.
39. **`has_criminal_activity`**: `1.0` if the incident was connected to broader ongoing criminal operations (e.g., gang activity, narcotics trafficking, fencing stolen goods).
40. **`criminal_activity_count_scaled`**: Complexity and count of concurrent criminal enterprises linked to the incident.
41. **`has_relationship`**: `1.0` if a prior relationship existed between offender and victim (domestic partner, family, friend, acquaintance); `0.0` for predatory stranger crimes.
42. **`relationship_count_scaled`**: Complexity of social and familial relationship ties involved in the encounter.

### Group 5: People & Demographics (13 Features)
43. **`victim_count_scaled`**: Number of victims targeted (scaled from 1 up to 5+ victims).
44. **`is_multi_victim`**: `1.0` if multiple victims were targeted in the same incident.
45. **`victim_age_known`**: `1.0` if victim age is documented; `0.0` if unknown/unidentified.
46. **`victim_avg_age_scaled`**: Normalized average age of the victims (scaled $0.0$ to $1.0$, where $0.38$ represents median 38 years old). Differentiates elderly/juvenile vulnerability targeting.
47. **`victim_age_spread_scaled`**: Age gap between youngest and oldest victims. Identifies multi-generational targeting (e.g., families).
48. **`victim_sexes_count_scaled`**: `1.0` if victims included both males and females; `0.0` if single sex.
49. **`victim_types_count_scaled`**: `1.0` if multiple victim classes were targeted simultaneously (e.g., individual citizen plus a commercial business).
50. **`offender_count_scaled`**: Group size of the offenders (lone actor vs pair vs group).
51. **`is_co_offender`**: `1.0` if two or more perpetrators acted in concert (accomplice, crew, gang dynamics).
52. **`offender_age_known`**: `1.0` if offender age is known; `0.0` if offender fled unidentified.
53. **`offender_avg_age_scaled`**: Normalized average age of the offenders (median imputed to $0.31$ for unknown cases, paired with `offender_age_known`).
54. **`offender_age_spread_scaled`**: Age variance among co-offenders (e.g., adult with juvenile accomplice vs peer group).
55. **`offender_sexes_count_scaled`**: `1.0` if the offending crew consisted of mixed genders.

### Group 6: Property & Economic Motivation (6 Features)
56. **`has_property`**: `1.0` if property was involved (stolen, damaged, counterfeited, or burned).
57. **`property_record_count_scaled`**: Number of distinct property items logged in the report.
58. **`has_stolen_property`**: `1.0` if property was actually stolen/appropriated by the perpetrator.
59. **`stolen_count_scaled`**: Volume of stolen property articles (scaled up to 10+ items).
60. **`property_value_log_scaled`**: Logarithmically scaled monetary value of property involved ($0.0$ for non-monetary up to $1.0$ for high-value financial hits).
61. **`is_cargo_theft`**: `1.0` for cargo theft targeting commercial freight, trucks, or intermodal supply chains.

### Group 7: Context & Harm (8 Features)
62. **`has_injury`**: `1.0` if physical bodily trauma was sustained by any victim during the incident.
63. **`injury_record_count_scaled`**: Severity and count of distinct injuries sustained.
64. **`has_drug`**: `1.0` if narcotics, controlled substances, or drug paraphernalia were involved.
65. **`suspected_drug_count_scaled`**: Variety of suspected drug types identified at the scene.
66. **`estimated_drug_quantity_log_scaled`**: Logarithmically scaled volume/weight of contraband seized.
67. **`has_bias_motivation`**: `1.0` if the crime was motivated by bias/hate against race, religion, sexual orientation, disability, or ethnicity.
68. **`has_arrest_on_scene`**: `1.0` if an arrest was made on scene at the time of reporting.
69. **`arrest_count_scaled`**: Scaled count of arrestees taken into custody on-scene.

---

## 4. Columns Excluded from Behavioral DNA & Technical Justifications

The cleaned dataset contains 196 columns, of which **126 columns were intentionally excluded** from the Behavioral DNA vector:

| Excluded Column Category | Column Count | Exact Columns Excluded | Detailed Technical Reason for Exclusion |
| :--- | :--- | :--- | :--- |
| **Administrative Identifiers** | `2` | `incident_id`, `agency_id` | Identifiers are non-behavioral labels. Including police agency ID would cluster crimes by police precinct rather than criminal modus operandi. `incident_id` is preserved as the dataset primary key. |
| **Local County One-Hot Dummies** | `93` | `county_name_autauga` through `county_name_winston` | Geography is not modus operandi. If 93 local county dummies were included in distance metrics, they would dominate the vector space and force crimes to cluster by jurisdiction rather than behavioral signature. Environmental scale is captured cleanly via `population_log_scaled` and `population_group_desc_*`. |
| **Metropolitan Area Dummies (MSA)** | `14` | `msa_name_birmingham` through `msa_name_tuscaloosa` | Excluded to maintain cross-jurisdictional behavioral discovery, preventing local MSA names from overwhelming behavioral MO. |
| **Redundant Binary Complements** | `2` | `cargo_theft_flag_f`, `county_name_not_specified` | `cargo_theft_flag_f` is identical to $1 - \text{cargo\_theft\_flag\_t}$, introducing exact multicollinearity. |
| **Non-Arrest Demographic Leakage** | `2` | `arrestee_avg_age`, `arrestee_age_known` | In Phase 2, we showed that arrestee age is only defined post-arrest. It does not reflect offender behavior at the crime scene. |
| **Redundant Agency Dummies** | `6` | `agency_type_name_city`, `county`, `university`, `tribal`, etc. | Agency type is predominantly redundant with municipality population group descriptors. `agency_is_state_police` is retained as a transit/highway indicator. |
| **Redundant Sub-Counts & Min/Max** | `7` | `incident_day`, `incident_quarter`, `relationships_count`, `criminal_activities_count`, `victim_races_count`, `victim_ethnicities_count`, `offender_races_count` | Redundant sub-counts that provide no additional variance beyond their primary count and diversity features. |

---

## 5. Demonstration: Real Incident Behavioral DNA Fingerprints

To illustrate how Behavioral DNA differentiates crime incidents across different crime classifications, here are 3 actual incident representations extracted from the dataset:

### Incident 1 (`INC_000001`): Commercial Property Damage (Daytime, Unarmed)
- **Time Profile**: Afternoon daytime (`time_is_night = 0.0`, `time_is_weekend = 0.0`, `time_hour_sin = 0.85`, `time_hour_cos = 0.15`).
- **Crime Target**: Property violation (`crime_against_property = 1.0`, `crime_against_person = 0.0`).
- **Armament & Method**: Completely unarmed (`has_weapon = 0.0`, `weapon_count_scaled = 0.0`), stranger victim (`has_relationship = 0.0`).
- **Victimology**: Single mature individual (`victim_avg_age_scaled = 0.55` [55 years old], `is_multi_victim = 0.0`).
- **Offender Dynamic**: Lone actor (`offender_count_scaled = 0.0`, `is_co_offender = 0.0`).
- **Property & Economic**: Property involved with moderate damage (`has_property = 1.0`, `property_value_log_scaled = 0.30`, `stolen_count_scaled = 0.0`).
- **Harm & Context**: Zero physical harm (`has_injury = 0.0`), zero narcotics (`has_drug = 0.0`).

### Incident 2 (`INC_000002`): Domestic Armed Violence (Weekend, Weapon Deployed)
- **Time Profile**: Weekend daytime (`time_is_weekend = 1.0`, `time_is_night = 0.0`).
- **Crime Target**: Purely against a person (`crime_against_person = 1.0`, `crime_against_property = 0.0`).
- **Armament & Method**: Armed encounter (`has_weapon = 1.0`, `weapon_count_scaled = 0.33`, `weapon_types_count_scaled = 0.50`), prior domestic/acquaintance relationship (`has_relationship = 1.0`).
- **Victimology**: Adult victim (`victim_avg_age_scaled = 0.47` [47 years old]).
- **Property & Economic**: Completely absent (`has_property = 0.0`, `property_value_log_scaled = 0.0`).
- **Harm & Context**: Bodily trauma inflicted (`has_injury = 1.0`, `injury_record_count_scaled = 0.33`).

### Incident 3 (`INC_000003`): Nighttime Enterprise Burglary (Nocturnal, Criminal Enterprise)
- **Time Profile**: Late night / nocturnal (`time_is_night = 1.0`).
- **Crime Target**: Property offense (`crime_against_property = 1.0`).
- **Armament & Method**: Unarmed stealth entry (`has_weapon = 0.0`), presence of organized criminal enterprise activity (`has_criminal_activity = 1.0`, `criminal_activity_count_scaled = 0.33`).
- **Property & Economic**: Commercial property targeted (`has_property = 1.0`, `property_value_log_scaled = 0.22`).
- **Harm & Context**: Non-violent (`has_injury = 0.0`), no immediate arrest on scene (`has_arrest_on_scene = 0.0`).

---

## 6. Pipeline Verification & Reproducibility

The feature engineering pipeline is fully automated and CLI-executable:

```bash
# Execute Behavioral DNA generation
python src/features/dna_encoder.py \
  --input-path data/processed/crime_dna_cleaned.csv \
  --output-path data/processed/crime_dna_behavioral_features.csv \
  --feature-names-path data/processed/behavioral_dna_feature_names.json \
  --metadata-path data/processed/behavioral_dna_metadata.json

# Execute full automated test suite
python -m unittest discover tests -v
```

All 12 tests across Phase 2 and Phase 3 pass in under 0.08 seconds:
```
test_cyclical_hour_proximity ... ok
test_feature_bounds_and_no_missing_values ... ok
test_feature_generation_dimension_and_names ... ok
test_feature_groups_integrity ... ok
test_output_artifacts_exist_and_consistent ... ok
test_cleaned_file_properties ... ok
test_raw_dataset_untouched ... ok
test_add_incident_identifier ... ok
test_categorize_columns ... ok
test_correct_encoding_artifacts ... ok
test_drop_uninformative_columns ... ok
test_handle_missing_and_sentinels ... ok
----------------------------------------------------------------------
Ran 12 tests in 0.071s
OK
```
