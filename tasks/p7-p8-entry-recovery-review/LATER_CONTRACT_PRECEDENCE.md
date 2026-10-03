# Later contract search and classification

Search scope: canonical task history 13B11O through 13B11P-R8 for P7 exit, passive-only P7, shadow, server/API/UI, P8 entry and graph amendment; R8 and O-R1 copies were hash-matched to Core seals. Findings:

| Source | Class | Meaning |
|---|---|---|
| `task13b11o-r1/P7_PIPELINE_CONTRACT_V1.md` lines 3–9 | Normative **task-local scope limit** | Frozen recorded/static pipeline contract; expressly preserves full P7 shadow/server and P8 gate |
| `task13b11p-r1/RECORDED_TURN_ADMISSION_V1.md`, `FOLLOWUPS.md` lines 47–53 | Normative **task-local scope limit** | Recorded-only API and replay; P8 waits on full P7 |
| `task13b11p-r2` through `-r7` contract/follow-up records | Task-local repair/deferment | Admission V2, tests and implementation authorization; no changed phase gate |
| `task13b11p-r8/FINAL-REPORT.md` lines 39–47, `FOLLOWUPS.md` | Normative task result and **deferment** | Passive implementation verified; live server/shadow left separate; no P8 authorization |
| `task13b11o/FOLLOWUPS.md` LIVE-01–05 | Deferment | Wire normalizer, model identity/window, capability projection and audit writer left for later P7 work |
| 13B11A `DEPENDENCY_GRAPH.md` and `IMPLEMENTATION_PHASES.md` | Unamended phase authority | Formal P7→P8 gate remains |

**Normative graph amendments found: none.** R8's “passive next step” review wording is a task-local note, not P8 entry authority. The previous `14c9b99` review remains provisional/non-canonical as an environment review even though the central phase-gate interpretation is now corroborated on Core.
