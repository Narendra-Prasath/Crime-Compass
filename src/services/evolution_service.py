"""
CRIME DNA — Behavioral Pattern Evolution Service

Integrates Phase 8 empirical longitudinal findings into the user-facing analysis flow.
Tracks how behavioral modus operandi and environmental characteristics evolve across
the historical 12-month observation period (January – December) for a given pattern.

Strictly enforces ethical boundaries: reflects population-level behavioral shifts,
never sequential actions of an individual offender unless legitimate linkage exists.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from src.models.clustering.config import CLUSTER_ARCHETYPES

logger = logging.getLogger("CRIME_DNA_EVOLUTION_SERVICE")

# Empirical historical benchmarks computed across 220,663 cleaned incidents
# Early (Jan-Apr), Middle (May-Aug), Later (Sep-Dec)
EMPIRICAL_CLUSTER_PERIODS: Dict[int, Dict[str, Dict[str, Any]]] = {
    0: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Daytime + Small Town + Property involved + No Weapon",
            "behavioral_characteristics": ["Daytime", "Small Town", "Property involved", "No Weapon"],
            "summary": "Winter property offenses concentrated in smaller jurisdictions during regular daylight hours.",
            "metrics": {"nighttime_pct": 14.2, "weapon_presence_pct": 0.8, "physical_injury_pct": 0.8, "property_involvement_pct": 99.6, "incident_volume": 5933}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Daytime + Small Town + Property involved + Minimal Force",
            "behavioral_characteristics": ["Daytime", "Small Town", "Property involved", "Minimal Force"],
            "summary": "Warm-weather uptick in nocturnal opportunistic theft (+1.9%) with sustained property focus.",
            "metrics": {"nighttime_pct": 16.1, "weapon_presence_pct": 1.0, "physical_injury_pct": 0.8, "property_involvement_pct": 99.8, "incident_volume": 6123}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Daytime + Municipal Structures + Property Target + No Weapon",
            "behavioral_characteristics": ["Daytime", "Municipal Structures", "Property Target", "No Weapon"],
            "summary": "Stabilization to daylight baseline with steady structure and vehicle property targeting.",
            "metrics": {"nighttime_pct": 14.0, "weapon_presence_pct": 1.0, "physical_injury_pct": 0.9, "property_involvement_pct": 99.8, "incident_volume": 5669}
        }
    },
    1: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Daytime/Evening + Interpersonal Conflict + Armed + Bodily Injury",
            "behavioral_characteristics": ["Daytime/Evening", "Interpersonal Conflict", "Armed", "Bodily Injury"],
            "summary": "Indoor and domestic interpersonal disputes with elevated firearm brandishing and physical trauma.",
            "metrics": {"nighttime_pct": 24.8, "weapon_presence_pct": 85.5, "physical_injury_pct": 85.0, "property_involvement_pct": 8.1, "incident_volume": 23270}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Nocturnal Surge + Outdoor Encounters + Armed + Elevated Lethality",
            "behavioral_characteristics": ["Nocturnal Surge", "Outdoor Encounters", "Armed", "Elevated Lethality"],
            "summary": "Significant seasonal expansion (+1.42% surge, Shift 02) driven by outdoor evening socialization.",
            "metrics": {"nighttime_pct": 27.4, "weapon_presence_pct": 85.6, "physical_injury_pct": 85.1, "property_involvement_pct": 8.5, "incident_volume": 26932}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Evening + Domestic/Indoor Ties + Armed + Bodily Injury",
            "behavioral_characteristics": ["Evening", "Domestic/Indoor Ties", "Armed", "Bodily Injury"],
            "summary": "Transition back to indoor domestic interpersonal encounters during colder late-year months.",
            "metrics": {"nighttime_pct": 25.7, "weapon_presence_pct": 84.8, "physical_injury_pct": 84.3, "property_involvement_pct": 8.3, "incident_volume": 24227}
        }
    },
    2: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Daytime + Suburban Commercial + Property involved + No Weapon",
            "behavioral_characteristics": ["Daytime", "Suburban Commercial", "Property involved", "No Weapon"],
            "summary": "Daytime suburban retail and structure larceny with near-zero weapon deployment.",
            "metrics": {"nighttime_pct": 8.1, "weapon_presence_pct": 0.4, "physical_injury_pct": 0.4, "property_involvement_pct": 100.0, "incident_volume": 11994}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Daytime + Mid-Sized Retail + Property involved + No Weapon",
            "behavioral_characteristics": ["Daytime", "Mid-Sized Retail", "Property involved", "No Weapon"],
            "summary": "Mid-year commercial retail theft volume peak across mid-sized suburban municipalities.",
            "metrics": {"nighttime_pct": 7.0, "weapon_presence_pct": 0.5, "physical_injury_pct": 0.5, "property_involvement_pct": 100.0, "incident_volume": 12459}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Daytime + High Property Theft + Unarmed + No Injury",
            "behavioral_characteristics": ["Daytime", "High Property Theft", "Unarmed", "No Injury"],
            "summary": "Pure non-violent commercial larceny during peak holiday shopping periods (lowest nocturnal rate: 5.0%).",
            "metrics": {"nighttime_pct": 5.0, "weapon_presence_pct": 0.7, "physical_injury_pct": 0.6, "property_involvement_pct": 100.0, "incident_volume": 10740}
        }
    },
    3: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Night + Residential + No Weapon",
            "behavioral_characteristics": ["Night", "Residential", "Property involved", "No Weapon"],
            "summary": "Nocturnal residential break-ins and burglaries during colder months without force or weapons.",
            "metrics": {"nighttime_pct": 46.8, "weapon_presence_pct": 1.3, "physical_injury_pct": 1.2, "property_involvement_pct": 99.9, "incident_volume": 10012}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Night + Residential + Weapon Uptick",
            "behavioral_characteristics": ["Night", "Residential", "Property involved", "Weapon Uptick"],
            "summary": "Peak nocturnal burglary volume (11,956 incidents) with slight escalation in force and weapon display (+0.6%).",
            "metrics": {"nighttime_pct": 49.1, "weapon_presence_pct": 1.9, "physical_injury_pct": 1.8, "property_involvement_pct": 99.9, "incident_volume": 11956}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Night + Commercial & Residential + High Property Target",
            "behavioral_characteristics": ["Night", "Commercial & Residential", "High Property Target", "Low Force"],
            "summary": "Expansion into commercial inventory break-ins alongside residential targets during holiday shopping months.",
            "metrics": {"nighttime_pct": 48.1, "weapon_presence_pct": 1.7, "physical_injury_pct": 1.6, "property_involvement_pct": 99.9, "incident_volume": 11367}
        }
    },
    4: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Night + Public Space + High Arrest + Society Infractions",
            "behavioral_characteristics": ["Night", "Public Space", "High Arrest", "Society Infractions"],
            "summary": "Winter nightlife enforcement, public intoxication, and disorderly infractions in urban spaces.",
            "metrics": {"nighttime_pct": 36.7, "weapon_presence_pct": 6.7, "physical_injury_pct": 1.2, "property_involvement_pct": 94.2, "incident_volume": 2910}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Night + Nightlife Entertainment + High Arrest + Low Weapon",
            "behavioral_characteristics": ["Night", "Nightlife Entertainment", "High Arrest", "Low Weapon"],
            "summary": "Elevated warm-weather nightlife density and proactive police patrols with consistent high arrest rate.",
            "metrics": {"nighttime_pct": 37.9, "weapon_presence_pct": 6.8, "physical_injury_pct": 1.1, "property_involvement_pct": 93.2, "incident_volume": 2994}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Night + Weekend Venues + Elevated Arrest + Weapon Presence",
            "behavioral_characteristics": ["Night", "Weekend Venues", "Elevated Arrest", "Weapon Presence"],
            "summary": "Holiday party season vice and liquor enforcement with slight uptick in weapon discoveries (+1.1%).",
            "metrics": {"nighttime_pct": 38.1, "weapon_presence_pct": 7.9, "physical_injury_pct": 1.7, "property_involvement_pct": 93.5, "incident_volume": 2752}
        }
    },
    5: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Daytime + Public Order + Regulatory Citations + No Injury",
            "behavioral_characteristics": ["Daytime", "Public Order", "Regulatory Citations", "No Injury"],
            "summary": "Non-drug enterprise offenses and regulatory citations resulting in formal summonses.",
            "metrics": {"nighttime_pct": 25.4, "weapon_presence_pct": 11.5, "physical_injury_pct": 0.4, "property_involvement_pct": 75.7, "incident_volume": 2806}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Daytime + Enterprise Violations + Formal Citations + Low Drug",
            "behavioral_characteristics": ["Daytime", "Enterprise Violations", "Formal Citations", "Low Drug"],
            "summary": "Mid-year regulatory investigations with elevated summer evening activity (nighttime: 29.9%).",
            "metrics": {"nighttime_pct": 29.9, "weapon_presence_pct": 10.8, "physical_injury_pct": 0.2, "property_involvement_pct": 77.1, "incident_volume": 2805}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Daytime + Year-End Regulatory + Administrative Arrest + No Injury",
            "behavioral_characteristics": ["Daytime", "Year-End Regulatory", "Administrative Arrest", "No Injury"],
            "summary": "Year-end commercial compliance checks and enterprise sanctions with zero reported physical trauma.",
            "metrics": {"nighttime_pct": 25.2, "weapon_presence_pct": 11.1, "physical_injury_pct": 0.0, "property_involvement_pct": 78.6, "incident_volume": 2485}
        }
    },
    6: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Daytime + Metropolitan Retail + Property involved + No Weapon",
            "behavioral_characteristics": ["Daytime", "Metropolitan Retail", "Property involved", "No Weapon"],
            "summary": "Dense urban retail shoplifting and grand larcenies in high-population core centers.",
            "metrics": {"nighttime_pct": 24.2, "weapon_presence_pct": 1.5, "physical_injury_pct": 1.4, "property_involvement_pct": 99.9, "incident_volume": 7554}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Daytime/Evening + Transit & Retail + Property involved + Low Weapon",
            "behavioral_characteristics": ["Daytime/Evening", "Transit & Retail", "Property involved", "Low Weapon"],
            "summary": "Elevated metropolitan pedestrian foot-traffic property thefts during summer tourism months.",
            "metrics": {"nighttime_pct": 25.8, "weapon_presence_pct": 2.3, "physical_injury_pct": 2.2, "property_involvement_pct": 99.9, "incident_volume": 9051}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Daytime + Commercial Holiday Surge + High Property Target + No Weapon",
            "behavioral_characteristics": ["Daytime", "Commercial Holiday Surge", "High Property Target", "No Weapon"],
            "summary": "Significant year-end commercial retail theft surge (+2.03% surge, Shift 03) peaking in October/December.",
            "metrics": {"nighttime_pct": 23.8, "weapon_presence_pct": 2.4, "physical_injury_pct": 2.4, "property_involvement_pct": 99.9, "incident_volume": 8937}
        }
    },
    7: {
        "early": {
            "period_label": "EARLY PERIOD",
            "time_range": "January – April (Winter / Early Months)",
            "behavioral_formula": "Daytime/Night + Street/Vehicle + Contraband Seizure + High Arrest",
            "behavioral_characteristics": ["Daytime/Night", "Street/Vehicle", "Contraband Seizure", "High Arrest"],
            "summary": "Targeted traffic and street stops seizing controlled substances with immediate on-scene arrests.",
            "metrics": {"nighttime_pct": 29.7, "weapon_presence_pct": 4.1, "physical_injury_pct": 0.3, "property_involvement_pct": 100.0, "incident_volume": 5875}
        },
        "middle": {
            "period_label": "MIDDLE PERIOD",
            "time_range": "May – August (Late Spring / Peak Summer)",
            "behavioral_formula": "Nocturnal Contraband + Active Seizures + On-Scene Arrest + No Weapon",
            "behavioral_characteristics": ["Nocturnal Contraband", "Active Seizures", "On-Scene Arrest", "No Weapon"],
            "summary": "Summer peak in nocturnal narcotics interdictions (nighttime rate rises to 32.1%).",
            "metrics": {"nighttime_pct": 32.1, "weapon_presence_pct": 3.2, "physical_injury_pct": 0.3, "property_involvement_pct": 100.0, "incident_volume": 6164}
        },
        "later": {
            "period_label": "LATER PERIOD",
            "time_range": "September – December (Fall / Year-End Holiday)",
            "behavioral_formula": "Evening Enforcement + Contraband Operations + High Arrest + Unarmed",
            "behavioral_characteristics": ["Evening Enforcement", "Contraband Operations", "High Arrest", "Unarmed"],
            "summary": "Steady late-year contraband interdictions characterized by zero injury rates and high apprehension rates.",
            "metrics": {"nighttime_pct": 30.5, "weapon_presence_pct": 3.0, "physical_injury_pct": 0.3, "property_involvement_pct": 100.0, "incident_volume": 5648}
        }
    }
}


class BehavioralEvolutionService:
    """
    Synthesizes historical behavioral evolution timelines for query incidents
    grounded in empirical Phase 8 longitudinal metrics.
    """

    def __init__(self):
        pass

    def build_evolution_timeline(
        self,
        input_data: Dict[str, Any],
        cl_id: int,
        cl_name: str,
        state: Any
    ) -> Dict[str, Any]:
        """
        Builds the 3-stage chronological evolution timeline for the identified pattern.

        Args:
            input_data: Raw input parameters for the query incident.
            cl_id: Assigned cluster identifier (0-7).
            cl_name: Name of the assigned cluster archetype.
            state: ApplicationState holding preloaded models and Phase 8 shifts.

        Returns:
            Structured evolution timeline response.
        """
        # Ensure cl_id is within bounds
        cl_id = max(0, min(7, int(cl_id)))
        period_data = EMPIRICAL_CLUSTER_PERIODS.get(cl_id, EMPIRICAL_CLUSTER_PERIODS[3])
        archetype = CLUSTER_ARCHETYPES.get(cl_id, {})
        archetype_name = archetype.get("name", cl_name)

        # 1. Construct the 3 stages: EARLY, MIDDLE, LATER
        stages = [
            {
                "stage_id": "early",
                "period_label": period_data["early"]["period_label"],
                "time_range": period_data["early"]["time_range"],
                "behavioral_formula": period_data["early"]["behavioral_formula"],
                "behavioral_characteristics": period_data["early"]["behavioral_characteristics"],
                "summary": period_data["early"]["summary"],
                "metrics": period_data["early"]["metrics"]
            },
            {
                "stage_id": "middle",
                "period_label": period_data["middle"]["period_label"],
                "time_range": period_data["middle"]["time_range"],
                "behavioral_formula": period_data["middle"]["behavioral_formula"],
                "behavioral_characteristics": period_data["middle"]["behavioral_characteristics"],
                "summary": period_data["middle"]["summary"],
                "metrics": period_data["middle"]["metrics"]
            },
            {
                "stage_id": "later",
                "period_label": period_data["later"]["period_label"],
                "time_range": period_data["later"]["time_range"],
                "behavioral_formula": period_data["later"]["behavioral_formula"],
                "behavioral_characteristics": period_data["later"]["behavioral_characteristics"],
                "summary": period_data["later"]["summary"],
                "metrics": period_data["later"]["metrics"]
            }
        ]

        # Safely parse month and hour for backward compatibility
        month = 7
        if input_data.get("incident_month") is not None:
            try:
                month = int(input_data["incident_month"])
            except (ValueError, TypeError):
                month = 7
        elif input_data.get("incident_date"):
            try:
                parts = str(input_data["incident_date"]).split("-")
                if len(parts) >= 2:
                    month = int(parts[1])
            except (ValueError, TypeError):
                month = 7

        hour = 14
        if input_data.get("incident_hour") is not None:
            try:
                hour = int(input_data["incident_hour"])
            except (ValueError, TypeError):
                hour = 14
        elif input_data.get("incident_time"):
            try:
                parts = str(input_data["incident_time"]).split(":")
                if len(parts) >= 1:
                    hour = int(parts[0])
            except (ValueError, TypeError):
                hour = 14

        is_night = bool(input_data.get("is_night") or (hour >= 20 or hour < 6))
        q_idx = max(0, min(3, (month - 1) // 3))
        q_names = ["Winter", "Spring", "Summer", "Fall"]
        calendar_quarter = f"Q{q_idx + 1} ({q_names[q_idx]})"

        # 2. Extract aligned Phase 8 statistical shifts
        aligned_shifts = []
        for shift in getattr(state, "significant_shifts", []):
            shift_title = shift.get("title", "")
            # Correlate shift with pattern
            if cl_id == 1 and "Cluster 1" in shift_title:
                aligned_shifts.append(shift)
            elif cl_id == 6 and "Cluster 6" in shift_title:
                aligned_shifts.append(shift)
            elif "Nocturnal" in shift_title and is_night:
                aligned_shifts.append(shift)
            elif "Arrest" in shift_title and input_data.get("has_arrest"):
                aligned_shifts.append(shift)

        # 3. Approved natural phrasing
        interpretation = "Behavioral characteristics changed over the observed historical period."
        dataset_time_span = "12-Month Historical Observation Period (January – December)"

        ethical_advisory = (
            "Based on patterns learned from historical incidents. "
            "CRIME DNA analyzes behavioral patterns in historical incident data. "
            "Similarity or novelty does not establish offender identity, guilt, or causation. "
            "Behavioral evolution reflects aggregate population-level shifts across historical incidents over the observed time period. "
            "It does not track individual persons and does not indicate sequential actions by an individual offender."
        )

        return {
            "timeline_title": "Historical Behavioral Evolution Timeline",
            "pattern_identifier": f"CCP_{cl_id:02d}",
            "pattern_name": archetype_name,
            "dataset_time_span": dataset_time_span,
            "evolution_interpretation": interpretation,
            "timeline_stages": stages,
            "aligned_statistical_shifts": aligned_shifts,
            "aligned_shifts": aligned_shifts,
            "ethical_advisory": ethical_advisory,

            # Backwards-compatible fields preserved for existing consumers
            "calendar_month": month,
            "hour_of_day": hour,
            "calendar_quarter": calendar_quarter,
            "baseline_alignment_note": interpretation,
            "historical_longitudinal_context": (
                f"Incident operates within Cluster {cl_id} ({archetype_name}). Longitudinal tracking indicates "
                f"behavioral characteristics changed over the observed historical period."
            )
        }


# Global singleton instance
evolution_service = BehavioralEvolutionService()
