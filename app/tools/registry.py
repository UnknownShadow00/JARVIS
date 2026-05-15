"""Tool registry - discovers, gates, and dispatches all JARVIS tools."""
from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from types import ModuleType
from typing import Any

from app.config import settings
from app.logs.audit import audit

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
        module = importlib.import_module(self._module_path)
        return module.execute(params or {})


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
        if name in self._tools:
            return self._tools[name]

        module_path = self._tool_modules.get(name)
        if module_path is None:
            raise ToolError(f"Unknown tool: {name!r}")

        try:
            module = importlib.import_module(module_path)
        except Exception as exc:  # noqa: BLE001
            audit.log("tool_load_error", {"tool": name, "error": str(exc)})
            raise ToolError(f"Unable to load tool {name!r}: {exc}") from exc

        if not hasattr(module, "execute") or not hasattr(module, "SAFETY_LEVEL"):
            raise ToolError(f"Invalid tool module: {name!r}")

        self._tools[name] = module
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
        """Execute a tool after Level 0-3 safety and dry-run checks."""
        params = params or {}
        module = self._load_tool(tool_name)
        safety_level: int = getattr(module, "SAFETY_LEVEL", 0)

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
            description = getattr(module, "DESCRIPTION", tool_name)
            output = f"[DRY RUN] Would execute '{tool_name}': {description} with params {params}"
            audit.log("tool_result", {"tool": tool_name, "dry_run": True, "output": output})
            return ToolResult(tool=tool_name, output=output, dry_run=True)

        try:
            output = module.execute(params)
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


def tool_descriptions() -> dict[str, str]:
    """Module-level convenience wrapper for embedding-based routing."""
    return registry.tool_descriptions()
