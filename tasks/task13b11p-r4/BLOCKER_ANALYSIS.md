# P-B05 — unchanged admission C15 conflicts with frozen guard order

**JARVIS P7 ADMISSION V2 FINALIZATION BLOCKED**

P-B04 is fully authorized and resolved. This is a separate discovered contract conflict, exposed while checking whether an exact implementation corpus can be frozen without moving unrelated semantics.

## Two binding requirements cannot both hold

Admission V1 admission-matrix.json row C15 requires a conversational request plus an unrelated executed result to reach S09_RESULT and stop with result_invalid at C-04. Its detail explicitly says the existing lane escalates to OPERATIONAL and C-04 then fails on route NONE versus the invocation action. All 23 non-confirmation rows, including C15, must remain unchanged in this repair.

P7 Pipeline Contract V1 UPDATED_GUARD_ORDER.md order 7 instead branches on the actual deterministic route before S06–S09: NONE with zero proposals goes to the conversational/non-action P6 path; NONE with proposals stops unexpected_proposal. Only a supported resolved single action reaches S06. PROPOSAL_GUARD.md requires actual route/action projection consistency. RESULT_REPLAY.md places C-04 at S09 after C-01–C-03, and S08_S09_CONTRACT.md says S02–S07 have already run before those association guards. Admission V1 expressly makes the pipeline contract higher precedence; it supplies missing detail and does not override that order.

## First-hand component evidence

At unchanged production, classify('What is a cache?') returns GENERAL_EXPLANATION and route returns NONE, target=None. lane.explain with tool_result=True returns OPERATIONAL, for proposal counts 0, 1 and 2. Lane escalation does not change the route. The evidence script calls only these pure components; it does not construct a result or pipeline, call a dispatcher or score a pipeline.

| Complete proposal-count partition | Frozen earlier branch | Why C15 cannot reach its required S09 stop |
|---|---|---|
| zero | NONE -> non-action P6 | No S06–S09 edge exists in the frozen walk. An unrelated supplied result cannot be passed to P6 as admitted: S09 has not established association. |
| one | NONE + proposals -> unexpected_proposal | Earlier stop at S06_CARDINALITY, not S09/result_invalid. |
| greater than one | same NONE + proposals branch | Same earlier stop; neither cardinality nor replay grants a routed action. |

These exhaust all proposal cardinalities. Using any malformed earlier input only stops sooner. Supplying caller fields to fabricate an executable route contradicts the actual router and S06 consistency guards. Labelling the expected stop S09 while checking C-04 early would change the ordered guard contract; ADMISSION_FAILURES.md says stage attribution is not a convenience reordering. Relabelling C15 as a component-only fixture would change its existing whole-admission meaning and cannot honestly claim coverage of run_recorded_turn.

## Required decision and unchanged evidence

A versioned reconciliation must choose the priority for mode-C results on non-executable routes: explicitly amend the guard walk/association location, or amend C15's expected stage/reason/fixture scope. Both reach beyond P-B02/P-B04 and require a new contract decision. No option is implemented or selected here. No new stop reason is needed merely to document the conflict.

The 23/32 versus 9/32 migration count remains verified. C15 remains byte-equivalent as a row object; no unrelated row moved. A complete exact fixture corpus cannot be declared frozen while its binding expected outcome contradicts the guard walk. V2 and fixtures remain unfrozen. P-B04 and its exact authorization records can be sealed independently without claiming final contract completion.
