# Production Integration Entry Criteria — Agent Execution Contract v1

**Status:** FROZEN FOR IMPLEMENTATION (Task 13B10D). None of these criteria is implemented by this
task. They define when production Hermes-enablement *work* may begin — not when it may ship.

A criterion is met only when it is demonstrated and recorded, not when it is planned.

| # | Criterion | Met today? |
|---|---|---|
| EC-01 | Contract v1 committed to the workspace and referenced by the implementation plan | Yes (this task) |
| EC-02 | Conformance test specification exists (`CONFORMANCE_TESTS.md`) | Yes (this task) |
| EC-03 | Conformance tests implemented and passing against the real control plane | No |
| EC-04 | Permission model implemented: classes, per-action mapping, deny-before-dispatch | No |
| EC-05 | Confirmation state machine implemented, including binding and expiry/freshness | No |
| EC-06 | Production tool dispatcher conforms: sole executor, bound results, canonical arguments | No |
| EC-07 | Provenance ledger implemented with sources, supersession and current-vs-superseded | No |
| EC-08 | Audit implemented per §19, excluding chain-of-thought | No |
| EC-09 | Operational response lock implemented: one obligation per turn, no model-raw fallback | No |
| EC-10 | Rollback path exists and is tested (disable flag, revert commit, restore config) | No |
| EC-11 | Current production baseline preserved and re-verifiable (golden 12/20, same eight failures) | Yes |
| EC-12 | Integration tested behind a feature flag, off by default | No |
| EC-13 | No direct public AI endpoint introduced; loopback/private network only | Yes (unchanged) |
| EC-14 | A written plan mapping the contract onto existing JARVIS code (Task 13B11A) | No |

**Gate.** Hermes **MUST NOT** be enabled in production until EC-01 through EC-14 are all met and
recorded. Meeting them authorizes integration work behind a flag; it does not authorize shipping
an enabled assistant to daily use, which needs its own acceptance.
