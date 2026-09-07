from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

import app.resource_manager as resource_module
import app.voice.wake_word as wake_module
from app.logs.audit import AuditLogger
from app.resource_manager import WakeListener
from app.voice.wake_word import WakeWordDetector


class _Manager:
    def __init__(self) -> None:
        self.wake_calls = 0
        self.woke = threading.Event()

    async def wake(self, reason: str) -> None:
        assert reason == "wake_listener"
        self.wake_calls += 1
        self.woke.set()


class _FakeWakeWord:
    def __init__(self, results: list[tuple[bytes, str]], *, delay: float = 0.0) -> None:
        self._results = results
        self._delay = delay
        self.calls: list[float] = []
        self.last_listen_outcome = "idle"

    def listen(self, timeout: float) -> bytes:
        assert timeout == 3.0
        self.calls.append(time.monotonic())
        if self._delay:
            time.sleep(self._delay)
        audio, self.last_listen_outcome = self._results[min(len(self.calls) - 1, len(self._results) - 1)]
        return audio


def _start_listener(monkeypatch, fake: _FakeWakeWord, *, initial: float = 0.02, maximum: float = 0.08):  # noqa: ANN001
    manager = _Manager()
    listener = WakeListener(manager)
    listener._INITIAL_RETRY_SECONDS = initial
    listener._MAX_RETRY_SECONDS = maximum
    monkeypatch.setattr(wake_module, "wake_word", fake)
    monkeypatch.setattr(resource_module.audit, "log", lambda *_args, **_kwargs: None)
    listener.start()
    return manager, listener


def test_immediate_empty_wake_result_is_backed_off_instead_of_spinning(monkeypatch) -> None:  # noqa: ANN001
    fake = _FakeWakeWord([(b"", "unavailable")])
    _, listener = _start_listener(monkeypatch, fake, initial=0.03, maximum=0.03)

    time.sleep(0.11)
    listener.stop()

    assert 2 <= len(fake.calls) <= 5


def test_unavailable_retry_uses_exponential_backoff(monkeypatch) -> None:  # noqa: ANN001
    fake = _FakeWakeWord([(b"", "unavailable")])
    _, listener = _start_listener(monkeypatch, fake, initial=0.02, maximum=0.08)

    time.sleep(0.15)
    listener.stop()

    intervals = [later - earlier for earlier, later in zip(fake.calls, fake.calls[1:])]
    assert len(intervals) >= 3
    assert intervals[0] >= 0.015
    assert intervals[1] >= 0.035
    assert intervals[2] >= 0.07


def test_listener_stop_interrupts_retry_wait(monkeypatch) -> None:  # noqa: ANN001
    fake = _FakeWakeWord([(b"", "unavailable")])
    _, listener = _start_listener(monkeypatch, fake, initial=2.0, maximum=2.0)
    deadline = time.monotonic() + 1.0
    while not fake.calls and time.monotonic() < deadline:
        time.sleep(0.005)

    started = time.monotonic()
    listener.stop()

    assert time.monotonic() - started < 0.25
    assert not listener.is_running()


def test_normal_blocking_timeout_has_no_additional_retry_delay(monkeypatch) -> None:  # noqa: ANN001
    fake = _FakeWakeWord([(b"", "timeout")], delay=0.025)
    _, listener = _start_listener(monkeypatch, fake, initial=0.08, maximum=0.08)

    time.sleep(0.12)
    listener.stop()

    assert len(fake.calls) >= 4


def test_wake_detection_still_wakes_manager_and_thread_exits(monkeypatch) -> None:  # noqa: ANN001
    fake = _FakeWakeWord([(b"captured-audio", "detected")])
    manager, listener = _start_listener(monkeypatch, fake)

    assert manager.woke.wait(timeout=1.0)
    deadline = time.monotonic() + 1.0
    while listener.is_running() and time.monotonic() < deadline:
        time.sleep(0.005)

    assert manager.wake_calls == 1
    assert not listener.is_running()


def test_missing_audio_dependency_is_rate_limited_and_recovery_is_observable(monkeypatch) -> None:  # noqa: ANN001
    detector = WakeWordDetector()
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(detector, "_dictation_active", lambda: False)
    monkeypatch.setattr(detector, "_push_to_talk_active", lambda: False)
    monkeypatch.setitem(sys.modules, "sounddevice", None)
    monkeypatch.setattr(wake_module.audit, "log", lambda event, data: events.append((event, data)))

    for _ in range(20):
        assert detector.listen(timeout=3.0) == b""

    unavailable = [event for event in events if event[0] == "wake_unavailable"]
    assert len(unavailable) == 1
    assert detector.last_listen_outcome == "unavailable"

    detector._mark_available()  # noqa: SLF001 - deterministic recovery transition
    recovered = [event for event in events if event[0] == "wake_available_recovered"]
    assert len(recovered) == 1
    assert recovered[0][1]["suppressed_repeats"] == 19


def test_audit_rotation_bounds_backups_and_keeps_valid_json(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(str(path), max_bytes=360, backup_count=2)

    for index in range(30):
        logger.log("ordinary_event", {"index": index, "payload": "x" * 48})
    logger._shutdown()  # noqa: SLF001 - deterministic queue flush

    retained = [path, path.with_name("audit.jsonl.1"), path.with_name("audit.jsonl.2")]
    assert all(candidate.exists() for candidate in retained)
    assert not path.with_name("audit.jsonl.3").exists()
    rows = [
        json.loads(line)
        for candidate in retained
        for line in candidate.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert rows
    assert all(row["schema_version"] == 2 for row in rows)
    assert any(row["data"]["index"] == 29 for row in rows)
    assert not any(row["data"]["index"] == 0 for row in rows)


def test_audit_logger_continues_after_rotation_and_preserves_important_events(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(str(path), max_bytes=300, backup_count=3)

    for index in range(8):
        logger.log("noise", {"index": index, "payload": "x" * 64})
    logger.log("protected_action", {"tool": "shell", "allowed": False})
    logger._shutdown()  # noqa: SLF001 - deterministic queue flush

    rows = [
        json.loads(line)
        for candidate in [path, *sorted(tmp_path.glob("audit.jsonl.*"))]
        for line in candidate.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert any(row["event_type"] == "protected_action" for row in rows)
    assert all("session_id" in row and "timestamp" in row for row in rows)


def test_audit_logger_shutdown_is_clean_and_idempotent(tmp_path: Path) -> None:
    logger = AuditLogger(str(tmp_path / "audit.jsonl"), max_bytes=1024, backup_count=1)
    logger.log("shutdown_test", {})

    logger._shutdown()  # noqa: SLF001 - deterministic queue flush
    logger._shutdown()  # noqa: SLF001 - idempotency is part of clean shutdown

    assert not logger._worker.is_alive()  # noqa: SLF001
