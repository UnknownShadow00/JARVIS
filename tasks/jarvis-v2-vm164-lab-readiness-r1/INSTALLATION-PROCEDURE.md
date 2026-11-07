# Dormant offline installation procedure — future authorization required

This package installs immutable application/dependency and dormant serial-candidate
files only. It creates no accounts, credentials, authority state, database, systemd
unit, socket, service or activation marker. It does not alter an existing release.
No command in this document has been run against VM164 by this sprint.

## Prerequisites and bootstrap boundary

Use only a trusted already-installed VM164 root console, independently matched to
VM164 UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193 and disk serial
g6k164-12821f6b54a2 / downloads:164/vm-164-disk-0.raw (64GiB). Historical records
leave installed-boot completion and root access unproven; the latest observer
attempt returns401. A failed/live installer, missing root context, media boot or
initialized evidence disk is a STOP, not permission to retry installation or wipe.
No generic rescue, GRUB, root-autologin, guest-agent, power or networking workaround
is included. Preserve incident disk/history under its existing hold.

The existing signed Ubuntu26.04.1 amd64 OS, root-protected CPython3.14.4,
SQLite3.46.1/OpenSSL3.5.5, bwrap, private ext4 and native library provenance must
already be approved and present. This wheel package includes neither an OS nor
a native-runtime installer. Missing or different prerequisites block installation;
no apt/dpkg/global pip operation or runtime substitution is performed.

Independently compare fresh trusted-PVE configuration and guest facts: no NIC,
no guest agent/passthrough/shared host channels, original single disk, serial0
socket, onboot disabled, disk-only boot and no transfer/setup media. Current
observer401 cannot establish these facts. Do not change its token or grants here.
All interfaces in the guest must be lo; shared/slave mounts or external filesystems
refuse. Existing Gate6K multi-UID boundaries and all root/operator/service/agent
roles remain unchanged and separately unqualified.

## One approved protected bootstrap

After the operator grants the exact finite scope in AUTHORIZATION-REQUEST.md:

1. Transfer only the final bundle and standalone lab_package.py by an explicitly
   approved offline path. Verify both SHA256 pins against independently retained
   BUNDLE.json. Never run root code from a preparation-user-writable location.
   The human must first copy the verified bootstrap into root-owned nonwritable
   custody and establish a root-owned0755 `/opt/jarvis-v2-lab/releases` parent and
   a root-owned nonwritable approval directory. Those protected writes are future
   authorized human work, not operations performed by the current sprint.
2. Run the protected bootstrap's read-only `probe` on VM164. Compare its public
   machine-id, boot-id, DMI UUID, disk/root filesystem UUID/device, OS/runtime,
   native mapped-file hashes, bwrap hash, network/mount and resource facts with
   independently trusted observations/artifact records. The probe is unsigned
   guest evidence, not guest attestation or privileged qualification. Preserve its
   original output in restricted operator custody.
3. Fill approval.example.json truthfully. Keep it root-owned0600 under protected
   ancestry. Bind the exact bundle SHA, fixed source revision/destination, actual
   machine/boot/rootfs/runtime/bwrap identities, operator reference and a UTC expiry
   within one hour. Nulls, wrong scope, changed boot/runtime, stale approval,
   wrong target, unsafe ancestry, insufficient resources or an existing destination
   refuse. Do not fill fields from guesses merely to make validation pass.
4. Run the bounded offline verifier, then the protected installation command:

```text
/usr/bin/python3.14 -I -B /root/protected-bootstrap/lab_package.py verify /approved-local-media-or-staging/BUNDLE.tar.gz EXACT_BUNDLE_SHA256
/usr/bin/python3.14 -I -B /root/protected-bootstrap/lab_package.py install /approved-local-staging/BUNDLE.tar.gz EXACT_BUNDLE_SHA256 /etc/jarvis-v2-lab/approval.json
/usr/bin/python3.14 -I -B /root/protected-bootstrap/lab_package.py validate-installed /approved-local-staging/BUNDLE.tar.gz EXACT_BUNDLE_SHA256 /etc/jarvis-v2-lab/approval.json
```

These are templates, not commands executed here. Use a sanitized root environment,
exact pinned executable and bootstrap; no ambient provider credentials. Approved
media must be detached before the install target check and subsequent smoke, so
stage the hash-verified archive locally first. No media attach/detach is authorized
by the preparation GO. Package extraction is safe-name/regular-file-only, bounded,
no-follow/descriptor-relative, exclusive and fsynced. Root-owned source/dependency
files remain immutable to the service principal. Partial output is preserved.

## After authorized dormant installation

Use an existing independently approved unprivileged lab principal. Do not create
or repurpose a privileged Nexus submitting identity to perform this step.

```text
/usr/bin/python3.14 -I -B /opt/jarvis-v2-lab/releases/rc1-345626bddd36028e/tools/smoke_runner.py /opt/jarvis-v2-lab/releases/rc1-345626bddd36028e /private-new-smoke-output EXACT_INSTALL_MANIFEST_SHA256
```

The last pin is BUNDLE.json installed_manifest_sha256. Every destination is new.
The runner copies verified public source/examples and creates disposable synthetic
state only inside a no-network, capability-free cage. It never starts the installed
application service, imports real config, contacts a provider, uses a real database
or connects the serial candidate. Retain full inputs, stdout/stderr, dependency and
smoke results. The existing nine hardware/desktop cases remain excluded.

## Broker and protected worker

The installed `serial-candidate/` is the independently reviewed13-file successor,
not the older12-file Phase3 source and not a JARVIS real adapter. It includes the
unchanged disabled/null-bound examples and units for review. It is not copied to
`/opt/g6k-serial`, installed into systemd, provisioned with state or started.

`tools/worker_preflight.py SOURCE UID GID` is a future read-only metadata checker:
exact reviewed manifest/files/root protection, existing nonroot g6k-bridge identity,
private tty ownership, getty masking, kernel console absence, no open serial holder
and lo-only network. It never opens the serial device, credentials or worker DB.
Even all metadata checks passing explicitly leaves activation false. Locked-account,
privilege/FD/capability paths, service filters, actual cross-UID DAC/seccomp/egress,
QEMU buffering and trusted report comparisons remain external authorization gates.
No shell/TTY/bootloader/account/permission repair is automated.
