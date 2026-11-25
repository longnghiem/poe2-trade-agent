from typing import Literal

from sqlmodel import Field, SQLModel

StatusOption = Literal["available", "securable", "online", "any"]


class ModFilter(SQLModel):
    """One mod condition, e.g. explicit.stat_3299347043 (# to maximum Life), at least 200."""

    stat_id: str = Field(max_length=100)
    label: str = Field(max_length=300)
    min: float | None = None
    max: float | None = None


class TradeSearch(SQLModel):
    """Everything needed to build a trade-site search, except the league."""

    category: str | None = Field(default=None, max_length=50)
    filters: list[ModFilter] = Field(default_factory=list)
    status_option: StatusOption = "securable"
    max_price: float | None = None
    price_currency: str | None = Field(default=None, max_length=30)
