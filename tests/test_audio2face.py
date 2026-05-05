from __future__ import annotations

from app.comms.audio2face import (
    audio2face_manager,
    build_audio_event,
    build_viseme_event,
)


def test_build_audio_event() -> None:
    result = build_audio_event(b"test-audio")

    assert result["type"] == "audio"
    assert isinstance(result["data"], str)
    assert result["data"]
    assert result["sample_rate"] == 22050
    assert "timestamp" in result


def test_build_viseme_event() -> None:
    test_viseme = {"phoneme": "AH", "weight": 0.9, "timestamp": 0.12}

    result = build_viseme_event([test_viseme])

    assert result["type"] == "visemes"
    assert result["data"] == [test_viseme]
    assert "timestamp" in result


def test_manager_not_connected_by_default() -> None:
    audio2face_manager.disconnect()

    assert audio2face_manager.is_connected() is False


def test_broadcast_audio_when_not_connected() -> None:
    audio2face_manager.disconnect()
    audio2face_manager.broadcast_audio(b"test-audio")
