import csv
import os

sample_rows = [
    # Repeated Pattern A: Evening commercial cash snatching / robbery (person_property, weapon=1, edged_weapon, evening 20:00-22:30, offenders=2, INR 25,000-80,000)
    {"incident_id": "FIR_2024_001", "incident_date": "2024-01-10", "incident_time": "21:15", "country": "India", "state_ut": "Karnataka", "district": "Bengaluru Urban", "city_town": "Bengaluru", "locality": "Indiranagar 100ft Rd", "pin_code": "560038", "location_type": "commercial_store", "crime_category": "person_property", "offense_description": "Cash counter hold-up at retail pharmacy", "method_activity": "counter_intimidation", "has_weapon": "1", "weapon_type": "edged_weapon", "has_property": "1", "property_value": "45000", "currency": "INR", "victim_count": "2", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_002", "incident_date": "2024-01-14", "incident_time": "21:45", "country": "India", "state_ut": "Karnataka", "district": "Bengaluru Urban", "city_town": "Bengaluru", "locality": "Koramangala 5th Block", "pin_code": "560095", "location_type": "commercial_store", "crime_category": "person_property", "offense_description": "Robbery of daily earnings at grocery mart", "method_activity": "counter_intimidation", "has_weapon": "1", "weapon_type": "edged_weapon", "has_property": "1", "property_value": "52000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_003", "incident_date": "2024-01-22", "incident_time": "22:10", "country": "India", "state_ut": "Karnataka", "district": "Bengaluru Urban", "city_town": "Bengaluru", "locality": "HSR Layout Sector 2", "pin_code": "560102", "location_type": "commercial_store", "crime_category": "person_property", "offense_description": "Quick cash register heist at closing time", "method_activity": "counter_intimidation", "has_weapon": "1", "weapon_type": "edged_weapon", "has_property": "1", "property_value": "38000", "currency": "INR", "victim_count": "2", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_004", "incident_date": "2024-02-05", "incident_time": "21:30", "country": "India", "state_ut": "Karnataka", "district": "Mysuru", "city_town": "Mysuru", "locality": "Devaraja Market", "pin_code": "570001", "location_type": "commercial_store", "crime_category": "person_property", "offense_description": "Closing hour robbery at wholesale cloth shop", "method_activity": "counter_intimidation", "has_weapon": "1", "weapon_type": "edged_weapon", "has_property": "1", "property_value": "65000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_005", "incident_date": "2024-02-18", "incident_time": "22:00", "country": "India", "state_ut": "Karnataka", "district": "Mysuru", "city_town": "Mysuru", "locality": "Jayalakshmipuram", "pin_code": "570012", "location_type": "commercial_store", "crime_category": "person_property", "offense_description": "Robbery at mobile repair outlet", "method_activity": "counter_intimidation", "has_weapon": "1", "weapon_type": "edged_weapon", "has_property": "1", "property_value": "42000", "currency": "INR", "victim_count": "2", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},

    # Repeated Pattern B: Late night warehouse / commercial shutter burglary (property, weapon=0, midnight 01:00-04:00, forced shutter entry, property INR 1,50,000-6,00,000)
    {"incident_id": "FIR_2024_006", "incident_date": "2024-01-18", "incident_time": "02:30", "country": "India", "state_ut": "Maharashtra", "district": "Mumbai Suburban", "city_town": "Mumbai", "locality": "Andheri East MIDC", "pin_code": "400093", "location_type": "industrial", "crime_category": "property", "offense_description": "Shutter lock snapped and inventory stolen from auto parts godown", "method_activity": "forced_entry", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "320000", "currency": "INR", "victim_count": "1", "offender_count": "3", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_007", "incident_date": "2024-01-26", "incident_time": "03:15", "country": "India", "state_ut": "Maharashtra", "district": "Mumbai Suburban", "city_town": "Mumbai", "locality": "Kandivali West Charkop", "pin_code": "400067", "location_type": "industrial", "crime_category": "property", "offense_description": "Commercial electronics godown break-in", "method_activity": "forced_entry", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "480000", "currency": "INR", "victim_count": "1", "offender_count": "3", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_008", "incident_date": "2024-02-12", "incident_time": "02:45", "country": "India", "state_ut": "Maharashtra", "district": "Pune", "city_town": "Pune", "locality": "Bhosari Industrial Area", "pin_code": "411026", "location_type": "industrial", "crime_category": "property", "offense_description": "Night-time copper wire and raw metal theft from warehouse", "method_activity": "forced_entry", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "550000", "currency": "INR", "victim_count": "1", "offender_count": "4", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_009", "incident_date": "2024-02-28", "incident_time": "03:30", "country": "India", "state_ut": "Maharashtra", "district": "Pune", "city_town": "Pune", "locality": "Hadapsar Industrial Estate", "pin_code": "411013", "location_type": "industrial", "crime_category": "property", "offense_description": "Tooling equipment stolen via broken rear ventilation grill", "method_activity": "forced_entry", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "260000", "currency": "INR", "victim_count": "1", "offender_count": "3", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_010", "incident_date": "2024-03-08", "incident_time": "01:50", "country": "India", "state_ut": "Maharashtra", "district": "Thane", "city_town": "Thane", "locality": "Wagle Estate", "pin_code": "400604", "location_type": "industrial", "crime_category": "property", "offense_description": "Night warehouse burglary targeting packaged consumer goods", "method_activity": "forced_entry", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "390000", "currency": "INR", "victim_count": "1", "offender_count": "3", "has_injury": "0", "has_arrest": "0"},

    # Repeated Pattern C: Morning two-wheeler mobile/chain snatching on open street (person_property, weapon=0/blunt, morning 06:30-08:30, offenders=2, victims=1, INR 15,000-50,000)
    {"incident_id": "FIR_2024_011", "incident_date": "2024-02-02", "incident_time": "06:45", "country": "India", "state_ut": "Delhi", "district": "New Delhi", "city_town": "New Delhi", "locality": "Lodhi Colony", "pin_code": "110003", "location_type": "street_open", "crime_category": "person_property", "offense_description": "Gold chain snatching by bike-borne individuals during morning walk", "method_activity": "bike_snatch", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "65000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_012", "incident_date": "2024-02-11", "incident_time": "07:15", "country": "India", "state_ut": "Delhi", "district": "South Delhi", "city_town": "New Delhi", "locality": "Hauz Khas Enclave", "pin_code": "110016", "location_type": "street_open", "crime_category": "person_property", "offense_description": "Handbag and mobile phone snatched from pedestrian", "method_activity": "bike_snatch", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "35000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_013", "incident_date": "2024-02-19", "incident_time": "06:55", "country": "India", "state_ut": "Delhi", "district": "South Delhi", "city_town": "New Delhi", "locality": "Greater Kailash 1", "pin_code": "110048", "location_type": "street_open", "crime_category": "person_property", "offense_description": "Chain snatching incident outside neighbourhood park", "method_activity": "bike_snatch", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "78000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_014", "incident_date": "2024-03-04", "incident_time": "07:30", "country": "India", "state_ut": "Delhi", "district": "Central Delhi", "city_town": "New Delhi", "locality": "Karol Bagh Arya Samaj Rd", "pin_code": "110005", "location_type": "street_open", "crime_category": "person_property", "offense_description": "Smartphone snatched from commuter walking to metro station", "method_activity": "bike_snatch", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "28000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_015", "incident_date": "2024-03-16", "incident_time": "07:05", "country": "India", "state_ut": "Uttar Pradesh", "district": "Gautam Buddha Nagar", "city_town": "Noida", "locality": "Sector 62", "pin_code": "201309", "location_type": "street_open", "crime_category": "person_property", "offense_description": "Two-wheeler riders snatched purse during morning commute", "method_activity": "bike_snatch", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "22000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},

    # Repeated Pattern D: Daytime residential locked-house burglary during office hours (property, afternoon 12:00-16:00, forced door latch, INR 1,20,000-4,00,000)
    {"incident_id": "FIR_2024_016", "incident_date": "2024-02-07", "incident_time": "13:30", "country": "India", "state_ut": "Tamil Nadu", "district": "Chennai", "city_town": "Chennai", "locality": "Anna Nagar West", "pin_code": "600040", "location_type": "residential_home", "crime_category": "property", "offense_description": "Daytime apartment theft while occupants were at workplace", "method_activity": "lock_break", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "180000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_017", "incident_date": "2024-02-21", "incident_time": "14:15", "country": "India", "state_ut": "Tamil Nadu", "district": "Chennai", "city_town": "Chennai", "locality": "Adyar Gandhi Nagar", "pin_code": "600020", "location_type": "residential_home", "crime_category": "property", "offense_description": "Front latch tampered; gold ornaments stolen from cupboard", "method_activity": "lock_break", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "240000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_018", "incident_date": "2024-03-02", "incident_time": "13:00", "country": "India", "state_ut": "Tamil Nadu", "district": "Coimbatore", "city_town": "Coimbatore", "locality": "RS Puram", "pin_code": "641002", "location_type": "residential_home", "crime_category": "property", "offense_description": "Locked house break-in during afternoon", "method_activity": "lock_break", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "150000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_019", "incident_date": "2024-03-19", "incident_time": "15:00", "country": "India", "state_ut": "Tamil Nadu", "district": "Coimbatore", "city_town": "Coimbatore", "locality": "Gandhipuram", "pin_code": "641012", "location_type": "residential_home", "crime_category": "property", "offense_description": "Apartment burglary via balcony sliding grill", "method_activity": "lock_break", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "210000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_020", "incident_date": "2024-04-03", "incident_time": "14:40", "country": "India", "state_ut": "Tamil Nadu", "district": "Madurai", "city_town": "Madurai", "locality": "KK Nagar", "pin_code": "625020", "location_type": "residential_home", "crime_category": "property", "offense_description": "Daytime residential theft targeting electronic gadgets & jewelry", "method_activity": "lock_break", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "135000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},

    # Repeated Pattern E: Late night roadside dispute / physical altercation outside transit hub (violent, weapon=blunt/bottle, midnight 23:00-01:30, injury=1, victims=1-2, property=0)
    {"incident_id": "FIR_2024_021", "incident_date": "2024-01-20", "incident_time": "23:45", "country": "India", "state_ut": "Telangana", "district": "Hyderabad", "city_town": "Hyderabad", "locality": "Secunderabad Station Rd", "pin_code": "500003", "location_type": "public_transit", "crime_category": "violent", "offense_description": "Brawl between auto drivers and private transport operators", "method_activity": "physical_assault", "has_weapon": "1", "weapon_type": "blunt", "has_property": "0", "property_value": "0", "currency": "INR", "victim_count": "2", "offender_count": "3", "has_injury": "1", "has_arrest": "1"},
    {"incident_id": "FIR_2024_022", "incident_date": "2024-02-09", "incident_time": "00:30", "country": "India", "state_ut": "Telangana", "district": "Hyderabad", "city_town": "Hyderabad", "locality": "Mehdipatnam Bus Stand", "pin_code": "500028", "location_type": "public_transit", "crime_category": "violent", "offense_description": "Night altercation outside eatery involving blunt instruments", "method_activity": "physical_assault", "has_weapon": "1", "weapon_type": "blunt", "has_property": "0", "property_value": "0", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "1", "has_arrest": "1"},
    {"incident_id": "FIR_2024_023", "incident_date": "2024-02-24", "incident_time": "23:55", "country": "India", "state_ut": "Telangana", "district": "Rangareddy", "city_town": "Hyderabad", "locality": "Gachibowli Junction", "pin_code": "500032", "location_type": "street_open", "crime_category": "violent", "offense_description": "Roadside altercation following minor vehicle collision", "method_activity": "physical_assault", "has_weapon": "1", "weapon_type": "blunt", "has_property": "0", "property_value": "0", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "1", "has_arrest": "0"},
    {"incident_id": "FIR_2024_024", "incident_date": "2024-03-12", "incident_time": "01:10", "country": "India", "state_ut": "Telangana", "district": "Hyderabad", "city_town": "Hyderabad", "locality": "Abids Station Circle", "pin_code": "500001", "location_type": "street_open", "crime_category": "violent", "offense_description": "Late night verbal altercation turning into physical scuffle", "method_activity": "physical_assault", "has_weapon": "0", "weapon_type": "none", "has_property": "0", "property_value": "0", "currency": "INR", "victim_count": "2", "offender_count": "3", "has_injury": "1", "has_arrest": "1"},

    # Repeated Pattern F: Digital / Bank ATM skimming and card swapping (property, morning/afternoon 10:00-14:00, weapon=0, property INR 40,000-1,20,000)
    {"incident_id": "FIR_2024_025", "incident_date": "2024-01-29", "incident_time": "11:20", "country": "India", "state_ut": "Uttar Pradesh", "district": "Lucknow", "city_town": "Lucknow", "locality": "Hazratganj", "pin_code": "226001", "location_type": "bank_financial", "crime_category": "property", "offense_description": "Deceptive card swapping at unmanned ATM kiosk", "method_activity": "atm_tampering", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "50000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_026", "incident_date": "2024-02-14", "incident_time": "12:40", "country": "India", "state_ut": "Uttar Pradesh", "district": "Lucknow", "city_town": "Lucknow", "locality": "Alambagh", "pin_code": "226005", "location_type": "bank_financial", "crime_category": "property", "offense_description": "Elderly citizen assisted at ATM, card cloned and cash withdrawn", "method_activity": "atm_tampering", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "75000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_027", "incident_date": "2024-03-01", "incident_time": "10:50", "country": "India", "state_ut": "Uttar Pradesh", "district": "Varanasi", "city_town": "Varanasi", "locality": "Sigra", "pin_code": "221010", "location_type": "bank_financial", "crime_category": "property", "offense_description": "ATM vestibule skimming overlay discovered after unauthorized debits", "method_activity": "atm_tampering", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "90000", "currency": "INR", "victim_count": "2", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_028", "incident_date": "2024-03-20", "incident_time": "13:10", "country": "India", "state_ut": "Uttar Pradesh", "district": "Varanasi", "city_town": "Varanasi", "locality": "Cantonment", "pin_code": "221002", "location_type": "bank_financial", "crime_category": "property", "offense_description": "Fraudulent withdrawal using swapped debit card", "method_activity": "atm_tampering", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "45000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},

    # Pattern G: Commercial Shop-lifting during peak market hours (property, afternoon 16:00-19:00, weapon=0, property INR 8,000-25,000)
    {"incident_id": "FIR_2024_029", "incident_date": "2024-02-04", "incident_time": "17:30", "country": "India", "state_ut": "Gujarat", "district": "Ahmedabad", "city_town": "Ahmedabad", "locality": "CG Road Navrangpura", "pin_code": "380009", "location_type": "commercial_store", "crime_category": "property", "offense_description": "Apparel and cosmetics concealed in bag during busy evening hours", "method_activity": "shoplifting", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "18000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_030", "incident_date": "2024-02-17", "incident_time": "18:15", "country": "India", "state_ut": "Gujarat", "district": "Ahmedabad", "city_town": "Ahmedabad", "locality": "Maninagar Market", "pin_code": "380008", "location_type": "commercial_store", "crime_category": "property", "offense_description": "High-value branded perfumes taken from counter display", "method_activity": "shoplifting", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "24000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_031", "incident_date": "2024-03-09", "incident_time": "16:45", "country": "India", "state_ut": "Gujarat", "district": "Surat", "city_town": "Surat", "locality": "Athwa Lines", "pin_code": "395007", "location_type": "commercial_store", "crime_category": "property", "offense_description": "Electronics accessory theft from showroom", "method_activity": "shoplifting", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "12000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_032", "incident_date": "2024-03-25", "incident_time": "17:50", "country": "India", "state_ut": "Gujarat", "district": "Surat", "city_town": "Surat", "locality": "Varachha", "pin_code": "395006", "location_type": "commercial_store", "crime_category": "property", "offense_description": "Textile sample bundles stolen from retail showroom", "method_activity": "shoplifting", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "28000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},

    # Pattern H: Public transit pickpocketing / phone theft (property, morning & evening transit rush 08:30-10:00 & 18:30-20:00, INR 15,000-45,000)
    {"incident_id": "FIR_2024_033", "incident_date": "2024-02-15", "incident_time": "09:10", "country": "India", "state_ut": "West Bengal", "district": "Kolkata", "city_town": "Kolkata", "locality": "Howrah Bridge Approach", "pin_code": "700001", "location_type": "public_transit", "crime_category": "property", "offense_description": "Wallet and identity cards picked from pocket on crowded bus", "method_activity": "pickpocketing", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "14000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_034", "incident_date": "2024-03-01", "incident_time": "19:00", "country": "India", "state_ut": "West Bengal", "district": "Kolkata", "city_town": "Kolkata", "locality": "Sealdah Station Plaza", "pin_code": "700014", "location_type": "public_transit", "crime_category": "property", "offense_description": "Smartphone removed from backpack while boarding suburban train", "method_activity": "pickpocketing", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "32000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "1"},
    {"incident_id": "FIR_2024_035", "incident_date": "2024-03-14", "incident_time": "08:50", "country": "India", "state_ut": "West Bengal", "district": "Kolkata", "city_town": "Kolkata", "locality": "Esplanade Metro Gate", "pin_code": "700069", "location_type": "public_transit", "crime_category": "property", "offense_description": "Purse stolen in escalator queue", "method_activity": "pickpocketing", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "19000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},
    {"incident_id": "FIR_2024_036", "incident_date": "2024-03-29", "incident_time": "19:25", "country": "India", "state_ut": "West Bengal", "district": "North 24 Parganas", "city_town": "Bidhannagar", "locality": "Salt Lake Sector V", "pin_code": "700091", "location_type": "public_transit", "crime_category": "property", "offense_description": "Mobile phone picked during rush hour at bus terminus", "method_activity": "pickpocketing", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "26000", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "0", "has_arrest": "0"},

    # Pattern I: Deliberate UNUSUAL COMBINATIONS for testing novel pattern discovery (Section 4.H & 7)
    # Unusual 1: Very high value jewellery heist with zero force or weapon during afternoon (unusual property, calm execution)
    {"incident_id": "FIR_2024_037", "incident_date": "2024-04-05", "incident_time": "14:00", "country": "India", "state_ut": "Maharashtra", "district": "Mumbai Suburban", "city_town": "Mumbai", "locality": "Bandra West Hill Rd", "pin_code": "400050", "location_type": "commercial_store", "crime_category": "property", "offense_description": "High-value gemstone tray substituted with replicas during private showing", "method_activity": "sleight_of_hand", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "1850000", "currency": "INR", "victim_count": "1", "offender_count": "2", "has_injury": "0", "has_arrest": "0"},
    # Unusual 2: Midnight unarmed altercation in commercial bank with zero property loss (odd timing, no weapon, injury)
    {"incident_id": "FIR_2024_038", "incident_date": "2024-04-12", "incident_time": "02:15", "country": "India", "state_ut": "Karnataka", "district": "Bengaluru Urban", "city_town": "Bengaluru", "locality": "MG Road", "pin_code": "560001", "location_type": "bank_financial", "crime_category": "violent", "offense_description": "Dispute between night maintenance crew and security guard", "method_activity": "unarmed_assault", "has_weapon": "0", "weapon_type": "none", "has_property": "0", "property_value": "0", "currency": "INR", "victim_count": "1", "offender_count": "1", "has_injury": "1", "has_arrest": "1"},
    # Unusual 3: Midday firearm display with zero property taken and zero injury (odd firearm presence without theft)
    {"incident_id": "FIR_2024_039", "incident_date": "2024-04-18", "incident_time": "12:10", "country": "India", "state_ut": "Uttar Pradesh", "district": "Lucknow", "city_town": "Lucknow", "locality": "Gomti Nagar", "pin_code": "226010", "location_type": "residential_home", "crime_category": "violent", "offense_description": "Firearm flashed during boundary wall property dispute", "method_activity": "armed_intimidation", "has_weapon": "1", "weapon_type": "firearm", "has_property": "0", "property_value": "0", "currency": "INR", "victim_count": "3", "offender_count": "2", "has_injury": "0", "has_arrest": "1"},
    # Unusual 4: Multi-victim cyber-financial phishing with commercial victim setting
    {"incident_id": "FIR_2024_040", "incident_date": "2024-04-22", "incident_time": "15:30", "country": "India", "state_ut": "Telangana", "district": "Hyderabad", "city_town": "Hyderabad", "locality": "HITEC City", "pin_code": "500081", "location_type": "commercial_store", "crime_category": "property", "offense_description": "Corporate billing account spoofing and fraudulent vendor payout", "method_activity": "cyber_phishing", "has_weapon": "0", "weapon_type": "none", "has_property": "1", "property_value": "2400000", "currency": "INR", "victim_count": "4", "offender_count": "3", "has_injury": "0", "has_arrest": "0"}
]

# Add additional 25 rows to reach 65 synthetic rows with realistic variation across the same cities
for i in range(41, 66):
    state_sample = ["Karnataka", "Maharashtra", "Delhi", "Tamil Nadu", "Telangana", "Uttar Pradesh", "Gujarat", "West Bengal"][i % 8]
    district_map = {
        "Karnataka": ("Bengaluru Urban", "Bengaluru", "Malleshwaram", "560003"),
        "Maharashtra": ("Mumbai Suburban", "Mumbai", "Goregaon East", "400063"),
        "Delhi": ("South Delhi", "New Delhi", "Saket", "110017"),
        "Tamil Nadu": ("Chennai", "Chennai", "Mylapore", "600004"),
        "Telangana": ("Hyderabad", "Hyderabad", "Kukatpally", "500072"),
        "Uttar Pradesh": ("Lucknow", "Lucknow", "Indira Nagar", "226016"),
        "Gujarat": ("Ahmedabad", "Ahmedabad", "Vastrapur", "380015"),
        "West Bengal": ("Kolkata", "Kolkata", "Alipore", "700027")
    }
    dist, city, loc, pin = district_map[state_sample]
    is_wep = "1" if (i % 3 == 0) else "0"
    is_prop = "1" if (i % 4 != 0) else "0"
    cat = "person_property" if (is_wep == "1" and is_prop == "1") else ("property" if is_prop == "1" else "violent")
    val = str(20000 + (i * 3500)) if is_prop == "1" else "0"
    hr = f"{8 + (i * 2) % 15:02d}:{(i * 12) % 60:02d}"
    
    sample_rows.append({
        "incident_id": f"FIR_2024_{i:03d}",
        "incident_date": f"2024-{1 + (i % 4):02d}-{10 + (i % 18):02d}",
        "incident_time": hr,
        "country": "India",
        "state_ut": state_sample,
        "district": dist,
        "city_town": city,
        "locality": loc,
        "pin_code": pin,
        "location_type": "street_open" if (i % 2 == 0) else "commercial_store",
        "crime_category": cat,
        "offense_description": f"Incident report #{i} documenting {cat.replace('_', ' ')}",
        "method_activity": "snatch" if cat == "person_property" else ("theft" if cat == "property" else "altercation"),
        "has_weapon": is_wep,
        "weapon_type": "edged_weapon" if is_wep == "1" else "none",
        "has_property": is_prop,
        "property_value": val,
        "currency": "INR",
        "victim_count": "1" if (i % 5 != 0) else "2",
        "offender_count": "2" if (i % 3 == 0) else "1",
        "has_injury": "1" if (cat == "violent") else "0",
        "has_arrest": "1" if (i % 2 == 0) else "0"
    })

fieldnames = [
    "incident_id", "incident_date", "incident_time", "country", "state_ut", "district",
    "city_town", "locality", "pin_code", "location_type", "crime_category",
    "offense_description", "method_activity", "has_weapon", "weapon_type",
    "has_property", "property_value", "currency", "victim_count", "offender_count",
    "has_injury", "has_arrest"
]

target_paths = [
    "data/sample/crime_compass_sample_india.csv",
    "frontend/public/crime_compass_sample_india.csv"
]

for p in target_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        # Write mandatory synthetic notice header
        f.write("# All rows in this sample dataset are synthetic and created for software demonstration. They are not real police records and must not be used as evidence or as a representation of actual crime rates.\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sample_rows:
            writer.writerow(row)

# Also create the Column Mapping Template CSV
template_cols = [
    "incident_id", "incident_date", "incident_time", "country", "state_ut", "district",
    "city_town", "locality", "pin_code", "location_type", "crime_category",
    "offense_description", "method_activity", "has_weapon", "weapon_type", "weapon_count",
    "has_property", "has_stolen_property", "property_value", "currency",
    "victim_count", "offender_count", "has_injury", "has_drug", "has_arrest"
]

template_paths = [
    "data/sample/crime_compass_column_mapping_template.csv",
    "frontend/public/crime_compass_column_mapping_template.csv"
]

for p in template_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        f.write("# Crime Compass Column Mapping Template — Use these recommended header names for automatic 100% mapping.\n")
        writer = csv.writer(f)
        writer.writerow(template_cols)
        writer.writerow(["FIR_EXAMPLE_001", "2024-05-15", "21:30", "India", "Karnataka", "Bengaluru Urban", "Bengaluru", "Indiranagar", "560038", "commercial_store", "person_property", "Cash counter robbery", "intimidation", "1", "edged_weapon", "1", "1", "1", "45000", "INR", "2", "2", "0", "0", "0"])

print(f"Generated {len(sample_rows)} sample rows in {target_paths}")
