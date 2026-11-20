"""Combines all API routers into one router, which the app mounts under /api/v1."""

from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()
api_router.include_router(health.router)
