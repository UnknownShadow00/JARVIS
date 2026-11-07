# Severity-ranked engineering findings

This is a source review and synthetic adversarial audit, not an independent
external audit or a live qualification. No critical exploit was demonstrated.
High severity means a privileged-access or preservation boundary can be left
unproved; medium means an important guard/evidence assumption needs correction;
low means a bounded assurance/documentation limitation. IDs identify findings,
not completed fixes. Every pinned file remains unchanged.

## High severity

### H1 — Live ejection is an unqualified dependency with hotplug disabled

**Verified local/code facts:** OPERATOR-PROCEDURE steps 5/6 require staging into
`/run`, unmounting the CD, changing `ide2` to empty while running, no pending
configuration, and no guest optical media before the probe. `host_guard.py`
requires `hotplug: 0`; `BOOT.PY.probe()` refuses a nonzero `sr*` size. No test
performs a real PVE/QEMU drive-medium change. The unchanged lab probe also
reports media presence, so relaxing just the wrapper is not a safe completion.

**Hypothesis requiring supervision:** this exact PVE/QEMU/drive combination may
apply the change live, reject it, or store only a pending change. The repository
does not establish which. A successful command is insufficient evidence of
effective ejection. `umount` releases a filesystem, not the host attachment.
There is no verified completion path if physical guest media remains present.

**Consequence/stop:** do not run the probe or claim completion on a pending-only
or still-present medium. Preserve evidence and close through the already approved
supervised failure procedure. No automatic hotplug change, QMP workaround or
pending-change clearance. See FAILURE-ANALYSIS for recovery and alternatives.

### H2 — The root shell exists before the watchdog; arming is not a hard cutoff

**Code-derived:** the GRUB flags request a passwordless root debug shell on tty1
during normal systemd startup. UUID/disk/size/PID1/TTY checks and human entry occur
before `systemd-run` arms the 20-minute timer. If a check or timer creation fails,
there is no armed guest watchdog. The packet acknowledges this but describes a
bounded root lifetime too broadly. A 60-minute supervised authorization does not
itself enforce a kernel or hypervisor cutoff.

`BOOT.PY.facts()` checks only `systemctl is-active ...timer`. It does not verify
the timer's monotonic deadline, remaining time, trigger service's exact poweroff
command, failed activation, or prior firing. A boolean active timer is weaker
than proof of the intended watchdog. A graceful poweroff request can also fail
to finish. No actual VM watchdog execution or shutdown is established.

**Operational hazard:** an interruption, console loss, slow input or hung system
can leave root available outside the assumed interval. Root can disable its own
timer; this is a supervised cooperative guard, not confinement of hostile root.

**Next:** before start, operator must accept a documented pre-arming observation
and recovery plan within current scope, or review a newly engineered watchdog
design. Do not invent a guaranteed timeout or unattended recovery. No timer was
armed in this sprint.

### H3 — Cleanup exceptions before `try` bypass its local poweroff fallback

**Code-derived and synthetically reproduced:** `BOOT.PY.close_unit()` reads
`STATE.JSON`, calls `facts()`, checks the boot binding and takes `snapshot()`
**before** entering the `try/finally` that requests poweroff. Missing/corrupt state,
facts refusal, changed session or snapshot I/O failure can exit without any
mask/stop/poweroff request from the closer. New tests reproduce state-read,
facts and snapshot failures with all command calls mocked and absent.

The watchdog may remain a separate fallback if correctly armed and functioning;
the closer's shutdown guarantee does not cover these paths. Top-level exception
handling prints/refuses but does not power off. No root cleanup is thereby
proved. A future helper revision needs regression tests and a new ISO/hash/review;
this sprint deliberately does not repin it.

### H4 — Close-unit deadline is shorter than its composed command budgets

**Code-derived:** `close()` submits a transient oneshot with
`TimeoutStartSec=45s`. Each command has a 20-second subprocess timeout. Pre-cleanup
`facts()` performs three commands; mask/stop/kill/show perform four more, and
successful closure then sleeps ten seconds before poweroff. Even two slow
successful cleanup calls can consume most of 45 seconds; all calls need not fit.
The service manager can terminate the closer before its Python `finally` finishes.
`subprocess.TimeoutExpired` is not in the top-level caught-exception list.

**Synthetic limit:** tests replace commands and sleeps with immediate mocks;
they do not exercise actual service timeout, SIGTERM/KILL or manager job ordering.
**Next:** qualify worst-case behavior and redesign deadlines/failure handling in
a separately reviewed helper revision. Do not increase or extend live timers
ad hoc, and do not promise forced shutdown under the existing authorization.

### H5 — Reported boot state fails preflight; attaching media can change it

**Operator-reported:** diagnostic ISO attached, VM last stopped,
`order=scsi0;ide2`; restoring `order=scsi0` approved but unreported as executed.
**Verified source/synthetic fact:** the official guard rejects that exact boot
shape, even though its existing test used the different shape `order=ide2;scsi0`.

