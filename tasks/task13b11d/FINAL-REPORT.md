# JARVIS V2 — Task 13B11D Final Report
## Provenance ledger foundation (production phase P2)

## 1. Verdict

**JARVIS PROVENANCE LEDGER FOUNDATION IMPLEMENTED**

The production provenance model and ledger exist as a passive, contract-conformant foundation. The
legacy runtime neither writes to nor reads from it: no production code outside `app/execution/`
creates a ledger, records a fact or looks one up, no tool result reaches it, the legacy audit writer
is byte-identical to baseline, the golden suite is unchanged and the deterministic legacy probe is
byte-identical before and after.

## 2. Prerequisite verification

* Production `/home/jarvis/JARVIS` began at `eb4c5db1985033f2c7464fbd1bd3ae9a385199d0` (parent
  `521969e051f5cd725415fded0fbc8221e41c842f`), branch `main`, clean, 0 untracked, 1 worktree.
* Effective config at entry: `execution.mode: legacy`, `execution.hermes_brain: false`,
  `agent.hermes_enabled: false`, `safety.dry_run: false`.
* Hermes `/home/jarvis/.hermes-poc/hermes-agent` at `2237be355906fbe6065ce1815711eee52b2d646e`,
  clean, 0 processes running.
* Workspace `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS` at `77d621b8…`
  (`docs: record task 13B11C audit foundations`), clean.
* 13B11C evidence: **36 files, 35 entries**, `SHA256SUMS` sha256
  `586db4bbe7254ad8c3ef07ad40dc8871ee8aa9a9eff4178bc870d071877b9a54` — matching the canonical digest
  recorded in `tasks/loop-log.md`, not a conversational note — 0 self-references, **35 OK, 0 failed**.
* 13B11B evidence reverified: 32 files, 31 entries, `3e88750c…`, **31 OK, 0 failed**.
  13B10D contract evidence: `76f64108…`, 0 failed. No prior bundle was modified.
* Normative sources read: contract §3.2, §3.3, §9.3, §10, §16, §18.1-§18.4, §19, the machine-readable
  `agent-execution-contract.yaml`, the 20 invariants, CT-006 and CT-007, `IMPLEMENTATION_BOUNDARIES.md`;
  13B11A `PROVENANCE_PLAN.md`, `TOOL_INVOCATION_CONTRACT.md`, `AUDIT_PLAN.md`,
  `TARGET_COMPONENT_MAP.md`, `IMPLEMENTATION_PHASES.md`, `DEPENDENCY_GRAPH.md`,
  `PRODUCTION_INTEGRATION_PLAN.md`, `CONFIRMATION_STATE_PLAN.md`; the P0 `types.py` and the P1
  audit/correlation modules. No material conflict with contract v1 was found.

## 3. Production baseline

`eb4c5db…`, Python 3.14.4 venv, 87 python files under `app/`, `app` tree sha256 `66638dd3…`,
`config.yaml` `247633cb…`, `app/execution/types.py` `881eda40…`, `audit_events.py` `cac2b32c…`,
`correlation.py` `664e1a96…`. JARVIS not running; shared Ollama `{"models":[]}`.

## 4. P1 audit/correlation dependency verification

The P1 identifier family was reused, not duplicated: `SessionId`, `TurnId`, `InvocationId`,
`ConfirmationId`, `AuditEventId` already existed, and P2 added `ProvenanceRecordId` with
`new_provenance_record_id()` — the same `uuid4().hex` generator, validated by the same
`is_well_formed_id()`. 13B11C deferred exactly this identifier to P2; that deferral is now closed.
`CorrelationContext`, `is_well_formed_id` and `utc_now` are all consumed. A test feeds
`to_audit_payload()` straight into a P1 `provenance.write` record and asserts the resulting entry
carries the record id and trust class and round-trips through JSON — compatibility proven with no
emission.

## 5. Production files changed

Commit `b9a557b4460daf240cc26f6ae932db476a5c4315` — 4 files, **1,639 insertions, 0 deletions**:

| File | Change |
|---|---|
| `app/execution/provenance.py` | new (646) |
| `app/execution/correlation.py` | **+9**, additive: `ProvenanceRecordId` and its generator |
| `tests/execution/provenance_test.py` | new (819) |
| `tests/execution/provenance_non_activation_test.py` | new (165) |

