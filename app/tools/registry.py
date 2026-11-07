"""Tool registry - discovers, gates, and dispatches all JARVIS tools."""
from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from types import ModuleType
from typing import Any

from app.config import settings
from app.logs.audit import audit
from app.observability.tracing import emit_event, trace_span

SAFETY_LEVEL = 0

_EXPLICIT_TOOL_MODULES: dict[str, str] = {
    "apps": "app.tools.apps",
    "browser": "app.tools.browser",
    "browser_use": "app.tools.browser_use",
    "calendar": "app.tools.calendar",
    "cad": "app.tools.cad",
    "cli": "app.tools.cli",
    "computer_use": "app.tools.computer_use",
    "files": "app.tools.files",
    "kasa": "app.tools.kasa",
    "mcp_client": "app.tools.mcp_client",
    "mouse_keyboard": "app.tools.mouse_keyboard",
    "obsidian": "app.tools.obsidian",
    "screenshot": "app.tools.screenshot",
    "shell": "app.tools.shell",
    "system_stats": "app.tools.system_stats",
    "vision": "app.tools.vision",
    "web_search": "app.tools.web_search",
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


class _LazyToolCallable:
    def __init__(self, module_path: str) -> None:
        self._module_path = module_path

    def __call__(self, params: dict[str, Any] | None = None) -> Any:
        raise ToolError("real_execution_disabled_independent_authorization_required")


def _discover_tool_modules() -> dict[str, str]:
    import app.tools as pkg

    modules = dict(_EXPLICIT_TOOL_MODULES)
    for info in pkgutil.iter_modules(pkg.__path__):
        if info.name == "registry":
            continue
        modules.setdefault(info.name, f"app.tools.{info.name}")
    return modules


TOOLS: dict[str, Callable[[dict[str, Any] | None], Any]] = {
    name: _LazyToolCallable(module_path)
    for name, module_path in _discover_tool_modules().items()
}


class ToolRegistry:
    """Discover available tools and enforce safety policy before execution."""

    def __init__(self) -> None:
        self._tools: dict[str, ModuleType] = {}
        self._tool_modules = _discover_tool_modules()
        self.TOOLS: dict[str, Callable[[dict[str, Any] | None], Any]] = {
            name: _LazyToolCallable(module_path)
            for name, module_path in self._tool_modules.items()
        }

    def _load_tool(self, name: str) -> ModuleType:
        # Metadata only. Do not import effect-capable modules or return raw
        # execute functions through compatibility getters.
        if type(name) is not str or name not in self._tool_modules:
            raise ToolError("unknown_tool")
        module=ModuleType(name)
        module.SAFETY_LEVEL=-1
        module.DESCRIPTION="Real execution disabled; independent authorized adapter required."
        module.execute=_LazyToolCallable(self._tool_modules[name])
        module.EXECUTION_ENABLED=False
        return module

    def get_tool(self, name: str) -> ModuleType:
        """Return a loaded tool module by name."""
        return self._load_tool(name)

    def get(self, name: str) -> ModuleType | None:
        """Return a loaded tool module by name, or None if absent."""
        try:
            return self._load_tool(name)
        except ToolError:
            return None

    def list_tools(self) -> list[dict[str, Any]]:
        """Return metadata for all known tools."""
        tools: list[dict[str, Any]] = []
        for name in sorted(self._tool_modules):
            try:
                module = self._load_tool(name)
            except ToolError as exc:
                tools.append({"name": name, "safety_level": -1, "description": str(exc)})
                continue
            tools.append(
                {
                    "name": name,
                    "safety_level": getattr(module, "SAFETY_LEVEL", -1),
                    "description": getattr(module, "DESCRIPTION", ""),
                    "execution_enabled":False,
                }
            )
        return tools

    def tool_descriptions(self) -> dict[str, str]:
        """Return tool descriptions for embedding-based routing."""
        descriptions: dict[str, str] = {}
        for name in sorted(self._tool_modules):
            try:
                module = self._load_tool(name)
            except ToolError:
                continue
            description = getattr(module, "DESCRIPTION", "") or (getattr(module, "__doc__", "") or "")
            safety_level = getattr(module, "SAFETY_LEVEL", "unknown")
            descriptions[name] = f"{description.strip()}\nSAFETY_LEVEL={safety_level}".strip()
        return descriptions

    def call(
        self,
        tool_name: str,
        params: dict[str, Any] | None = None,
        *,
        confirmed: bool = False,
    ) -> ToolResult:
        """Legacy confirmation/config flags cannot authorize real effects.

        Only the separately authenticated, pure synthetic Authority pipeline is
        implemented for this milestone. No real adapter can be registered here.
        Do not log parameter values or import a tool before refusing.
        """
        raise ToolError("real_execution_disabled_independent_authorization_required")

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


def tool_descriptions() -> dict[str, str]:
    """Module-level convenience wrapper for embedding-based routing."""
    return registry.tool_descriptions()


def _capability_for(tool_name: str, params: dict[str, Any]) -> str:
    if tool_name == "apps":
        return "close_app" if params.get("action") == "close" else "open_app"
    if tool_name == "browser":
        return "web_search" if params.get("action") == "search" else "browser_open"
    if tool_name == "files":
        return {
            "read": "file_read",
            "list": "file_list",
            "move": "file_move",
        }.get(str(params.get("action")), "file_access")
    return {
        "calendar": "calendar_read",
        "screenshot": "screen_capture",
        "vision": "screen_describe",
        "shell": "shell_execute",
        "computer_use": "computer_control",
        "mouse_keyboard": "computer_control",
        "obsidian": "notes_access",
        "browser_use": "browser_automation",
    }.get(tool_name, tool_name)