The original attachment template anticipated only an `ide2` change and did not
explicitly anticipate automatic boot-list augmentation. Never weaken the guard
to accept the observed order or assume the approved correction ran. The exact
approved r4 ISO is locally nonboot data, which reduces bootability of that object;
an unexpected or later-replaced bootable ISO in the list remains an unacceptable
alternate boot source. Prior installer incidents make boot-source confusion a
concrete preservation concern. Restore only in the returning supervised session,
then capture fresh stopped/attached evidence and rerun the official guard.

## Medium severity

### M1 — Official media-name validation accepts other hash-shaped images

**Synthetic finding:** passing `local:iso/vm164-trusted-bootstrap-0000000000000000.iso`
as both configured media and `--iso-volume` passes the old guard. Its regex binds
the naming pattern, not the fixed r4 identity. It never reads the actual host
volume's bytes. The procedure's exact-volume/whole-image checks are essential
independent controls; this is not a demonstrated bypass of the full procedure.

The new validator fixes the expected volume, hash and size and requires their
supplied observation to bind the config artifact. These are still assertions;
only supervised host custody and guest whole-device checks establish actual bytes.

### M2 — Missing fields, duplicate disk options and unrecognized devices

**Synthetic findings:** the old guard accepts missing `agent` and `vga` through
defaults, a `scsi0` string containing both correct and conflicting `serial=`
options, and an unchecked `efidisk0` extra device. It does not verify the supplied
VM name. These are unsafe completeness assumptions for adversarial/saved JSON.

The new validator requires explicit fields, exact name/UUID/volume/serial/size,
unique disk-option keys, and a conservative config-key allowlist. Unrecognized
fields refuse; an ordinary field newly emitted by PVE requires offline review,
not removal from the evidence. No real PVE output schema was tested here.

### M3 — Pending schema and effective/current configuration need stronger binding

**Synthetic finding:** old `pending=[{}]` is accepted. Pending items are examined
for markers but their schema/current values/duplicate keys are not validated.
The new validator rejects malformed rows and any field beyond `key/value`, even
`pending:null` or `deleted:0`; unchanged rows must match the current config.

**Code-derived observation:** the bootstrap uses `/config` without explicit
current selection; the reviewed broker transport uses `/config?current=1`.
**Unresolved hypothesis:** default-versus-effective/pending behavior for the
installed PVE version is not established by retained schema/docs. In supervision,
obtain explicit effective/current configuration using supported read-only syntax,
along with status and pending, before interpreting ejection. New envelopes require
the explicit `current=1` endpoint assertion; this does not prove the query ran.

### M4 — Guard hashes/digests do not prove origin, freshness or continued validity

**Code-derived:** the old guard accepts separate supplied files without a clock,
node-origin proof, sequence or cross-step protected baseline. Its output hardcodes
node pve; `not_a_live_check=True` is an important existing limitation. A valid
40-hex config digest is opaque PVE concurrency data, not a recomputed digest of
the saved JSON, a freshness proof or a signature. Config/status/pending calls are
separate observations, not an atomic transaction. Status can change while the
config digest remains the same.

The new validator adds raw-byte SHA256, strict UTC timestamps, a 30-second capture
span, a conservative 120-second latest age, a one-hour history bound, exact source
labels, snapshot links, allowed state edges, protected-field equality and digest
continuity. Tamper/old/new-invalid fixtures refuse. A user can fabricate all those
assertions or omit a later event; neither validator can discover that offline.
Fresh operator recapture is mandatory immediately before each supervised action.

### M5 — Clean boot observations and snapshots do not prove universal non-persistence

**Code-derived:** no persistent kernel-argument setter is present in the new
helper/procedure; GRUB editing is unsaved, runtime masks/units are under `/run`,
and watched public GRUB/account/identity files are compared. Those are sound
controls. Baseline capture occurs after entering the root boot, not before it.
`WATCHED` excludes `/etc/shadow`, `/etc/gshadow`, SSH configuration/key stores,
network configuration and alternative boot/config paths. Root lock is checked
with `passwd -S`, without exporting shadow data. No credential is read here.

Thus a matching snapshot proves only the selected files matched that baseline.
The close receipt computes `unchanged` before stopping the shell; it does not
recompute after cleanup or continuously prevent writes. The normal GRUB line and
locked-login observation are required but cannot prove every service or persistent
credential store is clean. Do not call this comprehensive guest attestation or a
byte-identical disk. A broader trusted baseline/design would need separate review;
do not collect secrets or repair credentials to strengthen this packet.

### M6 — Existing cgroup closure is useful but has unqualified races and scope

**Code-derived:** helper requires systemd/cgroup v2, the expected unit path and
MainPID membership; runtime-masks/stops then requests kill-all, checking inactive
state, MainPID 0, masked-runtime and empty/absent expected cgroup. Old tests cover
residual processes and Restart=always/KillMode=process behavior through mocks.

**Hypotheses:** real unit alias/mask precedence, service stop timing, cgroup path
disappearance, terminal hangup/reopen and child movement remain guest-dependent.
An empty unit cgroup does not prove an arbitrary root-spawned process has not
moved elsewhere. The shell is trusted/supervised; this is not hostile-root escape
prevention. A root prompt disappearing or typing `exit` is never closure proof.

