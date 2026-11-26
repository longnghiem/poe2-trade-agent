import uuid
from collections.abc import Callable, Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.db import engine
from app.core.security import read_access_token
from app.models import Template, User
from app.services.turnstile import verify_turnstile_token


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    user_id = read_access_token(token)
    user = session.get(User, uuid.UUID(user_id)) if user_id else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_owned_template_by_id(
    template_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Template:
    template = session.get(Template, template_id)
    # Someone else's template gives the same answer, so nobody can find out that it exists.
    if template is None or template.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


OwnedTemplate = Annotated[Template, Depends(get_owned_template_by_id)]


def get_public_template_by_id(template_id: uuid.UUID, session: SessionDep) -> Template:
    template = session.get(Template, template_id)
    # A private template gives the same answer, so nobody can find out that it exists.
    if template is None or not template.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


PublicTemplate = Annotated[Template, Depends(get_public_template_by_id)]


def get_turnstile_verifier() -> Callable[[str], bool]:
    return verify_turnstile_token


TurnstileVerifierDep = Annotated[Callable[[str], bool], Depends(get_turnstile_verifier)]
