"""Shared pytest fixtures. pytest loads this file by itself before running any test."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client() -> Generator[TestClient]:
    """A test client that sends requests straight to the app, with no real server running."""
    with TestClient(app) as test_client:
        yield test_client