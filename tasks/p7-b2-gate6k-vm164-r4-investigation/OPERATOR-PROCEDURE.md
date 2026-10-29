# Proposed operator procedure — no commands executed on VM164 or Proxmox

**Current action: keep the hold.** Leave VM164 running at the failed root shell and VM163 stopped. Retain the current disk in place. Do not rerun the guard/installer, remove stamps, edit YAML, select retry, resume storage, boot the target, build another ISO, run qualification, or perform a disk/media/lifecycle change. Earlier r4 retry instructions are not applicable to the initialized disk in this incident.

The next useful authorization is narrowly scoped **console-only read-only evidence collection**, with temporary output in verified live RAM. This packet is the concrete proposal for that action; the present GO covers Nexus work only. Do not execute the following guest block until that separate authorization is granted. No network enabling, SSH, writable evidence disk, guest agent, mounted target filesystem or service-control command is needed.

## 1. Capture volatile chronology before changing anything

At VM164's existing trusted root shell, after approval, run this read-only diagnostic block. It verifies UUID, boot ID and `/run` tmpfs **before** creating output. It neither runs nor imports the guard. Logs/configs may contain sensitive information: keep the resulting directory restricted and export only through a separately approved secure evidence channel; do not paste entire cloud-init data or logs into chat.

```bash
set -eu
test "$(id -u)" = 0
test "$(tr '[:upper:]' '[:lower:]' < /sys/class/dmi/id/product_uuid)" = faeb1db8-0df9-482d-b3e4-f6ccc1602193
test "$(cat /proc/sys/kernel/random/boot_id)" = c93413f7-41cb-4e50-a412-e882ad09fed0
test "$(findmnt -n -o FSTYPE --target /run)" = tmpfs
test "$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)" -gt 262144
command -v timeout >/dev/null
umask 077
g6k_evidence_dir=$(mktemp -d /run/g6k-r4-evidence.XXXXXXXX)
capture() {
    g6k_label=$1
    shift
    test "$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)" -gt 262144
    if (ulimit -c 0; ulimit -f 16384; timeout 30 "$@") > "$g6k_evidence_dir/$g6k_label.txt" 2>&1; then
        echo 0 > "$g6k_evidence_dir/$g6k_label.exit"
    else
        g6k_rc=$?
        echo "$g6k_rc" > "$g6k_evidence_dir/$g6k_label.exit"
    fi
}
capture time date -u --iso-8601=ns
capture uuid cat /sys/class/dmi/id/product_uuid
capture boot-id cat /proc/sys/kernel/random/boot_id
capture uptime cat /proc/uptime
capture cmdline cat /proc/cmdline
capture processes ps -e -o pid,ppid,lstart,etimes,stat,cgroup,args --forest
capture units systemctl list-units --all --no-pager
capture jobs systemctl list-jobs --no-pager
capture installer-service systemctl show snap.subiquity.subiquity-server.service -p ActiveState -p SubState -p MainPID -p InvocationID -p NRestarts -p ExecMainStartTimestamp -p ExecStart -p Restart
capture journal-monotonic journalctl --boot=c93413f741cb4e50a412e882ad09fed0 --output=short-monotonic --no-pager
capture journal-json journalctl --boot=c93413f741cb4e50a412e882ad09fed0 --output=json --no-pager
capture diskstats cat /proc/diskstats
capture mountinfo cat /proc/self/mountinfo
capture mounts findmnt --json --output SOURCE,TARGET,FSTYPE,OPTIONS,MAJ:MIN
capture swaps cat /proc/swaps
capture block lsblk --json --bytes --paths --output NAME,KNAME,PKNAME,MAJ:MIN,TYPE,SIZE,SERIAL,MODEL,RO,RM,FSTYPE,PTTYPE,MOUNTPOINTS
capture sda-properties udevadm info --query=property --name=/dev/sda
capture sda1-properties udevadm info --query=property --name=/dev/sda1
capture sda2-properties udevadm info --query=property --name=/dev/sda2
capture sr0-properties udevadm info --query=property --name=/dev/sr0
capture sda-signatures wipefs --json --no-act /dev/sda
capture sda1-signatures wipefs --json --no-act /dev/sda1
capture sda2-signatures wipefs --json --no-act /dev/sda2
capture partition-table sfdisk --json /dev/sda
capture ext4-header dumpe2fs -h /dev/sda2
capture disk-readonly blockdev --getro /dev/sda
capture block-class ls -l /sys/class/block
capture target-holders ls -la /sys/class/block/sda/holders /sys/class/block/sda/slaves
capture target-dev cat /sys/class/block/sda/dev
capture open-block-descriptors lsof -nP /dev/sda /dev/sda1 /dev/sda2
capture early-stamp stat /run/subiquity/early-commands
capture early-stamp-hash sha256sum /run/subiquity/early-commands
capture server-state cat /run/subiquity/server-state
capture snap-list snap list subiquity --all
capture snap-current readlink -f /snap/subiquity/current
capture media-mount findmnt --target /cdrom
capture effective-config cat /autoinstall.yaml
capture effective-config-hash sha256sum /autoinstall.yaml
capture media-config-hash sha256sum /cdrom/autoinstall.yaml
capture media-guard-hash sha256sum /cdrom/g6k-disk-guard-r4.py
capture log-files find /var/log/installer /run/subiquity /var/crash -maxdepth 3 -type f -printf '%p %s %TY-%Tm-%TdT%TH:%TM:%TS\n'
capture installer-log-mount findmnt --target /var/log/installer
capture installer-logs tar -c -f - --ignore-failed-read /var/log/installer /var/log/cloud-init.log /var/log/cloud-init-output.log /run/subiquity
capture cloud-config-files find /etc/cloud -maxdepth 3 -type f -printf '%p %s\n'
capture cloud-config tar -c -f - --ignore-failed-read /etc/cloud
capture end-time date -u --iso-8601=ns
(
    cd "$g6k_evidence_dir"
    sha256sum -- *.txt *.exit > SHA256SUMS
)
printf 'RAM evidence directory: %s\n' "$g6k_evidence_dir"
```

