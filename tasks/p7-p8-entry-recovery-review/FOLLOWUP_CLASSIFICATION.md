# Current follow-up classification

Primary buckets: **A** blocks formal P7 exit; **B** blocks P8 entry distinctly; **C** blocks later live execution/user-response wiring only; **D** deferred/nonblocking; **E** operator decision required before a specified extension. A formal-P7 item also transitively blocks P8, but appears only in A. The phase gate itself is the B item. Sources are the frozen `task13b11o-r1/FOLLOWUPS.md`, `task13b11p-r1/FOLLOWUPS.md`, R8 `DEFERRED.md`, and `task13b11o/FOLLOWUPS.md` unless noted.

| Item | Bucket | Evidence and boundary |
|---|---|---|
| Remaining server/API/UI shadow consumer, CT-001/013, measured window and rollback drill | A | 13B11A phase row, graph, EC-10; absent at production HEAD |
| F-MAP-01 / LIVE-02 | A | Real traffic needs JARVIS-owned request→binding and capability projection; `task13b11o-r1/FOLLOWUPS.md` says static comparison alone does not supply a live producer |
| F-FALLBACK-01 | A | Its failed-turn **audit** path needs settlement for the §7 audit-only shadow; user-visible rendering is needed only before control-plane responses. Non-renderable passive PipelineStop stays valid |
| F-AUDIT-01 / LIVE-04 | A | §7 shadow writes results to audit; conversational `turn.summary` obligation-nullability and writer/failure contract are open (`SCHEMA_V3_FOLLOWUP.md`) |
| LIVE-01 model wire, identity and shadow window; resource ownership where shared model is used | A | `task13b11o/FOLLOWUPS.md` LIVE-01 and 13B11A integration plan §§7,11; passive fixtures do not meet measured shadow |
| Formal P7 exit | B | 13B11A P8 entry cell says “P7 exit”; no separately named P8 blocker before P8 work |
| F-P7R1-01 | C | Exact result type/linkage is enough for recorded fixtures; independent dispatcher origin needed before live result consumer; `task13b11p-r1/FOLLOWUPS.md` row 01 |
| F-REPLAY-01 | C | Lost result after actual executor entry/cancellation; inert shadow cannot enter executor; `task13b11o-r1/FOLLOWUPS.md` row F-REPLAY-01 |
| Real registry/P5 invocation boundary and confirmation UX/TTL for mutations | C | Inert P7 shadow and P8 do not execute; original later P9/P10 gates remain |
| F-P7R1-02 | D | Non-dispatchable refusal replay deliberately excluded by frozen v1; no widening |
| F-P7R1-03 | D | Coarse reasons affect diagnostics; no enum expansion needed for phase entry |
| Browser D-01; D-P6-01/02 policy reinterpretation | D | Current signed browser and obligation outcomes retained; policy change is a separate operator task |
| FUTURE-AGENT-BRIDGE | D | `task13b11p-r2/DEFERRED.md`; external agent is outside P7/P8 |
| Cross-recorded-turn idempotency, duplicate-result detection, timestamp ordering; TIMEOUT settlement/provenance; redaction key list; tooling/digest/comment hardening | D | `task13b11p-r2/DEFERRED.md`, `task13b11o-r1/FOLLOWUPS.md` later-hardening section; no automatic retry |
| Shadow model/provider choice, numeric window and acceptance thresholds | E | LIVE-01 and 13B11A P7 “measured period” leave these unfrozen; decide before live shadow, not by this review |
| Pre-P7 recorded-only conformance graph exception | E | No such amendment found; only required if operator elects to change the existing order |

Resolved items P-B01–P-B06 and F-TYPE-01 are closed by R8 history and excluded from this open list. The classifications do not authorize implementation, schema or policy changes.
