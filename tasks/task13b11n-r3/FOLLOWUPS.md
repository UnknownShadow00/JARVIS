# Follow-ups
See ../FOLLOWUP-QUEUE.md for consolidated ordering. Items here identify the current dependency blockers.

| ID | Exact question / current behavior | Options / recommendation | Security consequence | Blocks |
|---|---|---|---|---|
| P7-PIPELINE-01 | What exact passive input and TurnOutcome schema is frozen? Neither exists in production. | Dedicated contract task before implementation (recommended), or postpone to full P7 design | Prevents ambiguous state becoming approved output | Pipeline |
| P7-GUARD-01 | How do existing action/capability maps bind proposal tool/args and permission evidence? P0 proposal grants nothing. | Freeze explicit existing-map composition; never infer new live capabilities | Prevents mismatched proposal authorization | Pipeline |
| P7-PROJECTION-01 | Who assembles snapshot, lane, constraints, confirmation and result projections? Current modules consume separate settled inputs. | One reviewed projection per stage; no model-supplied control state | Prevents forged satisfied constraints/trust | Pipeline |
| P7-LANE-01 | When is final lane decided given proposal/result signals after initial routing? | Freeze conservative stage order under existing lane policy; no downgrade | Prevents operational prose exposure | Pipeline |
| P7-FAILURE-01 | Which exact typed outcome represents malformed model/stage/build failures? Only conceptual failure rules exist. | Freeze failure matrix and representation before scoring | Prevents fallback fabricating success/approval | Pipeline |
| P7-AUDIT-01 | How is existing ModelDraftAuditRef composed into final events? Current reference exists; mapping absent. | Reuse safe reference; no whole provider payload; separate emission | Prevents reasoning/private-data retention and audit gaps | Pipeline audit |
| P7-LIVE-01 | What actual provider normalizer and shadow window are authorized? Only canonical recordings implemented. | Separate reviewed live integration with operator present | Live model/wiring/resource boundary | Live P7 |
| P7-DOC-01 | Correct stale future-phase/no-import comments? Current runtime behavior is accurate, comments lag. | Later scoped docs/comments update, not changes for busyness | Audit clarity only | No |
| P7-REASONING-01 | How do P1/P7 reasoning-name policies meet at future audit projection? P7 is stricter. | Exclude reasoning at source and freeze mapping; no casual P1 policy edit | Prevents private reasoning retention | Before pipeline audit/live |

Preserve all prior deferred items; the draft documents confer no new permissions or live authorization.
