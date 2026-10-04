# Canonical formal P7 exit checklist

This checklist decomposes the preserved 13B11A phase exit and later prerequisites into 20 reviewable requirements. Primary status is one of DONE, CONTRACT FROZEN, IMPLEMENTATION MISSING, MEASUREMENT MISSING, OPERATOR DECISION, BLOCKED. Secondary gaps are explicit. Counts are checklist accounting, not a project-wide percentage or permission to advance.

| ID | Requirement | Primary status | Exact authority/evidence | Remaining limitation |
|---|---|---|---|---|
| P7-01 | P0–P6 foundation prerequisites | DONE | 13B11A IMPLEMENTATION_PHASES:16-22; current canonical app/execution and 5721-test regression | Historical prerequisite completion; no new live-use claim |
| P7-02 | P7 recorded adapter foundation | DONE | 13B11N-R1 HERMES_ADAPTER_CONTRACT_V1; canonical app/brain/hermes_adapter.py | Recorded parser implemented, live transport remains P7-09 |
| P7-03 | Passive pipeline and frozen/unseen corpus | DONE | 13B11P-R8 seal: first-scored-run.json, unseen-first.json, zero-execution-proof.json | 116/116 and 53/53; historical passive proof only |
| P7-04 | F-MAP-01 reviewed request/binding producer and metadata | DONE | f-map-01-binding-contract-v1; registry-metadata-snapshot-r1; binding-projection-v1-r1 seals | Two mappings only; no live consumer |
| P7-05 | Session/turn/P2 context contract | CONTRACT FROZEN | tasks/p7-shadow-context-contract-v1; commit 63984ca | IMPLEMENTATION MISSING; protocol separately P7-07 |
| P7-06 | REST/WS envelope contract | CONTRACT FROZEN | tasks/p7-shadow-envelope-contract-v1-r1; commit 4fb1d4d | IMPLEMENTATION MISSING; no live wiring |
| P7-07 | Continuation/admission/lifecycle authority | OPERATOR DECISION | Operator A3; P2 LEDGER_API §§5–6; Context V1 SESSION_LIFECYCLE | Handle representation/binding, retry identity, limits and teardown before wiring |
| P7-08 | Passive owner/composer/evaluator consumers | IMPLEMENTATION MISSING | 13B11A component graph; pipeline RecordedTurn API; A/B contracts | Exact test exceptions and evaluator input/observability contract required |
| P7-09 | Current-turn adapter input and provider/model identity | OPERATOR DECISION | 13B11A TEST_STRATEGY:12,42; 13B11O LIVE-01; Unit C adapter review | Live proposal path absent; replay does not meet live-model exit |
| P7-10 | Evaluator scheduling/failure/resource isolation | OPERATOR DECISION | 13B11A PRODUCTION_INTEGRATION_PLAN §7; actual server.py async graph | No canonical task/thread/queue mechanism or bounds selected |
| P7-11 | Truthful shadow observation/measurement contract | BLOCKED | Operator C1–C2; Unit C SHADOW_MEASUREMENT_FIELD_PROVENANCE | Separate-record direction approved; full fact sources/completeness not defined |
| P7-12 | Measurement collection, storage and loss accounting | IMPLEMENTATION MISSING | 13B11A §7 comparison metrics; LIVE-04; F-AUDIT-01 | Storage/redaction/retention and writer failure contract unresolved |
| P7-13 | CT-001 phase acceptance | OPERATOR DECISION | 13B10D CONFORMANCE_TESTS:26-32; 13B11A P7 phase row and §7 | Final-user-visible control-plane response conflicts with legacy-visible shadow |
| P7-14 | CT-013 integrated conversation/safety proof | MEASUREMENT MISSING | 13B10D CONFORMANCE_TESTS:117-123; 13B11O-R1 pipeline conversation boundary | Compatible in principle; raw candidate alone is insufficient |
| P7-15 | Scored window and acceptance thresholds | OPERATOR DECISION | 13B11A P7 exit measured-period clause; LIVE-01; Unit C recommendation | No duration/sample/rate/latency threshold frozen |
| P7-16 | Measured zero shadow effects and unchanged visible legacy | MEASUREMENT MISSING | 13B11A IMPLEMENTATION_PHASES:23; §7; RISK_REGISTER R-13/R-14 | No shadow traffic authorized or run; fixtures do not substitute |
| P7-17 | Server/API/UI shadow integration with mode off by default | IMPLEMENTATION MISSING | 13B11A DEPENDENCY_GRAPH §§1,4; EC-12; Envelope REST/WS points | No server/API/UI edits; continuation transport still open |
| P7-18 | Rollback drill and noninterference proof | MEASUREMENT MISSING | 13B11A EC-10; FEATURE_FLAG_AND_ROLLBACK §3; R-18 | Plan prepared; no activation or drill executed |
| P7-19 | Shared model ownership/in-flight lifecycle | OPERATOR DECISION | 13B11A PRODUCTION_INTEGRATION_PLAN §11 and §20 no-conflicting-unload | Conditional on chosen provider path; no resource manager/infrastructure changes |
| P7-20 | Current legacy/regression safety baseline | DONE | Unit A/B pytest/golden; sealed legacy digest + 361 unchanged tracked files | Continuous gate currently met; eight golden failures preserved |

**Count:** 5/20 DONE (25% of this checklist); 2/20 CONTRACT FROZEN with implementation missing; 13/20 other unresolved requirements. No formal measured-shadow exit is complete. Counting frozen documents as runtime completion would be incorrect. P8 entry remains BLOCKED.

13B11O-R1 explicitly preserves full shadow/server P7 and P8 waits; 13B11P-R1 through R8 do not amend the graph. R1 admission, R3 V2 projection, R4 consumer gates, R5/R6 PB05 resolution and R7/R8 implementation are incorporated in the current passive pipeline rather than counted repeatedly as separate phase exits. F-MAP-01 production is complete only for the approved two mappings.

F-P7R1-01 result-origin authenticity, F-REPLAY-01 lost-result recovery and confirmation UX/TTL for actual mutation remain before-live-execution concerns, not newly required inert-shadow side effects. F-P7R1-02 refusal replay exclusions, F-P7R1-03 coarse reasons, browser D-01 and FUTURE-AGENT-BRIDGE are preserved. F-FALLBACK-01 and F-AUDIT-01 remain relevant to truthful failure/evidence coverage; no audit-v3 change here. Voice remains separately deferred.
