# Future trusted-console r4 handoff

**Not executed. Current GO covers isolated ISO engineering only.** No Proxmox/guest access, virtual disk operation, shutdown, reboot, reset, snapshot or installation occurred. The commands below are prepared for a later separately authorized VM164 media replacement/retry. Booting an unattended installer can format the intended virgin disk; that is outside the current ISO-only GO.

## 1. Preserve the failed r3 state before any lifecycle action

Leave the current failed installer intact during engineering. Retain the original r3 ISO, its hash, error message and relevant console transcript/metadata outside VM164. From the **already independently identified VM164 installer console**, the following future operator block is read-only:

```bash
(
set -eu
test "$(id -u)" = 0
python3 -I -B - <<'PY'
from pathlib import Path
assert Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()=='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
PY
date -u +%FT%TZ
cat /proc/sys/kernel/random/boot_id
lsblk --json --bytes --paths --output NAME,TYPE,SIZE,SERIAL,MODEL,RO,RM,MOUNTPOINTS
udevadm info --query=property --name=/dev/sda | python3 -c 'import json,sys; d=dict(line.rstrip().split("=",1) for line in sys.stdin if "=" in line); print(json.dumps({k:d.get(k) for k in ("DEVNAME","DEVTYPE","ID_SERIAL","ID_SERIAL_SHORT","ID_PATH")},indent=2))'
wipefs --json --no-act /dev/sda
findmnt --kernel --list --noheadings --output TARGET,SOURCE,FSTYPE,PROPAGATION
)
```

Capture the reported error and these public metadata values through the trusted console into independently retained evidence. Do not dump cloud data, credentials, process environments, root-home files or unreviewed log bundles. A screenshot/transcript preserves only visible information; **it is not a backup of the failed guest's full RAM/log state**. If fuller preservation is required and no approved export method exists, keep the VM running and stop here. This task has not supplied or approved a raw-log export, RAM snapshot or power change. No safe retry claim may conceal that reboot discards volatile evidence.

Only after retention is sufficient may the human separately authorize the new VM's lifecycle/installation retry. This handoff deliberately contains no automatic stop/reset or forced shutdown command. If VM164 is still running when a stopped-state operation is requested, the procedure refuses. VM163 must remain untouched throughout.

## 2. Transfer the new public ISO without replacing r3

Nexus source:

`/home/nexus/.local/share/jarvis-g6k-vm164-installer-r4/ubuntu-26.04.1-g6k-vm164-r4.iso`

SHA256:

`050875e2f3ffd5a7711bb2f520bce98404416d2117faedf2ba608831e2a416f3`

Bytes: `3042836480`.

Use an approved offline-file transfer / trusted Proxmox ISO-upload workflow into an **unused** filename on local ISO storage, yielding `local:iso/ubuntu-26.04.1-g6k-vm164-r4.iso`. Preserve r3 under its existing filename and independently retain both hashes. Do not overwrite an existing differing r4 file, create a NIC, start an ad hoc guest transfer service, enroll SSH keys or bypass authentication. Actual upload/access remains operator work; no UI session or transfer is claimed by this packet. Check local free capacity for this additional3.04GB file plus retained host reserve before upload.

## 3. Inspect and replace only optical media, while stopped

The following are standalone copy-and-paste shell blocks. Open the file and paste its full contents into the trusted **root@pve node console**; no script must already exist there:

1. [PVE-INSPECT-ONLY.sh](PVE-INSPECT-ONLY.sh) — read-only: checks node/address, VM164 UUID and hardware, dedicated raw volume identity, protected uploaded r4 hash and current status/media. It may inspect a running failed VM's configuration/file metadata but does not read its disk signatures or mutate anything in inspect mode.
2. [PVE-REPLACE-MEDIA-ONLY.sh](PVE-REPLACE-MEDIA-ONLY.sh) — **later authorization required**: requires stopped VM164, the exact expected r3 media, the same UUID/hardware/disk binding and an empty read-only raw-image signature report. It uses the PVE config digest to change only ide2 to r4 and preserve install-media-first boot order. It checks the result remains stopped. No disk creation, resizing, conversion, mounting, signature removal, cleanup or start occurs.

The future mutation is exactly equivalent to the following after all checks; use the guarded block, not this unguarded reference:

```bash
qm set 164 --digest "$verified_current_config_digest" \
  --ide2 local:iso/ubuntu-26.04.1-g6k-vm164-r4.iso,media=cdrom \
  --boot 'order=ide2;scsi0'
```

The helper requires the reviewed downloads directory raw-volume shape `downloads:164/vm-164-disk-N.raw`, actual raw size64GiB, root ownership, one link and no writable group/world permissions. Compare its **actual** volume/path/inode/device output to the independently retained VM creation record. No particular disk index or inode is invented. If actual storage/format/controller/version differs, stop for review; do not convert/replace a disk or edit assertions to force acceptance. This helper does not attest that no other hypervisor reference exists; the external dedicated-disk/console review is still necessary.

If signature inspection reports GPT, ext4 or any other signature, a partial installation, mounted/partitioned state, malformed output or an error, **preserve and stop**. No wipe, formatting workaround or new disk is authorized. Likewise stop if another device/NIC, hardware topology change, wrong UUID/serial or different media identity appears. Do not reuse an old `/etc/machine-id` or approval record.

## 4. Proposed safe retry sequence — requires a new GO for installation writes

After external failure-evidence retention, approval of VM164-only retry, stopped media replacement and revalidation of current resource safety:

1. Run [PVE-PRESTART-CHECK-ONLY.sh](PVE-PRESTART-CHECK-ONLY.sh). It repeats the target/r4 hash/raw-disk checks, requires r4 optical boot binding, and samples30seconds of headroom, swap/OOM counters, memory stalls and boot identity. It never starts the VM. It retains the previous conservative15,955,132,416-byte physical-availability screen. A successful short sample is not proof of representative future peaks; review current commitments/normal-load behavior too. Do not change existing VMs, swap settings, caches or memory allocations to clear it.
2. When those checks and the separate installation-write authorization are actually satisfied, the exact trusted-node boot command is:

```bash
# FUTURE ONLY: requires explicit VM164 installation retry/format authorization.
qm start 164
```

3. Observe only VM164's trusted console. r4 independently validates UUID, QEMU hardware serial, udev identities/uniqueness, path, size, single-disk topology, no NIC and zero signatures **before Subiquity can select the disk**. The actual7403 matcher then applies the exact three-field conjunction. On any refusal, keep the failed state and error; do not alter udev, substitute values, remove signatures or fall back to largest/first/arbitrary disk. If hardware identity changed, return metadata for review instead of broadening the match.
4. A layout preview should identify only the intended64GiB disk. Do not assume a confirmation prompt will provide an additional stop: early autoinstall admission is the protection. Normal installation will write a partition table/filesystem to that one virgin disk. The unchanged late guard still enforces private ext4 and SSH/cloud/identity preparation checks; it does not clear findings. Record actual installation success/failure and final stopped status separately. No success is inferred from matching tests or the new hash.

There is no root qualification invocation or final approval-marker creation in this procedure. Even a successful OS install leaves offline protected runtime/artifacts, actual identity/capacity/path checks, credential review, media removal and explicitly approved mount-propagation scope outstanding. All previous isolation requirements remain fail-closed.
