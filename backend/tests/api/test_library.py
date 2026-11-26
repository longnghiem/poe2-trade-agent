import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Vote
from tests.utils import register_and_login

LIBRARY_URL = "/api/v1/library"
TEMPLATES_URL = "/api/v1/templates"
STAT_GROUPS = [
    {
        "type": "count",
        "min": 2.0,
        "max": None,
        "mod_filters": [
            {"stat_id": "a", "label": "A", "min": 30.0, "max": None, "weight": None}
        ],
    }
]


def create(
    client: TestClient, headers: dict[str, str], name: str, **fields: Any
) -> dict[str, Any]:
    """Create a public template, or one with other fields, and return the answer's JSON."""
    body = {"name": name, "is_public": True} | fields
    response = client.post(TEMPLATES_URL, json=body, headers=headers)
    assert response.status_code == 201
    template: dict[str, Any] = response.json()
    return template


def library(
    client: TestClient, headers: dict[str, str], **params: str
) -> list[dict[str, Any]]:
    response = client.get(LIBRARY_URL, params=params, headers=headers)
    assert response.status_code == 200
    templates: list[dict[str, Any]] = response.json()
    return templates


def vote(client: TestClient, headers: dict[str, str], template_id: str) -> None:
    response = client.post(f"{LIBRARY_URL}/{template_id}/vote", headers=headers)
    assert response.status_code == 204


def remove_vote(client: TestClient, headers: dict[str, str], template_id: str) -> None:
    response = client.delete(f"{LIBRARY_URL}/{template_id}/vote", headers=headers)
    assert response.status_code == 204


def test_list_library_shows_public_templates_of_everyone(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    create(client, alice, "Alice public")
    create(client, alice, "Alice private", is_public=False)
    create(client, bob, "Bob public")

    templates = library(client, bob)

    assert [(t["name"], t["owner_username"]) for t in templates] == [
        ("Bob public", "bob"),
        ("Alice public", "alice"),
    ]


@pytest.mark.parametrize(
    "params",
    [{"q": "LIFE"}, {"category": "armour.chest"}, {"tag": "life"}],
)
def test_list_library_filters(client: TestClient, params: dict[str, str]) -> None:
    headers = register_and_login(client)
    create(client, headers, "Life armour", category="armour.chest", tags=["life"])
    create(client, headers, "Fast boots", category="armour.boots", tags=["speed"])

    assert [t["name"] for t in library(client, headers, **params)] == ["Life armour"]


def test_copy_template_creates_private_copy(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    original = create(
        client,
        alice,
        "Resists",
        folder="Alice's",
        tags=["res"],
        stat_groups=STAT_GROUPS,
    )

    response = client.post(f"{LIBRARY_URL}/{original['id']}/copy", headers=bob)

    assert response.status_code == 201
    copy = response.json()
    assert copy["name"] == "Copy of Resists"
    assert copy["is_public"] is False
    assert copy["folder"] is None
    assert copy["tags"] == ["res"]
    assert copy["stat_groups"] == STAT_GROUPS
    assert copy["id"] != original["id"]
    bobs = client.get(TEMPLATES_URL, headers=bob).json()
    assert [template["id"] for template in bobs] == [copy["id"]]


def test_copy_template_long_name_is_cut(client: TestClient) -> None:
    headers = register_and_login(client)
    original = create(client, headers, "x" * 100)

    response = client.post(f"{LIBRARY_URL}/{original['id']}/copy", headers=headers)

    assert response.status_code == 201
    assert response.json()["name"] == "Copy of " + "x" * 92


def test_copy_private_template_returns_404(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    original = create(client, alice, "Secret", is_public=False)

    response = client.post(
        f"{LIBRARY_URL}/{original['id']}/copy",
        headers=register_and_login(client, "bob"),
    )

    assert response.status_code == 404


def test_vote_counts_once(client: TestClient) -> None:
    headers = register_and_login(client)
    template = create(client, headers, "Life armour")

    vote(client, headers, template["id"])
    vote(client, headers, template["id"])

    [listed] = library(client, headers)
    assert (listed["vote_count"], listed["voted_by_me"]) == (1, True)


def test_list_library_counts_votes_of_everyone(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    template = create(client, alice, "Life armour")
    create(client, alice, "No votes")
    vote(client, alice, template["id"])
    vote(client, bob, template["id"])
    remove_vote(client, alice, template["id"])

    assert [
        (t["name"], t["vote_count"], t["voted_by_me"]) for t in library(client, alice)
    ] == [("No votes", 0, False), ("Life armour", 1, False)]
    assert [
        (t["name"], t["vote_count"], t["voted_by_me"]) for t in library(client, bob)
    ] == [("No votes", 0, False), ("Life armour", 1, True)]


def test_remove_vote_without_vote_changes_nothing(client: TestClient) -> None:
    headers = register_and_login(client)
    template = create(client, headers, "Life armour")

    remove_vote(client, headers, template["id"])

    assert library(client, headers)[0]["vote_count"] == 0


def test_list_library_sort_by_votes(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    one_vote = create(client, alice, "One vote")
    two_votes = create(client, alice, "Two votes")
    create(client, alice, "No votes, older")
    create(client, alice, "No votes, newer")
    vote(client, alice, one_vote["id"])
    vote(client, alice, two_votes["id"])
    vote(client, bob, two_votes["id"])

    assert [t["name"] for t in library(client, alice, sort="votes")] == [
        "Two votes",
        "One vote",
        "No votes, newer",
        "No votes, older",
    ]


def test_list_library_unknown_sort_returns_422(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.get(LIBRARY_URL, params={"sort": "old"}, headers=headers)

    assert response.status_code == 422


def test_vote_private_template_returns_404(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    template = create(client, alice, "Secret", is_public=False)

    response = client.post(
        f"{LIBRARY_URL}/{template['id']}/vote",
        headers=register_and_login(client, "bob"),
    )

    assert response.status_code == 404


def test_delete_template_removes_votes(client: TestClient, db: Session) -> None:
    headers = register_and_login(client)
    template = create(client, headers, "Life armour")
    vote(client, headers, template["id"])

    response = client.delete(f"{TEMPLATES_URL}/{template['id']}", headers=headers)

    assert response.status_code == 204
    assert db.exec(select(Vote)).all() == []


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("GET", LIBRARY_URL),
        ("POST", f"{LIBRARY_URL}/{uuid.uuid4()}/copy"),
        ("POST", f"{LIBRARY_URL}/{uuid.uuid4()}/vote"),
        ("DELETE", f"{LIBRARY_URL}/{uuid.uuid4()}/vote"),
    ],
)
def test_library_without_token_returns_401(
    client: TestClient, method: str, url: str
) -> None:
    assert client.request(method, url).status_code == 401
