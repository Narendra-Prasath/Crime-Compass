"""
CRIME DNA — Phase 11: Production Backend FastAPI Application

Entrypoint for the CRIME DNA RESTful API.
Initializes application state, loads models at startup via lifespan,
configures CORS and middleware, registers exception handlers, and mounts routes.
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.config import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    WORKSPACE_ROOT,
    DEBUG
)
from src.api.state import state
from src.api.exceptions import CrimeDNAException, crime_dna_exception_handler, generic_exception_handler
from src.api.routes import (
    health,
    stats,
    incidents,
    similarity,
    clusters,
    cross_crime,
    evolution,
    anomaly,
    explain,
    analysis,
    comparison,
    patterns,
    feedback,
    dataset_analysis
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CRIME_DNA_API")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Loads all pre-trained ML models and registries into memory at startup,
    ensuring zero retraining and instantaneous API response times.
    """
    logger.info("Starting Crime Compass 🧭 API server...")
    t0 = time.time()
    try:
        state.load_all()
        logger.info(f"All ML components successfully loaded in {time.time() - t0:.3f}s.")
    except Exception as e:
        logger.critical(f"Critical error loading application state: {e}", exc_info=True)
    yield
    logger.info("Crime Compass 🧭 API server shutting down gracefully.")


# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Process time middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    logger.info(f"{request.method} {request.url.path} -> Status {response.status_code} ({process_time:.2f}ms)")
    return response


# SPA HTML direct navigation fallback middleware
@app.middleware("http")
async def spa_html_fallback_middleware(request: Request, call_next):
    """
    Ensures direct browser navigation to client-side SPA routes (e.g. /compare, /patterns,
    /connection-map, /history, /incident-analyzer) serves frontend index.html when Accept includes text/html.
    """
    if has_frontend and request.method == "GET":
        path = request.url.path
        if not (
            path.startswith("/api")
            or path.startswith("/assets")
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi.json")
            or path.startswith("/healthz")
        ):
            accept = request.headers.get("accept", "")
            if "text/html" in accept:
                candidate_file = frontend_dist / path.lstrip("/")
                if not (path.lstrip("/") and candidate_file.is_file()):
                    return FileResponse(frontend_dist / "index.html")

    return await call_next(request)


# Register Exception Handlers
# pyrefly: ignore [bad-argument-type]
app.add_exception_handler(CrimeDNAException, crime_dna_exception_handler)
if not DEBUG:
    app.add_exception_handler(Exception, generic_exception_handler)


