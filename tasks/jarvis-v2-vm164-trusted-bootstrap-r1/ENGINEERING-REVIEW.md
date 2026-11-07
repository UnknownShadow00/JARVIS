# Security and preservation review

Verdict: suitable to request the narrowly scoped supervised **preflight** operation;
not an executed/qualified VM bootstrap, deployment or Gate6K pass. Review was a
separate source/negative-path pass in this preparation session, not an independent
external audit. All service/power commands in fixture tests were mocked. The real
generator was exercised only inside an unprivileged network-isolated container,
with no running system manager and no VM access.

## Evidence and design decisions

The sealed Unified RC1 and lab-readiness evidence verifier passed again, including
315 source files,31 wheels,2444 install files,18582 historical RC1 evidence files
and177460 prior files. No sealed predecessor was edited. Original revision:
e9b4734740070b9e7c990735e43801e592c114c6. Pinned lab_package.py is byte-for-byte
unchanged; no installer/broker authority is added to it. New helpers have only
Python standard-library imports. No new package installation/dependency change.

The operator's latest hardware/installed-boot report supersedes earlier boot
uncertainty. Those facts are explicitly operator-reported, not freshly observed
here. Old failed manual GRUB/serial experiments are not replayed. Current locked
passwords make ordinary/rescue administrator login unavailable. A transient VGA
systemd debug shell provides one passwordless supervised root boot while retaining
the installed disk/root/systemd path. Explicit tty1 avoids tty9 switching and
serial ambiguity; the matching getty mask prevents competition for the console.

Primary implementation references, reviewed2026-11-06:

- [systemd v259 debug generator](https://raw.githubusercontent.com/systemd/systemd/v259/src/debug-generator/debug-generator.c): tty argument parsing, generated TTYPath/drop-in and runtime masks.
- [systemd v259 debug shell unit](https://raw.githubusercontent.com/systemd/systemd/v259/units/debug-shell.service.in): Restart=always, KillMode=process and terminal lifecycle.
- [systemd-debug-generator manual](https://www.freedesktop.org/software/systemd/man/latest/systemd-debug-generator.html): supported one-boot parameters (manual retrieval was intermittent; pinned source plus actual local generator tests are the reproducible basis).

The local installed generator yields tty1, clears the default tty9 existence
condition, masks getty@tty1, and pulls debug-shell into default.target. With no
debug arguments it generates no debug-shell activation; boolean1 selects its
normal defaulttty9. The tested binary's hash and exact output are retained under
evidence/generator-tests. This does not prove the installed VM's binary/version;
the future helper requires actual tty1/unit properties and normal systemd PID1.

## Boundaries tested/reviewed

| Boundary | Control/evidence | Practical limit |
|---|---|---|
| Wrong VM/disk | DMI UUID and hardware serial before broader commands; fixed64GiB; offline host guard binds exact disk/UUID/digest/state | Trusted operator must bind readback origin/freshness; guest JSON is unsigned |
| Extra channels | Host guard refuses NIC/agent/passthrough/extra disks/pending config; guest requires lo and sda only | No live configuration read was performed in preparation |
| Untrusted transfer | Whole-ISO hash/size before mount; helper hash before execution; independent bounded ISO reader, exact3-file manifest; unchanged probe hash | Requires trusted host upload/custody and the supervised console |
| Filesystem writes/races | /run tmpfs, exclusive0700 directory and0600 O_EXCL/O_NOFOLLOW files; reject symlinks/hardlinks/FIFO/oversize; preserve partial stage | Mounted CD/root-only /run parents are trust assumptions checked before staging; no adversarial multi-UID guest race qualification claimed |
| Duplicate execution | Existing RAM/output paths refuse overwrite; same evidence pages may be re-displayed | No resume/automatic cleanup or rerun after a failed stage |
| Root lifetime | Supervised console,20-minute runtime watchdog, independent closer, runtime mask/stop, kill remaining processes, verify MainPID/state/cgroup | Actual guest shutdown/terminal behavior requires supervised execution |
| Cleanup accuracy | Review found Restart=always and KillMode=process; helper requires known cgroupv2/system.slice binding before cleanup and checks empty cgroup | systemctl exit alone is insufficient; inability to verify is a failed closure |
| Persistent changes | No passwd/usermod/SSH/grub writes or enable; root remains locked; compare public boot/account/identity hashes | Normal OS journals/boot accounting can change; no secret shadow content exported, no byte-identical disk claim |
| Evidence loss/forgery | Raw probe retained in RAM, indexed short base64 pages, strict local reconstruction and whole-record hash, host/console observations retained independently | RAM evidence vanishes at shutdown; watchdog never extended to save capture; incomplete capture stays incomplete |
| Real execution | Media contains no JARVIS application; helper only stages probe/runtime cleanup; no broker/provider/database or install entry point | Operator approval must remain within exact commands |
| Clean return | Runtime closure receipt, unsaved GRUB edit, subsequent default-entry/login observation, final stopped/empty host checks | No authenticated clean-boot service inspection exists; do not fabricate one |

## Findings resolved during preparation

1. Exiting the stock shell would restart root. Replaced that cleanup assumption
   with a distinct transient close unit and runtime mask, with failure shutdown.
2. KillMode=process can leave children. Added kill-all and cgroup emptiness checks;
   require the exact active cgroupv2 path before claiming closure. Residual-process
   and active-MainPID fixtures prove no false pass.
3. A delivery ISO left attached would contaminate the pinned preflight's optical-
   absence fact. Stage exclusively in RAM, unmount, eject media and verify live
   absence before running the probe. No flag added to waive the original probe.
4. Long raw JSON would be error-prone on VGA. Added bounded48-character base64
   payload rows, page indices, strict sequence/hash validation and exclusive local
   reconstruction; missing/duplicate/transposed rows fail.
5. Boot-id is per boot. Explicitly forbid reuse of the temporary probe's boot-id
   for a later protected installation; actual later binding remains required.
6. Initial test loader did not accept uppercase .PY. Fixed the test harness's
   explicit source loader; initial failure is retained. No guest code ran.
7. Cleanup must tolerate the debug shell's terminal hangup. Reopen the exact VGA
   character device for receipts; nested finally still requests poweroff if even
   that output fails. The console-error fixture verifies this failure path. The
   cgroup view accepts normal PID1 init.scope placement and requires the active
   shell MainPID to be present in its exact cgroup before trusting that path.

## Remaining execution blockers/limits

Approval is absent; nothing may yet touch PVE/VM164, power, media, console or
credentials. Existing observer failure is retained unchanged; no token repair.
Fresh trusted host binding, reachable VGA GRUB editor, installed python3.14,
actual generator/unit compatibility, same-boot media ejection, successful probe
capture, and true closure/clean-login evidence are unverified. Each is a stop
condition if unmet. There is no automatic serial, rescue, installer or persistent-
password fallback. Fresh probe results may expose real dependency/isolation/
resource shortfalls; do not fix them within this bootstrap authorization.

Existing installation/runtime/native-hash/identity assumptions remain blockers
until measured. The privileged worker's multi-UID protections and Gate6K tests
remain unqualified. No production VM162, preserved VM163, AI-server, real model,
real executor, database migration or V3 action belongs to this procedure.
