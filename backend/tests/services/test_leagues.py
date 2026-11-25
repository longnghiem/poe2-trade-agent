import time

import httpx
import pytest

from app.services import leagues
from app.services.leagues import LEAGUES_URL, LeagueCache, get_leagues

REQUEST = httpx.Request("GET", LEAGUES_URL)
GOOD_ANSWER = httpx.Response(
    200,
    json=[
        {"id": "Runes of Aldur", "name": "Runes of Aldur"},
        {"id": "Standard", "name": "Standard"},
    ],
    request=REQUEST,
)


@pytest.fixture(autouse=True)
def empty_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test with nothing cached."""
    monkeypatch.setattr(leagues, "cache", LeagueCache())


def fake_poe_ninja(monkeypatch: pytest.MonkeyPatch, answer: httpx.Response) -> None:
    """Make httpx.get return this answer instead of calling poe.ninja."""
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: answer)


def test_get_leagues_returns_names_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_poe_ninja(monkeypatch, GOOD_ANSWER)

    assert get_leagues() == ["Runes of Aldur", "Standard"]


def test_get_leagues_within_an_hour_uses_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_poe_ninja(monkeypatch, GOOD_ANSWER)
    get_leagues()
    monkeypatch.setattr(
        httpx, "get", lambda *args, **kwargs: pytest.fail("poe.ninja was called")
    )

    assert get_leagues() == ["Runes of Aldur", "Standard"]


def test_get_leagues_after_an_hour_asks_again(monkeypatch: pytest.MonkeyPatch) -> None:
    old_cache = LeagueCache(["Old League"], time.monotonic() - 60 * 60 - 1)
    monkeypatch.setattr(leagues, "cache", old_cache)
    fake_poe_ninja(monkeypatch, GOOD_ANSWER)

    assert get_leagues() == ["Runes of Aldur", "Standard"]


@pytest.mark.parametrize(
    "answer",
    [
        httpx.Response(503, json=[{"name": "Wrong"}], request=REQUEST),
        httpx.Response(200, text="<html>Blocked</html>", request=REQUEST),
        httpx.Response(200, json=[{"title": "Standard"}], request=REQUEST),
        httpx.Response(200, json=[None], request=REQUEST),
    ],
)
def test_get_leagues_bad_answer_returns_old_list_and_logs(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    answer: httpx.Response,
) -> None:
    old_cache = LeagueCache(["Old League"], time.monotonic() - 60 * 60 - 1)
    monkeypatch.setattr(leagues, "cache", old_cache)
    fake_poe_ninja(monkeypatch, answer)

    assert get_leagues() == ["Old League"]
    assert "Could not refresh leagues" in caplog.text


def test_get_leagues_unreachable_and_nothing_cached_returns_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def poe_ninja_unreachable(*_args: object, **_kwargs: object) -> httpx.Response:
        raise httpx.ConnectError("poe.ninja is unreachable")

    monkeypatch.setattr(httpx, "get", poe_ninja_unreachable)

    assert get_leagues() == []
