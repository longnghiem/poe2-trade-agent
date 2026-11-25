from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Mod
from tests.utils import register_and_login

MODS_URL = "/api/v1/mods"


def add_mods(db: Session, *mods: tuple[str, str]) -> None:
    """Save one mod per (source, text) pair."""
    for number, (source, text) in enumerate(mods):
        db.add(Mod(id=f"{source}.stat_{number}", text=text, source=source))
    db.commit()


def search(client: TestClient, q: str) -> list[tuple[str, str]]:
    """Search as a logged-in user and return the (source, text) pairs, in order."""
    response = client.get(MODS_URL, params={"q": q}, headers=register_and_login(client))
    assert response.status_code == 200
    return [(mod["source"], mod["text"]) for mod in response.json()]


def test_search_mods_returns_public_data(client: TestClient, db: Session) -> None:
    add_mods(db, ("explicit", "# to maximum Life"))

    response = client.get(
        MODS_URL, params={"q": "life"}, headers=register_and_login(client)
    )

    assert response.status_code == 200
    assert response.json() == [
        {"id": "explicit.stat_0", "text": "# to maximum Life", "source": "explicit"}
    ]


def test_search_mods_finds_text_in_any_case(client: TestClient, db: Session) -> None:
    add_mods(db, ("explicit", "# to maximum Life"), ("explicit", "# to maximum Mana"))

    assert search(client, "MAXIMUM life") == [("explicit", "# to maximum Life")]


def test_search_mods_matches_every_word_separately(
    client: TestClient, db: Session
) -> None:
    add_mods(
        db,
        ("pseudo", "+# total maximum Life"),
        ("pseudo", "+# total maximum Mana"),
        ("explicit", "# to maximum Life"),
    )

    assert search(client, "life total") == [("pseudo", "+# total maximum Life")]


def test_search_mods_follows_official_group_order(
    client: TestClient, db: Session
) -> None:
    add_mods(
        db,
        ("implicit", "# Life"),
        ("explicit", "Allies have # Life"),
        ("explicit", "# to maximum Life"),
        ("implicit", "Gain # Life"),
        ("crafted", "# Life"),
        ("pseudo", "+# total maximum Life"),
    )

    assert search(client, "life") == [
        ("pseudo", "+# total maximum Life"),
        ("explicit", "# to maximum Life"),
        ("explicit", "Allies have # Life"),
        ("implicit", "# Life"),
        ("implicit", "Gain # Life"),
        ("crafted", "# Life"),
    ]


def test_search_mods_follows_official_position_then_shorter_text(
    client: TestClient, db: Session
) -> None:
    db.add(Mod(id="a", text="Life A", source="explicit", position=None))
    db.add(Mod(id="b", text="Life", source="explicit", position=None))
    db.add(Mod(id="c", text="Life C", source="explicit", position=9))
    db.add(Mod(id="d", text="Longer Life D", source="explicit", position=2))
    db.commit()

    texts = [text for _, text in search(client, "life")]

    assert texts == ["Longer Life D", "Life C", "Life", "Life A"]


def test_search_mods_percent_sign_is_plain_text(
    client: TestClient, db: Session
) -> None:
    add_mods(db, ("explicit", "10% chance"), ("explicit", "# per 100 Life"))

    assert search(client, "10%") == [("explicit", "10% chance")]


def test_search_mods_many_matches_returns_50(client: TestClient, db: Session) -> None:
    add_mods(db, *[("explicit", f"# Life {number}") for number in range(51)])

    assert len(search(client, "life")) == 50


def test_search_mods_without_token_returns_401(client: TestClient) -> None:
    response = client.get(MODS_URL, params={"q": "life"})

    assert response.status_code == 401


def test_search_mods_short_query_returns_422(client: TestClient) -> None:
    response = client.get(
        MODS_URL, params={"q": "l"}, headers=register_and_login(client)
    )

    assert response.status_code == 422
