# JARVIS consolidated offline engineering review R1

The serial broker is a reviewed, uninstalled candidate. The core queue/scheduler
changes are uncommitted source improvements with focused offline evidence.
**Nothing is activated, and no live isolation or production readiness is proved.**
No action was denied in this sequence. Protected setup, credential issuance,
PVE/guest changes, live activation and privileged qualification are **pending and
unattempted**, not rejected. This report grants no authority.

## Review boundary and exact current source

Workspace: `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS`.
Base HEAD: `7f4ae164261b792262eb9b818421c444c2d4ccff`.
Branch: `docs/p7-d06-d07-passive-review`. The checkout is dirty: three application
files, status/log metadata and untracked tests/task packets. No commit/staging or
deployment was performed by this sequence. A branch/HEAD alone does not identify
the changed source.

| Current core file | SHA-256 |
| --- | --- |
| `app/agent/task_queue.py` | `50d1a4ebd6132f2593095874b170fa895d09c5bcd9ead9c598312cbf3314fc4c` |
| `app/agent/scheduler.py` | `71183f5bf54bc36f96a62abf04a1ca73566805f0eda67cdefba5f4410a726181` |
| `app/server.py` | `613a3b08ae074484f0187b0234105c05b85239c45c577eee69a2b0bd8e17052c` |

[SOURCE-SHA256SUMS](SOURCE-SHA256SUMS) binds14 public application/test/context files;
its digest is `6a7f43903b4d1353a6fbbb4f48f0e0053ea5f1ec6f3b987466131f308e5cccc6`.
The retained three-file diff from HEAD hashes to
`6a61fc62c8bc242e883721af6012bd62f327bb69e94c9291a357a4db4f18145a`.
Exact prechange blobs, source hashes, git status, tracked/staged diff hashes,
receipt identities and eight packet checks are in
[verification-20261030T225530235949Z.json](verification-20261030T225530235949Z.json).
This is a timed working-tree observation, not an atomic whole-tree or deployed
snapshot; the authorized status pointer and canonical completion append follow.
The source files themselves stay unchanged during consolidation. R3/R4 retain
exact public source snapshots; no source copies or prior tests are regenerated here.

## Milestones and evidence — counts overlap

| Milestone | Deliverable and authoritative retained receipt | Verified scope/result |
| --- | --- | --- |
| [Reviewed broker R1](../proxmox-automation-phase3-review-r1/README.md) | [release identities](../proxmox-automation-phase3-review-r1/RELEASE.json), [positive receipt](../proxmox-automation-phase3-review-r1/evidence/offline-tests.json) |71 methods/305 subtests;13 source files;40 public archive members. Fixed catalog broker/worker, replay/receipt handling, bounded framing/output and no-transport credential precheck. |
| [Queue persistence R1](../jarvis-v2-taskqueue-reliability-r1/README.md) | [positive receipt](../jarvis-v2-taskqueue-reliability-r1/evidence-20261030T213725199478Z.txt), source identity/diff |13 methods; includes10 existing functions as subtests and18 injected prepublication mutation failures. Atomic JSON publication/rollback and explicit uncertain-state handling. |
| [Queue store safety R2](../jarvis-v2-taskqueue-reliability-r2/README.md) | [positive receipt](../jarvis-v2-taskqueue-reliability-r2/evidence-20261030T222357610970Z.txt), frozen predecessor, defect baselines |29 methods/65 subtests: R1's13 plus16 new. Bounded IDs, damaged-store preservation, whitespace/empty-status compatibility, nonfinite rejection and nonregular-file protection. |
| [Queue callers R3](../jarvis-v2-taskqueue-callers-r3/README.md) | [positive receipt](../jarvis-v2-taskqueue-callers-r3/evidence-20261030T223312529709Z.txt), exact source snapshot, [ownership map](../jarvis-v2-taskqueue-callers-r3/OWNERSHIP.md) |42 methods/82 subtests: the29 queue methods plus13 new caller methods. Typed publication/audit outcomes and reconciliation IDs; truthful enqueue timestamps; no internal retry. |
| [Scheduler reliability R4](../jarvis-v2-scheduler-reliability-r4/README.md) | [positive receipt](../jarvis-v2-scheduler-reliability-r4/evidence-20261030T224808335328Z.txt), [caller/limits map](../jarvis-v2-scheduler-reliability-r4/CALLERS-AND-LIMITS.md), exact source snapshot/defect probe |39 methods/54 subtests:25 new,13 R3 caller methods and one wrapper for10 existing functions. Atomic schedule publication, explicit uncertainty, disabled/stale owner/object/lifecycle admission and failed-start cleanup. |
| [Public provenance](../jarvis-offline-provenance-r1/FINAL-REPORT.md) | [final byte-inspection evidence](../jarvis-offline-provenance-r1/evidence-20261030T222449706209Z.json), nine synthetic inspector tests |Gate6K615 source entries/616 archive members; Gate6L657 entries/658 members;131 artifact records/127 distribution pins/141 wheels. These are integrity counts, not application test counts. |

