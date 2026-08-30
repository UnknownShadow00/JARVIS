"""Deterministic grading for observed JARVIS decisions."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from evals.adapter import ObservedDecision
from evals.schema import GoldenScenario, ParameterExpectation


@dataclass(frozen=True)
class CaseGrade:
    scenario_id: str
    passed: bool
    criteria: dict[str, bool | None]
    expected: dict[str, Any]
    actual: dict[str, Any]
    failures: tuple[str, ...]
    duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def grade_scenario(scenario: GoldenScenario, actual: ObservedDecision, *, duration_ms: float) -> CaseGrade:
    expected = scenario.expected
    criteria: dict[str, bool | None] = {
        "mode": actual.mode == expected.mode,
        "capability": actual.capability == expected.capability,
        "parameters": match_parameters(expected.params, actual.params) if expected.params else None,
        "safety": actual.safety == expected.safety,
        "confirmation": actual.confirmation == expected.confirmation,
        "tool_name": actual.tool_name == expected.tool_name if expected.tool_name is not None else None,
        "must_not": _must_not_passes(scenario, actual),
    }
    failures = tuple(name for name, passed in criteria.items() if passed is False)
    return CaseGrade(
        scenario_id=scenario.id,
        passed=not failures,
        criteria=criteria,
        expected={
            "mode": expected.mode,
            "capability": expected.capability,
            "tool_name": expected.tool_name,
            "params": asdict(expected.params) if expected.params else None,
            "safety": expected.safety,
            "confirmation": expected.confirmation,
            "must_not": asdict(scenario.must_not),
        },
        actual=actual.to_dict(),
        failures=failures,
        duration_ms=round(duration_ms, 3),
    )


def match_parameters(expected: ParameterExpectation, actual: dict[str, Any]) -> bool:
    if not isinstance(actual, dict):
        return False

    for key in expected.absent:
        if key in actual:
            return False

    for key, value_expectation in expected.values.items():
        if key not in actual:
            if key in expected.optional:
                continue
            if isinstance(value_expectation, dict) and value_expectation.get("matcher") == "absent":
                continue
            return False
        if not match_value(value_expectation, actual[key]):
            return False

    if expected.match == "exact":
        absent_matchers = {
            key
            for key, value in expected.values.items()
            if isinstance(value, dict) and value.get("matcher") == "absent"
        }
        allowed = (set(expected.values) - absent_matchers) | set(expected.optional)
        required = set(expected.values) - set(expected.optional) - absent_matchers
        actual_keys = set(actual)
        if not required <= actual_keys <= allowed:
            return False
    return True


def match_value(expected: Any, actual: Any) -> bool:
    if not isinstance(expected, dict) or "matcher" not in expected:
        return actual == expected

    matcher = expected["matcher"]
    if matcher == "present":
        return actual is not None and (not isinstance(actual, str) or bool(actual.strip()))
    if matcher == "absent":
        return False
    if matcher == "exact":
        return actual == expected.get("value")
    if matcher == "normalized":
        return _normalize(actual) == _normalize(expected.get("value"))
    if matcher == "one_of":
        return any(actual == candidate for candidate in expected.get("values", []))
    return False


def aggregate_report(grades: list[CaseGrade]) -> dict[str, Any]:
    metrics = {
        "mode_accuracy": _accuracy(grades, "mode"),
        "capability_accuracy": _accuracy(grades, "capability"),
        "parameter_accuracy": _accuracy(grades, "parameters"),
        "safety_accuracy": _accuracy(grades, "safety"),
        "confirmation_accuracy": _accuracy(grades, "confirmation"),
    }
    failed_ids = [grade.scenario_id for grade in grades if not grade.passed]
    return {
        "total": len(grades),
        "passed": len(grades) - len(failed_ids),
        "failed": len(failed_ids),
        "failed_scenario_ids": failed_ids,
        "metrics": metrics,
    }


def _must_not_passes(scenario: GoldenScenario, actual: ObservedDecision) -> bool:
    prohibited = scenario.must_not
    if actual.capability in prohibited.capabilities:
        return False
    if actual.tool_name in prohibited.tool_names:
        return False
    if actual.mode in prohibited.modes:
        return False
    if set(actual.executed_capabilities) & set(prohibited.executed_capabilities):
        return False
    return True


def _accuracy(grades: list[CaseGrade], criterion: str) -> float:
    values = [grade.criteria[criterion] for grade in grades if grade.criteria[criterion] is not None]
    if not values:
        return 1.0
    return round(sum(value is True for value in values) / len(values), 4)


def _normalize(value: Any) -> str:
    text = str(value).casefold().strip()
    text = re.sub(r"[^\w\s:-]", "", text)
    return " ".join(text.split())
