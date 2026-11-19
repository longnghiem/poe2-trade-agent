"""Health check route, used by people and by the deploy pipeline to see that the API is up."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health() -> dict[str, str]:
    """Return a fixed answer so callers know the server is running."""
    return {"status": "ok"}