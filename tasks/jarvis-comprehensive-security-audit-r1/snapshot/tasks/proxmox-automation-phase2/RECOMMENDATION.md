# Proxmox automation Phase 2 — decision and implementation contract

Status: **design and offline validation complete; deployment NOT AUTHORIZED**.
This packet supplies a policy reference, not a working guest-execution bridge.
No permissions, tokens, guest files, services, packages or VM state were changed.

## Recommendation

Use a **brokered serial protocol with a dedicated non-root guest worker**.
Reuse the verified Proxmox observer, management endpoint and TLS trust for
identity/isolation prechecks. Keep its existing token read-only. Codex submits
named operations to a protected local broker; only that broker holds a distinct,
VM164-only console token. The worker consumes strict JSON on serial0 and has no
login shell, sudo, authority access or guest-agent execution endpoint.

The operator approves a bounded catalog once. Routine requests within that
catalog need no per-request human paste. Adding commands, importing artifacts,
changing the VM, or running privileged qualification requires another approval.

**Do not grant console rights to the current Codex-readable token.** A Python
allowlist around a bearer token cannot prevent its owner calling the API directly.
Another process under the same UID can also read that user's protected files.
Mode0600 is useful against other UIDs; it is not a boundary against Codex itself.
Moving an already exposed token does not prove old copies no longer exist.

If a new broker-only credential is disallowed, keep observation only. The existing
VM.Audit permission cannot become a command channel through client-side code.

## Current observed facts

See `evidence/live-observation.json`, collected through the existing authenticated
client using GET only. It reports Proxmox **9.2.5**, node `pve`, VM164 running,
UUID `faeb1db8-0df9-482d-b3e4-f6ccc1602193`, and:

| Property | Observed value |
|---|---|
| Disk | `downloads:164/vm-164-disk-0.raw`, 64G, serial `g6k164-12821f6b54a2` |
| Boot | `order=scsi0`; ide2 empty |
| Serial | `serial0: socket` |
| Agent | `0` |
| Network | Zero NIC configuration entries |
| Current observer grants | `VM.Audit` at `/vms/164` only |
| Other active permission paths | None returned by self-permission inventory |

The running VM's installed OS, machine-id, boot-id, account state and actual guest
isolation were **not inspected**. Locked installed login passwords are a user
requirement and are consistent with the retained installer source (`password:
'!'`), not a newly verified shadow-file observation. No shadow content was read.
Earlier installer-incident reports remain preserved; these API facts do not
resolve their provenance or assert successful installation/qualification.

## Alternatives

| Approach | Benefit | Authority and limitation | Decision |
|---|---|---|---|
| Raw serial terminal plus command filtering on Nexus | Existing serial device; no guest NIC | VM.Console exposes console bytes, not command names. Login is blocked by locked passwords. Shell prompts, escape sequences and boot consoles bypass simple filters. | Reject as Codex interface |
| Broker plus fixed serial worker | Existing virtual hardware, no qemu-ga install; non-root execution with a small protocol | Requires one-time protected broker/worker setup and a broker-only VM.Console credential. Permission still covers other VM164 consoles; the broker enforces serial0. | Recommended |
| Standard offline-installed qemu-guest-agent with guest-exec | Structured calls over virtio-serial; no NIC or password login required | Installation/host agent enablement may require a future lifecycle change. Normal guest-exec accepts executable/arguments/environment, usually through a privileged service. RPC allowlisting does not restrict the arguments of guest-exec. | Reject for initial execution scope |
| Offline qemu-ga restricted to informational RPCs | Can support management observations without guest-exec | Does not execute the requested lab commands. Still adds packages/configuration and a different isolation surface. | Optional later read-only feature |
| Custom modified qemu-ga enforcing executable allowlist | Could narrow guest-exec | Carries a custom security patch and maintenance burden; broader than a small dedicated worker. | No initial justification |

