# One supervised VM164 bootstrap — operator procedure, NOT executed

Status: preparation only. A separate explicit approval of AUTHORIZATION-REQUEST.md
is required before step 2 or any VM/PVE action. Use this single VGA/noVNC procedure;
retain evidence on the trusted operator workstation in a new exclusive execution
folder, never in a sealed predecessor packet. Window: at most 60 minutes; root
watchdog: 20 minutes after arming. Final VM state: stopped, empty existing CD drive,
original disk-only boot and locked passwords. No persistent administrator login is
created. Ordinary Ubuntu boots/shutdowns can update their own journal and boot
accounting; this procedure does not claim a bit-identical disk afterward.

## 1. Verify the packet locally

On Nexus, from the JARVIS project root, before requesting authorization:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/verify_packet.py
```

The ONLY delivery image is:

```text
tasks/jarvis-v2-vm164-trusted-bootstrap-r1/delivery-r4/vm164-trusted-bootstrap-fd91b8b07243565e.iso
bytes: 196608
SHA256: fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154
PVE volume after approved upload: local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso
BOOT.PY SHA256: ac90206dc70f8473fe3b0bfa2e3e9d1be7e3471af4090637cb715d96e0aaf6bb
LABPKG.PY SHA256: 08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a
```

The ISO is a nonboot data image, label J164BOOT, with exactly BOOT.PY, LABPKG.PY
and SHA256.SUM. It contains no installer, JARVIS application, credentials, kernel,
initrd, cloud-init data or autorun mechanism. Historical media-build-1 through 8, delivery/, delivery-final/ and delivery-r3/ are
superseded local engineering evidence; never transfer them. Delivery is the small
probe-only image, not the 23.5 MB future installation bundle.

## 2. Establish trusted host identity and preserve the initial state

Only after approval, use the existing trusted **node pve administrator console**.
Do not create/replace a token, use the serial broker or broaden the observer token.
In the Proxmox UI verify the selected node pve / VM164 and record a UTC timestamp.
From that console acquire fresh minimized readbacks immediately before each
transition (use new local/operator files for each step):

```sh
pvesh get /nodes/pve/qemu/164/config --output-format json
pvesh get /nodes/pve/qemu/164/status/current --output-format json
pvesh get /nodes/pve/qemu/164/pending --output-format json
```

Save each JSON result through the existing trusted operator evidence channel as
config.json, status.json, pending.json in an exclusive per-step directory. Do not
paste raw host configuration or unrelated VM inventory into chat. Copy the files
to Nexus for the **offline** guard (or run the reviewed guard on the trusted
workstation; no host Python/package installation is required):

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/host_guard.py \
  --config /NEW-STEP/config.json --status /NEW-STEP/status.json \
  --pending /NEW-STEP/pending.json --phase empty --expect-status running \
  --iso-volume local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso \
  --out /NEW-STEP/guard.json
```

Set `--expect-status stopped` if the first observation is already stopped. Replace
/NEW-STEP with a new exclusive evidence directory. The guard does no network or
VM operation. Its receipt hashes the supplied readbacks; a trusted operator must
bind their origin/node, timestamp and freshness. Do not use a fixture as readback.
It requires UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193; scsi0 volume
`downloads:164/vm-164-disk-0.raw`, serial `g6k164-12821f6b54a2`, size64G; no NIC,
agent, extra disk, passthrough/shared/command channel or pending config; existing
VGA std and serial0 socket; disk-only boot; protection1, hotplug0, onboot0;
>=4 vCPU, >=6000 MiB fixed RAM. A mismatch requires a revised review, not repair.
VM162, VM163 and the AI server are not targets and must not be queried/changed.

If running, select **Shutdown** (ACPI) for VM164 once and wait up to 120 seconds
for stopped. Do not select Stop/Reset or force shutdown. If it does not stop, stop
this procedure and preserve evidence. Reacquire/validate stopped, empty readbacks.

## 3. Upload and attach the single nonboot data CD

Use the approved existing administrator path to upload the image into node pve's
`local` ISO storage under the exact new name above. Check absence before upload;
do not replace any existing object, even one with the same name. Retain source
and host-side whole-file SHA256/196608-byte check through the storage UI/approved
host file view. Do not inspect/mount the raw guest disk. If storage cannot provide
an independently verified copy without additional access, stop.

From the latest stopped/empty guard receipt take the exact config digest. The
following is a **future operator command template**, not a script to auto-run:

```sh
qm set 164 --digest EXACT_LATEST_GUARD_DIGEST --ide2 local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso,media=cdrom
```

Only the empty existing ide2 media may change. No boot order/BIOS/disk/permissions/
NIC/agent/serial changes. Reacquire readbacks; run the guard with `--phase attached
--expect-status stopped` and the same ISO volume. No pending change may remain.
If the actual host command capability differs, stop; do not fall back to raw QMP,
args, disk attachment, guest-agent execution or config-file editing.

