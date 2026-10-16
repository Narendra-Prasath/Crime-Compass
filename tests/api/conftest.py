"""
CRIME DNA — Phase 11: API Test Fixtures
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="session")
def client():
    """
    Session-scoped TestClient to initialize FastAPI application state once
    and reuse across all API test modules.
    """
    with TestClient(app) as test_client:
        yield test_client
