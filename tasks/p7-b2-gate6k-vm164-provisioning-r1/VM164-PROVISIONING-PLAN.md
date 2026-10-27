# VM164 provisioning plan — stopped creation only

**No replacement VM has been created by this task. Starting a6000MiB guest remains NO-GO from the reported evidence.** This packet supersedes the previous packet's unresolved source-image design; the previous sealed packet remains unchanged. Profile: `network` for public tooling acquisition. No PVE SSH retry or remote command execution occurred.

The operator's trusted-console summary establishes pve at192.168.0.50, candidate164, active local/nonshared downloads storage (~872.66GB free), active local ISO storage (~62.60GB free), ~67.09GB RAM total,12.64GB MemAvailable,7.7GB swap used and0.89GB swap free. These are **operator-reported observations**, not a fresh agent observation. Raw inventory, storage backend details and observation timestamp were not supplied. Every allocation helper rechecks the live node and target.

## Memory decision

| Budget | Bytes |
|---|---:|
|6000MiB guest |6,291,456,000 |
|Reported MemAvailable |~12,640,000,000 |
|Remaining before QEMU overhead or workload growth |~6,348,544,000 |
|QEMU/management allowance for this plan |1,073,741,824 |
|Retained physical headroom for this plan |8,589,934,592 |
|Minimum MemAvailable screen |15,955,132,416 |
|Reported shortfall against that screen |~3,315,132,416 |

