# Test Plan and Results — Task 13B11B

## 1. What is tested, and what each test is for

### `tests/execution/types_test.py` (type tests)

| Test | Proves |
|---|---|
| contract identity | spec version `v1` is recorded and the runtime status is `FOUNDATIONS_ONLY`, so "types exist" is never read as "contract active" |
| execution modes / active set | the three modes exist and only `LEGACY` is in `ACTIVE_EXECUTION_MODES` |
| 13 parametrized vocabulary cases | every enum's value set is *exactly* the contract's, and values are unique |
| `MODEL_RAW` is not operational | constructing `OperationalResponseSource("MODEL_RAW")` raises; the token exists only on the conversational enum |
| unknown values rejected | no silent coercion of an unknown enum value |
| obligation priority | ranks 1–11, all eleven obligations covered, confirmation first, missing-context last, table immutable |
| trust distinctions | `USER_REPORTED` ≠ `TOOL_SUCCESS`, and source values never collide with trust-class values |
| immutability | field assignment raises `FrozenInstanceError`; mapping contents raise `TypeError` |
| raw vs canonical arguments | both are retained on an invocation (INV-006) |
| tool result shape | `SUCCESS` with empty `facts` is legal; `TIMEOUT` is not `ERROR`; facts are read-only |
| response types | operational and conversational responses are distinct types with fixed lanes |
| `to_mapping` | JSON-serializable output with stable enum values; rejects non-dataclasses |
| module purity | `types.py` imports nothing from `app.*` and contains no I/O or transport |

### `tests/execution/config_test.py` (configuration / mode)

Covers each case the task required: key absent, explicit legacy, malformed value, unknown
future-looking value (`hermes`, `enabled`, `selected`, `test`, `control-plane`), null, whitespace and
case handling, and the real `config.yaml` and `config.yaml.example`. Also: unknown keys inside the
section are dropped, out-of-range `shadow_sample_rate` and non-boolean `hermes_brain` fall back, a
malformed section logs a warning instead of raising, and the normalizer reports *why* it fell back.
A valid `shadow` value is proven to parse — which is why the non-activation tests exist.

### `tests/execution/non_activation_test.py` (inertness)

Fails if any module under `app/` other than `app/config.py` imports `app.execution` or mentions
`ExecutionMode`, `ExecutionConfig` or `execution.mode`; asserts the four request-path modules
(`server.py`, `brain/router.py`, `brain/tool_params.py`, `tools/registry.py`) contain none of those
markers; asserts `ACTIVE_EXECUTION_MODES == {LEGACY}`, that the loaded settings sit inside it, and
that `agent.hermes_enabled` and `execution.hermes_brain` are both false.

## 2. Results (production host, `.venv` Python 3.14.4)

| Run | Before (`2d7a2ec8`) | After (`521969e`) |
|---|---|---|
| `pytest -q` (repo default markers) | 417 passed, 11 deselected | **483 passed, 11 deselected** (+66 new) |
| `pytest` with the CI marker selection | 413 passed, **3 failed** (`tests/test_vad_timeout.py`, `ModuleNotFoundError: webrtcvad` — host lacks the desktop audio dependency) | 479 passed, **the same 3 failed** |
| `python -m evals.runner --mode deterministic` | 12/20, eight named failures | **12/20, the same eight failures** |

The three CI-selection failures are a pre-existing host dependency gap, measured in both states and
unchanged by this task.

## 3. Behavioural non-change proof

The change was stashed and the golden suite plus a deterministic legacy probe were run in both
states on the same host:

* **Golden report**, normalized by removing the per-run `trace_id` and `duration_ms`, is byte-identical:
  sha256 `6a2a5fd417b54374d825a3556a2f13c91fc469ce62a0cd35ad156a6b937ac8f0` before and after, with the
  same twelve passes and the same eight failing scenario ids.
* **Legacy probe** (`probe.py`): rule-based routing for ten representative prompts, the resulting tool
  parameters, the full tool/`SAFETY_LEVEL` inventory, the confirmation thresholds for levels 0–3,
  `approval_mode`, `dry_run`, `confidence_threshold`, both prompt shapes and two response-cleaner
  outputs. Output byte-identical, sha256 `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`.

The probe executes no tool and calls no model, so the comparison is deterministic and has no side
effects.

## 4. Not tested here, by design

Routing quality, permission decisions, confirmation binding, provenance behaviour, obligation
selection, response text, shadow comparison and the eighteen conformance tests. Each belongs to the
phase that implements the component it tests; asserting them now would mean asserting against
stand-ins.
