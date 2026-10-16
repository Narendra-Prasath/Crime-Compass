"""
CRIME DNA — Cross-Crime Behavioral Pattern Endpoints
"""

from fastapi import APIRouter, Path
from src.api.schemas import (
    CrossCrimeListResponse,
    CrossCrimePatternSummary,
    CrossCrimePatternDetailResponse,
    CategoryRepresentation,
    ExemplarIncident
)
from src.api.state import state
from src.api.exceptions import PatternNotFoundError

router = APIRouter(prefix="/cross-crime", tags=["Cross-Crime Behavioral Patterns"])


@router.get(
    "",
    response_model=CrossCrimeListResponse,
    summary="List All Cross-Crime Patterns",
    description="Returns high-level summaries for all 8 discovered cross-crime behavioral patterns."
)
async def list_cross_crime_patterns() -> CrossCrimeListResponse:
    summaries = []
    for pid in sorted(state.cross_crime_patterns.keys()):
        p = state.cross_crime_patterns[pid]
        categories = [
            CategoryRepresentation(
                category_name=c["category_name"],
                incident_count=c["incident_count"],
                percentage=c["percentage"]
            )
            for c in p.get("categories_represented", [])
        ]
        summaries.append(CrossCrimePatternSummary(
            pattern_id=p["pattern_id"],
            cluster_id=p["cluster_id"],
            pattern_name=p["pattern_name"],
            total_incidents=p["total_incidents"],
            categories_represented=categories
        ))

    return CrossCrimeListResponse(
        total_patterns=len(summaries),
        patterns=summaries,
        summary_metrics=state.cross_crime_summary
    )


@router.get(
    "/connection-map",
    summary="Get Behavioral Connection Map Graph",
    description="Returns computed graph topology of Crime Categories and Behavioral Patterns."
)
async def get_cross_crime_connection_map():
    from src.services.behavioral_graph_service import behavioral_graph_service
    return behavioral_graph_service.get_connection_map(state=state)


@router.get(
    "/{pattern_id}",
    response_model=CrossCrimePatternDetailResponse,
    summary="Get Cross-Crime Pattern Details",
    description="Retrieves full behavioral characteristics, inter-category similarities, exemplar triads, and evidence for a cross-crime pattern."
)
async def get_cross_crime_detail(
    pattern_id: str = Path(..., description="Pattern identifier, e.g. 'CCP_00'")
) -> CrossCrimePatternDetailResponse:
    pid_upper = pattern_id.upper()
    if pid_upper not in state.cross_crime_patterns:
        raise PatternNotFoundError(pattern_id)

    p = state.cross_crime_patterns[pid_upper]

    categories = [
        CategoryRepresentation(
            category_name=c["category_name"],
            incident_count=c["incident_count"],
            percentage=c["percentage"]
        )
        for c in p.get("categories_represented", [])
    ]

    exemplars = [
        ExemplarIncident(
            incident_id=e["incident_id"],
            crime_category=e["crime_category"],
            category_description=e["category_description"],
            behavioral_highlights=e.get("behavioral_highlights", {})
        )
        for e in p.get("exemplar_incidents", [])
    ]

    return CrossCrimePatternDetailResponse(
        pattern_id=p["pattern_id"],
        cluster_id=p["cluster_id"],
        pattern_name=p["pattern_name"],
        total_incidents=p["total_incidents"],
        categories_represented=categories,
        dominant_behavioral_characteristics=p.get("dominant_behavioral_characteristics", {}),
        inter_category_similarities=p.get("inter_category_similarities", {}),
        exemplar_incidents=exemplars,
        exemplar_pairwise_similarities=p.get("exemplar_pairwise_similarities", []),
        cross_crime_evidence=p.get("cross_crime_evidence", {})
    )
