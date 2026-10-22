# Human execution proposal — NOT AUTHORIZED OR EXECUTED

Approve one specifically identified throwaway Linux VM and this exact bundle before any provisioning below. No VM creation, deletion, resource change, account creation or privileged helper run is authorized on Nexus, Core, AI or Proxmox by Gate6J.

## Proposed environment and identity

Estimate:4 vCPU,8GiB RAM,40GiB disk; no GPU. These are planning estimates, not measured minimum requirements. Use a single private ext4 root filesystem on a Linux x86-64 VM with AF_UNIX SO_PEERCRED/SO_PASSCRED, /proc process start/boot metadata, libseccomp.so.2 and no shared host filesystem. The tested software environment is Python3.14.4, SQLite3.46.1 and cryptography46.0.5. Require the exact127 effective distribution versions in disposable/dependency-versions.json and requirements-versions.txt. The full offline test suite uses more disk than the targeted future runner; retain at least20GiB free before execution.

An independent human at the trusted management console must record the new VM UUID/VMID, guest machine-id, isolated disk identity, approved snapshot/disposal scope and absence of production attachment. A hostname or marker alone is not proof. Do not reuse VM200 or any existing service VM. VM provisioning is a separate approval, not an instruction to the agent.

Disconnect/remove every NIC before the qualification. Require only lo in /sys/class/net, no production routes, no host/shared mounts, no guest-agent host filesystem exposure, no SSH-agent forwarding, no inherited provider connections and no production secrets. Inspect ip link/route and findmnt privately; export only the conclusion and approved identifiers. The runner additionally rejects non-ext4/container roots, extra nonvirtual/shared filesystems, known hostnames, /home/jarvis, /home/nexus, common credential directories and host mount paths. It does not search secret contents and cannot prove arbitrary undisclosed credentials are absent. Use a fresh minimal image; a refusal is not permission to broaden the allowlist or remove evidence on another host.

## Exact release

Source tree: /home/nexus/.local/share/jarvis-gate6j-redteam/release-r2.

Transfer only `/home/nexus/.local/share/jarvis-gate6j-redteam/gate6j-release-r2.tar` through approved offline media.

Archive SHA256: `c8347d9e2c193fb96976cec7e36d2db8c92cb4851616ea84c58f497ad1161c00`.

SOURCE-SHA256SUMS SHA256: `9e824f0c3da92c0edb872ff5f3cbcbd9c32a98f228b49403a92d154584d746fe` (612 source/test/package files; archive has613 members including this manifest). Keep both expected hashes in the independent operator record outside the VM.

Do not copy a Core venv, credentials, runtime databases, homes, SSH state or production environment. Obtain an approved offline interpreter and wheelhouse independently, record their artifact hashes outside the VM and verify them before installation. The provided version lock is not a wheel-content attestation. If an exact artifact cannot be supplied, stop as BLOCKED; do not silently substitute versions or enable networking during the test.

## Explicit privileged provisioning for review

These commands are for the approved VM's human root console only. They were not run in Gate6J. Replace the artifact locations and independently attested VM identifier deliberately. Install no sudo rules, SSH keys, network policy or systemd service.

```sh
# Verify the transferred archive BEFORE extraction.
printf '%s  %s\n' c8347d9e2c193fb96976cec7e36d2db8c92cb4851616ea84c58f497ad1161c00 /media/reviewed/gate6j-release-r2.tar | sha256sum -c -
test ! -e /opt/g6j-release
install -d -o root -g root -m 0755 /opt/g6j-release
tar --no-same-owner -xf /media/reviewed/gate6j-release-r2.tar -C /opt/g6j-release
chown -R root:root /opt/g6j-release
find /opt/g6j-release -type d -exec chmod 0755 '{}' +
find /opt/g6j-release -type f -exec chmod 0644 '{}' +
cd /opt/g6j-release
sha256sum -c SOURCE-SHA256SUMS

# Three new non-login principals; AUTHORITY is root, the fourth kernel UID.
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6j-operator
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6j-service
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6j-agent
id g6j-operator
id g6j-service
id g6j-agent
```

Require distinct nonzero UIDs and private primary GIDs, no sudo/admin/shared supplementary group. Root remains the authority and may inherently read all same-host files; the experiment tests separation from service/operator/agent, not root compromise.

Provision the reviewed interpreter at `/opt/g6j-python` and a root-owned environment at `/opt/g6j-venv`. Its parent/import/site-package directories must not be writable by any role. The following dependency step is explicit future provisioning, never an agent action here:

