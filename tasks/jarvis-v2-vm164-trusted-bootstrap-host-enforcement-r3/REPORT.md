# R3 host enforcement — final offline engineering result

**PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY**

A concrete host-side preservation-first enforcement candidate is implemented,
independently reviewed and fixture-tested. **Live qualification and trusted-root
bootstrap remain NO-GO.** Policy A cannot guarantee expiration; Policy B is
modeled, disabled and unauthorized. No favorable mock has been promoted to host,
root-access, installation or Gate6K readiness.

## What was done

Implemented strict VM164 hardware/current-config/digest/ISO checks, a host-owned
prearm/start protocol, exact transient timer/service readbacks, suspend-aware
clock conversion, bounded allowlisted commands, root-private source/approval/
review/package gates, persistent session/approval fencing, hash-chained receipts,
rollback/quarantine, duplicate/interrupt handling and evidence-preserving cleanup/
retirement. Default CLI is dry-run. The real interface requires explicit future
execution flag, exact root-installed path, protected reviewed Stage2 records and
finite Stage3/A/non-root authority. None is installed or active here.

The source restricts every VM selector to164. No unlock/skiplock/protection change,
generic shell, VM config edit or native qm-stop route exists. B cannot be enabled
by a flag or JSON. Stage4/root-purpose approval is rejected by this build.

The current operator-reported pve/9.2.5/kernel7.0.14-6-pve/systemd257.13 readbacks
and stopped/order=scsi0/r4-attached VM facts are recorded in evidence/ENTRY.json.
They are accepted as verified operator reports, not independent Codex live checks.
No boot-order correction was repeated or implied. CPU/RAM/balloon and additional
binary/package/custody/clock facts required by the candidate remain unverified.

All three predecessor folders were inventoried/read and their sealed bytes
preserved:247 regular files,5 symlinks;207 text/source/evidence records indexed.
No sealed r1/r2 artifact, guest helper, application source or dirty worktree was
changed. Only this new task folder and append-only project tasks/loop-log.md
completion entries were written.

No network, Proxmox connection, real timer/service, host install, package query,
VM/guest command, credential/grant change, production action, Gate6K, JARVIS
installation/startup, provider/database/broker/executor or V3 operation occurred.
Tests used fixture interfaces with process/signaling tripwires. Local manual
files were read, not executable system-manager commands.

## Exact verification

Final fresh combined run: **294 methods passed;0 failures,0 errors,0 skips**.
This actually executed123 r3 methods (105 author +18 independently written),87 r2,
43 original bootstrap,32 strict-validator and9 legacy-hazard reproduction methods.
The last9 confirm preserved defects in old code; they do not claim the old
candidate became safe. Subcases are recorded separately, not added to294.

Additional verification:15 synthetic snapshot fixtures (1 consistent,14 expected
refusals);7 local CLI checks (dry-run, prerequisite refusal, cooperative/refusing A
and modeled B); source/AST/property/allowlist checks; deterministic inert archive
rebuild; all predecessor pins/seals and original canonical-log prefix preserved.
No real host/hardware/timer/termination test is counted as a pass or hidden skip.
See TEST-RESULTS.md and evidence/regression-release/RESULTS.json.

Independent reviewers found and drove fixes for setup rollback, prematurely
consumed phase claims, strict pre-action evidence, retirement/idempotence,
review/prerequisite binding, resource/I/O readbacks, clock-domain conversion,
stale source/session/grant generations and callback approval lifetime. Final
independent18 methods passed under tripwires. Initial failure findings, corrected
fixture error, retracted clock concern and all reruns are retained transparently.
Review reports are under evidence/INDEPENDENT-* and OFFLINE-PREREQUISITE-REVIEW.md.

## Inert review package and source pins

```text
candidate/host-enforcement-r3-offline-source.tar.gz
20418 bytes
archive SHA256 287894970aa2e5389cd405aa0a65ac633c75d7f4463b603484ffb04c60019d92
source-tree SHA256 43ea91000e251b9cf34fadf0466cb5135042a3232686c155de1b4ab5ee1ad3d1
standalone Stage2 canary SHA256 a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa
```

Exactly8 Python sources plus SOURCE-MANIFEST.json, fixed regular-file metadata,
no symlinks, credentials, installer activation, unit installation or JARVIS payload.
The verifier independently inspects/rebuilds the archive without extracting it.
No archive was transferred or installed. Source and artifact manifests plus the
final MANIFEST.json/SEAL.json provide local integrity, not a signature/WORM or
independent live-origin proof. Retain the manifest digest outside this workspace
with a later operator review.

