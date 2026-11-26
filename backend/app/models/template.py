import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.trade import TradeSearch


def utc_now() -> datetime:
    return datetime.now(UTC)


class Template(SQLModel, table=True):
    """A user's saved trade search."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=100)
    folder: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list, sa_type=JSONB)
    category: str | None = Field(default=None, max_length=50)
    stat_groups: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSONB)
    status_option: str = Field(default="securable", max_length=20)
    max_price: float | None = None
    price_currency: str | None = Field(default=None, max_length=30)
    is_public: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TemplateIn(TradeSearch):
    """What the client sends to create or replace a template."""

    name: str = Field(min_length=1, max_length=100)
    folder: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list)
    is_public: bool = False


class TemplatePublic(TemplateIn):
    """What the API returns for a template."""

    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
