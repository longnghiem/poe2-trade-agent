import json
from typing import Any
from urllib.parse import quote

from app.models import StatGroup, TradeSearch

TRADE_SEARCH_URL = "https://www.pathofexile.com/trade2/search/poe2"


def build_trade_request(search: TradeSearch) -> dict[str, Any]:
    """Return the JSON that the trade site expects in ?q=."""
    return {
        "query": {
            "status": {"option": search.status_option},
            "stats": [_stat_group(group) for group in search.stat_groups],
            "filters": _item_filters(search),
        },
        "sort": {"price": "asc"},
    }


def _stat_group(group: StatGroup) -> dict[str, Any]:
    """One group: its type, its min and max, and its mods, without empty values."""
    stat_filters: list[dict[str, Any]] = []
    for mod_filter in group.mod_filters:
        value = mod_filter.model_dump(
            include={"min", "max", "weight"}, exclude_none=True
        )
        stat_filters.append({"id": mod_filter.stat_id, "value": value})
    return {
        "type": group.type,
        "value": group.model_dump(include={"min", "max"}, exclude_none=True),
        "filters": stat_filters,
    }


def _item_filters(search: TradeSearch) -> dict[str, Any]:
    """The category and price filters; a filter without a value is left out."""
    filters: dict[str, Any] = {}
    if search.category:
        filters["type_filters"] = {"filters": {"category": {"option": search.category}}}
    if search.max_price is not None:
        price: dict[str, Any] = {"max": search.max_price}
        if search.price_currency:
            price["option"] = search.price_currency
        filters["trade_filters"] = {"filters": {"price": price}}
    return filters


def build_trade_url(league: str, search: TradeSearch) -> str:
    request_json = json.dumps(build_trade_request(search), separators=(",", ":"))
    return (
        f"{TRADE_SEARCH_URL}/{quote(league, safe='')}?q={quote(request_json, safe='')}"
    )
