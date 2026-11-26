"""Reads a pasted pathofexile.com trade2 search link back into a league and a search."""

import base64
import binascii
import gzip
import json
import logging
import zlib
from typing import Any, get_args
from urllib.parse import parse_qs, unquote, urlsplit

from sqlmodel import Session, col, select

from app.models import (
    Mod,
    ModFilter,
    ParsedTradeUrl,
    StatGroup,
    StatGroupType,
    StatusOption,
    TradeSearch,
)

logger = logging.getLogger(__name__)


def parse_trade_url(url: str, session: Session) -> ParsedTradeUrl:
    """Read a trade2 search link, with mod texts as labels, or raise ValueError."""
    league, query = read_trade_url(url)
    search = query_to_search(query)
    _add_mod_labels(search, session)
    return ParsedTradeUrl(league=league, search=search)


def read_trade_url(url: str) -> tuple[str, dict[str, Any]]:
    """Return the league and the search query in a trade2 search link."""
    parts = urlsplit(url.strip())
    segments = [unquote(segment) for segment in parts.path.split("/") if segment]
    if len(segments) < 4 or segments[:3] != ["trade2", "search", "poe2"]:
        raise ValueError("This is not a Path of Exile 2 trade search link")
    league = segments[3]
    q_values = parse_qs(parts.query).get("q")
    has_state = len(segments) >= 5 and segments[4].startswith("H4sI")
    if not q_values and not has_state:
        raise ValueError(
            "This link only points to a search saved on the trade site. "
            "Open it there, then copy the full link from the address bar"
        )
    try:
        data = json.loads(q_values[0]) if q_values else _decode_state(segments[4])
    except (binascii.Error, EOFError, zlib.error, json.JSONDecodeError) as error:
        logger.info("Could not decode a trade link", exc_info=True)
        raise ValueError("Could not read this trade link") from error
    query: dict[str, Any] = data.get("query", data)
    return league, query


def _decode_state(state: str) -> dict[str, Any]:
    """Decode an "H4sI..." path segment: JSON, gzip-compressed, then Base64url-encoded."""
    padded = state + "=" * (-len(state) % 4)
    data: dict[str, Any] = json.loads(gzip.decompress(base64.urlsafe_b64decode(padded)))
    return data


def query_to_search(query: dict[str, Any]) -> TradeSearch:
    """Pick out what a template stores. Each mod's label is its stat id for now."""
    filters: dict[str, Any] = query.get("filters") or {}
    type_filters = (filters.get("type_filters") or {}).get("filters") or {}
    trade_filters = (filters.get("trade_filters") or {}).get("filters") or {}
    category: dict[str, Any] = type_filters.get("category") or {}
    price: dict[str, Any] = trade_filters.get("price") or {}
    status: dict[str, Any] = query.get("status") or {}
    option: Any = status.get("option")
    return TradeSearch(
        category=category.get("option"),
        stat_groups=[
            _stat_group(group)
            for group in query.get("stats") or []
            if group.get("type") in get_args(StatGroupType)
            and not group.get("disabled")
        ],
        status_option=option if option in get_args(StatusOption) else "securable",
        max_price=price.get("max"),
        price_currency=price.get("option"),
    )


def _stat_group(group: dict[str, Any]) -> StatGroup:
    value = group.get("value") or {}
    return StatGroup(
        type=group["type"],
        min=value.get("min"),
        max=value.get("max"),
        mod_filters=[
            _mod_filter(stat_filter)
            for stat_filter in group.get("filters") or []
            if not stat_filter.get("disabled")
        ],
    )


def _mod_filter(stat_filter: dict[str, Any]) -> ModFilter:
    value = stat_filter.get("value") or {}
    return ModFilter(
        stat_id=stat_filter["id"],
        label=stat_filter["id"],
        min=value.get("min"),
        max=value.get("max"),
        weight=value.get("weight"),
    )


def _add_mod_labels(search: TradeSearch, session: Session) -> None:
    """Use the mod's text as the label for each mod that's in the mod table."""
    mod_filters = [
        mod_filter for group in search.stat_groups for mod_filter in group.mod_filters
    ]
    stat_ids = [mod_filter.stat_id for mod_filter in mod_filters]
    mods = session.exec(select(Mod).where(col(Mod.id).in_(stat_ids))).all()
    texts = {mod.id: mod.text for mod in mods}
    for mod_filter in mod_filters:
        mod_filter.label = texts.get(mod_filter.stat_id, mod_filter.label)
