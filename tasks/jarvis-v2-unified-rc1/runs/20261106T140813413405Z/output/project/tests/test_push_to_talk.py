from __future__ import annotations

from app.voice.push_to_talk import PushToTalkManager


def test_ptt_manager_instantiates() -> None:
    PushToTalkManager()


def test_ptt_not_active_by_default() -> None:
    manager = PushToTalkManager()
    assert manager.is_active() is False


def test_ptt_callback_registration() -> None:
    manager = PushToTalkManager()
    manager.on_press(lambda: None)
