# CRIME DNA — Phase 2: Data Cleaning & Preprocessing Specification

**Document Version:** 1.0  
**Input Dataset:** `crime_dna_ml.csv` (Unaltered, SHA-preserved raw master)  
**Output Dataset:** `data/processed/crime_dna_cleaned.csv`  
**Pipeline Script:** `src/data/cleaner.py`  
**Cleaning Metadata:** `data/processed/cleaning_metadata.json`  
**Test Suite:** `tests/test_data_cleaning.py`  
**Author:** Lead Software Engineer & ML Engineer  

---

## 1. Executive Summary & Processing Scope

Phase 2 transitions the raw FBI NIBRS-derived dataset (`crime_dna_ml.csv`) into a sanitized, production-ready feature matrix for Behavioral DNA profiling. In strict accordance with project rules:
- **Zero raw rows were deleted**: All 220,663 incident rows are preserved.
- **Original file untouched**: `crime_dna_ml.csv` remains strictly read-only.
- **No synthetic information invented**: No missing values were filled with arbitrary random or global constant values.
- **Upstream artifacts reversed**: Artificial imputations (such as default age 35 on crimes with no arrest, or type count 1 on unarmed crimes) were systematically corrected.
- **Identifiers separated**: A deterministic primary key `incident_id` was established, and administrative identifiers were isolated from behavioral MO features.

| Metric | Raw Dataset (`crime_dna_ml.csv`) | Cleaned Dataset (`data/processed/crime_dna_cleaned.csv`) | Net Change |
| :--- | :--- | :--- | :--- |
| **Row Count** | `220,663` | `220,663` | `0` (100% rows preserved) |
| **Column Count** | `210` | `196` | `-14` (+1 ID, -7 constant, -8 collinear copies) |
| **Primary Key** | None (`agency_id` was only admin ID) | `incident_id` (`INC_000001` to `INC_220663`) | Unique incident tracking enabled |
| **Zero-Variance Columns** | `7` | `0` | All uninformative constants eliminated |
| **Redundant Collinear Duplicates** | `8` | `0` | Exact duplicate feature pairs removed |
| **Non-Arrest Age Distortion** | `170,254` rows had `arrestee_avg_age = 35.0` | `NaN` (masked for downstream handling) | False age artifact eliminated |
| **Unarmed Count Distortion** | `153,606` unarmed rows had `weapon_types_count = 1` | `0` (consistent with `has_weapon = 0`) | Weapon MO logic restored |
| **Drug-Free Count Distortion** | `196,824` drug-free rows had `drug_types_count = 1` | `0` (consistent with `has_drug = 0`) | Substance MO logic restored |
| **File Size on Disk** | `102.1 MB` | `96.4 MB` | Streamlined storage footprint |

---

## 2. Inventory of Transformations: What Was Changed and Why

### A. Primary Key Generation (`incident_id`)
- **What was changed**: Added an explicit primary key column `incident_id` formatted as `INC_000001` through `INC_220663` as the first column.
- **Why it was changed**: The raw dataset contained no unique row identifier (only `agency_id`, which represents police precincts). Behavioral DNA similarity matching, cluster assignment, and web dashboard retrieval require referencing specific incidents.

### B. Removal of 7 Constant (Zero-Variance) Columns
- **What was changed**: Dropped 7 columns that contained identical values across all 220,663 records.
- **Why it was changed**: Zero-variance features carry zero mathematical information or predictive power, add noise to distance computations, and induce singular matrices in dimensional reduction algorithms.

### C. Removal of 8 Exact Collinear Duplicate Columns
- **What was changed**: Dropped 8 columns whose values exactly matched other existing columns across all 220,663 rows.
- **Why it was changed**: Collinear copies artificially inflate feature weights in Euclidean/Cosine distance metrics and create redundant dimensionality without providing novel behavioral signal.

### D. Correction of Upstream Encoding Artifacts
- **What was changed**:
  1. `weapon_types_count`: Corrected from `1` to `0` for 153,606 unarmed crimes (`has_weapon == 0`).
  2. `drug_types_count`: Corrected from `1` to `0` for 196,824 drug-free crimes (`has_drug == 0`).
  3. `arrestee_avg_age`: Corrected from `35.0` to `NaN` for 170,254 crimes where no arrest occurred (`has_arrest == 0`).
