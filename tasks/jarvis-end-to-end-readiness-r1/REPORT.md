# JARVIS V2 Sprint 6 — verified offline application integration

Result: PASS for the authorized offline milestone. Real execution remains disabled.
The actual application now combines authority enrollment, queue admission, scheduler
occurrences, synthetic execution, durable receipts, protected witnesses, recovery
decisions and archive verification. It does not qualify production or live execution.

## Implemented application changes

The disabled-by-default `SyntheticTransport` uses bounded authenticated AF_UNIX
socketpair messages for exactly echo and SHA-256 endpoints. Independent synthetic
operator authorization binds the original UUID, scope, store, checkpoint, goal,
exact capability/payload and validity. Request/response HMAC keys are distinct from
operator and ledger keys. Kernel peer identity, framing, schemas and exact pure
results are verified. There is no real tool, URL or arbitrary adapter transport.

Reservations, reports, execution evidence and terminal publication all use the one
fenced Authority SQLite writer. The endpoint durably reserves before computing.
Readiness reauthenticates historical grants, reports and completion evidence and
refuses wrong keys, missing witnesses, inconsistent receipts or stale ownership.
Queued expiry reaches a durable non-dispatch terminal state. Late computation
cannot poison history with a post-deadline report. Transport grant history has an
explicit lifetime cap of 128; prior history is never pruned.

A lost response with a committed report stays UNKNOWN. Offline operator CLI
reconciliation first authenticates the original report and records evidence;
a separately authorized action publishes it. A restart between actions preserves
the publication hold. Pre-open checkpoint binding, final permit expiry checks,
exact receipt replay and closed writer ownership prevent accidental retries.
A report is not a completion receipt. No public approval/completion/activation route
was added. Imported/approved branch proposals still cannot activate recovered work.

Legacy execution paths were closed: real registry calls/getters, tool and vision
chat/stream processing, confirmation dispatch, and clipboard/type dictation.
Host resource mutation HTTP routes refuse even authenticated requests. CLI failures
and --offline never start or terminate local processes. Native termination is
limited to positively captured child identity leases. WebSocket validation/cleanup
and bounded cancellable VAD/wake queues address independently reproduced audit
defects. These are deliberate compatibility changes, documented in
[the operator/client contract](../../docs/end_to_end_readiness.md).

## Actual end-to-end demonstration

[INTEGRATED-DEMONSTRATION.json](INTEGRATED-DEMONSTRATION.json) records one integrated
history, not unrelated substitute databases stitched into a success claim:

1. Real application lifespan admits an enrolled witnessed Authority and bound
   recovery registry, queue, scheduler and worker. ASGI requests use the configured
   disposable bearer. No network listener or production startup is used.
2. A held request is cancelled. An independently authorized execution submission
   traverses the actual API, signed socketpair endpoint, reservation/report,
   evidence and terminal receipts. An identical submission replays its receipt.
3. A scheduled pure SHA-256 occurrence uses actual APScheduler registration and
   explicit invocation of its original nominal callback; its UUID survives a
   duplicate callback. This is not wall-clock/cron timing qualification.
4. The actual recovery service renews the protected witness against current
   ancestry. A later response loss leaves a durable signed report and UNKNOWN.
5. Lifespan shutdown releases the writer. The actual FD-only operator CLI records
   authenticated evidence, replays the same UUID, and exits. A real app restart
   between actions keeps UNKNOWN without endpoint dispatch. A separate permit
   publishes; another real lifespan sees the terminal receipt with zero redispatch.
6. An archive of that integrated history is verified and restored inert. A durable
   branch proposal and authenticated approval retain original request/occurrence
   IDs. Opening the restored branch as active Authority is refused.
7. Closed legacy paths, input redaction and duplicate JSON rejection are exercised.
   Disposable key material is checked absent from public demonstration and logs.

The full-app mode has 20 scenario groups (including earlier enrollment/recovery
scenarios rerun on current source) and three native dependency probes. These are
separate from the pytest count below.

## Current source-bound verification

All final runs share the exact current 101 application Python file hashes and the
same runner hash. Inputs/helpers/test copies have per-run manifests. Earlier
failed/intermediate runs are retained and excluded from final totals.

| Final mode | Pytest passed | Wall seconds | Run |
|---|---:|---:|---|
| focused | 60 | 31.80 | `20261106T071510730181Z` |
| full-app | 103 | 25.17 | `20261106T071700785833Z` |
| core | 254 | 90.14 | `20261106T071726054819Z` |
| enrollment | 59 | 16.76 | `20261106T071856293416Z` |
| recovery | 72 | 68.76 | `20261106T071913158481Z` |

