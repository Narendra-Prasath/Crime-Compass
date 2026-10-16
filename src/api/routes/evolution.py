"""
CRIME DNA — Behavioral Evolution Endpoints
"""

from fastapi import APIRouter, Path, HTTPException
from src.api.schemas import (
    EvolutionTimelineResponse,
    ShiftsListResponse,
    SignificantShift,
    BehavioralEvolutionResult
)
from src.api.state import state
from src.services.evolution_service import evolution_service
from src.services.pattern_exploration_service import pattern_exploration_service
from src.models.clustering.config import CLUSTER_ARCHETYPES

router = APIRouter(prefix="/evolution", tags=["Behavioral Evolution"])


@router.get(
    "/timeline",
    response_model=EvolutionTimelineResponse,
    summary="Get Chronological Evolution Timeline",
    description="Returns temporal cluster distributions, feature trend trajectories, and detected behavioral shifts across chronological epochs."
)
async def get_evolution_timeline() -> EvolutionTimelineResponse:
    dashboard = state.timeline_dashboard

    shifts = [
        SignificantShift(**s)
        for s in state.significant_shifts
    ]

    return EvolutionTimelineResponse(
        metadata=dashboard.get("metadata", {}),
        cluster_timeline=dashboard.get("cluster_timeline", {}),
        feature_timeline=dashboard.get("feature_timeline", {}),
        significant_shifts=shifts
    )


@router.get(
    "/shifts",
    response_model=ShiftsListResponse,
    summary="List Significant Behavioral Shifts",
    description="Returns population-level behavioral shifts that exhibit statistically significant change over time."
)
async def get_significant_shifts() -> ShiftsListResponse:
    shifts = [
        SignificantShift(**s)
        for s in state.significant_shifts
    ]

    return ShiftsListResponse(
        total_shifts=len(shifts),
        shifts=shifts
    )


@router.get(
    "/{pattern_id}",
    response_model=BehavioralEvolutionResult,
    summary="Get Behavioral Pattern Evolution by Pattern ID",
    description=(
        "Returns how the specified behavioral pattern evolved across the historical observation period "
        "(Early, Middle, Later stages), including operational shifts, temporal windows, and longitudinal stability."
    )
)
async def get_pattern_evolution(
    pattern_id: str = Path(..., description="Pattern identifier, e.g. '0', 'CCP_00', 'PATTERN 01'")
) -> BehavioralEvolutionResult:
    try:
        cluster_id = pattern_exploration_service._resolve_cluster_id(pattern_id)
        archetype = CLUSTER_ARCHETYPES.get(cluster_id, {})
        archetype_name = archetype.get("name", f"Behavioral Cluster {cluster_id}")
        timeline = evolution_service.build_evolution_timeline(
            input_data={},
            cl_id=cluster_id,
            cl_name=archetype_name,
            state=state
        )
        return BehavioralEvolutionResult(**timeline)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Pattern evolution for '{pattern_id}' could not be resolved: {str(e)}"
        )
