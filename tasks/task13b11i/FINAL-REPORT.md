# Task 13B11I — Passive Permission Policy Foundation

**Verdict: JARVIS PERMISSION POLICY FOUNDATION IMPLEMENTED**

Production phase P4 of the Agent Execution Contract v1 integration plan, first unit. The contract
§11 permission layer — a class per action and target, decided before dispatch, from a versioned
auditable table, never by a model — now exists in production as a pure, passive, unwired module.
No production request is allowed, denied or confirmation-gated by it.

| | |
|---|---|
| production | `/home/jarvis/JARVIS` `52c5da5d7a5d304acd4088b11e1f9bd509067069` |
| parent | `03cab4960156220fe9b6c3a444fa7a41265c01e0` |
| files | 5 added, 0 modified, 2,678 insertions, 0 deletions |
| tests | 2113 → **2575 passed**, 11 deselected, 0 failed (462 new) |
| matrix | **40/40** rows decide their signed-off outcome |
| golden | **12/20** before and after, same eight failures |
| legacy probe | `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`, byte-identical |
| mode | `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false` |
| Hermes | `2237be355906fbe6065ce1815711eee52b2d646e`, clean, 0 processes |

## 1. Entry state, verified before anything was written

Production at `03cab496`, branch `main`, 1 worktree, **0 dirty, 0 untracked**, 8 commits ahead of
origin after this task, none pushed. `execution.mode=legacy`, both Hermes flags `false`,
`approval_mode="balanced"`, `dry_run=false`, Python 3.14.4. Hermes `2237be35…` clean and not
running. Workspace clean at the review commit `7ebcf838`. The 13B11H bundle verified at **53 files,
52 entries, digest `ef768d69…`, 0 failures** — the values the task specified. No prior bundle was
modified.

## 2. Operator sign-off, encoded

All ten decisions are in the table and each has named regression tests (46 in total). Two overrode
the review's recommendation and both were followed as signed off: **D-01** app launch is
`REQUIRE_CONFIRMATION`, not the review's `ALLOW`; **D-05** webcam is `REQUIRE_CONFIRMATION`. The
full mapping is `OPERATOR_DECISIONS.md`.

## 3. The method, unchanged from the series

The policy table was frozen and hashed **before** the module was written — the recorded check shows
`ls app/execution/permissions.py` returning "No such file or directory" at that moment. Six design
documents plus `policy-table.json`, digest recorded, then the module, then the tests. The baseline
was measured first-hand on a clean tree rather than taken from the previous task's report.

## 4. What was built

`app/execution/permissions.py`, 657 lines: the 40-row signed-off matrix as a frozen tuple of frozen
rows behind a read-only index, `PERMISSION_POLICY_VERSION = "1"`, `ApprovalMode`, `Constraint`,
`DenialKind`, an 11-member `PermissionReason`, frozen `PermissionRequest` and `PermissionDecision`,
`PermissionPolicyError`, `tighten()`, and one entry point `decide()`.

## 5. Matrix completeness

40 rows from the 35 review rows: three review rows split into the action subtypes a permission must
distinguish (`files` read/list/search; `files.move` and `files.move.overwrite`). **Review rows
1–35 all represented, 18 of 18 discovered registry modules covered, 0 duplicate keys, 0 wildcard
rows, 0 unregistered rows that do not deny.** 31 rows are backed by a real tool; the 9 that are not
all deny. Every row's live decision equals its signed-off base outcome — measured, 0 differences.

## 6. Fail-closed

Fifteen abnormal inputs were exercised and produced **0 `ALLOW` outcomes**: the three non-executable
actions, the three unavailable actions, unresolved target, action/capability clash, unknown and
empty capability, unknown and true overwrite state, unsatisfied constraint, unregistered row and
prohibited row. Exactly one reason, `ROW_MATCHED`, can accompany a non-`DENY` outcome, and that is
asserted rather than asserted-about. The module contains **no `except` clause at all**, so no
exception path can return a permissive decision.

## 7. approval_mode

Tightening only, proven exhaustively: **72 (outcome × class × mode) combinations with 0 weakenings**,
**72 ordered mode pairs with 0 inversions**, and **120 row × mode decisions end to end with 0
weakenings**. `DENY` is absorbing; `REQUIRE_CONFIRMATION` never becomes `ALLOW`; `balanced` is the
floor.

## 8. Purity and non-activation

