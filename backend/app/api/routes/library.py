from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, PublicTemplate, SessionDep, get_current_user
from app.models import LibraryTemplatePublic, Template, TemplateIn, TemplatePublic
from app.services.library import find_public_templates

router = APIRouter(prefix="/library", tags=["library"])


@router.get("", dependencies=[Depends(get_current_user)])
def list_library(
    session: SessionDep,
    q: str | None = None,
    category: str | None = None,
    tag: str | None = None,
) -> list[LibraryTemplatePublic]:
    """Public templates from everyone, last changed first."""
    return [
        LibraryTemplatePublic.model_validate(
            template, update={"owner_username": username}
        )
        for template, username in find_public_templates(session, q, category, tag)
    ]


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
