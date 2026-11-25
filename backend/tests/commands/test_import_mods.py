import json

import httpx
import pytest
from sqlmodel import Session, select

from app.commands import import_mods as command
from app.models import Mod

LIFE_LINE = json.dumps(
    {
        "ref": "# to maximum Life",
        "trade": {
            "ids": {
                "explicit": ["explicit.stat_3299347043"],
                "implicit": ["implicit.stat_3299347043"],
            }
        },
    }
)
OFFICIAL_STATS = json.dumps(
    {
        "result": [
            {
                "id": "pseudo",
                "entries": [
                    {"id": "pseudo.pseudo_total_life", "text": "+# total maximum Life"}
                ],
            },
            {
                "id": "explicit",
                "entries": [
                    {"id": "explicit.stat_3299347043", "text": "# to maximum Life"}
                ],
            },
        ]
    }
)
NO_IDS_LINE = json.dumps({"ref": "Grants Skill: Parry", "trade": {"ids": None}})


def fake_download(monkeypatch: pytest.MonkeyPatch, status_code: int, text: str) -> None:
    """Make httpx.get answer from here instead of GitHub; STATS_URL gets this answer."""

    def fake_get(url: str, **_: object) -> httpx.Response:
        request = httpx.Request("GET", url)
        if url == command.OFFICIAL_STATS_URL:
            return httpx.Response(200, text=OFFICIAL_STATS, request=request)
        return httpx.Response(status_code, text=text, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)


def test_parse_stats_lines_returns_one_mod_per_trade_id() -> None:
    mods = command.parse_stats_lines([LIFE_LINE])

    assert [(mod.id, mod.text, mod.source) for mod in mods] == [
        ("explicit.stat_3299347043", "# to maximum Life", "explicit"),
        ("implicit.stat_3299347043", "# to maximum Life", "implicit"),
    ]


def test_parse_stats_lines_skips_lines_without_trade_ids() -> None:
    mods = command.parse_stats_lines([NO_IDS_LINE, LIFE_LINE])

    assert len(mods) == 2


def test_parse_stats_lines_removes_duplicate_ids() -> None:
    mods = command.parse_stats_lines([LIFE_LINE, LIFE_LINE])

    assert len(mods) == 2


def test_parse_stats_lines_skips_mods_with_a_choice() -> None:
    ids = {"enchant": ["enchant.stat_2954116742"]}
    line = json.dumps({"ref": "Allocates #", "trade": {"ids": ids, "option": True}})

    assert command.parse_stats_lines([line]) == []


def test_merge_official_stats_adds_missing_mod() -> None:
    official = {"enchant.stat_2954116742|57190": "Allocates Doomsayer"}

    [mod] = command.merge_official_stats([], official)

    assert mod.id == "enchant.stat_2954116742|57190"
    assert (mod.text, mod.source) == ("Allocates Doomsayer", "enchant")
    assert mod.position == 0


@pytest.mark.parametrize(
    ("official_text", "expected"),
    [
        ("# to Armour (Local)", "# to Armour (Local)"),
        ("# to Armour in your Maps", "# to Armour"),  # an older wording: keep ours
    ],
)
def test_merge_official_stats_takes_only_a_suffix(
    official_text: str, expected: str
) -> None:
    mods = [Mod(id="explicit.stat_1", text="# to Armour", source="explicit")]

    [mod] = command.merge_official_stats(mods, {"explicit.stat_1": official_text})

    assert mod.text == expected


def test_import_mods_replaces_old_rows(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    db.add(Mod(id="explicit.stat_old", text="Removed mod", source="explicit"))
    db.add(Mod(id="explicit.stat_3299347043", text="Old text", source="explicit"))
    db.commit()
    fake_download(monkeypatch, 200, LIFE_LINE)

    command.import_mods()

    mods = db.exec(select(Mod).order_by(Mod.id)).all()
    assert [(mod.id, mod.text, mod.position) for mod in mods] == [
        ("explicit.stat_3299347043", "# to maximum Life", 1),
        ("implicit.stat_3299347043", "# to maximum Life", None),
        ("pseudo.pseudo_total_life", "+# total maximum Life", 0),
    ]


@pytest.mark.parametrize(
    ("status_code", "text"),
    [
        (404, LIFE_LINE),  # the download fails
        # the database refuses a text over 300 characters
        (200, LIFE_LINE.replace("# to maximum Life", "x" * 301)),
    ],
)
def test_main_import_fails_logs_error_and_keeps_old_rows(
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    status_code: int,
    text: str,
) -> None:
    db.add(Mod(id="explicit.stat_old", text="Old mod", source="explicit"))
    db.commit()
    fake_download(monkeypatch, status_code, text)

    with pytest.raises(SystemExit) as error:
        command.main()

    assert error.value.code == 1
    assert "The import failed" in caplog.text
    assert len(db.exec(select(Mod)).all()) == 1
