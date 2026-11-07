# JARVIS Golden Evaluations

The golden evaluation harness measures the same product expectations across the current JARVIS, a future Hermes-based implementation, and later model or tool-runtime changes. It records product gaps without changing production behavior to hide them.

> Never change production behavior simply to make the golden suite pass. A failed eval is evidence.

## Architecture and safety

The flow is:

```text
golden scenario
  -> current-JARVIS adapter
  -> real router and parameter/safety policy
  -> side-effect interceptor
  -> deterministic grader
  -> JSON report
```

The adapter calls the production router, parameter builder, tool metadata, confirmation policy, and pure shell deny-list validation. It deliberately stops before `ToolRegistry.call()`. It cannot launch applications, control input devices, run shell commands, delete files, shut down the host, send network requests for tools, or write calendar/habit data.

Golden IDs and expected results never enter the evaluated request. Production-facing input contains only the user text and real request context (`origin` and optional derived content).

## Schema

[`evals/golden.jsonl`](../evals/golden.jsonl) contains one strict schema-version-1 JSON object per line:

- `id`: stable, implementation-neutral scenario ID.
- `version`: schema version; currently `1`.
- `category`: product area.
- `input`: user-visible request.
- `context`: `origin` (`user_direct`, `scheduled`, `subagent`, or `derived`) and optional `content`.
- `expected`: response `mode`, capability, safety expectation, confirmation decision, optional implementation `tool_name`, and optional parameter rules.
- `must_not`: prohibited capabilities, internal tools, modes, or executed capabilities.
- `tags`: filters and product metadata.

Expected response modes are `direct`, `tool`, `clarify`, `refuse`, and `confirm`. Safety values are `safe_read_only`, `low_risk`, `confirmation_required`, and `blocked`.

Parameter rules support exact or subset object matching. Individual values may use exact equality or the `exact`, `normalized`, `present`, `absent`, and `one_of` matchers. Fields may also be optional or explicitly absent. Prefer deterministic matching; do not add fuzzy model-based graders unless a future requirement makes them unavoidable.

`capability` is the stable product contract. `tool_name`, when present, is an optional assertion about the current implementation and should not be used for migration-neutral requirements.

## Running evaluations

Deterministic CI mode uses the production rules first and checked-in router outputs only where a model response is necessary. It makes no Ollama or tool network request:

```bash
python -m evals.runner --mode deterministic
```

Run one or several cases and choose a report path:

```bash
python -m evals.runner --mode deterministic --case app-open-vscode-001
python -m evals.runner --mode deterministic --cases app-open-vscode-001,safety-shell-destructive-003 --output /tmp/jarvis-evals.json
```

Live mode uses the configured local Ollama router while retaining the same side-effect interception:

```bash
python -m evals.runner --mode live
```

Live mode checks the configured Ollama endpoint and router model first. It exits clearly when either is unavailable and never downloads a model.

Reports default to `artifacts/evals/`, which Git ignores. Each report includes per-case expectations, observations, criteria, failures, and duration, plus aggregate totals and separate mode, capability, parameter, safety, and confirmation accuracy. Product failures are informational in this first suite; malformed data, harness errors, or side-effect-boundary regressions fail the harness.

## Adding a scenario

1. Add one unique line to `evals/golden.jsonl` using a stable capability rather than coupling the expectation to a current function name.
2. Include the real provenance in `context.origin` and any untrusted derived content in `context.content`.
3. Describe side effects in `must_not`, especially for safety scenarios.
4. Add a deterministic router fixture only when the production rules require a model decision. A fixture represents the current router observation, not the desired answer.
5. Run the harness tests and all 20+ deterministic cases.

The golden set is the comparison contract for pre- and post-Hermes measurements. Expected answers remain in the evaluation layer, and no production code may special-case scenario IDs.