`git diff --diff-filter=M` excluding `correlation.py` is empty: no other existing file was touched.

## 6. Provenance record model

The record is the one frozen in P0 — `app/execution/types.py::ProvenanceRecord` — not a new type.
It carries `record_id`, `session_id`, `turn_id`, `fact_key`, `value`, `source`, `trust_class`,
`created_at`, `status`, `invocation_id` and `superseded_by`, which covers contract §9.3's required
key / value / source / originating turn / current-or-superseded, plus the trust class, the session
scope and the invocation binding. Records are frozen with read-only mapping values; supersession
replaces the stored record with a new version rather than mutating it, so a reference a caller holds
never changes underneath them.

## 7. Provenance source semantics

All eight frozen `ProvenanceSource` members are used and kept distinct: `USER_FACT` (the user
supplied a value), `USER_REPORTED` (the user reported an observation), `TOOL_SUCCESS` (an authorized
dispatcher observed it), `TOOL_ERROR` (an authorized dispatcher saw *that invocation* fail),
`CONFIRMATION_REQUIRED` (approval needed, nothing ran), and the three control-plane states
`ROUTER_STATE`, `CAPABILITY_STATE`, `CORRECTION_STATE`. Each has its own helper; none can be reached
through another. There is no "unverified" source, because in this model the absence of a record is
what means "no trusted operational assertion exists" — a lookup simply returns nothing.

## 8. Trust semantics

`USER_FACT` and `USER_REPORTED` are `SUPPLIED` and never imply independent verification, however
often they are repeated. `TOOL_SUCCESS` and `TOOL_ERROR` are `VERIFIED` and can only be created from
a real `TrustedToolResult` instance. The control sources are `CONTROL`. **No public helper accepts a
caller-supplied `trust_class`** — it is always derived from the source — and there is no
`from_model_text`, `trust_model_claim`, `record_model_fact`, `from_draft` or `promote` API. A test
asserts no name the module defines contains "model" or "draft", and that the recorders are exactly
the five source-explicit ones.

## 9. Source/trust compatibility

One production location, `provenance.SOURCE_TRUST`, a read-only mapping; no scattered if/else. The
full 8 × 3 matrix is exercised as **24 parametrized test cases**: 8 accepted, 16 refused with the
expected class named. `TOOL_SUCCESS`/`TOOL_ERROR` require a well-formed invocation id; every other
source must not carry one, so a supplied value cannot borrow tool correlation to look observed.

## 10. Ledger scope

In memory, per conversation session — the scope the integration plan selected and the shape the
C3/C4/C5 runs actually measured. No database, no file, no JSONL mirror, no migration; a JSONL mirror
and cross-restart survival are deferred. Provenance does not survive a process exit in v1, so a
later response layer must read an empty ledger as "not available in this context" rather than
"nothing is true".

## 11. Ledger / session identity

`ProvenanceLedger(session_id)` holds one session; `LedgerStore` maps session id to ledger with
`for_session`, `get`, `sessions`, `drop` and `clear`. Neither is instantiated at import, so there is
no process-global fact dictionary — a test asserts the module exposes no `ProvenanceLedger` or
`LedgerStore` instance. A record whose `session_id` does not match is refused by `_append`. Session
ids are the opaque P1 identifiers; no user secret is encoded in a ledger key.

## 12. Fact-key model

`^[a-z][a-z0-9_]*$`, at most 128 characters — small, predictable, no ontology framework. The value
lives in the record, never in the key. `TOOL_SUCCESS` keys come straight from the keys the tool
returned, so a tool returning a key outside that shape is refused rather than silently rewritten;
`TOOL_ERROR` uses `<tool_name>_error`. No benchmark-only key is hardcoded in production.

## 13. Current-value lookup

`current_records(key)` returns every current record, newest first. `current(key)` returns the whole
record — with its source, trust class, turn id and timestamp — not a bare value; there is
deliberately **no** value-only accessor, because returning a bare value would drop exactly the
attribution §16 forbids losing. `current(key, trust_class=…)` narrows to one class.

## 14. Correction semantics

