"""Combines all API routers into one router, which the app mounts under /api/v1."""

from fastapi import APIRouter

from app.api.routes import auth, health, mods, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(mods.router)
