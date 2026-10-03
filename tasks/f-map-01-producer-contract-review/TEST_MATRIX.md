# Future test matrix — pre-implementation draft

These tests must be frozen with concrete expected tool/argument maps **after** the missing schema is approved and before implementation. Recorded fixtures and inert doubles only; no live model, registry or tool. Cases testing P7 use its current stage/reason vocabulary. An ingress rejection is distinguished from a P7 stop.

| ID | Scenario | Required assertion |
|---|---|---|
| M01 | valid conversational request, route NONE | no executable expected/query; no dispatch; conversational or P6 outcome per existing lane |
| M02 | valid operational supported request | one JARVIS expected/query pair, P3 version, current P4 pairing; no authority grant |
| M03 | unsupported action | no synthetic capability; existing early refusal/unavailable outcome |
| M04 | ambiguous/multi route | no selected executable binding or proposal selection |
| M05 | ambiguous/unresolved target | no invented target/argument field; early P6 result |
| M06 | canonicalizer rejects JARVIS raw args | no repaired expected result; existing canonicalization failure |
| M07 | required binder missing | no executable projection; S06 projection_missing if actionable proposal arrives |
| M08 | one exact matching proposal | S06 passes; P4 still decides; zero dispatch |
| M09 | wrong tool or full-map mismatch/extra key | exact S06 mismatch; no key dropping or fuzzy match |
| M10 | zero proposals for executable route | S06 proposal_required |
| M11 | multiple proposals | S06 multiple_proposals; no ranking/merge |
| M12 | fake model expected binding/tool schema | cannot replace JARVIS expected side |
| M13 | fake client permission/approval/confirmed flag | stripped at ingress; P4 decision and P4 settled state only |
| M14 | wrong session/turn/proposal/model IDs | ingress/S01/S06 association refusal; no ID replacement |
| M15 | replay-associated request/result | mode C only with P5 pair, matching versions/IDs; no re-execution |
| M16 | route NONE with recorded refusal/result | preserve frozen Option A/C-00a exclusion; no replay widening |
| M17 | current browser.open policy row | preserve signed outcome; no browser D-01 reinterpretation |
| M18 | same immutable inputs repeated | byte/equality-stable projection; zero clock/random/provider/registry dependence |
| M19 | absent/untrusted live capability inventory | no default-vocabulary grant |
| M20 | target-bearing argument altered by client/model | full binding mismatch; no repair |
| M21 | confirmation continuation | only P4 settled V2 projection, no ConfirmationRecord import or claim |

The frozen P7 116-case and unseen 53-case corpora remain unchanged. This is an acceptance matrix proposal for a **later** approved binder contract; it is not a scored test result and cannot close F-MAP-01 while M02's exact mapping is undefined.
