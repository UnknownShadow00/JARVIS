# ADMISSION FAILURES

## Representation

Admission failure uses the already-frozen `PipelineStop` from
task13b11o-r1/PIPELINE_FAILURE_MODEL.md. No new failure type, field, enum member,
timestamp, failure id or message is added, and `PipelineStop` remains non-renderable: it
is not text and never becomes a user-visible response in this passive contract.

Every stop is JARVIS-owned and deterministic. Every pre-dispatch stop carries
`executed=False` and `result=None`. No `TrustedToolResult.ERROR` is fabricated for an
admission failure, no permission denial is synthesised, no obligation is selected and no
P6 fallback is hand-picked.

## Reason vocabulary — reuse only, no extension

`PipelineStopReason` is a closed set of 23 values under P7-D03. All seven failure
categories the task names are representable within it, so **no P7-local reason is added**:

| Conceptual category | Frozen stage | Frozen reason |
|---|---|---|
| invalid turn shape | `S01_INPUT` | `invalid_input` |
| confirmation/result conflict | `S01_INPUT` | `invalid_input` |
| result not trusted (wrong type / look-alike) | `S01_INPUT` | `invalid_input` |
| confirmation mismatch | `S08_CONFIRMATION` | `confirmation_invalid` |
| confirmation not admissible (state, freshness, claimed, non-confirmable) | `S08_CONFIRMATION` | `confirmation_invalid` |
| result/invocation mismatch | `S09_RESULT` | `result_invalid` |
| result replay not admissible (route, version, authority, support linkage) | `S09_RESULT` | `result_invalid` |

Stage attribution follows ownership of the violated rule: shape, type and turn/session
identity belong to S01; the confirmation record belongs to S08; the invocation/result pair
belongs to S09. `PipelineStage` is a closed identifier, not a count of stages traversed,
so a mode-C turn refused by C-00a stops at `S01_INPUT` without walking S02–S08, and that is
the honest attribution rather than a convenience reordering.

## Granularity limit (recorded)

Several distinct failures share one reason. `confirmation_invalid` covers wrong session,
wrong state, stale, already-claimed, mis-bound and non-confirmable alike, and
`result_invalid` covers every C-01…C-08 failure plus the mode-A `ALLOW`-without-result
case. That is intentional on two grounds:

- the reason set is **closed** by a prior freeze, and FREEZE_RECORD.md of that freeze
  forbids editing it silently;
- for confirmations it is also the correct security property. Reporting *why* a
  confirmation was refused would distinguish "no such record" from "foreign record" from
  "already claimed", which is the existence oracle `ConfirmationStore` deliberately avoids
  (its own `confirmation_not_found` is reported identically for unknown and foreign ids).

`PipelineStop.component_reason` cannot close the gap either: it is restricted to existing
owner machine-codes (declared `AdapterError` codes, confirmation/P5 refusal kinds, P6
contradiction and reason codes) and may not carry a P7-invented string. The distinction is
therefore carried by the **test matrix**: ADMISSION_MATRIX.md records, per row, which named
guard fired, and the implementation's tests assert the guard identity, not a stop field.
Recorded as F-P7R1-03 for a later, explicitly versioned reason extension if one is ever
wanted.

## `component_reason` use, by case

| Case | `component_reason` |
|---|---|
| S05 adapter rejection | the declared `AdapterError` code (`invalid_json`, `invalid_input`, `invalid_response`) |
| mode-C result carrying a dispatcher refusal, surfaced at a later stop | the existing `result.error_kind`, unchanged |
| S11 contradiction | the existing P6 `ObligationContradiction` code |
| every admission guard in this contract | `None` — P7 owns no machine-code vocabulary and invents none |

## Result retention on a stop

Reconciling the two frozen statements "every pre-dispatch stop has `executed=False` and
`result=None`" and "for a post-attempt stop with an existing valid result, `executed`
equals `result.executed` and the same result is retained":

| Stop | `result` | `executed` |
|---|---|---|
| any stop in mode A or mode B | `None` | `False` |
| mode C, stop at `S01_INPUT` (C-00/C-00a/C-00b) | `None` | `False` — the object was never established as this turn's result |
| mode C, stop at any stage before S09 passes, including S02–S08 | `None` | `False` — same reason |
| mode C, stop at `S09_RESULT` (C-01…C-08 failure) | `None` | `False` — an association failure is precisely a refusal to attach this result to this turn; retaining it would perform the attachment the guard refused |
| mode C, stop at `S10_PROVENANCE`, `S11_OBLIGATION`, `S12_RESPONSE` or `S13_AUDIT` after S09 passed | the admitted `turn.result` | `turn.result.executed` |

The last row is the post-attempt case the contradiction policy protects: a genuine attempt
is not erased merely because a later projection is contradictory, and
`PipelineStop.obligation_state`, where it exists, carries that same result or both are
`None`. The rows above it are not "erasing a result": no result had yet been established
for the turn.

`executed=True` with `result=None` is never emitted by P7 v1. The recorded-only core
cannot witness an executor entry, and must not fabricate that state; live
cancellation/transport-loss remains F-REPLAY-01.

## No user-facing prose

An admission failure produces no free-form message, no template, no prompt, no model
fallback and no conversational downgrade. `PipelineStop` is not renderable text. Downstream
P6 remains the only response authority, and only where independently complete, consistent
state genuinely supports a condition and `response.build` accepts its evidence — P7 may
not select a lower obligation or construct an `ApprovedOperationalResponse` itself. No
exact P6 rule currently describes an admission failure, so those turns return a
non-renderable stop. F-FALLBACK-01 stays BEFORE LIVE WIRING.

## No automatic recovery

No retry, no repair, no renewal, no re-ask, no "closest match", no alternative branch and
no subsequent execution after a stop. Malformed projections are rejected, never treated as
defaults.
