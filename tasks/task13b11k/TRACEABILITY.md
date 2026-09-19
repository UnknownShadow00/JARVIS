# Traceability — Task 13B11K

Every design decision to its normative source, and every requirement to its evidence.

## Contract clauses

| Clause | What it requires | Where it lands |
|---|---|---|
| §18.1 | only an authorized dispatcher's results enter trusted provenance | `app/execution/dispatch.py` is the only module under `app/` constructing `TrustedToolResult`; asserted by test |
| §18.2 | a trusted result binds invocation id, tool, normalized arguments, dispatcher, timestamp, status, data, audit event | every field copied from the invocation, `executor` names the dispatcher, `audit_ref` carries the turn id |
| §18.3 | `TOOL_ERROR` grounds that invocation only, preserving returned detail | the executor's `error_kind`/`error_message` are preserved; no fact is derived from them |
| §18.4 | success grounds only the facts explicitly returned | `facts` is non-empty on `SUCCESS` only, and holds exactly the executor's keys |
| §11.2 | no model self-authorizes; a denial is not overridable | the settled outcome is consumed, never recomputed; 10 coercion attempts, 0 weakenings |
| §12.1 | a gated action becomes `CONFIRMATION_REQUIRED` with `executed=false`, and no execution until a valid confirmation is associated | 45 matrix cells; the pairing rule was corrected to honour this exactly |
| §12.2 | model text is never confirmation | no text-accepting parameter exists on any entry point |
| §12.3 | approval binds action, target, arguments and session | all 12 fields compared; 9 cross-checked by the dispatcher first |
| §13.1, §13.2 | an unsupported action is answered, never mapped to a tool | `UNKNOWN_ACTION` refused at gate 2 and unbuildable |
| §8.1 | multi-action refused, never partially executed | `MULTI_ACTION_UNSUPPORTED` refused; `dispatch()` contains no loop |
| §19.1, §19.2 | dispatch is auditable; no chain-of-thought | schema v3 unchanged; the two invocation events validate against a real result; nothing emitted |

## Invariants

| Invariant | Evidence |
|---|---|
| INV-002 — a model assertion never creates trusted execution provenance | `ModelDraft`, `ToolProposal` and a result-shaped dict all become `executor_contract_violation` |
| INV-003 — only authorized dispatcher results create `TOOL_SUCCESS`/`TOOL_ERROR` | sole constructor, asserted; the ledger refuses by type |
| INV-004 — confirmation-required actions cannot execute before valid confirmation | the 45-cell block, plus the claim's full re-check |
| INV-006 — raw and canonical arguments are both auditable | both retained, distinct, immutable, checked at gate 3 |
| INV-011 — unsupported actions are not silently mapped | gate 2 |
| INV-012 — no silent partial execution | gate 2 + no loop |
| INV-013 — production side effects require permission policy | gate 4, and no path weakens it |
| INV-014 — destructive actions require deterministic confirmation policy | gates 5 and 6 |

## Plan documents

| Source | Decision it settled |
|---|---|
| `IMPLEMENTATION_PHASES.md` P5 | the phase, the path `app/execution/dispatch.py`, the inert dispatcher, "typed `TrustedToolResult` only creatable here" |
| `TARGET_COMPONENT_MAP.md` §1 | responsibility, inputs, outputs, and "never bypassable by importing a tool module" |
| `TOOL_INVOCATION_CONTRACT.md` §1-§3 | the invocation fields, the result fields, the five statuses, `executed=false` on refusals, `TIMEOUT` never folded into `ERROR` |
| `CONFIRMATION_STATE_PLAN.md` §3 | no resting `CONFIRMED`; approval transitions directly into `EXECUTING` under a lock |
| `PRODUCTION_INTEGRATION_PLAN.md` §13 | invocation id before dispatch; `PENDING → EXECUTING` per-record; no automatic retry |
| `PRODUCTION_INTEGRATION_PLAN.md` §19 | dispatcher unavailable → no execution; fail closed |
| `RISK_REGISTER.md` R-02, R-03, R-05, R-07, R-08, R-17 | permission before dispatch; single-use claim; long opaque id and full binding; version compared; only the dispatcher builds a trusted result; timeout distinct |
| `TEST_STRATEGY.md` §2, §4 | pre-registered expectations; the inert dispatcher fixture; the CPython audit-hook assertion |

## Conformance tests owned by P5

| Test | Status here |
|---|---|
| CT-002 — tool error grounds the failure response | the result side is done: the executor's kind and message are preserved and nothing is extrapolated. The response side is P6 |
| CT-003 — success grounds only the returned facts | done at the result and ledger level |
| CT-010 — raw and canonical arguments both audited | both retained and both present in the `dispatch.invoked` payload built in test |
| CT-014 — no tool-result spoofing via model text | done; three spoof shapes all refused |

CT-002 and CT-003 become fully green when the response builder exists at P6; the parts that
belong to the dispatcher are green now.

## Task requirements

| Requirement | Evidence file |
|---|---|
| exact baseline verified | `01-prerequisite-verification.txt`, `03-production-baseline.txt` |
| 13B11J evidence verified | `02-evidence-chain-verification.txt` |
| frozen matrix hashed before the module existed | `frozen-hashes.txt`, `docs/dispatch-matrix.json` |
| purity, no live wiring | `11-purity-and-no-live-wiring.txt` |
| security review | `13-security-review.txt` |
| full tests, golden, probe, hashes | `05-tests-and-golden-after.txt`, `09/10-probe-*.json` |