All selected positive receipts pass with no recorded failures/errors/skips.
**Do not add these numbers.** Subtests nest inside methods; R2 includes R1; R3
includes R2; R4 reuses only the relevant caller/legacy subset. R4 is not a rerun
of all42 R3 methods or a new complete application baseline. Broker revisions also
overlap earlier broker suites. Negative predecessor runs intentionally fail and
demonstrate defects; initial fixture/inspector mistakes are retained and explicitly
superseded in their packets. They are not passing coverage or current regressions.

The code is now later than the source used for R1/R2/R3 receipts. Current queue
remains R3's50d1…; scheduler/server are R4's71183…/613a…. Historical snapshots and
receipts remain attached to their own source identities. Consolidation ran **zero
tests** and executed/imported no inspected payload or application module.

## Broker identity and validation boundary

Reviewed source manifest:
`9e5bdd0ea59fa36021f462f4388597fefd4b65f9cee32024e86ba5d33d700301`.
Public archive:
`e2ab01927aeeff20d6e6a6e602aee112b3d1e99a79aaaf88d9263182e6a142f1`.
The actual original manifest58698f4c… and its packet are preserved separately;
the original packet had no archive. Current consolidation verifies the retained
packet member/archive hashes; the archive reopen/member comparison is the earlier
sealed release evidence, not a new live check.

The standalone broker authenticates the submitting Unix identity, pins an expiring
grant/source/TLS target and VM164 UUID/serial binding, and uses a protected separate
VM164 console credential. The guest catalog is only `identity`, `kernel` and
`isolation-summary`, with built-in read-only observations and no arbitrary shell.
Guest text is untrusted data and never executed. Replay/reservation/receipt state,
timeouts, locking, output bounds and explicit unknown outcomes are implemented.

The broker's71/305 evidence includes real same-UID Unix/TLS/PTY exchanges, bounded
child SQLite crash cases and Nexus seccomp probes against synthetic remote state.
It does **not** prove cross-UID DAC, restricted Codex identity, real PVE ACL/API/
WebSocket behavior, guest TTY/kernel/systemd isolation or Gate6K qualification.
Staged unit syntax verification is not installed service enforcement. A compromised
guest can lie about observations; local audit hashes do not supply independent
anti-rollback authority. A client receipt acknowledges parsed data, not durable
stdout/human observation. Stop/revoke must close existing channels and preserve
ledgers; token deletion alone is not proof an established channel ended.

## Independent targeted review

Actual reviewer: separate read-only `/root/serial_security_review`, configured
`gpt-6-astra`, reasoning high. No Claude or independent test rerun is claimed.
The reviewer changed no files and performed no credential/live/privileged action.

- Broker: four medium findings (lifetime framing budget, receipt lock race,
  attachment/readiness synchronization, credentials preceding actual-principal
  denial checks) and three follow-up edge cases were fixed. [Recorded closure](../proxmox-automation-phase3-review-r1/INDEPENDENT-REVIEW.md)
  reports no remaining blocking targeted finding for manifest9e5bdd… .
- Queue R2: two medium blockers—self-generated whitespace/empty-status records
  quarantining on reload, and blocking FIFO reads—were fixed and closed.
- R3: targeted closure found no blocker in publication/audit outcome propagation,
  reconciliation IDs, scheduler timestamp ordering or successful-response compatibility.
- R4: targeted closure found no blocker in rollback, applied-state quarantine,
  owner/object/generation checks, startup cleanup and stop ordering. It explicitly
  retained the already-admitted enqueue limitation.

These are scoped code-review dispositions, not full security certification or
operator authorization. Queue R1 and the provenance utility have implementation/
receipt verification; no separate independent full review is invented for them.

## What the core tests do and do not establish

Queue/scheduler/caller tests compile actual definitions while excluding real audit
imports and module singletons. Audit is recorded in memory; HTTP JSONResponse is
a recorder; decorators/routing/middleware/model validation are excluded. R4's
BackendRecorder has no timers/threads/framework/services; start/shutdown only
change fixture fields. Files and enqueued task records are disposable synthetic
fixtures. FIFO checks use a bounded isolated source-loader child.

This is **AST-isolated source/failure testing, not actual FastAPI/Pydantic/ASGI or
APScheduler integration**. No real app/lifespan/service was started. Recorded zero
guarded parent-network attempts does not turn these into live or cross-UID tests.

The current searched production app has no dequeue/claim/lease executor draining
TaskQueue. Chat/tool execution is separate. The standalone broker has not been
wired into an active application queue executor. JSON task creation and scheduler
enqueue acknowledgement are not goal execution.

Each process/instance has a private snapshot/asyncio lock or generation. Neither
atomic replace nor hash comparisons enforce a cross-process owner. A fresh
fixture demonstrates a stale second writer losing the first task. CLI wake fallback
and host/container launches can create another owner; actual deployment overlap
was not inspected. There is no durable HTTP idempotency key, occurrence receipt,
transactional outbox or exactly-once execution guarantee. HTTP retry fields are
advisory, audit submission is asynchronous and last_run is transient enqueue metadata.

