from sqlmodel import Session, col, select

from app.models import Template, User


def find_public_templates(
    session: Session, q: str | None, category: str | None, tag: str | None
) -> list[tuple[Template, str]]:
    """Return up to 50 public templates and their owners' usernames, last changed first.
    q matches part of the name, in any case; category and tag must match exactly.
    """
    statement = (
        select(Template, User.username)
        .join(User, col(Template.owner_id) == col(User.id))
        .where(col(Template.is_public).is_(True))
    )
    if q:
        statement = statement.where(col(Template.name).icontains(q, autoescape=True))
    if category:
        statement = statement.where(col(Template.category) == category)
    if tag:
        statement = statement.where(col(Template.tags).contains([tag]))
    statement = statement.order_by(col(Template.updated_at).desc()).limit(50)
    return list(session.exec(statement).all())
