"""
CRIME DNA — Phase 3: Behavioral DNA Configuration & Metadata

Defines the feature groups, transformation parameters, scaling boundaries,
and semantic descriptions for all 70 Behavioral DNA dimensions.
"""

from typing import Dict, List, Any

# Scaling parameters derived from empirical dataset audit
SCALING_PARAMS: Dict[str, float] = {
    "max_population": 237092.0,
    "max_property_value_log": 20.7233,
    "max_drug_quantity": 1088620.0,
    "median_victim_age": 38.0,
    "median_offender_age": 31.0,
    "cap_offense_count": 4.0,
    "cap_offense_categories": 3.0,
    "cap_location_count": 3.0,
    "cap_weapon_count": 3.0,
    "cap_weapon_types": 2.0,
    "cap_criminal_activities": 3.0,
    "cap_relationships": 3.0,
    "cap_victim_count": 5.0,
    "cap_victim_age_spread": 40.0,
    "cap_offender_count": 5.0,
    "cap_offender_age_spread": 30.0,
    "cap_property_records": 3.0,
    "cap_stolen_count": 10.0,
    "cap_injury_records": 3.0,
    "cap_drug_records": 3.0,
    "cap_arrest_count": 3.0,
}

# The 7 Behavioral Feature Groups
FEATURE_GROUPS: Dict[str, List[str]] = {
    "temporal_dynamics": [
        "time_hour_sin",
        "time_hour_cos",
        "time_month_sin",
        "time_month_cos",
        "time_weekday_sin",
        "time_weekday_cos",
        "time_is_weekend",
        "time_is_night",
    ],
    "crime_characteristics": [
        "crime_against_person",
        "crime_against_property",
        "crime_against_society",
        "crime_against_person_property",
        "crime_against_person_society",
        "crime_against_property_society",
        "crime_against_person_property_society",
        "offense_count_scaled",
        "offense_categories_count_scaled",
        "is_attempted",
    ],
    "location_and_environment": [
        "location_count_scaled",
        "population_log_scaled",
        "population_group_desc_cities_from_10,000_thru_24,999",
        "population_group_desc_cities_from_100,000_thru_249,999",
        "population_group_desc_cities_from_2,500_thru_9,999",
        "population_group_desc_cities_from_25,000_thru_49,999",
        "population_group_desc_cities_from_50,000_thru_99,999",
        "population_group_desc_cities_under_2,500",
        "population_group_desc_msa_counties_100,000_or_over",
        "population_group_desc_msa_counties_from_10,000_thru_24,999",
        "population_group_desc_msa_counties_from_25,000_thru_99,999",
        "population_group_desc_msa_counties_under_10,000",
        "population_group_desc_non_msa_state_police",
        "population_group_desc_non_msa_counties_from_10,000_thru_24,999",
        "population_group_desc_non_msa_counties_from_25,000_thru_99,999",
        "population_group_desc_non_msa_counties_under_10,000",
        "agency_is_state_police",
    ],
    "method_and_activity": [
        "has_weapon",
        "weapon_count_scaled",
        "weapon_types_count_scaled",
        "is_multi_weapon",
        "has_criminal_activity",
        "criminal_activity_count_scaled",
        "has_relationship",
        "relationship_count_scaled",
    ],
    "people_and_demographics": [
        "victim_count_scaled",
        "is_multi_victim",
        "victim_age_known",
        "victim_avg_age_scaled",
        "victim_age_spread_scaled",
        "victim_sexes_count_scaled",
        "victim_types_count_scaled",
        "offender_count_scaled",
        "is_co_offender",
        "offender_age_known",
        "offender_avg_age_scaled",
        "offender_age_spread_scaled",
        "offender_sexes_count_scaled",
    ],
    "property_and_economics": [
        "has_property",
        "property_record_count_scaled",
        "has_stolen_property",
        "stolen_count_scaled",
        "property_value_log_scaled",
        "is_cargo_theft",
    ],
    "context_and_harm": [
        "has_injury",
        "injury_record_count_scaled",
        "has_drug",
        "suspected_drug_count_scaled",
        "estimated_drug_quantity_log_scaled",
        "has_bias_motivation",
        "has_arrest_on_scene",
        "arrest_count_scaled",
    ],
}

