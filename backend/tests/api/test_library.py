import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

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


@pytest.mark.parametrize(
    ("method", "url"),
    [("GET", LIBRARY_URL), ("POST", f"{LIBRARY_URL}/{uuid.uuid4()}/copy")],
)
def test_library_without_token_returns_401(
    client: TestClient, method: str, url: str
) -> None:
    assert client.request(method, url).status_code == 401
