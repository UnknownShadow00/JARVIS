# CONFIRMATION CONTINUATION

Mode B. Admits one existing `ConfirmationRecord` so that a turn can report an outstanding
approval request with its exact identity, and so that a wrong, stale, replayed or
cross-session confirmation is refused deterministically instead of silently ignored.

## There is still no resting CONFIRMED

`ConfirmationState` has six persisted states plus the transient `EXECUTING`, and
`TRANSITIONS` contains no edge producing a `CONFIRMED` state. `ConfirmationStore.confirm`
validates an approval completely and then raises `ConfirmationDispatcherUnavailable`
without advancing the record. Mode B does not resurrect a resting approved state, does not
call `confirm`, does not call `claim_for_dispatch`, and does not construct or mutate any
record.

## The only admissible state

`turn.confirmation.state is ConfirmationState.PENDING`.

Every other state is inadmissible in mode B, and each for a stated reason:

| State | Why mode B refuses it |
|---|---|
| `EXECUTING` | the claim already happened, so an invocation exists; that condition is representable only as mode C. A record in `EXECUTING` with no result is the deferred transport-loss case F-REPLAY-01. |
| `SUCCEEDED`, `FAILED` | settled by the dispatcher; a result exists, so the turn is mode C. `TERMINAL_STATES` accepts no event. |
| `DENIED`, `CANCELLED`, `EXPIRED` | terminal; a changed request needs a new record with a new id, never a replay of this one. |

## Admission guards (all at S08; order is normative)

1. **B-01 session ownership.** `turn.confirmation.session_id == turn.correlation.session_id`.
   Exact string equality. No cross-session lookup exists because no store is consulted.
2. **B-02 state.** `state is PENDING`, per the table above.
3. **B-03 freshness.** `turn.confirmation.is_fresh_at(turn.evaluated_at)` is True, using
   the record's own `expires_at` and the single admitted evaluation instant. P7 reads the
   existing predicate; it does not compute a window, does not expire the record and
   freezes no TTL value.
4. **B-04 audit-reference association.** `turn.confirmation.audit_ref.session_id ==
   turn.correlation.session_id` and `turn.confirmation.audit_ref.turn_id` is the turn the
   record was created for. If `turn.correlation.confirmation_id` is present it must equal
   `turn.confirmation.confirmation_id`.
5. **B-05 unclaimed.** `turn.confirmation.invocation_id is None` and
   `turn.confirmation.execution_started is False`. A record already bound to an invocation
   is not admissible in mode B (see B-02 `EXECUTING`).
6. **B-06 binding describes this turn's action.** The stored `ConfirmationBinding` must
   describe the action this turn actually routed. Checked field by field against the
   authoritative deterministic projections, using only fields that already exist:

   | `ConfirmationBinding` field | Must equal |
   |---|---|
   | `confirmation_id` | the record's own id (already an invariant of `__post_init__`) |
   | `session_id` | `turn.correlation.session_id` |
   | `action_type` | the actual S03 `RouteResult.primary_action` |
   | `capability` | `turn.permission_projection.capability` |
   | `tool_name` | `turn.expected.tool_name` |
   | `permission_class` | the actual S07 `PermissionDecision.permission_class` |
   | `policy_version` | `permissions.PERMISSION_POLICY_VERSION` |
   | `canonicalization_version` | `canonicalize.CANONICALIZATION_VERSION`, and `turn.expected.version` |
   | `target` | the actual S03 `RouteResult.target` |
   | `user_id` | not constrained by P7; carried through unchanged |
   | `raw_arguments` | `turn.expected.raw_arguments` |
   | `canonical_arguments` | `turn.expected.canonical_arguments` |

   Comparison is by value over the already-frozen immutable forms, with exact scalar types
   — the same equality `ConfirmationStore` applies to its twelve bound fields. These are
   the existing frozen `BINDING_FIELD_NAMES`; no additional binding is invented and no
   binding is derived from model prose or from request text.

7. **B-07 confirmable action.** `binding.action_type not in
   confirmation.NON_CONFIRMABLE_ACTIONS`. A record for `NONE`, `UNKNOWN_ACTION` or
   `MULTI_ACTION_UNSUPPORTED` is inadmissible; the existing early route terminals own
   those turns and P6 would otherwise be asked to imply an impossible execution (§13.1).

## Disposition

A mode-B turn that passes B-01…B-07 continues to S10 → S11 → S12 with
`ObligationState.confirmation_claimed = False`, `result = None` and the actual S07
`permission_outcome = REQUIRE_CONFIRMATION`. The existing rule `P6-01b` then selects
`REQUEST_CONFIRMATION` at rank 1, and `response.build` renders the
`confirmation_required` template. That is the full extent of what a confirmation
continuation achieves, and it is correct: the approval is still outstanding.

A mode-B turn has no edge to S09. The frozen dispatch-path proof is therefore preserved
exactly: no admitted continuation reaches S09 without having passed every earlier gate,
and a continuation that carries only an unclaimed approval reaches S09 not at all.

## Mismatch

Any failure of B-01…B-07 produces `PipelineStop(stage=S08_CONFIRMATION,
reason=confirmation_invalid, executed=False, result=None)`.

No repair. No "closest pending confirmation". No cross-session lookup. No renewal, no new
record, no re-ask, no fallback to the initial-ask branch, no P6 obligation. The record is
not mutated and not expired. Existing confirmation privacy semantics are preserved: the
stop reason is identical whether the record is unknown, foreign, stale, terminal,
already-claimed or mis-bound, so admission is not an existence oracle. The distinguishing
detail lives in the test matrix, not in the emitted stop — see ADMISSION_FAILURES.md
"Granularity limit".

## Replay

A confirmation authority or claim must not authorize the same execution twice, and in P7
v1 it authorizes zero executions. The atomic claim remains `ConfirmationStore`'s, invoked
only by `TrustedDispatcher._claim`; P7 introduces no second claim mechanism and no
pre-claim. Repeated admission of the same mode-B record is deterministic: B-01…B-07 are
pure predicates over immutable data, so a second run returns an equal outcome, mutates
nothing and calls no executor. A record that a real dispatcher has since claimed is no
longer `PENDING` and is refused by B-02/B-05 — it never becomes a second authorization.
