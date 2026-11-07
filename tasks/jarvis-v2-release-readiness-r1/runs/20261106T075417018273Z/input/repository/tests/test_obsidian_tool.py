from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest

from app.config import load_settings, settings
from app.tools import mcp_client, obsidian
from app.tools.registry import registry


pytestmark = pytest.mark.unit


def _scratch_vault() -> Path:
    return Path("tasks") / f".obsidian-test-{uuid.uuid4().hex}"


def _configure_filesystem_mode(monkeypatch, vault_path: Path) -> None:
    monkeypatch.setattr(settings.tools, "obsidian_enabled", False)
    monkeypatch.setattr(settings.tools, "obsidian_vault_path", str(vault_path))
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(obsidian.audit, "log", lambda *_args, **_kwargs: None)


def test_obsidian_filesystem_crud_stays_inside_vault(monkeypatch) -> None:
    vault_path = _scratch_vault()
    _configure_filesystem_mode(monkeypatch, vault_path)

    try:
        created = obsidian.execute(
            {
                "action": "note_create",
                "path": "Projects/JARVIS Log",
                "content": "Initial [[linked]] note.",
            }
        )
        appended = obsidian.execute(
            {
                "action": "note_append",
                "path": "Projects/JARVIS Log",
                "content": "Second line.",
            }
        )
        read = obsidian.execute({"action": "note_read", "path": "Projects/JARVIS Log"})
        search = obsidian.execute({"action": "note_search", "query": "linked"})

        assert created == {"created": True, "path": "Projects/JARVIS Log.md", "chars": 24}
        assert appended == {"appended": True, "path": "Projects/JARVIS Log.md", "chars": 12}
        assert read["found"] is True
        assert read["content"] == "Initial [[linked]] note.\nSecond line."
        assert search["count"] == 1
        assert search["results"][0]["path"] == "Projects/JARVIS Log.md"
        assert (vault_path / "Projects" / "JARVIS Log.md").is_file()
    finally:
        shutil.rmtree(vault_path, ignore_errors=True)


def test_obsidian_blocks_path_traversal(monkeypatch) -> None:
    vault_path = _scratch_vault()
    _configure_filesystem_mode(monkeypatch, vault_path)

    try:
        result = obsidian.execute({"action": "note_create", "path": "../outside", "content": "nope"})

        assert "outside the configured vault" in result["error"]
        assert not (vault_path.parent / "outside.md").exists()
    finally:
        shutil.rmtree(vault_path, ignore_errors=True)


def test_obsidian_mcp_path_is_stubbed_when_enabled(monkeypatch) -> None:
    vault_path = _scratch_vault()
    monkeypatch.setattr(settings.tools, "obsidian_enabled", True)
    monkeypatch.setattr(settings.tools, "obsidian_vault_path", str(vault_path))
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(obsidian.audit, "log", lambda *_args, **_kwargs: None)

    result = obsidian.execute({"action": "note_append", "path": "Inbox", "content": "via mcp"})

    assert result["dry_run"] is True
    assert result["server"] == "obsidian"
    assert result["configured"]["command"] == f"npx obsidian-mcp {vault_path}"
    assert result["params"]["tool"] == "note_append"


def test_obsidian_is_registered_and_configured() -> None:
    loaded = load_settings()

    assert loaded.tools.obsidian_enabled is False
    assert loaded.tools.obsidian_vault_path == "./jarvis-vault"
    assert "obsidian" in registry.TOOLS
    assert "obsidian" in mcp_client.WHITELISTED_SERVERS
    assert mcp_client.status("obsidian")["configured"]["command"] == "npx obsidian-mcp ./jarvis-vault"


def test_obsidian_route_and_action_tag_params() -> None:
    from app.brain.router import router
    from app.brain.tool_params import build_tool_params

    result = router.classify("[ACTION:OBSIDIAN:note_append:Daily Log] captured detail")
    params = build_tool_params("obsidian", "[ACTION:OBSIDIAN:note_append:Daily Log] captured detail")

    assert result.intent == "use_tool"
    assert result.suggested_tool == "obsidian"
    assert params == {
        "action": "note_append",
        "path": "Daily Log",
        "content": "captured detail",
        "query": "captured detail",
    }
