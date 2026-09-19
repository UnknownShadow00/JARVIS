# Implementation — Task 13B11J

| | |
|---|---|
| production | `/home/jarvis/JARVIS` `c321cb8958935fa74db0916ec47e56f052410663` |
| parent | `52c5da5d7a5d304acd4088b11e1f9bd509067069` |
| module | `app/execution/confirmation.py`, 810 lines |
| tests | `tests/execution/confirmation_test.py` (119), `confirmation_transitions_test.py` (71), `confirmation_non_activation_test.py` (127) |
| frozen corpus | `tests/execution/confirmation_transition_table.json`, 42 cells |
| files | 5 added, 1 modified, 3,479 insertions, 1 deletion |
| suite | 2575 → **2892 passed**, 11 deselected, 0 failed |
| golden | **12/20** before and after, same eight |
| legacy probe | `fc68a0b0…`, byte-identical |
| mode | `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false` |

## 1. Method

The state vocabulary, the transition corpus, the binding fields, the store API and the expiry rules
were written and hashed **before** `app/execution/confirmation.py` existed — `ls` on the module and
on all three test files is recorded returning "No such file or directory" at the moment of hashing
(`06-frozen-inputs.txt`). The module and the tests each derive from the frozen corpus
independently; the tests read `confirmation_transition_table.json`, not the module's own table, and
assert its SHA-256.

## 2. What was built

### `ConfirmationState` — seven members, the plan's exact set

`PENDING`, `EXECUTING`, `SUCCEEDED`, `FAILED`, `DENIED`, `EXPIRED`, `CANCELLED`. Six persisted plus
the transient `EXECUTING`, exactly as `CONFIRMATION_STATE_PLAN.md` §3 freezes it. There is no
resting `CONFIRMED`, because the plan drops it: *"a confirmed action that is not yet executing is
an ambiguous state that invites double execution"*. See `STATE_MACHINE.md` §2.1 for why the task
prompt's `CONFIRMED → EXECUTING` wording was resolved in favour of the plan.

### `ConfirmationEvent` + `TRANSITIONS` + `next_state()`

Six events, six edges, one pure lookup. No store method branches on a state by hand, so there are no
ad-hoc transitions to audit. All 42 (state, event) cells are provable.

### `ConfirmationBinding` — twelve write-once fields

`confirmation_id`, `session_id`, `user_id`, `action_type`, `capability`, `tool_name`, `target`,
`canonical_arguments`, `raw_arguments`, `permission_class`, `policy_version`,
`canonicalization_version`. Contract §12.3 requires four; the plan's §4 approval rule names five;
all twelve are compared. Rationale and per-field traceability in `BINDING_CONTRACT.md`.

### `ConfirmationRecord`

Binding plus lifecycle: `state`, `created_at`, `expires_at`, `resolved_at`, `audit_ref`
(`CorrelationContext`), `provenance_ref`, `invocation_id`, `state_machine_version`. Frozen. A
transition builds a new record carrying the **identical** binding object; nothing rewrites a
binding field.

`execution_started` is the negation of contract §12.1's `executed = false`, and it is `False` for
every state this phase can reach.

### `create_confirmation()`

Accepts the permission decision as its three settled values — `permission_outcome`,
`permission_class`, `policy_version` — rather than as the P4 decision object. This was a deliberate
change during implementation (§4 below). Refuses any outcome other than `REQUIRE_CONFIRMATION`,
refuses `NONE` / `UNKNOWN_ACTION` / `MULTI_ACTION_UNSUPPORTED`, refuses naive timestamps, refuses a
window that is not in the future, refuses a correlation that already carries an `invocation_id`
(confirmation precedes dispatch), and refuses `ModelDraft` / `ToolProposal` anywhere in the
arguments, at any nesting depth.

### `ConfirmationStore`

