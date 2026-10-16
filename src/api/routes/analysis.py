"""
CRIME DNA — Incident Input & Real-Time Behavioral Analysis Endpoints
"""

import logging
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, status, Header, Query
from src.api.schemas import (
    IncidentInputRequest,
    InputAnalysisResponse,
    ScenarioPreset,
    AnalysisRecord,
    AnalysisRecordListResponse
)
from src.services.analysis_engine import analysis_engine
from src.services.analysis_record_service import analysis_record_service
from src.api.exceptions import ModelNotLoadedError

logger = logging.getLogger("CRIME_DNA_ANALYSIS_ROUTE")

router = APIRouter(prefix="/analyze", tags=["Incident Input & Real-Time Behavioral Analysis"])

# Curated, realistic behavioral scenario presets for user testing
PRESETS: List[Dict[str, Any]] = [
    {
        "id": "armed_commercial_robbery",
        "title": "Armed Commercial Robbery",
        "description": "Multi-offender evening robbery with handguns at a convenience store in a mid-sized city.",
        "category": "Violent Property",
        "payload": {
            "scenario_title": "Armed Commercial Robbery Scenario",
            "incident_date": "2024-11-15",
            "incident_time": "21:45",
            "crime_category": "person_property",
            "is_attempted": False,
            "offense_count": 2,
            "offense_categories_count": 2,
            "population_setting": "mid_sized_city",
            "location_count": 1,
            "has_weapon": True,
            "weapon_count": 2,
            "weapon_types_count": 1,
            "has_criminal_activity": True,
            "criminal_activity_count": 1,
            "has_relationship": False,
            "victim_count": 2,
            "victim_avg_age": 34.0,
            "victim_sexes_count": 2,
            "offender_count": 2,
            "offender_avg_age": 22.0,
            "offender_sexes_count": 1,
            "has_property": True,
            "has_stolen_property": True,
            "property_value": 3500.0,
            "is_cargo_theft": False,
            "has_injury": True,
            "injury_record_count": 1,
            "has_drug": False,
            "has_bias_motivation": False,
            "has_arrest": False,
            "arrest_count": 0
        }
    },
    {
        "id": "nocturnal_residential_burglary",
        "title": "Nocturnal Residential Burglary",
        "description": "Late-night forced entry into an unoccupied suburban dwelling with electronics and jewelry stolen.",
        "category": "Property",
        "payload": {
            "scenario_title": "Nocturnal Residential Burglary Case",
            "incident_date": "2024-10-04",
            "incident_time": "02:30",
            "crime_category": "property",
            "is_attempted": False,
            "offense_count": 1,
            "offense_categories_count": 1,
            "population_setting": "small_city",
            "location_count": 1,
            "has_weapon": False,
            "weapon_count": 0,
            "weapon_types_count": 0,
            "has_criminal_activity": False,
            "criminal_activity_count": 0,
            "has_relationship": False,
            "victim_count": 1,
            "victim_avg_age": 48.0,
            "victim_sexes_count": 1,
            "offender_count": 1,
            "offender_avg_age": 26.0,
            "offender_sexes_count": 1,
            "has_property": True,
            "has_stolen_property": True,
            "property_value": 7200.0,
            "is_cargo_theft": False,
            "has_injury": False,
            "injury_record_count": 0,
            "has_drug": False,
            "has_bias_motivation": False,
            "has_arrest": False,
            "arrest_count": 0
        }
    },
    {
        "id": "domestic_interpersonal_assault",
        "title": "Interpersonal Domestic Assault",
        "description": "Weekend late-night interpersonal dispute between domestic partners with physical injury and on-scene arrest.",
        "category": "Person / Violent",
        "payload": {
            "scenario_title": "Interpersonal Domestic Dispute",
            "incident_date": "2024-07-20",
            "incident_time": "23:15",
            "crime_category": "person",
            "is_attempted": False,
            "offense_count": 1,
            "offense_categories_count": 1,
            "population_setting": "mid_sized_city",
            "location_count": 1,
            "has_weapon": False,
            "weapon_count": 0,
            "weapon_types_count": 0,
            "has_criminal_activity": False,
            "criminal_activity_count": 0,
            "has_relationship": True,
            "victim_count": 1,
            "victim_avg_age": 32.0,
            "victim_sexes_count": 1,
            "offender_count": 1,
            "offender_avg_age": 35.0,
            "offender_sexes_count": 1,
            "has_property": False,
            "has_stolen_property": False,
            "property_value": 0.0,
            "is_cargo_theft": False,
            "has_injury": True,
            "injury_record_count": 1,
            "has_drug": True,
            "suspected_drug_count": 1,
            "has_bias_motivation": False,
            "has_arrest": True,
            "arrest_count": 1
        }
    },
    {
        "id": "metropolitan_retail_theft",
        "title": "Metropolitan Retail Shoplifting",
        "description": "Daytime retail theft of apparel from a high-density shopping venue in a major urban center.",
        "category": "Property",
        "payload": {
            "scenario_title": "Metropolitan Retail Shoplifting Case",
            "incident_date": "2024-05-14",
            "incident_time": "15:20",
            "crime_category": "property",
            "is_attempted": False,
            "offense_count": 1,
            "offense_categories_count": 1,
            "population_setting": "metropolitan_core",
            "location_count": 1,
            "has_weapon": False,
            "weapon_count": 0,
            "weapon_types_count": 0,
            "has_criminal_activity": False,
            "criminal_activity_count": 0,
            "has_relationship": False,
            "victim_count": 1,
            "victim_avg_age": 40.0,
            "victim_sexes_count": 1,
            "offender_count": 1,
            "offender_avg_age": 21.0,
            "offender_sexes_count": 1,
            "has_property": True,
            "has_stolen_property": True,
            "property_value": 850.0,
            "is_cargo_theft": False,
            "has_injury": False,
            "injury_record_count": 0,
            "has_drug": False,
            "has_bias_motivation": False,
            "has_arrest": True,
            "arrest_count": 1
        }
    }
]


