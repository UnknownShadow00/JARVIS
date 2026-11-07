# VM164 secure serial broker — Phase 3 implementation

**Candidate source implemented and offline tested. Not installed or activated.**
This phase made no connection to Proxmox, any VM or the AI server, and did not
open the existing API token. All changes are JARVIS source, tests, documentation
and evidence on Nexus. See `INSTALLATION.md` before any privileged setup.

## What is implemented

| Component | Implementation |
|---|---|
| Local client | `entry.py client ACTION [REQUEST_ID]`; fixed AF_UNIX socket; validated JSON result and receipt |
| Protected broker | Actual UID/GID/groups from SO_PEERCRED/SO_PEERGROUPS; root-controlled, expiring grant; exclusive file/thread lock; persistent request ledger |
| PVE transport | Fixed192.168.0.50:8006, TLS server name pve, pinned public CA, dedicated broker token; narrow API method/path set |
| Serial transport | VM164 serial0 only; bounded HTTP/chunked/WebSocket implementation; masked client frames; strict termproxy framing; no raw client terminal access |
| Guest worker | Fresh non-root identity; only built-in inspection actions; fixed public files/syscalls; no subprocess, shell, exec or transferred private key |
| Kernel guard | Worker-only no_new_privs/seccomp on Linux x86_64; denies exec, fork/clone, sockets, UID/GID changes, namespaces and selected privileged interfaces |
| Persistent audit | SQLite synchronous=EXTRA, durable reservation before possible send, hash-linked metadata, result hashes, no automatic evidence deletion |
| Deployment | Disabled/null-bound configuration examples; hardened systemd units; root-only state initialization, private token issuance and revoke commands |

No third-party Python packages are required. Python3.11+ with the existing
standard-library SQLite, TLS, ctypes and termios modules is required. Missing
runtime or unsupported kernel/architecture blocks installation/activation;
no dependency installation or security-guard fallback is included.

## Reviewed catalog

| Action | Exact operation | Excluded data |
|---|---|---|
| `identity` | Public approved UUID/channel, installed machine-id, boot-id, worker UID and release digest | Password/shadow data, credential stores, root role files |
| `kernel` | `os.uname().release`, returned in a restricted128-character alphabet | Arbitrary argv, paths or command output |
| `isolation-summary` | Only loopback check and bounded `/proc/self/mountinfo` counts: total, shared, external filesystem count | Raw paths/options/source names, environments, arbitrary journals |

The identity/inspection implementations use Python's fixed OS interfaces instead
of executing id/uname/helper binaries proposed in Phase2. This removes executable
and argument selection entirely. Read-only inspection writes only its necessary
private replay/audit records; it does not promise zero writes by the worker to its
own audit directory. No lab target, system configuration or credential is modified
by an action. There is no mutating/privileged catalog entry or extension RPC.

## Binding and protocol

Public request, one printable-ASCII JSON object plus LF, at most1024 bytes before
the delimiter:

```json
{"v":1,"vmid":164,"vm_uuid":"faeb1db8-0df9-482d-b3e4-f6ccc1602193","serial":"serial0","action":"kernel","request_id":"0123456789abcdef0123456789abcdef"}
```

Caller UID, grant ID and challenge are not accepted from this public request.
The broker obtains the caller identity from the kernel and binds it to the
root-approved grant. It validates fresh VM configuration, current status,
pending changes and its complete self-permission map. It accepts exactly
VM.Audit/VM.Console on `/vms/164` and no other effective grants. Zero-valued
permission entries are propagation flags and still count as grants.

The broker waits for a passive worker advertisement before transmitting an
inspection envelope. It accepts only the exact public qm startup banner, if
present; arbitrary prompts, kernel messages, ANSI or boot consoles refuse.
The worker generates a single-use session nonce. The envelope binds VMID, UUID,
serial0, machine-id, boot-id, worker UID, reviewed release digest, caller UID,
grant ID, request ID and fresh broker challenge. Both sides strictly validate
key sets, types and exact context. Duplicate keys and unsupported actions fail.

Authentication of the submitting process is the Unix kernel peer credential;
management-channel authentication is the broker-only API token over pinned TLS.
The worker's public metadata/nonce is **not** a cryptographic guest attestation.
An administrator controlling PVE or guest root remains outside the lower-role
threat boundary. A compromised worker can fabricate plausible observations.
Every successful public response explicitly marks `guest_report_untrusted:true`.
Responses are decoded data only; returned text never enters an executor.

## Replay, concurrency and uncertain delivery

