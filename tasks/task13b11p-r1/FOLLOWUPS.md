# FOLLOW-UPS

## P-B01 — RESOLVED

The complete recorded-turn admission API is frozen: `RecordedTurn` with its exact 21-field
required/optional/absent table, three derived admission shapes, the exact S08 confirmation
handoff and the exact S09 invocation/result/claim evidence, the validation order, the
failure representation, the idempotence and execution-count invariants, and a 32-row
hashed matrix. Option 1 of task13b11p/FOLLOWUPS.md was taken: a recorded-only callable over
existing typed projections, with every replay fixture generated outside it. Option 2 — an
isolated P5 continuation dependency inside P7 — was explicitly not taken.

No operator decision now blocks implementing the recorded/static passive pipeline.

## New, precisely bounded

| ID | Item | Classification | Required treatment |
|---|---|---|---|
| F-P7R1-01 | `TrustedToolResult` origin cannot be authenticated; type identity is not authenticated origin | BEFORE LIVE WIRING. Not blocking the passive unit, where the caller is always a fixture or a test-owned P4/P5 setup | Enforce exact type identity, C-01…C-08 linkage and C-04…C-07 authority agreement. Before any live consumer exists, specify how a result's dispatcher origin is established — e.g. a dispatcher-held registry of issued `invocation_id`s, which `TrustedDispatcher.dispatched_invocation_ids` already exposes. Do not add a caller-settable trust flag. |
| F-P7R1-02 | Replay of a genuine non-dispatchable-action refusal result is excluded in v1 | Deliberate v1 narrowing. Not blocking; zero execution either way | If it is ever wanted, an operator must first sign which obligation wins when an early route terminal and a `BLOCKED` result are both present. Then extend by explicit version history, with a re-frozen matrix. |
| F-P7R1-03 | Admission failure reasons are coarse: one reason covers several distinct guards | Diagnostic granularity only. Not a security gap; for confirmations uniformity is the desired anti-oracle property | Assert guard identity in tests. Any reason extension requires a versioned amendment to the closed `PipelineStopReason` set with new hashes and new evidence, never a silent edit. |

## Unchanged prerequisites

F-TYPE-01 is implementation work in the next passive task, now fully specified for both
`PipelineStop` and `RecordedTurn`.

F-MAP-01 (production request-to-binding derivation) remains unfrozen and remains BLOCKING
for any branch that derives a binding or dispatches from that mapping, and BEFORE LIVE
WIRING in every case. It does not block pure comparison against explicit caller or static
projections: `turn.expected` and `turn.permission_projection` are admitted, and a missing
one stops with `projection_missing` rather than being derived.

F-FALLBACK-01 (live user-visible response and failed-turn audit path for a stop) and
F-AUDIT-01 (conditional conversational summary obligation validation in schema v3) remain
BEFORE LIVE WIRING and BEFORE LIVE AUDIT WIRING respectively. F-REPLAY-01
(transport/cancellation evidence where a live executor may be entered without a result)
remains BEFORE LIVE WIRING, and is the reason a `ConfirmationRecord` in `EXECUTING` is
inadmissible in mode B.

Real registry integration and capability projection, actual Hermes normalization and
activation, measured shadow, resource ownership, audit durability and redaction,
confirmation TTL and UX, browser D-01 and every other policy change remain separate
approved tasks. None is needed to compare static fixtures, and no item here authorizes a
real tool or a live request path.

## Next dependency

Resume Task 13B11P: P7 PASSIVE PIPELINE IMPLEMENTATION, against the frozen P7 pipeline
contract, this admission contract, recorded Hermes outputs and static/test-double
projections only. The remaining P7 server/API/UI and shadow boundary follows the pipeline;
P8 waits on full P7 exit and is not unlocked by this freeze. Live consumers, shadow mode,
permission policy, confirmation policy and Hermes activation each still require separate
authorization. Stop here.
