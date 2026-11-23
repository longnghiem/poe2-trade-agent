import httpx

from app.core.config import settings

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
    except httpx.HTTPError:
        return False
    return response.json().get("success") is True