## 4. One temporary GRUB edit on the installed disk

Open VM164's trusted VGA **noVNC** console before starting, with a second trusted
management window for the exact VM164 start. Start VM164 once. For its existing
SeaBIOS/GRUB installation, hold Shift during the disk's GRUB startup to reveal the
menu if hidden. Use the VGA menu only. Select the normal installed Ubuntu entry,
press **e**, and photograph its unchanged linux/initrd/root arguments. If the menu
or editor cannot be reached in this single supervised attempt, or it demands a
GRUB credential, stop; no serial/GRUB command-line experiment or password reset.

On the existing **linux** line, retain every original kernel/root/ro/console
argument and append exactly these two space-separated arguments:

```text
systemd.debug_shell=tty1 systemd.mask=getty@tty1.service
```

No other changes, no init=/bin/bash, single/rescue/emergency, autoinstall or GRUB
save commands. Photograph the complete modified line; verify root/initrd match
its original entry and only these two additions. Boot with **Ctrl-X**. This editor
change applies only to this boot; do not run update-grub, grub-install or grub-editenv.
The visible tty1 debug shell should appear during normal systemd startup. If only
a login prompt, initramfs/emergency shell or no usable prompt appears, stop. Do
not try locked passwords. Keep the trusted console supervised throughout.

At the tty1 root prompt type these checks and arm the runtime-only watchdog.
Do not continue unless every check and systemd-run succeeds:

```sh
test "$(cat /sys/class/dmi/id/product_uuid)" = faeb1db8-0df9-482d-b3e4-f6ccc1602193 &&
test "$(cat /sys/block/sda/device/serial)" = g6k164-12821f6b54a2 &&
test "$(cat /sys/block/sda/size)" = 134217728 &&
test "$(cat /proc/1/comm)" = systemd &&
test "$(tty)" = /dev/tty1 &&
systemd-run --unit=vm164-bootstrap-watchdog --on-active=20m --timer-property=AccuracySec=1s /usr/bin/systemctl --no-block poweroff &&
systemctl is-active vm164-bootstrap-watchdog.timer &&
test "$(ls -1 /sys/class/net)" = lo &&
printf 'IDENTITY_AND_WATCHDOG_OK\n'
```

Expected: active, then IDENTITY_AND_WATCHDOG_OK (interfaces exactly lo). No watchdog if identity checks
fail; return to the already identity-checked host console and use VM164 ACPI
Shutdown. A timer/runtime manager failure is a stop condition. Do not extend the
timer or leave the root prompt unattended. Verify `/usr/bin/python3.14` exists;
if absent, stop instead of installing anything.

## 5. Verify, stage in RAM, then eject the CD

On the verified guest tty1, check the **entire block device**, not a truncated
prefix. Both must match the pinned image before mounting or executing helper code:

```sh
blockdev --getsize64 /dev/sr0
sha256sum /dev/sr0
```

Expected: 196608 and fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154.
A different size/hash or missing sr0 is a stop condition; no alternate device guessing.

```sh
mkdir -m 0700 /run/vm164-bootstrap-media &&
mount -t iso9660 -o ro,nosuid,nodev,noexec /dev/sr0 /run/vm164-bootstrap-media &&
sha256sum /run/vm164-bootstrap-media/BOOT.PY
```

Compare the helper hash with step1. Only after an exact match, run:

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-media/BOOT.PY stage
```

Check BOOT.PY hash against step1 before executing it. Expect RAM_STAGED. The helper
requires matching identity, disk64GiB, real systemd PID1, installed ext4 root,
tmpfs /run, lo-only, sda-only, exact transient flags and active tty1 debug shell,
locked root, no persistent debug-shell override/enablement, active watchdog, exact
read-only media inventory and unchanged probe pin. It exclusively creates
/run/vm164-bootstrap-r1 (0700) with 0600 files, recording machine-id, boot-id and
hashes of public boot/account/identity files. No account, password or disk repair.
An existing RAM path or partial stage is preserved and refuses a retry.

```sh
umount /run/vm164-bootstrap-media
```

Now on the trusted host reacquire running/attached readbacks and validate them.
Use their latest digest to eject **media only**, keeping the existing empty ide2:

```sh
qm set 164 --digest EXACT_LATEST_GUARD_DIGEST --ide2 none,media=cdrom
```

Reacquire and validate `--phase empty --expect-status running`; no pending changes.
Do not proceed if eject became a pending change or the guest still sees media.
Changing hotplug policy/removing hardware to make this work is outside approval.

## 6. Run the unchanged pinned read-only probe and capture evidence

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-r1/BOOT.PY probe &&
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-r1/BOOT.PY page 0
```

