# Task 13B11D — Test Plan and Results

89 new tests (81 + 8); `tests/execution` totals 225.

| File | Tests | Covers |
|---|---|---|
| `tests/execution/provenance_test.py` | 81 | records, source/trust matrix, corrections, attribution, tool results, timeout, history, isolation, model non-authority, serialization |
| `tests/execution/provenance_non_activation_test.py` | 8 | no live wiring, request-path ignorance, purity, no duplicate vocabulary, mode unchanged |

## 1. Basic records

One test per source: `USER_FACT` and `USER_REPORTED` are `SUPPLIED` with no invocation id;
`TOOL_SUCCESS` is `VERIFIED` and bound to the result's invocation; `TOOL_ERROR` is `VERIFIED`,
keyed `<tool>_error` and carries the structured error; `CONFIRMATION_REQUIRED` is `CONTROL` with
`executed: False`. A caller passing `executed: True` in the confirmation detail is overridden. The
control-state helper accepts the three control sources and refuses the other five. Records are
frozen, their mapping values read-only, and mutating the caller's dict afterwards does not reach the
stored record.

## 2. Source / trust compatibility

The full matrix is exercised: 8 sources × 3 trust classes = **24 parametrized cases**, 8 accepted
and 16 refused with `must carry trust` naming the expected class. Separately: a tool source without
an invocation id is refused, and a `USER_FACT` carrying one is refused — a supplied value cannot
borrow tool correlation. Validation also covers malformed record ids, naive timestamps, a
`SUPERSEDED` record with no `superseded_by`, a `CURRENT` record that names one, and a raw string
where the source enum belongs. Fact keys are checked over eight bad inputs and five good ones.

## 3. Corrections and supersession

A correction makes the newer value current, keeps the older one as `SUPERSEDED` with
`superseded_by` pointing at its replacement, and leaves the caller's original object untouched.
Four successive corrections form a verified chain. A user correction **does not** supersede a tool
observation — both stand, `current()` raises `AmbiguousProvenance`, and each class is retrievable by
name. A newer observation supersedes only the older observation. Recording the same value again
supersedes by key, keeping both records. Correcting one key leaves other keys current.

## 4. Attribution

A user report never becomes a tool observation: the verified view of the same key stays `None`, and
repeating it keeps it `SUPPLIED`. A supplied value is queryable with its source and trust intact. A
ledger holding all five source kinds exposes each one's trust class directly — no string parsing.

## 5. Tool results

Only the returned `facts` are recorded, one record per key, nothing inferred. A `SUCCESS` with empty
`facts` records nothing at all. A `TOOL_ERROR` adds one invocation-scoped record and nothing about
installation, the filesystem or the package manager, and creates no success provenance. Two errors
from different invocations supersede by key with both retained. A mapping shaped like a
`TrustedToolResult` is refused and leaves the ledger empty.

## 6. Timeout and the other non-grounding statuses

`TIMEOUT`, `BLOCKED` and `CONFIRMATION_REQUIRED` are parametrized: each raises, each leaves the
ledger empty, and the facts the refused result claimed are absent. A timeout is asserted to be
neither success nor error, to remain distinct from `ERROR`, and to be outside `GROUNDING_STATUSES`,
which is exactly `{SUCCESS, ERROR}`.

## 7. History, snapshots and isolation

History is newest-first and complete; supersession deletes and edits nothing; every return is a
tuple a caller cannot mutate; a snapshot holds only current records and does not follow later
writes. Two sessions with the same fact key never share a value, a record cannot be appended to
another session's ledger, and the store creates one ledger per session, drops it on request and
starts clean afterwards. The module exposes no shared global ledger or store.

## 8. Model non-authority

No name the module defines contains "model" or "draft"; the five recorders are exactly the
source-explicit ones; `from_model_text`, `trust_model_claim`, `record_model_fact`, `from_draft` and
`promote` are all absent. A `ModelDraft` and a `ToolProposal` are both refused as fact values. Model
prose recorded deliberately as a user fact stays `SUPPLIED`. No recorder's signature accepts
`trust_class`. Unsupported value types are refused.

## 9. Serialization and audit compatibility

A record serializes to the eleven stable field names with enums as strings and an ISO-8601
timestamp, round-trips through JSON, and the returned dict is a copy. A snapshot serializes and
contains no reasoning-shaped field. One test feeds `to_audit_payload` straight into a P1
`provenance.write` audit record and asserts the resulting entry carries the record id and trust
class and round-trips — compatibility proven without emitting anything.

## 10. No live wiring

No module outside `app/execution/` names any of ten ledger symbols; there are zero
`ProvenanceLedger(`, `LedgerStore(`, `.record_user_fact(` or `.record_tool_result(` sites in `app/`;
`server.py`, `router.py`, `tool_params.py`, `response_cleaner.py`, `registry.py`, `safety.py`,
`resource_manager.py` and `logs/audit.py` contain no reference to provenance or the execution
package; the module imports only the standard library plus `app.execution.types` and
`app.execution.correlation`, with no `eval`/`exec`/`open`/`__import__`; it defines no duplicate of
the P0 enums; provenance ids validate with the P1 validator; building a ledger with the legacy audit
writer monkeypatched to raise proves it is never called; and the execution mode and both Hermes
flags are re-asserted.

## 11. Results (production venv, Python 3.14.4)

| Run | Before (eb4c5db) | After (b9a557b) |
|---|---|---|
| `pytest -q` | 553 passed, 11 deselected, 0 failed | **642 passed, 11 deselected, 0 failed** |
| `tests/execution` | 136 passed | 225 passed |
| `evals.runner --mode deterministic` | 12 passed / 8 failed | **12 passed / 8 failed, same eight IDs** |
| legacy probe (13B11B/C fixture) | sha256 `fc68a0b0…` | **sha256 `fc68a0b0…` — byte-identical** |

Collection 642/653 with 11 deselected by the `pytest.ini` marker expression, unchanged. No new
failures of any kind. The eight known golden failures are unchanged: `calendar-move-event-002`,
`habit-status-001`, `habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.
