from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.api.deps import SessionDep, TurnstileVerifierDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Token, User, UserPublic, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(
    body: UserRegister, session: SessionDep, verify_turnstile: TurnstileVerifierDep
) -> User:
    if not verify_turnstile(body.turnstile_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Human check failed"
        )
    existing = session.exec(select(User).where(User.username == body.username)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username is already taken"
        )
    user = User(username=body.username, hashed_password=hash_password(body.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    username = form.username.lower()
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )
    return Token(access_token=create_access_token(str(user.id)))