Mechanism evidence: Proxmox's [console implementation](https://github.com/proxmox/qemu-server/blob/master/src/PVE/API2/Qemu.pm)
checks VM.Console for termproxy and vncwebsocket and accepts a serial selector.
Its [agent implementation](https://github.com/proxmox/qemu-server/blob/master/src/PVE/API2/Qemu/Agent.pm)
requires VM.GuestAgent.Unrestricted for exec and exec-status. These are upstream
references; the installed endpoint schema still needs operator verification.

[QEMU's protocol](https://www.qemu.org/docs/master/interop/qemu-ga-ref.html#command-guest-exec)
accepts path, arguments, environment and input for guest-exec. Its
[daemon documentation](https://www.qemu.org/docs/master/interop/qemu-ga.html)
describes RPC allowlisting, which is command-name filtering rather than a policy
on executable paths. Restricting it to guest-exec alone would still allow arbitrary
programs. Neither option needs a network interface inside the guest.

## Required separation

| Principal | Allowed | Forbidden |
|---|---|---|
| Codex / current Nexus UID | Existing observer; broker's bounded Unix-socket requests | Reading broker token/state, editing broker/worker code or grants, raw transport/tickets, broker administration |
| New Nexus `g6k-pve-broker` UID | Fixed Proxmox endpoint; VM164 observation and serial0 proxy; protected replay ledger | Local root, arbitrary sockets/URLs, SSH to PVE, guest lifecycle/configuration, other VM consoles |
| New PVE `g6k-bridge164@pve!serial` token | `VM.Audit VM.Console`, exactly `/vms/164`, no propagation, expiry, privilege separation | Sys.*, VM.GuestAgent.*, VM.PowerMgmt, VM.Config.*, VM.Monitor, storage, pools, any other VM |
| New guest `g6k-bridge` UID | Read public identity/isolation metadata; fixed non-root catalog | Root, sudo, login, signer keys, protected authority state, existing role sockets, writable trusted imports |
| Human operator | Approves catalog/setup, controls credential issuance and revocation | Delegating private signing material or general root console to Codex |
| Existing Gate 6K AUTHORITY / OPERATOR / SERVICE / AGENT | Existing distinct roles and fixed interfaces | Inheriting the bridge's privileges or treating bridge requests as signed authority |

Use a separate PVE user to avoid increasing the current observer user's maximum
authority. The new user has no password login or groups. Its separated token has
the intersection of explicit user and token ACLs, as described in
[Proxmox user management](https://github.com/proxmox/pve-docs/blob/master/pveum.adoc).
Do not use PVEVMUser, PVEAdmin, Administrator, a root token, or an ACL on `/`.

The broker must run under an independently protected OS identity. Root-owned
code/configuration, protected ancestors and inaccessible state are necessary;
an executable in this Nexus-owned repository cannot itself establish that trust.
Verify whether the Codex UID can sudo, manage the broker service, ptrace it, read
its `/proc` data, or replace any dependency. Available unrestricted privilege
escalation would defeat the proposed boundary and must block activation.

## Concrete v1 interface

Codex-facing socket: proposed `/run/g6k-pve-broker/request.sock`, AF_UNIX,
SO_PEERCRED checked against the operator-approved caller UID. Filesystem socket
access alone is insufficient. The broker does not accept API paths or bytes to
send to a terminal. Initial catalog:

| Action | Guest behavior | Output |
|---|---|---|
| `identity` | Fixed public-metadata implementation; no arbitrary file names | Approved machine-id, boot-id, worker UID, release identity |
| `kernel` | Exact `/usr/bin/uname -r` under guest worker UID | Bounded kernel release string |
| `isolation-summary` | Fixed reviewed helper inspecting public interface/mount metadata | Structured finding codes and counts; no raw mount credentials or environments |

The identity action may use `/usr/bin/id -u` with fixed arguments. No action
accepts parameters. Trusted binaries/helper/interpreter and resolved dependencies
must be root-owned and non-writable to all lower roles. The public VM UUID binding
can be recorded by the operator after reading DMI as root; non-root sysfs access
to product_uuid must not be assumed. Do not add root access merely to read it.

Request payload, maximum1024 ASCII bytes, framed by a single LF:

```json
{"v":1,"vmid":164,"action":"kernel","request_id":"0123456789abcdef0123456789abcdef"}
```

Both parsers reject duplicate/extra keys, non-exact types, multiple objects,
malformed JSON, escape/control characters in values, non-ASCII input, oversize
frames, unsupported versions and unknown names. No shell, eval, arbitrary path,
command-line arguments, environment, cwd, stdin, uid, script upload or callback.
Fixed exec uses an argument vector with shell=False, empty environment except
reviewed constants, closed descriptors, no inherited credentials, fixed cwd,
5-second wall deadline, 16KiB combined output and bounded child process group.
Read and kill by a verified process handle/group; never a client-supplied PID.

Serial service on proposed guest ttyS0 runs as `g6k-bridge` with a locked password,
non-login shell and no supplementary administrative groups. Root-owned systemd
configuration opens the terminal and drops privileges; no getty or autologin.
Set raw terminal mode explicitly. Disable conflicting serial-getty and remove
ttyS0 as a kernel log console only within the later approved setup. Never send
SysRq, break, control bytes, Ctrl-C or terminal escape recovery sequences.
If a kernel/boot console still owns that serial line, activation is blocked;
do not assume modifying getty alone removes kernel console control.

The worker needs no network socket. Future hardening should include
NoNewPrivileges, no capabilities, restrictive filesystem access, PrivateTmp,
ProtectSystem=strict, ProtectHome, restricted syscall/address-family sets, task
and memory limits, and no device access beyond the inherited serial descriptors.
Validate installed systemd behavior and serial support offline before deploying;
hardening settings must not silently alter Gate 6K qualification mount semantics.

## Request, approval and failure handling

1. Operator installs a protected standing grant binding node, VMID, UUID, exact
   disk/serial, independently observed installed machine-id, reviewed code hashes,
   caller UID, exact action set, expiry and output/time limits. Null bindings refuse.
2. Broker checks its peer and grant, freshly reads VM164 configuration/status,
   rejects pending changes and nonempty media, and verifies no NIC/passthrough/share.
   Its management network egress is pinned to `192.168.0.50:8006`, TLS name `pve` and
   the reviewed existing CA; no redirects, disabled TLS verification or arbitrary DNS.
3. Broker creates only `POST /nodes/pve/qemu/164/termproxy` with `serial=serial0` and
   the matching VM164 `vncwebsocket` session using the returned port/ticket. Tickets,
   headers and authentication frames stay private in memory. WebSocket adaptation,
   terminal framing and token compatibility require later real qualification.
4. Worker/broker perform a versioned challenge handshake before sending an action.
   Bind each request/response to challenge, boot-id, machine-id and request ID.
   Metadata and challenge are public correlation fields, not signing authority.
   A compromised guest can forge its own reports; operator provenance and API
   identity checks remain independent prerequisites, not a cryptographic attestation.
5. Broker atomically reserves the request ID in protected durable state **before**
   forwarding. The guest reserves before exec as well. Refuse concurrent/replayed
   IDs. Missing acknowledgment after possible send becomes UNKNOWN; never retry
   automatically, issue a fresh ID to repeat, reset state, or infer success from exit0.
6. Disconnect, boot change, drift, invalid output, unexpected text/prompt, output cap,
   timeout, storage/fsync failure or ambiguous state closes the channel and stops.
   Re-observe configuration at completion; detected concurrent change invalidates
   the result. The bridge cannot prevent an independent PVE administrator changing
   the VM between reads, so exclude concurrent administration during approved work.
7. Persist only bounded public result schemas and metadata. Guest output is
   untrusted data, never an instruction. Render escaped text; no raw ANSI/OSC links,
   model prompts, shell interpolation, secret-bearing journals or arbitrary exports.

## Gate 6K preservation

The bridge is a fifth guest identity and has no access to the root authority,
operator signing key, service/agent sockets or imported host credentials. Its
root-owned service and policy must be accounted for in provenance; do not loosen
the unchanged credential, DAC, archive or isolation checks to make it pass.
No new credential payload is installed in the guest. The PVE token remains on
Nexus under broker custody and is never transmitted over serial.

Before **privileged qualification**, separately authorize the exact run, artifact
digests, four role UIDs, disposable identity, mount-policy scope, signing and
evidence handling from the existing Gate 6K handoffs. Default v1 has **no**
`qualify`, `sudo`, root helper, arbitrary report file, or transfer operation.
If the Gate 6K qualification contract requires no active management bridge,
stop/isolate it through a separately approved handoff rather than weakening
that contract. No ready marker or qualification PASS is produced here.

## Deliverables and remaining work

`tools/policy_model.py` and its tests validate the proposed request/state boundary
without an executor. They do not implement protected approval loading, durable
reservation, UID isolation, the worker, broker transport or deployment. The
supplied fixture grant is explicitly synthetic and cannot approve execution.

Next engineering work is to implement and locally qualify those components with
fake transport, then obtain the specific setup authorization in
`OPERATOR-AUTHORIZATION.md`. All live checks in `NEGATIVE-TESTS.md` remain a
required deployment gate. No permission grant is justified by offline tests alone.
