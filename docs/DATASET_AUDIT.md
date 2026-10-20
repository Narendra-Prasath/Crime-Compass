# CRIME DNA — Phase 1: Comprehensive Dataset & Behavioral Audit Report

**Document Version:** 1.0  
**Dataset:** `crime_dna_ml.csv`  
**Target System:** AI-Powered Crime Behavioral Pattern Analyzer (CRIME DNA)  
**Author:** Lead Software Engineer & ML Engineer  

---

## 1. Executive Summary & Core Dataset Metrics

| Metric | Value | Interpretation / Architectural Note |
| :--- | :--- | :--- |
| **Total Records (Rows)** | `220,663` | Substantial dataset providing rich sample density for behavioral clustering and pattern discovery. |
| **Total Features (Columns)** | `210` | High-dimensional feature space derived from FBI NIBRS incident records. |
| **Duplicate Rows** | `0` (0.00%) | Every row represents a distinct recorded incident. |
| **Missing / Null Values** | `0` (0.00% across all 210 cols) | The dataset has undergone prior imputation/preprocessing (null values replaced with 0s, default means, or categorical flags). |
| **Data Types** | `int64`: 191, `float64`: 19 | 100% numeric format. All text/categorical fields were pre-encoded into dummy indicator columns or counts. |
| **Zero-Variance (Constant) Columns** | `7` | Single constant value across all 220,663 rows; offer zero predictive/discriminative power. |
| **Exact Duplicate Column Pairs** | `17` | Collinear identical feature duplicates created during upstream pipeline featurization. |
| **Highly Skewed Columns (|skew| > 3.0)** | `151` | Features with extreme positive/negative skewness requiring log, robust scaling, or clipping. |

---

## 2. Critical Audit Findings & Data Integrity Anomalies

During deep inspection of `crime_dna_ml.csv`, several subtle upstream data transformation anomalies and leakage points were detected that directly impact ML modeling and behavioral fingerprinting:

### A. Zero-Variance (Constant) Columns
The following 7 columns have `nunique == 1` across all 220,663 records and should be excluded from all ML distance calculations and models:
1. `incident_year`: Always `2024` (100% of records are from calendar year 2024).
2. `cargo_theft_flag_nan`: Always `0`.
3. `county_name_nan`: Always `0`.
4. `msa_name_nan`: Always `0`.
5. `agency_type_name_nan`: Always `0`.
6. `population_group_desc_nan`: Always `0`.
7. `crime_against_nan`: Always `0`.

### B. Collinear Exact Duplicate Feature Pairs
Our hash-equality verification across all 220,663 rows identified 17 exact duplicate column relationships:
- `offense_count` == `offense_names_count` (Identical counts)
- `location_count` == `location_type_count` == `location_types_count` (Triplicate columns)
- `bias_count` == `bias_descriptions_count` (Identical counts)
- `has_injury` == `has_injury_record` (Identical boolean indicators)
- `has_arrest` == `has_arrest_record` (Identical boolean indicators)
- `has_property` == `has_property_record` (Identical boolean indicators)
- `has_drug` == `has_suspected_drug` (Identical boolean indicators)
- Geographic 1-to-1 mappings:
  - `county_name_baldwin` == `msa_name_daphne_fairhope_foley,_al`
  - `county_name_mobile` == `msa_name_mobile,_al`
  - `county_name_russell` == `msa_name_columbus,_ga_al`
  - `agency_type_name_state_police` == `population_group_desc_non_msa_state_police`
- Redundant constant nan flags (`cargo_theft_flag_nan` == `county_name_nan` == `msa_name_nan` == `agency_type_name_nan` == `population_group_desc_nan` == `crime_against_nan` == 0)

### C. Synthetic Default Imputations Requiring Masking
1. **Arrestee Age Default Imputation**: For all 170,254 incidents where `has_arrest == 0` (no arrest occurred), `arrestee_avg_age` is imputed to exactly `35.0`! In an unmasked distance metric (Euclidean/Cosine), crimes without an arrest will appear closer to crimes committed by 35-year-old arrestees than 20- or 50-year-olds. This is a severe artifact that must be addressed.
2. **Weapon Types Count on Unarmed Crimes**: When `has_weapon == 0` (153,606 incidents), `weapon_types_count` is set to `1` (representing 'None' or an unparsed category count) while `weapon_count` is `0.0`.
3. **Drug Types Count on Drug-Free Crimes**: When `has_drug == 0` (196,824 incidents), `drug_types_count` is set to `1` while `suspected_drug_count` and `estimated_drug_quantity` are `0.0`.
4. **Zero-Age for Unknown Victims and Offenders**: When `victim_age_known == 0` (2,332 cases) and `offender_age_known == 0` (23,973 cases), their average, min, and max ages are set to `0.0`. In numerical algorithms, age 0 represents a neonate/infant, not an unknown age. Separate missingness indicators and binning or median substitution must be handled carefully.