The wrapper rechecks current boot identity, RAM probe hash and complete media
absence, then runs exactly:

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-r1/LABPKG.PY probe
```

It preserves raw stdout as PROBE.JSON and its hash in RAM. No application, serial
broker, executor, provider or database is opened. No target-requirement values are
invented: missing bwrap, unexpected native/runtime versions, shared mounts or
resource shortfalls remain genuine installation blockers for later review. Do
not rerun the probe to overwrite evidence; exclusive outputs reject repeats.

Capture the SHA256 and all pages shown on tty1. Page argument is **zero based**:
page0 prints PROBE_PAGE1/N, then page1 through page(N-1). Each page has at most8
54-column `R0000:...` base64 rows; retain screenshots in order and transcribe rows
exactly into rows.txt on the trusted workstation. Full hash is a 71-column line.
Before shutdown, reconstruct and verify on Nexus in a new execution directory:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-r1/tools/decode_probe.py \
  --rows /NEW-EXECUTION/rows.txt --sha256 EXACT_CAPTURED_PROBE_SHA256 \
  --out /NEW-EXECUTION/decoded
```

Missing/duplicate/unordered rows, hash mismatch, wrong UUID/serial/disk or remaining
optical media fail closed. If transcription fails, re-display the same RAM pages;
do not change the data. Capture must finish before the watchdog. If time expires,
keep partial evidence and mark the execution incomplete. The JSON is unsigned and
from a temporary-root boot; matching trusted host observations are also required.
It does not qualify a clean boot or authorize installation/Gate6K.

## 7. Close temporary root, return to clean boot, leave stopped

After the external PROBE.JSON hash is verified and retained:

```sh
/usr/bin/python3.14 -I -B -S /run/vm164-bootstrap-r1/BOOT.PY close
```

**Do not type exit as cleanup.** The stock debug shell has Restart=always. The
helper submits a separate runtime oneshot; it runtime-masks/stops debug-shell,
requests kill of remaining unit processes, checks inactive/failed state, MainPID0,
masked-runtime and empty unit cgroup, and compares public persistent-file hashes.
It prints a closure receipt on tty1 and requests graceful poweroff after10 seconds.
Capture the receipt: both temporary_root_closed_this_boot and
persistent_files_unchanged must be true. This behavior is fixture-tested, not yet
VM-qualified. The independent watchdog remains armed until shutdown.

Use fresh host readbacks to confirm stopped/empty/no pending; retain closure
receipt and state evidence. If closure is false, throws, or shutdown fails, follow
failure handling below; never record successful closure based on exit alone.

For final proof of non-persistence, start VM164 once more from its unchanged disk
with empty CD. In GRUB's editor photograph the linux line **without either added
argument**, then press Esc to discard the inspection and boot the default entry
normally. No new boot edit. Observe the ordinary Ubuntu login prompt; Enter must
not reveal an unauthenticated root shell. Do not attempt passwords. Retain console
evidence of that clean login. Since no authenticated administrator exists after
this clean boot, do not claim to have run service/cmdline inspection there. The
runtime closure receipt, unsaved GRUB edit, fresh normal-entry observation,
locked-login behavior and final stopped state are the available closure evidence.
If this clean-entry/login observation cannot be obtained, mark closure incomplete.

Finally select VM164 **Shutdown** (ACPI), confirm stopped and rerun host guard on
fresh empty/stopped readbacks. Leave the uploaded data ISO retained and detached
for evidence; do not delete any media/evidence/disk. Original empty-drive config
and disk-only boot must match, with no pending config, NIC or agent. No debug
service is enabled persistently by this procedure. All temporary files and units
were on /run and disappear with the first shutdown.

## Failure handling — preserve, close, stop; no alternate experiments

Before root is obtained: preserve screenshots/readbacks, gracefully ACPI-shutdown
only VM164 if running, confirm stopped, detach the data CD only if the latest
matching guard permits that exact transition. No retry of GRUB/serial/init modes.
After trusted identity is established: capture error/screens before RAM is lost.
If probe/stage/close fails and a root prompt remains, use only
`systemctl --no-block poweroff` on the already verified tty1, or wait for the
watchdog under supervision; confirm stopped from the trusted host. Do not exit
and leave a restarting shell. If the guest hangs, one host ACPI Shutdown is within
scope. A forced Stop/reset, unavailable target binding or emergency intervention
requires a new explicit operator decision; do not run it automatically. A failed
closure must never be labeled verified; stopped VM closes access but further
normal-boot proof remains required. Do not repair, chmod/chown persistent paths,
edit passwords, remove overrides, change boot files, add NIC/agent/SSH, mount raw
disks, replay the old installer, or activate any JARVIS/broker/Gate6K path.

Keep the initial/step readback hashes, approved scope/reference, UTC times,
modified and clean GRUB screenshots, watchdog evidence, verified probe JSON,
closure receipt and final state together in the new execution packet. Record an
incomplete result truthfully. Review actual probe facts before preparing any
separate protected-install approval; existing installation assumptions are not
established by this document.