```sh
# First independently verify the operator-supplied interpreter/wheelhouse hashes.
/opt/g6j-python/bin/python3.14 -m venv /opt/g6j-venv
/opt/g6j-venv/bin/python -m pip install --no-index --find-links /media/reviewed/wheelhouse -r /opt/g6j-release/disposable/requirements-versions.txt
/opt/g6j-venv/bin/python -m pip check
```

The independent build must reproduce SQLite3.46.1 as well as Python3.14.4. Install the reviewed libseccomp runtime through offline OS provisioning. All127 versions must pass the runner's check; this file intentionally contains exact versions rather than an online resolver. No mutable Core path is used by the future runner.

Privately create `/etc/g6j-disposable-approved.json`, root-owned0600, using O_EXCL. Exact fields:

```json
{
  "machine_id": "ACTUAL_VALUE_FROM_THIS_VM_ETC_MACHINE_ID",
  "scope": "GATE6J_DISPOSABLE_ONLY",
  "network": "NO_NIC",
  "release": "/opt/g6j-release",
  "credentials": "NONE",
  "mounts": "PRIVATE_ROOT_ONLY",
  "source_manifest": "9e824f0c3da92c0edb872ff5f3cbcbd9c32a98f228b49403a92d154584d746fe",
  "vm_identity": "ACTUAL_EXTERNALLY_ATTESTED_NEW_VM_IDENTIFIER"
}
```

Do not leave placeholders. The marker records human authorization and declarations; it is not independent proof by itself. `/var/lib/g6j-disposable` must not exist. Never erase an earlier failed run to make preflight pass: use a newly approved VM/snapshot and retain the failure evidence externally.

## Ownership and execution

The reviewed runner explicitly creates only fixture paths under /var/lib/g6j-disposable: root0755 parent; authority root0700/database0600; operator child0700/key0600; app and backup service0700; fixture release/config root-owned read-only. Socket parents run/operator and run/service are root:respective-private-group0750; sockets root:group0660. No group can rewrite socket directories. The agent has no private group membership granting access. The helper is a foreground root process, not an installed service or general administration API.

After console verification and approval, run exactly:

```sh
cd /opt/g6j-release
env -i PATH=/usr/bin:/bin HOME=/root PYTHONDONTWRITEBYTECODE=1 /opt/g6j-venv/bin/python -B /opt/g6j-release/disposable/qualify_all.py
```

Order: preflight/source/dependency checks → kernel no_new_privs and non-AF_UNIX socket denial → fresh separate role processes → signed singleton successor fixture → CLOSED attach → signed OPEN with intentionally dropped response → signed one-use permit → DAC and actual peer tests → concurrent consume at real runtime acceptance → fake blocked-provider uncertainty → all-app rollback refusal → authority reopen/replay → service-UID crash/transport/security suite. There is no real provider, production epoch or measurement.

## Outcomes, evidence and failure handling

PASS requires permitted operations and expected denials to have actually executed with four distinct measured kernel UIDs, all cross-UID cases passing and the subsequent suite exit0. A setup refusal is BLOCKED; unexecuted tests are NOT RUN. An assertion, timeout or unexplained exception is FAIL. The current Gate6J record is GENUINE MULTI-UID QUALIFICATION: NOT RUN.

Retain `/var/lib/g6j-disposable/report.json`, `qualification.json`, `suite-stdout.txt`, `suite/cases.xml` and `EVIDENCE-SHA256SUMS`. Cross-UID cases and the same-UID logical pytest supplement must remain distinguishable. Verify the report manifest with sha256sum -c and record its SHA256 separately outside the VM. Also record the exact source manifest, interpreter/OS/kernel/filesystem and human VM approval identifier. Export only this allowlisted, reviewed nonsecret evidence. Do not export signing.key, raw environments, arbitrary logs, app conversations or a whole VM filesystem.

On preflight failure, stop before fixture creation. On later failure, preserve all existing paths and reports; no automatic reset, repaired permissions, retry of a consumed command or inferred remote completion. The runner stops only its own child processes/listeners. A failed or interrupted attempt is not refunded. Human review decides whether a separately approved new VM run is appropriate.

Deleting the fixture tree, wiping synthetic signing material, reverting/deleting the VM or removing its disk requires separate owner authorization. Production provisioning, V2 disposition, successor creation, V3 deployment, provider qualification and pilot activation remain entirely separate future approvals.
