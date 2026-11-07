# Consolidated pending authorization — not executed

One staged setup request for the exact source/archive in `RELEASE.json`, not an
approval. Original58698f4c… identifies the historical candidate, not this revision.
Complete the actual public bindings in `approval.example.json` before action.

## Systems and proposed changes

| System | Proposed scope | Excluded |
|---|---|---|
| Nexus/VM161 | Fresh locked broker and restricted submitting identities; root-owned source/config/units; private state; separate no-transport precheck/canary; timed broker acceptance | No sudo/docker/lxd/admin or privileged inherited handles for submitter; no shared mount/cache/resource-policy changes |
| PVE192.168.0.50 | Fresh G6K164Serial role, g6k-bridge164@pve user, separated !serial token; exactly VM.Audit VM.Console at /vms/164, propagate0 | No root shell/token, node/storage/pool/other-VM, lifecycle/config or guest-agent rights; observer untouched |
| VM164 | Pinned public worker source/config, fresh locked non-root g6k-bridge, private audit state, reviewed unit, exclusive ttyS0 | No packages, SSH, password unlock, NIC, private credentials, root/qualifier commands, disk or lifecycle changes |

Target: node pve, VM164, UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193,
downloads:164/vm-164-disk-0.raw, hardware serial g6k164-12821f6b54a2,
64GiB, serial0 socket, no NIC, qemu-ga disabled. Catalog: identity, kernel,
isolation-summary only. Existing request/output/time caps remain enforced.

## Prerequisites and blocked facts

The actual submitting process/session must lack root/container/service-management,
ptrace, privileged capabilities/FDs and broker-file access. Current Nexus
sudo/docker/lxd membership is not accepted. Creating a second account alone is
insufficient if the agent remains privileged elsewhere. Check sudo/polkit/ACL,
container and process-access paths independently; no escalation attempt is required.

Actual guest machine-id, new numeric UIDs/GIDs/filesystem identity and an installed
root session are unknown to this offline review. Operator binds these observed
facts during the one scoped ceremony. User-reported installed boot and clean
metadata are historical observations, not new measurements by this task.

If no installed-root context exists, stop before guest setup. An exact maintenance
bootstrap needs separately approved media digest, filesystem/partition identity,
preservation and enumerated power/media/mount transitions. This packet does not
authorize generic rescue/GRUB/root-autologin/password/SSH workarounds or invent
those missing facts. VM162, VM163, AI VM200 and other apps are excluded.

## Stage1 — Nexus installation and no-transport qualification

After approval, follow `INSTALLATION.md` absence/ownership checks with this revised
13-file manifest. Also install g6k-serial-precheck.service and .socket. Keep the
host config disabled; no token.json and no HOST-ACTIVATE. The precheck has its own
Unix socket and AF_UNIX-only unit; code cannot construct PVETransport/open a token
or ledger, or perform inspections.

In the human-root Nexus context only, reserve a new synthetic credential canary:

```sh
test ! -e /var/lib/g6k-serial-host/token.json || exit 1
test ! -e /var/lib/g6k-serial-host/secret-canary.txt || exit 1
install -o g6k-pve-broker -g g6k-pve-broker -m 0600 /dev/null /var/lib/g6k-serial-host/secret-canary.txt
```

The empty canary is not a credential. Root creates HOST-PRECHECK exclusively,
mode0644, containing the approved public grant_id plus LF. Complete disabled
config already binds the actual approved identity/release/expiry. During the
explicitly authorized precheck window only:

```sh
systemctl daemon-reload
systemctl start g6k-serial-precheck.socket
runuser -u g6k-submit -- /usr/bin/python3 -I -B /opt/g6k-serial/entry.py client-precheck identity
runuser -u g6k-submit -- /usr/bin/python3 -I -B /opt/g6k-serial/entry.py probe-paths
```