- **Why it was changed**: An upstream ETL pipeline erroneously counted category 'None' as a type, and filled missing arrestee ages with a default value of 35.0 even when no arrest took place. In similarity search, these artifacts would group unarmed crimes as having a weapon type, and non-arrest crimes as having a 35-year-old perpetrator.

### E. Explicit Missingness Handling for Demographics & Sentinel Values
- **What was changed**:
  1. Set `victim_avg_age`, `victim_min_age`, and `victim_max_age` to `NaN` for 2,332 records where `victim_age_known == 0`.
  2. Set `offender_avg_age`, `offender_min_age`, and `offender_max_age` to `NaN` for 23,973 records where `offender_age_known == 0`.
  3. Set `property_value` to `NaN` for 1 record containing the NIBRS sentinel value `999999999.0`.
- **Why it was changed**: The raw data recorded unknown ages as `0.0`. In numerical algorithms, `0.0` represents an infant or newborn, which severely distorts criminal profiling. By converting unknown values to `NaN` while preserving the indicator flags (`victim_age_known`, `offender_age_known`), Phase 3 feature engineering can treat them as an explicit "Unknown Demographics" category or apply median imputation conditioned on crime type.

---

## 3. Principled Strategies

### Missing-Value Strategy
1. **No row deletions**: Removing rows with missing demographic or outcome attributes would discard valuable incident records and introduce sampling bias. All 220,663 rows are retained.
2. **No blind zero-filling**: Blindly filling unknown ages with 0 equates unknown offenders with infants.
3. **Explicit missingness preservation**: Where values are genuinely unknown, they are set to `NaN` and paired with existing boolean indicator columns (`victim_age_known`, `offender_age_known`, `has_arrest`, `arrestee_age_known`). This allows Phase 3 encoders to apply domain-aware imputations or discrete age binning (`Unknown`, `Juvenile`, `Young Adult`, `Adult`, `Senior`).

### Duplicate Strategy
- **Row duplicates**: The raw dataset contains `0` full-row duplicate records. All 220,663 records represent distinct reported incidents.
- **Column duplicates**: 8 feature columns were verified via byte-hash comparison to be 100% duplicate copies of other columns and were eliminated.

### Data Leakage Strategy
- Features representing **post-incident police investigation outcomes** (`has_arrest`, `arrest_count`, `arrestee_avg_age`, `arrestee_age_known`, `arrestee_sexes_count`, `recovered_count`) were isolated and tagged.
- **Rule for Phase 3**: These outcome features must **not** be incorporated into the Behavioral DNA fingerprint representation. Behavioral DNA must capture how the criminal acted at the scene, not whether the police successfully apprehended them or recovered stolen goods later.

---

## 4. Itemized Columns Removed (15 Columns)

| # | Column Name | Raw Unique Values | Exact Reason for Removal |
| :--- | :--- | :--- | :--- |
| 1 | `incident_year` | 1 (`2024`) | Zero variance. Constant calendar year across 100% of records. |
| 2 | `cargo_theft_flag_nan` | 1 (`0`) | Zero variance. Dummy variable for NaN cargo theft flag with no positive instances. |
| 3 | `county_name_nan` | 1 (`0`) | Zero variance. Dummy variable for NaN county name with no positive instances. |
| 4 | `msa_name_nan` | 1 (`0`) | Zero variance. Dummy variable for NaN MSA with no positive instances. |
| 5 | `agency_type_name_nan` | 1 (`0`) | Zero variance. Dummy variable for NaN agency type with no positive instances. |
| 6 | `population_group_desc_nan` | 1 (`0`) | Zero variance. Dummy variable for NaN population group with no positive instances. |
| 7 | `crime_against_nan` | 1 (`0`) | Zero variance. Dummy variable for NaN crime category with no positive instances. |
| 8 | `offense_names_count` | 6 | Redundant collinear copy of `offense_count` (100% identical). |
| 9 | `location_type_count` | 4 | Redundant collinear copy of `location_count` (100% identical). |
| 10 | `location_types_count` | 4 | Redundant collinear copy of `location_count` (100% identical). |
| 11 | `bias_descriptions_count` | 2 | Redundant collinear copy of `bias_count` (100% identical). |
| 12 | `has_injury_record` | 2 | Redundant collinear copy of `has_injury` (100% identical). |
| 13 | `has_arrest_record` | 2 | Redundant collinear copy of `has_arrest` (100% identical). |
| 14 | `has_property_record` | 2 | Redundant collinear copy of `has_property` (100% identical). |
| 15 | `has_suspected_drug` | 2 | Redundant collinear copy of `has_drug` (100% identical). |

