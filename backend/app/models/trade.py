from typing import Literal

from sqlmodel import Field, SQLModel

# The trade site's "Instant Buyout and In Person", "Instant Buyout" and "Any"; its two
# "In Person" options are not offered.
StatusOption = Literal["available", "securable", "any"]
StatGroupType = Literal["and", "count", "weight"]


class ModFilter(SQLModel):
    """One mod condition, e.g. explicit.stat_3299347043 (# to maximum Life), at least 200."""

    stat_id: str = Field(max_length=100)
    label: str = Field(max_length=300)
    min: float | None = None
    max: float | None = None
    # How much this mod's value counts; only used in a "weight" group.
    weight: float | None = None


class StatGroup(SQLModel):
    """
    "and": every mod must match.
    "count": the number of mods that match must be between min and max.
    "weight": each mod's value times its weight, added up, must be between min and max.
    """

    type: StatGroupType = "and"
    min: float | None = None
    max: float | None = None
    mod_filters: list[ModFilter] = Field(default_factory=list)


class TradeSearch(SQLModel):
    """Everything needed to build a trade-site search, except the league."""

    category: str | None = Field(default=None, max_length=50)
    stat_groups: list[StatGroup] = Field(default_factory=list)
    status_option: StatusOption = "securable"
    max_price: float | None = None
    price_currency: str | None = Field(default=None, max_length=30)


class TradeLinkRequest(SQLModel):
    """A league and the search to open in it."""

    league: str = Field(min_length=1, max_length=100)
    search: TradeSearch


class TradeLinkResponse(SQLModel):
    """A link that opens the search on the official trade site."""

    url: str


class ParseTradeUrlRequest(SQLModel):
    """A trade-site search link that the user pasted."""

    url: str = Field(min_length=1, max_length=10000)


class ParsedTradeUrl(SQLModel):
    """The league and the search read from a pasted trade-site link."""

    league: str
    search: TradeSearch
