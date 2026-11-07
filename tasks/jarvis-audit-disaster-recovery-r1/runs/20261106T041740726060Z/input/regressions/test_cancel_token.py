from __future__ import annotations

from fastapi.testclient import TestClient

from app.brain.cancel_token import CancelToken, current_token
from app.server import app


def setup_function() -> None:
    current_token.reset()


def teardown_function() -> None:
    current_token.reset()


def test_token_not_cancelled_initially() -> None:
    assert CancelToken().is_cancelled() is False


def test_token_cancel_sets_flag() -> None:
    token = CancelToken()
    token.cancel()
    assert token.is_cancelled() is True


def test_token_reset_clears_flag() -> None:
    token = CancelToken()
    token.cancel()
    token.reset()
    assert token.is_cancelled() is False


def test_stop_endpoint() -> None:
    with TestClient(app) as client:
        response = client.post("/stop")
    assert response.status_code == 200
    assert response.json() == {"status": "stopped"}
