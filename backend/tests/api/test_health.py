from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from app.api.deps import get_db
from app.main import app


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_database_down_returns_500() -> None:
    unreachable_engine = create_engine(
        "postgresql+psycopg://user:password@localhost:1/none"
    )

    def get_unreachable_db() -> Generator[Session]:
        with Session(unreachable_engine) as session:
            yield session

    app.dependency_overrides[get_db] = get_unreachable_db
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