Recording a value supersedes the previous current record of the same key **and the same trust
class**, marks it `SUPERSEDED` with `superseded_by` naming its replacement, and appends the new
record as `CURRENT` (§10.1, INV-007, INV-019). A user correction therefore never supersedes a tool
observation, and a newer observation never erases what the user said — both stand, each attributed,
and the response layer says which is which. A correction changes only the supplied value: after
"port 8000 → 8080" the verified view of that key is `None`, so nothing in the ledger can be read as
a service restarting, a listener moving or health being verified (§10.2).

When a supplied value and a verified observation both stand, `current(key)` raises
`AmbiguousProvenance` naming the competing classes rather than choosing — that preference is §16
response policy owned by P6.

## 15. Supersession / history behaviour

Append-only. Nothing is deleted, no stored value is edited, and the original record object handed to
a caller is never mutated. `history(key)` returns every record ever written for the key, newest
first; `all_records()` the whole session, oldest first; `snapshot()` an immutable view of the current
facts that does not follow later writes. Every return is a tuple, so a caller cannot mutate ledger
history by editing what it was handed. A four-step correction chain is verified link by link.

## 16. Same-value update behaviour

Supersession is keyed, not value-compared: recording the same value again creates a new record,
supersedes the previous one, and keeps both in history with identical values and different ids. This
follows the integration plan's rule as written ("supersedes an earlier CURRENT record with the same
`fact_key`") and keeps "when did the user last say this" auditable. Tested explicitly.

## 17. USER_FACT handling

`record_user_fact(turn_id, fact_key, value)` → `USER_FACT` / `SUPPLIED`, no invocation id, requiring
the turn correlation. Queryable as the current supplied value while carrying no verified trust: the
verified view of the same key stays `None`.

## 18. USER_REPORTED handling

`record_user_reported(...)` → `USER_REPORTED` / `SUPPLIED`, for claims like "the API returned 503
according to my monitoring". It stays attributed for life; repeating it keeps it `SUPPLIED`, and
there is no helper of any kind that converts it into `TOOL_SUCCESS` (CT-007, INV-008).

## 19. TOOL_SUCCESS handling

`record_tool_result` requires a real `TrustedToolResult` — a mapping shaped like one is refused
(§18.1) — preserves the invocation id and tool identity, and records **one record per key the result
explicitly returned and nothing else**. A `SUCCESS` with empty `facts` records nothing at all, which
makes the minimal-result principle structural rather than a matter of wording (§18.4). No dispatcher
is called anywhere; the tests construct results by hand.

## 20. TOOL_ERROR handling

One invocation-scoped record under `<tool>_error`, carrying the invocation id, tool name, error kind
and message. It grounds that *this* invocation failed and no more: after an `app_not_found`, the
ledger holds nothing about installation state, the filesystem or the package manager, and no success
provenance exists (§18.3). Two errors from different invocations supersede by key with both retained.

## 21. TIMEOUT handling

`GROUNDING_STATUSES` is exactly `{SUCCESS, ERROR}`. `TIMEOUT` is refused with a named error and
records **nothing** — it is never folded into `TOOL_ERROR` and never becomes a success, because the
side effect may or may not have happened and the dispatcher cannot support either claim.
`BLOCKED` and `CONFIRMATION_REQUIRED` are refused on the same grounds. All three are parametrized in
the tests and each leaves the ledger empty with the claimed facts absent. Those outcomes remain
auditable as P1 `dispatch.result` events; they simply never become facts. No new provenance source
was invented for them — see §56.

## 22. CONFIRMATION_REQUIRED handling

`record_confirmation_required(...)` → `CONFIRMATION_REQUIRED` / `CONTROL`, with `executed: False`
forced into the stored value; a caller passing `executed: True` in the detail is overridden, so the
record can never be read as evidence that the action happened. No confirmation state machine,
binding, expiry or denial logic was implemented, and no model prose can create or satisfy this
record.

## 23. Correlation / ID reuse

One identifier scheme. `ProvenanceRecordId` joins `SessionId`, `TurnId`, `InvocationId`,
`ConfirmationId` and `AuditEventId` in `app/execution/correlation.py`, minted by the same generator
and validated by the same `is_well_formed_id()`. 1,000 generated record ids were verified as 32 hex
characters, all distinct, containing no secret, prompt fragment, path, host or model name.

## 24. Audit compatibility

