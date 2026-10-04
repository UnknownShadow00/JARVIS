# Formal P7 exit checklist

Fresh review of 13B11A IMPLEMENTATION_PHASES P7: integration in shadow, CT-001/CT-013; exit requires zero side effects and zero visible change for a measured period. P8 requires P7 exit. Later passive contracts do not amend that gate.

| ID | Requirement | Status | Source | Remaining gap |
|---|---|---|---|---|
| P7-01 | P0–P6 foundations | DONE | tasks/task13b11a/IMPLEMENTATION_PHASES.md:16–22; canonical app/execution | Historical foundation evidence; no new live execution |
| P7-02 | Recorded canonical adapter | DONE | tasks/task13b11n-r1/HERMES_ADAPTER_CONTRACT_V1.md; app/brain/hermes_adapter.py | Native provider transport/normalizer remains absent |
| P7-03 | Passive pipeline/corpus | IMPLEMENTED PASSIVE — UNWIRED | task13b11p-r8 seal; first-scored-run.json and unseen-first.json | 116 frozen +53 unseen cases; not live evidence |
| P7-04 | F-MAP metadata/binding | IMPLEMENTED PASSIVE — UNWIRED | f-map-01-binding-contract-v1, registry-metadata-snapshot-r1, binding-projection-v1-r1 seals | Only OPEN_APP/OPEN_URL; no live consumers |
| P7-05 | Context owner | CONTRACT FROZEN — IMPLEMENTATION MISSING | tasks/p7-shadow-context-contract-v1; 63984cac4bacb0d1a28ef9bff9f0ab3ee7e52200 | Named LedgerStore gate exception required |
| P7-06 | Ingress envelope | CONTRACT FROZEN — IMPLEMENTATION MISSING | tasks/p7-shadow-envelope-contract-v1-r1; 4fb1d4da1342b35f7ed997550a45dccd69922eca | Depends on context implementation; no server consumer |
| P7-07 | Continuation/admission/lifecycle | OPERATOR DECISION | tasks/p7-formal-exit-preparation/OPERATOR-DECISIONS.md D01/D02 | Authentication binding, retries, owner capacity/lifecycle unresolved |
| P7-08 | Passive consumer/test transitions | BLOCKED | Unit C TEST_AUTHORIZATION.md and exact 26-site GATE_INVENTORY.json | No existing test exception approved |
| P7-09 | Authentic live adapter input/provider boundary | BLOCKED | D05 30b4b888e8b4a87c0e59f434f9cb3911bd342377; D06 blocked review | D05 semantics frozen; installed model verified; shared ownership/wire/prompt source/collector missing |
| P7-10 | Evaluator/scheduler isolation | OPERATOR DECISION | 13B11A PRODUCTION_INTEGRATION_PLAN §§7,14; original D07; actual server | D07 not run; mechanism/queue/timeout/cancellation unresolved |
| P7-11 | Observation producer | CONTRACT FROZEN — IMPLEMENTATION MISSING | 28bfd59bc75a176d9804c0aa748f550cb5357390; D03 exact18-field schema | Passive type import gate exceptions required; source fact collection absent |
| P7-12 | Evidence persistence/loss/collection | CONTRACT FROZEN — IMPLEMENTATION MISSING | 39ba8a5686010f74e1e86312c215f75ef5e0253e; D04; D05 compatibility | Sink semantic contract frozen; backend/recovery/collector/upstream accounting implementation missing |
| P7-13 | CT-001 acceptance | OPERATOR DECISION | task13b10d/CONFORMANCE_TESTS.md:26–32; 13B11A P7 row | Final-visible control-plane response and draft-in-audit requirement unresolved for legacy-visible/no-audit-change shadow |
| P7-14 | CT-013 integrated conversation safety | CT REQUIRED | task13b10d/CONFORMANCE_TESTS.md:117–123; P7 phase row | Ordinary safety/leakage integrated evidence absent |
| P7-15 | Scored measurement window/thresholds | OPERATOR DECISION | 13B11A IMPLEMENTATION_PHASES.md P7 exit; original D09 | Recommendations only; pilot does not meet formal acceptance |
| P7-16 | Live zero effects/unchanged visible legacy | LIVE SHADOW REQUIRED | 13B11A IMPLEMENTATION_PHASES.md P7 exit and §7 | No traffic authorized or performed; baseline equality is not live-shadow proof |
| P7-17 | REST/WS capture and wiring | BLOCKED | 13B11A DEPENDENCY_GRAPH; envelope REST_CAPTURE/WEBSOCKET_CAPTURE | D01/D02/D07/D10 and production consumers unresolved; voice separate |
| P7-18 | Rollback/noninterference drill | MEASUREMENT REQUIRED | 13B11A FEATURE_FLAG_AND_ROLLBACK §3; EC-10 | Plan exists; no activation/drill |
| P7-19 | Shared model/resource lifecycle | OPERATOR DECISION | 13B11A PRODUCTION_INTEGRATION_PLAN §§11,21; app/resource_manager.py:559 | Exact ownership/unload-in-flight relation unresolved; cap1 insufficient |
| P7-20 | Current baseline preserved | DONE | Session pytest/golden; entry/final361-file hashes; sealed legacy digest | 5721 pass/11 deselected; golden12/20 unchanged |

Counts: {"BLOCKED": 3, "CONTRACT FROZEN \u2014 IMPLEMENTATION MISSING": 4, "CT REQUIRED": 1, "DONE": 3, "IMPLEMENTED PASSIVE \u2014 UNWIRED": 2, "LIVE SHADOW REQUIRED": 1, "MEASUREMENT REQUIRED": 1, "OPERATOR DECISION": 5}. This is a 20-item evidence checklist, not a project percentage. Three DONE plus two existing IMPLEMENTED PASSIVE — UNWIRED foundations; four contracts await implementation; eleven other requirements remain unresolved. The earlier checklist counted the two passive foundations as DONE (5/20); using the current requested status vocabulary changes that label, not the evidence. No formal measured-shadow exit has been established. P8 BLOCKED.