# Plain-language descriptions for every feature for XAI and documentation
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    # Time
    "time_hour_sin": "Cyclical sine component of the hour of the incident, capturing diurnal rhythms.",
    "time_hour_cos": "Cyclical cosine component of the hour of the incident, capturing 24-hour periodicity.",
    "time_month_sin": "Cyclical sine component of the month of the incident, capturing annual seasonality.",
    "time_month_cos": "Cyclical cosine component of the month of the incident, capturing winter-to-summer transitions.",
    "time_weekday_sin": "Cyclical sine component of the day of the week.",
    "time_weekday_cos": "Cyclical cosine component of the day of the week.",
    "time_is_weekend": "Indicates whether the incident occurred during the weekend (Saturday or Sunday).",
    "time_is_night": "Indicates whether the incident occurred during nighttime hours (predominantly 20:00 to 06:00).",
    
    # Crime Characteristics
    "crime_against_person": "Offense targeted human victims directly (violent/personal crime).",
    "crime_against_property": "Offense targeted property, structures, or economic assets.",
    "crime_against_society": "Offense targeted public order, morality, or social regulation (drugs, weapons offenses).",
    "crime_against_person_property": "Dual violation involving concurrent crimes against persons and property.",
    "crime_against_person_society": "Dual violation involving personal harm and societal regulation breach.",
    "crime_against_property_society": "Dual violation involving property offenses and societal regulation breach.",
    "crime_against_person_property_society": "Complex triple-category violation affecting person, property, and society simultaneously.",
    "offense_count_scaled": "Relative volume of distinct statutory offenses committed in the single event.",
    "offense_categories_count_scaled": "Breadth of distinct crime categories involved in the event.",
    "is_attempted": "Indicates whether any offense in the incident was attempted rather than fully executed.",
    
    # Location & Environment
    "location_count_scaled": "Indicates whether the crime spanned multiple physical locations or scenes.",
    "population_log_scaled": "Logarithmically scaled population of the jurisdiction, representing urban density.",
    "population_group_desc_cities_from_10,000_thru_24,999": "Incident occurred in a small city (10k-25k population).",
    "population_group_desc_cities_from_100,000_thru_249,999": "Incident occurred in a major metropolitan city (100k-250k population).",
    "population_group_desc_cities_from_2,500_thru_9,999": "Incident occurred in a small town (2.5k-10k population).",
    "population_group_desc_cities_from_25,000_thru_49,999": "Incident occurred in a mid-sized town/suburb (25k-50k population).",
    "population_group_desc_cities_from_50,000_thru_99,999": "Incident occurred in a medium-large city (50k-100k population).",
    "population_group_desc_cities_under_2,500": "Incident occurred in a rural municipality under 2,500 population.",
    "population_group_desc_msa_counties_100,000_or_over": "Incident occurred in a large metropolitan county.",
    "population_group_desc_msa_counties_from_10,000_thru_24,999": "Incident occurred in a smaller metropolitan county.",
    "population_group_desc_msa_counties_from_25,000_thru_99,999": "Incident occurred in a medium-sized metropolitan county.",
    "population_group_desc_msa_counties_under_10,000": "Incident occurred in a sparsely populated metropolitan county.",
    "population_group_desc_non_msa_state_police": "Incident was reported by state police in non-metropolitan jurisdiction.",
    "population_group_desc_non_msa_counties_from_10,000_thru_24,999": "Incident occurred in a rural county (10k-25k population).",
    "population_group_desc_non_msa_counties_from_25,000_thru_99,999": "Incident occurred in a medium rural county (25k-100k population).",
    "population_group_desc_non_msa_counties_under_10,000": "Incident occurred in a remote rural county under 10,000 population.",
    "agency_is_state_police": "Incident fell under state police jurisdiction (e.g., highway/interstate corridor).",

    # Method & Activity
    "has_weapon": "Presence of a weapon during the commission of the incident.",
    "weapon_count_scaled": "Relative volume of weapons deployed or present during the offense.",
    "weapon_types_count_scaled": "Diversity of distinct weapon classes deployed (e.g., firearm + cutting instrument).",
    "is_multi_weapon": "Multiple distinct weapons were brought or deployed, signaling heightened tactical preparation.",
    "has_criminal_activity": "Evidence of organized or enterprise criminal operations (gangs, trafficking, narcotics trade).",
    "criminal_activity_count_scaled": "Volume of concurrent criminal activities identified.",
    "has_relationship": "Offender had an established prior relationship with the victim (domestic/acquaintance vs predatory stranger).",
    "relationship_count_scaled": "Complexity of interpersonal relationships recorded in the event.",

    # People & Demographics
    "victim_count_scaled": "Number of victims targeted in the incident (scaled).",
    "is_multi_victim": "Indicates an incident targeting multiple victims.",
    "victim_age_known": "Flag indicating that victim age is documented (distinguishes known ages from unknown).",
    "victim_avg_age_scaled": "Normalized average age of victims (0.0 to 1.0, representing ages up to 100).",
    "victim_age_spread_scaled": "Age range between youngest and oldest victims, identifying cross-generational targeting.",
    "victim_sexes_count_scaled": "Presence of both male and female victims.",
    "victim_types_count_scaled": "Diversity of victim types (e.g., individual citizens, businesses, financial institutions).",
    "offender_count_scaled": "Size of the offender crew (lone actor vs duo vs pack).",
    "is_co_offender": "Indicates multiple co-offenders acting in concert.",
    "offender_age_known": "Flag indicating that offender age is documented.",
    "offender_avg_age_scaled": "Normalized average age of perpetrators.",
    "offender_age_spread_scaled": "Age dispersion among co-offenders.",
    "offender_sexes_count_scaled": "Presence of mixed-gender co-offenders.",

    # Property & Economics
    "has_property": "Indicates property was targeted, stolen, or damaged.",
    "property_record_count_scaled": "Volume of distinct property records associated with the crime.",
    "has_stolen_property": "Indicates property was taken by the offender.",
    "stolen_count_scaled": "Number of distinct items stolen.",
    "property_value_log_scaled": "Normalized logarithmic financial loss or monetary value of property involved.",
    "is_cargo_theft": "Specialized targeting of commercial freight, cargo, or supply chain shipments.",

    # Context & Harm
    "has_injury": "Physical injury or bodily harm was inflicted on one or more victims.",
    "injury_record_count_scaled": "Volume of distinct injury records recorded.",
    "has_drug": "Suspected or verified narcotics/illicit substance presence.",
    "suspected_drug_count_scaled": "Number of suspected drug varieties identified.",
    "estimated_drug_quantity_log_scaled": "Normalized logarithmic magnitude of contraband quantity.",
    "has_bias_motivation": "Hate crime or bias-motivated targeting.",
    "has_arrest_on_scene": "Incident resolved with immediate on-scene arrest.",
    "arrest_count_scaled": "Number of arrestees taken into custody on-scene.",
}

