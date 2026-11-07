# Independent comprehensive audit crosswalk

The separate Cloudflare audit was read without editing its snapshots, runners,
evidence or findings. SEPARATE-AUDIT-OBSERVATION.json records exact observed hashes
and finding/metadata bytes. Its metadata still said in_progress; later changes
belong to that audit. The observation contains no confirmed vulnerability, one
rejected screenshot reachability claim, and one conditional anonymous-loopback
needs_validation lead. Earlier draft judgments are not presented as final findings.

| Independently reproduced implementation defect | Reviewed application correction | Current regression evidence |
|---|---|---|
| D1 confirmation executes after emergency stop | /confirm removed; ToolRegistry and compatibility getters always refuse real execution | test_approval_gates, test_safety_levels, integrated closure checks |
| D2 narration fallback repeats effect | both stream and normal tool/vision dispatch are inert before narration | integrated stream/normal and registry closure checks |
| D3 heuristic termination targets unrelated same-UID child | only captured native-child identity leases can terminate; CLI never falls back to local host control | native unrelated/owned/stale child cases in test_audit_integration_fixes |
| D4 continuous VAD lacks bounded recording | absolute deadline, frame cap, cancellation and bounded callback queues | synthetic stream tests, no audio hardware imports |
| D5 malformed WebSocket leaves manager entries | input type/size checks and finally disconnect | native TestClient WebSocket cleanup/close cases |
| D6 CLI missing bearer and false offline fallback | bearer attached; denied/timeout/disconnected responses fail; --offline cannot mutate host | HTTP/CLI failure and alias-guard regressions |

These closures intentionally remove unsafe legacy capabilities. They do not claim
that those capabilities have gained live authorization. The current synthetic
execution path remains the only supported effect boundary.

The screenshot helper's temporary storage was not hardened here: it is unreachable
through current supported application dispatch, and the audit rejected it as a
current application vulnerability. Any future authorized capture adapter must
review private exclusive file creation and real installed writer behavior.

The ordinary blank-token loopback task API remains a documented conditional trust
assumption. Stock startup refuses missing authority admission; tests with explicit
synthetic binding are not a deployed listener or cross-UID/browser exploit. A
nonempty API token and explicit principal/ingress policy are required before the
proposed live stage. Transport submissions, diagnostics and stop already require
credentials; host mutation routes are closed. No anonymous deployment was activated
or probed, and no confirmed audit issue was dismissed as a vulnerability without
independent confirmation.
