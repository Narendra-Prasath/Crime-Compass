"""
CRIME DNA — Phase 11: API Custom Exceptions and Handlers

Provides structured error handling for the FastAPI application.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("CRIME_DNA_API")


class CrimeDNAException(Exception):
    """Base exception for CRIME DNA API."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class IncidentNotFoundError(CrimeDNAException):
    """Raised when an incident ID does not exist in the index or dataset."""
    def __init__(self, incident_id: str):
        super().__init__(
            message=f"Incident '{incident_id}' not found in the Crime Compass database.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ClusterNotFoundError(CrimeDNAException):
    """Raised when a requested cluster ID does not exist."""
    def __init__(self, cluster_id: int):
        super().__init__(
            message=f"Cluster '{cluster_id}' not found. Available clusters are 0 through 7.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class PatternNotFoundError(CrimeDNAException):
    """Raised when a requested cross-crime pattern ID does not exist."""
    def __init__(self, pattern_id: str):
        super().__init__(
            message=f"Cross-crime pattern '{pattern_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidVectorError(CrimeDNAException):
    """Raised when a submitted vector does not meet expected dimensionality or bounds."""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=422
        )


class ModelNotLoadedError(CrimeDNAException):
    """Raised when an ML model artifact is required but failed to load at startup."""
    def __init__(self, model_name: str):
        super().__init__(
            message=f"Required ML component '{model_name}' is not ready or loaded.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


async def crime_dna_exception_handler(request: Request, exc: CrimeDNAException) -> JSONResponse:
    """Standard exception handler for CrimeDNAException instances."""
    logger.warning(f"Handled application exception on {request.url.path}: {exc.message} (Status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.message,
            "status_code": exc.status_code
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for uncaught server exceptions."""
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "An internal server error occurred while processing the request.",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )
