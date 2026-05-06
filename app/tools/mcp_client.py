from __future__ import annotations

from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 1
DESCRIPTION = "Whitelisted MCP client wrapper stub with dry-run/status behavior."

WHITELISTED_SERVERS: dict[str, dict[str, str]] = {
    "github": {"transport": "configured", "note": "Project baseline MCP server"},
    "context7": {"transport": "configured", "note": "Project baseline MCP server"},
    "exa": {"transport": "configured", "note": "Project baseline MCP server"},
    "memory": {"transport": "configured", "note": "Project baseline MCP server"},
    "playwright": {"transport": "configured", "note": "Project baseline MCP server"},
    "sequential-thinking": {"transport": "configured", "note": "Project baseline MCP server"},
}


def execute(params: dict[str, Any]) -> dict[str, Any]:
    action = str(params.get("action", "status")).lower().strip()
    server = str(params.get("server", "")).lower().strip()

    if action == "status":
        return status(server or None)

    if server not in WHITELISTED_SERVERS:
        return {"error": "server_not_whitelisted", "server": server, "allowed": sorted(WHITELISTED_SERVERS)}

    result = {
        "dry_run": True,
        "server": server,
        "action": action,
        "note": "FastMCP/client execution is not installed in this phase; this is a validated request plan.",
        "params": dict(params),
    }
    audit.log("mcp_client_stub", result)
    return result


def status(server: str | None = None) -> dict[str, Any]:
    if server:
        return {
            "server": server,
            "whitelisted": server in WHITELISTED_SERVERS,
            "configured": WHITELISTED_SERVERS.get(server),
            "dry_run": settings.safety.dry_run,
        }
    return {
        "available": False,
        "stub": True,
        "dry_run": settings.safety.dry_run,
        "allowed_servers": sorted(WHITELISTED_SERVERS),
        "note": "Install and configure an MCP client library before live calls.",
    }