Total: **548 distinct pytest cases passed**, zero failed/skipped in final modes.
[RESULTS.json](RESULTS.json) contains exact run/input/runner bindings and measured
resource use. This is a selected broader regression closure, not the complete
repository/hardware/model/frontend suite. No historical result is counted as new.

[CRASH-RECOVERY.json](CRASH-RECOVERY.json) contains **15 new independent-process
SIGKILL cases**, including before/after SQLite commit, claim, endpoint reservation,
computation, report, evidence and publication. Competing writers are refused;
restart makes zero new endpoint invocations. Missing record evidence stays UNKNOWN;
valid already-recorded normal evidence may publish without redispatch. The explicit
operator-created recovery evidence has the additional separate-publication hold.
The recovery mode also reran the prior proposal/decision/witness crash cases against
current source; those are not presented as newly designed Sprint 6 crash tests.
Disk-full injection, stale owners, replay, forgery, wrong keys, missing anchors,
rollback/corruption, concurrency, deadline/cancellation and incomplete histories
are exercised in the focused and broader suites. SIGKILL is not physical power-loss
qualification. Exact stage observations and original UUID/payload hashes are retained.

The initial focused failure exposed an incorrect witness-loss expectation and
cleanup behavior; a later 15-case crash failure exposed a constructor cleanup
exception masking owner_busy. Tests and product cleanup were corrected and final
affected suites rerun. Review additionally found and corrected report-only recovery,
late report expiry, wrong-key historical readiness, auto-publication of recovered
evidence, queued expiry and unsafe legacy fallback paths. Nothing was hidden by
replacing old run output.

## Performance, review and preservation

The benchmark mode passed **13 bounded cases**, including three new 1/4/8-task
signed-IPC application cases and ten prior benchmark shapes rerun on current source.
[PERFORMANCE.md](PERFORMANCE.md) gives measurements and scale limitations.
Maximum observed final aggregate descendant RSS was about 116.2 MiB; the 254-case
core run took 90.14 seconds. Every run stayed within the unchanged guard limits.
Heavy runs were sequential and deferred when the independent audit payload was
observed. The audit's running snapshot/evidence was never modified or interrupted.

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records the separate read-only static
security review, its exact source pins and limits. The reviewer did not run tests.
[AUDIT-CROSSWALK.md](AUDIT-CROSSWALK.md) maps the separate comprehensive audit's six
reproduced implementation defects to reviewed fixes. Its point-in-time observation
contains no confirmed vulnerability, one rejected dormant screenshot trace and one
conditional loopback-auth lead; metadata was still in_progress. No final audit
completion claim is made here.

[EVIDENCE-VERIFICATION.json](EVIDENCE-VERIFICATION.json) verifies all **91,076 prior
packet files**, including the current broker successor, unchanged and preserves the
original canonical log prefix. SOURCE.patch and source/ contain actual changes
relative to the captured Sprint 6 baseline. SOURCE-SHA256.json, run manifests,
SYMLINKS.json and SHA256SUMS bind source, helper and packet bytes. No sealed prior
packet or audit snapshot was rewritten. Completion is appended to the project
canonical log, not a home-directory log.

## Remaining blockers and next milestone

The offline milestone is verified. Live execution is blocked by the absence of a
reviewed real adapter, independent OS/signing custody, live identity/configuration
qualification and physical storage durability evidence. Same-process HMAC socketpair
fixtures are not a hostile-principal boundary or public-key nonrepudiation. Trusted
external witness/time/key custody remains required. History verification is a full
scan and lifetime-capped at 128 grants; an authenticated archival ceremony and
larger protected performance characterization are future work. Child leases are
RAM-only. Host-control commands are unavailable pending an independent durable
control workflow. Ordinary anonymous loopback held-task mode retains a conditional
local trust assumption; require a bearer and explicit principal policy before live
use. Optional audio/desktop/model/provider/frontend/device suites were not run;
updated dictation no-effect behavior is covered by focused boundary regressions,
not the complete optional audio suite. Dependency advisories were not re-audited;
no dependencies were changed or installed and no commit/push was performed.

The exact prerequisites for the **first separately authorized live read-only stage**
are enumerated in [docs/end_to_end_readiness.md](../../docs/end_to_end_readiness.md#first-authorized-live-read-only-stage--prerequisites-not-authorization).
The current Proxmox broker/worker was read as a contract/reference only; it remains
unconnected, its independent preissuance/acceptance order and Gate 6K protections
unchanged. No production startup, provider call, real database migration, credential
rotation, infrastructure/VM change, restored activation or V3 deployment occurred.

Recommended next offline milestone: durable externally held adapter authorization
and service ownership, with two-principal synthetic qualification and bounded
history verification/archival design, before proposing a live read-only adapter.
