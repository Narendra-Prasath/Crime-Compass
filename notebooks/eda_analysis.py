"""
CRIME DNA — Phase 4: Exploratory Data Analysis & Behavioral Profiling

This script performs deep exploratory data analysis across all 70 Behavioral DNA dimensions
and generates publication-quality figures illustrating behavioral distributions, temporal rhythms,
urban context, weapon deployment, victimology, correlations, and rare anomalous crime signatures.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Ensure workspace root is in sys.path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Set clean styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

FIG_DIR = os.path.join(workspace_root, "docs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

DNA_PATH = os.path.join(workspace_root, "data", "processed", "crime_dna_behavioral_features.csv")
CLEANED_PATH = os.path.join(workspace_root, "data", "processed", "crime_dna_cleaned.csv")

print(f"Loading Behavioral DNA features from {DNA_PATH}...")
df_dna = pd.read_csv(DNA_PATH, low_memory=False)
print(f"Loaded DNA features: {df_dna.shape}")

print(f"Loading Cleaned data for reference from {CLEANED_PATH}...")
df_clean = pd.read_csv(CLEANED_PATH, low_memory=False)
print(f"Loaded Cleaned data: {df_clean.shape}")


# -------------------------------------------------------------
# 1. Crime Distribution (Target Category Combinations)
# -------------------------------------------------------------
print("\nGenerating Figure 1: Crime Distribution...")
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
crime_cats = {
    "Property Only": (df_dna["crime_against_property"] == 1.0) & (df_dna["crime_against_person"] == 0.0) & (df_dna["crime_against_society"] == 0.0),
    "Person (Violent) Only": (df_dna["crime_against_person"] == 1.0) & (df_dna["crime_against_property"] == 0.0) & (df_dna["crime_against_society"] == 0.0),
    "Society (Public Order) Only": (df_dna["crime_against_society"] == 1.0) & (df_dna["crime_against_person"] == 0.0) & (df_dna["crime_against_property"] == 0.0),
    "Person + Property": df_dna["crime_against_person_property"] == 1.0,
    "Property + Society": df_dna["crime_against_property_society"] == 1.0,
    "Person + Society": df_dna["crime_against_person_society"] == 1.0,
    "Person + Property + Society": df_dna["crime_against_person_property_society"] == 1.0,
}
counts = {k: v.sum() for k, v in crime_cats.items()}
pcts = {k: (v / len(df_dna)) * 100 for k, v in counts.items()}

colors = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d"]
bars = ax.barh(list(pcts.keys())[::-1], list(pcts.values())[::-1], color=colors[::-1], height=0.65)
ax.set_xlabel("Percentage of Total Incidents (%)", fontsize=11, fontweight="bold")
ax.set_title("Crime Target Category Distribution (220,663 Incidents)", fontsize=13, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlim(0, 60)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.8, bar.get_y() + bar.get_height()/2, f"{w:.1f}% ({int(w*len(df_dna)/100):,})",
            va="center", fontsize=9, fontweight="bold", color="#333333")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "01_crime_distribution.png"))
plt.close(fig)


# -------------------------------------------------------------
# 2. Time Patterns (Diurnal Cycle & Monthly Trends)
# -------------------------------------------------------------
print("Generating Figure 2: Temporal Patterns...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

# Hourly distribution from cleaned dataset
hourly_counts = df_clean["incident_hour"].value_counts().sort_index()
hourly_pct = (hourly_counts / len(df_clean)) * 100
ax1.plot(hourly_pct.index, hourly_pct.values, marker="o", color="#1b7837", linewidth=2.2, markersize=5)
ax1.fill_between(hourly_pct.index, hourly_pct.values, alpha=0.18, color="#1b7837")
ax1.set_title("24-Hour Diurnal Crime Rhythm", fontsize=12, fontweight="bold")
ax1.set_xlabel("Hour of Day (00:00 - 23:00)", fontsize=10, fontweight="bold")
ax1.set_ylabel("% of Incidents", fontsize=10, fontweight="bold")
ax1.set_xticks(range(0, 24, 2))
ax1.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], rotation=45)
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1.axvspan(20, 23.5, color="#762a83", alpha=0.12, label="Night Window (20:00-06:00)")
ax1.axvspan(0, 6, color="#762a83", alpha=0.12)
ax1.legend(loc="upper left")

# Monthly distribution
monthly_counts = df_clean["incident_month"].value_counts().sort_index()
monthly_pct = (monthly_counts / len(df_clean)) * 100
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ax2.bar(range(1, 13), [monthly_pct.get(m, 0) for m in range(1, 13)], color="#386cb0", width=0.6)
ax2.set_title("Monthly Incident Volume (2024)", fontsize=12, fontweight="bold")
ax2.set_xlabel("Calendar Month", fontsize=10, fontweight="bold")
ax2.set_ylabel("% of Incidents", fontsize=10, fontweight="bold")
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(months)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "02_temporal_patterns.png"))
plt.close(fig)


# -------------------------------------------------------------
# 3. Night vs Day Comparison Across Crime Profiles
# -------------------------------------------------------------
print("Generating Figure 3: Night vs Day Profiles...")
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

is_night = df_dna["time_is_night"] == 1.0
profiles = ["crime_against_person", "crime_against_property", "crime_against_society", "has_weapon", "has_injury", "has_drug", "is_co_offender"]
profile_labels = ["Violent / Person", "Property", "Society / Vice", "Weapon Involved", "Injury Inflicted", "Drug Related", "Co-Offenders"]

night_means = [df_dna.loc[is_night, col].mean() * 100 for col in profiles]
day_means = [df_dna.loc[~is_night, col].mean() * 100 for col in profiles]

x = np.arange(len(profiles))
width = 0.35

rects1 = ax.bar(x - width/2, day_means, width, label="Daytime (06:00 - 20:00)", color="#fdbf6f", edgecolor="#e31a1c", linewidth=0.5)
rects2 = ax.bar(x + width/2, night_means, width, label="Nighttime (20:00 - 06:00)", color="#1f78b4", edgecolor="#08306b", linewidth=0.5)

ax.set_ylabel("Prevalence within Time Window (%)", fontsize=10, fontweight="bold")
ax.set_title("Behavioral Characteristics: Nighttime vs Daytime", fontsize=12, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(profile_labels, rotation=20, ha="right", fontsize=9, fontweight="bold")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.legend(frameon=True, facecolor="white")

for rect in rects1 + rects2:
    h = rect.get_height()
    ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "03_night_vs_day.png"))
plt.close(fig)


# -------------------------------------------------------------
# 4. Weekend vs Weekday Patterns
# -------------------------------------------------------------
print("Generating Figure 4: Weekend vs Weekday Patterns...")
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

is_wknd = df_dna["time_is_weekend"] == 1.0
wknd_means = [df_dna.loc[is_wknd, col].mean() * 100 for col in profiles]
wkdy_means = [df_dna.loc[~is_wknd, col].mean() * 100 for col in profiles]

rects1 = ax.bar(x - width/2, wkdy_means, width, label="Weekday (Mon - Fri)", color="#7fc97f", edgecolor="#238b45", linewidth=0.5)
rects2 = ax.bar(x + width/2, wknd_means, width, label="Weekend (Sat - Sun)", color="#beaed4", edgecolor="#54278f", linewidth=0.5)

ax.set_ylabel("Prevalence within Period (%)", fontsize=10, fontweight="bold")
ax.set_title("Behavioral Characteristics: Weekend vs Weekday", fontsize=12, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(profile_labels, rotation=20, ha="right", fontsize=9, fontweight="bold")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.legend(frameon=True, facecolor="white")

for rect in rects1 + rects2:
    h = rect.get_height()
    ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "04_weekend_vs_weekday.png"))
plt.close(fig)


# -------------------------------------------------------------
# 5. Location & Urban Hierarchy Patterns
# -------------------------------------------------------------
print("Generating Figure 5: Location & Urban Setting...")
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

pop_cols = [c for c in df_dna.columns if c.startswith("population_group_desc_")]
clean_pop_labels = [
    c.replace("population_group_desc_", "").replace("_", " ").title()
    for c in pop_cols
]
pop_counts = [df_dna[c].sum() for c in pop_cols]
pop_pcts = [(cnt / len(df_dna)) * 100 for cnt in pop_counts]

# Sort by count
sorted_indices = np.argsort(pop_pcts)
sorted_labels = [clean_pop_labels[i] for i in sorted_indices]
sorted_pcts = [pop_pcts[i] for i in sorted_indices]

bars = ax.barh(sorted_labels, sorted_pcts, color="#41b6c4", height=0.65)
ax.set_xlabel("Percentage of Total Incidents (%)", fontsize=10, fontweight="bold")
ax.set_title("Incidents Across Urban & Jurisdictional Hierarchy", fontsize=12, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.5, bar.get_y() + bar.get_height()/2, f"{w:.1f}%",
            va="center", fontsize=8.5, fontweight="bold", color="#222222")

ax.set_xlim(0, max(sorted_pcts) + 5)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "05_location_urban_patterns.png"))
plt.close(fig)


# -------------------------------------------------------------
# 6. Weapon Patterns (Armament & Violence Escalation)
# -------------------------------------------------------------
print("Generating Figure 6: Weapon Patterns...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

weapon_status = {
    "Unarmed": (df_dna["has_weapon"] == 0).sum(),
    "Single Weapon": ((df_dna["has_weapon"] == 1) & (df_dna["is_multi_weapon"] == 0)).sum(),
    "Multiple Weapons": (df_dna["is_multi_weapon"] == 1).sum()
}
colors_wep = ["#74add1", "#f46d43", "#a50026"]
wedges, texts, autotexts = ax1.pie(
    list(weapon_status.values()),
    labels=list(weapon_status.keys()),
    autopct="%1.1f%%",
    startangle=140,
    colors=colors_wep,
    textprops={"fontsize": 10, "fontweight": "bold"}
)
ax1.set_title("Weapon Involvement Across Incidents", fontsize=12, fontweight="bold")

# Weapons vs Injury correlation
wep_inj = pd.crosstab(df_dna["has_weapon"] == 1, df_dna["has_injury"] == 1, normalize="index") * 100
wep_inj.index = ["Unarmed", "Armed"]
wep_inj.columns = ["No Injury Inflicted", "Injury Inflicted"]
wep_inj.plot(kind="bar", stacked=True, color=["#abd9e9", "#d73027"], ax=ax2, edgecolor="white", width=0.5)
ax2.set_title("Injury Escalation by Weapon Presence", fontsize=12, fontweight="bold")
ax2.set_ylabel("Percentage (%)", fontsize=10, fontweight="bold")
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.set_xticklabels(["Unarmed Incidents", "Armed Incidents"], rotation=0, fontsize=10, fontweight="bold")
ax2.legend(loc="upper right")

for c in ax2.containers:
    ax2.bar_label(c, fmt="%.1f%%", label_type="center", color="black", fontsize=9, fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "06_weapon_patterns.png"))
plt.close(fig)


# -------------------------------------------------------------
# 7. Victim & Offender Patterns (Crew Size & Age Dynamics)
# -------------------------------------------------------------
print("Generating Figure 7: Victim & Offender Dynamics...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

# Offender crew distribution
crew_counts = pd.cut(df_clean["offender_count"], bins=[0, 1, 2, 3, 5, 30], labels=["1 (Solo)", "2 (Duo)", "3 (Trio)", "4-5 (Group)", "6+ (Pack)"]).value_counts(normalize=True).sort_index() * 100
bars1 = ax1.bar(crew_counts.index, crew_counts.values, color="#8073ac", width=0.6)
ax1.set_title("Offender Group Structure (Crew Size)", fontsize=12, fontweight="bold")
ax1.set_ylabel("% of Incidents", fontsize=10, fontweight="bold")
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, h + 0.8, f"{h:.1f}%", ha="center", fontsize=9, fontweight="bold")
ax1.set_ylim(0, 90)

# Victim vs Offender Age distribution
ax2.hist(df_clean["victim_avg_age"].dropna(), bins=25, alpha=0.55, color="#2166ac", label=f"Victim Age (Median: {df_clean['victim_avg_age'].median():.0f})", density=True)
ax2.hist(df_clean["offender_avg_age"].dropna(), bins=25, alpha=0.55, color="#b2182b", label=f"Offender Age (Median: {df_clean['offender_avg_age'].median():.0f})", density=True)
ax2.set_title("Victim vs Offender Age Density", fontsize=12, fontweight="bold")
ax2.set_xlabel("Age (Years)", fontsize=10, fontweight="bold")
ax2.set_ylabel("Probability Density", fontsize=10, fontweight="bold")
ax2.legend(frameon=True, facecolor="white")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "07_people_victim_offender_patterns.png"))
plt.close(fig)


# -------------------------------------------------------------
# 8. Property & Economic Valuation Patterns
# -------------------------------------------------------------
print("Generating Figure 8: Property & Economics...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

# Stolen property count distribution
has_prop = df_dna["has_property"].sum() / len(df_dna) * 100
has_stolen = df_dna["has_stolen_property"].sum() / len(df_dna) * 100
is_cargo = df_dna["is_cargo_theft"].sum() / len(df_dna) * 100

ax1.bar(["Property Involved", "Items Actually Stolen", "Cargo / Freight Target"], [has_prop, has_stolen, is_cargo], color=["#4575b4", "#74add1", "#fdae61"], width=0.55)
ax1.set_title("Property Targeting Prevalence", fontsize=12, fontweight="bold")
ax1.set_ylabel("% of All Incidents", fontsize=10, fontweight="bold")
ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1.set_ylim(0, 70)
for p in ax1.patches:
    h = p.get_height()
    ax1.annotate(f"{h:.1f}%", xy=(p.get_x() + p.get_width() / 2, h + 1), ha="center", fontsize=9.5, fontweight="bold")

# Property log value distribution (only for incidents with property)
prop_vals = df_clean.loc[df_clean["property_value_log"] > 0, "property_value_log"]
ax2.hist(prop_vals, bins=30, color="#313695", edgecolor="white", alpha=0.85)
ax2.set_title("Distribution of Log Property Loss (when > $0)", fontsize=12, fontweight="bold")
ax2.set_xlabel("Log Property Loss: log(1 + Property Value)", fontsize=10, fontweight="bold")
ax2.set_ylabel("Number of Incidents", fontsize=10, fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "08_property_economic_patterns.png"))
plt.close(fig)


# -------------------------------------------------------------
# 9. Injury, Drug, & Arrest Context
# -------------------------------------------------------------
print("Generating Figure 9: Context, Injury, Drugs & Arrest...")
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

ctx_rates = {
    "Physical Injury Inflicted": df_dna["has_injury"].mean() * 100,
    "Narcotics / Contraband Involved": df_dna["has_drug"].mean() * 100,
    "Organized Enterprise / Activity": df_dna["has_criminal_activity"].mean() * 100,
    "Immediate On-Scene Arrest": df_dna["has_arrest_on_scene"].mean() * 100,
    "Bias / Hate Motivated": df_dna["has_bias_motivation"].mean() * 100,
    "Prior Victim-Offender Relationship": df_dna["has_relationship"].mean() * 100
}
y_pos = np.arange(len(ctx_rates))
bars = ax.barh(y_pos, list(ctx_rates.values()), color=["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628"], height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(list(ctx_rates.keys()), fontsize=10, fontweight="bold")
ax.set_xlabel("Incidence Rate across All Incidents (%)", fontsize=10, fontweight="bold")
ax.set_title("Contextual Modus Operandi & Outcome Prevalence", fontsize=12, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlim(0, 35)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.6, bar.get_y() + bar.get_height()/2, f"{w:.2f}%", va="center", fontsize=9, fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "09_context_harm_drugs_arrest.png"))
plt.close(fig)


# -------------------------------------------------------------
# 10. Numerical Feature Correlation Matrix Heatmap
# -------------------------------------------------------------
print("Generating Figure 10: Feature Correlation Matrix...")
core_corr_features = [
    "time_is_night", "time_is_weekend",
    "crime_against_person", "crime_against_property", "crime_against_society",
    "has_weapon", "weapon_count_scaled", "is_multi_weapon",
    "has_relationship", "has_injury", "injury_record_count_scaled",
    "victim_count_scaled", "is_multi_victim", "victim_avg_age_scaled",
    "offender_count_scaled", "is_co_offender", "offender_avg_age_scaled",
    "has_property", "has_stolen_property", "property_value_log_scaled",
    "has_drug", "has_arrest_on_scene", "population_log_scaled"
]

corr_matrix = df_dna[core_corr_features].corr()

fig, ax = plt.subplots(figsize=(14, 12), dpi=300)
cax = ax.matshow(corr_matrix, cmap="coolwarm", vmin=-0.6, vmax=0.6)
fig.colorbar(cax, shrink=0.8, pad=0.03, label="Pearson Correlation Coefficient")

ax.set_xticks(range(len(core_corr_features)))
ax.set_yticks(range(len(core_corr_features)))
clean_corr_labels = [c.replace("_scaled", "").replace("_log", "").replace("crime_against_", "target_") for c in core_corr_features]
ax.set_xticklabels(clean_corr_labels, rotation=90, fontsize=8.5, fontweight="bold")
ax.set_yticklabels(clean_corr_labels, fontsize=8.5, fontweight="bold")
ax.set_title("Correlation Heatmap of Behavioral DNA Dimensions", fontsize=13, fontweight="bold", pad=25)
ax.grid(False)

# Add numerical values for significant correlations
for i in range(len(core_corr_features)):
    for j in range(len(core_corr_features)):
        val = corr_matrix.iloc[i, j]
        if abs(val) > 0.35 and i != j:
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="white" if abs(val) > 0.45 else "black", fontsize=7.5, fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "10_feature_correlations.png"))
plt.close(fig)


# -------------------------------------------------------------
# 11. Feature Distributions across Behavioral DNA
# -------------------------------------------------------------
print("Generating Figure 11: Feature Distributions...")
fig, axes = plt.subplots(2, 3, figsize=(14, 8), dpi=300)
dist_features = [
    ("time_hour_sin", "Diurnal Rhythm (Hour Sine)", "#1f77b4"),
    ("offense_count_scaled", "Offense Multiplicity", "#ff7f0e"),
    ("weapon_count_scaled", "Scaled Weapon Volume", "#2ca02c"),
    ("victim_avg_age_scaled", "Normalized Victim Age", "#d62728"),
    ("property_value_log_scaled", "Log Property Loss", "#9467bd"),
    ("population_log_scaled", "Jurisdictional Density (Log Pop)", "#8c564b")
]

for idx, (col, title, color) in enumerate(dist_features):
    ax = axes[idx // 3, idx % 3]
    ax.hist(df_dna[col], bins=25, color=color, alpha=0.75, edgecolor="white")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Value ([0.0, 1.0])", fontsize=9)
    ax.set_ylabel("Count", fontsize=9)
    ax.set_xlim(-0.02, 1.02)

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "11_feature_distributions.png"))
plt.close(fig)


# -------------------------------------------------------------
# 12. Rare Behavioral Signatures (Outlier Fingerprints)
# -------------------------------------------------------------
print("Generating Figure 12: Rare Behavioral Signatures...")
rare_signatures = {
    "Triple Target (Person + Property + Society)": df_dna["crime_against_person_property_society"] == 1.0,
    "Armed Cargo Supply-Chain Theft": (df_dna["is_cargo_theft"] == 1.0) & (df_dna["has_weapon"] == 1.0),
    "Multi-Victim Armed Domestic Assault": (df_dna["has_relationship"] == 1.0) & (df_dna["has_weapon"] == 1.0) & (df_dna["is_multi_victim"] == 1.0),
    "Multi-Weapon Narcotics Enterprise": (df_dna["is_multi_weapon"] == 1.0) & (df_dna["has_drug"] == 1.0) & (df_dna["has_criminal_activity"] == 1.0),
    "Hate / Bias-Motivated Violent Assault": (df_dna["has_bias_motivation"] == 1.0) & (df_dna["has_injury"] == 1.0),
    "Large Gang Crew (4+ Co-offenders)": df_dna["offender_count_scaled"] >= 0.75,
}

rare_counts = {k: v.sum() for k, v in rare_signatures.items()}
rare_pcts = {k: (v / len(df_dna)) * 100 for k, v in rare_counts.items()}

fig, ax = plt.subplots(figsize=(11, 5), dpi=300)
bars = ax.barh(list(rare_pcts.keys())[::-1], list(rare_pcts.values())[::-1], color="#e7298a", height=0.6)
ax.set_xlabel("Prevalence (% of 220,663 Incidents)", fontsize=10, fontweight="bold")
ax.set_title("Rare Behavioral Modus Operandi Combinations", fontsize=12, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mtick.PercentFormatter())

for bar in bars:
    w = bar.get_width()
    cnt = int(w * len(df_dna) / 100)
    ax.text(w + 0.02, bar.get_y() + bar.get_height()/2, f"{w:.3f}% ({cnt:,} cases)",
            va="center", fontsize=8.5, fontweight="bold", color="#333333")

ax.set_xlim(0, max(rare_pcts.values()) * 1.35)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "12_rare_behavioral_signatures.png"))
plt.close(fig)

print(f"\nAll 12 exploratory figures successfully created in {FIG_DIR}!")
