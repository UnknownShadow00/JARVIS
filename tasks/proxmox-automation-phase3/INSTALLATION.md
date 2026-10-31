# Limited operator installation — future actions only

**No commands below were run against privileged installation paths, PVE or VM164
in Phase3. Do not activate either service as part of this installation.**
Run privileged blocks only from the human's trusted root context, after approval.
Do not configure sudo for Codex, disclose a root credential or give it root login.

## Smallest approval requested

The necessary PVE/guest setup is a one-time **scoped installation ceremony**:

> Approve a fresh dedicated PVE user/token restricted to VM164 Audit+Console,
> finite expiry and privilege separation, held only by the protected Nexus broker;
> approve installing the pinned non-root serial inspection worker and private
> audit state on VM164 using an operator-controlled root session, with ttyS0
> getty ownership resolved and passwords kept locked. Catalog: identity, kernel,
> isolation-summary only. Keep no NIC, qemu-ga disabled, original observer token
> unchanged, VM162/163/AI untouched, and no privileged qualification. Installation
> does not include activation, package installation or lifecycle changes.

There is also a necessary **Nexus prerequisite**: protect the broker under a new
non-administrative UID and run submissions under a genuinely restricted separate
UID/session. The current sudo/docker/lxd Nexus identity fails production policy.
PVE/VM164 changes alone cannot meet the isolation requirement on that principal.
No user/group or runtime isolation changes were made during this phase.

If there is no existing installed-OS root session, locked passwords require a
separate, exact offline maintenance/rescue authorization. That must specify media
digest, disk/partition identities, evidence preservation and each power/media/mount
transition. It is not implicit in the approval above. No password unlock, SSH,
root autologin, GRUB input by Codex or generic rescue command is authorized here.

## 1. Review and freeze the packet

Independently retain the packet SHA256SUMS digest and the source manifest digest
from `evidence/source-pins.json`. Work from a newly created, root-controlled
reviewed copy, proposed `/root/g6k-phase3-reviewed`, not the Nexus-writable repo.
Copy only public candidate files through an independently reviewed channel.
On VM164 that channel must be approved offline public media, never a shared host
mount or an existing VM's disk. Mount/detach actions need their explicit scope.

After independently checking the source manifest fingerprint, verify its12 files:

```sh
cd /root/g6k-phase3-reviewed/src
sha256sum SOURCE-SHA256SUMS
sha256sum -c SOURCE-SHA256SUMS
/usr/bin/python3 -I -B -c 'import sqlite3,ssl,ctypes,termios; print("required stdlib modules present")'
```

Compare the printed **public manifest digest** with the independent record. Stop
on any mismatch, unsupported Python/Linux architecture, missing module, unexpected
file/cache/link or user-writable interpreter/import/library path. Do not download
packages, transplant a runtime from another VM, or recursively chown a user tree.

## 2. Common source installation on Nexus and VM164

Verify `/opt/g6k-serial` and `/etc/g6k-serial` do not already exist, including
symlinks; stop on conflict. All filenames below come from the reviewed pinned
manifest, which must not change while copying. In each approved root context:

```sh
cd /root/g6k-phase3-reviewed
test ! -e /opt/g6k-serial && test ! -L /opt/g6k-serial || exit 1
test ! -e /etc/g6k-serial && test ! -L /etc/g6k-serial || exit 1
install -d -o root -g root -m 0755 /opt/g6k-serial /opt/g6k-serial/g6k_serial /etc/g6k-serial
while read -r g6k_digest g6k_name; do
    install -o root -g root -m 0644 "src/$g6k_name" "/opt/g6k-serial/$g6k_name" || exit 1
done < src/SOURCE-SHA256SUMS
install -o root -g root -m 0644 src/SOURCE-SHA256SUMS /opt/g6k-serial/SOURCE-SHA256SUMS
cd /opt/g6k-serial
sha256sum -c SOURCE-SHA256SUMS
```

