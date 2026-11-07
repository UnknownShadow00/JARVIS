# JARVIS V2 — verified offline release candidate

**PASS for controlled offline security testing. Real execution remains disabled.**
This is a release-candidate preparation result, not production deployment or live
VM qualification. No production startup, real provider/model/executor activation,
Proxmox/VM modification, credentials/permission grant, real database migration,
privileged Gate 6K qualification or V3 deployment occurred.

Candidate: **jarvis-v2-offline-rc1-ab2d17fb7c522ef9**. The immutable, source-only
[archive](release/jarvis-v2-offline-rc1-ab2d17fb7c522ef9.tar.gz) is 382890 bytes and
has SHA-256 `edddc545b30ad78c801ea9e482666e0d6c91a041475b91fa4b9c98abae69e138`.
[release/BUILD.json](release/BUILD.json) binds all 306 public source files,
the exact 31-package offline application/test lock and retained artifact provenance.
A second deterministic rebuild produced identical bytes. Existing publication is
refused; the archive and release metadata are read-only. Hashes require independent
external retention; same-UID filesystem control is not WORM or public-key signing.

## Implemented security and integration fixes

- **Anonymous authority access retired.** Every authority router route, including
  reads, cancellation, schedules, receipts, execution status and detailed /ready,
  requires a nonempty configured matching bearer in both the main app and embedded
  router. A blank token grants no task authority. /health remains liveness only.
- **Protected ancestry checked before creation.** Component-relative no-follow
  directory opens validate owner/write permissions; mkdirat creates only beneath
  retained validated parents. Authority and LedgerGuard retain ancestor identities
  and fence replacement, including moving original leaf inodes under a new parent.
- **WebSocket all-exit protection.** Main and UE5 handlers validate binary/text and
  8 KiB size bounds, bound pending/active connections and every send/close, and
  clean registrations on audit failure, cancellation and disconnect. Failed live
  broadcast peers remain counted until their handlers exit. Independent review
  found and closed the earlier cap-bypass and unbounded-send paths.
- **Safe class and example defaults.** Automatic resource control and transitions
  require explicit opt-in even for partial resource_mode dictionaries. The public
  example uses dry-run and disables boot, dictation and trace retention. Existing
  explicit real configuration is not read, changed or migrated. Docker contexts
  exclude known credentials, runtime configuration, state and evidence.
- **Current regression contracts.** Retired standalone JSON writers, public
  completion, ScheduledJob objects, confirmation dispatch and real-tool narration
  assumptions were replaced with actual durable-authority/no-effect tests. Positive
  API fixtures supply explicit disposable credentials and admission. Original test
  sources and every unsuccessful run remain available for comparison.

There are 41 changed/added source/test/doc/default files relative to the
captured actual Sprint 6 baseline; see [CHANGES.json](CHANGES.json), [SOURCE.patch](SOURCE.patch)
and [source/](source/). This is not a misleading patch against the older Git HEAD.
The exact code is in the detached `JARVIS-release-r1` worktree and sealed source
archive. Concurrent shared-workspace changes were preserved for review in
[SHARED-WORKSPACE.json](SHARED-WORKSPACE.json) and CONCURRENT-CHANGES.patch. The final
candidate was **not promoted over active shared writers**. No mixed shared checkout
is claimed to have these final hashes or results. Initial pre-isolation scaffolding
and independent concurrent edits remain in the shared checkout.

## Current broad regression results

All ten selected final modes bind the same **102 application Python source hashes**
and runner. Inputs/test copies are separately hash-bound. No earlier passing suite
or intermediate failure is counted as a new final success.

| Final mode | Cases | Wall seconds | Run |
|---|---:|---:|---|
| core | 254 | 97.61 | `20261106T083415986410Z` |
| broad-collect | inventory 927 | 1.56 | `20261106T083553698796Z` |
| broad-safe | 503 | 29.02 | `20261106T083555422640Z` |
| broad-legacy | 17 | 2.95 | `20261106T083624601792Z` |
| broad-security | 33 | 5.82 | `20261106T083627704180Z` |
| focused | 60 | 35.00 | `20261106T083633678036Z` |
| full-app | 103 | 25.63 | `20261106T083708780859Z` |
| enrollment | 59 | 17.86 | `20261106T083734515555Z` |
| recovery | 72 | 71.48 | `20261106T083752481657Z` |

