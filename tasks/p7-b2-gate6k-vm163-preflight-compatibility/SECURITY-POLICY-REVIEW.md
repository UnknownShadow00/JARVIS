# Narrow preflight correction

Scope: isolated Nexus engineering; no connection to VM163, Core, AI or Proxmox. The supplied VM facts are operator-reported, not fresh observations by this task. The original candidate and installed `/opt/g6j-release` are preserved.

## Demonstrated defects

1. `CREDENTIAL_PATHS` treated ordinary preparation and OS directories as evidence of credential exposure. Reproductions against the sealed Gate6K implementation refused each of `/home/jarvis`, `/run/credentials`, and `/var/lib/cloud/instance` solely by existence.
2. The specified `python -I -B .../qualify_all.py` could not import `qualify_multi_uid`: isolated Python excludes the script directory. The reproduction imports the module under a non-main name and never executes qualification. The fix inserts only the installed, protected sibling directory before the fixed import.
3. A separate private `/boot` ext4 partition was invariably rejected. The correction accepts exactly `/boot`, with a separately approved `/dev/...` source, a distinct device from `/`, and filesystem root `/`. No arbitrary additional disk/mount exception is introduced.
4. The historical test harness hardcoded Core's interpreter. Its Nexus-only adaptation binds to the actual interpreter exactly, uses `sys.prefix` for read-only library access, and retains the signal broker's direct-child/UID/cwd/pidfd checks. This does not change V3 runtime code.

## Credential policy

The active runner calls `inspect_environment_paths()` and `require_paths()` before any disposable state creation. It does not use the historical existence list as its live policy. The old constant remains for API/history clarity; passing any detected indicator through the older `credential_paths` interface still refuses.

| Location | Accepted metadata | Refusal / additional requirement |
|---|---|---|
| `/home/jarvis` | Real directory owned by the independently identified nonroot preparation account; no group/other write; safe ancestors | Symlink, unknown owner, writable ancestry, known credential locations, actual JARVIS repository or historical authority-state path refuse. Arbitrary preparation files are not scanned or certified secret-free. Human fresh-image/no-imported-credentials approval remains necessary. |
| `/run/credentials` and systemd credstores | Protected directories with no regular payload files | Any regular payload, even empty or root-only, refuses. Symlinks, hardlinks, special files, unsafe permissions/ownership or unavailable inspection refuse. No approval field overrides active credentials. |
| `/var/lib/cloud` | Root-owned, non-writable-by-others metadata; canonical `instance` alias to a real `instances/<id>` directory | Complete cache metadata inventory includes seed and prior instances. Known key indicators, unsafe links/special files, exposed opaque nonempty data and inspection/race failures refuse. Populated protected caches additionally require snapshot-bound human provenance review; private ownership alone never certifies absence of credentials. |
| Known root credentials, host mounts, production-state locations | Absent | Presence, including dangling links, refuses. |

Cloud-init's canonical alias is validated with `readlink`, not followed blindly. Opaque cache files (including `obj.pkl`, user/vendor data and scripts) are never opened or deserialized. Nonempty opaque files must be root-private. Ordinary cache status names may be readable, but every populated cache still requires the explicit provenance review. The metadata digest covers names, types, ownership, modes, sizes, timestamps and inode/device associations, **not file contents or secret hashes**; only aggregate counts, digest and fixed diagnostic codes are exported. Metadata changes invalidate that approval. It is an inspection snapshot, not a guarantee against a hostile root racing or replacing the host.

Required review value: `FRESH_DISPOSABLE_IMAGE_NO_IMPORTED_CREDENTIALS`, with the exact current metadata digest, in the root-protected VM-specific approval. The human must establish that from trusted installation/preparation provenance without dumping or sharing cache contents. If provenance is unknown or actual credentials may have been imported, qualification stays blocked. Do not invent that attestation, delete/hide directories, mask stores with mounts, or loosen permissions to pass.

A bounded metadata inspector opens only directories using `O_DIRECTORY|O_NOFOLLOW` and dirfds. Tests enforce that it never opens regular cache/credential contents. Limits: depth16,4096 entries per tree,8192 aggregate cloud rows,128 top-level cache entries; exceeded limits refuse. Known-path checks are not a universal secret detector. Physical isolation, fresh image provenance, no credential import, absence of forwarded agents and trustworthy protected code remain independent operator responsibilities.

## Mount and identity policy

Root remains private ext4. Non-loopback interfaces and prohibited host identities refuse. The marker retains exact machine-id, VMID/UUID, disk, console, release and digest bindings. A marker/hostname alone is not proof of hypervisor identity or isolation.

`boot_source=/dev/sda2` permits only the reported `/boot` shape; another source, bind subtree, same device, absent approved mount, filesystem mismatch or extra boot/EFI mount refuses. The historical `mounts=PRIVATE_ROOT_ONLY` value continues to prohibit external/shared storage; this optional, explicit boot partition field is its sole new exception.

Credential-specific systemd tmpfs/ramfs mounts may have ordinary protected topology only with `ro,nosuid,nodev,noexec` and root `/`. Actual payloads are checked independently and still refuse. Shared/master propagation, protected path overrides (including home and cloud cache), duplicate mountpoints, automounts, shared/network filesystems, bind subtrees and extra real filesystems remain refused. The offline ISO at `/mnt/g6l-cd` must not remain mounted during qualification. No mount/network change was performed here.

## Primary-source context

Cloud-init documents `/var/lib/cloud/instance` as an instance-cache alias and describes sensitive cache data: [cloud-init internal files](https://docs.cloud-init.io/en/latest/development/internal_files.html), [upstream cache layout](https://github.com/canonical/cloud-init/blob/main/doc/var-lib-cloud.txt). Systemd documents per-service credentials and credential stores: [systemd.exec](https://www.freedesktop.org/software/systemd/man/258/systemd.exec.html), [upstream credentials documentation](https://github.com/systemd/systemd/blob/main/docs/CREDENTIALS.md). These explain the policy; they do not attest VM163's actual contents or configuration.
