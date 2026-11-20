import uuid
from datetime import UTC, datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=30)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserRegister(SQLModel):
    """What the sign-up form sends."""

    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=128)
    turnstile_token: str = ""

    @field_validator("username")
    @classmethod
    def lowercase_username(cls, value: str) -> str:
        """Save usernames in lowercase"""
        return value.lower()


class UserPublic(SQLModel):
    """What the API returns for a user."""

    id: uuid.UUID
    username: str
