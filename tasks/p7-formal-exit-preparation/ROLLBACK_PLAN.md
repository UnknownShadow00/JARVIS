# Future shadow rollback plan — not executed

Authority: 13B11A FEATURE_FLAG_AND_ROLLBACK §3, PRODUCTION_ENTRY_ROADMAP EC-10, RISK_REGISTER R-18. No deployment command is invented. No activation, configuration, service or nightly-snapshot change occurs now.

| Step | Future action | Required proof |
|---|---|---|
| Detect and stop admission | on shadow side effect, visible contamination, failed seal or wrong runtime authority, cease new shadow admission | exact incident boundary and untouched legacy behavior recorded |
| Disable mode/feature | use canonical plan's execution.mode=legacy; keep hermes_brain=false and hermes_enabled=false for disabled configuration | request path no longer enters context/evaluator; both REST and WS remain legacy |
| Quiesce scheduled work | apply the approved scheduler's shutdown/cancel/drain rule | no late evaluator writes or model/resource use; scheduler decision must specify this first |
| Revert consumers if needed | revert the separately identified future server/API/UI consumer commits per canonical additive rollback level 3 | no legacy source loss; contract/evidence preserved; exact commit list only once implementation exists |
| Context state | stop creating new sessions/turns; detach shadow-owned in-memory stores; use P2 drop/clear only under approved lifecycle | no global/cross-session data loss; legacy reads no shadow ledger; handles invalidated/rejected by chosen protocol |
| Measurement records | retain sealed evidence and incident records; disable new writes with approved writer shutdown | historical seals remain valid; no rollback deletion of evidence |
| Non-evidence transient buffers | drain/discard only according to approved lifecycle/retention contract | explicit accounted loss; no silent record removal or guessed retention TTL |
| Restore legacy proof | verify flags, production commit/status, regression/golden and critical file digests; safe probe only if guaranteed no provider/tool call | both transports unaffected; known golden eight unchanged; no model activation needed |
| No external cleanup claim | inspect independent shadow call guards/counters and accepted observation scope | zero shadow external execution means no shadow external mutation to undo; result.executed=False alone is insufficient |

The canonical plan states rollback never deletes evidence, contract artifacts, provenance logs or models. Therefore measurement-log removal is not part of rollback; any later retention/removal policy needs separate authority and must preserve sealed evidence. New shadow must not create confirmation state, so no cleanup of shadow-created approvals is expected. Do not confuse existing legacy side effects during ordinary future traffic with shadow side effects; rollback disables shadow, not unrelated historic legacy work.

Current mode is already legacy and no context/ingress/evaluator exists. No drill is claimed. A future drill must prove disabling mode and reverting consumers independently, including pending WS streams and deferred work. Resource/model ownership and scheduler teardown are prerequisites to exact operational commands, so none are fabricated here.
