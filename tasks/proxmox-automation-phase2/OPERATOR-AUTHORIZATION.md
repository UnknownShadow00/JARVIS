# One-time operator authorization and activation sequence

**Future procedure only. Nothing in this file is approval.** There is no runnable
production broker/worker yet; the offline model cannot be deployed as one.
Do not run the permission commands now. Finish local implementation, review its
manifest and complete the following gates in order. Stop at any missing fact.

## 1. Retain the decision packet and establish protected custody

Use a private trusted operator session, with terminal transcription, shell tracing,
HTTP debugging and shared clipboard recording disabled. No PVE password, API
token, bearer header, VNC ticket or signing key goes to Codex/chat/task logs.
The operator's existing PVE administrative session supplies setup authority;
Codex receives neither its credentials nor a reusable administrative session.

Independently retain the reviewed broker/worker manifest SHA256 and this scope:

> I authorize one-time setup of a fixed-action serial bridge for node pve,
> VM164, UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193, disk
> downloads:164/vm-164-disk-0.raw, serial g6k164-12821f6b54a2, size64GiB.
> I approve only identity, kernel and isolation-summary under a new non-root
> guest UID, with a protected broker identity, VM164-only console access,
> explicit expiry and the independently retained implementation hashes.
> Keep the current observer token VM.Audit only, passwords locked, guest agent
> disabled and VM164 without a NIC. No VM162/VM163/AI-server access, general
> shell/root execution, package installation, qualification, new media, reboot,
> recovery boot or other lifecycle operation is included.

Record operator identity/reference, UTC approval time, caller UID, new broker UID,
guest UID, installed machine-id, approved code digests and expiry in the final
protected grant. `APPROVAL-TEMPLATE.json` is incomplete and conveys no authority.
The standing grant authorizes routine actions until expiry; it does not authorize
Codex to extend the grant or install a modified catalog.

## 2. Resolve locked-password bootstrap explicitly

First independently establish whether the installed system is actually running
and a trusted **installed-OS root session** already exists. API status cannot
answer that. A serial login prompt with locked passwords does not provide a
usable root session. Do not unlock accounts, set a password, enable SSH, add an
SSH key, use root autologin, add a debug shell, or let Codex type into GRUB.

If no trusted root session exists, **stop setup** and obtain this additional,
separate authorization with an exact media digest and observed disk identity:

> I authorize one operator-controlled VM164 maintenance/rescue session using
> the exact reviewed offline media and disk/partition identities recorded in
> the approval. Preserve the existing evidence first by the approved method.
> I approve only the specified power/media transitions and installed-filesystem
> access needed to install the reviewed non-root serial worker and its service.
> No password changes, package downloads, host shares, network attachment,
> filesystem repair, reinstall, wipe or privileged qualification is authorized.
> Return to the installed disk with transfer media detached and original
> approved boot order. Record all transitions and installed file hashes.

This approval must enumerate the actual transitions, exact media, filesystem
UUID/partition and preservation method before use. No generic reboot, mount,
chroot, init=/bin/sh or repair recipe is pre-approved by this packet. An installer
root shell, rescue environment or chroot must not be reported as installed-OS
guest validation. The earlier VM164 incident evidence is not silently cleared.

## 3. Install protected local components before granting transport rights

After setup approval and manifest review, the operator provisions an independent
locked Nexus `g6k-pve-broker` system identity and root-controlled code/configuration
and parent directories, with a private broker-owned state/credential directory.
No Codex-editable Python path, venv, unit, drop-in, executable or import dependency
may become trusted broker code. No sudo rule or administrative group is given
to Codex or the broker. Verify the actual UID boundary, proc/ptrace restrictions,
service management rights and socket peer checks before issuing a credential.

Create the initial socket and denial-only broker with transport disabled. Test
token-file and service/config access denial under the **actual Codex UID**.
This is an explicit approved deployment step, not accomplished by the user-owned
reference files in this packet.

## 4. Grant only the reviewed PVE permission set

At the trusted PVE management console, first confirm the proposed user, role and
token names are unused, no group/inherited/pool grants affect them, and installed
endpoint help agrees with the source-reviewed permissions:

```sh
pvesh usage /nodes/pve/qemu/164/termproxy --verbose
pvesh usage /nodes/pve/qemu/164/vncwebsocket --verbose
```

After the explicit setup authorization, the following are the proposed exact
non-secret ACL commands. They create fresh objects; do not use modify-on-conflict
or reuse an existing identity with unknown grants.

