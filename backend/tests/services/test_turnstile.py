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


def test_verify_turnstile_token_cloudflare_unreachable_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def cloudflare_unreachable(*_args: object, **_kwargs: object) -> httpx.Response:
        raise httpx.ConnectError("Cloudflare is unreachable")

    monkeypatch.setattr(httpx, "post", cloudflare_unreachable)

    assert verify_turnstile_token("some-token") is False


def test_verify_turnstile_token_error_page_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(503, text="<html>Bad gateway</html>"),
    )

    assert verify_turnstile_token("some-token") is False


def test_verify_turnstile_token_wrong_secret_logs_warning(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(
            200, json={"success": False, "error-codes": ["invalid-input-secret"]}
        ),
    )

    assert verify_turnstile_token("some-token") is False
    assert "Cloudflare rejected the Turnstile secret key" in caplog.text