# Concise, professional, human-readable labels for all 70 behavioral fingerprint dimensions
FEATURE_FRIENDLY_NAMES: Dict[str, str] = {
    # 1. Temporal Dynamics
    "time_hour_sin": "Diurnal Rhythm (Cycle Sine)",
    "time_hour_cos": "Diurnal Rhythm (Cycle Cos)",
    "time_month_sin": "Seasonal Timing (Annual Sine)",
    "time_month_cos": "Seasonal Timing (Annual Cos)",
    "time_weekday_sin": "Weekly Rhythm (Day Sine)",
    "time_weekday_cos": "Weekly Rhythm (Day Cos)",
    "time_is_weekend": "Weekend Execution",
    "time_is_night": "Nocturnal Execution (Night)",

    # 2. Crime Characteristics
    "crime_against_person": "Direct Violence Against Person",
    "crime_against_property": "Property / Economic Targeting",
    "crime_against_society": "Societal Regulation Breach",
    "crime_against_person_property": "Dual Person & Property Offense",
    "crime_against_person_society": "Dual Person & Societal Offense",
    "crime_against_property_society": "Dual Property & Societal Offense",
    "crime_against_person_property_society": "Multi-Domain Offense",
    "offense_count_scaled": "Offense Volume Index",
    "offense_categories_count_scaled": "Offense Category Breadth",
    "is_attempted": "Attempted Offense Status",

    # 3. Location & Environment
    "location_count_scaled": "Multi-Scene Geometry",
    "population_log_scaled": "Urban Population Density",
    "population_group_desc_cities_from_10,000_thru_24,999": "Small City (10k-25k pop.)",
    "population_group_desc_cities_from_100,000_thru_249,999": "Metropolitan Core (100k-250k)",
    "population_group_desc_cities_from_2,500_thru_9,999": "Town Setting (2.5k-10k pop.)",
    "population_group_desc_cities_from_25,000_thru_49,999": "Mid-Sized City (25k-50k pop.)",
    "population_group_desc_cities_from_50,000_thru_99,999": "Medium-Large City (50k-100k)",
    "population_group_desc_cities_under_2,500": "Rural Municipality (<2.5k pop.)",
    "population_group_desc_msa_counties_100,000_or_over": "Large Metro County (>100k)",
    "population_group_desc_msa_counties_from_10,000_thru_24,999": "Small Metro County (10k-25k)",
    "population_group_desc_msa_counties_from_25,000_thru_99,999": "Mid-Metro County (25k-100k)",
    "population_group_desc_msa_counties_under_10,000": "Rural Metro County (<10k)",
    "population_group_desc_non_msa_state_police": "State Police Corridor Setting",
    "population_group_desc_non_msa_counties_from_10,000_thru_24,999": "Rural County (10k-25k pop.)",
    "population_group_desc_non_msa_counties_from_25,000_thru_99,999": "Mid-Rural County (25k-100k)",
    "population_group_desc_non_msa_counties_under_10,000": "Remote Rural County (<10k)",
    "agency_is_state_police": "State Police Jurisdiction",

    # 4. Method & Activity
    "has_weapon": "Weapon Deployed",
    "weapon_count_scaled": "Weapon Deployment Volume",
    "weapon_types_count_scaled": "Weapon Diversity Index",
    "is_multi_weapon": "Multi-Weapon Arsenal",
    "has_criminal_activity": "Secondary Criminal Activity",
    "criminal_activity_count_scaled": "Enterprise Activity Volume",
    "has_relationship": "Prior Interpersonal Relationship",
    "relationship_count_scaled": "Relationship Complexity",

    # 5. People & Demographics
    "victim_count_scaled": "Victim Count Index",
    "is_multi_victim": "Multiple Victims Targeted",
    "victim_age_known": "Documented Victim Demographics",
    "victim_avg_age_scaled": "Victim Age Index",
    "victim_age_spread_scaled": "Cross-Generational Victim Spread",
    "victim_sexes_count_scaled": "Mixed-Gender Victim Group",
    "victim_types_count_scaled": "Diverse Victim Types",
    "offender_count_scaled": "Offender Crew Size",
    "is_co_offender": "Co-Offenders Acting in Concert",
    "offender_age_known": "Documented Offender Profile",
    "offender_avg_age_scaled": "Offender Age Index",
    "offender_age_spread_scaled": "Perpetrator Age Dispersion",
    "offender_sexes_count_scaled": "Mixed-Gender Co-Offenders",

    # 6. Property & Economics
    "has_property": "Property Targeted / Loss",
    "property_record_count_scaled": "Property Records Volume",
    "has_stolen_property": "Stolen Property Involved",
    "stolen_count_scaled": "Stolen Item Volume",
    "property_value_log_scaled": "Financial Valuation Index",
    "is_cargo_theft": "Commercial Cargo Theft",

    # 7. Context & Harm
    "has_injury": "Bodily Harm / Injury Inflicted",
    "injury_record_count_scaled": "Injury Severity Volume",
    "has_drug": "Contraband / Narcotics Presence",
    "suspected_drug_count_scaled": "Suspected Narcotics Varieties",
    "estimated_drug_quantity_log_scaled": "Narcotics Volume Index",
    "has_bias_motivation": "Hate / Bias Motivation",
    "has_arrest_on_scene": "Immediate Scene Arrest",
    "arrest_count_scaled": "On-Scene Arrest Volume",
}