This installs no activation marker, credential or service startup. The same source
is installed on both hosts; guest code never reads the provisioner/host credential
paths. Private token/session material is never transferred to the guest.

## 3. Nexus identities, disabled grant, state and units

First confirm these identities do not already exist. If they do, stop and review
rather than altering an existing account. No supplementary groups or sudo grants:

```sh
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6k-pve-broker
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6k-submit
id g6k-pve-broker
id g6k-submit
passwd -S g6k-pve-broker
passwd -S g6k-submit
install -d -o g6k-pve-broker -g g6k-pve-broker -m 0700 /var/lib/g6k-serial-host
install -o root -g root -m 0644 /root/g6k-phase3-reviewed/deploy/host.example.json /etc/g6k-serial/host.json
```

The system accounts remain password-locked. `g6k-submit` denotes the newly
restricted agent process identity, not a password login; the operator must arrange
the actual agent session under that identity without inheriting administrative
groups, capabilities or handles. Check effective sudo/polkit, container sockets,
ptrace/proc access, role/config/file ownership and service management rights.
The bridge does not configure or grant an impersonation/sudo mechanism to Nexus.

Complete the root-owned host.json in the trusted session, leaving enabled=false:
actual numeric caller/broker/worker UIDs and GIDs; installed guest machine-id;
independent source-manifest digest as release; new32-hex public grant_id; finite
epoch expires_at; operator reference; exact action subset; public CA fingerprint.
Use the same public binding values in the guest file below. Nulls always refuse.
Do not bind to a fixture value, live installer/chroot machine-id or root UID.

Copy the **existing reviewed public PVE CA only**, independently confirm its hash,
and do not open/copy the existing observer token:

Derive the authoritative comparison from `sha256sum /etc/pve/pve-root-ca.pem`
in the trusted PVE operator console and retain it independently. Comparing two
Nexus-writable copies alone does not establish CA provenance.

```sh
install -o root -g root -m 0644 /home/nexus/.config/g6k-proxmox/pve-root-ca.pem /etc/g6k-serial/pve-root-ca.pem
sha256sum /etc/g6k-serial/pve-root-ca.pem
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py init-host
install -o root -g root -m 0644 /root/g6k-phase3-reviewed/deploy/g6k-serial.socket /etc/systemd/system/g6k-serial.socket
install -o root -g root -m 0644 /root/g6k-phase3-reviewed/deploy/g6k-serial.service /etc/systemd/system/g6k-serial.service
systemd-analyze verify --man=no /etc/systemd/system/g6k-serial.socket /etc/systemd/system/g6k-serial.service
```

Verify the unit filenames were absent before installation; `install` is not an
overwrite approval. init-host refuses preexisting state; preserve any partial or
failed directory. No systemctl start/enable or HOST-ACTIVATE creation here.
Do not give the submitting identity read access to token/ledger or write access
to any installed code, unit, configuration, interpreter or ancestor directory.

## 4. PVE permission setup and private credential issuance

At the trusted PVE console, verify node/VMID/UUID/disk/serial0/no-NIC identity,
installed API help and all proposed user/role/token names are unused. In particular,
verify config/current, pending, termproxy and vncwebsocket compatibility and no
extra privileges are needed. Stop instead of adding a broader built-in role.

After the scoped setup approval, proposed exact PVE commands:

```sh
pveum role add G6K164Serial --privs 'VM.Audit VM.Console'
pveum user add g6k-bridge164@pve --enable 1 --comment 'VM164 fixed-action broker only'
pveum acl modify /vms/164 --users g6k-bridge164@pve --roles G6K164Serial --propagate 0
```

The new PVE user has no password or groups. Do not modify
g6k-codex164@pve!observer. No ACL on `/`, node, pool, datastore or other VM.
No VM.PowerMgmt, VM.Config.*, VM.GuestAgent.*, Sys.Console or root API token.