The collection inventory has **927 repository cases**, zero collection errors and
zero skipped modules. **918 repository cases passed**; **nine were deselected**:
six real-hardware smoke cases and three desktop/audio timeout cases whose required
sounddevice/webrtcvad environment was intentionally not installed. Two bounded
slow tests were explicitly included. Exact node IDs/reasons are in
[TEST-INVENTORY.json](TEST-INVENTORY.json). A manual Ollama CLI helper contains zero
test functions and raises on missing optional SDK at import; the guarded runner
explicitly excludes that helper, without counting it as a test or a pass. Do not
substitute an unguarded production-directory pytest invocation for reproduction.

An additional **80 retained authority/router/process packet cases passed**, giving
**998 distinct pytest cases**. Full-app's **103 pytest cases repeat an exact subset
of repository tests** and are not added again. It also independently runs **20
application scenario groups** and three native dependency probes. This is the
broadest safely executed offline closure here, not hardware, provider, browser,
frontend runtime, full desktop or deployed dependency qualification.

Initial collection exposed absent optional imports, missing fixture HOME/tasks
files and retired ScheduledJob imports. Initial broad and legacy runs exposed
outdated completion/tool/JSON contracts, real-startup assumptions and missing
bearers; these were corrected and rerun. The stricter ancestry checks additionally
rejected old group-writable full-app/benchmark scratch parents; those fixtures
were made private rather than weakening the product. Independent static review
found further actual WebSocket and pre-creation ancestry defects and drove fixes.
A final whitespace-only change has independently confirmed identical AST and was
followed by fresh exact-byte runs. [REGRESSION-EVOLUTION.json](REGRESSION-EVOLUTION.json)
and all original run stdout/stderr preserve the unsuccessful iterations; they are
excluded from acceptance totals.

## Security hypotheses and independent review

The completed comprehensive Cloudflare audit reviewed a frozen 390-file revision,
not every later candidate byte. It reported zero confirmed exploitable
vulnerabilities, one conditional authority lead, one rejected dormant screenshot
trace and a current UE5 cleanup defect. [CLOUDFLARE-AUDIT-REVIEW.json](CLOUDFLARE-AUDIT-REVIEW.json)
retains exact observed findings/defects/metadata and hashes. Its six older defects
were already closed in Sprint 6; those closures were exercised again here.

The anonymous read/cancel behavior was reproduced using original baseline router
source and explicitly admitted disposable state. It is confirmed application
behavior under that fixture, not proof of an operating anonymous deployment or a
cross-UID/browser exploit. The candidate refuses it, including actual admitted
lifespan tests, embedded routes and malformed credentials. No real deployment was
probed to establish the earlier conditional threat facts.

The original exact ancestor-switch harness was rerun on the candidate and again
failed with SQLite's read-only-database refusal; no invented task was accepted.
[ANCESTOR-HYPOTHESIS.json](ANCESTOR-HYPOTHESIS.json) records the result. Additional
real-filesystem tests reject group/world-writable ancestors before child creation,
symlink insertion during creation and replacement with the same leaf inodes.
These checks do not prove hostile-root/same-UID resistance or an atomic SQLite VFS.
Actual different-UID rights, ACL/mount identities and external custody remain
operator assurance requirements. They are not silently declared fixed deployment
facts. See [SECURITY-REVIEW.md](SECURITY-REVIEW.md) for the crosswalk and limits.

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records separate read-only delta review,
review-driven fixes and nine exact final source/default/context pins. No remaining
critical/high/medium defect was found in that reviewed delta. The reviewer did not
execute tests or change files. Current runtime results belong to the primary
engineer's isolated evidence, not the static reviewer or historical audit.

## Complete application and crash evidence

[INTEGRATED-DEMONSTRATION.json](INTEGRATED-DEMONSTRATION.json) reruns the real FastAPI
lifespan, bearer-protected API, admitted witnessed Authority/recovery registry,
queue, actual scheduler registration/callback, independently permitted signed
AF_UNIX synthetic endpoint, reservation/report/evidence/publication receipts,
cancellation and shutdown. Scheduled callbacks use the original nominal time;
this is not wall-clock cron qualification. No network listener or real tool runs.