# Domain mapping for all 70 features
FEATURE_BEHAVIORAL_DOMAINS: Dict[str, str] = {
    col: grp
    for grp, cols in FEATURE_GROUPS.items()
    for col in cols
}

# Human-facing labels for 7 behavioral domains
DOMAIN_LABELS: Dict[str, str] = {
    "temporal_dynamics": "Time Pattern",
    "crime_characteristics": "Crime Type",
    "location_and_environment": "Location",
    "method_and_activity": "Method / MO",
    "people_and_demographics": "People / Context",
    "property_and_economics": "Property",
    "context_and_harm": "Harm / Outcome",
}

# Modus operandi salience weights for breaking ties between normalized features with identical magnitude
FEATURE_SALIENCE_WEIGHTS: Dict[str, float] = {
    "has_weapon": 3.2,
    "has_injury": 3.2,
    "is_multi_weapon": 2.9,
    "crime_against_person_property": 2.9,
    "crime_against_person": 2.8,
    "crime_against_property": 2.7,
    "is_multi_victim": 2.8,
    "is_cargo_theft": 2.7,
    "has_criminal_activity": 2.6,
    "has_property": 2.5,
    "has_relationship": 2.5,
    "time_is_night": 2.5,
    "has_bias_motivation": 2.6,
    "has_drug": 2.4,
    "is_co_offender": 2.3,
    "has_arrest_on_scene": 2.2,
    "has_stolen_property": 2.2,
    "is_attempted": 2.0,
    "time_is_weekend": 1.9,
    "victim_age_known": 1.1,
    "offender_age_known": 1.1,
}

