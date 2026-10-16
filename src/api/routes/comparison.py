"""
CRIME DNA — Behavioral DNA Comparison API Endpoints

Provides endpoints for comparing Incident A vs Incident B:
- Newly entered incidents
- Selected historical incidents
- A combination of both
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas import (
    DnaComparisonRequest,
    DnaComparisonResponse,
    IncidentComparisonSpec
)
from src.services.comparison_service import comparison_service
from src.api.state import state

logger = logging.getLogger("CRIME_DNA_COMPARISON_ROUTE")

router = APIRouter(prefix="/compare", tags=["CRIME DNA Comparison"])


@router.post("", response_model=DnaComparisonResponse)
def compare_incidents(payload: DnaComparisonRequest) -> DnaComparisonResponse:
    """
    Compares two incidents (Incident A vs Incident B) using their 70D Behavioral DNA vectors.
    Computes exact side-by-side feature matching, DNA similarity, matching/differing
    characteristics, and 'What Changed?' behavioral transition analysis.
    """
    try:
        inc_a_dict = payload.incident_a.model_dump()
        inc_b_dict = payload.incident_b.model_dump()

        result = comparison_service.compare(
            incident_a=inc_a_dict,
            incident_b=inc_b_dict,
            state=state
        )
        return DnaComparisonResponse(**result)
    except ValueError as ve:
        logger.warning(f"Validation error comparing incidents: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error comparing incidents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Incident comparison failed: {str(e)}")


@router.get("/presets")
def get_comparison_presets() -> Dict[str, Any]:
    """
    Returns demonstrative comparison presets covering:
    1. Newly Entered vs Newly Entered (Theft vs Burglary Escalation)
    2. Newly Entered vs Historical Incident
    3. Historical Incident vs Historical Incident
    """
    return {
        "presets": [
            {
                "id": "preset_theft_vs_burglary",
                "title": "Unarmed Residential Theft vs Armed Residential Burglary",
                "description": "Compares an unarmed theft against an armed nighttime burglary with handgun escalation.",
                "incident_a": {
                    "label": "Incident A (Daytime Residential Theft)",
                    "input_data": {
                        "scenario_title": "Unarmed Residential Theft",
                        "incident_date": "2024-04-12",
                        "incident_time": "14:30",
                        "crime_category": "theft",
                        "location_type": "residential",
                        "is_weekend": False,
                        "has_property": True,
                        "property_value": 1200.0,
                        "has_weapon": False,
                        "has_injury": False
                    }
                },
                "incident_b": {
                    "label": "Incident B (Night Residential Burglary)",
                    "input_data": {
                        "scenario_title": "Armed Residential Burglary",
                        "incident_date": "2024-04-18",
                        "incident_time": "02:15",
                        "crime_category": "burglary",
                        "location_type": "residential",
                        "is_weekend": True,
                        "has_property": True,
                        "property_value": 3500.0,
                        "has_weapon": True,
                        "weapon_count": 1,
                        "has_injury": False
                    }
                }
            },
            {
                "id": "preset_input_vs_historical",
                "title": "New User Incident vs Historical Anchor (INC_000001)",
                "description": "Evaluates a newly submitted commercial robbery against historical incident INC_000001.",
                "incident_a": {
                    "label": "New Commercial Robbery Input",
                    "input_data": {
                        "scenario_title": "Evening Store Robbery",
                        "incident_date": "2024-07-22",
                        "incident_time": "21:45",
                        "crime_category": "robbery",
                        "location_type": "commercial",
                        "is_weekend": True,
                        "has_property": True,
                        "property_value": 1800.0,
                        "has_weapon": True,
                        "weapon_count": 1,
                        "has_injury": False
                    }
                },
                "incident_b": {
                    "label": "Historical Reference INC_000001",
                    "incident_id": "INC_000001"
                }
            },
            {
                "id": "preset_historical_pair",
                "title": "Historical Incident Pair (INC_000001 vs INC_000002)",
                "description": "Direct comparison between two indexed historical incidents.",
                "incident_a": {
                    "label": "Historical Incident INC_000001",
                    "incident_id": "INC_000001"
                },
                "incident_b": {
                    "label": "Historical Incident INC_000002",
                    "incident_id": "INC_000002"
                }
            }
        ],
        "total_presets": 3
    }
