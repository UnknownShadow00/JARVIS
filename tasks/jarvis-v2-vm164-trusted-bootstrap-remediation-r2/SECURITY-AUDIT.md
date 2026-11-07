# Offline security review of the r2 remediation candidate

This is a source and adversarial-test review in the same engineering session,
not an independent external audit or installed-platform qualification. No network,
Proxmox connection, VM operation, guest command, credential read/change, system
manager invocation or JARVIS installation/start occurred. Native xorriso was used
only as the previously pinned unprivileged offline image builder, inside its
no-network bwrap command. All fixture manager/TTY/process operations were mocked.

## Review inputs and integrity

Read the four requested locations. The requested predecessor SECURITY-AUDIT.md
was absent; its actual REPORT, FINDINGS, FAILURE-ANALYSIS, OPERATOR-HANDOFF,
validator, hazard tests and pinned bootstrap procedure/helper were reviewed.
Missing source is recorded in evidence/ENTRY.json, not invented or backfilled.
The user's newer stopped/order=scsi0/attached-r4 report supersedes the older
unconfirmed-correction narrative, as operator-reported evidence only.

At entry, recorded143 predecessor regular-file hashes and5 symlink targets across
both bootstrap/audit packets, plus the append-only canonical log prefix. Local
verification rechecks these bytes/links, the original104-file/5-link bootstrap
manifest/seal, old r4 ISO hash and audit SHA256SUMS; no /home-wide delegated
verification is needed. No original candidate/evidence/procedure was patched.
The unchanged lab probe's08eae2... pin is verified by builder and member reader.
No third-party dependency was added, downloaded or installed; no fresh advisory
lookup was attempted under the explicit no-network boundary.

## Hazard-by-hazard findings

**H1:** r2 does not depend on actual live ejection, so no hotplug behavior is
asserted. The conservative parser is loaded from its pinned repository source
and specialized in memory for the new ISO and stop-before-detach edges. Old code
remains unchanged. The unchanged probe reports true optical presence. New decoder
requires true for this diagnostic and always denies installation qualification.
A new test invokes the original installer target predicate and confirms that
attached media is still rejected. This is a narrowed diagnostic contract, not an
optical-absence waiver or full r1 success declaration.

**H2:** a cooperative guest timer cannot fence root that precedes it or can disable
it. The selected design requires independently owned, prearmed host enforcement
outside guest/cleanup/console authority. lease_policy.py implements immutable
clock/target/deadline/admission predicates and replay only; it has no transport or
runtime execution adapter, and every receipt denies root_boot_go/authority. Its
synthetic qualified=true inputs are deliberately not live evidence. Actual host
backend/version/custody/deadline/termination behavior remains an OPEN high-severity
blocker; a model PASS must never substitute for it. No claim of automatic real
expiry is made. A reliable forced cutoff also requires an explicit crash-risk/
preservation decision, beyond the old graceful-only scope.

**H3:** reviewed the candidate's complete close path, not only its happy branch.
Narrow target identity is independent of SESSION.json and checked before any
target-sensitive mutation. Failed/unknown identity invokes nothing else in the
guest. Once identity is verified, the outer finally covers validation failures;
the nested finally covers cleanup/inspection/receipt failures and attempts
poweroff. Each command phase catches errors, timeout, soft interruption and bad
receipts, recording INCOMPLETE rather than pass. No pre-try broad snapshot or
probe-exists requirement remains. Direct internal inspect also checks identity
before its manager read. A failed submission still leaves the required host fence.
SIGKILL/OOM/default SIGTERM/manager/kernel death remain outside Python guarantees;
only real independent host enforcement can cover those cases.

**H4:** eight bounded phases compose to48 seconds of nominal command/reap waits,
global budget60 with6 reserved for poweroff, manager90/stop5. No sleep and no retry
loop consumes the envelope. Runner launches a new child process group, kills all
of it on timeout/interruption, attempts one bounded reap and proceeds. It never
starts an unknown action. Normal budget exhaustion cannot use the poweroff
reserve; total exhaustion remains incomplete. Popen/kernel scheduling, unit
properties and manager teardown are not empirically bounded here; modeled host
escalation at600 seconds and required stop observation by630 are acceptance
criteria, not a proven cutoff. The actual stop readback alone proves that state.

## Negative coverage and practical limits

The87 new methods cover per-step failure/timeout, missing/corrupt/stale state,
snapshot-validation error, wrong/malformed identity, KeyboardInterrupt/SystemExit,
invalid inspect/validation receipts, residual children, receipt hangup, failed
poweroff, exhausted budgets, process-group cleanup/reap failure, killed-guest-worker
model, duplicate/late boot, inactive/unqualified/guest-owned fence, authority loss,
clock rollback/suspend jump/host reboot, target/config drift, lease immutability,
strict pending/old-media/state-edge rejection, unchanged installer refusal,
readonly/hash/tty/RAM handoff controls, exclusive evidence and capture tamper/loss.

Process death and suspend tests are explicitly **models**, not real signals/host
suspend qualification. All actual guest command/process calls are mocked. The
native ISO reader proves structure/member bytes, not the actual host upload or
kernel mount. Source hashes, fixtures and stdout can be fabricated by the local
owner; they are not credentials, signatures, origin authentication or WORM.
The parser's source/freshness assertions do not turn offline JSON into live fact.

The final combined run really executes171 test methods:87 new,43 original bootstrap,
32 original validator,9 legacy-hazard reproductions; zero failures/errors/skips.
Those last9 pass by confirming defects remain in the preserved old code. They do
not claim that old code is safe. Six additional local CLI fixtures return expected
codes with root_boot_go=false; they are not added to171. Earlier75-method run had
one failure/four errors from fixture mountinfo escaping and missing path decoding;
corrected fixture/kernel-escape handling, reran and retained all logs.

New helper writes only exclusive /run files and runtime mask/unit state. It does
not export shadow/credential contents, edit accounts/GRUB/network/SSH, activate
real executors or implement providers/management transport. It does not claim
universal non-persistence, block ancestry/multi-UID containment or native-runtime
compatibility. Normal OS activity and forced shutdown can change disk state.
All such installation/qualification assumptions remain separate blockers.

## Conclusion

Offline preparation passes; actual root-session readiness is **NO-GO**. H1 is
avoided in the revised diagnostic path, H3/H4 software paths are strengthened and
regression-tested, but their physical guarantees depend on the still-missing H2
host backend and supervised qualification. No unresolved high-severity deployment
assumption is converted into PASS. See RISK-REGISTER.md and GO-NO-GO.md.
