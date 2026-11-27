import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Template, TemplateIn, TemplatePublic, User

BODY_ARMOUR = {
    "name": "Body armour",
    "folder": "Warrior",
    "tags": ["life", "cold"],
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
    "status_option": "available",
    "max_price": 5.0,
    "price_currency": "divine",
    "is_public": True,
}


def add_user(db: Session) -> User:
    user = User(username="exile", hashed_password="hash")
    db.add(user)
    db.commit()
    return user


def test_template_saved_and_loaded_keeps_values(db: Session) -> None:
    body = TemplateIn.model_validate(BODY_ARMOUR)
    template = Template(**body.model_dump(), owner_id=add_user(db).id)
    db.add(template)
    db.commit()

    db.expire_all()
    loaded = db.get(Template, template.id)

    public = TemplatePublic.model_validate(loaded)
    assert public.model_dump(include=set(BODY_ARMOUR)) == BODY_ARMOUR
    assert public.updated_at.tzinfo is not None


def test_template_only_name_uses_defaults(db: Session) -> None:
    body = TemplateIn(name="Empty")
    template = Template(**body.model_dump(), owner_id=add_user(db).id)
    db.add(template)
    db.commit()

    db.refresh(template)
    assert template.tags == []
    assert template.stat_groups == []
    assert template.status_option == "securable"
    assert template.is_public is False


def test_template_unknown_owner_is_rejected(db: Session) -> None:
    db.add(Template(name="No owner", owner_id=uuid.uuid4()))

    with pytest.raises(IntegrityError):
        db.commit()


@pytest.mark.parametrize(
    "change",
    [
        {"name": ""},
        {"status_option": "sometimes"},
        # no label
        {"stat_groups": [{"mod_filters": [{"stat_id": "explicit.stat_3299347043"}]}]},
        {"stat_groups": [{"type": "not"}]},  # a group type we don't support
    ],
)
def test_template_in_invalid_value_is_rejected(change: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        TemplateIn.model_validate(BODY_ARMOUR | change)
