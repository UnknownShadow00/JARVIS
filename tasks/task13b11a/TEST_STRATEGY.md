# Test Strategy

**Status:** plan only. Existing `tests/` and `evals/` are unchanged and remain the regression gate.

## 1. Layers

| Layer | Scope | Where | Gate |
|---|---|---|---|
| **Unit** | classifier, router, canonicalizer, lane, permissions, confirmation, provenance, obligations, response builder | `tests/execution/*_test.py`, following the existing `*_test.py` convention | every phase |
| **Contract** | CT-001…CT-018 from `CONFORMANCE_TESTS.md` | `tests/contract/` | P8 and every phase thereafter |
| **Integration (inert)** | adapter → guard → permission → inert dispatcher → provenance → response | `tests/execution/integration/` with a synthetic dispatcher | P8 |
| **Shadow** | live model, live classification, **zero** side effects, no user-visible change | runtime mode, measured from audit | P7 |
| **Read-only live** | real `system_stats`, `calendar` read, `web_search`, `screenshot` | manual + integration | P9 |
| **Confirmation-gated mutation** | `apps`, `browser`, `files` move, then `shell`, one at a time | manual with operator present | P10 |
| **A/B** | legacy vs control plane on the same inputs | comparison harness + `evals` | P11 |
| **Regression** | `pytest` suite and `python -m evals.runner --mode deterministic` | existing | every phase |

## 2. Rules carried over from the C3/C4/C5 method

These are the practices that made the diagnostic results trustworthy, and they apply to
implementation testing too:

1. **Pre-register expectations.** Routing and obligation expectations are written and frozen
   before the run that measures them; a rubric edited after seeing results is not evidence.
2. **Assert on the final user-visible output**, not only on internal state.
3. **A containment test needs a real unsafe draft.** Passing because the model behaved is not a
   pass (CT-001, CT-014).
4. **No per-case branches.** A reviewer checks that the same code path serves unrelated inputs.
5. **Abort and restart on any mid-run change.** A scored comparison run whose code changed
   half-way is discarded, not patched.
6. **Separate model-quality metrics from system-safety metrics** in every report (§20).

## 3. Conformance test ownership

| Test | Phase first green | Component under test |
|---|---|---|
| CT-005, CT-009, CT-016, CT-017 | P3 | router / lane |
| CT-004, CT-015 | P4 | permissions / confirmation |
| CT-002, CT-003, CT-010, CT-014 | P5 | dispatcher / trusted result |
| CT-006, CT-007 | P2 (ledger) re-verified at P6 | provenance / attribution |
| CT-011, CT-012, CT-018 | P6 | obligation engine |
| CT-001, CT-013 | P7 | pipeline with a live model |

## 4. Fixtures

* An **inert dispatcher** (synthetic results, no side effects) reused from the C3/C4/C5 method —
  re-implemented as a test fixture, not copied from the harness.
* A **CPython audit-hook assertion** proving zero real side effects during inert phases; this is
  the technique that produced the "0 real side effects" evidence in C4/C5 and it transfers
  directly.
* **Recorded model outputs** (including known-unsafe drafts) so containment tests do not depend on
  sampling luck.

## 5. What is explicitly not a test target in v1

Adversarial prompt-injection corpora, tool timeout injection, and stale-confirmation replay were
**not** exercised in C3/C4/C5 (contract failure model F-08, F-13, F-15). They should be added as
first-class tests during P4-P7 rather than inherited as assumptions.
