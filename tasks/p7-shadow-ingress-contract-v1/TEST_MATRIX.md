# Future implementation tests — pre-registered categories

| Case | Required assertion |
|---|---|
| pure conversation / CT-013 | no binding; conversational shadow outcome or explicit model-free observation; legacy reply unchanged |
| OPEN_APP, OPEN_URL | exact frozen binding, current P4 decision, zero new-path tool call |
| unsupported action / ambiguous target | no invented binding or execution |
| permission DENY / REQUIRE_CONFIRMATION | observation only; no confirmation record/claim |
| client fake capability/permission/target | ignored or rejected before producer authority |
| model fake success / exact proposal / mismatch / zero / multiple proposals / CT-001 | exact P7 guard and no operational draft exposure |
| producer/adapter/P7 failure and timeout | typed observation, no legacy failure or extra latency beyond frozen bound |
| REST, WS streaming and WS fallback | one shadow attempt per accepted turn; same legacy reply/stream |
| audit/measurement write failure | no operational truth fabrication; legacy continues |
| no-side-effect sentinels | 0 new-path dispatcher, registry.call, handler, executor, confirmation mutation, provenance write, operational audit |
| flag off/malformed/rollback | no shadow entry and identical legacy behavior |

Pre-register concrete inputs, outputs and acceptance criteria before implementation. Recorded unsafe drafts are permitted in test fixtures only; scored real shadow period remains later.
