# Task 13B11J — Passive Confirmation State Machine Foundation

**Verdict: JARVIS CONFIRMATION STATE FOUNDATION IMPLEMENTED**

Phase P4 of the Agent Execution Contract v1 production integration plan, second and final unit.
Contract §12 — confirmation is JARVIS-owned state that binds an approval to one exact pending
action and to the session that asked for it, and nothing executes until a valid confirmation is
deterministically associated with that action — now exists in production as a pure, passive,
unwired module. No production request is gated, delayed or approved by it.

| | |
|---|---|
| production | `/home/jarvis/JARVIS` `c321cb8958935fa74db0916ec47e56f052410663` |
| parent | `52c5da5d7a5d304acd4088b11e1f9bd509067069` |
| files | 5 added, 1 modified, 3,479 insertions, 1 deletion |
| tests | 2575 → **2892 passed**, 11 deselected, 0 failed (317 new) |
| transition corpus | **42/42** cells behave exactly as frozen |
| security review | **37/37** checks pass |
| golden | **12/20** before and after, the same eight |
| legacy probe | `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`, byte-identical |
| critical files | **24/24** byte-identical |
| mode | `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false` |
| Hermes | `2237be355906fbe6065ce1815711eee52b2d646e`, clean, 0 processes |

## 1. Entry state, verified first-hand

Production began at `52c5da5d…`, parent `03cab496…`, branch `main`, 1 worktree, **0 dirty, 0
untracked**, 8 commits ahead of origin, none pushed. `execution.mode=legacy`, both Hermes flags
`false`, `approval_mode="balanced"`, `dry_run=false`, Python 3.14.4. Hermes `2237be35…` clean and
not running. Workspace clean at `e5d48b03`.

The 13B11I bundle verified at **46 files, 45 entries, digest
`e83dad89b8c8254a64bc48d5f94b898bdf0373bee7e1d6e64bd4f253e285c7b6`, 0 failures** — the values the
task specified. All 29 sealed bundles under `evidence/` were re-verified afterwards: **0 failures
anywhere**, and every digest matches what the earlier reports recorded. No prior evidence was
modified.

## 2. Method, unchanged from the series

Eight design documents and the 42-cell transition corpus were written and hashed **before**
`app/execution/confirmation.py` existed. `06-frozen-inputs.txt` records `ls` returning "No such
file or directory" for the module and all three test files at the moment of hashing, together with
`grep -rc ConfirmationState app/ → 0`. The module and the tests each derive from the corpus
independently — the tests read `confirmation_transition_table.json` as data and assert its SHA-256
(`2d89cc2c…`), never the module's own table.

## 3. What was built

`app/execution/confirmation.py`, 810 lines: `ConfirmationState` (7 members), `ConfirmationEvent`
(6), `TRANSITIONS` (6 edges), `next_state()`, `ConfirmationBinding` (12 write-once fields),
`ConfirmationRecord`, `create_confirmation()`, `to_audit_payload()`, `ConfirmationStore` (6
operations), six errors, and four frozen sets. No `try` block anywhere.

## 4. The state vocabulary is the plan's, not the prompt's

`CONFIRMATION_STATE_PLAN.md` §3 freezes seven states — six persisted plus the transient
`EXECUTING` — and **deliberately drops a resting `CONFIRMED`**: *"a confirmed action that is not
yet executing is an ambiguous state that invites double execution."*

The task prompt speaks of a `CONFIRMED` state and a `CONFIRMED → EXECUTING` edge. The prompt's own
§13 resolves the difference in favour of the plan, so no `CONFIRMED` member was added. The prompt's
§16 requirement — approval does not mean executed — is met in a stronger form: in this phase
approval reaches no state at all.

## 5. The dangerous edge is a wall, not a gap

`PENDING → EXECUTING` claims execution ownership. `confirm()` runs the entire check in order —
the record exists and belongs to the session, it is `PENDING`, `now < expires_at`, then all twelve
binding fields — and only a **fully valid** approval reaches `ConfirmationDispatcherUnavailable`,
which is both a `ConfirmationError` and a `NotImplementedError`. The record is not advanced and not
mutated; measured byte-equal afterwards.

Ordering is the point. An invalid approval always learns *why* it is invalid before it learns the
dispatcher is missing, so the session, freshness and binding checks are genuinely exercised rather
than shadowed by the wall. `SUCCEEDED` and `FAILED` have no public route: no store method name
contains "succeed", "fail", "execute" or "dispatch". Reachable states in this phase are exactly
`PENDING`, `DENIED`, `EXPIRED`, `CANCELLED`; `EXECUTING`, `SUCCEEDED` and `FAILED` are unreachable,
and every reachable record reports `execution_started = False`.

