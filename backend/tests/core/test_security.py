import uuid

import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    read_access_token,
    verify_password,
)


def test_verify_password_correct_password_returns_true() -> None:
    hashed = hash_password("correct horse")
    assert verify_password("correct horse", hashed)


def test_verify_password_wrong_password_returns_false() -> None:
    hashed = hash_password("correct horse")

    assert not verify_password("wrong horse", hashed)


def test_hash_password_same_password_gives_different_hashes() -> None:
    first = hash_password("correct horse")
    second = hash_password("correct horse")

    assert first != second
    assert "correct horse" not in first


def test_access_token_round_trip_returns_user_id() -> None:
    user_id = str(uuid.uuid4())

    token = create_access_token(user_id)

    assert read_access_token(token) == user_id


def test_read_access_token_garbage_returns_none() -> None:
    assert read_access_token("garbage") is None


def test_read_access_token_other_secret_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = create_access_token(str(uuid.uuid4()))

    monkeypatch.setattr(
        settings, "JWT_SECRET", "another-secret-of-32-or-more-characters"
    )

    assert read_access_token(token) is None


def test_read_access_token_expired_token_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "JWT_EXPIRE_DAYS", -1)

    token = create_access_token(str(uuid.uuid4()))

    assert read_access_token(token) is None