```sh
pveum role add G6K164Serial --privs 'VM.Audit VM.Console'
pveum user add g6k-bridge164@pve --enable 1 --comment 'VM164 fixed-action broker only'
pveum acl modify /vms/164 --users g6k-bridge164@pve --roles G6K164Serial --propagate 0
```

Use a separately reviewed, **operator-only secret provisioner** with the existing
trusted management session to create `serial` under `g6k-bridge164@pve`,
`privsep=1`, a finite operator-approved epoch expiry, and no other privileges.
The exact API operation for that provisioner is:

```text
POST /api2/json/access/users/g6k-bridge164@pve/token/serial
privsep=1&expire=<approved_epoch_seconds>
```

The returned token value must travel only from that private TLS response into
the broker's exclusive protected credential file (proposed
`/var/lib/g6k-pve-broker/token.json`, mode0600, broker-owned, with protected
ancestors and no symlink/hardlink substitutions), never through Codex, stdout,
environment exports, command arguments, task evidence, clipboard or a debug log.
Do not run bare `pveum user token add`: its normal output includes the secret.
Do not reuse, copy or elevate the existing observer credential. A reviewed
secret-capture provisioner is a **required implementation prerequisite**, not
provided by the offline model. If unavailable, stop before token creation.

Only after protected credential capture succeeds:

```sh
pveum acl modify /vms/164 --tokens 'g6k-bridge164@pve!serial' --roles G6K164Serial --propagate 0
pveum user permissions g6k-bridge164@pve --path /vms/164
pveum user token permissions g6k-bridge164@pve serial --path /vms/164
```

Also inspect the **entire** effective permission maps for this user/token in the
trusted session and confirm no grants at `/`, `/vms/162`, `/vms/163`, other VMs,
nodes, storage or pools. Do not infer absence merely from the positive VM164
query. Leave the existing `g6k-codex164@pve!observer` grants unchanged.
No Sys.Console, PVE root token or VM.GuestAgent.* permission is needed.
Command syntax is based on the official
[pveum synopsis](https://github.com/proxmox/pve-docs/blob/master/generated/pveum.1-synopsis.adoc);
verify installed help before the authorized deployment.

## 5. Install the non-root worker through the authorized guest-root path

The human operator verifies guest DMI UUID, disk hardware serial, installed
machine-id and installed boot, then installs only the manifest-reviewed worker,
public identity binding and root-owned service/policy. Create a fresh locked
`g6k-bridge` user with no privileged groups and no access to the existing Gate 6K
role files/sockets. Reuse an already installed, provenance-verified runtime only;
missing runtime means stop for a separately approved offline package procedure.

Stop/disable the **exact ttyS0 serial-getty** and establish the reviewed serial
ownership/terminal settings. No root autologin or emergency-shell fallback.
Resolve kernel ttyS0 ownership within the exact authorized scope; a required
bootloader change/reboot needs that explicit lifecycle approval. Do not guess
that starting a worker on a kernel-controlled console is safe. Retain ordinary
operator VGA access separately; Codex's broker exposes no VGA/VNC passthrough.

Do not enable qemu-ga, change VM hardware/network or install the Gate 6K runtime
as an incidental dependency. Detach approved setup media before activation,
verify guest only-loopback/no shared mounts/no imported credentials, and retain
the actual role separation checks. Supply no private key/token to the guest.

## 6. Bind the standing grant, qualify and activate

The operator fills the protected grant from independent observations, restricts
the exact three-action catalog, and records the final manifest hash externally.
Run the post-approval live negative tests in `NEGATIVE-TESTS.md`, including
raw-console denial from the Codex UID, no bypass through token access, other-VM
self-permission absence, terminal noise, timeout/UNKNOWN and role DAC checks.
Do not issue a successful-operation claim until all required tests have evidence.

Approve activation of that exact grant/version only after tests pass. Codex can
then request named routine actions without manual command pasting. Setup,
qualification tests and activation can be covered by one precisely scoped
setup approval; unexpected changes cannot. A future privileged Gate 6K run is
always a distinct decision and is absent from the default catalog.

## Revocation and rollback authority

Proposed immediate PVE revocation, if approved for the installed bridge:

```sh
pveum acl delete /vms/164 --tokens 'g6k-bridge164@pve!serial' --roles G6K164Serial
pveum user token remove g6k-bridge164@pve serial
```

Revoke the standing grant and close the broker's active WebSocket/session as
well: do not assume ACL/token removal alone terminates an already established
console. Preserve broker/guest replay ledgers and public evidence. Guest worker
removal/getty restoration, token-file disposal, reboot, snapshot rollback or VM
deletion are separately scoped operator changes. Do not delete failed fixtures.