@router.get(
    "/presets",
    response_model=List[ScenarioPreset],
    summary="Get Realistic Scenario Presets",
    description="Returns preconfigured, realistic crime scenarios grounded in the behavioral dataset for rapid demonstration and validation."
)
async def get_scenario_presets():
    return PRESETS


@router.post(
    "",
    response_model=InputAnalysisResponse,
    summary="Analyze Incident with CRIME DNA",
    description="Encodes a user-submitted incident into a unit L2-normalized 70D Behavioral DNA vector and coordinates real-time evaluation across all 8 intelligence perspectives."
)
@router.post(
    "/input",
    response_model=InputAnalysisResponse,
    summary="Analyze Incident Input with CRIME DNA (Alias)",
    description="Encodes a user-submitted incident into a unit L2-normalized 70D Behavioral DNA vector and coordinates real-time evaluation across all 8 intelligence perspectives."
)
async def analyze_incident_input(
    request: IncidentInputRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    try:
        # Pydantic v2 model_dump with fallback to dict
        data = request.model_dump() if hasattr(request, "model_dump") else request.dict()
        effective_user_id = request.user_id or x_user_id or x_session_id or "user_anon"
        result = analysis_engine.analyze(data, user_id=effective_user_id)
        return result
    except ModelNotLoadedError as mnle:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(mnle)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation failed for incident input: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Incident input analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Behavioral intelligence analysis engine encountered an unexpected error: {str(e)}"
        )


@router.get(
    "/records",
    response_model=AnalysisRecordListResponse,
    summary="List Clean Analysis Records",
    description="Retrieves a list of clean, privacy-preserving incident analysis records, optionally filtered by user ID, search query, or crime category."
)
async def list_analysis_records(
    user_id: Optional[str] = Query(None, description="Filter records by user or session ID"),
    search: Optional[str] = Query(None, description="Search by Analysis ID, scenario title, or pattern name"),
    category: Optional[str] = Query(None, description="Filter by crime category"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    effective_uid = user_id or x_user_id
    return analysis_record_service.list_records(
        user_id=effective_uid,
        search=search,
        category=category,
        limit=limit,
        offset=offset
    )


@router.get(
    "/records/{analysis_id}",
    response_model=AnalysisRecord,
    summary="Get Clean Analysis Record by ID",
    description="Retrieves an immutable, privacy-preserving analysis record by its unique Analysis ID."
)
async def get_analysis_record(analysis_id: str):
    record = analysis_record_service.get_record(analysis_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{analysis_id}' was not found."
        )
    return record


@router.delete(
    "/records/{analysis_id}",
    summary="Delete Clean Analysis Record",
    description="Deletes an immutable analysis record by its unique Analysis ID."
)
async def delete_analysis_record(
    analysis_id: str,
    user_id: Optional[str] = Query(None, description="Optional user ID check"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    effective_uid = user_id or x_user_id
    deleted = analysis_record_service.delete_record(analysis_id, user_id=effective_uid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{analysis_id}' was not found or could not be removed."
        )
    return {
        "status": "success",
        "analysis_id": analysis_id,
        "message": f"Analysis record '{analysis_id}' successfully removed from user history."
    }


# ============================================================================
# Clean Top-Level Analyses Router (/analyses & /analysis/{analysis_id})
# ============================================================================
analyses_router = APIRouter(tags=["Incident History & Analyses"])


@analyses_router.get(
    "/analyses",
    response_model=AnalysisRecordListResponse,
    summary="List User Incident Analyses",
    description="Retrieves a list of clean, privacy-preserving incident analysis records, optionally filtered by user ID, search query, or crime category."
)
async def list_analyses(
    user_id: Optional[str] = Query(None, description="Filter records by user or session ID"),
    search: Optional[str] = Query(None, description="Search by Analysis ID, scenario title, or pattern name"),
    category: Optional[str] = Query(None, description="Filter by crime category"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    effective_uid = user_id or x_user_id
    return analysis_record_service.list_records(
        user_id=effective_uid,
        search=search,
        category=category,
        limit=limit,
        offset=offset
    )


@analyses_router.get(
    "/analysis/{analysis_id}",
    response_model=AnalysisRecord,
    summary="Get Specific Incident Analysis by ID",
    description="Retrieves an immutable, privacy-preserving analysis record by its unique Analysis ID."
)
async def get_analysis_by_id(analysis_id: str):
    record = analysis_record_service.get_record(analysis_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{analysis_id}' was not found."
        )
    return record


@analyses_router.delete(
    "/analysis/{analysis_id}",
    summary="Delete Specific Incident Analysis",
    description="Deletes an immutable analysis record by its unique Analysis ID."
)
async def delete_analysis_by_id(
    analysis_id: str,
    user_id: Optional[str] = Query(None, description="Optional user ID check"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    effective_uid = user_id or x_user_id
    deleted = analysis_record_service.delete_record(analysis_id, user_id=effective_uid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{analysis_id}' was not found or could not be removed."
        )
    return {
        "status": "success",
        "analysis_id": analysis_id,
        "message": f"Analysis record '{analysis_id}' successfully removed from user history."
    }

