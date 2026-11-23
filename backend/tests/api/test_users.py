from fastapi.testclient import TestClient

from tests.utils import register_and_login

CURRENT_USER_URL = "/api/v1/users/current_user"


def test_users_current_user_with_token_returns_user(client: TestClient) -> None:
    headers = register_and_login(client, "exile")

    response = client.get(CURRENT_USER_URL, headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "exile"
    assert set(response.json()) == {"id", "username"}


def test_users_current_user_without_token_returns_401(client: TestClient) -> None:
    response = client.get(CURRENT_USER_URL)

    assert response.status_code == 401


def test_users_current_user_invalid_token_returns_401(client: TestClient) -> None:
    register_and_login(client, "exile")

    response = client.get(CURRENT_USER_URL, headers={"Authorization": "Bearer garbage"})

    assert response.status_code == 401
