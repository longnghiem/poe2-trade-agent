from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import read_access_token, verify_password
from app.models import User

REGISTER_URL = "/api/v1/auth/register"


def test_register_new_user_returns_201_with_public_data(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL, json={"username": "exile", "password": "long enough"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "exile"
    assert set(body) == {"id", "username"}


def test_register_new_user_saves_hashed_password(
    client: TestClient, db: Session
) -> None:
    client.post(REGISTER_URL, json={"username": "exile", "password": "long enough"})

    user = db.exec(select(User).where(User.username == "exile")).one()
    assert user.hashed_password != "long enough"
    assert verify_password("long enough", user.hashed_password)


def test_register_mixed_case_username_is_saved_lowercase(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL, json={"username": "ExileBob", "password": "long enough"}
    )

    assert response.json()["username"] == "exilebob"


def test_register_taken_username_returns_409(client: TestClient) -> None:
    client.post(REGISTER_URL, json={"username": "exile", "password": "long enough"})

    response = client.post(
        REGISTER_URL, json={"username": "exile", "password": "other password"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username is already taken"}


def test_register_taken_username_in_other_case_returns_409(
    client: TestClient,
) -> None:
    client.post(REGISTER_URL, json={"username": "exile", "password": "long enough"})

    response = client.post(
        REGISTER_URL, json={"username": "EXILE", "password": "long enough"}
    )

    assert response.status_code == 409


def test_register_short_password_returns_422(client: TestClient, db: Session) -> None:
    response = client.post(REGISTER_URL, json={"username": "exile", "password": "abc"})

    assert response.status_code == 422
    assert db.exec(select(User)).first() is None


LOGIN_URL = "/api/v1/auth/login"


def test_login_correct_password_returns_token(client: TestClient) -> None:
    client.post(REGISTER_URL, json={"username": "exile", "password": "long enough"})

    response = client.post(
        LOGIN_URL, data={"username": "exile", "password": "long enough"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert read_access_token(body["access_token"]) is not None


def test_login_mixed_case_username_returns_token(client: TestClient) -> None:
    client.post(REGISTER_URL, json={"username": "exile", "password": "long enough"})

    response = client.post(
        LOGIN_URL, data={"username": "Exile", "password": "long enough"}
    )

    assert response.status_code == 200


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    client.post(REGISTER_URL, json={"username": "exile", "password": "long enough"})

    response = client.post(
        LOGIN_URL, data={"username": "exile", "password": "wrong password"}
    )

    assert response.status_code == 401


def test_login_unknown_username_returns_401(client: TestClient) -> None:
    response = client.post(
        LOGIN_URL, data={"username": "nobody", "password": "long enough"}
    )

    assert response.status_code == 401
