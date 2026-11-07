# Security review and verified disposition

The completed comprehensive Cloudflare audit is preserved read-only. Its final
390-file snapshot predates some Sprint 6 and release-candidate edits. The audit's
zero-confirmed-vulnerability verdict is not silently extended to later source;
CLOUDFLARE-AUDIT-REVIEW.json records its exact outputs and the release's separate
delta review is pinned in INDEPENDENT-REVIEW.json.

| Item | Accurate prior status | Current evidence/disposition |
|---|---|---|
| Anonymous loopback authority | Conditional source-grounded lead; no established deployed anonymous listener or excluded reachable UID/browser | Baseline admitted read/cancel reproduced from original router source; candidate main and embedded routes deny blank/missing/wrong/malformed credentials, including readiness; valid identity preserves receipts/replay |
| Filesystem ancestor replacement | Exact same-UID switch chain rejected by SQLite; other-UID replacement authority unestablished | Original harness rerun and refused; ancestor owner/mode and identity checks, no-follow component creation, pre-mutation rejection, symlink-insertion race and same-leaf parent replacement tests pass; not hostile-root/UID or atomic-VFS qualification |
| D7 UE5 binary cleanup | Current reproduced reliability defect in audit's packaged snapshot | Text/byte/size validation and finally cleanup pass; concurrent authored UE5 regression source retained; primary extends pending/active and send/close bounds |
| D1 confirmation after stop / D2 narration redispatch | Earlier reproduced defects, closed/gated in Sprint 6 | Confirmation absent; registry/getters/chat/vision refuse effects before dispatch; current safety, tracing, pipeline and full-app regressions pass |
| D3 heuristic termination / D6 CLI false fallback | Earlier reproduced defects, closed/gated in Sprint 6 | Native-child PID identity leases and no CLI local fallback retained; current independent native-child/API regressions pass |
| D4 continuous VAD / D5 WebSocket cleanup | Earlier reproduced defects, closed/gated in Sprint 6 | Bounded/cancellable synthetic input coverage and all-exit WebSocket regressions pass; nine hardware/desktop cases explicitly excluded |
| Dormant screenshot temporary path | Rejected as a currently reachable application vulnerability | Real dispatch remains closed; dormant capture storage is not claimed hardened and must be reviewed before future exposure |
| Post-cutoff CLI/resource/auth/default changes | Comprehensive audit explicitly did not review later bytes | Retained Sprint 6 pins cover unchanged CLI/resource boundary; release delta covers auth, ancestry, sockets and defaults/context with exact final pins |

Independent delta review found additional real defects during this sprint: timeout
removal of still-live peers could defeat the cap; direct sends/closes were unbounded;
main connect/audit preceded cleanup; UTF8 allocation preceded character bound;
private-directory mkdir occurred before ancestor validation; and exempt embedded
readiness exposed non-aggregate identifiers. Those findings were fixed, statically
re-reviewed and exercised through failure tests. These were engineering findings,
not retroactively assigned Cloudflare vulnerability verdicts or severity claims.

The final source review PASS applies to the stated offline trusted-local scope.
The reviewer ran no tests. Runtime results are independently retained by the primary
engineer. Package/default/context review and the final whitespace-only repin are
explicitly recorded; no source identity is inferred merely from a version label.

External assumptions remain: trusted root/process UID and supported local storage;
protected key/token/witness/checkpoint/time custody; single-worker upstream frame
limits; a documented shared-bearer caller policy; and current installed dependency/
identity/permission verification. Authentication is not per-principal authorization.
The real app's admission/error middleware is part of its tested boundary; another
embedding must retain equivalent body limits and redaction, not just mount routes.
No two-UID/browser/TLS/physical-storage/production exploit or live defense test was
performed. The first-live proposal requires those relevant facts without creating
credentials, broadening permissions or enabling a real application adapter here.
