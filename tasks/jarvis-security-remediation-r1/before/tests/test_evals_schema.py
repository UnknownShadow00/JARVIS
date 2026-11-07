from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals.schema import ScenarioValidationError, load_golden_scenarios, parse_scenario


GOLDEN = Path(__file__).parents[1] / "evals" / "golden.jsonl"


def _valid_scenario() -> dict:
    return {
        "id": "schema-example-001",
        "version": 1,
        "category": "direct_response",
        "input": "Hello.",
        "context": {"origin": "user_direct"},
        "expected": {
            "mode": "direct",
            "capability": None,
            "safety": "safe_read_only",
            "confirmation": False,
        },
        "tags": ["unit"],
    }


def test_golden_suite_has_exactly_twenty_unique_scenarios() -> None:
    scenarios = load_golden_scenarios(GOLDEN)
    assert len(scenarios) == 20
    assert len({scenario.id for scenario in scenarios}) == 20


def test_origin_provenance_is_representable() -> None:
    for origin in ("user_direct", "scheduled", "subagent", "derived"):
        raw = _valid_scenario()
        raw["context"] = {"origin": origin}
        assert parse_scenario(raw).context.origin == origin
    assert any(s.context.origin == "derived" for s in load_golden_scenarios(GOLDEN))


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    raw = json.dumps(_valid_scenario())
    source = tmp_path / "duplicate.jsonl"
    source.write_text(f"{raw}\n{raw}\n", encoding="utf-8")
    with pytest.raises(ScenarioValidationError, match="duplicate scenario id"):
        load_golden_scenarios(source)


@pytest.mark.parametrize(
    "mutation,error",
    [
        (lambda row: row.pop("expected"), "missing fields"),
        (lambda row: row.update(version=2), "version must be 1"),
        (lambda row: row.update(context={"origin": "browser"}), "unsupported context.origin"),
        (lambda row: row.update(unexpected=True), "unknown fields"),
    ],
)
def test_malformed_scenarios_are_rejected(mutation, error: str) -> None:
    raw = _valid_scenario()
    mutation(raw)
    with pytest.raises(ScenarioValidationError, match=error):
        parse_scenario(raw)