Require PRECHECK_AUTHENTICATED/exact caller UID/transport_enabled=false and all
fixed protection probes true. Retain actual wrong-UID/socket and code/config/unit
denial evidence, without real credentials. Independently complete escalation,
capability, FD, proc/ptrace and service-management review. These are actual Nexus
boundary checks, not guest qualification or a mock substitute for them.

Stop both precheck socket/service, verify inactive/no remaining processes, remove
only HOST-PRECHECK, and retain evidence/canary. Normal broker remains disabled.
Root records performed checks in mode0600
`/etc/g6k-serial/PREISSUANCE-ACCEPTED.json`, exactly this shape:

```json
{"grant_id":"BOUND_ID","release":"BOUND_SHA256","caller_uid":1234,"caller_gid":1234,"broker_uid":1235,"broker_gid":1235,"operator_reference":"BOUND_REFERENCE","checked_at":1234567890,"expires_at":1234568490,"checks":{"actual_peer_credentials":true,"synthetic_secret_denied":true,"code_config_units_protected":true,"escalation_review_passed":true}}
```

Example values are placeholders, not approval. Bind the actual disabled grant and
limit the record to600 seconds and the grant expiry. Codex must not author it.
Both host markers must be absent and the precheck stopped before issuance.
The issuer checks before secret prompts and again immediately before dialing;
stale evidence or changed config/source/CA/markers prevents network. Any partial
output is retained; there is no automatic retry or deletion.

## Stage2 — PVE permissions and private issuance

Only after Stage1 evidence passes, execute the fresh-user/role/token ACL blocks
in `INSTALLATION.md`. Check installed schema first; no broader-role fallback.
User and separated token effective maps each contain only Audit+Console at164.
No observer-token access/change or direct guest-exec permission.

Initial grant/token lifetime: at most3600 seconds from the operator-approved
window, using one absolute epoch expiry in host/guest configs and the new token.
Operator freezes the actual timestamp before action; no fixed future approval
time is fabricated. Preissuance evidence lasts at most600 seconds. No automatic
renewal; extending expiry requires a new reviewed grant.

The private issuer is human-root/private-TTY only. Existing management session
material stays in its memory; the new token goes directly to broker0600 storage.
No root password/token/session in chat, argv, environment, shared clipboard,
logs or evidence. Failed issuance/orphan token state is preserved and reviewed.

## Stage3 — VM164 setup and timed read-only acceptance

Use only the approved installed-root context and pinned public offline transfer
method. Install source/config/new locked identity/state/unit; preserve Gate6K
roles and credential checks. Assign ttyS0 exclusively. A required kernel-console
bootloader edit, reboot or rescue operation needs its exact additional scope.
Detach approved transfer media before testing; no host share, NIC or SSH.

`LIVE-ACCEPTANCE.md` enumerates activation and genuine negative controls. Approval
must explicitly include worker and normal broker socket start after public
bindings/rights are verified. Do not enable at boot. QEMU buffering/attachments,
actual DAC/roles/seccomp and service filters must be measured live, not inferred
from the offline suite. Tests that intentionally create uncertainty run last.

## Stop/revoke and rollback

Nexus: stop both accepting sockets/services, remove only public activation and
precheck markers, close active channels and verify inactivity. PVE: remove only
this token's164 ACL and delete g6k-bridge164@pve!serial. VM164: stop only the new
worker from trusted console if included in stop scope. See STOP-AND-REVOKE.md.

Preserve DBs/journals/canary/attestation/public inventories and checkpoints. Never
export token.json/full state directories. No ledger reset/retry, VM restore/delete,
fixture cleanup, disk replacement, old-role changes or automatic getty restoration.
Removal of new accounts/units/token files is later separately reviewed cleanup;
historical evidence stays intact.

## One pending decision

Approve or decline this bounded staged ceremony for the pinned revision, including
Stage1 before real credentials and only then scoped PVE/VM164 setup and acceptance.
Unknown bootstrap facts stay blocked, not permission to improvise. Gate6K
privileged multi-UID qualification, production/V3/succession/retirement, real
providers/models and other-system access remain excluded. **Nothing here ran.**