## 6. Binding: twelve fields, not five

Contract §12.3 requires four. The plan's §4 approval rule names five. All twelve are compared,
because the task's own §34 requires a changed capability subtype, permission class, policy version
or canonicalization version to invalidate an approval — which the five-field list would not catch.
A stricter check can never authorize something the plan's check would refuse.

Twelve single-field mutations were each measured: **0 succeeded**, and each left the honest record
`PENDING` with its binding intact. Two pending actions in one session were tested; each approval
reached only its own record.

`canonicalization_version` is bound because `RISK_REGISTER.md` R-07's mitigation is literally
*"store `canonicalization_version`; compare at approval"*.

## 7. Expiry is data plus an injected clock

No timer, no thread, no task, no `datetime.now()`, no `utc_now()`. Every time-dependent operation
takes `now` explicitly — the "inject both" the dependency graph specifies for this component. The
window is **half-open** and the boundary is a decision, not an accident: `now < expires_at` is
fresh, `now == expires_at` is not, tested at five explicit timestamps including one microsecond
either side.

R-04's *"expired records move to `EXPIRED` on load and on access"* is implemented uniformly for the
"on access" half: `get`, `confirm`, `deny` and `cancel` all expire a stale record and refuse. A
stale approval never reaches the binding check, and an expired record cannot be revived by rewinding
the clock.

**No TTL value is frozen here.** Plan §6 *proposes* 5 and 2 minutes per class; no operator signed
them, D-01…D-10 contain no TTL, and `config/permissions.yaml` does not exist. The mechanism is
here; the values wait for sign-off. `test_no_ttl_policy_is_frozen_in_this_module` asserts it.

## 8. Two things changed during implementation, in the open

**(a) The permission engine is consumed, not imported.** The first draft took a
`PermissionDecision` and imported `app.execution.permissions`. That broke two sealed 13B11I
invariants that exist to prove P4's engine is unwired — *"no module under app/ imports the
permission engine"* and the nineteen-symbol reference scan. Weakening a sealed proof to make room
for a new module is the wrong direction, so the API changed: `create_confirmation()` takes
`permission_outcome`, `permission_class` and `policy_version`. The guard is unchanged in strength,
the engine keeps its zero-importer property, and a test builds a real decision through the live
`decide()`, asserts `matched_row == capability`, and feeds its three fields in — so P4
compatibility is still proven against the real engine.

**(b) One existing test changed, by addition only.** The 13B11E canonicalizer non-activation test
asserts `canonicalization_version` appears only in `types.py` and `audit_events.py`. The
confirmation record must carry it (R-07), so the allow-list gained a third passive declarer with
the reason in the comment. The test's real invariant — the canonicalizer is never *invoked* from
production code — is untouched and still passes. This is the only modification in the commit.

Both are recorded here rather than smoothed over, because a reader comparing this commit to the
13B11I evidence would otherwise find an unexplained difference.

## 9. Two decisions the plan left open, resolved and argued

`CONFIRMATION_STATE_PLAN.md` §4: *"Any mismatch → no execution, record moves to `CANCELLED` or
stays `PENDING` (design decision at implementation time)"*.

* **Binding mismatch leaves the record `PENDING`.** Cancelling it would let anyone holding the
  opaque id destroy a legitimate pending approval — a denial of service on the real user's
  decision. Nothing executes either way, so the choice that preserves the honest path wins.
* **A session mismatch is reported as "not found".** A distinguishable error is an oracle that
  confirms a given opaque id exists. The two error strings are asserted **equal**.

Both alternatives are recorded in `BINDING_CONTRACT.md` §3 and are one-line changes if the operator
prefers them.

## 10. Passive by measurement, not by assertion

* **2,080** public operations under a CPython audit hook watching file opens, sockets,
  subprocesses, dynamic import, exec/compile, filesystem mutation and sleep — **0** sensitive
  events. Thread count unchanged at 1.
* Imports are exactly nine: `__future__`, `threading`, `dataclasses`, `datetime`, `enum`, `types`,
  `typing`, `app.execution.correlation`, `app.execution.types`. `threading` is used for exactly one
  `Lock` and nothing else.