### D. Extreme Outliers and Sentinel Values
- `property_value`: Ranges from `$0.0` to `$999,999,999.0` (skew = `330.72`). The `$999,999,999` value is a classic NIBRS sentinel placeholder for unknown/unlimited value. There are 5 records with property values over $10M. Fortunately, `property_value_log` is already available in the dataset (max `20.72`), which stabilizes this feature.
- `estimated_drug_quantity`: Ranges from `0.0` to `1,088,620.0` (skew = `432.51`), with 138 records having quantities > 1,000. Requires log1p transform.

---

## 3. Behavioral DNA Feature Taxonomy & Categorization

To construct robust Behavioral DNA representations, features are categorized into 5 distinct architectural roles:

### Category 1: Recommended Core Behavioral DNA Candidates
These features define the **tactical, temporal, and situational modus operandi (MO)** of the crime incident:
- **Temporal Profile**: `incident_hour` (requires cyclical transformation), `incident_weekday`, `is_weekend`, `is_night`, `incident_month`, `incident_quarter`.
- **Crime Nature & Severity**: `crime_against_person`, `crime_against_property`, `crime_against_society`, `crime_against_person___property`, `crime_against_person___society`, `crime_against_property___society`, `crime_against_person___property___society`, `offense_count`, `attempted_count`.
- **Weapon Dynamics**: `has_weapon`, `weapon_count` (capped), `weapon_types_count` (masked).
- **Victimology & Harm**: `victim_count`, `victim_avg_age` (binned/masked), `victim_sexes_count`, `victim_races_count`, `victim_types_count`, `injury_record_count`, `has_injury`.
- **Offender Dynamics**: `offender_count` (identifies lone actor vs co-offenders vs pack/crew), `offender_avg_age` (binned/masked), `offender_sexes_count`, `offender_races_count`.
- **Victim-Offender Relationship**: `has_relationship`, `relationship_count`, `relationships_count` (distinguishes stranger violence from domestic/acquaintance crime).
- **Property & Economic Vector**: `has_property`, `property_record_count`, `stolen_count`, `property_value_log`, `cargo_theft_flag_t`.
- **Contraband & Narcotics Dynamics**: `has_drug`, `suspected_drug_count`, `drug_types_count` (masked), `estimated_drug_quantity` (log1p).
- **Criminal Activity & Bias Motivation**: `has_criminal_activity`, `criminal_activity_count`, `bias_count`.
- **Environmental Context**: `population_group_desc_*` (urban scale: dense city vs small town vs rural county).

### Category 2: Potentially Useful Features Requiring Preprocessing
- `incident_hour`: Must be transformed via `sin(2*pi*hour/24)` and `cos(2*pi*hour/24)` so 23:00 and 00:00 have distance 1.
- `incident_weekday`: Must be transformed cyclically or one-hot encoded.
- `property_value`: Extreme skewness (`skew=330.72`). Prefer `property_value_log` or robust quantile clipping.
- `estimated_drug_quantity`: Extreme skewness (`skew=432.51`). Requires `log1p` transformation.
- `victim_avg_age` & `offender_avg_age`: Need explicit handling for 0 (unknown) vs actual infants, using `victim_age_known` and `offender_age_known` flags.
- `county_name_*` (93 columns) & `msa_name_*` (15 columns): 108 geographic dummy columns would dominate distance metrics and force clusters by geography rather than behavioral MO. Must be kept separate from the behavioral vector or projected via PCA/SVD to low dimensions.

### Category 3: Identifiers (Non-Behavioral)
- `agency_id`: Administrative database identifier for the police agency (min=49, max=39648, 386 unique agencies). Not a behavioral property of the offender or incident.

### Category 4: Possible Data Leakage / Post-Incident Police Outcomes
- `has_arrest`, `arrest_count`, `arrestee_avg_age`, `arrestee_age_known`, `arrestee_sexes_count`: Arrest is a police outcome that occurs *after* the crime. If included in behavioral clustering, it groups crimes by law enforcement clearance rather than offender behavior. (These features are excellent for supervised arrest prediction, but must be segregated from pure behavioral DNA).
- `recovered_count`: Property recovery is an outcome of police investigation.

### Category 5: Unsuitable for ML / Redundant / Zero-Variance
- Constant zero-variance columns: `incident_year`, `cargo_theft_flag_nan`, `county_name_nan`, `msa_name_nan`, `agency_type_name_nan`, `population_group_desc_nan`, `crime_against_nan`.
- Redundant collinear copies: `offense_names_count`, `location_type_count`, `location_types_count`, `bias_descriptions_count`, `has_injury_record`, `has_arrest_record`, `has_property_record`, `has_suspected_drug`.

---

## 4. Complete Column Inventory (All 210 Columns)

The table below reports every single column present in `crime_dna_ml.csv` with data types, null statistics, cardinality, numerical ranges, summary statistics, and skewness.