def get_api_catalog() -> dict:
    """Returns top-level API metadata, documentation links, and canonical CRIME DNA product endpoints."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "online",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "openapi": "/openapi.json",
        "canonical_product_endpoints": {
            "health": "GET /health",
            "stats": "GET /stats",
            "analyze": "POST /analyze",
            "analysis_detail": "GET /analysis/{analysis_id}",
            "analyses_history": "GET /analyses",
            "patterns": "GET /patterns",
            "pattern_detail": "GET /patterns/{pattern_id}",
            "compare": "POST /compare",
            "evolution": "GET /evolution/{pattern_id}",
            "feedback": "POST /feedback",
            "connection_map": "GET /connection-map"
        },
        "backward_compatible_prefix": "/api",
        "endpoints": [
            "/health",
            "/healthz",
            "/stats",
            "/analyze",
            "/analysis/{analysis_id}",
            "/analyses",
            "/patterns",
            "/patterns/{pattern_id}",
            "/compare",
            "/evolution/{pattern_id}",
            "/feedback",
            "/connection-map",
            "/api/health",
            "/api/healthz",
            "/api/stats",
            "/api/analyze",
            "/api/analyze/input",
            "/api/analyze/presets",
            "/api/analysis/{analysis_id}",
            "/api/analyses",
            "/api/patterns",
            "/api/patterns/{pattern_id}",
            "/api/compare",
            "/api/compare/presets",
            "/api/evolution/{pattern_id}",
            "/api/evolution/timeline",
            "/api/evolution/shifts",
            "/api/feedback",
            "/api/feedback/summary",
            "/api/connection-map",
            "/api/patterns/connection-map",
            "/api/incidents/{incident_id}",
            "/api/incidents/{incident_id}/dna",
            "/api/similarity/similar/{incident_id}",
            "/api/similarity/search",
            "/api/similarity/vector",
            "/api/clusters",
            "/api/clusters/{cluster_id}",
            "/api/cross-crime",
            "/api/cross-crime/{pattern_id}",
            "/api/anomaly/summary",
            "/api/anomaly/outliers",
            "/api/anomaly/{incident_id}",
            "/api/explain/{incident_id_1}/{incident_id_2}",
            "/api/explain"
        ]
    }


# Check if pre-compiled frontend distribution is available
frontend_dist = WORKSPACE_ROOT / "frontend" / "dist"
has_frontend = frontend_dist.exists() and (frontend_dist / "index.html").exists()

@app.get("/api", tags=["Root"], include_in_schema=False)
async def api_root() -> JSONResponse:
    """Returns top-level API metadata and documentation links."""
    return JSONResponse(content=get_api_catalog())

@app.get("/", tags=["Root"])
async def root(request: Request):
    """Returns top-level API metadata, documentation links, or web UI based on Accept header."""
    accept = request.headers.get("accept", "")
    if has_frontend and "text/html" in accept:
        return FileResponse(frontend_dist / "index.html")
    return JSONResponse(content=get_api_catalog())



# ----------------------------------------------------------------------------
# 1. Register Canonical Clean Product Routers at Root
# ----------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(stats.router)
app.include_router(analysis.router)
app.include_router(analysis.analyses_router)
app.include_router(patterns.router)
app.include_router(patterns.connection_map_router)
app.include_router(comparison.router)
app.include_router(evolution.router)
app.include_router(feedback.router)
app.include_router(dataset_analysis.router)

# ----------------------------------------------------------------------------
# 2. Register Routers under /api (Preserving Full Backward Compatibility)
# ----------------------------------------------------------------------------
api_prefix = "/api"
app.include_router(health.router, prefix=api_prefix)
app.include_router(stats.router, prefix=api_prefix)
app.include_router(incidents.router, prefix=api_prefix)
app.include_router(similarity.router, prefix=api_prefix)
app.include_router(clusters.router, prefix=api_prefix)
app.include_router(cross_crime.router, prefix=api_prefix)
app.include_router(evolution.router, prefix=api_prefix)
app.include_router(anomaly.router, prefix=api_prefix)
app.include_router(explain.router, prefix=api_prefix)
app.include_router(analysis.router, prefix=api_prefix)
app.include_router(analysis.analyses_router, prefix=api_prefix)
app.include_router(comparison.router, prefix=api_prefix)
app.include_router(patterns.router, prefix=api_prefix)
app.include_router(patterns.connection_map_router, prefix=api_prefix)
app.include_router(feedback.router, prefix=api_prefix)
app.include_router(dataset_analysis.router, prefix=api_prefix)


# ----------------------------------------------------------------------------
# 3. Static Files & SPA Client Fallback (When frontend/dist is present)
# ----------------------------------------------------------------------------
if has_frontend:
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Do not intercept /api routes that weren't matched
        if full_path.startswith("api/") or full_path == "api":
            return JSONResponse(status_code=404, content={"detail": f"API endpoint /{full_path} not found."})

        # Return static file if directly requested (e.g. vite.svg, favicon.ico)
        candidate_file = frontend_dist / full_path
        if full_path and candidate_file.is_file():
            return FileResponse(candidate_file)

        # Fallback to index.html for client-side routing (/compare, /patterns, /history, etc.)
        return FileResponse(frontend_dist / "index.html")

