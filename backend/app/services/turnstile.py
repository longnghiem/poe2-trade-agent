import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
# Cloudflare's error codes for a wrong or missing TURNSTILE_SECRET_KEY. Other codes, such as
# invalid-input-response, mean a bot or an expired token, which is normal.
SECRET_ERROR_CODES = {"missing-input-secret", "invalid-input-secret"}


def verify_turnstile_token(token: str) -> bool:
    if not token:
        return False
    try:
        response = httpx.post(
            VERIFY_URL,
            data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
            timeout=10,
        )
        answer = response.json()
    except httpx.HTTPError, ValueError:
        logger.warning("Could not verify the Turnstile token", exc_info=True)
        return False
    error_codes = answer.get("error-codes", [])
    if SECRET_ERROR_CODES.intersection(error_codes):
        logger.warning("Cloudflare rejected the Turnstile secret key: %s", error_codes)
    return answer.get("success") is True
