# Implementation Phases

**Status:** plan only. Ordering is derived from the dependency graph and from what the current
code makes safe, not from the example ordering in the task specification.

Two ordering decisions differ from the generic example and are deliberate:

* **Audit and types come before provenance.** Every later phase needs the correlation ids and the
  typed vocabulary; provenance is the first consumer, not the first requirement.
* **The dispatcher boundary comes before the response engine.** The response engine's whole value
  is refusing to state anything a trusted result does not contain, so the trusted result type must
  exist first, or the response engine would be tested against a stand-in and re-tested later.

| Phase | Deliverable | New modules | Depends on | Tests | Entry criteria | Exit criteria | Rollback point | Production impact |
|---|---|---|---|---|---|---|---|---|
| **P0** | Flag + typed vocabulary | `app/execution/types.py`, `ExecutionConfig` in `app/config.py`, `execution:` block in `config.yaml` (default `legacy`) | — | unit: config defaults to legacy; types immutable | contract v1 committed (done) | `mode: legacy` proven to change nothing; `pytest` and `evals` unchanged | delete the config block | none — nothing reads the flag yet |
| **P1** | Audit vocabulary + correlation | `app/execution/audit_events.py`, additive events in `app/logs/audit.py` | P0 | unit: event envelope, no chain-of-thought field; legacy events unchanged | P0 exit | new events emit in shadow harness only | revert commit | none — events only fire on the new path |
| **P2** | Provenance ledger | `app/execution/provenance.py` | P0, P1 | unit: record/supersede/snapshot; user vs tool trust class | P1 exit | ledger passes CT-006, CT-007 in isolation | revert commit | none |
| **P3** | Classifier + router + canonicalizer + lane | `app/execution/classifier.py`, `router.py`, `canonicalize.py`, `lane.py`, lexicon/grammar data under `config/` | P0, P2 | unit + a pre-registered routing table; CT-005, CT-009, CT-016, CT-017 | P2 exit | deterministic, no model call, reproducible on replay | revert commit | none |
| **P4** | Permission engine + confirmation manager | `app/execution/permissions.py`, `confirmation.py`, `config/permissions.yaml` | P3 | unit: matrix, binding, expiry; CT-004, CT-015 | P3 exit; permission matrix approved by the operator | no path can execute without a decision | revert commit | none while `legacy` |
| **P5** | Dispatcher boundary | `app/execution/dispatch.py` wrapping `registry.call` | P4 | unit with an **inert** dispatcher; CT-002, CT-003, CT-010, CT-014 | P4 exit | typed `TrustedToolResult` only creatable here | revert commit | none while `legacy` |
| **P6** | Obligation engine + operational response builder + raw-prose lock | `app/execution/obligations.py`, `response.py` | P5 | unit: one obligation per turn, priority order; CT-011, CT-012, CT-018 | P5 exit | no operational path can return model text (type-level) | revert commit | none while `legacy` |
| **P7** | Hermes adapter + pipeline + shadow mode | `app/brain/hermes_adapter.py`, `app/execution/pipeline.py`, `mode: shadow` | P6 | integration in shadow; CT-001, CT-013 | P6 exit | shadow runs with zero side effects and zero user-visible change, for a measured period | set `mode: legacy` | shadow compute only |
| **P8** | Inert end-to-end conformance | test-only inert dispatcher fixtures | P7 | full CT-001…CT-018 green | P7 exit | all 18 conformance tests pass against the real control plane | flag | none |
| **P9** | Read-only tools live | none (policy change only) | P8 | integration with `system_stats`, `calendar` read, `web_search`, `screenshot` | P8 exit + operator approval | real read-only results flow through provenance and the response builder | flag | first real user-visible change, read-only |
| **P10** | Confirmation-gated mutations | none (policy change only) | P9 | integration with `apps`, `browser`, `files` move, then `shell` | P9 exit + a clean shadow comparison | mutating actions execute only after a bound, unexpired confirmation | flag | real side effects, confirmed only |
| **P11** | A/B and readiness | comparison harness | P10 | blind A/B legacy vs control plane; golden unchanged | P10 exit | quality no worse, safety metrics zero, EC-01…EC-14 met | flag | production candidate |

## Notes on phase discipline

* Phases P0-P8 have **no production behaviour change** at all: the flag stays `legacy` (or
  `shadow`, which is inert). That is eight reversible phases before the first user-visible effect.
* Each phase is independently revertible because the new package is additive; no legacy function
  is modified until P7 adds a single branch at the top of `_process`.
* No phase may be entered while the previous phase has a failing conformance test. "Nearly
  passing" is not an exit criterion.
* Real destructive tools (`shell`, file delete, `cad` print, messaging) are not enabled before
  P10, and each is enabled individually, not as a class.