`add`, `get`, `confirm`, `deny`, `cancel`, `expire`. That is the whole public surface — verified by
test. No listing, no search, no "latest", no iteration, no accessor that returns the internal dict,
no module-level instance. Mutations run under a process-local `threading.Lock`; the limits of that
claim are stated in `STORE_API.md` §4 rather than implied.

### `to_audit_payload()`

The schema-v3 `confirmation_state` field, built and serialized in tests, emitted nowhere. No new
event, no new field, no schema bump — `audit_events.py` already had all five confirmation events.

## 3. The dangerous edge, and why it is a wall rather than a gap

`PENDING → EXECUTING` is the edge that claims execution ownership. `confirm()` performs the entire
check in order — record exists and is owned by the session, state is `PENDING`, `now < expires_at`,
then all twelve binding fields — and only a **fully valid** approval reaches
`ConfirmationDispatcherUnavailable` (a `ConfirmationError` **and** a `NotImplementedError`). The
record is not advanced and not mutated.

Ordering matters: an invalid approval always learns *why* it is invalid before it learns the
dispatcher is missing, so the binding, session and freshness checks are real and testable rather
than shadowed by the wall. `SUCCEEDED` and `FAILED` have no public route at all.

## 4. Two things that changed during implementation, in the open

**(a) The permission engine is consumed, not imported.** The first draft took a
`PermissionDecision` object and imported `app.execution.permissions`. That broke two sealed 13B11I
invariants — *"no module under app/ imports the permission engine"* and *"no public symbol is
referenced anywhere under app/"* — which exist to prove P4's engine is unwired. Weakening a sealed
proof to make room for a new module is the wrong direction, so the API changed instead:
`create_confirmation()` takes `permission_outcome`, `permission_class` and `policy_version`. The
guard is unchanged in strength, the engine keeps its zero-importer property, and a test builds a
real decision with the live `decide()` and feeds its three fields in, so P4 compatibility is still
proven end to end.

**(b) One existing test was changed, by addition.** The 13B11E canonicalizer non-activation test
asserts that the field name `canonicalization_version` appears only in `types.py` and
`audit_events.py`. The confirmation record must carry it — `RISK_REGISTER.md` R-07's mitigation is
literally *"store `canonicalization_version`; compare at approval"* — so the allow-list gained a
third passive declarer, with the reason in the comment. The test's real invariant, that the
canonicalizer is never *invoked* from production code, is untouched and still passes. This is the
only modification in the commit; everything else is new files.

## 5. Two design decisions the plan left open

`CONFIRMATION_STATE_PLAN.md` §4 leaves the mismatch outcome to implementation time. Both choices
are made, argued and tested — see `BINDING_CONTRACT.md` §3:

* a **binding mismatch leaves the record `PENDING`**, because cancelling it would let anyone
  holding the id destroy a legitimate pending approval;
* a **session mismatch is reported as "not found"**, because a distinguishable error is an oracle
  that confirms an opaque id exists. The two error strings are asserted equal.

## 6. Measured, not asserted

* 2,080 public operations under a CPython audit hook watching file opens, sockets, subprocesses,
  dynamic import, exec/compile, filesystem mutation and sleep — **0** sensitive events; thread
  count unchanged at 1.
* 25 full 42-cell sweeps → **1** distinct result. 300 identical approvals → **1** distinct answer.
* Imports are exactly `__future__`, `threading`, `dataclasses`, `datetime`, `enum`, `types`,
  `typing`, `app.execution.correlation`, `app.execution.types`. **0** `try` blocks in the module.
* **0** importers, **0** call sites and **0** references to any of nineteen public symbols anywhere
  under `app/`; the package `__init__` does not mention it; eleven named live-path modules are
  clean.
* Security review: **37/37** checks pass across replay, cross-session approval, binding mismatch,
  stale confirmation, mutable target, arbitrary transition, model-created approval,
  execution-before-dispatch, hidden default confirmation, global latest-confirmation, TOCTOU,
  mutable global store and serialization.