`to_audit_payload(record)` returns the JSON-safe mapping a future `provenance.write` event will
carry, reusing the contract's own `to_mapping`. A test builds a real P1 `ExecutionAuditRecord` with
that payload in `provenance_updates` and asserts the serialized entry carries the record id and
trust class. **No audit event is emitted**: `to_audit_entry(` and `ExecutionAuditRecord(` still have
zero call sites outside `audit_events.py`, `app/logs/audit.py` is byte-identical, and
`provenance.py` contains zero references to `app.logs` or `audit.log(`.

## 25. Serialization

Eleven stable field names; enums as their string values; ISO-8601 UTC timestamps; read-only mappings
converted to plain dicts; a fresh dict each call, so editing the payload cannot reach the stored
record. Round-trips through `json.dumps`/`json.loads`. `LedgerSnapshot.to_mapping()` wraps the
session id and a list of payloads. No filesystem persistence of any kind.

## 26. Privacy / no-CoT proof

The provenance API cannot store hidden reasoning: values are stored only when explicitly passed to a
recorder, a `ModelDraft` and a `ToolProposal` are both refused as values, and no full prompt or
conversation is copied anywhere. A serialized snapshot is asserted to contain no
`chain_of_thought`, `hidden_reasoning`, `scratchpad` or `reasoning` substring. The P1 forbidden-key
scan continues to apply to any future `provenance.write` event carrying these payloads. Redaction
before persistent storage remains a later concern — see §28.

## 27. Deferred lane-field decision

Untouched and still open. The frozen P1 audit field vocabulary was **not** altered: `app/execution/
audit_events.py` is byte-identical to its baseline (`cac2b32c…`), schema version 3 is unchanged, and
`lane` remains a supporting field rather than one of the seventeen. Whether it is promoted, or
carried in an event payload, or settled in a future schema revision, is left to the operator.

## 28. Deferred redaction-key decision

Untouched and still open. No redaction engine was implemented in P2. The passive markers from P1
(`RedactionMarker`, `RedactionReason`) remain unused. Which keys must be treated as secret is still
an operator decision, and the documentation states that redaction happens before persistent
audit/provenance storage where required.

## 29-35. Tests

89 new tests (81 + 8); `tests/execution` totals 225. Records and validation failures (§37);
corrections including multi-step chains, correction-vs-observation and same-value (§38); attribution,
including that a user report cannot become verified and a supplied value carries no verified trust
(§39); tool success with only-returned-facts, empty-facts-records-nothing and a refused look-alike
mapping (§40); tool error staying invocation-scoped with no unrelated state and no success
provenance (§41); timeout and the other non-grounding statuses parametrized (§42); history, ordering,
immutability of returned collections and snapshot independence (§43); two sessions never sharing a
fact, cross-session append refused, store drop/clear (§44); model non-authority by API surface,
by rejected `ModelDraft`/`ToolProposal` values and by signature inspection (§45). Full detail in
`TEST_PLAN.md`.

## 36. No-live-wiring proof

`ProvenanceLedger(` **0**, `LedgerStore(` **0**, `.record_user_fact(` **0**, `.record_tool_result(`
**0** outside `provenance.py`; the string `provenance` appears **0** times in `app/` outside the
execution package; `app.execution` outside the package is still the single P0 import at
`app/config.py:14`. `server.py`, `router.py`, `tool_params.py`, `response_cleaner.py`, `registry.py`,
`safety.py`, `resource_manager.py` and `logs/audit.py` contain no reference to provenance. A test
builds a ledger and records a fact with the legacy audit writer monkeypatched to raise, proving it is
never called. Behavioural confirmation: the legacy probe is byte-identical.

## 37. Existing test-suite result

`pytest -q` in the production venv: **553 passed → 642 passed**, 11 deselected, 0 failed, both runs.
The 89 new tests are the entire delta. Collection 642/653 with 11 deselected by the `pytest.ini`
marker expression, unchanged. No new failures, expected or otherwise.

## 38. Golden before/after

`python -m evals.runner --mode deterministic`, before and after:
**`HARNESS PASS — 20 scenarios graded; current product baseline: 12 passed, 8 failed`**, with the
same eight IDs both times: `calendar-move-event-002`, `habit-status-001`, `habit-complete-002`,
`safety-delete-downloads-001`, `safety-shutdown-002`, `safety-derived-injection-004`,
`clarify-open-target-001`, `clarify-delete-target-002`. No scenario changed.

## 39. Legacy behaviour non-change

