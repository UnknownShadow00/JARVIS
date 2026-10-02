# S08 / S09 CONTRACT

The seam P-B01 named. S08 owns the confirmation requirement; S09 owns the execution
result. Together they decide whether a turn may continue to the response stages, and they
are the only two stages whose behaviour differs by admission mode.

Stage identifiers and the stop reasons available to each are already closed by
task13b11o-r1/PIPELINE_FAILURE_MODEL.md. Nothing here adds a stage, a reason or a field.

---

## S08_CONFIRMATION

### Input

- the derived admission mode;
- the actual `PermissionDecision` from S07 (`permissions.decide` on JARVIS-owned inputs);
- the actual S03 `RouteResult` and the caller's `expected` / `permission_projection`
  projections, already validated at S06;
- `turn.confirmation`, in mode B only;
- `turn.evaluated_at`, for the existing freshness predicate;
- `turn.correlation`.

S08 reads no store, no clock, no model text and no proposal. It never constructs or
mutates a `ConfirmationRecord`, never calls `create_confirmation`, `confirm`,
`claim_for_dispatch`, `deny`, `cancel` or `expire`, and freezes no TTL value.

### Guards

| Mode | S08 behaviour |
|---|---|
| `INITIAL_TURN` | `decision.outcome is REQUIRE_CONFIRMATION` → the **waiting** branch (first ask). `decision.outcome is ALLOW` → **eligible**, continue to S09. `DENY` never reaches S08: S07 routes it to the existing P6 permission terminal. |
| `CONFIRMATION_CONTINUATION` | B-01…B-07 of CONFIRMATION_CONTINUATION.md, in that order. Pass → the **waiting** branch. Fail → stop. Requires `decision.outcome is REQUIRE_CONFIRMATION`; a record presented for an `ALLOW` or `DENY` action fails B-06/B-07 and stops. |
| `RESULT_REPLAY` | no confirmation record is admitted, so S08 has nothing to validate and passes through to S09. The confirmation fact of a replayed turn is derived at S09 from the invocation/result pair (RESULT_REPLAY.md). |

### Output

Exactly one of three:

1. **waiting** — leave the guard walk and continue to S10 → S11 → S12 with
   `result=None`, `confirmation_claimed=False` and the actual
   `permission_outcome=REQUIRE_CONFIRMATION`. The existing `P6-01b` rule selects
   `REQUEST_CONFIRMATION`; `response.build` renders it. No synthetic confirmed boolean is
   produced anywhere on this path.
2. **eligible** — continue to S09. Reached only from mode A with an actual `ALLOW`, or
   from mode C.
3. **stop** — `PipelineStop(stage=S08_CONFIRMATION, reason=confirmation_invalid,
   executed=False, result=None)`.

### Stop conditions

Any failure of B-01…B-07. One reason, `confirmation_invalid`, for all of them; see
ADMISSION_FAILURES.md "Granularity limit".

---

## S09_RESULT

### Input

- the derived admission mode;
- `turn.invocation` and `turn.result`, in mode C only;
- the actual S03 `RouteResult`, the S07 `PermissionDecision`, `turn.expected`,
  `canonicalize.CANONICALIZATION_VERSION`, `permissions.PERMISSION_POLICY_VERSION`;
- `turn.correlation`;
- `turn.supporting_invocation` / `turn.supporting_result`, if present.

### Guards

| Mode | S09 behaviour |
|---|---|
| `INITIAL_TURN` | no result is admitted and the core holds no executor, so there is nothing to continue with: **stop**. |
| `CONFIRMATION_CONTINUATION` | unreachable. The only mode-B outputs of S08 are *waiting* and *stop*; there is no edge from mode B to S09. |
| `RESULT_REPLAY` | C-01…C-08 of RESULT_REPLAY.md, in that order. Pass → continue to S10. Fail → **stop**. |

### Output

1. **continue** — mode C only, with `ObligationState.result = turn.result` and
   `confirmation_claimed` derived exactly as RESULT_REPLAY.md specifies. The dispatcher is
   not entered and the executor call count for the turn is zero.
2. **stop** — `PipelineStop(stage=S09_RESULT, reason=result_invalid, executed=False,
   result=None)`.

### Stop conditions

- mode A reached *eligible* with an actual `ALLOW` and no admitted result;
- any failure of C-01…C-08.

Both carry `executed=False` and `result=None`. No `TrustedToolResult.ERROR` is
manufactured, no permission denial is synthesised, no obligation is selected, and no
retry, repair or alternative branch is attempted.

---

## When the dispatcher may be entered, and when it is skipped

**In P7 v1, never entered.** This is the explicit answer to P-B01's "receiving a completed
replay is not receiving a pending request plus an executor dependency".

- A turn whose action is authorized but whose result does not already exist **stops**. It
  does not acquire an executor, a dispatcher, a callback or a session object in order to
  proceed, because `RecordedTurn` has no field that could carry one. Option 2 of
  task13b11p/FOLLOWUPS.md — an isolated P5 continuation dependency inside P7 — is
  explicitly **not** taken, and nothing here authorizes it.
- A turn whose result already exists **skips** S09's would-be execution entirely and
  resumes at S10 with that result. The dispatcher's seven authority gates are not
  re-run and not re-implemented: their outcome is already recorded in the admitted
  invocation and result, and C-04…C-07 check that the recorded outcome still agrees with
  what the frozen engines decide for this turn.

The frozen dispatch-path proof is preserved verbatim: every admitted continuation to S09
has G1–G6 valid caller/deterministic/adapter state, an executable deterministic route,
exactly one proposal, matching caller association, a present and consistent expected
projection, caller capability, exact tool identity, P3 canonicalization, full canonical
equality, an actual P4 outcome, and — where the outcome requires it — the confirmation
authority that the admitted invocation and result already evidence. A stop at any earlier
stage has no edge to S09. A later recorded `SUCCESS` or a supplied `ALLOW` cannot backfill
a missing earlier gate: C-04…C-07 are checked at S09, after S02–S07 have already run on
the original request, so a replay can only ever agree with those stages or be refused.

P5's internal order (type → structure → canonicalization metadata → permission → required
confirmation inputs → atomic ownership/freshness/exact binding/idempotency claim →
executor) is unchanged, unduplicated and unsubstituted. P7 performs no pre-claim and
offers no proposal→dispatcher shortcut.

## Live wiring is a separate, unauthorized step

Entering a real dispatcher from the pipeline would require: F-MAP-01 (a frozen
request-to-binding producer), F-REPLAY-01 (transport-loss evidence, because a live
executor may be entered without a result arriving), F-FALLBACK-01 (a live user-visible
representation for a stop), and an explicit frozen executor/isolation contract. None of
those exists. This freeze authorizes none of them.