| # | Column Name | Dtype | Missing (Count, %) | Unique | Min | Max | Mean | Skewness | Notes / Interpretation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `agency_id` | `int64` | 0 (0.0%) | 386 | 49.0 | 39648.0 | 623.68 | 8.77 | Standard Incident / Behavioral Feature |
| 2 | `incident_hour` | `int64` | 0 (0.0%) | 24 | 0.0 | 23.0 | 12.47 | -0.41 | Standard Incident / Behavioral Feature |
| 3 | `population` | `int64` | 0 (0.0%) | 349 | 0.0 | 237092.0 | 84300.01 | 0.74 | Standard Incident / Behavioral Feature |
| 4 | `offense_count` | `int64` | 0 (0.0%) | 6 | 1.0 | 6.0 | 1.15 | 2.76 | Standard Incident / Behavioral Feature |
| 5 | `attempted_count` | `int64` | 0 (0.0%) | 3 | 0.0 | 2.0 | 0.01 | 12.33 | ⚡ Highly Skewed Outlier Distribution |
| 6 | `location_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.01 | 9.10 | Standard Incident / Behavioral Feature |
| 7 | `location_type_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.01 | 9.10 | Standard Incident / Behavioral Feature |
| 8 | `weapon_count` | `float64` | 0 (0.0%) | 5 | 0.0 | 4.0 | 0.31 | 0.94 | Standard Incident / Behavioral Feature |
| 9 | `criminal_activity_count` | `float64` | 0 (0.0%) | 5 | 0.0 | 4.0 | 0.28 | 1.25 | Standard Incident / Behavioral Feature |
| 10 | `victim_count` | `int64` | 0 (0.0%) | 21 | 1.0 | 38.0 | 1.07 | 20.79 | ⚡ Highly Skewed Outlier Distribution |
| 11 | `victim_avg_age` | `float64` | 0 (0.0%) | 554 | 0.0 | 99.0 | 39.51 | 0.52 | Standard Incident / Behavioral Feature |
| 12 | `victim_min_age` | `float64` | 0 (0.0%) | 100 | 0.0 | 99.0 | 38.94 | 0.55 | Standard Incident / Behavioral Feature |
| 13 | `victim_max_age` | `float64` | 0 (0.0%) | 100 | 0.0 | 99.0 | 39.81 | 0.52 | Standard Incident / Behavioral Feature |
| 14 | `injury_record_count` | `float64` | 0 (0.0%) | 6 | 0.0 | 5.0 | 0.30 | 1.10 | Standard Incident / Behavioral Feature |
| 15 | `offender_count` | `int64` | 0 (0.0%) | 19 | 1.0 | 27.0 | 1.10 | 9.24 | Standard Incident / Behavioral Feature |
| 16 | `offender_avg_age` | `float64` | 0 (0.0%) | 538 | 0.0 | 99.0 | 30.53 | -0.03 | Standard Incident / Behavioral Feature |
| 17 | `offender_min_age` | `float64` | 0 (0.0%) | 99 | 0.0 | 99.0 | 30.15 | -0.02 | Standard Incident / Behavioral Feature |
| 18 | `offender_max_age` | `float64` | 0 (0.0%) | 99 | 0.0 | 99.0 | 31.14 | -0.06 | Standard Incident / Behavioral Feature |
| 19 | `relationship_count` | `float64` | 0 (0.0%) | 7 | 0.0 | 6.0 | 0.34 | 1.30 | Standard Incident / Behavioral Feature |
| 20 | `property_record_count` | `float64` | 0 (0.0%) | 5 | 0.0 | 4.0 | 0.77 | 0.29 | Standard Incident / Behavioral Feature |
| 21 | `stolen_count` | `float64` | 0 (0.0%) | 18 | 0.0 | 50.0 | 0.05 | 34.04 | ⚡ Highly Skewed Outlier Distribution |
| 22 | `recovered_count` | `float64` | 0 (0.0%) | 9 | 0.0 | 12.0 | 0.01 | 16.39 | ⚡ Highly Skewed Outlier Distribution |
| 23 | `property_value` | `float64` | 0 (0.0%) | 7505 | 0.0 | 999999999.0 | 11709.30 | 330.72 | ⚡ Highly Skewed Outlier Distribution |
| 24 | `suspected_drug_count` | `float64` | 0 (0.0%) | 4 | 0.0 | 3.0 | 0.13 | 3.56 | Standard Incident / Behavioral Feature |
| 25 | `estimated_drug_quantity` | `float64` | 0 (0.0%) | 2400 | 0.0 | 1088620.0 | 10.56 | 432.51 | ⚡ Highly Skewed Outlier Distribution |
| 26 | `arrest_count` | `float64` | 0 (0.0%) | 11 | 0.0 | 11.0 | 0.25 | 2.29 | Post-Incident Clearance / Outcome |
| 27 | `arrestee_avg_age` | `float64` | 0 (0.0%) | 291 | 0.0 | 99.0 | 35.19 | 1.38 | Post-Incident Clearance / Outcome |
| 28 | `bias_count` | `int64` | 0 (0.0%) | 2 | 1.0 | 2.0 | 1.00 | 35.37 | ⚡ Highly Skewed Outlier Distribution |
| 29 | `incident_month` | `int64` | 0 (0.0%) | 12 | 1.0 | 12.0 | 6.52 | -0.02 | Standard Incident / Behavioral Feature |
| 30 | `incident_day` | `int64` | 0 (0.0%) | 31 | 1.0 | 31.0 | 15.46 | 0.03 | Standard Incident / Behavioral Feature |
| 31 | `incident_weekday` | `int64` | 0 (0.0%) | 7 | 0.0 | 6.0 | 2.96 | 0.00 | Standard Incident / Behavioral Feature |
| 32 | `is_weekend` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.27 | 1.01 | Standard Incident / Behavioral Feature |
| 33 | `is_night` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.26 | 1.09 | Standard Incident / Behavioral Feature |
| 34 | `has_weapon` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.30 | 0.85 | Standard Incident / Behavioral Feature |
| 35 | `has_injury` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.29 | 0.91 | Standard Incident / Behavioral Feature |
| 36 | `has_arrest` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.23 | 1.29 | Post-Incident Clearance / Outcome |
| 37 | `has_property` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.68 | -0.77 | Standard Incident / Behavioral Feature |
| 38 | `has_drug` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.11 | 2.53 | Standard Incident / Behavioral Feature |
| 39 | `incident_year` | `int64` | 0 (0.0%) | 1 | 2024.0 | 2024.0 | 2024.00 | 0.00 | ⚠️ Constant / Zero Variance |
| 40 | `incident_quarter` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 2.51 | -0.01 | Standard Incident / Behavioral Feature |
| 41 | `has_criminal_activity` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.28 | 1.00 | Standard Incident / Behavioral Feature |
| 42 | `has_relationship` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.32 | 0.76 | Standard Incident / Behavioral Feature |
| 43 | `has_property_record` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.68 | -0.77 | Standard Incident / Behavioral Feature |
| 44 | `has_suspected_drug` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.11 | 2.53 | Standard Incident / Behavioral Feature |
| 45 | `has_arrest_record` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.23 | 1.29 | Post-Incident Clearance / Outcome |
| 46 | `has_injury_record` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.29 | 0.91 | Standard Incident / Behavioral Feature |
| 47 | `victim_age_known` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.99 | -9.57 | Standard Incident / Behavioral Feature |
| 48 | `offender_age_known` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.89 | -2.52 | Standard Incident / Behavioral Feature |
| 49 | `arrestee_age_known` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 1.00 | -102.49 | ⚡ Highly Skewed Outlier Distribution |
| 50 | `property_value_log` | `float64` | 0 (0.0%) | 7505 | 0.0 | 20.7 | 2.93 | 0.66 | Standard Incident / Behavioral Feature |
| 51 | `offense_names_count` | `int64` | 0 (0.0%) | 6 | 1.0 | 6.0 | 1.15 | 2.76 | Standard Incident / Behavioral Feature |
| 52 | `offense_categories_count` | `int64` | 0 (0.0%) | 5 | 1.0 | 5.0 | 1.09 | 3.55 | Standard Incident / Behavioral Feature |
| 53 | `crime_against_count` | `int64` | 0 (0.0%) | 3 | 1.0 | 3.0 | 1.03 | 5.24 | Crime Target Category (One-Hot) |
| 54 | `location_types_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.01 | 9.10 | Standard Incident / Behavioral Feature |
| 55 | `weapon_types_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.00 | 20.56 | ⚡ Highly Skewed Outlier Distribution |
| 56 | `criminal_activities_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.01 | 13.27 | ⚡ Highly Skewed Outlier Distribution |
| 57 | `victim_sexes_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.04 | 5.49 | Standard Incident / Behavioral Feature |
| 58 | `victim_races_count` | `int64` | 0 (0.0%) | 5 | 1.0 | 5.0 | 1.02 | 7.86 | Standard Incident / Behavioral Feature |
| 59 | `victim_ethnicities_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.02 | 7.75 | Standard Incident / Behavioral Feature |
| 60 | `victim_types_count` | `int64` | 0 (0.0%) | 4 | 1.0 | 4.0 | 1.02 | 8.14 | Standard Incident / Behavioral Feature |
| 61 | `offender_sexes_count` | `int64` | 0 (0.0%) | 3 | 1.0 | 3.0 | 1.04 | 5.01 | Standard Incident / Behavioral Feature |
| 62 | `offender_races_count` | `int64` | 0 (0.0%) | 3 | 1.0 | 3.0 | 1.01 | 8.91 | Standard Incident / Behavioral Feature |
| 63 | `offender_ethnicities_count` | `int64` | 0 (0.0%) | 3 | 1.0 | 3.0 | 1.01 | 8.72 | Standard Incident / Behavioral Feature |
| 64 | `relationships_count` | `int64` | 0 (0.0%) | 6 | 1.0 | 6.0 | 1.02 | 9.92 | Standard Incident / Behavioral Feature |
| 65 | `drug_types_count` | `int64` | 0 (0.0%) | 3 | 1.0 | 3.0 | 1.02 | 8.59 | Standard Incident / Behavioral Feature |
| 66 | `arrestee_sexes_count` | `int64` | 0 (0.0%) | 2 | 1.0 | 2.0 | 1.01 | 9.85 | Post-Incident Clearance / Outcome |
| 67 | `bias_categories_count` | `int64` | 0 (0.0%) | 2 | 1.0 | 2.0 | 1.00 | 90.39 | ⚡ Highly Skewed Outlier Distribution |
| 68 | `bias_descriptions_count` | `int64` | 0 (0.0%) | 2 | 1.0 | 2.0 | 1.00 | 35.37 | ⚡ Highly Skewed Outlier Distribution |
| 69 | `cargo_theft_flag_f` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 1.00 | -26.00 | ⚡ Highly Skewed Outlier Distribution |
| 70 | `cargo_theft_flag_t` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 26.00 | ⚡ Highly Skewed Outlier Distribution |
| 71 | `cargo_theft_flag_nan` | `int64` | 0 (0.0%) | 1 | 0.0 | 0.0 | 0.00 | 0.00 | ⚠️ Constant / Zero Variance |
| 72 | `county_name_autauga` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 14.17 | ⚡ Highly Skewed Outlier Distribution |
| 73 | `county_name_autauga,_elmore` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 7.53 | County Geographic Dummy (One-Hot) |
| 74 | `county_name_baldwin` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.09 | County Geographic Dummy (One-Hot) |
| 75 | `county_name_barbour` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 14.80 | ⚡ Highly Skewed Outlier Distribution |
| 76 | `county_name_bibb` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 17.83 | ⚡ Highly Skewed Outlier Distribution |
| 77 | `county_name_bibb,_tuscaloosa` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 28.54 | ⚡ Highly Skewed Outlier Distribution |
| 78 | `county_name_blount` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.99 | ⚡ Highly Skewed Outlier Distribution |
| 79 | `county_name_blount,_etowah` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 92.11 | ⚡ Highly Skewed Outlier Distribution |
| 80 | `county_name_bullock` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 29.84 | ⚡ Highly Skewed Outlier Distribution |
| 81 | `county_name_butler` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 17.41 | ⚡ Highly Skewed Outlier Distribution |
| 82 | `county_name_butler,_conecuh` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 469.75 | ⚡ Highly Skewed Outlier Distribution |
| 83 | `county_name_calhoun` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 6.21 | County Geographic Dummy (One-Hot) |
| 84 | `county_name_calhoun,_etowah` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 42.15 | ⚡ Highly Skewed Outlier Distribution |
| 85 | `county_name_calhoun,_talladega` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 13.73 | ⚡ Highly Skewed Outlier Distribution |
| 86 | `county_name_chambers` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.08 | ⚡ Highly Skewed Outlier Distribution |
| 87 | `county_name_cherokee` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.89 | ⚡ Highly Skewed Outlier Distribution |
| 88 | `county_name_cherokee,_dekalb` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 58.24 | ⚡ Highly Skewed Outlier Distribution |
| 89 | `county_name_chilton` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.74 | ⚡ Highly Skewed Outlier Distribution |
| 90 | `county_name_chilton,_shelby` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 18.42 | ⚡ Highly Skewed Outlier Distribution |
| 91 | `county_name_choctaw` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 29.78 | ⚡ Highly Skewed Outlier Distribution |
| 92 | `county_name_clarke` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 13.77 | ⚡ Highly Skewed Outlier Distribution |
| 93 | `county_name_clay` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 21.55 | ⚡ Highly Skewed Outlier Distribution |
| 94 | `county_name_cleburne` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 18.24 | ⚡ Highly Skewed Outlier Distribution |
| 95 | `county_name_coffee` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 15.20 | ⚡ Highly Skewed Outlier Distribution |
| 96 | `county_name_coffee,_dale` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.57 | ⚡ Highly Skewed Outlier Distribution |
| 97 | `county_name_colbert` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.24 | ⚡ Highly Skewed Outlier Distribution |
| 98 | `county_name_conecuh` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 53.51 | ⚡ Highly Skewed Outlier Distribution |
| 99 | `county_name_coosa` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 52.17 | ⚡ Highly Skewed Outlier Distribution |
| 100 | `county_name_covington` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.89 | ⚡ Highly Skewed Outlier Distribution |
| 101 | `county_name_crenshaw` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 31.70 | ⚡ Highly Skewed Outlier Distribution |
| 102 | `county_name_cullman` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 7.81 | County Geographic Dummy (One-Hot) |
| 103 | `county_name_cullman,_marshall` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 14.39 | ⚡ Highly Skewed Outlier Distribution |
| 104 | `county_name_dale` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.43 | ⚡ Highly Skewed Outlier Distribution |
| 105 | `county_name_dale,_houston` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.35 | County Geographic Dummy (One-Hot) |
| 106 | `county_name_dallas` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.15 | ⚡ Highly Skewed Outlier Distribution |
| 107 | `county_name_dekalb` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.41 | ⚡ Highly Skewed Outlier Distribution |
| 108 | `county_name_elmore` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 13.80 | ⚡ Highly Skewed Outlier Distribution |
| 109 | `county_name_elmore,_tallapoosa` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 18.37 | ⚡ Highly Skewed Outlier Distribution |
| 110 | `county_name_escambia` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.41 | ⚡ Highly Skewed Outlier Distribution |
| 111 | `county_name_etowah` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 6.83 | County Geographic Dummy (One-Hot) |
| 112 | `county_name_etowah,_marshall` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 61.13 | ⚡ Highly Skewed Outlier Distribution |
| 113 | `county_name_fayette` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 27.39 | ⚡ Highly Skewed Outlier Distribution |
| 114 | `county_name_fayette,_marion` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 30.99 | ⚡ Highly Skewed Outlier Distribution |
| 115 | `county_name_franklin` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 13.35 | ⚡ Highly Skewed Outlier Distribution |
| 116 | `county_name_geneva,_houston` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 271.21 | ⚡ Highly Skewed Outlier Distribution |
| 117 | `county_name_greene` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 27.11 | ⚡ Highly Skewed Outlier Distribution |
| 118 | `county_name_henry` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 16.99 | ⚡ Highly Skewed Outlier Distribution |
| 119 | `county_name_houston` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.02 | ⚡ Highly Skewed Outlier Distribution |
| 120 | `county_name_jackson` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 12.30 | ⚡ Highly Skewed Outlier Distribution |
| 121 | `county_name_jefferson` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.07 | 3.27 | County Geographic Dummy (One-Hot) |
| 122 | `county_name_jefferson,_shelby` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.09 | 2.77 | County Geographic Dummy (One-Hot) |
| 123 | `county_name_jefferson,_shelby,_st_clair` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 16.53 | ⚡ Highly Skewed Outlier Distribution |
| 124 | `county_name_jefferson,_st_clair` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 12.10 | ⚡ Highly Skewed Outlier Distribution |
| 125 | `county_name_jefferson,_tuscaloosa` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 95.87 | ⚡ Highly Skewed Outlier Distribution |
| 126 | `county_name_jefferson,_walker` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 66.41 | ⚡ Highly Skewed Outlier Distribution |
| 127 | `county_name_lamar` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 26.62 | ⚡ Highly Skewed Outlier Distribution |
| 128 | `county_name_lauderdale` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 7.42 | County Geographic Dummy (One-Hot) |
| 129 | `county_name_lawrence` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 21.67 | ⚡ Highly Skewed Outlier Distribution |
| 130 | `county_name_lawrence,_morgan` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 43.77 | ⚡ Highly Skewed Outlier Distribution |
| 131 | `county_name_lee` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.12 | County Geographic Dummy (One-Hot) |
| 132 | `county_name_lee,_macon` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 156.57 | ⚡ Highly Skewed Outlier Distribution |
| 133 | `county_name_lee,_russell` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 8.36 | County Geographic Dummy (One-Hot) |
| 134 | `county_name_limestone` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.55 | ⚡ Highly Skewed Outlier Distribution |
| 135 | `county_name_limestone,_madison` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.09 | 2.94 | County Geographic Dummy (One-Hot) |
| 136 | `county_name_limestone,_morgan` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 7.87 | County Geographic Dummy (One-Hot) |
| 137 | `county_name_lowndes` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 50.62 | ⚡ Highly Skewed Outlier Distribution |
| 138 | `county_name_macon` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 20.67 | ⚡ Highly Skewed Outlier Distribution |
| 139 | `county_name_madison` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 6.61 | County Geographic Dummy (One-Hot) |
| 140 | `county_name_marengo` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 17.83 | ⚡ Highly Skewed Outlier Distribution |
| 141 | `county_name_marion` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 16.64 | ⚡ Highly Skewed Outlier Distribution |
| 142 | `county_name_marion,_winston` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 24.77 | ⚡ Highly Skewed Outlier Distribution |
| 143 | `county_name_marshall` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 9.70 | County Geographic Dummy (One-Hot) |
| 144 | `county_name_mobile` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.08 | 2.99 | County Geographic Dummy (One-Hot) |
| 145 | `county_name_monroe` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 26.45 | ⚡ Highly Skewed Outlier Distribution |
| 146 | `county_name_montgomery` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.05 | 4.35 | County Geographic Dummy (One-Hot) |
| 147 | `county_name_morgan` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 11.14 | ⚡ Highly Skewed Outlier Distribution |
| 148 | `county_name_not_specified` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 18.22 | ⚡ Highly Skewed Outlier Distribution |
| 149 | `county_name_perry` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 110.71 | ⚡ Highly Skewed Outlier Distribution |
| 150 | `county_name_pickens` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 26.24 | ⚡ Highly Skewed Outlier Distribution |
| 151 | `county_name_pike` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 9.68 | County Geographic Dummy (One-Hot) |
| 152 | `county_name_randolph` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 13.26 | ⚡ Highly Skewed Outlier Distribution |
| 153 | `county_name_russell` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 18.04 | ⚡ Highly Skewed Outlier Distribution |
| 154 | `county_name_shelby` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 8.71 | County Geographic Dummy (One-Hot) |
| 155 | `county_name_st_clair` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 8.91 | County Geographic Dummy (One-Hot) |
| 156 | `county_name_sumter` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 35.07 | ⚡ Highly Skewed Outlier Distribution |
| 157 | `county_name_talladega` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 6.87 | County Geographic Dummy (One-Hot) |
| 158 | `county_name_tallapoosa` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.54 | ⚡ Highly Skewed Outlier Distribution |
| 159 | `county_name_tuscaloosa` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.05 | 4.05 | County Geographic Dummy (One-Hot) |
| 160 | `county_name_walker` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.94 | ⚡ Highly Skewed Outlier Distribution |
| 161 | `county_name_washington` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 22.10 | ⚡ Highly Skewed Outlier Distribution |
| 162 | `county_name_wilcox` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 28.75 | ⚡ Highly Skewed Outlier Distribution |
| 163 | `county_name_winston` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 21.42 | ⚡ Highly Skewed Outlier Distribution |
| 164 | `county_name_nan` | `int64` | 0 (0.0%) | 1 | 0.0 | 0.0 | 0.00 | 0.00 | ⚠️ Constant / Zero Variance |
| 165 | `msa_name_anniston_oxford,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.52 | MSA Geographic Dummy (One-Hot) |
| 166 | `msa_name_auburn_opelika,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.05 | 4.11 | MSA Geographic Dummy (One-Hot) |
| 167 | `msa_name_birmingham,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.24 | 1.25 | MSA Geographic Dummy (One-Hot) |
| 168 | `msa_name_columbus,_ga_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 18.04 | ⚡ Highly Skewed Outlier Distribution |
| 169 | `msa_name_daphne_fairhope_foley,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.09 | MSA Geographic Dummy (One-Hot) |
| 170 | `msa_name_decatur,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 9.60 | MSA Geographic Dummy (One-Hot) |
| 171 | `msa_name_dothan,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 9.17 | MSA Geographic Dummy (One-Hot) |
| 172 | `msa_name_florence_muscle_shoals,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.90 | MSA Geographic Dummy (One-Hot) |
| 173 | `msa_name_gadsden,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 6.78 | MSA Geographic Dummy (One-Hot) |
| 174 | `msa_name_huntsville,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.13 | 2.19 | MSA Geographic Dummy (One-Hot) |
| 175 | `msa_name_mobile,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.08 | 2.99 | MSA Geographic Dummy (One-Hot) |
| 176 | `msa_name_montgomery,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.08 | 3.20 | MSA Geographic Dummy (One-Hot) |
| 177 | `msa_name_not_specified` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.23 | 1.27 | MSA Geographic Dummy (One-Hot) |
| 178 | `msa_name_tuscaloosa,_al` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.05 | 3.93 | MSA Geographic Dummy (One-Hot) |
| 179 | `msa_name_nan` | `int64` | 0 (0.0%) | 1 | 0.0 | 0.0 | 0.00 | 0.00 | ⚠️ Constant / Zero Variance |
| 180 | `agency_type_name_city` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.78 | -1.37 | Agency Type (One-Hot) |
| 181 | `agency_type_name_county` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.20 | 1.51 | Agency Type (One-Hot) |
| 182 | `agency_type_name_other` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 14.85 | ⚡ Highly Skewed Outlier Distribution |
| 183 | `agency_type_name_other_state_agency` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 16.47 | ⚡ Highly Skewed Outlier Distribution |
| 184 | `agency_type_name_state_police` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 50.62 | ⚡ Highly Skewed Outlier Distribution |
| 185 | `agency_type_name_tribal` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 35.27 | ⚡ Highly Skewed Outlier Distribution |
| 186 | `agency_type_name_university_or_college` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.16 | ⚡ Highly Skewed Outlier Distribution |
| 187 | `agency_type_name_nan` | `int64` | 0 (0.0%) | 1 | 0.0 | 0.0 | 0.00 | 0.00 | ⚠️ Constant / Zero Variance |
| 188 | `population_group_desc_cities_from_10,000_thru_24,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.16 | 1.87 | Population Scale (One-Hot) |
| 189 | `population_group_desc_cities_from_100,000_thru_249,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.28 | 0.98 | Population Scale (One-Hot) |
| 190 | `population_group_desc_cities_from_2,500_thru_9,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.11 | 2.51 | Population Scale (One-Hot) |
| 191 | `population_group_desc_cities_from_25,000_thru_49,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.11 | 2.43 | Population Scale (One-Hot) |
| 192 | `population_group_desc_cities_from_50,000_thru_99,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.08 | 3.05 | Population Scale (One-Hot) |
| 193 | `population_group_desc_cities_under_2,500` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.05 | 4.01 | Population Scale (One-Hot) |
| 194 | `population_group_desc_msa_counties_100,000_or_over` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.07 | 3.39 | Population Scale (One-Hot) |
| 195 | `population_group_desc_msa_counties_from_10,000_thru_24,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 10.92 | ⚡ Highly Skewed Outlier Distribution |
| 196 | `population_group_desc_msa_counties_from_25,000_thru_99,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.07 | 3.52 | Population Scale (One-Hot) |
| 197 | `population_group_desc_msa_counties_under_10,000` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 12.67 | ⚡ Highly Skewed Outlier Distribution |
| 198 | `population_group_desc_non_msa_state_police` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 50.62 | ⚡ Highly Skewed Outlier Distribution |
| 199 | `population_group_desc_non_msa_counties_from_10,000_thru_24,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 5.71 | Population Scale (One-Hot) |
| 200 | `population_group_desc_non_msa_counties_from_25,000_thru_99,999` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.02 | 6.68 | Population Scale (One-Hot) |
| 201 | `population_group_desc_non_msa_counties_under_10,000` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 14.69 | ⚡ Highly Skewed Outlier Distribution |
| 202 | `population_group_desc_nan` | `int64` | 0 (0.0%) | 1 | 0.0 | 0.0 | 0.00 | 0.00 | ⚠️ Constant / Zero Variance |
| 203 | `crime_against_person` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.31 | 0.82 | Crime Target Category (One-Hot) |
| 204 | `crime_against_person___property` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.03 | 6.08 | Crime Target Category (One-Hot) |
| 205 | `crime_against_person___property___society` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 53.16 | ⚡ Highly Skewed Outlier Distribution |
| 206 | `crime_against_person___society` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.00 | 17.53 | ⚡ Highly Skewed Outlier Distribution |
| 207 | `crime_against_property` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.51 | -0.03 | Crime Target Category (One-Hot) |
| 208 | `crime_against_property___society` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.01 | 12.90 | ⚡ Highly Skewed Outlier Distribution |
| 209 | `crime_against_society` | `int64` | 0 (0.0%) | 2 | 0.0 | 1.0 | 0.15 | 2.00 | Crime Target Category (One-Hot) |
| 210 | `crime_against_nan` | `int64` | 0 (0.0%) | 1 | 0.0 | 0.0 | 0.00 | 0.00 | ⚠️ Constant / Zero Variance |

---

## 5. Architectural Blueprint for Behavioral DNA Representation

Based on the audited schema, the **Behavioral DNA Fingerprint** for each crime incident should be structured as a normalized vector across 7 functional sub-profiles:

```
┌────────────────────────────────────────────────────────────────────────┐
│                         CRIME BEHAVIORAL DNA                           │
├──────────────────┬──────────────────┬──────────────────┬───────────────┤
│ 1. Temporal MO   │ 2. Target Choice │ 3. Lethality &   │ 4. Offender   │
│    - Sin/Cos Hr  │    - Person      │    Violence      │    Structure  │
│    - Is Night    │    - Property    │    - Weapon cnt  │    - Solo/Crew│
│    - Weekend     │    - Society     │    - Injury flag │    - Age band │
├──────────────────┼──────────────────┼──────────────────┼───────────────┤
│ 5. Victimology   │ 6. Economic &    │ 7. Deviance &    │ 8. Urban      │
│    - Victim cnt  │    Property MO   │    Substance     │    Context    │
│    - Rel. flag   │    - Value log   │    - Drug cnt    │    - Pop size │
│    - Victim type │    - Stolen cnt  │    - Activity cnt│    - Pop group│
└──────────────────┴──────────────────┴──────────────────┴───────────────┘
```

---

## 6. Recommendations for Phase 2 Execution

1. **Data Cleaning & Deduplication Module** (`src/data/cleaner.py`):
   - Drop the 7 constant zero-variance columns.
   - Remove redundant duplicate columns (`offense_names_count`, duplicate location counts, etc.).
   - Rectify the `arrestee_avg_age=35.0` artifact and mask invalid weapon/drug type counts when flags are 0.
2. **Feature Engineering Pipeline** (`src/features/dna_encoder.py`):
   - Implement cyclical encoding for `incident_hour` (`hour_sin`, `hour_cos`) and `incident_month`.
   - Robustly scale log-transformed property values and drug quantities.
   - Construct sub-vector embeddings for behavioral dimensions.
3. **Exploratory Data Analysis Notebook** (`notebooks/01_exploratory_data_analysis.ipynb`):
   - Visualize behavioral feature correlations, temporal patterns, and geographic distributions.
4. **Baseline Behavioral DNA Embedding Generation**:
   - Produce normalized DNA vectors ready for cosine similarity and clustering algorithms.

*Phase 1 Complete. Ready for Phase 2 upon user instruction.*