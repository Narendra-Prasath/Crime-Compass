"""
CRIME DNA — Explore Discovered Behavioral Patterns Endpoints

Provides clean, structured access to the 8 empirical behavioral patterns
discovered from the 220,663 incident historical dataset.
"""

from typing import Optional
from fastapi import APIRouter, Path, HTTPException, Query
from src.api.schemas import (
    ExplorePatternsResponse,
    PatternDetailViewResponse,
    BehavioralConnectionMapResponse
)
from src.api.state import state
from src.services.pattern_exploration_service import pattern_exploration_service

router = APIRouter(prefix="/patterns", tags=["Explore Patterns"])


@router.get(
    "",
    response_model=ExplorePatternsResponse,
    summary="Explore Discovered Behavioral Patterns",
    description=(
        "Returns clean, high-level pattern cards for all 8 behavioral archetypes "
        "discovered from the historical dataset (220,663 incidents). "
        "Each card shows concise behavioral formula, incident count, crime categories, "
        "time profile, and empirical strength."
    )
)
async def list_patterns() -> ExplorePatternsResponse:
    try:
        res = pattern_exploration_service.get_all_pattern_cards(state)
        return ExplorePatternsResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load patterns: {str(e)}")


@router.get(
    "/connection-map",
    response_model=BehavioralConnectionMapResponse,
    summary="Get Behavioral Connection Map Graph Topology",
    description=(
        "Returns the complete computed graph topology of Crime Categories and Behavioral Patterns. "
        "Connections represent shared behavioral characteristics discovered across the 220,663 incident corpus."
    )
)
async def get_connection_map(
    pattern_id: Optional[str] = Query(None, description="Optional pattern filter, e.g. '0', 'PATTERN 01', 'CCP_00'"),
    category: Optional[str] = Query(None, description="Optional crime category filter, e.g. 'property', 'violent'")
) -> BehavioralConnectionMapResponse:
    try:
        from src.services.behavioral_graph_service import behavioral_graph_service
        res = behavioral_graph_service.get_connection_map(
            state=state,
            filter_pattern_id=pattern_id,
            filter_category=category
        )
        return BehavioralConnectionMapResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate connection map: {str(e)}")


@router.get(
    "/{pattern_id}",
    response_model=PatternDetailViewResponse,
    summary="Get Detailed Behavioral Pattern Profile",
    description=(
        "Retrieves a comprehensive detail view for a specific pattern (by ID, index 0-7, or code CCP_00-07). "
        "Includes why this pattern exists, crime categories involved, behavioral characteristics, "
        "historical 3-stage evolution timeline, supporting evidence, and expandable analysis details."
    )
)
async def get_pattern_detail(
    pattern_id: str = Path(..., description="Pattern identifier, e.g. 'PATTERN 01', '0', 'CCP_00'")
) -> PatternDetailViewResponse:
    try:
        detail = pattern_exploration_service.get_pattern_detail(pattern_id, state)
        return PatternDetailViewResponse(**detail)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' could not be resolved: {str(e)}")


# ============================================================================
# Dedicated Direct Connection Map Router (/connection-map)
# ============================================================================
connection_map_router = APIRouter(tags=["Explore Patterns"])


@connection_map_router.get(
    "/connection-map",
    response_model=BehavioralConnectionMapResponse,
    summary="Get Behavioral Connection Map Graph Topology",
    description=(
        "Returns the complete computed graph topology of Crime Categories and Behavioral Patterns. "
        "Connections represent shared behavioral characteristics discovered across the 220,663 incident corpus."
    )
)
async def get_direct_connection_map(
    pattern_id: Optional[str] = Query(None, description="Optional pattern filter, e.g. '0', 'PATTERN 01', 'CCP_00'"),
    category: Optional[str] = Query(None, description="Optional crime category filter, e.g. 'property', 'violent'")
) -> BehavioralConnectionMapResponse:
    try:
        from src.services.behavioral_graph_service import behavioral_graph_service
        res = behavioral_graph_service.get_connection_map(
            state=state,
            filter_pattern_id=pattern_id,
            filter_category=category
        )
        return BehavioralConnectionMapResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate connection map: {str(e)}")

