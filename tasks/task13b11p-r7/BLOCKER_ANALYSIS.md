# P-B06 — canonicalizer whole-app isolation gate missing from authorization

Classification: CONTRACT DEFECT in the frozen test-change inventory. Implementation task §41 mandates STOP. R6 P_B03_TEST_CHANGE_INVENTORY.md's zero-change table cites only `_modules_outside_the_execution_package`; it does not describe the independent full-app loop in `test_there_are_zero_live_canonicalization_call_sites`.

Actual file: tests/execution/canonicalize_non_activation_test.py, function test_there_are_zero_live_canonicalization_call_sites. Both assertions use the same unchanged all-app scan and exclude only canonicalize.py. Existing source is preserved in evidence.

| Assertion | Existing expected | Required observed addition | Why binding |
|---|---|---|---|
| line 57 `callers == []` | zero call-site markers anywhere under app | `app/execution/pipeline.py:canonicalize(` | Final guard order S06_CANONICALIZE and proposal guard require actual P3 canonicalization, with no duplicate alias rules. |
| line 65 `declarers == [...]` | audit_events.py, confirmation.py, dispatch.py, types.py only | app/execution/pipeline.py | SettledConfirmationProjection has exact field canonicalization_version; S08 B-06 and S09 C-06 consume it. |

The second assertion is reached only after the first passes; R7 did not edit the test to expose it. Running the identical scan directly produced the five exact declarer paths and is recorded in canonicalizer-exact-conflict.json. Frozen source field names and required calls make the conflict substantive. Aliasing a call, hiding a name, dynamic dataclasses/imports or source-text tricks would evade the invariant; none is a repair.

## Exact requested authorization — NOT GRANTED by R7

1. In this function only, retain the entire scan and replace the caller expectation with exactly `["app/execution/pipeline.py:canonicalize("]`. `CanonicalizationResult(` construction remains absent in every production module. Every second canonicalization caller remains forbidden.
2. Retain all four existing declarer entries, adding only `"app/execution/pipeline.py"` between dispatch.py and types.py in sorted order. No arbitrary sibling module or wildcard.
3. Add an exact AST budget in this authorized site: pipeline may consume only canonicalize, CanonicalizationResult (type/reference only), CanonicalizationError and CANONICALIZATION_VERSION from the canonicalizer; only canonicalize may be called. Retain outside-package ban, all live request-path assertions, purity checks and every other test function unchanged. No alias/dynamic lookup escape.

This is **two additional existing assertion instances at one existing site in one additional file**. If separately approved, total inventory becomes 22 instances / 11 sites / 6 files. The current frozen 20 / 10 / 5 inventory remains historical and unchanged. Any revised inventory must be explicitly versioned and sealed before resuming. No stage, proposal, permission, confirmation, replay or Option A outcome change is requested.

R6 contract/corpus remain unedited. No corpus expectation was changed. No production commit. No implementation can claim acceptance until the operator decides this exact addition and all remaining gates run.
