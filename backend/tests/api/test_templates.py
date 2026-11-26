import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.utils import register_and_login

TEMPLATES_URL = "/api/v1/templates"
BODY_ARMOUR = {
    "name": "Body armour",
    "folder": "Warrior",
    "tags": ["life"],
    "category": "armour.chest",
    "stat_groups": [
        {
            "type": "and",
            "min": None,
            "max": None,
            "mod_filters": [
                {
                    "stat_id": "explicit.stat_3299347043",
                    "label": "# to maximum Life",
                    "min": 200.0,
                    "max": None,
                    "weight": None,
                }
            ],
        }
    ],
    "status_option": "online",
    "max_price": 5.0,
    "price_currency": "divine",
    "is_public": False,
}


def create(
    client: TestClient, headers: dict[str, str], name: str = "Body armour"
) -> dict[str, Any]:
    """Create a template with this name and return the answer's JSON."""
    response = client.post(
        TEMPLATES_URL, json=BODY_ARMOUR | {"name": name}, headers=headers
    )
    assert response.status_code == 201
    template: dict[str, Any] = response.json()
    return template


def list_names(client: TestClient, headers: dict[str, str]) -> list[str]:
    response = client.get(TEMPLATES_URL, headers=headers)
    assert response.status_code == 200
    return [template["name"] for template in response.json()]


def test_create_template_returns_template(client: TestClient) -> None:
    template = create(client, register_and_login(client))

    assert BODY_ARMOUR.items() <= template.items()
    assert set(template) - set(BODY_ARMOUR) == {
        "id",
        "owner_id",
        "created_at",
        "updated_at",
    }


def test_create_template_unknown_status_returns_422(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.post(
        TEMPLATES_URL,
        json=BODY_ARMOUR | {"status_option": "sometimes"},
        headers=headers,
    )

    assert response.status_code == 422
    assert list_names(client, headers) == []


def test_list_templates_returns_only_mine(client: TestClient) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    create(client, alice, "Alice's")
    create(client, bob, "Bob's")

    assert list_names(client, alice) == ["Alice's"]
    assert list_names(client, bob) == ["Bob's"]


def test_list_templates_last_changed_first(client: TestClient) -> None:
    headers = register_and_login(client)
    first = create(client, headers, "First")
    create(client, headers, "Second")
    assert list_names(client, headers) == ["Second", "First"]

    client.put(f"{TEMPLATES_URL}/{first['id']}", json=first, headers=headers)

    assert list_names(client, headers) == ["First", "Second"]


def test_get_template_returns_template(client: TestClient) -> None:
    headers = register_and_login(client)
    template = create(client, headers)

    response = client.get(f"{TEMPLATES_URL}/{template['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json() == template


def test_update_template_replaces_fields(client: TestClient) -> None:
    headers = register_and_login(client)
    template = create(client, headers)
    new_group = {"type": "count", "min": 1.0, "max": None, "mod_filters": []}

    client.put(
        f"{TEMPLATES_URL}/{template['id']}",
        json={"name": "New name", "stat_groups": [new_group], "is_public": True},
        headers=headers,
    )

    saved = client.get(f"{TEMPLATES_URL}/{template['id']}", headers=headers).json()
    assert saved["name"] == "New name"
    assert saved["stat_groups"] == [new_group]
    assert saved["is_public"] is True
    assert saved["folder"] is None  # not sent, so back to the default
    assert saved["created_at"] == template["created_at"]


def test_update_template_cannot_change_id_or_owner(client: TestClient) -> None:
    headers = register_and_login(client)
    template = create(client, headers)
    other_ids = {"id": str(uuid.uuid4()), "owner_id": str(uuid.uuid4())}

    response = client.put(
        f"{TEMPLATES_URL}/{template['id']}", json=template | other_ids, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == template["id"]
    assert response.json()["owner_id"] == template["owner_id"]


def test_delete_template_removes_it(client: TestClient) -> None:
    headers = register_and_login(client)
    template = create(client, headers)

    response = client.delete(f"{TEMPLATES_URL}/{template['id']}", headers=headers)

    assert response.status_code == 204
    assert list_names(client, headers) == []


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_other_users_template_returns_404(client: TestClient, method: str) -> None:
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    template = create(client, alice)

    response = client.request(
        method,
        f"{TEMPLATES_URL}/{template['id']}",
        json=BODY_ARMOUR | {"name": "Bob was here"},
        headers=bob,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Template not found"}
    assert list_names(client, alice) == ["Body armour"]


def test_get_unknown_template_returns_404(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.get(f"{TEMPLATES_URL}/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", ""),
        ("GET", ""),
        ("GET", f"/{uuid.uuid4()}"),
        ("PUT", f"/{uuid.uuid4()}"),
        ("DELETE", f"/{uuid.uuid4()}"),
    ],
)
def test_templates_without_token_returns_401(
    client: TestClient, method: str, path: str
) -> None:
    response = client.request(method, TEMPLATES_URL + path, json=BODY_ARMOUR)

    assert response.status_code == 401
