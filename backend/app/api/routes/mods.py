from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import case, col, func, select

from app.api.deps import SessionDep, get_current_user
from app.models import Mod, ModPublic

# The group order of the official trade site. Other sources come last.
SOURCES = [
    "pseudo",
    "explicit",
    "implicit",
    "fractured",
    "enchant",
    "rune",
    "desecrated",
    "sanctum",
    "skill",
]

router = APIRouter(prefix="/mods", tags=["mods"])


@router.get(
    "", response_model=list[ModPublic], dependencies=[Depends(get_current_user)]
)
def search_mods(
    session: SessionDep, q: Annotated[str, Query(min_length=2)]
) -> list[Mod]:
    """Return up to 50 mods whose text contains every word of q, in the official site's order."""
    source_order = case(
        {source: number for number, source in enumerate(SOURCES)},
        value=col(Mod.source),
        else_=len(SOURCES),
    )
    statement = select(Mod)
    for word in q.split():
        statement = statement.where(col(Mod.text).icontains(word, autoescape=True))
    statement = statement.order_by(
        source_order,
        col(Mod.position),  # PostgreSQL puts mods without a position last
        func.length(Mod.text),
        col(Mod.text),
        col(Mod.id),
    ).limit(50)
    return list(session.exec(statement).all())