## Design elimination versus modeled or pending behavior

| Area | Established by source/offline tests | Not established |
|---|---|---|
| Wrong target/default actions | Literal164 allowlist; strict identity/device/digest checks; default dry; no root-purpose/B runtime | Actual host current/API/storage/task semantics |
| Root before guest watchdog | Candidate does not admit root; host jobs would be prearmed while stopped before a separately gated start | Actual systemd deadline firing and absolute expiry |
| Partial/duplicate/replayed state | Reserved/consumed tokens, pinned source/session/grant, phase locks, CLOSED absorbing, archived retirement | Atomic exclusion of every external host-root/HA controller |
| Timeout/evidence failures | Shared command budgets, group kill/reap, durable intent, quarantine and failure receipts | Kernel/fs/manager hangs and queued PVE tasks completing within bounds |
| Timer proof | Exact modeled timer/service/argv/resources/clock interval predicates; canary protocol | Active timer/Type=exec alone does not prove eventual worker or termination |
| Policy A | Bounded graceful-only code, explicit blocker on refusal; no force fallback | NO strict access-expiration guarantee |
| Policy B | Distinct authorization model and explicit crash-risk requirement | No native implementation/activation, no real strict termination proof |

Absolute deadlines are host-boottime arm+540s grace, +600s deadline and required
stopped proof by+630s; start<=15s after arm. Runtime normal work budgets include
native authorization:40s grace,25s deadline, with45s/30s service limits and5s
stop limit. These are proposed/tested software criteria, not hardware guarantees.
Clock readbacks may be MONOTONIC while WakeSystem timers operate on BOOTTIME;
qualified conversion is mandatory. No actual clock domain was invented.

## Explicit remaining blockers

1. Real systemd257 show serialization, deadline clock domain/WakeSystem, exec/
   failure/scheduler/resource/cancellation/journal behavior is unqualified. Local
   primary docs are259.5, not the real host257.13. Reboot/reexec/suspend behavior
   cannot be assumed and needs separately reviewed host-impact scope.
2. Actual supported qm shutdown/stop flags and protection/lock/task semantics are
   not in retained matching offline documentation. Additional tool paths/hashes,
   Python/qemu package versions and existing unprivileged callback UID are unknown.
   Stage2 read-only inspection must close those gaps before any VM trial.
3. Stage3 actual VM164 current/disk/media/config/status, ACPI refusal/timeout,
   natural-stop/race, queued-task and independent stopped evidence is pending.
   Snapshots are not atomic and a killed CLI is not task completion.
4. Both jobs share host PID1/Python/storage/kernel/PVE dependencies. Host faults,
   identity drift, locks, damaged evidence, expired authority or external root
   controllers can prevent a timely stop. This design does not guarantee strict
   expiration through those failures.
5. Current A deliberately prioritizes preservation without force. Strict B would
   require separate explicit data-loss/force authorization, newly reviewed native
   code and physical qualification; authorization alone is insufficient.

No required unresolved assumption becomes PASS. Current source rejects any new
root bootstrap. Installation/Gate6K remain separate blocked milestones.

## Required deliverables and safe reproduction

DESIGN.md; SECURITY-AUDIT.md; TIMEOUT-AND-TERMINATION-POLICY.md; TEST-RESULTS.md;
QUALIFICATION-PLAN.md; OPERATOR-PROCEDURE.md; AUTHORIZATION-REQUEST.md; GO-NO-GO.md;
src/, tests/, fixtures/, templates/, candidate/, evidence/ and integrity manifests.
No real runtime locations were created. Installation/removal is review-only.

From the project root, use NEW exclusive output directories outside the seal:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/verify_packet.py
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src/cli.py --dry-run
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/run_checks.py --out /NEW-LOCAL-TEST-OUTPUT
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/replay_fixtures.py --out /NEW-LOCAL-FIXTURE-OUTPUT
```

A safer design avoiding an interactive guest-root console is possible in principle:
a separately reviewed hash-pinned noninteractive read-only diagnostic with null
stdin, narrow output and boot/task controls. It is not a qualified guest artifact
here. Prefer that path if crash-for-expiration authority/risk is unacceptable.

**Exact next operator action:** review AUTHORIZATION-REQUEST.md for a finite
Stage2-only NON-VM timer/interface qualification window, with existing-root setup
and verified NONROOT callbacks. Keep VM164 stopped/unchanged. Do not approve
Stage3, forced termination or root bootstrap by inference. Final recommendation:
**NO-GO for live enforcement/trusted-root bootstrap; Stage1 offline work complete.**
