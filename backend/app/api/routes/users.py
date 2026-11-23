from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models import User, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/current_user", response_model=UserPublic)
def read_current_user(current_user: CurrentUser) -> User:
    return current_user
