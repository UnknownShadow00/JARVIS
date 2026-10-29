# Minimal proposed verification — no target mount or boot

Status: read-only procedure proposed, **not executed**. Current authorization is Nexus analysis and planning only. Use only the existing trusted VM164 root console after separate approval for live read-only collection. No network, package installation, guest agent, mount, loop device, chroot or service/lifecycle change is required. If a tool is absent, stop and report it; do not install tools.

This verifies installer evidence and static boot prerequisites. It cannot certify actual successful boot. Preserve current console evidence externally before interaction. Every diagnostic process changes some volatile memory; none is a RAM acquisition or byte-for-byte preservation of RAM. If a memory image is required, obtain a separately approved acquisition plan first; do not trigger a snapshot, pause, dump or shutdown here.

## 1. Confirm the existing console and target, then make one small evidence query

Read-only identity/state precheck:

```bash
date -u --iso-8601=seconds
cat /sys/class/dmi/id/product_uuid /proc/sys/kernel/random/boot_id
lsblk --bytes --paths --output NAME,PKNAME,MAJ:MIN,TYPE,SIZE,SERIAL,FSTYPE,MOUNTPOINTS /dev/sda
findmnt --output SOURCE,TARGET,FSTYPE,MAJ:MIN
command -v debugfs
```

Require VM UUID `faeb1db8-0df9-482d-b3e4-f6ccc1602193`, current recorded boot ID `c93413f7-41cb-4e50-a412-e882ad09fed0`, `/dev/sda` hardware serial `g6k164-12821f6b54a2`, exact disk bytes `68719476736`, and the recorded sda1 BIOS/sda2 ext4 topology. Stop on disagreement, a mounted target, an active writer, changing observations or incomplete inspection. A mount table from one namespace is not a global proof of no writer; use already authorized process/namespace evidence if there is doubt. Do not try to unmount, stop or freeze anything.

**Exact next target-evidence command:**

```bash
debugfs -R 'ls -l /var/log/installer' /dev/sda2
```

