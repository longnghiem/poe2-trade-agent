import json
from urllib.parse import parse_qs, urlsplit

from app.models import ModFilter, StatGroup, TradeSearch
from app.services.trade_link import build_trade_request, build_trade_url

BODY_ARMOUR = TradeSearch(
    category="armour.chest",
    stat_groups=[
        StatGroup(
            mod_filters=[
                ModFilter(
                    stat_id="pseudo.pseudo_total_life",
                    label="+# total maximum Life",
                    min=200,
                ),
                ModFilter(stat_id="explicit.stat_1", label="Other", min=1, max=5),
            ]
        ),
        StatGroup(
            type="count",
            min=2,
            mod_filters=[
                ModFilter(stat_id="explicit.stat_2", label="Cold", min=30),
                ModFilter(stat_id="explicit.stat_3", label="Fire", min=30),
            ],
        ),
        StatGroup(
            type="weight",
            min=100,
            mod_filters=[
                ModFilter(stat_id="explicit.stat_4", label="Life", weight=1.5)
            ],
        ),
    ],
    max_price=5,
    price_currency="divine",
)


def test_build_trade_request_full_search() -> None:
    assert build_trade_request(BODY_ARMOUR) == {
        "query": {
            "status": {"option": "securable"},
            "stats": [
                {
                    "type": "and",
                    "value": {},
                    "filters": [
                        {"id": "pseudo.pseudo_total_life", "value": {"min": 200}},
                        {"id": "explicit.stat_1", "value": {"min": 1, "max": 5}},
                    ],
                },
                {
                    "type": "count",
                    "value": {"min": 2},
                    "filters": [
                        {"id": "explicit.stat_2", "value": {"min": 30}},
                        {"id": "explicit.stat_3", "value": {"min": 30}},
                    ],
                },
                {
                    "type": "weight",
                    "value": {"min": 100},
                    "filters": [{"id": "explicit.stat_4", "value": {"weight": 1.5}}],
                },
            ],
            "filters": {
                "type_filters": {"filters": {"category": {"option": "armour.chest"}}},
                "trade_filters": {"filters": {"price": {"max": 5, "option": "divine"}}},
            },
        },
        "sort": {"price": "asc"},
    }


def test_build_trade_request_leaves_out_empty_values() -> None:
    doomsayer = ModFilter(
        stat_id="enchant.stat_2954116742|57190", label="Allocates Doomsayer"
    )

    query = build_trade_request(
        TradeSearch(stat_groups=[StatGroup(mod_filters=[doomsayer])])
    )["query"]

    assert query["stats"] == [
        {
            "type": "and",
            "value": {},
            "filters": [{"id": "enchant.stat_2954116742|57190", "value": {}}],
        }
    ]
    assert query["filters"] == {}


def test_build_trade_request_price_without_currency() -> None:
    query = build_trade_request(TradeSearch(max_price=5))["query"]

    assert query["filters"] == {"trade_filters": {"filters": {"price": {"max": 5}}}}


def test_build_trade_url_encodes_league_and_search() -> None:
    url = build_trade_url("Runes of Aldur", BODY_ARMOUR)

    assert url.startswith(
        "https://www.pathofexile.com/trade2/search/poe2/Runes%20of%20Aldur?q=%7B%22"
    )
    [q] = parse_qs(urlsplit(url).query)["q"]
    assert json.loads(q) == build_trade_request(BODY_ARMOUR)
