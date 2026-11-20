"""Health check route, used by people and by the deploy pipeline to see that the API is up."""

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: SessionDep) -> dict[str, str]:
    session.exec(select(1))
    return {"status": "ok"}