`debugfs` opens the filesystem read-only when `-w` is omitted. This command does not mount it or replay its journal. Use only the explicit read requests shown; do not enter an interactive debug session or use checksum-bypass/repair options. Check stderr as well as stdout: missing files or internal errors must not be treated as successful inspection merely because the program exits zero. The default read-only behavior is documented in the [e2fsprogs debugfs manual](https://man7.org/linux/man-pages/man8/debugfs.8.html).

If the filesystem indicates journal recovery is needed, this non-replaying view can omit committed-but-uncheckpointed changes. Treat missing/inconsistent data as inconclusive; do not mount, replay, clear flags or repair it to obtain a cleaner view. A forensic reconstruction would require a separately approved evidence-copy workflow.

Record the directory entries, sizes and times. A saved `installer-journal.txt`, curtin log and Subiquity logs justify the next small reads. If the directory is missing, stop and report that result; it does not prove installation failed, but the completion-path evidence is absent.

## 2. Read only the completion evidence

```bash
debugfs -R 'cat /var/log/g6k-install-origin.json' /dev/sda2
debugfs -R 'cat /var/log/installer/curtin-install.log' /dev/sda2
debugfs -R 'cat /var/log/installer/installer-journal.txt' /dev/sda2
```

Use the listed exact filenames for additional Subiquity server logs; filenames can vary by PID/revision. If a file is a symlink, inspect it with `debugfs -R 'stat PATH'` and resolve its target within the image rather than assuming `cat` dereferences it. Keep output restricted: installer journals can contain sensitive material. Arrange an approved bounded console transcript/export rather than filling the live environment with a full dump. Do not discard stderr, suppress missing-file errors, or interpret a truncated transcript as the complete log. Do not read credential stores.

Check, in order:

1. First-run timestamps/config/disk mapping, any original early-guard PASS, partitioning/mkfs, extraction and curthooks/bootloader success.
2. Successful postinstall and the late-guard success line, then final Subiquity completion/DONE and log-copy path. Distinguish per-invocation curtin success from final installer completion; inspect following errors and chronology.
3. Origin JSON is complete and binds the expected UUID and hardware serial, ext4 target, nonempty machine ID and distinct planned role IDs. It reports guest boot validation and qualification **NOT_RUN**, as expected.
4. Compare the saved log dates to 04:02–04:04 and the current 06:22 service. Do not merge different boots or treat the copied installer journal as a target-OS boot journal. Seek the first boot's ID where available; do not invent one.

If a complete, first-run-bound installer record is found, classify it as evidence of installation completion. Missing/truncated reports, contradictory stage results or a late failure leave completion unproved. A clean ext4 state, a directory tree or a single successful curtin line cannot settle it.

## 3. Inspect static boot prerequisites only if step 2 warrants it

Small, read-only checks:

```bash
dumpe2fs -h /dev/sda2
debugfs -R 'cat /usr/lib/os-release' /dev/sda2
debugfs -R 'cat /etc/fstab' /dev/sda2
debugfs -R 'ls -l /boot' /dev/sda2
debugfs -R 'ls -l /boot/grub' /dev/sda2
debugfs -R 'cat /boot/grub/grub.cfg' /dev/sda2
debugfs -R 'stat /sbin/init' /dev/sda2
debugfs -R 'stat /usr/lib/systemd/systemd' /dev/sda2
debugfs -R 'ls -l /usr/lib/modules' /dev/sda2
debugfs -R 'stat /var/lib/dpkg/status' /dev/sda2
debugfs -R 'ls -l /var/lib/dpkg/updates' /dev/sda2
debugfs -R 'ls -l /var/log/journal' /dev/sda2
dd if=/dev/sda bs=512 count=1 status=none | od -Ax -tx1z
```

Correlate root filesystem UUID from the ext4 header with fstab and GRUB root/search entries. It is **not** the DMI VM UUID or the GPT disk identifier. Verify nonempty matching kernel/initrd and module-version paths referenced in GRUB; resolve symlinks through `stat`. Review package configuration status and any pending dpkg updates if installer logs indicate interruption; do not run dpkg/apt/chroot on the target. Presence of a package database is not a package-integrity check. Compare installed machine ID with the origin report if necessary, without invoking the setup tool.

For this recorded SeaBIOS/GPT layout, an ext4 root and a BIOS boot partition are necessary but insufficient. Seek successful BIOS GRUB installation to the **whole disk** in curthooks logs, valid grub.cfg references, BIOS platform modules and evidence of embedded core-image setup. The first 512-byte read is supporting evidence only: `55 aa` also exists in a protective MBR and is **not bootloader proof**. Nonzero BIOS-partition bytes alone are also insufficient. A full sector-level GRUB-chain verification should be a subsequent read-only analysis of approved captured ranges, not improvised repair or `grub-install`.

If target persistent journal files exist, they may provide additional boot IDs. Do not use `journalctl --image`, guestfish, loop mappings or a mount to inspect them. A separately approved, bounded `debugfs dump` can copy selected journal files **out** to verified `/run` tmpfs for `journalctl --file`; that is a later collection step, not needed for the first query. Do not confuse `dump` output paths with writes into the target. Target journal absence is normal for some never-booted installations.

Permitted conclusion after favorable evidence: **“installer completion supported; static boot prerequisites consistent; actual target boot unverified.”** Full installed-file integrity, successful boot and Gate 6K readiness are not certified by this minimal procedure.

## 4. Recover shutdown chronology without changing the VM

At the current VM164 console, the smallest journal inventory is:

```bash
journalctl --utc --list-boots --no-pager
```

This only lists boots retained in the accessible journals. A fresh RAM-backed installer boot may show only the current boot; that is not contrary evidence. Do not blindly use `journalctl -b -1` and assume it is the 04:02 installer. [systemd documents](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) the boot-list and external-journal selection behavior.

Separately authorize read-only **VM164-specific** history on the trusted Proxmox console if raw historical task logs have not already been retained:

```bash
pvenode task list --vmid 164 --source all --limit 100
```

If the relevant period is not covered, paginate the list using the documented start/limit options rather than interpreting absence as no event. Inspect `pvenode task log` for the exact VM164 UPIDs returned, especially both starts and intervening shutdown/stop tasks. Proxmox's [official command synopsis](https://github.com/proxmox/pve-docs/blob/master/generated/pvenode.1-synopsis.adoc) documents these read-only queries. A successful `qmshutdown` task would support an operator-requested shutdown; guest-initiated poweroff may require host journal/QEMU exit evidence and may lack such a task. A second start does not identify the preceding exit as clean or installation-driven.

Before any future raw content acquisition, retain backing metadata without opening it for content:

```bash
stat --printf='device=%d inode=%i bytes=%s atime=%x mtime=%y ctime=%z\n' /mnt/downloads/images/164/vm-164-disk-0.raw
```

Require device `66305`, inode `13107209` and size `68719476736`; compare host metadata with the supplied record. Record atime too: content reads of a host backing file can affect its access time. The proposed guest filesystem inspection avoids target filesystem atime updates because it never mounts the filesystem, but it is not a promise that every host metadata field or RAM byte remains unchanged. Do not open a running raw disk with tools that repair, lock for writes, convert or create snapshots. Do not use the whole raw file as if it starts at the ext4 partition offset.

Seek host VM164 events between 04:02 and 06:23, correlate task UPIDs/QEMU exits with saved installer chronology, and distinguish poweroff request from completion. Keep unrelated VM and production data out of exports. A clean filesystem flag is corroboration only, not evidence of complete installation or a clean whole-VM shutdown.

Stop after evidence review. Any first-target boot, lifecycle change, disk replacement, repair, boot-order change or qualification remains separately unauthorized.
