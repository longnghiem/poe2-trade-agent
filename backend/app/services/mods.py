from sqlmodel import Session, case, col, func, select

from app.models import Mod

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


def find_mods(session: Session, q: str) -> list[Mod]:
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
