from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from unittest.mock import patch

from evals.adapter import CurrentJarvisAdapter, EvaluationRequest, ObservedDecision
from evals.runner import build_report, run_scenarios, write_report
from evals.schema import load_golden_scenarios


GOLDEN = Path(__file__).parents[1] / "evals" / "golden.jsonl"


def test_evaluation_request_cannot_contain_golden_metadata() -> None:
    assert {item.name for item in fields(EvaluationRequest)} == {"user_input", "context"}


def test_deterministic_adapter_intercepts_every_selected_tool() -> None:
    scenarios = load_golden_scenarios(GOLDEN)
    adapter = CurrentJarvisAdapter(mode="deterministic")

    with (
        patch("app.tools.registry.registry.call", side_effect=AssertionError("tool execution attempted")),
        patch("subprocess.run", side_effect=AssertionError("shell execution attempted")),
        patch("subprocess.Popen", side_effect=AssertionError("process launch attempted")),
        patch("webbrowser.open", side_effect=AssertionError("browser launch attempted")),
        patch("httpx.Client", side_effect=AssertionError("network request attempted")),
    ):
        grades = run_scenarios(scenarios, adapter)

    assert len(grades) == 20
    assert all(not grade.actual["executed"] for grade in grades)
    assert all(not grade.actual["executed_capabilities"] for grade in grades)
    assert len({grade.actual["trace_id"] for grade in grades}) == 20
    assert adapter.interceptor.selections


def test_destructive_shell_is_blocked_before_execution() -> None:
    scenario = next(
        item
        for item in load_golden_scenarios(GOLDEN)
        if item.id == "safety-shell-destructive-003"
    )
    adapter = CurrentJarvisAdapter(mode="deterministic")
    grade = run_scenarios([scenario], adapter)[0]
    assert grade.passed
    assert grade.actual["mode"] == "refuse"
    assert grade.actual["safety"] == "blocked"
    assert grade.actual["executed"] is False


def test_runner_passes_only_real_request_data_to_adapter() -> None:
    scenario = load_golden_scenarios(GOLDEN)[:1]

    class RecordingAdapter:
        request: EvaluationRequest | None = None

        def evaluate(self, request: EvaluationRequest) -> ObservedDecision:
            self.request = request
            return ObservedDecision(
                mode="direct",
                capability=None,
                tool_name=None,
                params={},
                safety="safe_read_only",
                confirmation=False,
                origin=request.context["origin"] or "user_direct",
                router_intent="respond",
                router_confidence=1.0,
                reasoning="recorded",
                intercepted=False,
                executed=False,
            )

    adapter = RecordingAdapter()
    run_scenarios(scenario, adapter)
    assert adapter.request is not None
    assert vars(adapter.request) == {
        "user_input": scenario[0].input,
        "context": {"origin": "user_direct", "content": None},
    }
    assert "expected" not in vars(adapter.request)
    assert "id" not in vars(adapter.request)


def test_report_generation_is_machine_readable(tmp_path: Path) -> None:
    scenarios = load_golden_scenarios(GOLDEN)
    grades = run_scenarios(scenarios, CurrentJarvisAdapter(mode="deterministic"))
    report = build_report(mode="deterministic", scenarios=scenarios, grades=grades)
    output = write_report(report, tmp_path / "nested" / "report.json")
    decoded = json.loads(output.read_text(encoding="utf-8"))
    assert decoded["suite"] == "golden-v1"
    assert decoded["total"] == 20
    assert len(decoded["cases"]) == 20
