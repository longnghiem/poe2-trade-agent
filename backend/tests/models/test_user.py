import pytest
from pydantic import ValidationError

from app.models import User, UserPublic, UserRegister


def testUserRegister_ValidInput_IsAccepted() -> None:
    body = UserRegister(username="exile", password="long enough")

    assert body.username == "exile"
    assert body.turnstile_token == ""


def testUserRegister_MixedCaseUsername_IsLowercased() -> None:
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
def testUserRegister_InvalidInput_IsRejected(username: str, password: str) -> None:
    with pytest.raises(ValidationError):
        UserRegister(username=username, password=password)


def testUserPublic_FromUser_HasNoPasswordHash() -> None:
    user = User(username="exile", hashed_password="secret-hash")

    public = UserPublic.model_validate(user)

    assert public.model_dump() == {"id": user.id, "username": "exile"}
