from __future__ import annotations

from fastapi.testclient import TestClient

from app.brain.cancel_token import CancelToken, current_token
from app.server import app
import pytest


@pytest.fixture(autouse=True)
def explicit_disposable_authority(tmp_path):
    from app.agent import runtime
    from synthetic_authority import fixture_authority
    previous,worker=runtime._authority,runtime._execution_worker
    runtime._authority=runtime._execution_worker=None
    runtime.bind_authority(fixture_authority(tmp_path/'cancel/state.sqlite'))
    try:yield
    finally:
        runtime.close_authority();runtime._authority=previous;runtime._execution_worker=worker


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


def test_stop_endpoint(monkeypatch) -> None:
    from app.config import settings
    monkeypatch.setattr(settings.server,"api_token","synthetic-stop-token")
    with TestClient(app) as client:
        response = client.post("/stop",headers={"Authorization":"Bearer synthetic-stop-token"})
    assert response.status_code == 200
    assert response.json() == {"status": "stopped"}
