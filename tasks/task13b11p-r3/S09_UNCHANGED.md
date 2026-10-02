> **DRAFT — NOT FROZEN. P-B04 blocks completion; see BLOCKER_ANALYSIS.md. This file does not authorize implementation.**

# S09 — RECORDED RESULT ADMISSION, unchanged

Normative replay semantics remain tasks/task13b11p-r1/RESULT_REPLAY.md, S08_S09_CONTRACT.md (S09 section), and ASSOCIATION_RULES.md (invocation/result section). No V2 change to any mode-C matrix object or expected result. References to absent confirmation records mean absent field 15, now the projection. References to the dispatcher non-action set use the equal existing obligations.NON_ACTION_OUTCOMES set, as R2 established; no dispatcher import is required.

S01: exact ToolInvocation and TrustedToolResult identities; pair present together; projection absent; dispatchable action; invocation turn/session equal correlation. S09 C-01 invocation ID and validity; C-02 tool/action identity; C-03 optional correlation child; C-04 actual route agreement; C-05 expected canonical binding; C-06 current versions; C-07 actual recomputed permission outcome/class; C-08 distinct linked historical support. All remain ordered and unchanged.

Mode A reaching ALLOW with no recorded result -> S09 result_invalid, executed=False, result=None. Mode B never reaches S09. Mode C passing association -> S10 provenance -> S11 obligations -> S12 response. Failed association -> S09 result_invalid without retaining the unassociated result. Shape and session failures remain S01 invalid_input.

SUCCESS, ERROR, TIMEOUT, CONFIRMATION_REQUIRED and BLOCKED retain their exact existing dispositions. P6 owns status/executed consistency and contradiction codes; a valid associated result is retained on a downstream stop. No fabricated result, retry or re-dispatch. `confirmation_claimed = result.executed is True and invocation.permission_outcome is PermissionOutcome.REQUIRE_CONFIRMATION` remains a derived P6 input, never an admission assertion.

Zero dispatcher entries, executor calls, new invocations, new trusted results and claims. Type identity still does not independently prove dispatcher origin (F-P7R1-01). Non-dispatchable refusal replay remains excluded (F-P7R1-02). Reasons remain coarse (F-P7R1-03).
