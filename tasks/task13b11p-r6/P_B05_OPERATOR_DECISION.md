# P-B05 — operator Option A, R6

Authority: the current Task 13B11P-R6 operator instruction §§1–9. R5 identified a missing exact rejection boundary; this instruction selects it. Option A is binding. Option B (early rejection-only C-04 / S09_RESULT label / ordering exception) is explicitly rejected.

After valid S01, classification, routing, initial lane, successful recorded parsing and final lane: actual route NONE + nonzero proposals stops S06_CARDINALITY / unexpected_proposal. Actual route NONE + zero proposals + derived Mode C stops S06_PROJECTION / projection_invalid, before the non-action P6 branch. This refusal-only branch cannot admit a result or enter supported-action matching/permissions/S08/S09/P6.

Exact stop: correlation=turn.correlation, stage=S06_PROJECTION, reason=projection_invalid, executed=False, result=None, obligation_state=None, component_reason=None. No new stage or reason. The positive-proposal stop has the same null/false fields and S06_CARDINALITY / unexpected_proposal.

Route NONE invalidates this recorded operational projection before P6 consumption. Projection validation owns that rejection. Existing cardinality precedence is preserved; S09 remains the full recorded-result admission boundary, without an early C-04 exception. No operational response is constructed from this invalid state. No authority, permission, confirmation, execution or lifecycle policy changes. No live action occurs.

Scope is the exact NONE branch selected in R5/R6. Other guard conditions, modes and owner decisions remain frozen. P-B02/P-B03/P-B04 are not reopened.
