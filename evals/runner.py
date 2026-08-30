"""CLI and report writer for JARVIS golden evaluations."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from evals.adapter import (
    AdapterError,
    CurrentJarvisAdapter,
    EvaluationRequest,
    LiveUnavailableError,
    ObservedDecision,
)
from evals.grader import CaseGrade, aggregate_report, grade_scenario
from evals.schema import GoldenScenario, load_golden_scenarios

DEFAULT_GOLDEN = Path(__file__).with_name("golden.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/evals")


class DecisionAdapter(Protocol):
    def evaluate(self, request: EvaluationRequest) -> ObservedDecision: ...


def run_scenarios(scenarios: list[GoldenScenario], adapter: DecisionAdapter) -> list[CaseGrade]:
    grades: list[CaseGrade] = []
    for scenario in scenarios:
        request = EvaluationRequest(
            user_input=scenario.input,
            context={"origin": scenario.context.origin, "content": scenario.context.content},
        )
        started = time.perf_counter()
        decision = adapter.evaluate(request)
        duration_ms = (time.perf_counter() - started) * 1000
        grades.append(grade_scenario(scenario, decision, duration_ms=duration_ms))
    return grades


def build_report(*, mode: str, scenarios: list[GoldenScenario], grades: list[CaseGrade]) -> dict[str, Any]:
    return {
        "suite": "golden-v1",
        "schema_version": 1,
        "mode": mode,
        "generated_at": datetime.now(UTC).isoformat(),
        **aggregate_report(grades),
        "cases": [grade.to_dict() for grade in grades],
        "scenario_count_loaded": len(scenarios),
    }


def write_report(report: dict[str, Any], output: str | Path) -> Path:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def select_scenarios(
    scenarios: list[GoldenScenario],
    *,
    cases: str,
    case_ids: list[str],
) -> list[GoldenScenario]:
    requested = set(case_ids)
    if cases != "all":
        requested.update(item.strip() for item in cases.split(",") if item.strip())
    if not requested:
        return scenarios
    known = {scenario.id for scenario in scenarios}
    missing = requested - known
    if missing:
        raise ValueError(f"Unknown scenario IDs: {sorted(missing)}")
    return [scenario for scenario in scenarios if scenario.id in requested]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run migration-neutral JARVIS golden evaluations")
    parser.add_argument("--mode", choices=("deterministic", "live"), default="deterministic")
    parser.add_argument("--golden", default=str(DEFAULT_GOLDEN), help="Golden JSONL path")
    parser.add_argument("--cases", default="all", help="all or a comma-separated list of scenario IDs")
    parser.add_argument("--case", action="append", default=[], dest="case_ids", help="Run one scenario ID")
    parser.add_argument("--output", help="Machine-readable JSON report path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        all_scenarios = load_golden_scenarios(args.golden)
        scenarios = select_scenarios(all_scenarios, cases=args.cases, case_ids=args.case_ids)
        adapter = CurrentJarvisAdapter(mode=args.mode)
        if args.mode == "live":
            availability = adapter.check_live_available()
            print(f"Live router: {availability['router_model']} at {availability['base_url']}")
        grades = run_scenarios(scenarios, adapter)
        report = build_report(mode=args.mode, scenarios=scenarios, grades=grades)
    except LiveUnavailableError as exc:
        print(f"LIVE BASELINE PENDING — OLLAMA/MODEL UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    except (AdapterError, OSError, ValueError) as exc:
        print(f"EVAL HARNESS ERROR: {exc}", file=sys.stderr)
        return 2

    output = args.output or DEFAULT_OUTPUT_DIR / f"golden-v1-{args.mode}.json"
    target = write_report(report, output)
    print(
        f"HARNESS PASS — {report['total']} scenarios graded; "
        f"current product baseline: {report['passed']} passed, {report['failed']} failed"
    )
    if report["failed_scenario_ids"]:
        print("Failed scenario IDs: " + ", ".join(report["failed_scenario_ids"]))
    print(f"Report: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