* 25 full 42-cell sweeps → **1** distinct result. 300 identical approvals → **1** distinct answer.
* **0** importers, **0** call sites, **0** references to any of nineteen public symbols anywhere
  under `app/`. The package `__init__` does not mention it. Eleven named live-path modules are
  clean. `to_audit_payload` is defined in exactly two passive modules and called from no live path.
* The audit writer, the provenance ledger and `registry.call` were each monkeypatched to fail the
  test if called; every operation was then run. None fired.
* **0** schema-v3 emissions anywhere under `app/`; the audit schema is still v3 with 17 fields,
  `lane` still absent, 5 confirmation events, `ProvenanceSource` still 8 members with no `TIMEOUT`.

## 11. Legacy confirmation is untouched

The `_pending_confirmations` dict, the `POST /confirm/{request_id}` route and the `pop` are present
verbatim. The legacy confirmation slice of `server.py` hashes
`9c43b6f93039543e992c9dd25391e46765d68c463aea747fc464870dd601b2f5` before and after, asserted by a
test so a future edit fails loudly. `registry.call` still has its four callers. All 17
`SAFETY_LEVEL` declarations are unchanged. No pending confirmation was migrated.

## 12. Security review — 37/37

Replay (terminal records cannot be re-approved, ids cannot be re-registered), cross-session approval
(four intrusion vectors, 0 succeed, error strings identical), binding mismatch (12 mutations, 0
succeed, honest record preserved), stale confirmation (boundary refused, cannot be revived),
mutable approved target (binding, state and nested values all frozen), arbitrary transition (all 42
cells, 0 deviations, no ad-hoc branch on an execution state), model-created approval (7 vectors, 0
succeed; **the module compares against no string literal at all**), execution before dispatch (no
`EXECUTING`, record untouched, no route to `SUCCEEDED`/`FAILED`), hidden default confirmation (no
default state, creation always `PENDING`, pre-approved records rejected), global
latest-confirmation approval (no listing accessor; not addressable by target, tool, capability or
action), TOCTOU (one locked step, no wall clock, policy and canonicalization versions bound),
mutable global store (6 declared names, none mutable; records private), serialization (JSON-safe,
**no deserializer exists**, no prose, execution reported not started).

No known unsafe authority path.

## 13. Deferred, recorded not resolved

Persistence and the on-load expiry sweep (deferred together — a restart loses pending approvals
rather than resurrecting them, the safe direction); per-class TTL values pending sign-off;
`PENDING → EXECUTING`, `SUCCEEDED` and `FAILED` owned by P5; re-deriving canonical arguments at
approval (P7 pipeline composition); the live confirmation UI/API mapping (P7). Carried forward
untouched from earlier tasks: the `browser.open`/`browser.search` vs D-01 tension, `lane` as an
audit field, the redaction secret-key list, the `TIMEOUT` provenance source, and the P6
classifier/router unsupported-verb reconciliation.

## 14. Final state

Production `c321cb89…`, clean, 0 untracked, 9 commits ahead of origin, none pushed. Workspace
clean. Hermes `2237be35…` clean, 0 processes, both flags `false`; the shared Ollama at
`192.168.0.27:11434` reported `{"models":[]}` — no inference was performed by this task.

Evidence: `/home/jarvis/.hermes-poc/evidence/task13b11j-confirmation-foundation/`, sealed with
`SHA256SUMS` excluding itself, verified with 0 failures.

## 15. Next

**STOP.** Per `DEPENDENCY_GRAPH.md` §2 the critical path now reads
`… → permissions (P4) → confirmation (P4) → dispatcher (P5)`. P4 is structurally complete: both of
its components exist, both are pure, both are passive and neither is wired.

The next boundary is **P5 — the trusted dispatcher / `ToolInvocation` boundary**. Not started. The
smallest passive unit that can consume a routed action, canonical arguments, a permission decision
and a valid confirmation state without any real side effect is the **`ToolInvocation` constructor
plus an inert dispatcher seam**: the one place permitted to build a `TrustedToolResult`, with an
injected executor that is a test double, so `registry.call` is never reached and
`ToolResultStatus.BLOCKED` / `CONFIRMATION_REQUIRED` always carry `executed = false`. That unit
would also be the natural owner of the `PENDING → EXECUTING` edge this task deliberately left as a
wall.

Do not enable Hermes. Do not start Task 13C. Do not wire confirmation into live requests. Do not
execute tools. Do not modify legacy confirmation.
