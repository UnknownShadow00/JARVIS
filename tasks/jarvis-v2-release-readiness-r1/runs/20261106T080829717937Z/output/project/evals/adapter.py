"""Current-JARVIS adapter that captures decisions before any tool side effect."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

import httpx

from app.brain.router import IntentRouter, RouterResult
from app.brain.tool_params import build_tool_params
from app.config import settings
from app.observability.tracing import start_trace, trace_span
from app.tools.registry import registry

DEFAULT_FIXTURES = Path(__file__).with_name("fixtures") / "current_deterministic.json"


class AdapterError(RuntimeError):
    """Raised when a deterministic decision cannot be produced safely."""


class LiveUnavailableError(RuntimeError):
    """Raised when the configured local Ollama router model is unavailable."""


@dataclass(frozen=True)
class EvaluationRequest:
    """Only real request data; golden IDs and expectations cannot fit here."""

    user_input: str
    context: dict[str, str | None]


@dataclass(frozen=True)
class ObservedDecision:
    mode: str
    capability: str | None
    tool_name: str | None
    params: dict[str, Any]
    safety: str
    confirmation: bool
    origin: str
    router_intent: str
    router_confidence: float
    reasoning: str
    intercepted: bool
    executed: bool
    executed_capabilities: tuple[str, ...] = ()
    trace_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SideEffectInterceptor:
    """Records selected tools but deliberately has no execution method."""

    selections: list[dict[str, Any]] = field(default_factory=list)

    def capture(self, *, tool_name: str, capability: str, params: dict[str, Any]) -> None:
        self.selections.append({"tool_name": tool_name, "capability": capability, "params": dict(params)})


class CurrentJarvisAdapter:
    """Observe current routing/params/safety while stopping before registry.call()."""

    def __init__(
        self,
        *,
        mode: str = "deterministic",
        fixtures_path: str | Path = DEFAULT_FIXTURES,
        interceptor: SideEffectInterceptor | None = None,
    ) -> None:
        if mode not in {"deterministic", "live"}:
            raise ValueError(f"Unsupported eval mode: {mode}")
        self.mode = mode
        self.interceptor = interceptor or SideEffectInterceptor()
        self._router = IntentRouter()
        self._fixtures = self._load_fixtures(fixtures_path) if mode == "deterministic" else {}
        if mode == "deterministic":
            self._router._classify_with_ollama = self._classify_with_fixture  # type: ignore[method-assign]

    def check_live_available(self) -> dict[str, Any]:
        if self.mode != "live":
            raise ValueError("Live availability is only relevant in live mode")
        url = f"{settings.models.ollama_base_url}/api/tags"
        try:
            with httpx.Client(timeout=httpx.Timeout(3.0)) as client:
                response = client.get(url)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # noqa: BLE001
            raise LiveUnavailableError(f"Ollama unavailable at {settings.models.ollama_base_url}: {exc}") from exc

        available = {
            str(item.get("name") or item.get("model") or "")
            for item in payload.get("models", [])
            if isinstance(item, dict)
        }
        configured = settings.models.router
        if not any(name == configured or name.split(":", 1)[0] == configured.split(":", 1)[0] for name in available):
            raise LiveUnavailableError(f"Configured router model '{configured}' is not installed in Ollama")
        return {"base_url": settings.models.ollama_base_url, "router_model": configured, "models": sorted(available)}

    def evaluate(self, request: EvaluationRequest) -> ObservedDecision:
        message = self._production_message(request)
        if self.mode == "deterministic":
            rules_result = self._router._classify_by_rules(message)  # noqa: SLF001
            if rules_result is None and message not in self._fixtures:
                raise AdapterError(f"No deterministic router fixture for input: {request.user_input!r}")

        origin = request.context.get("origin") or "user_direct"
        with start_trace(origin=origin, component="evals.adapter", transport="evaluation") as trace_id:
            with patch("app.brain.router.audit.log"), patch("app.tools.registry.audit.log"):
                routed = self._router.classify(message)
                decision = self._observe_routed_decision(routed, message, origin)
                return replace(decision, trace_id=trace_id)

    def _observe_routed_decision(self, routed: RouterResult, message: str, origin: str) -> ObservedDecision:
        if routed.intent == "confirm_action":
            return self._decision(routed, origin=origin, mode="confirm", safety="confirmation_required", confirmation=True)
        if routed.intent == "clarify":
            return self._decision(routed, origin=origin, mode="clarify", safety="safe_read_only")
        if routed.intent == "refuse":
            return self._decision(routed, origin=origin, mode="refuse", safety="blocked")
        if routed.intent == "vision":
            return self._observe_tool(routed, message, origin, "vision")
        if routed.intent == "use_tool" and routed.suggested_tool:
            return self._observe_tool(routed, message, origin, routed.suggested_tool)
        return self._decision(routed, origin=origin, mode="direct", safety="safe_read_only")

    def _observe_tool(
        self,
        routed: RouterResult,
        message: str,
        origin: str,
        tool_name: str,
    ) -> ObservedDecision:
        with trace_span(
            "tool_parameters",
            component="app.brain.tool_params",
            metadata={"tool": tool_name},
        ):
            params = build_tool_params(tool_name, message)
        capability = _capability_for(tool_name, params)
        params = _canonical_params(capability, params)

        module = registry.get(tool_name)
        if module is None:
            return self._decision(
                routed,
                origin=origin,
                mode="refuse",
                capability=capability,
                tool_name=tool_name,
                params=params,
                safety="blocked",
                intercepted=True,
            )

        safety_level = int(getattr(module, "SAFETY_LEVEL", 0))
        if tool_name == "shell":
            try:
                from app.tools.shell import _ensure_command_allowed

                _ensure_command_allowed(str(params.get("command") or ""))
            except PermissionError:
                self.interceptor.capture(tool_name=tool_name, capability=capability, params=params)
                return self._decision(
                    routed,
                    origin=origin,
                    mode="refuse",
                    capability=capability,
                    tool_name=tool_name,
                    params=params,
                    safety="blocked",
                    intercepted=True,
                )

        safety = _safety_for(tool_name, safety_level)
        with trace_span(
            "safety",
            component="app.tools.registry",
            metadata={
                "tool": tool_name,
                "capability": capability,
                "safety_level": safety_level,
                "parameter_keys": list(params),
            },
        ):
            confirmation_required = registry._requires_confirmation(safety_level)  # noqa: SLF001
        if safety_level >= 3:
            mode = "refuse"
            confirmation = False
        elif confirmation_required:
            mode = "confirm"
            safety = "confirmation_required"
            confirmation = True
        else:
            mode = "tool"
            confirmation = False

        self.interceptor.capture(tool_name=tool_name, capability=capability, params=params)
        return self._decision(
            routed,
            origin=origin,
            mode=mode,
            capability=capability,
            tool_name=tool_name,
            params=params,
            safety=safety,
            confirmation=confirmation,
            intercepted=True,
        )

    @staticmethod
    def _decision(
        routed: RouterResult,
        *,
        origin: str,
        mode: str,
        safety: str,
        capability: str | None = None,
        tool_name: str | None = None,
        params: dict[str, Any] | None = None,
        confirmation: bool = False,
        intercepted: bool = False,
    ) -> ObservedDecision:
        return ObservedDecision(
            mode=mode,
            capability=capability,
            tool_name=tool_name,
            params=params or {},
            safety=safety,
            confirmation=confirmation,
            origin=origin,
            router_intent=routed.intent,
            router_confidence=routed.confidence,
            reasoning=routed.reasoning,
            intercepted=intercepted,
            executed=False,
        )

    def _classify_with_fixture(self, message: str) -> str:
        fixture = self._fixtures.get(message)
        if fixture is None:
            raise AdapterError(f"No deterministic router fixture for input: {message!r}")
        return json.dumps(fixture)

    @staticmethod
    def _production_message(request: EvaluationRequest) -> str:
        content = request.context.get("content")
        if not content:
            return request.user_input
        return f"{request.user_input}\n\nContext:\n{content}"

    @staticmethod
    def _load_fixtures(path: str | Path) -> dict[str, dict[str, Any]]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or not isinstance(payload.get("router_outputs"), dict):
            raise AdapterError("Deterministic router fixture file is malformed")
        return payload["router_outputs"]


def _capability_for(tool_name: str, params: dict[str, Any]) -> str:
    if tool_name == "apps":
        return "close_app" if params.get("action") == "close" else "open_app"
    if tool_name == "browser":
        return "web_search" if params.get("action") == "search" else "browser_open"
    if tool_name == "files":
        return {"read": "file_read", "list": "file_list", "move": "file_move"}.get(
            str(params.get("action")), "file_access"
        )
    return {
        "calendar": "calendar_read",
        "screenshot": "screen_capture",
        "vision": "screen_describe",
        "web_search": "web_search",
        "shell": "shell_execute",
        "system_stats": "system_stats",
        "computer_use": "computer_control",
        "mouse_keyboard": "computer_control",
        "obsidian": "notes_access",
        "browser_use": "browser_automation",
    }.get(tool_name, tool_name)


def _canonical_params(capability: str, params: dict[str, Any]) -> dict[str, Any]:
    canonical = dict(params)
    if capability in {"open_app", "close_app"} and "app" in canonical:
        app = str(canonical["app"]).strip().casefold()
        aliases = {
            "vscode": "visual studio code",
            "vs code": "visual studio code",
            "code": "visual studio code",
            "calc": "calculator",
        }
        canonical["app"] = aliases.get(app, app)
    return canonical


def _safety_for(tool_name: str, safety_level: int) -> str:
    if safety_level >= 3:
        return "blocked"
    if safety_level >= 2:
        return "confirmation_required"
    if safety_level == 1:
        return "low_risk"
    if tool_name in {"apps", "kasa"}:
        return "low_risk"
    return "safe_read_only"
