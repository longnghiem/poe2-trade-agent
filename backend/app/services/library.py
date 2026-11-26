import uuid
from typing import Literal

from sqlmodel import Session, col, func, select

from app.models import LibraryTemplatePublic, Template, User, Vote

LibrarySort = Literal["new", "votes"]


def find_public_templates(
    session: Session,
    user_id: uuid.UUID,
    q: str | None,
    category: str | None,
    tag: str | None,
    sort: LibrarySort,
) -> list[LibraryTemplatePublic]:
    """Return up to 50 public templates with their owners' usernames and votes.
    q matches part of the name, in any case; category and tag must match exactly.
    sort "new" puts the last changed first; "votes" puts the most votes first, then the last changed.
    user_id is the user asking, for voted_by_me.
    """
    vote_count = func.count(col(Vote.user_id)).label("vote_count")
    statement = (
        select(Template, User.username, vote_count)
        .join(User, col(Template.owner_id) == col(User.id))
        # An outer join keeps the templates that have no votes yet.
        .outerjoin(Vote, col(Vote.template_id) == col(Template.id))
        .where(col(Template.is_public).is_(True))
        .group_by(col(Template.id), col(User.username))
    )
    if q:
        statement = statement.where(col(Template.name).icontains(q, autoescape=True))
    if category:
        statement = statement.where(col(Template.category) == category)
    if tag:
        statement = statement.where(col(Template.tags).contains([tag]))
    if sort == "votes":
        statement = statement.order_by(vote_count.desc())
    statement = statement.order_by(col(Template.updated_at).desc()).limit(50)
    rows = session.exec(statement).all()

    template_ids = [template.id for template, _, _ in rows]
    my_votes = select(Vote.template_id).where(
        Vote.user_id == user_id, col(Vote.template_id).in_(template_ids)
    )
    voted_ids = set(session.exec(my_votes).all())

    return [
        LibraryTemplatePublic.model_validate(
            template,
            update={
                "owner_username": username,
                "vote_count": count,
                "voted_by_me": template.id in voted_ids,
            },
        )
        for template, username, count in rows
    ]
