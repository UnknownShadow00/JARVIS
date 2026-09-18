# Task 13B11C — Test Plan and Results

New tests live beside the P0 ones, following the repository's `tests/execution/*_test.py`
convention. 70 new tests (49 + 13 + 8); `tests/execution` totals 136.

| File | Tests | Covers |
|---|---|---|
| `tests/execution/audit_events_test.py` | 49 | vocabulary, required-field shape, raw/canonical, correlation requirements, validation, privacy, serialization |
| `tests/execution/correlation_test.py` | 13 | identifier properties, context derivation, immutability, correlation ≠ authorization |
| `tests/execution/audit_non_activation_test.py` | 8 | no live wiring, legacy audit untouched, purity, mode still legacy |

## 1. Vocabulary

The seventeen names are written out literally in the test file rather than derived from the enum,
so renaming an event fails a test instead of passing one. Asserted: exact value set; count 17;
uniqueness and no aliases; `<stage>.<transition>` shape with no model/family/harness/benchmark
substring; unknown names rejected (`turn.started`, `TURN.REQUEST`, `dispatch.invoke`, `""`,
`confirmation`); schema version 3 with legacy 2; the confirmation and invocation event groups.

## 2. Required field shape

`CONTRACT_AUDIT_FIELDS` equals the seventeen contract fields in contract order; every one is owned
by at least one event (`contract_field_coverage` returns all 17); every event declares at least one
required field and all names exist on the record; the table is immutable. A classification event is
built carrying only `request_class` and asserted to leave every other contract field `None` — the
"no dummy lies" property. Each event is then built empty and asserted to fail naming its own missing
fields. Records and their mappings are frozen, and mutating a caller's source dict afterwards does
not change the record.

## 3. Correlation

Identifiers are non-empty, 32 hex characters, well-formed, and 1,000 consecutive mints per class are
distinct. Malformed values are rejected. A context round-trips through JSON. The context is frozen.
A child preserves the parent `session_id` and `turn_id`, leaves the parent untouched, and an
invocation id is distinct from a confirmation id. `CorrelationContext` has exactly four fields and
no permission/confirmed/approved/trusted/authorized/executed attribute — correlation is not
authorization. Identifiers contain no fragment of a sample prompt, path, host or model name.

## 4. Serialization

The envelope has exactly the six legacy keys, `trace_id` carries the turn id, `json.dumps` is stable
across calls, every sample round-trips through `json.loads`, enums serialize as their stable string
values, unset fields are omitted rather than written as `null`, and a `detail` block that tries to
override the event type, mode, turn id and permission outcome loses to the top-level fields.
Representative records are built for every stage in the vocabulary — request, classification,
routing, proposal, guard, permission, confirmation created/confirmed/expired, dispatch invoked and
result, provenance write, obligation, operational and conversational response, and turn summary —
and serialized to JSONL lines (written only to `tmp_path`, never to a production log).

## 5. Privacy

Static: no field of the record contains `chain_of_thought`, `scratchpad`, `reasoning` or
`monologue`, and `FORBIDDEN_REASONING_FIELDS` contains the four names the task lists plus the two
the contract yaml forbids. Dynamic: a payload key matching a forbidden name is rejected at any
depth, in mappings, in lists and inside `detail`, after normalization — so `chainOfThought` and
`chain-of-thought` are caught too. A blocked draft is proven recordable as digest + truncated
excerpt with a `TRUNCATED` marker, and an unselected draft as a digest with `NOT_RETAINED` and no
text at all.

## 6. No live wiring

No module outside `app/execution/` names any of the nine new symbols; there are zero
`to_audit_entry(` / `ExecutionAuditRecord(` call sites in `app/`; the legacy audit source contains
no reference to the new package; an AST walk proves the only `"schema_version"` literal written by
`app/logs/audit.py` is `2`; the two new modules import nothing beyond the standard library and
`app.execution.*`, and contain no `open`/`eval`/`exec`/`__import__` call; building and serializing a
record with the legacy writer monkeypatched to raise proves the foundation never reaches it; and
`settings.execution.mode` is still `LEGACY` with `hermes_brain` and `hermes_enabled` both false.

## 7. Results (production venv, Python 3.14.4)

| Run | Before (521969e) | After (eb4c5db) |
|---|---|---|
| `pytest -q` | 483 passed, 11 deselected, 0 failed | **553 passed, 11 deselected, 0 failed** |
| `tests/execution` | 66 passed | 136 passed |
| `evals.runner --mode deterministic` | 12 passed / 8 failed | **12 passed / 8 failed, same eight IDs** |
| legacy probe (13B11B fixture) | sha256 `fc68a0b0…` | **sha256 `fc68a0b0…` — byte-identical** |

No new failures, expected or otherwise. The 13B11B report mentioned three CI-marker failures from a
`webrtcvad` host dependency gap; they did not appear in either run here — collection is
553/564 with 11 deselected by the `pytest.ini` marker expression, before and after.

The eight known golden failures are unchanged: `calendar-move-event-002`, `habit-status-001`,
`habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.
