# Qualification stages — only Stage1 authorized/completed

No later stage becomes authorized when a fixture passes. Keep VM164 stopped and
its currently reported r4 ISO attachment/configuration unchanged during Stage1.

## Stage1 — offline engineering and independent review

Implemented source, dry-run, filesystem/store fixtures, strict identity/unit/
clock/authorization predicates, Policy A runtime candidate and Policy B model.
Run all new tests plus preserved safety regressions with process/signaling
tripwires; replay negatives, verify source/archive/manifests and predecessor pins.
Independent code and prerequisite reviews are retained under evidence/. No
actual systemd, timers, package queries, Proxmox or VM interface is used. This
stage can report PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY, never live GO.

## Stage2 — supervised NON-ROOT, NON-VM timer/execution qualification

**Pending separate approval.** Existing host administrator privileges are needed
for tightly scoped root-system-manager setup/WakeSystem and root-owned public
callback placement. The CALLBACKS themselves must run as an independently verified
EXISTING unprivileged UID, never UID/eUID0. No guest boot/login, VM request,
credential/user/grant creation or use of the VM164 runtime worker belongs here.
If only user-manager timers are authorized, they cannot qualify the root-system
manager/WakeSystem mechanism; do not silently substitute them.

1. Read-only capture exact systemd/binary/package/interface evidence: provided
   paths plus python3, pvesh, pvesm, dpkg-query; supported Python; qemu-server and
   pve-qemu-kvm versions; installed qm help/manual for shutdown and stop; current
   show-property serialization. Root-owned binary/symlink chains/hashes are
   mandatory. No unsupported command guessed from this package may affect a VM.
2. Verify an existing unprivileged callback UID and its lack of VM privileges.
   Place only the standalone src/stage2_canary.py at the separately approved public
   root-owned immutable path. It has no subprocess/network/VM/manager/private-grant
   interface, defaults dry, rejects UID0 and checks its exact path/hash. The full
   host runtime/private grants need not be deployed to perform these callbacks.
3. With a NEW reviewed unique Stage2 unit namespace, record exact argv and create
   a harmless transient timer/service using Type=exec and the verified unprivileged
   User. Keep journal/results; do not use collect or reset-failed. Timer activation
   alone is not callback proof. Future setup belongs to the reviewed operator,
   not an automatic current-sprint script.
4. Capture paired CLOCK_BOOTTIME/CLOCK_MONOTONIC, boot-id and raw show bytes before
   and after creation, twice while waiting and after firing. Prove absolute future
   OnBootSec construction, actual NextElapseUSecMonotonic clock convention, offset
   conversion and latency. The code supports either qualified convention; default
   UNKNOWN blocks. A hand-authored equal-clock fixture is insufficient.
5. Observe callback success with NONZERO UID/eUID and intended clock values,
   intentional script exit7, missing executable/exec failure, missing dependency,
   timeout, inactive timer, timer/service failure, late firing, duplicate names,
   cancellation/cleanup interruption, distinct rearm and preserved journals.
   Proposed runtime property parsers/limits must match actual systemd257, including
   all requested resource, kill, timeout, private umask and I/O properties.
6. Review results independently; produce canonical hashed private review and
   prerequisite records with actual evidence references, never just set booleans.
   Unknown or failed requirements stay missing. Existing fixture kinds are rejected
   by native authorization; editing their kind does not create real evidence.

Manager reexec/restart, host reboot and real suspend/wake can affect the entire
Proxmox node/other VMs. They are **NOT** included in a harmless timer-window
approval. Qualify through a separately reviewed maintenance/appropriate isolated
scope or leave them unresolved. Do not reboot, suspend or reexec pve just to make
this table pass. Until proven applicable, no survival or hard-bound claim is made.

Stage2 success is a version/path/clock/custody finding, not VM termination proof.
Installed help semantics differing from the proposed flags require a new reviewed
source change and new hashes; never try undocumented fallback flags on a VM.

## Stage3 — supervised VM164-specific expiration validation

**Pending a separate finite approval and completed applicable Stage2 gates.**
The CURRENT BUILD permits only Policy A and normal/non-root VM164 qualification.
Policy B cannot run even with an approval JSON; see termination policy.

- Collect fresh trusted current config/status/pending plus storage/content checks;
  validate exact reported identity, disk/serial/size, fixed ISO, no NIC/agent/
  extra device/pending, disk-only boot and resource fields. Latest operator facts
  do not supply all CPU/RAM/balloon/binary-custody fields; do not invent them.
- Review original-disk preservation/recovery scope. Ordinary OS boots write state;
  a forced-stop test could damage it. No disk format/mount/repair, snapshot/media/
  boot-order/lock/protection change is implied. Keep r4 ISO attached for the fixed
  r3 hardware profile; no live eject. No VM162/163/200 or AI-server access.
- Install only the exact reviewed source and protected records after explicit
  installation approval. Pin source, package/binary versions, boot-id and finite
  grant. No code/grant/prerequisite replacement while a lease is active.
- Prepare while stopped, inspect actual timer/service/command/deadline/canary
  proofs and fresh status BEFORE start. Start<=15s from arm or NO START. One
  explicit normal-disk boot; no GRUB debug/root/rescue flags or guest command.
- Observe actual grace callback/task/ACPI behavior and fresh stopped state. Exercise
  refusal/timeouts/locking/cleanup/queued-task/natural-poweroff races only under
  individually named approved failure scope. The program does not bypass locks
  or protection. Lost acknowledgment or killed client is not task completion.
- If guest remains running, Policy A reports a HARD BLOCKER without force. The
  operator cannot assume force authority to finish a trial. Any manual emergency
  force is a new exact decision; this candidate offers no executable B route.
- Verify journal/invocation/result/evidence retention, cancellation only after
  actual stopped proof, idle workers, historical duplicate cleanup, archived
  retirement, approval replay refusal and independently approved next generation.
  Do not extend a running lease or reuse a boot-id/approval to save evidence.

A future Policy B trial would require a new reviewed native implementation,
separate explicit VM164 data-loss/forced-termination authority, qualified supported
command/lock/protection behavior and an accepted preservation plan BEFORE start.
This document neither provides nor requests that authority now. Even that trial
cannot prove an unconditional bound through every host/identity/lock failure.

## Stage4 — new trusted-root bootstrap authorization

**NO-GO in this build.** No Stage4/root purpose is accepted by the runtime.
Policy A cannot enforce expiration of uncooperative privileged access. B remains
modeled, disabled and unauthorized. Earlier actual qualifications and a new
reviewed root design/media/preservation/authority decision are mandatory; passing
Stage1 or Stage3/A does not promote automatically. Prefer the separately engineered
noninteractive diagnostic route if a forced cutoff is unacceptable.

No stage grants JARVIS installation/startup, broker/executor/provider/database
work, Gate6K, production, another VM, new credentials/ACLs or V3 authority.
