# Independent release delta security review

Reviewer `/root/sprint6_security_review` performed an independent read-only static
review in the detached release worktree. No tests, source, configuration, runtime
state, packets or logs were executed or modified by that reviewer. The six exact
source pins are in INDEPENDENT-REVIEW.json. Verdict: PASS, with no remaining
critical/high/medium defect in the reviewed delta.

The review found and drove fixes for live-but-untracked WebSocket peers after send
failure, unbounded direct sends/closes, main connection/audit cleanup, UTF8 size
allocation, unchecked directory creation before ancestor validation, and the
embedded anonymous detailed readiness response. Runtime regressions are the primary
engineer's separately captured evidence; they are not attributed to the reviewer.

All authority routes now require a configured bearer. Directory creation walks
retained validated parents with no-follow component opens and mkdirat; Authority
and LedgerGuard retain ancestry identities. Both WebSocket interfaces bound input,
connections, pending accepts, sends and closes; failed live peers retain their
admission count until handler exit. Connect/audit and cancellation have all-exit
registration cleanup.

Limits: root/same-UID compromise is excluded, and this is not an atomic SQLite VFS.
Protected key/token/witness/time custody and supported local storage semantics remain
external responsibilities. Shared bearer identity is not per-principal authorization.
WebSocket caps are per-process; upstream frame limits and one-worker deployment are
prerequisites. Broadcast time can reach peer count times the timeout. Authenticated
readiness probes must supply the credential. No production, live adapter, TLS,
network-filesystem or infrastructure security claim follows from this review.

A final static delta review also verified disabled ResourceModeConfig defaults,
matching public example defaults, and .dockerignore exclusions. Explicit legacy
configuration values remain unchanged. These context exclusions do not replace the
candidate archive's independent public-source allowlist. Three additional exact
source pins are included in the JSON. No runtime tests were run by the reviewer.