---

## 5. Architectural Breakdown of Retained Columns (196 Columns)

All 196 retained columns are categorized in `data/processed/cleaning_metadata.json`:

```
CRIME DNA Cleaned Feature Space (196 Columns)
├── 1. Identifiers & Metadata (2 columns)
│   ├── incident_id (Primary Key)
│   └── agency_id (Reporting Police Agency ID)
├── 2. Temporal Dynamics (7 columns)
│   ├── incident_hour, incident_month, incident_day, incident_weekday
│   └── is_weekend, is_night, incident_quarter
├── 3. Offense & Behavioral MO (15 columns)
│   ├── offense_count, attempted_count, location_count
│   ├── criminal_activity_count, has_criminal_activity, criminal_activities_count
│   ├── bias_count, bias_categories_count
│   ├── offense_categories_count, crime_against_count
│   ├── cargo_theft_flag_f, cargo_theft_flag_t
│   └── crime_against_person, crime_against_person___society, crime_against_society
├── 4. Victimology & Demographics (11 columns)
│   ├── victim_count, has_injury, injury_record_count, victim_age_known
│   ├── victim_avg_age, victim_min_age, victim_max_age
│   └── victim_sexes_count, victim_races_count, victim_ethnicities_count, victim_types_count
├── 5. Offender Crew & Relationship Dynamics (11 columns)
│   ├── offender_count, offender_age_known, has_relationship
│   ├── offender_avg_age, offender_min_age, offender_max_age
│   ├── offender_sexes_count, offender_races_count, offender_ethnicities_count
│   └── relationship_count, relationships_count
├── 6. Weapon & Lethality Profile (3 columns)
│   ├── weapon_count, has_weapon, weapon_types_count
├── 7. Property, Contraband & Economic Vector (13 columns)
│   ├── property_record_count, stolen_count, property_value, property_value_log
│   ├── has_property, has_drug, suspected_drug_count, estimated_drug_quantity, drug_types_count
│   └── crime_against_person___property, crime_against_person___property___society,
│       crime_against_property, crime_against_property___society
├── 8. Environmental & Geographic Context (128 columns)
│   ├── population
│   ├── county_name_* (93 one-hot columns)
│   ├── msa_name_* (14 one-hot columns)
│   ├── agency_type_name_* (7 one-hot columns)
│   └── population_group_desc_* (13 one-hot columns)
└── 9. Post-Incident Outcomes / Data Leakage (6 columns)
    ├── has_arrest, arrest_count, arrestee_avg_age
    ├── arrestee_age_known, arrestee_sexes_count, recovered_count
```

---

## 6. Pipeline Execution & Reproducibility

The preprocessing pipeline is fully automated and CLI-executable:

```bash
# Execute preprocessing from project root
python src/data/cleaner.py \
  --input-path crime_dna_ml.csv \
  --output-path data/processed/crime_dna_cleaned.csv \
  --metadata-path data/processed/cleaning_metadata.json

# Execute automated test suite
python -m unittest tests/test_data_cleaning.py -v
```

All 7 test cases pass unconditionally:
```
test_cleaned_file_properties ... ok
test_raw_dataset_untouched ... ok
test_add_incident_identifier ... ok
test_categorize_columns ... ok
test_correct_encoding_artifacts ... ok
test_drop_uninformative_columns ... ok
test_handle_missing_and_sentinels ... ok
----------------------------------------------------------------------
Ran 7 tests in 0.034s
OK
```
