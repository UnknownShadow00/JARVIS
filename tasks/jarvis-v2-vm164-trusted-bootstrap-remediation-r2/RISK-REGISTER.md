# r2 risk register — root bootstrap remains NO-GO

Status meanings: an offline software regression PASS is not physical qualification.
The old packets/ISO remain unchanged, with their documented hazards. This packet
is a separately pinned candidate; it does not amend the authority of old approvals.

| ID / severity | r1 hazard | r2 change and offline evidence | Residual blocker / required supervised evidence |
|---|---|---|---|
| H1 / high in legacy path | Live media change may fail or become pending with hotplug0 | Remove the running eject transition. Keep the new CD read-only throughout the diagnostic; unchanged probe reports optical_media_present=true. New state gate requires running/attached -> stopped/attached -> stopped/empty. Tests reject a direct running detach, pending changes, old/wrong ISO, and relabelled media. | Legacy eject feasibility remains UNKNOWN and is not needed by r2. A stopped-state media swap/detach still needs explicit approval, fresh effective readbacks and actual content checks. Attached diagnostic is NEVER installation-ready; original installer still rejects it in a new regression test. |
| H2 / high, OPEN | Passwordless root exists before a human arms the guest timer; timer merely requests graceful poweroff | Require independent HOST-owned enforcement armed and inspected while the VM is stopped, before any start. Fixed host boot/target/config/session binding; suspend-inclusive clock; no extension or automatic restart. Policy/negative replay implemented. No guest timer is accepted as its substitute. | No deployed/version-bound host runtime backend or real qualification exists. HOST-FENCE-CONTRACT.json deliberately has runtime_driver=null, qualified=false. Every local receipt sets root_boot_go=false. Need separately reviewed implementation, protected host custody, exact installed-version API/timer behavior, prior-to-start worker/deadline observations, and actual termination/failure trials WITHOUT root first. |
| H3 / high until physical qualification | Missing/corrupt state, facts/snapshot failure can bypass the closer's pre-try fallback | Target identity is independently checked in a bounded child. For a verified target, state failures, malformed receipts, command errors/timeouts, console hangup, KeyboardInterrupt/SystemExit all proceed through nested cleanup and poweroff attempts. No probe/state prerequisite to submit abort cleanup. Process groups are killed/reaped on child timeouts. | Wrong/unknown identity intentionally causes NO guest mutation; it cannot justify powering off an unverified guest. SIGKILL, OOM, interpreter/manager death and hung kernel cannot execute Python finally. Independent host expiry must remain operational. Real unit masking/cgroup/TTY/stop behavior and actual stopped readback remain unverified. |
| H4 / high until physical qualification | 45-second service deadline is below the composed command budgets | No cleanup sleep. Eight steps, each <=5-second wait plus <=1-second timeout kill/reap:48 seconds nominal maximum. Global60-second work budget, last6 reserved for poweroff. Unit TimeoutStartSec90, TimeoutStopSec5, control-group killing, no restart. Tests cover all-command timeouts, exhausted normal/global budget, interrupt, reap failure and failed poweroff. | Spawn/kernel/manager scheduling and real stop latency are not proven bounded by offline mocks. Unit resource/timeout settings need actual compatibility tests. Host escalation is scheduled independently at +600 seconds; that request is NOT proof of access expiry. Qualification requires actual stopped proof by +630 seconds, or FENCE FAILURE. This is an acceptance criterion, not an established guarantee. |

Additional material risks:

- **Preservation versus hard expiry:** a reliable cutoff must not depend solely
  on a cooperative guest. Emergency VM164 hard termination may lose in-flight
  Ubuntu journal/filesystem writes. It needs an explicit preservation/recovery
  decision and narrow forced-termination authority. Neither authority nor a
  guarantee of disk integrity is inferred from this task. If unacceptable, keep
  stopped and engineer a noninteractive/alternative boot path separately.
- **Unknown target during cleanup:** fail closed against acting on another guest.
  Host enforcement must bind the already-admitted VM164 execution, reject VMID
  reuse/config drift and never retarget another VM. The runtime implementation
  and its identity-loss behavior are absent, so this remains a blocker.
- **Operator report is not live origin:** current report is stopped, order=scsi0,
  old approved r4 ISO attached. Do not repeat the already-reported boot correction.
  Revalidate effective/current view, pending schema, exact UUID/disk/ISO and
  generation immediately before any future action. Neither timestamps nor a
  fabricated active-worker assertion can authenticate origin offline.
- **Guest root is trusted, not confined:** a root user can disable guest timers,
  move children/cgroups or alter files. A host fence outside its authority limits
  exposure only if actually implemented/qualified. Console custody, no NIC/agent
  and private disk/mount boundaries remain mandatory, never relaxed.
- **New candidate custody:** the new ISO is unapproved/unattached. Execute no old
  BOOT.PY and never mix its r4 cleanup/guest-timer procedure with r2. Image size
  and J164BOOT label alone do not identify either ISO; full hashes are mandatory.
- **Non-persistence evidence:** new code writes only exclusive /run evidence and
  runtime manager state; no password/key/SSH/network/GRUB edit API exists. It does
  not compare all persistent files or prove a clean guest. Ordinary OS boots and
  abrupt termination can write the disk. A later clean boot and trusted stopped
  observations are required; a fresh protected-install boot-id is separate.
- **Evidence versus root duration:** capture pages early, close promptly, decode
  after shutdown. Never extend a lease to save evidence. Lost or bad capture is
  incomplete; no automatic retry or reuse of the vanished /run/boot-id.

No row claims that a real PVE, QEMU, systemd or hardware behavior has passed here.
See GO-NO-GO.md for the exact gate separation and AUTHORIZATION-REQUEST.md for
future scope. Current recommendation: **NO-GO for a new root bootstrap**.
