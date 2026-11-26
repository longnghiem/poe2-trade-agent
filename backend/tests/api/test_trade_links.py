from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Mod, ModFilter, StatGroup, TradeSearch
from app.services.trade_link import build_trade_url
from tests.utils import register_and_login

TRADE_LINKS_URL = "/api/v1/trade-links"


def test_trade_links_returns_url(client: TestClient) -> None:
    response = client.post(
        TRADE_LINKS_URL,
        json={"league": "Standard", "search": {"category": "armour.chest"}},
        headers=register_and_login(client),
    )

    assert response.status_code == 200
    expected = build_trade_url("Standard", TradeSearch(category="armour.chest"))
    assert response.json() == {"url": expected}


def test_trade_links_without_token_returns_401(client: TestClient) -> None:
    response = client.post(TRADE_LINKS_URL, json={"league": "Standard", "search": {}})

    assert response.status_code == 401


def test_parse_trade_link_uses_mod_labels(client: TestClient, db: Session) -> None:
    db.add(Mod(id="explicit.stat_1", text="# to maximum Life", source="explicit"))
    db.commit()
    search = TradeSearch(
        stat_groups=[
            StatGroup(
                mod_filters=[
                    ModFilter(stat_id="explicit.stat_1", label="old", min=200),
                    ModFilter(stat_id="explicit.stat_2", label="old"),
                ]
            )
        ]
    )

    response = client.post(
        f"{TRADE_LINKS_URL}/parse",
        json={"url": build_trade_url("Standard", search)},
        headers=register_and_login(client),
    )

    assert response.status_code == 200
    assert response.json()["league"] == "Standard"
    [group] = response.json()["search"]["stat_groups"]
    labels = [mod_filter["label"] for mod_filter in group["mod_filters"]]
    assert labels == ["# to maximum Life", "explicit.stat_2"]


def test_parse_trade_link_bad_link_returns_400(client: TestClient) -> None:
    response = client.post(
        f"{TRADE_LINKS_URL}/parse",
        json={"url": "https://example.com"},
        headers=register_and_login(client),
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "This is not a Path of Exile 2 trade search link"
    }


def test_parse_trade_link_without_token_returns_401(client: TestClient) -> None:
    response = client.post(f"{TRADE_LINKS_URL}/parse", json={"url": "x"})

    assert response.status_code == 401
