import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, PublicTemplate, SessionDep
from app.models import LibraryTemplatePublic, Template, TemplateIn, TemplatePublic, Vote
from app.services.library import LibrarySort, find_public_templates

router = APIRouter(prefix="/library", tags=["library"])


@router.get("")
def list_library(
    current_user: CurrentUser,
    session: SessionDep,
    q: str | None = None,
    category: str | None = None,
    tag: str | None = None,
    sort: LibrarySort = "new",
) -> list[LibraryTemplatePublic]:
    """Public templates from everyone, with their votes."""
    return find_public_templates(session, current_user.id, q, category, tag, sort)


@router.post(
    "/{template_id}/copy",
    response_model=TemplatePublic,
    status_code=status.HTTP_201_CREATED,
)
def copy_template(
    current_user: CurrentUser, template: PublicTemplate, session: SessionDep
) -> Template:
    """Save a private copy of a public template for the current user."""
    fields = TemplateIn.model_validate(template).model_dump()
    fields["name"] = f"Copy of {template.name}"[:100]
    fields["folder"] = None  # folders are the owner's own order
    fields["is_public"] = False
    new_template = Template(**fields, owner_id=current_user.id)
    session.add(new_template)
    session.commit()
    session.refresh(new_template)
    return new_template


@router.post("/{template_id}/vote", status_code=status.HTTP_204_NO_CONTENT)
def vote(
    current_user: CurrentUser, template: PublicTemplate, session: SessionDep
) -> None:
    """Upvote a public template. Voting again changes nothing."""
    if session.get(Vote, (current_user.id, template.id)) is None:
        session.add(Vote(user_id=current_user.id, template_id=template.id))
        session.commit()


@router.delete("/{template_id}/vote", status_code=status.HTTP_204_NO_CONTENT)
def remove_vote(
    current_user: CurrentUser, template_id: uuid.UUID, session: SessionDep
) -> None:
    """Remove the current user's vote. Without a vote, this changes nothing."""
    existing = session.get(Vote, (current_user.id, template_id))
    if existing is not None:
        session.delete(existing)
        session.commit()
