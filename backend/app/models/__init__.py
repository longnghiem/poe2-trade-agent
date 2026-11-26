"""Database tables and API data shapes. Every table class is imported here, so that importing
app.models registers all tables on SQLModel.metadata."""

from app.models.mod import Mod, ModPublic
from app.models.template import Template, TemplateIn, TemplatePublic
from app.models.trade import (
    ModFilter,
    ParsedTradeUrl,
    ParseTradeUrlRequest,
    StatGroup,
    StatGroupType,
    StatusOption,
    TradeLinkRequest,
    TradeLinkResponse,
    TradeSearch,
)
from app.models.user import Token, User, UserPublic, UserRegister

__all__ = [
    "User",
    "UserPublic",
    "UserRegister",
    "Token",
    "Mod",
    "ModPublic",
    "ModFilter",
    "StatGroup",
    "StatGroupType",
    "StatusOption",
    "TradeSearch",
    "TradeLinkRequest",
    "TradeLinkResponse",
    "ParseTradeUrlRequest",
    "ParsedTradeUrl",
    "Template",
    "TemplateIn",
    "TemplatePublic",
]