The broker checks replay before any management request. A process-wide file lock
and thread lock allow one operation at a time. SQLite reserves an ID atomically
and commits/fsyncs before the action can be sent. The worker independently reserves
before inspection. A consumed ID is never executed again, even after restart.

Host states: RESERVED → REPORTED → ACKED. REPORTED requires a receipt from the
same authenticated local client. Any RESERVED, UNKNOWN or unacknowledged REPORTED
blocks **all** later actions, including new IDs. Worker states: RESERVED → REPORTED,
with UNKNOWN on an inspection failure. A stale RESERVED also halts on restart.
The host does not accept a guest replay assertion as proof of execution absence.

After any possible send, timeout, invalid response, boot/config drift or audit
failure yields UNKNOWN and preserves state. There is no retry, refund, clear,
reset, resume, arbitrary-PID kill or reconciliation RPC. Recovery requires
operator review and separately authorized fresh grant/state; existing evidence
must remain intact. Concurrent independent PVE administration must be excluded;
before/after observations cannot atomically lock an administrator out of the VM.

## Limits

Host transaction deadline5 seconds, local request/receipt deadline2 seconds each,
guest action alarm5 seconds, serial frame16KiB, cumulative serial input64KiB,
management response1MiB, mount metadata1MiB/4096 entries, maximum10000 requests
per ledger. HTTP, frames, fragments and control-message loops are separately
bounded. Service templates cap threads/processes and memory. No process is
spawned by the worker; a SIGALRM interruption or partial/failed delivery halts it.

## Important deployment blocker

This Nexus session has UID1000 and membership in sudo/docker/lxd. Membership
alone does not establish effective escalation, but it is inconsistent with an
independently restricted execution principal. Production startup and per-client
authorization reject privileged or extra supplementary groups. **Do not activate
for the current Nexus principal.** Provide a separately restricted submitting
UID/session with no path to root, Docker/LXD, service management or broker files.
This phase neither changed membership nor tested an escalation path.

The broker/worker source in this user-writable repository is not a live security
boundary. Only a separately approved root-controlled deployment, protected
interpreter/dependencies, separate identities and verified OS enforcement can
establish that boundary. See `LIVE-ACCEPTANCE.md`; those checks are NOT RUN.

## Reproducibility and pins

```sh
cd '/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS'
python3 -I -B tasks/proxmox-automation-phase3/tests/run_offline.py
cd tasks/proxmox-automation-phase3/src
sha256sum -c SOURCE-SHA256SUMS
```

`src/SOURCE-SHA256SUMS` covers all12 candidate source files, including the entry
point, hardening and private provisioner. Its SHA256 is recorded in
`evidence/source-pins.json`; that exact digest becomes `release` in both grants.
The installed tree must contain only these files and the manifest: extra modules
or bytecode caches refuse. Use the isolated interpreter invocation shown above.
`SHA256SUMS` at the packet root additionally pins tests, units, docs and evidence.
Independent operator retention of those digests is still required; hashes alone
are not approval or a signature from an operator.

Final test evidence: `evidence/offline-tests.json` and `.txt`. It includes real
AF_UNIX/TLS/PTY/SQLite/process-exit/kernel-guard tests with synthetic remote state,
and explicitly records that actual cross-UID/VM isolation was not tested. The
earlier full-run failure is retained; a fixture inherited group-writable modes
and the ownership validator correctly refused it. The fixture was corrected.

## Public protocol sources

The adapter follows Proxmox's [xterm client](https://github.com/proxmox/pve-xtermjs/blob/master/xterm.js/src/main.js)
and [termproxy implementation](https://github.com/proxmox/pve-xtermjs/blob/master/termproxy/src/main.rs):
ticket authentication, OK prefix and length-prefixed input. The exact optional
banner follows [qm terminal](https://github.com/proxmox/qemu-server/blob/master/src/PVE/CLI/qm.pm).
VM console selection follows the [QEMU API implementation](https://github.com/proxmox/qemu-server/blob/master/src/PVE/API2/Qemu.pm).
WebSocket framing follows [RFC6455](https://www.rfc-editor.org/rfc/rfc6455).
These public-source reads were not connections to the user's Proxmox system.
Installed-version compatibility and token/WebSocket behavior remain live gates.

## Next review

Review `INSTALLATION.md`, `LIVE-ACCEPTANCE.md`, `STOP-AND-REVOKE.md` and
`SECURITY-REVIEW.md`. The smallest privileged request is described explicitly
in the installation file. Installation, restricted identity setup and a trusted
guest-root bootstrap require approval. Activation is a later approval; privileged
Gate6K qualification is a separate decision and is not implemented by this bridge.
