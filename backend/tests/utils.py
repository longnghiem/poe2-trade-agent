"""Helpers shared by the API tests."""

from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient, username: str = "exile", password: str = "long enough"
) -> dict[str, str]:
    """Create a user, log in, and return the header that authenticates as them."""
    client.post(
        "/api/v1/auth/register", json={"username": username, "password": password}
    )
    response = client.post(
        "/api/v1/auth/login", data={"username": username, "password": password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
