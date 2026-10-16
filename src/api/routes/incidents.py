"""
CRIME DNA — Incident Lookup and Behavioral DNA Endpoints
"""

from fastapi import APIRouter, Path
from src.api.schemas import IncidentProfileResponse, BehavioralDNAResponse
from src.api.state import state
from src.api.exceptions import IncidentNotFoundError

router = APIRouter(prefix="/incidents", tags=["Incidents & Behavioral DNA"])


@router.get(
    "/{incident_id}",
    response_model=IncidentProfileResponse,
    summary="Incident Profile Lookup",
    description="Fetches full contextual profile, assigned behavioral cluster, and novelty assessment for an incident."
)
async def get_incident(
    incident_id: str = Path(..., description="Unique incident identifier, e.g. 'INC_136975'")
) -> IncidentProfileResponse:
    profile = state.get_incident_profile(incident_id)
    if profile is None:
        raise IncidentNotFoundError(incident_id)

    return IncidentProfileResponse(**profile)


@router.get(
    "/{incident_id}/dna",
    response_model=BehavioralDNAResponse,
    summary="Incident Behavioral DNA Fingerprint",
    description="Fetches the 70-dimensional normalized Behavioral DNA vector, sub-profile group energies, and top active traits."
)
async def get_incident_dna(
    incident_id: str = Path(..., description="Unique incident identifier, e.g. 'INC_136975'")
) -> BehavioralDNAResponse:
    dna = state.get_incident_dna(incident_id)
    if dna is None:
        raise IncidentNotFoundError(incident_id)

    return BehavioralDNAResponse(**dna)