**360 requests** decided under a CPython audit hook watching file opens, sockets, subprocesses,
dynamic import, `exec`/`compile`, filesystem mutation and `time.sleep` — **zero** sensitive events.
21 sweeps of the whole table identical; 500 repeated calls produced one output and left the request
unmodified. The module imports only `__future__`, `dataclasses`, `enum`, `types`, `typing` and
`app.execution.types`. **0** importers, **0** call sites, **0** references to any of fourteen public
symbols anywhere under `app/`; the package `__init__` does not export it; the only `app.execution`
reference outside the package is still `app/config.py:14` from P0.

## 9. Model non-authority

`PermissionRequest` has no field for confidence, a safe flag, a recommendation, an approval claim or
prose — checked against a list of nineteen forbidden field names. A `ModelDraft` or `ToolProposal`
passed as an argument raises rather than being ignored. Seven claim strings ("the user already
confirmed this", "ALLOW", "permission granted by the assistant", …) change nothing, and a denial
holds against every one of them.

## 10. Non-change

**22 critical files byte-identical**, including `app/server.py`, `app/tools/registry.py`,
`app/computer/safety.py`, `app/logs/audit.py`, the legacy router, `tool_params.py`,
`response_cleaner.py`, every P0–P3 execution module, `config.yaml` and `CLAUDE.md` (production's
copy). `registry._requires_confirmation` untouched, `registry.call` still has its four callers, no
`SAFETY_LEVEL` changed, audit schema still version 3 with seventeen fields, `lane` still not among
them, `ProvenanceSource` still eight members with no `TIMEOUT`. No deferred item was resolved and
no scope widened.

## 11. Two things found and fixed in the open

**A wrong denial reason.** The first draft denied `messaging.system_egress` and `resource.control`
with `CAPABILITY_NOT_REGISTERED`. That is false: those surfaces exist and are forbidden by D-06 and
D-07, and the distinction drives which contract obligation the turn gets — `REPORT_CAPABILITY_
UNAVAILABLE` for an absent capability (§13.1) versus a refusal for a prohibition. The frozen table
was amended to carry `denial_kind`, re-hashed from
`8feca50e…` to `9a8558ae…`, and the amendment is recorded inside `policy-table.json` with the
previous digest, what changed, why, and the fact that no scored test existed yet. No row's class,
outcome, registration or constraint moved.

**A modelling gap in the request.** Requiring `primary_action` made every capability outside the
five routed actions undecidable — there is no `PrimaryAction` for closing an app, fetching a URL or
running a shell command. Rather than loosen the action/capability gate, the field became optional
with an explicit meaning, and the gate was strengthened to check the pairing in **both** directions
when an action is supplied. The three unavailable actions still deny against any capability.

## 12. One tension recorded, not resolved

D-01 is worded "application launch / **PC control**", and the review question it answered was about
`apps open`. The signed-off matrix leaves `browser.open` and `browser.search` at `ALLOW` (review
rows 12–13, never raised as a decision), yet opening a URL does launch a browser window. This
implementation follows the matrix literally and flags the question; changing those two rows would
be a policy change with no sign-off behind it. A one-line operator answer flips two rows and two
tests.

## 13. Deliberately not done

No confirmation manager, record, id, store, state machine, TTL or expiry. No dispatcher change, no
`registry.call` wrapper. No learned or persisted permissions. No `config/permissions.yaml` — the
externalization is recorded as a deferral with its requirements. No networking for D-04; the
constraint is a precondition the engine cannot discharge itself, which is why an unconstrained
fetch denies. No audit emission and no schema change. No live wiring, no Hermes, no Task 13C.

## 14. Rollback

Runtime: none. Source: `git revert 52c5da5d…`. No database, confirmation, audit, provenance, model
or Hermes cleanup. Details in `ROLLBACK.md`.

## 15. Next

Per `DEPENDENCY_GRAPH.md` the next component is the **confirmation state-machine foundation**, and
it is **not started**. The smallest passive unit that can consume `REQUIRE_CONFIRMATION` without
executing anything: the confirmation **record and its state machine** — an opaque id, the binding
fields from §12.3 (action, target, canonical arguments, session), `created_at`/`expires_at` as
data, and the six transitions from `CONFIRMATION_STATE_PLAN.md` §3 — with an in-memory store behind
an interface, no persistence, no clock-driven expiry sweep, and **no execution on approval**: the
`PENDING → EXECUTING` edge should raise `NotImplementedError` until the dispatcher boundary exists
at P5. That keeps the clock and the store out of the pure layer and leaves the only dangerous edge
unbuilt.
