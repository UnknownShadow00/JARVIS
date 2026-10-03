# Open follow-up classification

Each item has one primary bucket. A = blocks passive P8 entry; B = before live wiring; C = deferred/nonblocking; D = operator decision required now. “Passive P8” is not yet a frozen unit, so A includes the unfulfilled formal phase gate and missing verification; B/C classify follow-ups relative to a future explicitly scoped recorded-only test unit.

| Item | Bucket | Reason and source |
|---|---|---|
| Formal P7 exit (server/API/UI, shadow period, CT-001/013) | A | 13B11A `IMPLEMENTATION_PHASES.md` P7/P8 rows and `DEPENDENCY_GRAPH.md` §1 |
| R8 baseline/evidence verification in this workspace | A | Named commit/object and bundle absent; `evidence/R8_VERIFICATION.md` |
| Passive P8 scope/entry amendment | D | 13B11A defines only full P8; R8 `FOLLOWUPS.md` expressly withholds automatic P8 start |
| F-P7R1-01 origin authenticity | B | `task13b11p-r1/FOLLOWUPS.md` row 01: type identity cannot prove dispatcher origin; before live consumer |
| F-MAP-01 request-to-binding producer | B | `task13b11o-r1/FOLLOWUPS.md` row F-MAP-01: blocks deriving/dispatching, not static projection comparison |
| F-FALLBACK-01 stopped-turn live response/audit | B | same file row F-FALLBACK-01; passive stop is non-renderable |
| F-AUDIT-01 conversation summary obligation | B | same file row F-AUDIT-01; before live audit wiring |
| F-REPLAY-01 lost-result/cancellation evidence | B | same file row F-REPLAY-01; before live executor wiring |
| Real capability/registry projection, Hermes normalization/activation, resource ownership, audit durability/redaction, confirmation TTL/UX | B | `task13b11o-r1/FOLLOWUPS.md` §Preserved before-live decisions; R8 `DEFERRED.md` |
| F-P7R1-02 excluded refusal replay | C | `task13b11p-r1/FOLLOWUPS.md` row 02: deliberate v1 exclusion |
| F-P7R1-03 coarse stop reasons | C | same file row 03: diagnostic granularity, closed enum |
| Browser D-01 | C | `task13b11o/CAPABILITY_PROJECTION.md`; current policy preserved pending optional policy review |
| FUTURE-AGENT-BRIDGE | C | `task13b11p-r2/DEFERRED.md` §FUTURE-AGENT-BRIDGE |
| Cross-recorded-turn idempotency, duplicate-result detection, recorded/evaluated timestamp ordering | C | `task13b11p-r2/DEFERRED.md` paragraph 4; recorded v1 scope |
| TIMEOUT confirmation settlement/provenance source; D-P6-01/D-P6-02 policy reinterpretation; destructive/financial/messaging policy | C | `task13b11p-r2/DEFERRED.md`; existing mappings retained |
| Vulnerability/type/lint/coverage tooling, resource budget, digest convention, stale comments | C | `task13b11o-r1/FOLLOWUPS.md` §Later hardening |

Resolved history is not relisted as open: P7-D01–D04 (`task13b11o-r1/FOLLOWUPS.md` opening), P-B01–P-B06 and F-TYPE-01 (`task13b11p-r8/FOLLOWUPS.md`, `FINAL-REPORT.md`). Historical `tasks/FOLLOWUP-QUEUE.md` headings predate those resolutions.
