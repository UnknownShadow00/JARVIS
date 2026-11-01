# JARVIS: offline durability, readiness and client compatibility

Date: 2026-10-31 (America/Chicago).
Status: source/offline engineering complete for these bounded contracts.
Real execution, production startup, broker wiring/activation and live qualification
remain disabled/unperformed. This report approves no action or security change.

## Implemented authority and preserved evidence

One SQLite authority owns tasks, schedules, occurrences, receipts, events and
held outbox state. A lifetime writer lock excludes a second process; durable
generations and transaction-time identity checks fence stale owners. Canonical
full UUIDs bind operation, server-owned scope and payload to durable receipts.
Same-key replay returns the stored decision; changed requests conflict. Task,
occurrence, receipt, outbox and schedule last_run commit together. Lost responses
require original-key reconciliation, never blind fresh-key retry.

The scheduler uses nominal UTC occurrence identity and one-shot timers. Stop,
remove and disable cancel pending occurrences. Claimed work retains honest
cancel_requested/UNKNOWN outcomes; an applied effect is never declared prevented.
Backend failures preserve committed decisions and disable further admission.
Stop attempts local cleanup even when its durable stop cannot be confirmed.
Explicit bounded legacy import preserves source bytes/mappings, disables imported
schedules and retains historical nonpending work as UNKNOWN. No real store was
read or migrated. The opt-in simulator writes only synthetic SQLite effect markers;
there is no external executor or public completion/result mutation endpoint.

Preserved predecessor packet: tasks/jarvis-authority-readiness-r1/.
Its seal is
840451e8b09397793e72fbada08ef7dc82d86b5f41ea93e8d731162d283202a8.
Its source manifest is
965f210acd46304cad1021ebe93cc9249ac767ac5ae006f983d422786bb3730f.

That packet records 80 focused cases, zero failures/skips, including eight actual
independent-process ownership/crash/recovery cases. The actual app.main/server
offline lifespan passed four scenario groups: readiness/routes/auth/replay,
shutdown, mandatory storage-failure cleanup and overdue-schedule startup refusal.
Three native dependency checks passed with pinned origins/hashes. Core took
9.470 seconds with 102,662,144-byte observed aggregate RSS peak; full-app/native
took 1.088 seconds with 78,958,592-byte peak. The expected synthetic startup
warnings concerned absent Piper binary/model and an unserved loopback probe.
They were retained; a warning-free full-app run is not claimed.

The exact retained 28-distribution closure has 31 active dependency edges and
1,096 verified wheel RECORD payloads; its private target pins 1,188 files.
Recognized hash-pinned PyPA pip ran only inside fresh guards, without downloads,
source builds or global installs. Full-app tests then used a fresh pip-free
interpreter with synthetic config and disabled real providers/voice/comms.
The original 22-package target remains unchanged. Independent gpt-6-astra/high
static review closed ten findings on eight backend sources before any executor
wiring. That verdict does not cover live isolation or claim new reader review.

## Actual first-party caller inventory and compatibility

The successor inventory inspected 143 scoped public files (627,183 bytes): app,
CLI, desktop/HUD/PWA/hologram, scripts, evals, active docs/CI and four named active
top-level diagnostic scripts. It excludes dependency/generated bundles, historical
sealed tasks/run copies, snapshots, test fixtures and real configs/runtime data.
INVENTORY.json records exact paths, hashes, patterns and line evidence;
CALLER-CLASSIFICATION.json records manual transport/path classification.

No first-party task/schedule mutation client exists in that scope. No mutation
client was invented. The CLI calls health/resource routes; Electron/hologram use
WebSocket messages; the PWA uses WebSocket chat and REST /chat fallback. Its
service worker forwards requests but does not construct queue mutations. Sensor
scripts target /sensors/data. Server routes, scheduler/backend internals and old
tests are not deployed HTTP clients. Existing lifecycle start/stop calls remain.
Boot state/todo counters describe project backlog, not runtime queue receipts.

One actual read consumer required a change: app/agent/reporter.py. It now reads
the authoritative snapshot, labels pending work as admitted with execution held,
shows UNKNOWN and cancel_requested, preserves actual cancellation/simulation
states and reports unavailable storage as requiring reconciliation. It no longer
falls back to a hidden legacy dictionary or says all systems are nominal.

The affected existing tests/test_reporter.py was updated; stale _tasks patches
were replaced by disposable real-authority snapshots. Ten focused cases pass,
zero failures/errors/skips, in 1.383 seconds with 59,666,432-byte observed aggregate
RSS peak. They cover held admission/read-only reporting/full IDs, UNKNOWN,
claimed and confirmed cancellation, synthetic completion, storage unavailability
and disabled/mocked messaging. No real Discord/Telegram/provider/voice send ran.
Final run: runs/20261031T092526957242Z/RUN.json in the successor packet.

The prior nine-case packet-only pass is superseded. An intermediate ten-case
fixture failed because its temporary path traversed the cage's /tmp symlink;
Authority correctly rejected it. Resolving the owned temporary path fixed that
fixture. Both records are retained; backend and guards were not weakened.

Active README, CLAUDE guidance, Hermes guide and resource-management notes now
describe the single-writer/reconciliation boundary. docs/task_api.md specifies
retained UUIDs, identical retry payloads, full IDs, original-key receipt lookup,
soft DELETE cancellation and removed public PATCH completion. Hermes takeover or
parallel writers are not implemented/supported. No authentication policy changed.
No external client was accessed or verified; external compatibility remains a
rollout gate requiring those semantics before connecting it.

## Current identities, bounds and reproduction

