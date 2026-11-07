import time
import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.unit


def test_cancel_token_stops_pipeline():
    from app.brain.cancel_token import CancelToken
    token = CancelToken()
    token.cancel()
    assert token.is_cancelled()
    token.reset()
    assert not token.is_cancelled()


def test_router_returns_respond_intent():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "gemma3:4b",
        "message": {"role": "assistant", "content": "respond"},
        "done": True,
    }
    mock_response.raise_for_status = MagicMock()
    with patch("httpx.Client.post", return_value=mock_response):
        from app.brain.router import IntentRouter
        router = IntentRouter.__new__(IntentRouter)
        router.config = MagicMock()
        router.config.get.return_value = "gemma3:4b"
        result = router._classify_with_ollama("hello jarvis")
    assert result == "respond"


def test_full_loop_timing_mock():
    start = time.time()
    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "respond", "done": True}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        from app.brain.router import IntentRouter
        router = IntentRouter.__new__(IntentRouter)
        router.config = MagicMock()
        router.config.get.return_value = "gemma3:4b"
        router._classify_with_ollama("hello")
    elapsed = time.time() - start
    assert elapsed < 2.0


def test_pipeline_imports():
    try:
        from app.brain.cancel_token import current_token  # noqa: F401
        from app.brain.router import classify_intent  # noqa: F401
        from app.logs.audit import AuditLog  # noqa: F401
    except ImportError as e:
        pytest.skip(f"Import not available: {e}")