On Nexus, from the private human-root terminal only, issue the **new** token:

```sh
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py issue-token
```

This asks, with echo disabled and no non-TTY fallback, for the existing operator's
private PVEAuthCookie and CSRFPreventionToken from the trusted management session.
It never asks for a PVE password. Do not paste either into chat, argv, environment,
task logs or a shared clipboard/transcript. These values are ephemeral process
memory in the root-only provisioner, not exported to Codex or the broker.

It makes one fixed TLS-protected token-creation request with privsep=1 and the
approved expiry. Returned value goes directly to an exclusive0600 broker-owned
`/var/lib/g6k-serial-host/token.json` and never stdout. No retries or overwrite.
If issuance fails/response is lost, preserve the partial file and have the operator
inspect/revoke the fixed named token on PVE; never print token data or retry it.
Bare pveum token-add is excluded because it prints the returned secret.

Only after protected capture succeeds, at PVE:

```sh
pveum acl modify /vms/164 --tokens 'g6k-bridge164@pve!serial' --roles G6K164Serial --propagate 0
pveum user permissions g6k-bridge164@pve
pveum user token permissions g6k-bridge164@pve serial
```

Check the entire effective maps: exactly Audit+Console at `/vms/164`, no other
active paths, no group/pool/inherited authority; separated token and finite expiry.
Do not query another guest's resource to test this. Privilege syntax follows
the official [pveum synopsis](https://github.com/proxmox/pve-docs/blob/master/generated/pveum.1-synopsis.adoc).
VM.Console is still broad at PVE; only protected credential custody plus the
broker make the submitting process's interface restricted.

## 5. VM164 non-root worker installation

Use the independently approved installed-OS root context. Confirm DMI UUID,
hardware disk serial/size/volume correspondence, machine-id and current boot.
The unprivileged worker does not assume product_uuid is readable. Its public
expected UUID is pinned by the operator and independently checked in the API.

After the common source block above, verify user/unit/state names are absent:

```sh
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6k-bridge
id g6k-bridge
passwd -S g6k-bridge
install -d -o g6k-bridge -g g6k-bridge -m 0700 /var/lib/g6k-serial-worker
install -o root -g root -m 0644 /root/g6k-phase3-reviewed/deploy/worker.example.json /etc/g6k-serial/worker.json
```

Complete the root-owned public binding file with the independently observed
machine-id, shared release/grant_id/expiry, worker UID/GID and restricted Nexus
caller UID. Leave enabled=false. Do not copy any private token/key/session.

```sh
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py init-worker
install -o root -g root -m 0644 /root/g6k-phase3-reviewed/deploy/g6k-serial-worker.service /etc/systemd/system/g6k-serial-worker.service
systemd-analyze verify --man=no /etc/systemd/system/g6k-serial-worker.service
```

In the explicitly approved ttyS0 ownership change, stop and disable only
serial-getty@ttyS0 and its activation links. Verify no other process owns ttyS0.
Do not enable an autologin or give the worker a login/admin group. Verify the
installed `/proc/cmdline` has no ttyS0 kernel console, early console or serial
debugger. If fixing it requires GRUB/boot configuration or reboot, stop for that
additional exact authorization; a getty change alone is insufficient.

Keep original Gate6K root/operator/service/agent identities and DAC boundaries
unchanged. No marker, qualification, package install, NIC or qemu-ga change.
Detach previously approved public setup media before any live inspection.

## Installation stop point

Retain file/mode/owner/source inventories, account metadata and public ACL maps.
Neither activation marker exists; both JSON examples remain disabled until a new
approval. No start/enable, test console traffic, guest inspection or privileged
qualification is included in installation. Run `LIVE-ACCEPTANCE.md` only after
explicit activation-for-read-only-acceptance authorization. See
`STOP-AND-REVOKE.md` for preserving evidence while revoking the bridge.
