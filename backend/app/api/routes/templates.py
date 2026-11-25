from fastapi import APIRouter, status
from sqlmodel import col, select

from app.api.deps import CurrentUser, OwnedTemplate, SessionDep
from app.models import Template, TemplateIn, TemplatePublic
from app.models.template import utc_now

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", response_model=TemplatePublic, status_code=status.HTTP_201_CREATED)
def create_template(
    body: TemplateIn, session: SessionDep, current_user: CurrentUser
) -> Template:
    template = Template(**body.model_dump(), owner_id=current_user.id)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


@router.get("", response_model=list[TemplatePublic])
def list_my_templates(session: SessionDep, current_user: CurrentUser) -> list[Template]:
    statement = (
        select(Template)
        .where(Template.owner_id == current_user.id)
        .order_by(col(Template.updated_at).desc())
    )
    return list(session.exec(statement).all())


@router.get("/{template_id}", response_model=TemplatePublic)
def read_template(template: OwnedTemplate) -> Template:
    return template


@router.put("/{template_id}", response_model=TemplatePublic)
def update_template(
    body: TemplateIn, template: OwnedTemplate, session: SessionDep
) -> Template:
    """Replace all fields that the client may set."""
    template.sqlmodel_update(body.model_dump())
    template.updated_at = utc_now()
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template: OwnedTemplate, session: SessionDep) -> None:
    session.delete(template)
    session.commit()
