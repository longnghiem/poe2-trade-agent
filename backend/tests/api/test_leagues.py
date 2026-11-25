import pytest
from fastapi.testclient import TestClient

from app.api.routes import leagues
from tests.utils import register_and_login

LEAGUES_URL = "/api/v1/leagues"


def test_leagues_returns_list(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(leagues, "get_leagues", lambda: ["Runes of Aldur", "Standard"])

    response = client.get(LEAGUES_URL, headers=register_and_login(client))

    assert response.status_code == 200
    assert response.json() == ["Runes of Aldur", "Standard"]


def test_leagues_without_token_returns_401(client: TestClient) -> None:
    response = client.get(LEAGUES_URL)

    assert response.status_code == 401
