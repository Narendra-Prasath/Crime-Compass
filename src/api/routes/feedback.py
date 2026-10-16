"""
CRIME DNA — Human-In-The-Loop Investigator Feedback Endpoints
"""

from fastapi import APIRouter, HTTPException
from src.api.schemas import (
    InvestigatorFeedbackPayload,
    InvestigatorFeedbackResponse,
    FeedbackSummaryResponse
)
from src.services.feedback_service import feedback_service

router = APIRouter(prefix="/feedback", tags=["Investigator Feedback"])


@router.post(
    "",
    response_model=InvestigatorFeedbackResponse,
    summary="Submit Human-in-the-Loop Feedback",
    description=(
        "Records evaluation feedback from an investigator on whether a behavioral match was useful, "
        "and which behavioral dimensions (time, location, property, method, other) were relevant. "
        "Stored strictly as evaluation and validation data; not used for automatic model retraining."
    )
)
async def submit_feedback(payload: InvestigatorFeedbackPayload) -> InvestigatorFeedbackResponse:
    try:
        res = feedback_service.record_feedback(
            is_useful=payload.is_useful,
            target_type=payload.target_type,
            target_id=payload.target_id,
            useful_aspects=payload.useful_aspects,
            notes=payload.notes
        )
        return InvestigatorFeedbackResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


@router.get(
    "/summary",
    response_model=FeedbackSummaryResponse,
    summary="Get Evaluation Feedback Summary",
    description="Returns aggregate statistics on investigator feedback utility rates and aspect breakdowns."
)
async def get_feedback_summary() -> FeedbackSummaryResponse:
    try:
        summary = feedback_service.get_feedback_summary()
        return FeedbackSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback summary: {str(e)}")
