"""Tool registry - discovers, gates, and dispatches all JARVIS tools."""
from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Any

from app.config import settings
from app.logs.audit import audit
from app.tools import apps as apps_tool
from app.tools import calendar as calendar_tool
from app.tools import files as files_tool
from app.tools import interpreter as interpreter_tool
from app.tools import shell as shell_tool
from app.tools import system_stats as system_stats_tool
from app.tools import web_search as web_search_tool

SAFETY_LEVEL = 0

TOOLS: dict[str, Any] = {
    "apps": apps_tool.execute,
    "calendar": calendar_tool.execute,
    "files": files_tool.execute,
    "interpreter": interpreter_tool.execute,
    "shell": shell_tool.execute,
    "system_stats": system_stats_tool.execute,
    "web_search": web_search_tool.execute,
}


class ToolError(Exception):
    """Raised when a tool call is blocked or fails."""


class ToolResult:
    """Normalized result from a tool invocation."""

    def __init__(self, *, tool: str, output: Any, dry_run: bool = False) -> None:
        self.tool = tool
        self.output = output
        self.dry_run = dry_run

    def __repr__(self) -> str:
        tag = " [DRY RUN]" if self.dry_run else ""
        return f"ToolResult({self.tool}{tag}): {self.output}"


class ToolRegistry:
    """Discover available tools and enforce safety policy before execution."""

    def __init__(self) -> None:
        self._tools: dict[str, ModuleType] = {}
        self._load_all()
        self.TOOLS = {name: mod.execute for name, mod in self._tools.items()}

    def _load_all(self) -> None:
        import app.tools as pkg

        explicit_tools = {
            "apps": apps_tool,
            "calendar": calendar_tool,
            "files": files_tool,
            "interpreter": interpreter_tool,
            "shell": shell_tool,
            "system_stats": system_stats_tool,
            "web_search": web_search_tool,
        }
        self._tools.update(explicit_tools)

        for info in pkgutil.iter_modules(pkg.__path__):
            if info.name == "registry":
                continue
            try:
                mod = importlib.import_module(f"app.tools.{info.name}")
                if hasattr(mod, "execute") and hasattr(mod, "SAFETY_LEVEL"):
                    self._tools[info.name] = mod
            except Exception as exc:  # noqa: BLE001
                audit.log("tool_load_error", {"tool": info.name, "error": str(exc)})
        self.TOOLS = {name: mod.execute for name, mod in self._tools.items()}

    def get_tool(self, name: str) -> ModuleType:
        """Return a loaded tool module by name."""
        if name not in self._tools:
            raise ToolError(f"Unknown tool: {name!r}")
        return self._tools[name]

    def list_tools(self) -> list[dict[str, Any]]:
        """Return metadata for all loaded tools."""
        return [
            {
                "name": name,
                "safety_level": getattr(mod, "SAFETY_LEVEL", -1),
                "description": getattr(mod, "DESCRIPTION", ""),
            }
            for name, mod in self._tools.items()
        ]

    def call(
        self,
        tool_name: str,
        params: dict[str, Any] | None = None,
        *,
        confirmed: bool = False,
    ) -> ToolResult:
        """Execute a tool after Level 0-3 safety and dry-run checks."""
        params = params or {}

        if tool_name not in self._tools:
            raise ToolError(f"Unknown tool: {tool_name!r}")

        mod = self._tools[tool_name]
        safety_level: int = getattr(mod, "SAFETY_LEVEL", 0)

        audit.log(
            "tool_call",
            {
                "tool": tool_name,
                "safety_level": safety_level,
                "params": params,
                "dry_run": settings.safety.dry_run,
                "confirmed": confirmed,
            },
        )

        if safety_level >= 3:
            raise ToolError(f"Tool '{tool_name}' is Level 3 (blocked). Cannot execute automatically.")

        if self._requires_confirmation(safety_level) and not confirmed:
            raise ToolError(f"Tool '{tool_name}' is Level {safety_level}. Requires user confirmation before executing.")

        if settings.safety.dry_run:
            description = getattr(mod, "DESCRIPTION", tool_name)
            output = f"[DRY RUN] Would execute '{tool_name}': {description} with params {params}"
            audit.log("tool_result", {"tool": tool_name, "dry_run": True, "output": output})
            return ToolResult(tool=tool_name, output=output, dry_run=True)

        try:
            output = mod.execute(params)
        except Exception as exc:
            audit.log("tool_error", {"tool": tool_name, "error": str(exc)})
            raise ToolError(f"Tool '{tool_name}' raised: {exc}") from exc

        audit.log("tool_result", {"tool": tool_name, "output": str(output)[:500]})
        return ToolResult(tool=tool_name, output=output)

    def execute(
        self,
        tool_name: str,
        params: dict[str, Any] | None = None,
        *,
        confirmed: bool = False,
    ) -> ToolResult:
        """Compatibility wrapper for call()."""
        return self.call(tool_name, params, confirmed=confirmed)

    def _requires_confirmation(self, safety_level: int) -> bool:
        mode = settings.safety.approval_mode
        if mode == "strict":
            return safety_level >= 0
        if mode == "safe":
            return safety_level >= 1
        return safety_level >= 2


registry = ToolRegistry()