That same history includes witness renewal, a committed-report/lost-response UNKNOWN,
actual FD-only operator CLI reconciliation and identical receipt replay, a restart
that retains the separate publication hold, a second explicit publication permit,
and another real lifespan with zero endpoint redispatch. Its archive verifies and
restores inert; a durable proposal and authenticated approval preserve original
UUIDs and still cannot open as an active branch. Legacy tools/getters/chat/vision,
confirmation, dictation and host mutation paths remain closed.

[CRASH-RECOVERY.json](CRASH-RECOVERY.json) has **15 current independent-process
transport SIGKILL observations**, plus **22 registry/witness SIGKILL observations**
from retained crash shapes rerun on current source. All transport restart cases
made zero new endpoint calls. Missing reports stay UNKNOWN; authenticated durable
evidence may publish without redispatch under its appropriate authorization.
Stale writers, replay/forgery, wrong keys, expiry/revocation, partial publication,
missing/rolled-back/corrupt anchors, SQLite/injected ENOSPC and restart reconciliation
are covered. No historical crash observation was relabeled as a new run. SIGKILL
and injected disk-full tests do not establish physical power-loss or actual full
host-disk durability.

## Dependency, performance and evidence identity

The base 28-distribution environment and plan/interpreter/bwrap identities are
verified before payload execution. Three supplemental retained wheels (NumPy,
BeautifulSoup, SoupSieve) match saved upstream file hashes and every wheel RECORD;
no download or host environment install occurred. Supplemental files are mounted
read-only and checked in-cage. Full-app uses the base closure; broader unit tests
use 31 packages. This is not a fresh advisory audit or the complete optional
production desktop/provider graph. The lock, retained metadata and SBOM-like
inventory are in release/BUILD.json and OPTIONAL-DEPENDENCIES.json.

Thirteen current bounded benchmark cases passed, including actual 1/4/8-task signed
IPC histories. [PERFORMANCE.md](PERFORMANCE.md) gives exact timings and resource
maxima. No limit was raised, and no guard stop occurred in the final modes. All
heavy payloads ran sequentially in networkless capability-free namespaces. Prior
verified artifacts were read only; the comprehensive audit was not interrupted.

[SOURCE-SHA256.json](SOURCE-SHA256.json), release manifests, per-run input manifests,
SYMLINKS.json and SHA256SUMS bind source and evidence. Verification preserves all
**114,583 initially existing predecessor files** and the canonical log prefix.
The required completion entry is appended to this project's tasks/loop-log.md.
The source archive excludes runtime config, keys, databases, logs, model files and
sealed evidence; it must travel with its retained offline test dependencies and
evidence companion for reproduction. It is not a self-contained OS/container image.

## Exact next decision and remaining blockers

[READINESS-CHECKLIST.md](READINESS-CHECKLIST.md) separates passed offline criteria
from unresolved live prerequisites. The **one consolidated proposal** is
[LIVE-READONLY-PROPOSAL.md](LIVE-READONLY-PROPOSAL.md), cryptographically bound to this
candidate in its JSON companion. It proposes prerequisite verification followed,
only under separate authorization, by one `identity` action through the already
qualified standalone VM164 broker with a retained explicit 32-hex request ID.
It does not connect a JARVIS real adapter or bundle credentials, role/ACL changes,
installation, guest changes, production startup or privileged qualification.
Unknown installed UID/GID, machine/boot, grant/time, source/CA and canary acceptance
facts remain null/blocking. If setup is needed, stop for a separate exact proposal.

Live use remains blocked by independent installed identity/custody/permission and
VM164 no-NIC/serial facts, physical storage durability, reviewed real-adapter
integration, credentialed browser/probe design, current intended dependency/advisory
qualification and ingress/frame/worker controls. Shared bearer is not per-principal
identity; co-located symmetric HMAC transport is not privilege isolation or public-key
nonrepudiation. Native child leases remain RAM-only. Transport history is capped
at 128 lifetime grants and fully scanned; tested transport performance reaches
eight tasks, not that cap. Mutable Docker/action/model references and dormant
capture helpers require separate review before reuse. None of these limits is
waived by an approved restored proposal or by this offline PASS.

Recommended next offline work: independent service/adapter authorization custody,
two-principal synthetic qualification, and bounded authenticated history archival.
Do not activate real execution to advance those investigations.
