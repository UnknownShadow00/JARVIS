# Stop/revoke without erasing evidence

Future operator procedure, not run in Phase3. These commands address only the
new bridge. No existing observer token, other VM, guest role, disk or lab fixture
is removed. Do not assume token deletion terminates an established WebSocket.

## Immediate stop at Nexus

From the trusted operator-root context, remove the public activation grant marker
and stop both the accepting socket and service:

```sh
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py revoke-host
systemctl stop g6k-serial.socket g6k-serial.service
```

The runtime watcher notices grant/source/marker changes and closes tracked TLS
channels and local connections. systemctl stop provides independent termination.
If the marker is already absent, revoke-host refuses rather than fabricating a
success; still perform the authorized service/socket stop and verify inactivity.
If source/entry is suspect, use the trusted service manager directly instead.
No new acceptance should remain possible through the socket.

## Revoke only the bridge token at PVE

```sh
pveum acl delete /vms/164 --tokens 'g6k-bridge164@pve!serial' --roles G6K164Serial
pveum user token remove g6k-bridge164@pve serial
```

Inspect the named token metadata/ACL removal without displaying any credential
value. Leave the existing g6k-codex164@pve!observer unchanged. If a new issuance
failed after a possible creation, the same fixed token ID is the orphan to review;
do not issue another token or overwrite the preserved local partial file.

## Stop the guest worker, if authorized

At the trusted VM164 operator console:

```sh
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py revoke-worker
systemctl stop g6k-serial-worker.service
```

No power operation, guest-agent call, getty/autologin restoration or cleanup is
included. Restoring a previous serial-owner policy is a separate reviewed change.

## Preserve and review

Preserve host/guest ledger.sqlite3, operation.lock and any SQLite journal remnants,
root-approved public config/manifest, unit/ownership metadata and bounded public
client receipts. A reserved or unacknowledged request remains uncertain. There
is no CLI command to clear it. Do not delete/reinitialize directories, remove a
failed fixture, restore a snapshot or reuse a grant ID to make a test pass.

For a consistent operator-owned evidence acquisition, first stop the exact bridge
services and exclude other writers. Inspect only the explicit SQLite tables via
read-only access and verify the local hash chain. Store public audit exports in
an approved destination; root record ownership and an external hash checkpoint
are needed to detect replacement/rollback of the local evidence. Local hash
chains alone cannot defend against root or an actor controlling the ledger owner.

**Never copy an entire host state directory as public evidence:** it contains
token.json. Export only reviewed ledger event metadata, request/result hashes,
public grants/manifests and allowlisted client results. No token file, raw serial
transcript, management ticket, credential directory, environment, signing key or
whole guest filesystem. Token-file removal/rotation and any new grant/state are
new operator decisions; revocation above does not erase those files.
