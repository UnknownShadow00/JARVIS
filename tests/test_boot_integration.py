from __future__ import annotations

from contextlib import ExitStack
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app import boot


def _response() -> Mock:
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    return response


async def _run(*, http_side_effect, popen_side_effect=None, perf=(0, 0, 0, 1)):
    speak = AsyncMock()
    original_is_file = boot.Path.is_file
    perf_values = list(perf)
    perf_index = 0

    def fake_perf_counter() -> int:
        nonlocal perf_index
        value = perf_values[min(perf_index, len(perf_values) - 1)]
        perf_index += 1
        return value

    with ExitStack() as stack:
        play = stack.enter_context(patch("app.voice.sounds.sounds.play"))
        stack.enter_context(patch("app.voice.tts.tts.speak", speak))
        stack.enter_context(patch("httpx.get", side_effect=http_side_effect))
        stack.enter_context(patch("subprocess.Popen", side_effect=popen_side_effect))
        stack.enter_context(
            patch("app.boot.Path.is_file", lambda path: path.as_posix().endswith("frontend/electron/package.json") or original_is_file(path))
        )
        stack.enter_context(patch("app.boot.asyncio.sleep", AsyncMock()))
        stack.enter_context(patch("app.boot.time.perf_counter", side_effect=fake_perf_counter))
        await boot.run_boot_sequence()
    return play, speak


@pytest.mark.asyncio
async def test_boot_sequence_completes() -> None:
    play, _ = await _run(http_side_effect=_response(), popen_side_effect=FileNotFoundError())
    play.assert_called_with("boot_intro")


@pytest.mark.asyncio
async def test_morning_report_contains_sir() -> None:
    _, speak = await _run(http_side_effect=_response(), popen_side_effect=FileNotFoundError())
    assert "sir" in speak.await_args.args[0].lower()


@pytest.mark.asyncio
async def test_boot_skips_electron_gracefully() -> None:
    await _run(http_side_effect=_response(), popen_side_effect=FileNotFoundError())


@pytest.mark.asyncio
async def test_boot_ollama_timeout() -> None:
    await _run(
        http_side_effect=httpx.ConnectError("offline"),
        popen_side_effect=FileNotFoundError(),
        perf=(0, 0, 0, 31, 31),
    )
