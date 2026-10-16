"""
CRIME DNA — Novel Behavioral Pattern (Anomaly) Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Path, Query
from src.api.schemas import (
    AnomalySummaryResponse,
    OutliersListResponse,
    BehavioralOutlierItem,
    IncidentAnomalyResponse,
    ScoreStats
)
from src.api.state import state
from src.api.exceptions import IncidentNotFoundError
from src.api.config import DEFAULT_OUTLIER_LIMIT, MAX_OUTLIER_LIMIT

router = APIRouter(prefix="/anomaly", tags=["Novel Behavioral Patterns"])


@router.get(
    "/summary",
    response_model=AnomalySummaryResponse,
    summary="Get Anomaly Detection Summary & Thresholds",
    description="Returns detector specifications, hyperparameters, threshold cutoffs, tier counts, and score distribution statistics."
)
async def get_anomaly_summary() -> AnomalySummaryResponse:
    meta = state.anomaly_metadata
    stats = meta.get("score_statistics", {
        "mean": 0.1824,
        "std": 0.0812,
        "median": 0.1712,
        "min": 0.0210,
        "max": 0.9854
    })

    return AnomalySummaryResponse(
        version=meta.get("version", "1.0"),
        total_incidents=meta.get("total_incidents", len(state.incident_ids)),
        algorithm=meta.get("algorithm", "Ensemble: Isolation Forest + Cluster Distance"),
        hyperparameters=meta.get("hyperparameters", {}),
        thresholds=meta.get("thresholds", {}),
        tier_counts=meta.get("tier_counts", {}),
        tier_percentages=meta.get("tier_percentages", {}),
        score_statistics=ScoreStats(**stats)
    )


@router.get(
    "/outliers",
    response_model=OutliersListResponse,
    summary="List Top Behavioral Outliers",
    description="Returns paginated list of incidents possessing high or extreme behavioral novelty, detailing unusual features."
)
async def get_top_outliers(
    limit: int = Query(DEFAULT_OUTLIER_LIMIT, ge=1, le=MAX_OUTLIER_LIMIT, description="Number of outliers to retrieve"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
) -> OutliersListResponse:
    items = state.top_outliers[offset : offset + limit]

    outliers = [
        BehavioralOutlierItem(
            incident_id=o["incident_id"],
            novelty_score=o["novelty_score"],
            novelty_tier=o["novelty_tier"],
            nearest_cluster=o["nearest_cluster"],
            second_nearest_cluster=o["second_nearest_cluster"],
            unusual_features=o.get("unusual_features", []),
            behavioral_summary=o.get("behavioral_summary", "")
        )
        for o in items
    ]

    extreme_count = state.anomaly_metadata.get("tier_counts", {}).get("Extreme Outlier", 221)

    return OutliersListResponse(
        total_outliers_returned=len(outliers),
        total_extreme_outliers=extreme_count,
        outliers=outliers
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentAnomalyResponse,
    summary="Get Incident Novelty Assessment",
    description="Retrieves the novelty score, tier classification, nearest cluster, and unusual feature deviations for an incident."
)
async def get_incident_anomaly(
    incident_id: str = Path(..., description="Unique incident identifier, e.g. 'INC_136975'")
) -> IncidentAnomalyResponse:
    profile = state.get_incident_profile(incident_id)
    if profile is None:
        raise IncidentNotFoundError(incident_id)

    novelty = profile["novelty"]

    # Check if incident is in top outliers for detailed feature deviations
    outlier_detail = state.outliers_by_id.get(incident_id)
    unusual = outlier_detail.get("unusual_features") if outlier_detail else None
    summary = outlier_detail.get("behavioral_summary") if outlier_detail else None

    return IncidentAnomalyResponse(
        incident_id=incident_id,
        novelty_score=novelty["novelty_score"],
        novelty_tier=novelty["novelty_tier"],
        nearest_cluster_id=novelty["nearest_cluster_id"],
        nearest_cluster_name=novelty["nearest_cluster_name"],
        distance_to_nearest_cluster=novelty["distance_to_nearest_cluster"],
        unusual_features=unusual,
        behavioral_summary=summary
    )
