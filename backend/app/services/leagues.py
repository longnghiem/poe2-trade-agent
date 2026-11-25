import logging
import time
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

LEAGUES_URL = "https://poe.ninja/poe2/api/economy/leagues"
CACHE_SECONDS = 60 * 60


@dataclass
class LeagueCache:
    """The league names from the last successful request, kept while the server runs."""

    leagues: list[str] = field(default_factory=list)
    fetched_at: float = 0.0


cache = LeagueCache()


def get_leagues() -> list[str]:
    """Return the league names, asking poe.ninja at most once an hour."""
    if cache.leagues and time.monotonic() - cache.fetched_at < CACHE_SECONDS:
        return cache.leagues
    try:
        response = httpx.get(LEAGUES_URL, timeout=5)
        response.raise_for_status()
        cache.leagues = [league["name"] for league in response.json()]
        cache.fetched_at = time.monotonic()
        logger.info("Loaded %d leagues from poe.ninja", len(cache.leagues))
    except httpx.HTTPError, KeyError, TypeError, ValueError:
        logger.warning("Could not refresh leagues from poe.ninja", exc_info=True)
    return cache.leagues
