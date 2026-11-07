"""Strict versioned schema for migration-neutral golden scenarios."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
ORIGINS = {"user_direct", "scheduled", "subagent", "derived"}
MODES = {"direct", "tool", "clarify", "refuse", "confirm"}
SAFETY_EXPECTATIONS = {"safe_read_only", "low_risk", "confirmation_required", "blocked"}
PARAM_MATCH_MODES = {"exact", "subset"}
VALUE_MATCHERS = {"exact", "normalized", "present", "absent", "one_of"}
CATEGORIES = {
    "direct_response",
    "app_control",
    "screen_vision",
    "search_research",
    "calendar",
    "habits",
    "safety",
    "clarification",
}
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ScenarioValidationError(ValueError):
    """Raised when golden data does not conform to schema version 1."""


@dataclass(frozen=True)
class ScenarioContext:
    origin: str
    content: str | None = None


@dataclass(frozen=True)
class ParameterExpectation:
    match: str = "subset"
    values: dict[str, Any] = field(default_factory=dict)
    optional: tuple[str, ...] = ()
    absent: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExpectedDecision:
    mode: str
    capability: str | None
    safety: str
    confirmation: bool
    params: ParameterExpectation | None = None
    tool_name: str | None = None


@dataclass(frozen=True)
class ProhibitedBehavior:
    capabilities: tuple[str, ...] = ()
    tool_names: tuple[str, ...] = ()
    modes: tuple[str, ...] = ()
    executed_capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class GoldenScenario:
    id: str
    version: int
    category: str
    input: str
    context: ScenarioContext
    expected: ExpectedDecision
    must_not: ProhibitedBehavior
    tags: tuple[str, ...]


def load_golden_scenarios(path: str | Path) -> list[GoldenScenario]:
    source = Path(path)
    scenarios: list[GoldenScenario] = []
    seen: set[str] = set()

    for line_number, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ScenarioValidationError(f"{source}:{line_number}: invalid JSON: {exc.msg}") from exc
        try:
            scenario = parse_scenario(raw)
        except ScenarioValidationError as exc:
            raise ScenarioValidationError(f"{source}:{line_number}: {exc}") from exc
        if scenario.id in seen:
            raise ScenarioValidationError(f"{source}:{line_number}: duplicate scenario id: {scenario.id}")
        seen.add(scenario.id)
        scenarios.append(scenario)

    if not scenarios:
        raise ScenarioValidationError(f"{source}: no scenarios found")
    return scenarios


def parse_scenario(raw: Any) -> GoldenScenario:
    data = _object(raw, "scenario")
    _keys(data, required={"id", "version", "category", "input", "context", "expected", "tags"}, optional={"must_not"})

    scenario_id = _string(data["id"], "id")
    if not _ID_RE.fullmatch(scenario_id):
        raise ScenarioValidationError("id must contain only lowercase letters, digits, and hyphens")

    version = data["version"]
    if not isinstance(version, int) or isinstance(version, bool) or version != SCHEMA_VERSION:
        raise ScenarioValidationError(f"version must be {SCHEMA_VERSION}")

    category = _string(data["category"], "category")
    if category not in CATEGORIES:
        raise ScenarioValidationError(f"unsupported category: {category}")

    user_input = _string(data["input"], "input").strip()
    if not user_input:
        raise ScenarioValidationError("input must not be empty")

    context = _parse_context(data["context"])
    expected = _parse_expected(data["expected"])
    must_not = _parse_must_not(data.get("must_not", {}))
    tags = _string_tuple(data["tags"], "tags")

    return GoldenScenario(
        id=scenario_id,
        version=version,
        category=category,
        input=user_input,
        context=context,
        expected=expected,
        must_not=must_not,
        tags=tags,
    )


def _parse_context(raw: Any) -> ScenarioContext:
    data = _object(raw, "context")
    _keys(data, required={"origin"}, optional={"content"})
    origin = _string(data["origin"], "context.origin")
    if origin not in ORIGINS:
        raise ScenarioValidationError(f"unsupported context.origin: {origin}")
    content = data.get("content")
    if content is not None:
        content = _string(content, "context.content")
    return ScenarioContext(origin=origin, content=content)


def _parse_expected(raw: Any) -> ExpectedDecision:
    data = _object(raw, "expected")
    _keys(
        data,
        required={"mode", "capability", "safety", "confirmation"},
        optional={"params", "tool_name"},
    )
    mode = _string(data["mode"], "expected.mode")
    if mode not in MODES:
        raise ScenarioValidationError(f"unsupported expected.mode: {mode}")
    capability = data["capability"]
    if capability is not None:
        capability = _string(capability, "expected.capability")
    safety = _string(data["safety"], "expected.safety")
    if safety not in SAFETY_EXPECTATIONS:
        raise ScenarioValidationError(f"unsupported expected.safety: {safety}")
    confirmation = data["confirmation"]
    if not isinstance(confirmation, bool):
        raise ScenarioValidationError("expected.confirmation must be a boolean")
    params = _parse_params(data["params"]) if "params" in data else None
    tool_name = data.get("tool_name")
    if tool_name is not None:
        tool_name = _string(tool_name, "expected.tool_name")
    return ExpectedDecision(mode, capability, safety, confirmation, params, tool_name)


def _parse_params(raw: Any) -> ParameterExpectation:
    data = _object(raw, "expected.params")
    _keys(data, required=set(), optional={"match", "values", "optional", "absent"})
    match = data.get("match", "subset")
    if match not in PARAM_MATCH_MODES:
        raise ScenarioValidationError(f"unsupported expected.params.match: {match}")
    values = _object(data.get("values", {}), "expected.params.values")
    for key, value in values.items():
        _string(key, "expected.params.values key")
        _validate_value_expectation(value, f"expected.params.values.{key}")
    optional = _string_tuple(data.get("optional", []), "expected.params.optional")
    absent = _string_tuple(data.get("absent", []), "expected.params.absent")
    if set(optional) & set(absent):
        raise ScenarioValidationError("expected.params optional and absent fields must not overlap")
    return ParameterExpectation(match=match, values=values, optional=optional, absent=absent)


def _validate_value_expectation(value: Any, location: str) -> None:
    if not isinstance(value, dict) or "matcher" not in value:
        return
    matcher = value.get("matcher")
    if matcher not in VALUE_MATCHERS:
        raise ScenarioValidationError(f"unsupported {location}.matcher: {matcher}")
    allowed = {"matcher"}
    if matcher in {"exact", "normalized"}:
        allowed.add("value")
        if "value" not in value:
            raise ScenarioValidationError(f"{location}.value is required for {matcher}")
    elif matcher == "one_of":
        allowed.add("values")
        if not isinstance(value.get("values"), list) or not value["values"]:
            raise ScenarioValidationError(f"{location}.values must be a non-empty list")
    _keys(value, required={"matcher"}, optional=allowed - {"matcher"})


def _parse_must_not(raw: Any) -> ProhibitedBehavior:
    data = _object(raw, "must_not")
    _keys(data, required=set(), optional={"capabilities", "tool_names", "modes", "executed_capabilities"})
    modes = _string_tuple(data.get("modes", []), "must_not.modes")
    unknown_modes = set(modes) - MODES
    if unknown_modes:
        raise ScenarioValidationError(f"unsupported must_not.modes: {sorted(unknown_modes)}")
    return ProhibitedBehavior(
        capabilities=_string_tuple(data.get("capabilities", []), "must_not.capabilities"),
        tool_names=_string_tuple(data.get("tool_names", []), "must_not.tool_names"),
        modes=modes,
        executed_capabilities=_string_tuple(
            data.get("executed_capabilities", []), "must_not.executed_capabilities"
        ),
    )


def _object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScenarioValidationError(f"{location} must be an object")
    return value


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str):
        raise ScenarioValidationError(f"{location} must be a string")
    return value


def _string_tuple(value: Any, location: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ScenarioValidationError(f"{location} must be a list of strings")
    if len(value) != len(set(value)):
        raise ScenarioValidationError(f"{location} must not contain duplicates")
    return tuple(value)


def _keys(data: dict[str, Any], *, required: set[str], optional: set[str]) -> None:
    missing = required - data.keys()
    if missing:
        raise ScenarioValidationError(f"missing fields: {sorted(missing)}")
    unknown = data.keys() - required - optional
    if unknown:
        raise ScenarioValidationError(f"unknown fields: {sorted(unknown)}")
