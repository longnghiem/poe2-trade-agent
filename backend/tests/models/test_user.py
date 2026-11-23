from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import User, UserPublic, UserRegister


def test_user_register_valid_input_is_accepted() -> None:
    body = UserRegister(username="exile", password="long enough")

    assert body.username == "exile"
    assert body.turnstile_token == ""


def test_user_register_mixed_case_username_is_lowercased() -> None:
    body = UserRegister(username="ExileBob", password="long enough")

    assert body.username == "exilebob"


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("ab", "long enough"),  # username too short
        ("a" * 31, "long enough"),  # username too long
        ("exile", "short"),  # password too short
    ],
)
def test_user_register_invalid_input_is_rejected(username: str, password: str) -> None:
    with pytest.raises(ValidationError):
        UserRegister(username=username, password=password)


def test_user_public_from_user_has_no_password_hash() -> None:
    user = User(username="exile", hashed_password="secret-hash")

    public = UserPublic.model_validate(user)

    assert public.model_dump() == {"id": user.id, "username": "exile"}


def test_user_saved_and_loaded_keeps_values(db: Session) -> None:
    db.add(User(username="exile", hashed_password="secret-hash"))
    db.commit()

    user = db.exec(select(User).where(User.username == "exile")).one()

    assert user.hashed_password == "secret-hash"
    assert user.created_at.tzinfo is not None
    assert datetime.now(UTC) - user.created_at < timedelta(minutes=1)


def test_user_duplicate_username_is_rejected(db: Session) -> None:
    db.add(User(username="exile", hashed_password="hash-1"))
    db.commit()

    db.add(User(username="exile", hashed_password="hash-2"))
    with pytest.raises(IntegrityError, match="duplicate key|unique"):
        db.commit()
    db.rollback()
