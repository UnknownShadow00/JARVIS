# VM164 disk matching — r3 failure and r4 correction

The r3 configuration used the wrong serial identity for Subiquity. Its independent early guard checked the correct QEMU hardware serial via `lsblk`, but `storage.layout.match.serial` reused that value for a different interface. This was an r3 configuration error; the two checks were not verifying the same property.

The retained, hash-verified Subiquity7403 snapshot provides the exact implementation:

- `evidence/pinned-source/filesystem-model.py`, `_make_matchers`, lines1740–1797: `serial` matches `ID_SERIAL` in the probed udev dictionary; `path` matches `disk.path`; `id_path` matches udev `ID_PATH`. The typed `MatchDirective` explicitly includes these three fields.
- `_filtered_matches`, lines1813–1815: **all** supplied matchers must succeed. `_matching_disks` supports fallback lists, but r4 supplies only one dictionary. No fallback or glob is introduced.
- `evidence/pinned-source/filesystem-controller.py`, lines2162–2173: an empty matching candidate set produces the exact reported “Failed to find matching device” exception.

The operator's actual observation was:

| Independent identity | Reported value |
|---|---|
| DMI VM UUID | `faeb1db8-0df9-482d-b3e4-f6ccc1602193` |
| Kernel disk path | `/dev/sda` |
| Hardware serial via lsblk | `g6k164-12821f6b54a2` |
| Exact disk bytes | `68719476736` |
| Model | `QEMU HARDDISK` |
| udev ID_SERIAL | `0QEMU_QEMU_HARDDISK_drive-scsi0` |
| udev ID_SERIAL_SHORT | `drive-scsi0` |
| udev ID_PATH | `pci-0000:09:01.0-scsi-0:0:0:0` |

These are user-reported actual console observations; this task did not connect to the guest. Their timestamp and raw logs were not supplied. The supplied observation is retained verbatim in minimized structured evidence, without claiming a raw-log export.

The exact corrected layout is:

```yaml
storage:
  layout:
    name: direct
    match:
      path: /dev/sda
      serial: 0QEMU_QEMU_HARDDISK_drive-scsi0
      id_path: pci-0000:09:01.0-scsi-0:0:0:0
```

This is a conjunction of three exact values, not path-only or arbitrary-disk selection. `lsblk`'s hardware serial remains mandatory in a separate early guard, together with root authority, the exact VM UUID, loopback-only networking, exactly one disk,64GiB exact size, fixed/writable target, no mounted target/partitions/dependents, and an explicitly empty read-only signature report. The hardware serial is **not changed** to the udev value.

The new guard also enumerates all reported block devices and their udev metadata. Each of the expected ID_SERIAL, ID_SERIAL_SHORT and ID_PATH values must belong uniquely to `/dev/sda`. A second device claiming any of them refuses, even if the new Subiquity path condition would otherwise exclude that device. Additional disks refuse, including read-only ones. Other devices must be read-only optical or loop installation media; unexpected writable device-mapper/RAID/loop/media devices refuse. Missing, conflicting or malformed metadata is a failure, never an empty inventory. `udevadm settle` only waits; there is no trigger, property rewrite, disk reset or signature removal.

The early command now invokes `/cdrom/g6k-disk-guard-r4.py` using isolated Python. There are no override arguments, user-supplied fixture modes or approved-looking marker files. The guard performs **no formatting**. Passing it allows the existing installer workflow to proceed only during a later authorized installation run; it does not authorize that run itself.

All other autoinstall settings are semantically identical to r3. The source Squashfs and late target guard are byte-identical. The prior installation-time empty-SSH construction, cloud-init disable sentinel, locked identities, credential checks, networking, runtime requirements, mount policy and qualification boundaries are unchanged. No r3 evidence, VM state, virtual disk or Gate6K source was edited.

Synthetic tests execute the actual pinned Subiquity matching method bodies with type annotations removed only for standalone loading; installer probing/imports/services are never executed. With the observed udev fixture, r3's serial-only directive returns zero candidates and r4's conjunction returns only `/dev/sda`. Negative controls cover wrong UUID/hardware serial/size/model, additional disks, initialized/uninspectable signatures, NICs, mounted/partitioned/readonly/removable target, extra writable devices, malformed/incomplete udev data and ambiguous identities. Separate tests bind the future console procedure to VM164 and reject foreign volumes/external devices. These are userspace synthetic controls, not kernel qualification or an actual successful installation.
