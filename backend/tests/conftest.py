"""Shared pytest fixtures. pytest loads this file by itself before running any test."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, text

from app import models  # noqa: F401  (importing it registers every table on SQLModel.metadata)
from app.core.config import settings

test_database_url = os.environ.get("TEST_DATABASE_URL")
if test_database_url:
    settings.DATABASE_URL = test_database_url
else:
    dev_url = make_url(settings.DATABASE_URL)
    settings.DATABASE_URL = dev_url.set(
        database=f"{dev_url.database}_test"
    ).render_as_string(hide_password=False)

from app.core.db import engine  # noqa: E402
from app.main import app  # noqa: E402

if engine.url.database is None or not engine.url.database.endswith("_test"):
    raise RuntimeError(
        f"Tests must use a database ending in _test, not {engine.url.database}"
    )


@pytest.fixture(scope="session", autouse=True)
def create_tables() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def clean_tables() -> Generator[None]:
    yield
    table_names = ", ".join(
        f'"{table.name}"' for table in SQLModel.metadata.sorted_tables
    )
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture
def db() -> Generator[Session]:
    """A session for tests that read or write rows directly."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def client() -> Generator[TestClient]:
    """A test client that sends requests straight to the app, with no real server running."""
    with TestClient(app) as test_client:
        yield test_client
