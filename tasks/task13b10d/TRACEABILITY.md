# Traceability — contract clause → validated task → artifact → evidence

**Status:** FROZEN FOR IMPLEMENTATION (Task 13B10D).

Every normative section of `JARVIS_AGENT_EXECUTION_CONTRACT.md` traces to behaviour that was
actually measured in Tasks 13B10C3, 13B10C4 or 13B10C5. The artifacts named below are
**TEST-ONLY** diagnostic code held in evidence bundles and in `tasks/task13b10c3|c4|c5/`. They
**MUST NOT** be copied into production; they are the specification's evidence, not its
implementation.

Evidence bundles (on the Core host, under the PoC evidence directory):

| Bundle | Files | Manifest | `SHA256SUMS` sha256 |
|---|---|---|---|
| `task13b10c3-provenance-lock` | 94 | 93 | `6e39a8768c6a05b49e243c8eaa3d8bf16e38b8e15ce4e3eebba4dc6865468e1e` |
| `task13b10c4-action-routing` | 146 | 145 | `6f562c404e5b6dd85c1b494c2ad7c203e493cd2608934b642ee4e89e9e7c6e06` |
| `task13b10c5-operational-utility` | 137 | 136 | `97c2042467cd2d5a6817e8f59ca92da36e17d273eada96bcfd265857694ec456` |

| Contract clause | Validated in | Artifact (test-only) | Evidence |
|---|---|---|---|
| §3 Trust boundary; §4.2 operational lane lock | 13B10C3 | `provenance_lock.py` (`d868b879…`, byte-identical in C3/C4/C5) | C3/C4/C5 `safety-metrics.json`, `operational-draft-review.json` |
| §4 Lanes; §4.3 lane policy | 13B10C3 | `lane.py`, `lane-policy.json` | C4/C5 `final-response-sources.json` (lane per turn) |
| §5 Request classification | 13B10C3 → C4 | `task13b10c2_classifier.py` | C5 `classification-ledger.json` |
| §5.2–5.4 Router outputs, segmentation | 13B10C4 | `task13b10c4_action_router.py` (`20b126f7…`), `action-lexicon.json`, `connector-grammar.json` | C4/C5 `routing-metrics.json`, `routing-decisions.json` |
| §6 Primary action types | 13B10C4 | `action-lexicon.json`, `tool-schemas.json` | C4/C5 `routing-preregistration.json` |
| §7 Reporting intent non-executable | 13B10C4 | router reporting-intent extraction | C4 `j04-j06-causal-comparison.json` (0/5 → 5/5), C5 `routing-metrics.json` |
| §8 Multi-action policy | 13B10C4 → C5 | `task13b10c_proposal_guard.py` (`9488fd2d…`) | C4 multi-action blocks 10/10; C5 20/20, 0 dispatches |
| §9.1–9.2 Canonicalization | 13B10C3 | `task13b10c_provenance.py::canonicalize` | C5 `tool-proposals-and-results.json` (raw + canonical per event) |
| §9.3 Provenance records | 13B10C3 | `task13b10c_provenance.py::Ledger` | C5 `per-turn-ledger.json` (`ledger_snapshot`) |
| §10 Correction semantics | 13B10C3 → C5 | ledger supersession + response layer | C5 `visible-response-audit.json` (stale corrected value 0) |
| §11 Permission classes | *structure only* | proposal guard + dispatcher gating | C5 `safety-metrics.json` (0 executions, 0 invented targets) — full matrix **not** implemented |
| §12 Confirmation | 13B10C3 → C5 | dispatcher `confirmation_required`, `executed=false` | C5 `safety-metrics.json` (29 events, 0 bypass) |
| §13 Capability limits | 13B10C4 → C5 | router `UNKNOWN_ACTION` + `task13b10c5_response.py` | C5 `obligation-metrics.json` (25 capability responses) |
| §14 Response obligations + priority | 13B10C5 | `task13b10c5_response.py` (`d9e64483…`), `response-obligation-design.json` | C5 `obligation-metrics.json` (350/350, consistency 350/350) |
| §15 Deterministic operational responses | 13B10C5 | `task13b10c5_response.py`, `deterministic-operational-templates.json` | C5 `final-response-sources.json`, `grounded-detail-preservation.json` (97.9%) |
| §16 USER_FACT attribution | 13B10C5 | response layer attribution rules | C5 `attribution-ledger.json` (170/170 = 100%) |
| §17 Ambiguity | 13B10C4 → C5 | guard `AMBIGUOUS_ACTION` + `REQUEST_TARGET` | C5 `routing-metrics.json` (25/25 blocked) |
| §18 Tool-result trust | 13B10C3 → C5 | `task13b10a_control_plane.py` dispatcher, provenance intake | C5 `tool-proposals-and-results.json`, audit-hook proof (0 side effects) |
| §19 Audit | 13B10C3 → C5 | per-turn record written by the harness | C5 `per-turn-ledger.json`, `all-draft-review.json` |
| §20 Metric separation | 13B10C5 | analysis split | C5 `metrics.json` (model quality vs safety sections) |
| §21 Prompt injection | 13B10C3 → C5 | lock + guard refusing model-authored authority | C5 `manual-review-ledger.json` (92 unsafe drafts contained) |
| §22 INV-001…INV-020 | C3/C4/C5 | all of the above | C5 `safety-metrics.json`, `visible-response-audit.json`, `counterfactual-review.json` |

## Invariant → evidence

| Invariant | Strongest evidence |
|---|---|
| INV-001 | C5: 350 operational drafts, 92 manually unsafe, **0** user-visible |
| INV-002 / INV-003 | C5: 0 `executed:true` results; trusted provenance only from the dispatcher |
| INV-004 / INV-014 | C5: 29 confirmation-required events, 0 bypass, 0 deploy/delete executions |
| INV-005 | C5: 25/25 ambiguity turns blocked, 0 invented destructive targets |
| INV-006 | C5: raw + canonical arguments recorded for every proposal |
| INV-007 / INV-019 | C5: 0 stale corrected values visible across 395 turns |
| INV-008 | C5: attribution 170/170 |
| INV-009 | C5: 350/350 turns with exactly one obligation |
| INV-010 | C5: 0 operational `MODEL_RAW`; 0 sources outside the allowed set |
| INV-011 | C5: 20/20 unsupported actions answered as capability-unavailable, 0 substitutions |
| INV-012 | C5: 20/20 multi-action turns, 0 dispatches |
| INV-013 / INV-015 | C5: 0 real side effects under the CPython audit hook |
| INV-016 | C5: 0 lane disagreements between the frozen lock shadow and the response layer |
| INV-017 | C4: J04–J06 0/5 → 5/5; C5: reporting intent 395/395 with no extra dispatch |
| INV-018 | C5: `MISSING_CONTEXT` misuse 0 |
| INV-020 | C3–C5: no model text ever altered a control-plane decision |
