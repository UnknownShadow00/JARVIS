# VM164 timeline update — earlier installation is now the leading explanation

The most likely sequence is that the **04:02 boot created the target filesystem and performed some or all of the installation**, then a separate **06:22 start booted the still-first installer ISO**. The current automatic r4 guard encountered partitions already created in the earlier run. This explains the apparent disk mutation without requiring the current failing early command to have allowed storage writes.

**Installation completion, orderly shutdown and actual target bootability remain unestablished.** The new evidence supports an earlier installation attempt, not a successful installation. Read the target's retained installer evidence before considering a new disk or another install. The previous packet's new-blank-disk recommendation was conditional on an unresolved mutation; this update supersedes that recommendation as the immediate recovery direction. Preserve the existing disk and investigate whether it already contains a complete OS. Neither replacement nor in-place installation is currently justified or authorized.

Scope: `workspace-write` for new Nexus-only analysis/evidence documents. No live VM/PVE/VM163/production/AI access, target mount, disk operation, ISO creation, boot change, lifecycle action or qualification occurred. Prior sealed packets remain unchanged. [Operator timeline](evidence/operator-timeline.json) records supplied facts separately from inference; raw host logs and headers were not supplied to this task.

| UTC, 2026-10-28 | Trusted evidence supplied | Supported interpretation |
|---|---|---|
| 04:02:59 | VM164 `qmstart` successful | Earlier VM start; inspect task log to bind the actual QEMU launch |
| 04:03:41 | ext4 filesystem creation time | Filesystem creation 42 seconds after that start, subject to guest clock accuracy |
| 04:04:17 | ext4 last-write time and backing-file mtime/ctime | Further filesystem/backing-file activity 36 seconds after creation, 78 seconds after start |
| 06:22:37 | VM164 started again | Separate later start, 2 h 19 m 38 s after the first; preceding stop time/cause not supplied |
| 06:22:48 | Current Subiquity service started | Current installer service began 11 seconds after later start |
| Current | ISO first in boot order; automatic guard refuses partition-inherited identity | Consistent with re-entering installation media against the previously initialized disk |

Backing identity supplied: `/mnt/downloads/images/164/vm-164-disk-0.raw`, inode **13107209**, device **66305** (decimal), size **68,719,476,736 bytes**. This makes the correlation more specific than matching only `/dev/sda`. It is not a content hash or proof of exclusive access throughout the interval. ctime is inode status-change time, **not file creation time**. ext4 times are mutable guest filesystem metadata; host mtime/ctime are not a complete write audit. Their agreement supports the sequence but does not prove the last target write or a clean shutdown. The supplied timestamps are treated as UTC; compare raw values and clock alignment before precise attribution.

## Completion and shutdown evidence available in the retained code

The original guard passes on a correctly identified virgin disk and would not see inherited partition identifiers until partitions exist. In the pinned normal startup path it must finish before the same instance starts normal installation controllers. A later boot has fresh live `/run` state, so the current automatic failure does not require a stale-success stamp or a same-instance concurrency failure. An earlier PASS and matching first-boot media/config are still not established by the supplied timestamps.

Pinned `install-controller.py:425–466` orders partitioning (including mkfs), extraction and curthooks. `:661–680` then orders postinstall, late commands and `DONE`. Thus ext4 could exist even if extraction, bootloader installation, postinstall or the late guard failed. Curtin emits success for **each explicitly selected stage invocation**, including the initial empty-stage invocation. A single “installation finished”/curtin success line is not sufficient; correlate all stage boundaries and final Subiquity state.

The retained r4 configuration specifies **`shutdown: poweroff`**. The newly extracted exact [shutdown controller](evidence/shutdown-controller.py), from hash-verified Subiquity snap 7403, is decisive for choosing evidence:

- `:71–75`: normal log copying waits for `Install.install_task` and the late-command completion event.
- `:108–127`: it copies `/var/log/installer/` into the target and writes `/var/log/installer/installer-journal.txt` using the **installer boot's** `journalctl -b`.
- `:77–83` and `:132–143`: normal noninteractive shutdown follows the ready event only in `DONE`, then invokes the configured poweroff/reboot action.

The copied journal is especially useful evidence that the normal workflow reached the completion/log-copy path when its contents and timestamps match the first run. A file name alone is insufficient, and copying/logging failures can leave it absent, empty or truncated. It is captured **before** shutdown, so absence of the eventual poweroff message in this file is expected and does not disprove a shutdown. The text journal's default format may not expose a boot ID; obtain an ID from retained structured journals or corroborating logs if available.

The unchanged late guard writes `/var/log/g6k-install-origin.json` after its identity, target, cloud sentinel, role-account and machine-ID operations, then prints `INSTALLER_TARGET_GUARD_COMPLETE; GUEST_PREFLIGHT_AND_BOOT_REVIEW_REQUIRED`. A valid, correctly bound report plus the matching success line supports reaching the late-command stage. It is an unsigned installation-origin report, **not** qualification approval, boot proof or a substitute for final installer status. Do not execute this guard again to inspect it: it performs writes.

## What is and is not established

| Question | Current finding | Required read-only evidence |
|---|---|---|
| Did the earlier run create ext4? | Strongly supported by creation time closely following its start, correlated with backing-file metadata | First-run partitioning/mkfs log tied to disk/config and clocks |
| Did it extract/configure Ubuntu? | Unknown | Saved extraction, curthooks and postinstall results plus actual OS files |
| Did installation finish? | Unknown | Final Subiquity/late-command completion, matching origin report and completion-path log copy; review later errors |
| Did it power off normally? | Unknown; configured poweroff makes it plausible | Guest shutdown record correlated with host QEMU exit/stop event and timing; task log alone may omit guest-initiated poweroff |
| Was there a stop before the later start? | Likely if this was a real second QEMU launch | Both `qmstart` UPID logs, intervening host VM164 events; exact stop time/cause remains open |
| Are previous boot records recoverable? | Possible | Copied installer journal/logs; current live journal only if it retained older boots; persistent target journals only if present |
| Is the target complete and bootable? | Unknown | Installer completion plus static root, package, kernel/initrd/modules, fstab and BIOS-GRUB checks |
| Has the installed OS booted successfully? | Not established | A real target boot is forbidden here; no static inspection can prove future boot success |

A fresh live installer commonly loses the previous boot's RAM journal. `journalctl --list-boots` in the current live environment lists only retained journal boots, not every historical VM start. An empty previous-boot result does not disprove the 04:02 run. Conversely, `/var/log/installer/installer-journal.txt` records the installer environment, not proof that the installed OS booted. A never-booted target can legitimately lack persistent system journals.

## Next safe action

Maintain the preservation hold. The highest-value next target check is a read-only directory listing of retained installer logs through `debugfs`, without mounting the filesystem. [The exact minimal procedure](READ-ONLY-PLAN.md) starts with identity/state confirmation, then lists logs, reads the origin report and selected saved logs, and proceeds to static boot prerequisites only if needed. It contains separate host-history queries for shutdown attribution.

This is a **plan only** under the present GO. Live read-only commands need the operator's separate authorization. Do not wipe, replace, repair, resume installation or alter boot order to investigate. If evidence eventually supports completion and a plausible boot chain, the next decision would be a separately approved preservation and first-target-boot plan, not an installer retry. Keep VM164 running, its disk attached and untouched, and VM163 stopped; no RAM snapshot, pause or shutdown is authorized.