R4 rejects newly arriving stale/disabled/removed callbacks. **Already-admitted
enqueues can finish after remove/stop returns**, including while waiting on the
queue lock; this is tested, not hidden as a cancellation guarantee. Callback
queue/audit exceptions retain R3 propagation and do not blanket-quarantine the
scheduler. Later distinct cron fires are not deduplicated occurrence retries.
Mutable internal references, synchronous I/O, unsupported directory sync and
hardware power-loss limits remain. Resource ACTIVE is not scheduler readiness.

## Gate6K source/dependency provenance is historical

The retained Gate6K source archive hash is
`ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d`,
manifest5a68588e… . Gate6L archive is228b0086…, manifest1c598e37… . The
[provenance report](../jarvis-offline-provenance-r1/FINAL-REPORT.md) holds full pins,
wheel records and signature/integrity limitations; matching bytes is not a new
publisher signature, current dependency compatibility or execution authorization.

Its600-path workspace comparison at22:24:45–22:24:49 UTC recorded267 same,
17 different and316 absent files. That scan predates R3/R4 and is not repeated or
presented as a new whole-tree observation. Current exact comparison of the three
core files still differs from Gate6K: queue e9df1b…→50d1a4…, scheduler
f8c578…→71183f…, server cb16b2…→613a3b…. Machine evidence gives all full hashes.
The earlier scan found two extra Python test files; R3/R4 subsequently added two
more. No current full-tree compatibility or transplanted candidate_v3 is claimed.

**Historical7741 passed/11 deselected is preserved historical evidence for its
own sealed source/runtime. It does not validate this checkout.** No full baseline,
Golden12/20 rerun, privileged multi-UID qualification or real provider/model run
was performed here.

## Remaining blockers: technical gaps versus authority gates

| Item | Current status and required next evidence |
| --- | --- |
| Full framework/dependency integration | Technical gap: current interpreter cannot discover FastAPI/Pydantic/pytest/APScheduler. [A bounded future plan](INTEGRATION-PLAN.md) and [exact candidate inputs](INTEGRATION-INPUTS.json) are provided. No blanket human-approval requirement for routine offline engineering is invented; no install/import happens during consolidation. |
| Single-owner/idempotency/occurrence/outbox design | Unimplemented product semantics, not a failed permission request. Keep the [R3 proposal](../jarvis-v2-taskqueue-callers-r3/OWNERSHIP.md) separate from a future migration; no daemon, hash-check lock or auto-migration is introduced. |
| Actual restricted Nexus executor | Pending specifically privileged setup and boundary evidence. A new account alone is insufficient if the submitting Codex process retains administrator/container/ptrace/service or privileged-FD paths. Current process has not passed the required actual-principal qualification. |
| Credential denial before issuance | Pending actual no-transport precheck using a synthetic protected canary, code/config/unit denial and independent escalation review. Broker stays disabled with no real token/activation marker. Root-controlled fresh source/grant/UID-bound attestation must precede real issuance; it expires within600 seconds. |
| PVE permission | Pending new separated principal/token with only VM.Audit+VM.Console on /vms/164, propagate0, bounded to the approved window (initial maximum3600 seconds). Existing VM.Audit observer remains unchanged. No root credential is exposed to Codex. |
| Trusted VM164 setup/identity | Pending trusted installed-root context, actual guest machine-id, numeric identities/filesystem facts, pinned offline transfer and exclusive ttyS0 ownership. Locked passwords stay locked; no SSH/NIC/QGA workaround. Missing root access means stop and scope exact maintenance media/filesystem/preservation/power transitions separately, not generic rescue authority. |
| Live read-only acceptance/activation | Pending explicit timed activation scope after all earlier stages pass. Recorded target is VM164 UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193, serial0/ttyS0 and no NIC; those facts need future live revalidation, not assumption from this report. Actual UID/ACL/TTY/kernel/QEMU behavior remains unproved. |
| Privileged Gate6K/future command expansion | Separate pending authorization. Broker setup does not authorize multi-UID qualification, privileged/mutating catalog commands, production changes or other-system access. |

The **single existing staged request** remains
[APPROVAL-PACKET.md](../proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md), with
[exact limited installation](../proxmox-automation-phase3-review-r1/INSTALLATION.md),
[live acceptance](../proxmox-automation-phase3-review-r1/LIVE-ACCEPTANCE.md),
[public binding template](../proxmox-automation-phase3-review-r1/approval.example.json)
and [stop/revoke/evidence preservation](../proxmox-automation-phase3-review-r1/STOP-AND-REVOKE.md).
These links are not fresh approvals. Preserve private ledgers/receipts; never export
token.json or whole credential/state directories. VM162, VM163 and the AI server
remain outside scope. No permissions, bootstrap or activation are attempted here.

## Consolidation result and next safe work

Eight prior packet manifests/193 members match retained pins. Code is unchanged;
only this report/evidence packet, a status pointer and canonical log append are
written. This packet's SHA256SUMS is its review identity, not a signature/approval.

The next routine offline unit may refine the bounded isolated dependency/framework
plan or build fresh source-level ResourceManager readiness/error-propagation
fixtures. Current technical restrictions and exact side-effect bounds govern that
work; privileged host/PVE/guest setup remains separately gated. No next code unit
was started during this consolidation.
