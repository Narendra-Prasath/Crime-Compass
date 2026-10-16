"""
CRIME DNA — Behavioral Similarity Explainability Endpoints
"""

from fastapi import APIRouter, Path
from src.api.schemas import (
    SimilarityExplanationResponse,
    ExplainRequest,
    GroupContributionItem,
    FeatureContributionItem,
    BehavioralGroupComparisonItem
)
from src.api.state import state
from src.api.exceptions import IncidentNotFoundError, ModelNotLoadedError

router = APIRouter(prefix="/explain", tags=["Similarity Explainability"])


def _run_explanation(inc1: str, inc2: str) -> SimilarityExplanationResponse:
    if state.explainer is None:
        raise ModelNotLoadedError("Behavioral Similarity Explainer")

    if state.get_incident_index(inc1) is None:
        raise IncidentNotFoundError(inc1)
    if state.get_incident_index(inc2) is None:
        raise IncidentNotFoundError(inc2)

    raw_res = state.explainer.explain_pair(inc1, inc2)

    comp_items = [
        BehavioralGroupComparisonItem(
            group_key=c["group_key"],
            group_name=c["group_name"],
            status=c["status"],
            indicator=c["indicator"],
            label=c["label"],
            raw_label=c.get("raw_label"),
            match_tier=c["match_tier"],
            similarity_score=c["similarity_score"],
            contribution_score=c["contribution_score"],
            share_percentage=c["share_percentage"],
            details=c.get("details")
        )
        for c in raw_res.get("behavioral_group_comparisons", [])
    ]

    group_items = [
        GroupContributionItem(
            group_key=g["group_key"],
            display_name=g["display_name"],
            absolute_contribution=g["absolute_contribution"],
            percentage_of_similarity=g["percentage_of_similarity"]
        )
        for g in raw_res.get("sorted_group_contributions", [])
    ]

    feature_items = [
        FeatureContributionItem(
            feature_name=f["feature_name"],
            contribution=f["contribution"],
            incident_1_value=f.get("incident_1_value", 0.0),
            incident_2_value=f.get("incident_2_value", 0.0),
            description=f.get("description")
        )
        for f in raw_res.get("top_contributing_features", [])
    ]

    return SimilarityExplanationResponse(
        incident_pair=raw_res["incident_pair"],
        similarity_score_pct=raw_res["similarity_score_pct"],
        cosine_similarity_raw=raw_res["cosine_similarity_raw"],
        plain_english_explanation=raw_res.get("plain_english_explanation"),
        behavioral_group_comparisons=comp_items,
        main_contributing_similarities=raw_res.get("main_contributing_similarities", []),
        differences=raw_res.get("differences", []),
        group_contributions=group_items,
        top_contributing_features=feature_items,
        formatted_text_summary=raw_res["formatted_text_summary"],
        disclaimer=(
            "Based on patterns learned from historical incidents. "
            "CRIME DNA analyzes behavioral patterns in historical incident data. "
            "Similarity or novelty does not establish offender identity, guilt, or causation. "
            "Explanations represent mathematical feature-space attribution without establishing causal relationships."
        )
    )


@router.get(
    "/{incident_id_1}/{incident_id_2}",
    response_model=SimilarityExplanationResponse,
    summary="Explain Similarity Between Two Incidents (GET)",
    description="Calculates exact group and feature contributions explaining WHY two incidents are considered behaviorally similar."
)
async def explain_pair_get(
    incident_id_1: str = Path(..., description="First incident identifier, e.g. 'INC_136975'"),
    incident_id_2: str = Path(..., description="Second incident identifier, e.g. 'INC_145291'")
) -> SimilarityExplanationResponse:
    return _run_explanation(incident_id_1, incident_id_2)


@router.post(
    "",
    response_model=SimilarityExplanationResponse,
    summary="Explain Similarity Between Two Incidents (POST)",
    description="Calculates exact group and feature contributions explaining WHY two incidents are considered behaviorally similar via POST payload."
)
async def explain_pair_post(payload: ExplainRequest) -> SimilarityExplanationResponse:
    return _run_explanation(payload.incident_id_1, payload.incident_id_2)