### M7 — RAM delivery and failure recovery cannot silently resume

**Code-derived:** exclusive `/run` staging and probe outputs preserve partials;
all staged bytes disappear at shutdown. Pending-only ejection may leave a stopped
VM with attached/pending media and no staged helper. The success-path guard rejects
pending configurations, so its receipt cannot authorize clearing unexpected
pending changes. A later boot cannot reuse the lost RAM path or previous boot-id.
Keep failure evidence and request a separately reviewed operator recovery plan
when the approved fail-closed path cannot establish the final state. No retries,
new boot mode or pending mutation are implemented in the new validator.

### M8 — Guest root filesystem ancestry is not established by UUID/serial alone

**Code-derived:** the helper checks DMI UUID and sda hardware serial before broader
inspection, requires sda-only among selected disk-name classes and ext4 `/`, and
binds machine/boot identity. These are valuable independent checks. It does not
resolve the mounted root device through sysfs to prove it is a partition of the
original sda; its selected disk-name regex also does not enumerate all dm/md/loop
topologies. The pinned lab probe reports root major/minor and filesystem UUIDs,
but the later target predicate compares supplied bindings rather than proving
block ancestry itself. An ext4 root plus a correct separately present disk is
weaker than an independently established installed-root-to-original-disk binding.

No wrong-root exploit was demonstrated. Trusted fresh host configuration and
independently reviewed guest root-device/UUID/native facts remain essential
before installation. Do not synthesize a root binding from the expected serial,
mount raw disks, or run an old mutating disk guard to fill this gap.

## Low severity / remaining assurance work

### L1 — Capture/hash continuity still depends on trusted external custody

The indexed base64 decoder checks order, duplicates, total SHA256, UUID/serial/
size and media absence. This is strong transcription detection. It does not
authenticate origin or require an independently supplied expected boot-id; later
binding must compare the decoded boot-id to independent session evidence. A root
report can lie. Page display does not itself revalidate the guest session; retain
the separately captured hash and all screenshots. Same-UID local seals are not
WORM or signatures. Missing pages, poweroff-before-capture or mismatched hashes
stay incomplete. No secret-bearing raw console/config dump is needed in chat.

### L2 — One-time GRUB interception and guest compatibility remain empirical

The three retained generator tests used the preparation host's binary, not VM164's
system manager. They do not prove reachable GRUB/noVNC timing, installed tty1
support, absence of terminal competition, CPython availability or actual clean
return. A missed single interception is a stop, not permission for automated
key spam, another boot, rescue, serial or a persistent GRUB edit. Stage is not
allowed until whole-device hash/size and helper hash have matched; Python
`noexec` mount flags do not prevent an interpreter reading an unverified script.

### L3 — Offline PASS cannot discharge live, install or production gates

Original tests still pass with the gaps above. New tests deliberately preserve
that distinction. Neither current local inventory checks, 31 verified wheels,
45 SBOM components nor synthetic transitions qualify actual multi-UID, native
runtime, mount/network isolation, service custody or power-loss behavior. See
RC1-OFFLINE-REVIEW for the installation blockers. No readiness marker or real
executor/broker activation was created.

## Requested review coverage

| Requested area | Findings / evidence |
|---|---|
| 1. Automatic boot-order change | H5; old and new exact-shape negative tests |
| 2. Attached ISO content and exact volume | M1; fixed-volume fixtures; local ISO inspection; operator custody still required |
| 3. Hotplug 0 and pending-only ejection | H1, M3; pending fixture; supervised criteria in FAILURE-ANALYSIS |
| 4. Guest cannot physically eject mounted CD | H1, M7; fail-closed flow and no improvised workaround |
| 5. Unexpected CD boot source | H5; unknown ISO/extra boot-device tests; historical installer timeline |
| 6. One-time GRUB interception | L2; single-attempt supervised stop |
| 7. tty1 root debug shell | H2, M6; root lock is not shell containment |
| 8. Pre-watchdog exposure | H2; no guaranteed pre-arming cutoff |
| 9. Watchdog/cleanup lifetime | H2–H4, M6; three new pre-try failure reproductions |
| 10. Nonpersistent kernel command line | M5, L2; unsaved edit, watched-file scope and required normal-entry evidence |
| 11. UUID/disk identity | M2, M8; early identity guards, wrong-target tests, root ancestry limit |
| 12. Verify before payload execution | M1, L2; whole-medium/helper/probe verification order |
| 13. Accounts/SSH/networking preservation | M5; no edits, no hidden comprehensive-attestation claim |
| 14. Pending operations | M3; strict pending schema and negative fixtures |
| 15. Evidence/hash/failure recovery | M4, M7, L1; original bytes, chain, RAM loss and preserve-only failures |
| 16. Stale saved readbacks | M4; explicit offline source and UTC clock/age tests |
| 17. Offline versus live qualification | L3; false authority/live/Gate6K receipt flags and separate operator gates |
