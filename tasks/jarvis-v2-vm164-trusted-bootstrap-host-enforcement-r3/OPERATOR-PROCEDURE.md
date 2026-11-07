# Operator procedure — reviewable, NOT installed or run

**Current action: keep VM164 stopped. Only offline verification is authorized.**
No timer, source placement under real host paths, package query, Proxmox connection
or guest action has happened. The reported config/ISO stays unchanged.

## Presently safe local commands

From the JARVIS project root:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/verify_packet.py
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src/cli.py --dry-run
```

Replays/tests use NEW exclusive output directories outside this sealed packet.
They never pass --execute-reviewed-host or use a real manager/VM interface.

## Future Stage2 only, after explicit approval

Follow QUALIFICATION-PLAN.md. Review the package/source pins in SOURCE-MANIFEST.json
and candidate/ARTIFACT.json. Existing unprivileged callback UID must be verified;
no UID is assumed and no account/grant is created. The administrator may place
ONLY the approved public callback copy at:

```text
/opt/jarvis-vm164-r3-stage2/canary.py
```

Its directories must be root-owned/nonwritable to others and the regular code
root-owned/read-only. The separately approved timer/service uses the verified
existing NONROOT User, explicit Type=exec and finite limits. Root-system-manager
setup is privileged and needs the Stage2 approval; callbacks are unprivileged.
The script rejects root and a wrong source hash/path. Callback output includes
UID/eUID, clock pair and boot-id; it does not call any executable or VM interface.

Qualified canary invocation, **future argv data only**:

```text
/usr/bin/python3 -I -B -S /opt/jarvis-vm164-r3-stage2/canary.py
  --approved-nonvm-callback --expected-source-sha256 <reviewed canary hash>
  --mode success
```

Mode failure intentionally exits7. Missing-executable and timer/timeout/collision
trials require their named scope. Capture actual raw show/journal/clock evidence.
Do not copy synthetic timestamps or assume an active timer proves execution.
Do not use VM164, guest root or the private Stage3 worker in this stage. Host
reboot/reexec/suspend requires separate impact review; no broad maintenance is
included in a harmless timer approval. Leave unknown qualifiers false.

## Future Stage3 installation, after Stage2 and a separate approval

The inert archive contains exactly8 Python sources plus SOURCE-MANIFEST.json.
Inspect regular member names/hashes locally before transfer; do not blindly
extract as root. Never overwrite existing destinations. Archive/source hashes
are in candidate/ARTIFACT.json; local source verifier rebuilds it identically.

Future fixed installation layout (no location currently created by this task):

| Path | Proposed custody |
|---|---|
| /opt/jarvis-vm164-host-fence-r3/ | Existing admin creates NEW root0700 directory; copy only8 verified sources as root0444 |
| /etc/jarvis-vm164-r3/authorization.json | Root-private finite reviewed Stage3/A/non-root grant; never template values |
| /etc/jarvis-vm164-r3/stage2-prerequisites.json | Actual hashed Stage2 evidence/custody/version/clock record, root-private |
| /etc/jarvis-vm164-r3/review-record.json | Root-private reviewed source/Stage2 binding and Stage3/A scope |
| /var/lib/jarvis-vm164-host-fence-r3/ | NEW root0700 persistent state/evidence root, on trusted storage |

Do not enable/daemonize source or install static units in /etc/systemd. Runtime
units are created only by explicitly approved prepare. No code/file replacement
while active. Missing or preexisting ambiguous destination is a stop, not an
instruction to chmod/chown/repair unrelated data. These custody changes are
future installation actions requiring approval, not current permission grants.

The native authorization binds canonical Stage2/review hashes, source-tree hash,
host boot, finite UTC grant, exact packages/binaries and A/non-root purpose. The
code checks actual local package metadata. pvesh/pvesm/dpkg/Python paths, source
help contracts, show serialization and resource behavior must first be qualified.
Templates deliberately refuse; flags/hashes alone do not authenticate live facts.

## Future Stage3 controlled use, Policy A only

Use the existing trusted pve administrator console and the exact approved grant.
Fresh observations must match pve/164/UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193,
original downloads:164/vm-164-disk-0.raw/64GiB/serial g6k164-12821f6b54a2 and the
unchanged r4 ISO hash. No NIC/agent/extra channel/pending or boot-order drift.
Do not repeat the already-reported boot correction or detach media live.

The following names describe separately approved CLI actions; they are NOT run
by this preparation and must not be pasted into Nexus as a live procedure:

```text
/usr/bin/python3 -I -B -S /opt/jarvis-vm164-host-fence-r3/cli.py
    prepare | start | verify | observe | cleanup | retire
    --execute-reviewed-host
```

- `prepare`: reserve one session/approval, selfcheck, create both fixed-deadline
  pairs, read back exact state and confirm stopped. ARMED is NOT termination proof.
  Any failure attempts owned cancellation, quarantines unknown/orphan units and
  denies start. Keep all evidence; do not delete a tombstone to retry.
- `start`: permitted only once, stopped and<=15s from arm after fresh timer/service/
  source/session/grant/config checks. **Normal/non-root guest boot only.** No GRUB
  root flags, login unlock, serial broker or guest command. Unexpected privileged
  prompt is a failed qualification, not permission to use it.
- `verify`: pre-firing admission consistency; rejects drift/cancellation/fired
  assumptions. `observe`: read-only machine-readable current VM/unit/result data
  after/during execution, never a qualification grant. Readbacks are not atomic.
- `worker`: only the nonce/phase-bound timer invocation; do not manually invent,
  duplicate or rearm it to extend a session. Phase locks and exact binding prevent
  an old callback acting on a new generation. Intent must be durable before action.
- `cleanup`: only after fresh actual stopped proof; stop only verified-owned units,
  require idle workers/inactive units and final stopped proof. Never disarm while
  guest remains running. An interrupted cleanup remains CLOSING and resumable
  against stopped proof. CLOSED duplicates are historical/no-action, not live proof.
- `retire`: a distinct NEW finite reviewed approval is required after CLOSED,
  stopped proof and idle/inactive workers. The old active pointer is archived,
  never deleted as evidence. Used approval digests remain consumed. A new arm is
  a new explicitly permitted trial, not renewal of an active session.

## Failure, removal and evidence custody

Policy A's failed ACPI shutdown is a hard blocker. Do not run qm stop, unlock,
skiplock, alter protection/hotplug/boot/media or invoke an undocumented workaround.
Forced stop remains unavailable here even with a JSON. Use only a separately
reviewed authorized preservation/recovery decision; do not reset/reboot the host
or touch another VM. Record missing/late/failed evidence truthfully.

To remove later: first establish actual stopped state and approved ownership of
all unit names; run approved cleanup, verify units inactive and workers idle,
retire under new finite authority, and archive the whole state/journal/source/
review package through the approved custody channel. Disable no unrelated unit.
Retain failed/completed unit results and journal export before any separately
approved unit unload/removal. Do not collect/reset-failed/delete evidence to make
a test pass. If state/ownership/source changed, preserve it and obtain explicit
recovery review; do not improvise a force/unlink procedure.

No cleanup, archive or observed VM stop grants root bootstrap, installation,
Gate6K or production readiness. VM162/163/200, AI server, JARVIS/broker/real
executors/providers/databases and V3 remain outside every step.
