"""Tests for app/computer/safety.py."""
from unittest.mock import patch

from app.computer.safety import safety_gate


def test_level0_always_allowed():
    allowed, reason = safety_gate.check("move_mouse", 0)
    assert allowed is True
    assert reason == "ok"


def test_level2_requires_confirmation():
    allowed, reason = safety_gate.check("click", 2, confirmed=False)
    assert allowed is False
    assert "confirmation" in reason


def test_level2_with_confirmation(monkeypatch):
    monkeypatch.setattr("app.computer.safety.settings.safety.dry_run", False)
    allowed, reason = safety_gate.check("click", 2, confirmed=True)
    assert allowed is True
    assert reason == "ok"


def test_level3_blocked():
    allowed, reason = safety_gate.check("admin_script", 3)
    assert allowed is False
    assert reason == "blocked"


def test_dry_run_blocks_level1(monkeypatch):
    monkeypatch.setattr("app.computer.safety.settings.safety.dry_run", True)
    allowed, reason = safety_gate.check("read_file", 1)
    assert allowed is False
    assert reason == "dry_run_active"
