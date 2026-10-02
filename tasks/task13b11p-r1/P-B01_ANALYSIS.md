# P-B01 ANALYSIS

## What was actually unresolved

Task 13B11P stopped at its §5 API gate. Its finding, restated precisely:

> the proposal guard and `PipelineStop` are frozen, but the complete turn-input API is not
> — specifically S08–S09 confirmation/result replay admission.

Four sub-questions were open:

1. **The aggregate.** `task13b11o/STATE_PROJECTIONS.md:3` says the whole-pipeline input is
   explicitly NOT FROZEN, and V1 freezes constituent boundaries without supplying a
   replacement field/variant table. The plan's conceptual entry `handle_turn(session, text)`
   would have smuggled a store through the `session` parameter.
2. **S08's eligible handoff.** V1 says "eligible handoff → S09" without saying what an
   eligible handoff *is*. `ConfirmationRecord` is explicitly observation, not approval;
   `ConfirmationStore.confirm` is a wall; there is no resting `CONFIRMED`.
3. **S09's evidence.** V1 says "recorded current-result/invocation/claim linkage, or a
   later explicitly isolated P5 boundary with all seven existing gates" — two different
   designs, unselected.
4. **Required-together rules.** Which of confirmation evidence, result evidence, provenance
   selection and the audit projection are required together, and which absence is valid.

The security consequence 13B11P named: choosing implicitly could turn snapshot possession
into confirmation authority, lose executed-result evidence at an early stop, or introduce
an executable callback into a recorded boundary.

## How each is resolved

| Sub-question | Resolution | Where |
|---|---|---|
| 1 the aggregate | one immutable `RecordedTurn` with 21 fields, every one mapped to a stage the frozen guard order already names; no `session`, no store, no clock, no callable | TURN_INPUT_SCHEMA.md |
| 2 S08's eligible handoff | *eligible* is reached only from mode A with an actual `ALLOW`, or from mode C. A confirmation continuation is never eligible — mode B has no edge to S09, and its only successful disposition is the existing P6 `REQUEST_CONFIRMATION` | S08_S09_CONTRACT.md, CONFIRMATION_CONTINUATION.md |
| 3 S09's evidence | the recorded-only design is selected. The isolated P5 boundary is explicitly not frozen and not authorized. A turn that is authorized but has no result **stops** rather than acquiring an executor | S08_S09_CONTRACT.md "When the dispatcher may be entered" |
| 4 required-together | a complete table with `R`/`O`/`—` per mode, plus five explicit required-together groups | TURN_INPUT_SCHEMA.md, ASSOCIATION_RULES.md |

Each named security consequence is closed by construction rather than by a check:

- *snapshot possession becoming authority* — `LedgerSnapshot` is read by the classifier
  context projection and S10 only; no authority input reads it. Possession of a
  `ConfirmationRecord` is admissible only in `PENDING`, and only after twelve-field binding
  equality against this turn's actual route (S-02, S-03).
- *losing executed-result evidence at an early stop* — the retention table in
  ADMISSION_FAILURES.md: a mode-C stop after S09 passes retains the result and its
  `executed` flag; a stop before or at S09 has no established result to retain, which is
  not the same as erasing one.
- *an executable callback in a recorded boundary* — `RecordedTurn` has no callable field of
  any kind, so there is nothing to smuggle one through (S-06, S-12).

## The three facts in the production source that decided the shape

1. `ConfirmationStore.confirm` validates an approval in full and then raises
   `ConfirmationDispatcherUnavailable` without advancing the record. The only edge that
   claims execution is `claim_for_dispatch`, and it binds the approval to the invocation
   that will run it in the same step. There is no state between unclaimed and claimed —
   which is exactly why three admission shapes suffice and why modes B and C are disjoint
   rather than arbitrarily separated.
2. `invocation.confirmation_id is not None` does not prove a claim occurred. Dispatcher
   gate 5 returns `CONFIRMATION_REQUIRED` with `confirmation_absent`,
   `confirmation_binding_absent` or `confirmation_authority_unavailable` while the id is
   present and nothing was claimed. The sound derivation is
   `result.executed and invocation.permission_outcome is REQUIRE_CONFIRMATION`, because the
   executor is reachable only past gate 6 and gate 6 performs the claim. The two frozen P6
   contradiction checks (`CONFIRMATION_EXECUTED_WITHOUT_AUTHORITY`,
   `APPROVAL_WITHOUT_REQUIREMENT`) confirm this is the only non-contradictory mapping, so
   the rule is forced by existing contracts rather than chosen here.
3. `POLICY_TABLE` gives `browser.open` an `ALLOW` base outcome, and `tighten` cannot lower
   an outcome, so under the production `BALANCED` mode `OPEN_URL` is a genuine `ALLOW`.
   The "authorized but no result" case is therefore reachable with the real frozen policy
   and needed no mocked P4 — which matters, because the frozen pipeline matrix forbids
   mocking P4 to make a whole-turn case reachable.

Fact 3 is what turned P-B01 from an interface question into a decidable one: the case the
blocker was really about is a *reachable* case, it cannot be answered by a dispatch, and
the only honest answer in a zero-execution core is a structured stop. That is matrix row
`A03`, `PipelineStop(stage=S09_RESULT, reason=result_invalid)`.

## What this analysis does not claim

No pipeline was implemented, no fixture was scored and no row of the admission matrix was
measured. The matrix is a pre-implementation specification. The authenticity of a
`TrustedToolResult` remains unprovable from type identity alone (F-P7R1-01), and the
admission failure reasons remain coarse (F-P7R1-03). Neither was hidden to make the
contract look complete.
