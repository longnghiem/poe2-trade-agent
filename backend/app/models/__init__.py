"""Database tables and API data shapes. Every table class is imported here, so that importing
app.models registers all tables on SQLModel.metadata."""

from app.models.mod import Mod, ModPublic
from app.models.user import Token, User, UserPublic, UserRegister

__all__ = ["User", "UserPublic", "UserRegister", "Token", "Mod", "ModPublic"]
