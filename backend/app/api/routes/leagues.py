from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.services.leagues import get_leagues

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("", dependencies=[Depends(get_current_user)])
def read_leagues() -> list[str]:
    return get_leagues()