The eight reviewed backend files remain byte-identical to the predecessor. The
only changed application source is the separately tested reporter. Thus the old
88-file full-app snapshot is predecessor evidence, not a new whole-app rerun.
The unchanged 80-case backend suite was not rerun for this reader/docs change.

Current successor SOURCE-SHA256SUMS pins 147 public source/context files:
56cdaf308bed23455906205df99f8a085714bd6eb203df1dacaf94f4e4c309d9.
Current reporter SHA256:
77a247a9f34cf25ef2294acd1c9785373da6987757fdbdabd27a548cf9bea545.
Current tests/test_reporter.py SHA256:
168e62ba55193e95509a53bb67de44c2380985da240777223f30851b55fc1442.
Final focused RUN.json SHA256:
7394456419633ecd509e1370d05159d8b62e021b90a3a577800494ee441d8085.
RESULTS.json binds these to unchanged backend hashes, superseded runs and the
preserved predecessor seal. SHA256SUMS seals this successor's public evidence;
RELEASE.json records preservation and source/report identities.

Verification used one payload process in the existing verified unprivileged
bubblewrap, with fresh user/mount/PID/network/IPC/UTS namespaces, capabilities0,
NoNewPrivs, stdio-only initial descriptors, read-only source/dependencies and hidden
outside sentinel. IPv4/IPv6 documentation-address probes were unreachable. No
installer, application server or device runtime started in this continuation.
Its watchdog limited aggregate RSS to128MiB, wall time15s, controlled files2,000
and controlled tree16MiB; observed193 files/1,029,590 bytes. Existing per-process
limits remained AS1GiB, CPU120/121s, file64MiB, descriptors64 and core0. No cap was
enlarged. The new Nexus heavy-window reservation was respected; parent scheduling
clearance preceded focused verification and did not change any resource cap.

Scoped discovery is reproducible with the recorded rg patterns and inventory.py.
To rerun safely, use a new unsealed copy, retaining original sealed packets:

```sh
cd '/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS'
sha256sum -c tasks/jarvis-client-compatibility-r1/SOURCE-SHA256SUMS
set -e
test ! -e tasks/jarvis-client-compatibility-reproduction
cp -a tasks/jarvis-client-compatibility-r1 tasks/jarvis-client-compatibility-reproduction
python3 -I -B -S tasks/jarvis-client-compatibility-reproduction/run_reader_checks.py
```

The runner validates the retained dependency target and current backend hashes,
checks fresh public headroom, copies only public source/example into its new
fixture and imports the actual reporter under synthetic configuration. It never
reads a real store/config or contacts production. Historical durability/full-app
commands and frozen inputs/results remain in the predecessor report/run records;
reproduce them only in a separate unsealed workspace, preserving original seals.

## Remaining limits and conditional eventual-live proposal

Offline processes/mocks are not proof of live VM isolation or physical disk
power-loss durability. Same-UID hostile code, external anti-rollback, multi-host
storage, optional voice/provider features and real-effect reconciliation remain
outside this evidence. An overdue enabled schedule blocks startup instead of
catching up; explicit owner-quiesced disable/recreation is required, following
the preserved offline recovery procedure. Never reset ledgers, delete locks,
rewrite timestamps or fresh-key resubmit uncertain work to force progress.

No actionable security request exists until the actual restricted Nexus execution
identities/path and trusted guest/bootstrap/grant bindings are established.
No stage is approved or actionable by this document. The current privileged
Nexus session is not an accepted submitting boundary. Actual guest machine-id,
numeric role identities/filesystem binding, trusted installed-root context and
complete finite grant/expiry facts remain prerequisites, not guessed values.

Only after those facts exist may an operator consider the existing staged packet
tasks/proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md:

1. Independently establish the restricted Nexus submitting/broker identities and
   protected source/config/units. Complete actual no-transport denial tests with
   synthetic canaries before any real credential issuance.
2. Separately authorize only a fresh broker-only PVE grant of VM.Audit plus
   VM.Console on /vms/164, propagation0 and finite initial expiry. Keep the existing
   observer token unchanged and all secrets outside Codex, logs, argv and exports.
3. Through a trusted installed-OS root context, separately authorize only the
   pinned locked non-root worker/config/unit and exclusive serial0/ttyS0 setup.
   Keep passwords locked, no SSH/NIC/packages/guest-agent or privileged catalog.
   Missing root context requires an exact separately approved maintenance/media/
   partition/preservation/lifecycle plan, not a password or GRUB workaround.
4. After genuine identity, DAC and transport gates pass, separately authorize a
   timed live read-only acceptance window for VM164 UUID
   faeb1db8-0df9-482d-b3e4-f6ccc1602193 and the exact disk/serial binding. Initial
   catalog remains identity, kernel and isolation-summary. No raw console access,
   arbitrary commands, executor wiring, mutations or privileged Gate6K is implied.

The reviewed broker source manifest remains
9e5bdd0ea59fa36021f462f4388597fefd4b65f9cee32024e86ba5d33d700301;
its public archive remains
e2ab01927aeeff20d6e6a6e602aee112b3d1e99a79aaaf88d9263182e6a142f1.
Its INSTALLATION.md, LIVE-ACCEPTANCE.md and STOP-AND-REVOKE.md retain exact limited
operator steps. Before approval there is nothing to activate from this report.

Conditional stop/revoke closes accepting sockets/services and active channels,
revokes only the new VM164 token ACL/token, and stops only the new worker if that
stop scope was approved. Preserve ledgers and independent checkpoints; token
deletion alone may leave an established console alive. No automatic rollback,
getty restoration, reboot, VM deletion or private state/credential export is
authorized. VM162, VM163, the AI server and other applications remain untouched.
