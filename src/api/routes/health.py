"""
CRIME DNA — Health and Readiness Endpoints
"""

import time
from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.api.state import state
from src.api.config import API_VERSION

router = APIRouter(tags=["System Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health and Readiness Probe",
    description="Returns API status, uptime, pre-loaded ML component statuses, and corpus dimensions."
)
async def get_health() -> HealthResponse:
    uptime = time.time() - state.startup_timestamp if state.startup_timestamp > 0 else 0.0
    all_online = all(v == "online" for v in state.components_status.values())
    status_str = "healthy" if (state.is_ready and all_online) else "degraded"

    return HealthResponse(
        status=status_str,
        api_version=API_VERSION,
        uptime_seconds=round(uptime, 2),
        components_status=state.components_status,
        indexed_incidents=len(state.incident_ids),
        vector_dimension=len(state.feature_names)
    )


@router.get(
    "/healthz",
    summary="Lightweight Liveness Probe",
    description="Immediate 200 OK probe for container orchestrators and load balancers."
)
async def healthz():
    return {"status": "ok", "ready": state.is_ready}
