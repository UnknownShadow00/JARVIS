# P-B06 implementation authorization supplement — FROZEN

Operator: Task 13B11P-R8 §§2–8. Historical R6 semantic contracts/corpus and P-B03/P-B04 inventory are unchanged. This supplement resolves only the R7 inventory omission.

File: `tests/execution/canonicalize_non_activation_test.py`.
Function: `test_there_are_zero_live_canonicalization_call_sites`.

| Existing assertion | Exact authorized replacement | Authorized relationship |
|---|---|---|
| `assert callers == []` | `assert callers == ["app/execution/pipeline.py:canonicalize("]` | Only canonical passive P7 calls existing `canonicalize`. `CanonicalizationResult(` construction remains forbidden everywhere outside its owning module. |
| `assert declarers == ["app/execution/audit_events.py", "app/execution/confirmation.py", "app/execution/dispatch.py", "app/execution/types.py"]` | `assert declarers == ["app/execution/audit_events.py", "app/execution/confirmation.py", "app/execution/dispatch.py", "app/execution/pipeline.py", "app/execution/types.py"]` | Only P7 is added as a `canonicalization_version` declarer, required by the frozen projection and B-06/C-06 guards. |

Retain the complete existing all-app scan, all old entries, and every other test function. At this same site add an AST restriction: pipeline canonicalizer names exactly within `canonicalize`, `CanonicalizationResult` (reference/type only), `CanonicalizationError`, `CANONICALIZATION_VERSION`; only `canonicalize` may be called. This strengthens the two exact exceptions; it grants no third relaxation. No aliases, wildcard consumers, dynamic lookup, server calls, live request-path consumers, alternate versions or copied normalization. Every second new consumer remains forbidden.

Exactly two assertion instances, one function, one additional file. Combined P-B03/P-B04/P-B06 scope: 22 instances, 11 sites, 6 existing test files. Confirmation and dispatch tests: zero modifications. Any further historical assertion transition requires a new operator decision.

The canonicalizer keeps sole normalization authority and its existing version. Pipeline remains passive/unwired, receives no execution authority, provider access or live integration. Freeze must precede pipeline creation; freeze receipt records absence and digest. No later silent edits.
