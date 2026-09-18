# Production Entry Roadmap — EC-01…EC-14

**Status:** plan only. Source of the criteria: `tasks/task13b10d/PRODUCTION_ENTRY_CRITERIA.md`
(contract v1).

| EC | Criterion | Status today | Phase that satisfies it | Validating test / task |
|---|---|---|---|---|
| EC-01 | Contract v1 committed and referenced by the plan | **Met** (`5dd853e`, referenced throughout this plan) | — | this task |
| EC-02 | Conformance test specification exists | **Met** (`CONFORMANCE_TESTS.md`, CT-001…CT-018) | — | Task 13B10D |
| EC-03 | Conformance tests implemented and passing against the real control plane | Not met | P8 (implemented), re-run in P11 | Task 13C (re-scoped) |
| EC-04 | Permission model implemented: classes, per-action mapping, deny-before-dispatch | Not met | P4 | unit + CT-015 |
| EC-05 | Confirmation state machine with binding and expiry | Not met | P4 | unit + CT-004 + replay/expiry tests |
| EC-06 | Production dispatcher conforms: sole executor, bound results, canonical arguments | Not met | P5 | CT-002, CT-003, CT-010, CT-014 |
| EC-07 | Provenance ledger with sources, supersession, current-vs-superseded | Not met | P2 | CT-006, CT-007 |
| EC-08 | Audit per §19, excluding chain-of-thought | Partially met (transport and correlation exist) | P1, completed by P6 | audit field coverage test |
| EC-09 | Operational response lock: one obligation per turn, no model-raw fallback | Not met | P6 | CT-011, CT-012, CT-018 |
| EC-10 | Rollback path exists and is tested | Not met (no flag-driven path yet) | P0 for the flag; drill at P7 and P9 | rollback drill recorded in evidence |
| EC-11 | Current production baseline preserved and re-verifiable | **Met** (golden 12/20, same eight failures; verified again in this task by commit hash and clean tree) | every phase | `python -m evals.runner --mode deterministic` |
| EC-12 | Integration tested behind a feature flag, off by default | Not met | P7 (shadow), P9-P10 (live) | shadow-mode audit review |
| EC-13 | No direct public AI endpoint introduced | **Met** (loopback binding, bearer token, WS origin checks) | maintained through P11 | config + binding check each phase |
| EC-14 | Written plan mapping the contract onto existing JARVIS code | **Met by this task** | — | this document set |

## Summary

* Met today: **EC-01, EC-02, EC-11, EC-13, EC-14** (five).
* Partially met: **EC-08**.
* Remaining: **EC-03, EC-04, EC-05, EC-06, EC-07, EC-09, EC-10, EC-12** (eight), all covered by
  phases P0-P11.

**Gate restated.** Hermes may not be enabled in production until all fourteen are met and
recorded, and meeting them authorizes flag-gated integration work — not shipping an enabled
assistant into daily use, which needs its own acceptance.
