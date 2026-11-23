import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile_token(token: str) -> bool:
    if not token:
        return False
    try:
        response = httpx.post(
            VERIFY_URL,
            data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
            timeout=10,
        )
        return response.json().get("success") is True
    except httpx.HTTPError, ValueError:
        logger.warning("Could not verify the Turnstile token", exc_info=True)
        return False
