# Decision packet — R5: NEW OPERATOR DECISION REQUIRED

## QUESTION

For an otherwise well-shaped mode-C turn with actual route NONE and zero proposals, where the recorded invocation/result is for a dispatchable action, where must P7 reject the route/result conflict before the non-action P6 branch? Existing authority requires rejection but does not specify this exact boundary. For every nonzero proposal count, existing S06_CARDINALITY/unexpected_proposal already wins and remains unchanged under both options.

## OPTION A — dedicated rejection at the non-action branch

After actual classification/routing, successful recorded parsing and final lane, retain the existing NONE+nonzero stop. For NONE+zero in mode C, add a refusal-only projection guard immediately before the non-action P6 terminal. Exact outcome: PipelineStop(stage=S06_PROJECTION, reason=projection_invalid, executed=False, result=None, obligation_state=None, component_reason=None). The guard compares actual route NONE with the dispatchable recorded invocation; it can only stop, never admit a result or select an obligation. It does not run supported-action binding/permission checks or reach S09.

Security: preserves normal guard order, no result promotion, no downstream P6, no execution or new authority. Compatibility: adds a narrowly specified rejection branch and changes C15's zero-case stage/reason. Explicitly authorizes that S06_PROJECTION label for this refusal even though the ordinary successful S06 walk still requires a supported action. All other rows and the closed reason vocabulary remain unchanged. A positive-count C15 subcase stays S06_CARDINALITY/unexpected_proposal.

Affected documents/tests: C15 must become cardinality-explicit (one parent case with zero/positive variants, or separately indexed rows); guard-order branch table; admission failure stage mapping; C15-dependent summaries and future fixtures. Existing production tests: no edits. Future new pipeline tests cover this branch, ensure P6/S09 not called, and preserve N24. P-B03/P-B04 test-change inventory unchanged.

## OPTION B — early rejection-only route association

Keep the existing NONE+nonzero stop. For NONE+zero in mode C, perform the C-04 route mismatch check at the same pre-terminal point and immediately return PipelineStop(stage=S09_RESULT, reason=result_invalid, executed=False, result=None, obligation_state=None, component_reason=None). This is a specifically authorized early rejection check, not successful S09 admission. It must never continue to C-05–C-08, P6 or any execution boundary on this branch. Ordinary successful S09 still requires every earlier gate.

Security: also rejects without result promotion or execution. Compatibility: preserves C15's zero-case label but explicitly changes C-04 timing and the prior all-C-guards-at-S09 ordering; document why the diagnostic S09 label differs from traversal. This is not already authorized by the generic “stage is an identifier” sentence. Positive-count C15 changes to the existing unexpected_proposal expectation. Same dependent documents/new tests as A, plus RESULT_REPLAY.md and S-09 ordering exception. P-B03/P-B04 inventory unchanged.

## RECOMMENDED OPTION

**A**, because it preserves S09 as the single full recorded-result admission point and localizes rejection to the branch that cannot admit a result. This is an architectural preference supported by the sealed separation of stages, not an existing mandate for the proposed stage/reason. Do not implement or freeze it without an explicit decision.

No option changes permission, confirmation, result origin, obligations, proposal selection, dispatcher authority or live behavior. No option admits non-dispatchable-invocation replay (F-P7R1-02). Do not treat “feed P6 the unassociated result”, “drop the result”, “invent an action”, “skip proposal guards” or “dispatch” as alternatives. Scope here is actual NONE, not a blanket change to all early route terminals; broader cases require their own evidence before final corpus freeze.
