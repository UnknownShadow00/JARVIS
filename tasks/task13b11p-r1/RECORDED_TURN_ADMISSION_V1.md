# RECORDED-TURN ADMISSION CONTRACT V1

Canonical contract resolving P-B01, the blocker Task 13B11P raised against the frozen
P7 PIPELINE CONTRACT V1. It freezes the complete immutable turn-admission API of the
passive composition boundary `app/execution/pipeline.py`, including the S08–S09
confirmation/result seam. It implements nothing.

Normative precedence: current operator decisions → P7 PIPELINE CONTRACT V1 (task13b11o-r1)
→ this file → existing frozen component contracts → older proposals. Where V1 and this
file both speak, V1 wins; this file only supplies what V1 left unfrozen. No V1 file is
edited, no V2 of V1 is created, and no P0–P6 production contract changes.

## What was unfrozen, and what is frozen here

P-B01 asked one question: what exactly does a caller hand the pipeline for one recorded
turn, which parts are required together, which absences are valid, and what is accepted
as the S08 eligible-confirmation handoff and the S09 result/claim evidence.

Frozen by this contract:

- one immutable P7-local admission type, `RecordedTurn`, with an exact field table
  (TURN_INPUT_SCHEMA.md) built only from existing frozen types;
- three admission shapes, **derived** from field presence and never declared by the
  caller (ADMISSION_MODES.md);
- the exact confirmation continuation state and its association rules
  (CONFIRMATION_CONTINUATION.md);
- the exact result-replay evidence, its association rules and its zero-execution
  guarantee (RESULT_REPLAY.md);
- the S08 and S09 input/guard/output/stop contract, and precisely when the dispatcher
  may be entered versus skipped (S08_S09_CONTRACT.md);
- admission validation order, failure representation and the reason mapping onto the
  already-closed `PipelineStopReason` set (ADMISSION_FAILURES.md);
- idempotence and execution-count invariants (IDEMPOTENCE.md);
- a frozen 24-row admission matrix with a pre-implementation digest (ADMISSION_MATRIX.md).

## The central rule

A recorded-turn continuation is not a new source of authority. Admission may transport
control-plane state that JARVIS already established; it may not create permission,
confirmation, execution, a trusted result, provenance trust or an approved response.
Model and provider content cannot author an admission mode, a binding, a claim or a
result. The caller supplies evidence; the frozen engines supply every decision.

## The decisive structural choice

`RecordedTurn` carries **no callable, no store, no clock, no session object and no
executor**, and no boolean that could stand in for an authority decision. There is no
`confirmed`, `approved`, `executed` or `success` field anywhere in the admission API.
Consequently the recorded-only core cannot execute, cannot mint an identifier, cannot
claim a confirmation and cannot construct a `TrustedToolResult` — not because a check
forbids it, but because it holds nothing capable of it. Every execution-count invariant
in IDEMPOTENCE.md follows from the type, not from a guard that could be bypassed.

This is the resolution P-B01 asked for: option 1 of task13b11p/FOLLOWUPS.md — an explicit
recorded-only callable over existing typed projections, with replay evidence produced
outside it. No isolated P5 continuation API is frozen, no executor callback seam is
introduced, and `ConfirmationStore` / `TrustedDispatcher` ownership is unchanged.

## The callable

```
run_recorded_turn(turn: RecordedTurn) -> TurnOutcome
```

One positional argument of exactly type `RecordedTurn`. No second parameter, no keyword
dependency, no default-constructed collaborator. `TurnOutcome` is the alias V1 already
permits: `ApprovedOperationalResponse | ConversationalResponse | PipelineStop`. The
function name is an implementation detail V1 already released; the *shape* above is
frozen. The module is a pure function of its argument.

## Why the three shapes are exactly three, and mutually exclusive

Operator decision (task §19): for P7 v1 confirmation continuation and result replay are
mutually exclusive admission modes. That decision is not arbitrary, and the frozen
production types show why.

In production, confirmation authority is consumed *inside* `TrustedDispatcher._claim`,
which is the same step that binds the approval to the invocation that will run it
(`ConfirmationStore.claim_for_dispatch`). There is no resting `CONFIRMED`. Therefore an
approval exists in exactly two observable conditions:

- **unclaimed** — `ConfirmationState.PENDING`. It authorizes nothing. This is the only
  confirmation state P7 v1 admits, and it admits it as an *observation*, in
  CONFIRMATION_CONTINUATION mode, whose only successful disposition is the existing P6
  `REQUEST_CONFIRMATION` obligation. Mode B has no edge to S09.
- **claimed** — the claim already happened, so an invocation exists and the dispatcher
  owns the outcome. P7 can only ever meet that condition as `invocation.confirmation_id`
  plus the linked `TrustedToolResult`, i.e. RESULT_REPLAY mode. The confirmation fact is
  then a *projection of the invocation/result pair*, not separately admitted authority.

That is the exact equivalence task §19 anticipated, in the direction that holds: mode C
needs no confirmation field because mode C's confirmation fact is already inside its
invocation and result. Supplying both a confirmation record and a result would assert one
turn's approval to be simultaneously unclaimed and claimed. It is contradictory, so it is
refused (ADMISSION_FAILURES.md A-03).

## Scope and non-scope

In scope: the admission API, its validation order, its failure representation and the
S08–S09 seam, for a recorded/static passive composition with zero live reachability.

Not in scope and not authorized by this freeze: implementing the pipeline; a production
request-to-binding derivation (F-MAP-01 stays unfrozen); a live user-visible failure
response (F-FALLBACK-01); schema-v3 conversational obligation validation (F-AUDIT-01);
transport-loss evidence (F-REPLAY-01); any live model, Ollama, provider, registry,
dispatcher, store, audit or provenance activity; Hermes enablement; any policy, schema or
`execution.mode` change.

Do not edit the frozen files silently. A discovered defect in this contract requires
explicit subsequent version history with new hashes and new evidence.
