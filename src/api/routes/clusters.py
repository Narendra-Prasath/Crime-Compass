"""
CRIME DNA — Unsupervised Behavioral Clustering Endpoints
"""

from fastapi import APIRouter, Path
from src.api.schemas import (
    ClustersListResponse,
    ClusterSummaryItem,
    ClusterDetailResponse,
    ClusterDistinctiveFeature
)
from src.api.state import state
from src.api.exceptions import ClusterNotFoundError

router = APIRouter(prefix="/clusters", tags=["Behavioral Clusters"])


@router.get(
    "",
    response_model=ClustersListResponse,
    summary="List All Behavioral Clusters",
    description="Returns high-level summaries for all 8 discovered unsupervised behavioral clusters."
)
async def list_clusters() -> ClustersListResponse:
    summaries = []
    for cid_str in sorted(state.cluster_profiles.keys(), key=lambda x: int(x)):
        p = state.cluster_profiles[cid_str]
        summaries.append(ClusterSummaryItem(
            cluster_id=int(p["cluster_id"]),
            name=p["name"],
            macro_category=p["macro_category"],
            summary=p["summary"],
            incident_count=p["incident_count"],
            percentage_of_total=p["percentage_of_total"]
        ))

    return ClustersListResponse(
        total_clusters=len(summaries),
        clusters=summaries
    )


@router.get(
    "/explore",
    summary="Explore Discovered Behavioral Patterns (Cards Format)",
    description="Returns clean pattern cards for all 8 discovered behavioral patterns."
)
async def explore_clusters():
    from src.services.pattern_exploration_service import pattern_exploration_service
    return pattern_exploration_service.get_all_pattern_cards(state)


@router.get(

    "/{cluster_id}",
    response_model=ClusterDetailResponse,
    summary="Get Cluster Behavioral Profile",
    description="Retrieves the detailed behavioral profile, dominant patterns, and top distinctive features for a cluster."
)
async def get_cluster_detail(
    cluster_id: int = Path(..., ge=0, le=7, description="Cluster identifier (0-7)")
) -> ClusterDetailResponse:
    cid_str = str(cluster_id)
    if cid_str not in state.cluster_profiles:
        raise ClusterNotFoundError(cluster_id)

    p = state.cluster_profiles[cid_str]
    distinctive = [
        ClusterDistinctiveFeature(
            feature=f["feature"],
            cluster_mean=f["cluster_mean"],
            global_mean=f["global_mean"],
            difference=f["difference"]
        )
        for f in p.get("top_distinctive_features", [])
    ]

    return ClusterDetailResponse(
        cluster_id=int(p["cluster_id"]),
        name=p["name"],
        macro_category=p["macro_category"],
        summary=p["summary"],
        incident_count=p["incident_count"],
        percentage_of_total=p["percentage_of_total"],
        dominant_patterns=p.get("dominant_patterns", {}),
        top_distinctive_features=distinctive
    )