The probe fixture was reused byte-identically (`bb4624f9…`, the same file used in 13B11B and
13B11C), run at `eb4c5db` before any P2 file was installed and again at `HEAD` after the commit.
Both outputs are **byte-identical**, sha256
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291` (13,519 bytes) — the same value
13B11C recorded. It covers rule-based intent routing and reasons, tool parameters, the 18-tool
inventory with SAFETY_LEVELs, `approval_mode: balanced`, `dry_run: false`,
`confidence_threshold: 0.75`, `max_tool_chain: 5`, per-level confirmation (`0/1 → false`,
`2/3 → true`), prompt shape and response-cleaner output. No tool executed, no model called.

## 40. Execution-mode status

`execution.mode: legacy`, `execution.hermes_brain: false`, `agent.hermes_enabled: false`, before and
after. No P2 code reads the execution mode at all. The 13B11B and 13B11C mode tests re-run and pass
unchanged, and a new test re-asserts all three.

## 41. Hermes non-use

No Hermes process running (`ps -eo pid,args` matching `hermes|uvicorn|app.server` returns no rows
with this audit script excluded); repository `2237be355906fbe6065ce1815711eee52b2d646e`, 0 dirty
lines; no provider call, no adapter, no Granite load; the shared Ollama at `192.168.0.27:11434`
reported `{"models":[]}` before and after; zero occurrences of "hermes" in `provenance.py`.

## 42. Tool-path non-change

`app/tools/registry.py` `e70d4d50…` and `app/computer/safety.py` `a41127209…` — both identical to
baseline. `registry.call` has the same four callers, all in `app/server.py` (639, 737, 814, 858). No
wrapper, no dispatcher, no new caller. Tool inventory and every `SAFETY_LEVEL` identical in the probe.

## 43. Confirmation-path non-change

`app/server.py` `b1448ed1…` — identical to baseline. `_pending_confirmations` (87), its write (646),
`confirm_request` (792-793) and the `approval_gate_triggered` / `approval_gate_confirmed` events
(669, 834) are untouched. The `CONFIRMATION_REQUIRED` provenance source is groundwork only: no state
machine, binding, expiry or denial logic exists.

## 44. Audit non-change

`app/logs/audit.py` `835fb246…` and `app/observability/tracing.py` `e6defa78…` — identical to
baseline; 204 legacy call sites unchanged; the only `"schema_version"` literal written is still `2`
and never `3`. `app/execution/audit_events.py` `cac2b32c…` — identical, so the P1 schema was not
altered. Zero live schema-v3 events and zero provenance event emissions.

## 45. Lifecycle non-change

`app/resource_manager.py` `43e293d0…` — identical to baseline. `provenance.py` mentions
`LIGHT_SLEEP`/`DEEP_SLEEP` zero times, and `LedgerStore.drop`/`clear` are called zero times outside
the module. Sleep, wake, preload and unload behaviour is untouched.

## 46. Security review

Zero literal hits across both files for `eval(`, `exec(`, `__import__`, `importlib`, `subprocess`,
`os.system`, `popen`, `socket`, `requests`, `httpx`, `urllib`, `open(`, `Path(`, `write_text`,
`write_bytes`, `pickle`, `yaml.load`, `marshal`, `shelve`, `input(`, `nonlocal`, `setattr(`. The one
`global` hit is the word inside a docstring. Imports: `re`, `threading`, `dataclasses`, `datetime`,
`types`, `typing`, `__future__` plus `app.execution.types` and `app.execution.correlation` — nothing
else. Zero module-level mutable containers, zero `global`/`nonlocal` statements, zero module-level
ledger or store instances, `SOURCE_TRUST` read-only, and no recorder accepting a caller-supplied
trust class — so there is no mutable global authorization state and no implicit trust elevation.
1,000 generated record ids carried no secret, prompt fragment, path, host or model name. No network
access, no filesystem write, no unsafe deserialization.

## 47. Contract traceability

`TRACEABILITY.md` maps every artifact to its clause, invariant, P2 requirement and future consumer,
including all seven the task required: source distinction (§3.2/§9.3 → INV-008 → P3/P6), trust
distinction (§9.3/§16.1 → INV-008 → P6), correction and supersession (§10 → INV-007/INV-019 → P3/P6),
tool result provenance (§18.1-§18.4 → INV-003 → P5/P6), user-reported attribution (§16.1 → INV-008 →
P6/CT-007), current-value lookup (§16.1 → INV-008 → P6), and historical auditability (§10.1/§19.1 →
INV-019 → audit replay).

## 48. Rollback

Runtime rollback is a no-op: nothing reads or writes the ledger and the mode is already `legacy`.
Source rollback is `git revert b9a557b` (or `git reset --hard eb4c5db`), which deletes the three new
files and removes the nine added lines from `correlation.py`. No database rollback, no audit
migration, no state migration, no model cleanup, no Hermes cleanup. In-memory ledger state
disappears with the process. Details in `ROLLBACK.md`.

## 49. Production diff

4 files, 1,639 insertions, 0 deletions. One existing file modified — `app/execution/correlation.py`,
+9 lines, the additive record identifier. Full patch in `evidence/15-production-diff.patch`, stat in
`evidence/14-production-diff-stat.txt`, the correlation delta isolated in
`evidence/source/correlation-delta.patch`.

## 50. Production commit

`b9a557b4460daf240cc26f6ae932db476a5c4315`, parent `eb4c5db1985033f2c7464fbd1bd3ae9a385199d0`,
branch `main`, message `feat: add execution provenance ledger foundation`. Not pushed.

## 51. Workspace commit

Separate commit in `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS`, message
`docs: record task 13B11D provenance foundation`, containing `tasks/task13b11d/` and the
`tasks/loop-log.md` entry — documentation only. Histories stay separate: no production source in the
workspace commit, no documentation in the production commit.

## 52. Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11d-provenance-foundation/` — **35 files, 34 manifest
entries**, `SHA256SUMS` excludes itself (0 self-references) and verifies **34 OK, 0 failures**.
`README.txt` maps every artifact to the script or command that produced it. The 13B11C and 13B11B bundles were reverified
afterwards and are unchanged. The digest is reported to the operator in the task response and in
`tasks/loop-log.md` rather than inside the sealed bundle, which cannot contain its own hash.

## 53. Final production state

`/home/jarvis/JARVIS` at `b9a557b4…`, branch `main`, clean, 0 untracked, 1 worktree, 3 commits ahead
of `origin/main` (13B11B, 13B11C, 13B11D — none pushed). 88 python files under `app/`.
`execution.mode: legacy`, `execution.hermes_brain: false`, `agent.hermes_enabled: false`,
`safety.dry_run: false`. All sixteen watched files byte-identical to the entry baseline; the only
changed existing file is `correlation.py`, by nine additive lines.

## 54. Final Hermes state

`2237be355906fbe6065ce1815711eee52b2d646e`, clean, not running, not configured, not referenced by
any production code. Shared Ollama `{"models":[]}`.

## 55. Repository cleanliness

Production repo clean, 0 untracked, no stray worktree. Workspace repo clean after the documentation
commit. No prior evidence bundle modified.

## 56. Recommendation

Per the 13B11A dependency graph, the critical path is
`config/types (P0) → audit (P1) → provenance (P2) → classifier+router (P3) → permissions (P4)`, so
**P3 is what P2 unblocks — not permissions**. P3 as the phase table defines it bundles four modules
(`classifier.py`, `router.py`, `canonicalize.py`, `lane.py`) plus lexicon and grammar data.

The **smallest independently reversible unit now available is the canonicalizer**
(`app/execution/canonicalize.py`): a pure, versioned function over `(tool_name, raw_args)` returning
canonical arguments and the rules applied. The graph places it as a direct child of P0 with no
dependency on the classifier, the router or the ledger, it is trivially testable, and it fills the
`canonical_arguments` and `canonicalization_version` fields the P1 audit schema already defines —
closing INV-006 end to end. `lane.py` is the next smallest on the same grounds.

Suggested next task: **13B11E — deterministic argument canonicalizer**, passive and unwired, with
exact versioned rules, no fuzzy matching and no guessing (§9.1), and no router or classifier work
bundled in.

Two operator decisions remain open and neither blocks P3: whether `lane` joins the seventeen audit
fields, and which keys the future redaction engine must treat as secret. A third is now on the
table: whether a timed-out invocation deserves an explicit provenance source, which would extend the
frozen P0 `ProvenanceSource` enum and is therefore an operator call rather than an implementation
detail.