Binary tar output intentionally goes to a capture file despite its `.txt` suffix. Each command has a 30-second timeout and a Bash file-size limit of 16 MiB, with core dumps disabled; check exit records for timeouts, file-limit exits and incomplete archives. The block requires more than 256 MiB of available memory before each capture and stops if that threshold is lost. These bounds may truncate the timeline: missing logs/tools and incomplete captures are evidence gaps, not PASS. A complete collection may need a separately arranged bounded/streamed export. No all-clear is inferred from a process or descriptor snapshot. Exporting the RAM packet, acquiring full process mount namespaces/config overrides or collecting extra files requires an approved method; do not add a disk, enable networking or fetch packages to improvise one.

Record operator, console, acquisition start/end time, each export hash and destination custody. Keep originals restricted, compare hashes on receipt, then produce a minimized timeline keyed by boot ID, PID, unit InvocationID and monotonic time. Identify the **automatic** failing guard's parent process and invocation; look for an earlier `READ_ONLY_VM164_DISK_GUARD_ACCEPTED`, every Subiquity start and every curtin partitioning/block-meta/mkfs start/finish. Capture effective config hashes per invocation and storage configs/device maps. Establish whether the observed GPT ID and ext4 creation metadata correlate with those commands. A missing journal record is not proof that no write occurred.

## 2. Obtain host-side provenance under separate read-only approval

Do not run the old PVE prestart/media scripts: VM164 is running and those are stale workflows. The newly approved host evidence scope should be limited to VM164 metadata, resolved backing-volume identity/format/backing chain, current optical attachment/media digest, raw pre-r4 signature-check output with timestamps, relevant VM164 task/lifecycle history, disk access by other processes and any existing block-write audit. No VM163 access is needed. No VM lifecycle, lock manipulation, image repair, snapshot, disk conversion or disk modification is included.

Do not claim a new raw backing-file scan is equivalent to guest-visible bytes without verifying image format and offsets. Do not open the image with a tool that can repair metadata or obtain conflicting writable access. Exact host commands must be bound to independently confirmed backend/path and approval; this investigation deliberately does not guess a running disk path or issue host commands.

## 3. Review the timeline and preserve the original disk

Resolve writer attribution if logs permit; otherwise record the explicit remaining uncertainty and its containment disposition. Capture a consistent forensic image only through a later separately approved acquisition plan. VM164 may remain running while volatile evidence is gathered; preservation does not imply it is immutable or that another writer is impossible. Discovering an active writer requires a new preservation decision, not an unapproved kill, freeze, shutdown or detachment here.

Recommended eventual disposition: preserve this disk permanently as incident evidence and approve a new blank disk as a distinct asset. Before authorizing anything, specify preservation destination/method, exact old/new volume identities, fresh target hardware serial, VM UUID, attachment plan, resource budget, media hashes and the revised protection mechanism. Preserve the original outside the installation topology only when separately authorized; never install with both evidence and new target attached because the single-disk gate must continue to refuse.

## 4. Conditions for a future installation attempt

The order is: evidence review and documented mutation-mechanism disposition → approved protection implementation and disposable rehearsal → separate media build approval → exact new-disk/lifecycle/installation-write approval. Require proof the new target is uninitialized, exclusive and correctly bound; passing `wipefs` alone is insufficient. If an independent zero-fill provenance claim is required, obtain it through an approved full-content verification of the new disk, never by wiping this disk.

Run the new installation only after all conditions in [REVISED-DESIGN.md](REVISED-DESIGN.md) are verified. On any refusal, preserve state and stop; never use the old r4 retry commands or bypass partitions/signatures. Installation success, first boot, credentials/mount/isolation readiness and Gate 6K qualification remain separate findings and approvals.
