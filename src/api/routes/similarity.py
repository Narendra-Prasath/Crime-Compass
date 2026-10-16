"""
CRIME DNA — Behavioral Similarity Endpoints
"""

from typing import Optional, List
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Path, Query, HTTPException, status
from src.api.schemas import (
    SimilarIncidentsResponse,
    SimilarIncidentMatch,
    SimilarityQueryRequest,
    VectorSimilarityQueryRequest,
    VectorSimilarIncidentsResponse
)
from src.api.state import state
from src.api.exceptions import IncidentNotFoundError, InvalidVectorError, ModelNotLoadedError
from src.api.config import DEFAULT_TOP_K, MAX_TOP_K

router = APIRouter(prefix="/similarity", tags=["Behavioral Similarity Engine"])


from src.models.similarity.engine import (
    normalize_category_for_matching,
    extract_relevant_behavioral_characteristics
)


def _enrich_matches(matches: List[dict], query_category: Optional[str] = None) -> List[SimilarIncidentMatch]:
    """Helper to attach cluster name, crime category, cross-crime indicators, and behavioral traits to matches."""
    enriched = []
    norm_query_cat = normalize_category_for_matching(query_category) if query_category else None

    for m in matches:
        inc_id = m["incident_id"]
        profile = state.get_incident_profile(inc_id)
        ctx = profile.get("context", {}) if profile else {}
        crime_cat = ctx.get("primary_crime_category", "Unknown Offense")
        cluster_name = profile["cluster"]["cluster_name"] if profile else None

        # Cross-crime evaluation
        norm_match_cat = normalize_category_for_matching(crime_cat)
        is_cross = bool(norm_query_cat and (norm_query_cat != norm_match_cat))
        category_rel = "Different Crime Category" if is_cross else "Same Crime Category"
        cross_indicator = (
            f"⚡ Cross-Crime Match: Shares behavioral characteristics with {crime_cat}"
            if is_cross else None
        )

        traits = extract_relevant_behavioral_characteristics(ctx)
        sim_pct = float(m["similarity_score_pct"])

        enriched.append(SimilarIncidentMatch(
            rank=m["rank"],
            incident_id=inc_id,
            similarity_score_pct=sim_pct,
            similarity=f"{sim_pct:.1f}%",
            cosine_distance=m["cosine_distance"],
            subprofile_similarity_pct=m.get("subprofile_similarity_pct"),
            primary_crime_category=crime_cat,
            crime_category=crime_cat,
            cluster_name=cluster_name,
            is_cross_crime_match=is_cross,
            category_relationship=category_rel,
            cross_crime_indicator=cross_indicator,
            relevant_behavioral_characteristics=traits
        ))
    return enriched


@router.get(
    "/similar/{incident_id}",
    response_model=SimilarIncidentsResponse,
    summary="Find Behaviorally Similar Incidents (GET)",
    description="Retrieves the top K nearest incidents in 70-dimensional Behavioral DNA space, excluding the query incident itself."
)
@router.get(
    "/{incident_id}",
    response_model=SimilarIncidentsResponse,
    summary="Find Behaviorally Similar Incidents (Alias)",
    include_in_schema=False
)
async def get_similar_incidents(
    incident_id: str = Path(..., description="Query incident identifier, e.g. 'INC_136975'"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=MAX_TOP_K, description="Number of similar incidents to return"),
    include_breakdown: bool = Query(True, description="Whether to include 7-group subprofile similarity percentages")
) -> SimilarIncidentsResponse:
    if state.similarity_engine is None:
        raise ModelNotLoadedError("Behavioral Similarity Engine")

    if state.get_incident_index(incident_id) is None:
        raise IncidentNotFoundError(incident_id)

    res = state.similarity_engine.find_similar(
        incident_id=incident_id,
        top_k=top_k,
        include_breakdown=include_breakdown
    )

    query_profile = state.get_incident_profile(incident_id)
    query_cat = query_profile.get("context", {}).get("primary_crime_category") if query_profile else None

    enriched_matches = _enrich_matches(res["matches"], query_category=query_cat)
    has_cross = any(bool(m.is_cross_crime_match) for m in enriched_matches)
    cross_indicator = (
        "Similar behavioral characteristics were found across different crime categories."
        if has_cross else "All similar incidents belong to the same statutory category."
    )

    grouped = {
        "same_crime_category": [m for m in enriched_matches if not m.is_cross_crime_match],
        "different_crime_categories": [m for m in enriched_matches if m.is_cross_crime_match]
    }

    return SimilarIncidentsResponse(
        query_incident_id=res["query_incident_id"],
        top_k_requested=res["top_k_requested"],
        total_matches_returned=len(enriched_matches),
        cross_crime_indicator=cross_indicator,
        has_cross_crime_matches=has_cross,
        matches=enriched_matches,
        grouped_by_category_relationship=grouped
    )


@router.post(
    "/search",
    response_model=SimilarIncidentsResponse,
    summary="Find Behaviorally Similar Incidents (POST)",
    description="Retrieves the top K nearest incidents via POST request payload."
)
async def post_search_similar(payload: SimilarityQueryRequest) -> SimilarIncidentsResponse:
    return await get_similar_incidents(
        incident_id=payload.incident_id,
        top_k=payload.top_k,
        include_breakdown=payload.include_breakdown
    )


@router.post(
    "/vector",
    response_model=VectorSimilarIncidentsResponse,
    summary="Query Nearest Incidents by Arbitrary Behavioral DNA Vector",
    description="Allows querying the index using an arbitrary 70-dimensional Behavioral DNA vector."
)
async def post_search_by_vector(payload: VectorSimilarityQueryRequest) -> VectorSimilarIncidentsResponse:
    if state.similarity_engine is None or state.similarity_engine.model is None:
        raise ModelNotLoadedError("Behavioral Similarity Engine")

    vec = np.array(payload.vector, dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0.0 or np.isnan(norm):
        raise InvalidVectorError("Input vector norm is zero or contains NaNs; cannot normalize.")

    vec_norm = (vec / norm).reshape(1, -1)

    distances, indices = state.similarity_engine.model.kneighbors(
        vec_norm,
        n_neighbors=payload.top_k
    )

    matches = []
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0]), start=1):
        matched_id = state.incident_ids[idx]
        sim_pct = round(max(0.0, min(100.0, (1.0 - float(dist)) * 100.0)), 2)
        matches.append({
            "rank": rank,
            "incident_id": matched_id,
            "similarity_score_pct": sim_pct,
            "cosine_distance": round(float(dist), 6)
        })

    enriched = _enrich_matches(matches)
    has_cross = any(bool(m.is_cross_crime_match) for m in enriched)
    cross_indicator = (
        "Similar behavioral characteristics were found across different crime categories."
        if has_cross else "All similar incidents belong to the same statutory category."
    )

    grouped = {
        "same_crime_category": [m for m in enriched if not m.is_cross_crime_match],
        "different_crime_categories": [m for m in enriched if m.is_cross_crime_match]
    }

    return VectorSimilarIncidentsResponse(
        top_k_requested=payload.top_k,
        total_matches_returned=len(enriched),
        cross_crime_indicator=cross_indicator,
        has_cross_crime_matches=has_cross,
        matches=enriched,
        grouped_by_category_relationship=grouped
    )