The1GiB allowance and8GiB reserve are conservative **engineering policy choices**, not Proxmox guarantees or a claim that overhead is always bounded by1GiB. Swap occupancy alone cannot distinguish old cold pages from current thrashing. Low remaining swap, unknown swap-in/out rates, PSI, workload peaks and configured commitments prevent treating12.64GB available as safe admission. Linux documents actual stall measurements through [PSI](https://docs.kernel.org/accounting/psi.html).

`NEXT-CONSOLE.sh` collects seven observations over30seconds: MemAvailable/swap bytes, page-swap/OOM/major-fault counters, memory and I/O PSI, boot ID, local running VM maximum allocations and the downloads backend. It creates no files and allocates nothing. Its screen refuses the reported headroom, any observed swap/OOM activity, memory stalls or a boot change. A quiet sample is only a screen: representative normal-load peaks, existing VM configured maxima and non-VM commitments still need review. Do not count swap, KSM savings, ballooning or memory overcommit as a physical reserve. No stress workload, swapoff, cache drop, tuning, VM shutdown/migration or RAM reduction is proposed.

**Safe independent stage:** configure VM164 stopped with6000MiB, autostart off, no HA registration and no start command. This does not allocate6000MiB of guest RAM or demonstrate safe runtime capacity. No smaller RAM fallback is automatic. If management itself has less than2GiB available, the allocation helper refuses even this preparation stage. This is not a new permission request: existing GO covers safe stopped provisioning; the unresolved memory screen blocks boot.

## Exact console sequence

Use the existing trusted **root@pve node console**. Open/copy each entire shell file into that console; these are standalone here-document blocks and do not require SSH or a file that is already present on PVE.

1. [NEXT-CONSOLE.sh](NEXT-CONSOLE.sh): read-only pressure/inventory report. Preserve the minimized JSON locally.
2. [INSPECT-CREATION-CONSOLE.sh](INSPECT-CREATION-CONSOLE.sh): reruns allocation prerequisites and prints the exact proposed `qm create` argv; no allocation.
3. [CREATE-STOPPED-CONSOLE.sh](CREATE-STOPPED-CONSOLE.sh): rechecks immediately, exclusively creates an evidence directory, rechecks again, then invokes only `qm create164` with `--start0` and `--onboot0`. Run only if inspection confirms the intended local backing storage and no unexpected findings. It never starts a VM.
4. Upload only the two exact reviewed ISO files to **local / ISO images** through existing authenticated Proxmox UI access. Check that the filenames are unused; never overwrite a differing existing image. Then use [ATTACH-INSTALLER-CONSOLE.sh](ATTACH-INSTALLER-CONSOLE.sh) to hash-check and attach the installer to the recorded stopped new VM. No boot occurs.

The create command embedded in the helper is:

```bash
# Reference only: use the guarded console block above, which performs live checks.
qm create 164 --name jarvis-g6k-clean-164 --ostype l26 \
  --bios seabios --machine q35 --cpu host --sockets 1 --cores 4 \
  --memory 6000 --balloon 0 --onboot 0 --start 0 --agent 0 \
  --hotplug 0 --protection 1 --scsihw virtio-scsi-single \
  --scsi0 downloads:64,format=raw,serial=g6k164-12821f6b54a2,cache=none \
  --ide2 none,media=cdrom --serial0 socket --vga std --tablet 0 \
  --smbios1 uuid=faeb1db8-0df9-482d-b3e4-f6ccc1602193 --boot order=scsi0
```

[Proxmox's command reference](https://github.com/proxmox/pve-docs/blob/master/generated/qm.1-synopsis.adoc) documents new-volume allocation using storage:size, disk serials, UUID configuration and explicit start control. Source/API review is not proof of successful execution on this PVE version. Any unsupported option fails and preserves partial state; never add skiplock/force/import/clone fallbacks.

## Live allocation checkpoints

- Root, hostname pve and management address. Cluster inventory, absence of164 QEMU/LXC configs and `/cluster/nextid --vmid164` must all establish the ID is currently free. Normal atomic `qm create` provides the final collision refusal; the observation is not a reservation.
- Four host CPUs. Recheck memory metadata; creation still has no permission to start. Global VM inventory is read only; no existing guest config or agent is accessed.
- downloads must actually be an enabled, active **directory** image store, nonshared, on a verified local ext4/xfs/btrfs filesystem. Inspect backing-device ancestry; network block devices, thin/unreviewed LVM and unfamiliar backends refuse. The user's summary did not identify the backend type; the helper does not guess. If downloads is ZFS/LVM-thin or another type, stop and review that backend before generating a different allocation command.
- Use both PVE available bytes and filesystem `f_bavail`, with64GiB plus the larger of32GiB or10% of filesystem capacity retained. No existing VM164 volumes may be present, even orphaned ones. Local ISO storage must be active/nonshared, support ISO content and retain at least20GiB available before these preparations.
- The **planned** new UUID and serial in `VM164-PLAN.json` bind the installer. These are not observed guest identities. A guest filesystem UUID, actual volume ID and machine-id cannot exist before the respective creation/formatting stages; no values are invented.
- After creation independently inspect actual PVE config:4 cores,1 socket,6000MiB,balloon0,onboot0,protection1, trusted VGA/serial console, guest agent disabled, no NIC (including disconnected NICs), no shares/passthrough/custom args/hooks/cloud-init drive, and only the new disk plus empty optical slot.
- Verify the new raw volume's actual PVE ID/path, root ownership, inode/device, single link,64GiB logical size, no backing file and stopped status. Logical size is not a full physical reservation: allocated blocks are recorded separately. Never use VM163's disk or attach any existing disk.

Creation records go to exclusive `/root/g6k-vm164-create-r1/` on PVE. Preserve and review any partial outcome or failure record. Do not destroy/free/retry a partial allocation, overwrite its record, change another VM, or automatically shut down even an unexpectedly running164. Return the minimized precheck/result and selected config values to the project; do not return tokens, environments or root-home contents.

## Remaining stop points

Boot remains blocked by current memory evidence, and installation/boot validation is still pending. Existing GO covers new-VM boot/install only once actual safety checks support it; no new blanket GO is needed. This packet supplies no automated start path.

Gate6K readiness additionally requires protected runtime/artifact installation, fresh actual identities, no credential/path findings, media detachment, at least20GiB available, and **explicit approval of propagation scope**. Neither a private namespace nor a guest-wide propagation change was performed. The final qualification marker and privileged qualification remain expressly prohibited in this task. VM163 stays running/preserved as reported; no existing VM, production Core or AI service was changed/accessed.
