"""Obsidian vault note tool with optional MCP handoff."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 1
DESCRIPTION = "Create, append, read, and search Markdown notes inside the configured Obsidian vault."

_MAX_READ_BYTES = 64_000
_MAX_SEARCH_BYTES = 256_000
_MAX_SEARCH_RESULTS = 25
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def execute(params: dict[str, Any]) -> dict[str, Any]:
    """Execute a constrained Obsidian note action."""
    action = str(params.get("action", "note_search")).strip().lower()
    audit.log("obsidian_action", _audit_payload(action, params))

    if settings.safety.dry_run:
        return {"dry_run": True, "action": action, "note": "Would execute Obsidian note action."}

    if settings.tools.obsidian_enabled:
        return _execute_mcp(action, params)

    try:
        if action == "note_create":
            return _note_create(params)
        if action == "note_append":
            return _note_append(params)
        if action == "note_read":
            return _note_read(params)
        if action == "note_search":
            return _note_search(params)
    except (OSError, PermissionError, ValueError) as exc:
        audit.log("obsidian_error", {"action": action, "error": str(exc)})
        return {"error": str(exc)}
    return {"error": f"Unknown Obsidian action: {action!r}", "allowed": _allowed_actions()}


def _execute_mcp(action: str, params: dict[str, Any]) -> dict[str, Any]:
    from app.tools import mcp_client

    return mcp_client.execute(
        {
            "action": "call",
            "server": "obsidian",
            "tool": action,
            "params": dict(params),
        }
    )


def _note_create(params: dict[str, Any]) -> dict[str, Any]:
    note_path = _safe_note_path(_note_name(params))
    content = str(params.get("content", ""))
    overwrite = bool(params.get("overwrite", False))

    if note_path.exists() and not overwrite:
        return {"error": "note_exists", "path": _relative(note_path)}

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(content, encoding="utf-8")
    return {"created": True, "path": _relative(note_path), "chars": len(content)}


def _note_append(params: dict[str, Any]) -> dict[str, Any]:
    note_path = _safe_note_path(_note_name(params))
    content = str(params.get("content", ""))
    separator = "" if not note_path.exists() or note_path.stat().st_size == 0 else "\n"

    note_path.parent.mkdir(parents=True, exist_ok=True)
    with note_path.open("a", encoding="utf-8") as note_file:
        note_file.write(f"{separator}{content}")
    return {"appended": True, "path": _relative(note_path), "chars": len(content)}


def _note_read(params: dict[str, Any]) -> dict[str, Any]:
    note_path = _safe_note_path(_note_name(params))
    if not note_path.is_file():
        return {"found": False, "path": _relative(note_path), "content": ""}
    size = note_path.stat().st_size
    if size > _MAX_READ_BYTES:
        return {"error": "note_too_large", "path": _relative(note_path), "bytes": size}
    return {"found": True, "path": _relative(note_path), "content": note_path.read_text(encoding="utf-8")}


def _note_search(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query", "")).strip()
    root = _vault_root()
    if not query or not root.exists():
        return {"query_chars": len(query), "count": 0, "results": []}

    needle = query.lower()
    results: list[dict[str, str]] = []
    for item in sorted(root.rglob("*.md")):
        if len(results) >= _MAX_SEARCH_RESULTS:
            break
        try:
            resolved = item.resolve()
            resolved.relative_to(root)
            if not resolved.is_file():
                continue
            content = ""
            if resolved.stat().st_size <= _MAX_SEARCH_BYTES:
                content = resolved.read_text(encoding="utf-8", errors="replace")
            haystack = f"{resolved.stem}\n{content}".lower()
            if needle not in haystack:
                continue
            results.append({"path": _relative(resolved), "snippet": _snippet(content, needle)})
        except (OSError, ValueError, UnicodeError):
            continue

    return {"query_chars": len(query), "count": len(results), "results": results}


def _note_name(params: dict[str, Any]) -> str:
    note = str(params.get("path") or params.get("note") or params.get("title") or "").strip()
    if not note:
        raise ValueError("Obsidian note action requires path, note, or title.")
    return note


def _safe_note_path(note: str) -> Path:
    root = _vault_root()
    cleaned = note.strip().strip("[]")
    candidate = Path(cleaned)
    if candidate.suffix.lower() != ".md":
        candidate = candidate.with_suffix(".md")
    target = (candidate.expanduser() if candidate.is_absolute() else root / candidate).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PermissionError(f"Obsidian note path is outside the configured vault: {target}") from exc
    return target


def _vault_root() -> Path:
    configured = Path(settings.tools.obsidian_vault_path).expanduser()
    root = configured if configured.is_absolute() else _PROJECT_ROOT / configured
    return root.resolve()


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(_vault_root()).as_posix()
    except ValueError:
        return path.name


def _snippet(content: str, needle: str) -> str:
    if not content:
        return ""
    lower = content.lower()
    index = lower.find(needle)
    if index < 0:
        return content[:160]
    start = max(0, index - 60)
    end = min(len(content), index + len(needle) + 100)
    return content[start:end].replace("\n", " ").strip()


def _audit_payload(action: str, params: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "action": action,
        "mcp_enabled": settings.tools.obsidian_enabled,
        "vault": settings.tools.obsidian_vault_path,
    }
    note = params.get("path") or params.get("note") or params.get("title")
    if note is not None:
        payload["note"] = str(note)
    if "content" in params:
        payload["content_chars"] = len(str(params.get("content") or ""))
    if "query" in params:
        payload["query_chars"] = len(str(params.get("query") or ""))
    return payload


def _allowed_actions() -> list[str]:
    return ["note_create", "note_append", "note_read", "note_search"]
