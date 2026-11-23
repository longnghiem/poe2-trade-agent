import httpx
import pytest

from app.services.turnstile import verify_turnstile_token


def test_verify_turnstile_token_empty_token_returns_false_without_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        httpx, "post", lambda *args, **kwargs: pytest.fail("Cloudflare was called")
    )

    assert verify_turnstile_token("") is False


@pytest.mark.parametrize("success", [True, False])
def test_verify_turnstile_token_returns_cloudflare_answer(
    monkeypatch: pytest.MonkeyPatch, success: bool
) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(200, json={"success": success}),
    )

    assert verify_turnstile_token("some-token") is success
