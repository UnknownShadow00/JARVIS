from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from app.voice.vad import vad


def _run(timeout: float) -> bytes:
    stream = MagicMock()
    stream.__enter__.return_value = MagicMock()
    stream.__exit__.return_value = False
    with patch("sounddevice.RawInputStream", return_value=stream), patch("webrtcvad.Vad", return_value=MagicMock()):
        return vad.record_until_silence(timeout=timeout)


def test_no_speech_returns_empty() -> None:
    assert _run(0.3) == b""


def test_result_type_is_bytes() -> None:
    assert isinstance(_run(0.3), bytes)


def test_short_timeout_exits_fast() -> None:
    started_at = time.perf_counter()
    result = _run(0.5)
    elapsed = time.perf_counter() - started_at
    assert result == b""
    assert elapsed < 3.0
