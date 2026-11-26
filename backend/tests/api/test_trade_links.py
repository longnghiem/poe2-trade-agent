from fastapi.testclient import TestClient

from app.models import TradeSearch
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
