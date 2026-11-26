import pytest

from app.models import ModFilter, StatGroup, TradeSearch
from app.services.trade_link import build_trade_url
from app.services.trade_url_parser import query_to_search, read_trade_url

# Copied from the trade site: life at least 200, and 2 of 3 resistances at least 30.
SITE_LINK = (
    "https://www.pathofexile.com/trade2/search/poe2/Runes%20of%20Aldur/"
    "H4sIAAAAAAAAA6WR22oDIRCG3-W_lrBRE1lfpYRgV9MK7gEdQ5bFdy8m5FCS0kLnao7fDP8sSGQoJ-gF"
    "40R-HKBhhhmFnSsJ-m0BzZM75y0YDj6Qi5eCt9Bwpyn4ztOqDuwFb1shVSMFGI4mZFfZvR-gedMUBuuT"
    "eQ_OQh9MSK7sClt-g0rOm4arlssnqHjFZK9PE4pvuORS_Yey3qq1UFvxV8qOXfXrxjzQsyqlttwEuKi9"
    "f4gf3M6Q-xjj_P1dsR9zXHWfLhFKKQwUjf0JMUXf3ZcPOQSG3pygN-yGrNlS7QvQcyvkHwIAAA"
)


def resistance(stat_id: str) -> ModFilter:
    return ModFilter(stat_id=stat_id, label=stat_id, min=30)


def test_read_trade_url_site_link() -> None:
    league, query = read_trade_url(SITE_LINK)

    assert league == "Runes of Aldur"
    assert query_to_search(query) == TradeSearch(
        category="armour.chest",
        stat_groups=[
            StatGroup(
                mod_filters=[
                    ModFilter(
                        stat_id="explicit.stat_3299347043",
                        label="explicit.stat_3299347043",
                        min=200,
                    )
                ]
            ),
            StatGroup(
                type="count",
                min=2,
                mod_filters=[
                    resistance("explicit.stat_4220027924"),
                    resistance("explicit.stat_3372524247"),
                    resistance("explicit.stat_1671376347"),
                ],
            ),
        ],
        status_option="any",
        max_price=5,
    )


def test_read_trade_url_reads_our_own_link() -> None:
    search = TradeSearch(
        category="armour.chest",
        stat_groups=[
            StatGroup(type="count", min=1, max=2, mod_filters=[resistance("a|1")]),
            StatGroup(
                type="weight",
                min=100,
                mod_filters=[ModFilter(stat_id="b", label="b", weight=1.5)],
            ),
        ],
        status_option="online",
        max_price=50,
        price_currency="exalted",
    )

    league, query = read_trade_url(build_trade_url("HC Runes of Aldur", search))

    assert league == "HC Runes of Aldur"
    assert query_to_search(query) == search


def test_query_to_search_skips_what_a_template_cannot_store() -> None:
    query = {
        "status": {"option": "sometimes"},
        "stats": [
            {"type": "and", "filters": [{"id": "a"}, {"id": "b", "disabled": True}]},
            {"type": "not", "filters": [{"id": "c"}]},
            {"type": "count", "disabled": True, "filters": [{"id": "d"}]},
        ],
    }

    assert query_to_search(query) == TradeSearch(
        stat_groups=[StatGroup(mod_filters=[ModFilter(stat_id="a", label="a")])]
    )


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("https://www.pathofexile.com/trade/search/Standard", "not a Path of Exile 2"),
        (
            "https://www.pathofexile.com/trade2/search/poe2/Standard/Ab3dE",
            "saved on the trade site",
        ),
        (SITE_LINK[:-20], "Could not read"),
        (
            "https://www.pathofexile.com/trade2/search/poe2/Standard?q={",
            "Could not read",
        ),
    ],
)
def test_read_trade_url_bad_link_is_rejected(url: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        read_trade_url(url)


def test_read_trade_url_broken_link_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(ValueError):
        read_trade_url(SITE_LINK[:-20])

    assert "Could not decode a trade link" in caplog.text
