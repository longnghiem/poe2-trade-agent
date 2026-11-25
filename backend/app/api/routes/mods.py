from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import SessionDep, get_current_user
from app.models import Mod, ModPublic
from app.services.mods import find_mods

router = APIRouter(prefix="/mods", tags=["mods"])


@router.get(
    "", response_model=list[ModPublic], dependencies=[Depends(get_current_user)]
)
def search_mods(
    session: SessionDep, q: Annotated[str, Query(min_length=2)]
) -> list[Mod]:
    return find_mods(session, q)
