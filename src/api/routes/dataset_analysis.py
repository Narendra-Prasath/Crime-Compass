"""
CRIME COMPASS 🧭 — Dataset Upload & Behavioral Analysis Routes

Provides endpoints for:
- POST /datasets/validate
- POST /datasets/analyze
- GET /datasets/analyses/{analysis_id}
- DELETE /datasets/analyses/{analysis_id}
- GET /datasets/analyses/{analysis_id}/export
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Query, Response, Request
from fastapi.responses import JSONResponse

from src.api.schemas import (
    DatasetValidationResponse,
    DatasetAnalyzeRequest,
    DatasetAnalysisResultResponse,
    DatasetDeleteResponse
)
from src.services.dataset_service import dataset_service

logger = logging.getLogger("CRIME_COMPASS_DATASET_ROUTES")

router = APIRouter(prefix="/datasets", tags=["Dataset Upload & Behavioral Analysis"])


@router.post(
    "/validate",
    response_model=DatasetValidationResponse,
    summary="Validate and preview an uploaded incident dataset (CSV)"
)
async def validate_dataset(request: Request) -> Any:
    """
    Validates an uploaded CSV dataset, checks headers, missingness, and duplicates,
    generates a 5-row preview, and automatically suggests column mappings to the 70D Behavioral DNA schema.
    """
    try:
        content: Optional[bytes] = None
        name = "dataset.csv"

        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            data = await request.json()
            raw_text = data.get("csv_text") or data.get("content") or ""
            content = raw_text.encode("utf-8")
            name = data.get("filename") or "dataset.csv"
        else:
            form = await request.form()
            file_upload = form.get("file")
            if file_upload and hasattr(file_upload, "read"):
                content = await file_upload.read()  # type: ignore
                name = getattr(file_upload, "filename", "dataset.csv") or "dataset.csv"
            else:
                raw_text = form.get("csv_text")
                if raw_text:
                    content = str(raw_text).encode("utf-8")
                    name = str(form.get("filename") or "dataset.csv")

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty or no CSV content provided. Please upload a valid CSV file."
            )

        result = dataset_service.validate_and_preview(content, name)
        return result
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error validating dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and validate dataset: {str(e)}"
        )


@router.post(
    "/analyze",
    response_model=DatasetAnalysisResultResponse,
    summary="Execute real behavioral intelligence analysis on an uploaded dataset"
)
async def analyze_dataset(request: Request) -> Any:
    """
    Executes real machine learning behavioral analysis on the mapped dataset:
    - Adaptive Spherical K-Means clustering (empirical dataset patterns)
    - Pairwise similarity comparisons with query self-exclusion
    - Cross-crime modus operandi pattern discovery
    - Location-specific insights & proportions
    - Temporal evolution & reporting disclaimers
    - Unusual behavioral combinations (distance to cluster centroids)
    - Optional comparison with Alabama 2024 historical reference baseline
    - Transparent 'Why These Results?' explanations & technical specifications
    """
    import json

    try:
        content: Optional[bytes] = None
        name = "dataset.csv"
        c_map: Dict[str, str] = {}
        s_scope: Dict[str, Any] = {}
        token: Optional[str] = None
        uid: Optional[str] = None

        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            body = await request.json()
            payload = DatasetAnalyzeRequest(**body)
            token = payload.file_token
            if payload.csv_text:
                content = payload.csv_text.encode("utf-8")
            name = payload.filename
            c_map = payload.column_mapping
            s_scope = payload.scope
            uid = payload.user_id
        else:
            form = await request.form()
            file_upload = form.get("file")
            if file_upload and hasattr(file_upload, "read"):
                content = await file_upload.read() # type: ignore
                name = getattr(file_upload, "filename", "dataset.csv") or "dataset.csv"
            
            token = form.get("file_token") # type: ignore
            raw_csv = form.get("csv_text") # type: ignore
            if raw_csv and not content:
                content = str(raw_csv).encode("utf-8")

            raw_mapping = form.get("column_mapping") or form.get("column_mapping_json")
            if raw_mapping:
                c_map = json.loads(str(raw_mapping))

            raw_scope = form.get("scope") or form.get("scope_json")
            if raw_scope:
                s_scope = json.loads(str(raw_scope))

            uid = form.get("user_id") # type: ignore

        if not content and not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide an uploaded file, file_token, or csv_text."
            )

        result = dataset_service.analyze_dataset(
            file_content=content,
            file_token=token,
            filename=name,
            column_mapping=c_map,
            scope=s_scope,
            user_id=uid
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error analyzing dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/analyses/{analysis_id}",
    response_model=DatasetAnalysisResultResponse,
    summary="Retrieve a completed dataset analysis by its unique ID"
)
async def get_dataset_analysis(analysis_id: str) -> Any:
    """Retrieves an isolated dataset analysis result by unique analysis_id."""
    result = dataset_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset analysis '{analysis_id}' was not found or has been deleted."
        )
    return result


@router.delete(
    "/analyses/{analysis_id}",
    response_model=DatasetDeleteResponse,
    summary="Securely delete an uploaded dataset analysis"
)
async def delete_dataset_analysis(analysis_id: str) -> Any:
    """Securely deletes an analysis result from memory and storage."""
    deleted = dataset_service.delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset analysis '{analysis_id}' was not found or already deleted."
        )
    return {
        "status": "success",
        "analysis_id": analysis_id,
        "deleted": True,
        "message": f"Dataset analysis '{analysis_id}' has been permanently and safely deleted."
    }


@router.get(
    "/analyses/{analysis_id}/export",
    summary="Export a dataset analysis summary in JSON or CSV format"
)
async def export_dataset_analysis(
    analysis_id: str,
    format: str = Query("json", pattern="^(json|csv)$")
) -> Any:
    """Exports dataset analysis in JSON or CSV format."""
    try:
        filename, media_type, file_bytes = dataset_service.export_analysis(analysis_id, format)
        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Error exporting analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/sample",
    summary="Download the synthetic sample Indian incident dataset (CSV)"
)
async def download_sample_dataset() -> Any:
    """Provides a synthetic sample CSV of Indian incidents for testing Crime Compass Mode 2."""
    try:
        filename, media_type, file_bytes = dataset_service.get_sample_dataset_bytes()
        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error serving sample dataset: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/template",
    summary="Download the Crime Compass column mapping template CSV"
)
async def download_mapping_template() -> Any:
    """Provides the standard column mapping template CSV."""
    try:
        filename, media_type, file_bytes = dataset_service.get_mapping_template_bytes()
        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Error serving template CSV: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

