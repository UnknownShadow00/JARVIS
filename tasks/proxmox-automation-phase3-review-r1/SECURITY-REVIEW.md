# Historical author review context

This copied original author review is retained as context, not the independent R1
review or a new test receipt. INDEPENDENT-REVIEW.md records the actual Astra/high
findings and closure. R1 README/protocol and APPROVAL-PACKET.md supersede the old
readiness stream, receipt-lock lifetime and credential/precheck ordering. The live
isolation and audit limitations below remain unproven and explicitly retained.

# Phase3 author review and evidence limits

This is the implementing agent's review, not an independent security audit or
live Gate6K qualification. Candidate source is complete; activation remains
blocked pending the independent installation and acceptance procedures.

## Security decisions checked in source and offline tests

| Boundary | Enforcement | Validation |
|---|---|---|
| Caller identity | Kernel UID/GID/groups, protected grant, privileged/supplementary-group refusal | Real AF_UNIX credential query plus wrong-user/group tests; positive same-UID fixture explicitly bypasses production group policy |
| Proxmox authority | Separate broker credential, fixed target/methods, pinned TLS/CA; exact self-permission scope | Real TLS over local AF_UNIX pairs with synthetic CA/server; unauthorized paths/credentials, invalid TLS/WS responses rejected |
| Guest execution | Exactly three built-in inspection operations; no exec/subprocess/eval/shell path | Catalog/injection tests; process-local seccomp test in a disposable nonroot Nexus child |
| Replay | Atomic host and guest SQLite reservations before possible action | Duplicate ID/session, persistent uncertainty and real child os._exit/reopen tests |
| Concurrency | Thread lock plus process file lock held through transaction | Contention across threads and independent file descriptors; only one sends |
| Lost result/receipt | UNKNOWN or pending REPORTED halts whole grant, including new IDs | Lost guest response, local disconnect/missing receipt, corrupt/audit-full failure tests |
| Protocol confusion | Exact schemas/types/bindings, printable ASCII, duplicate-key rejection | Escapes, duplicate keys, wrong context/VM/UID/channel, malformed WS/HTTP and banner/prompt tests |
| Resource bounds | Absolute deadlines, input/output/frame/chunk limits, bounded helpers | Trickle timeout, oversize/fragmentation/control-message tests; deployment units additionally cap memory/tasks |
| Untrusted worker | Strict validated result shape; explicit untrusted flag; no interpreted output | Malicious extra fields/control/injection reports fail; plausible fabricated version deliberately demonstrates attestation limitation |
| Secrets/evidence | No normal traceback/body/header logging; token private to broker; public audit metadata/result hashes | Synthetic canaries; root-only provisioner capture fixture emits no output; no real credential opened |
| Trusted files | Descriptor-relative O_NOFOLLOW, ownership/mode/link checks, fixed source manifest and no extra files | Symlink/hardlink/mode/owner/source-drift tests; actual root install still NOT RUN |
| Revocation | Marker/grant/source watcher, active socket close, operator stops socket+service and revokes exact token | Offline active-channel abort and grant/source refusal tests; live PVE/session revocation NOT RUN |

## Corrections made during implementation

- Real SO_PEERGROUPS testing exposed CPython's1024-byte getsockopt buffer limit;
  the implementation now uses that limit and refuses unsupported/oversized cases.
- The first complete guarded run correctly rejected a test release whose
  directories/files inherited the developer umask's group-write permission.
  The fixture now has explicit protected modes. The failed run remains evidence.
- Public client receipts were added so a lost local response cannot be bypassed
  with a new request ID after the guest has already reported a result.
- Replay is checked before any proxy creation as well as atomically at reserve.
- Inspection loops read until EOF or the cap; a short read is not treated as EOF.
- The worker rejects a kernel-owned serial console, configures raw115200 baud
  without flow-control stalls, and has no shell/debug/getty fallback.
- Source trees reject extra modules/caches; grant expiry is clamped by a monotonic
  deadline in addition to wall time. Revocation closes existing channels.
- Broker/private issuer disable process dumping before loading secrets; the
  worker is also undumpable and the service templates set LimitCORE=0.

## Deployment blockers and residual limits

**Current Nexus privilege:** UID1000 has sudo/docker/lxd memberships. No escalation
was attempted; actual capability was not determined. Activation for that identity
is refused. A new restricted agent identity/session, protected broker UID and
independent checks for non-group escalation paths are required. Group checks alone
are not proof of the absence of ACLs, polkit, inherited FDs or other authority.

**Locked guest login:** installation requires a trusted installed-OS root session.
It does not require unlocking passwords. If no session exists, exact maintenance
boot/media/filesystem access needs separate authorization. No live installed
machine-id, worker UID/GID, serial owner or interpreter origin was learned here.

**Compromised guest:** the guest can fabricate its own observations, including
public identifiers. Nonces prevent stale/mixed responses, not malicious truth
claims. No imported private identity/signing credential is added to the guest.
The independent PVE identity/operator checks remain necessary. Seccomp and DAC
reduce authority; they are not a claim of resistance to a compromised kernel,
root, hypervisor or unknown syscall/kernel vulnerability.

**Broker trust:** the broker necessarily holds a VM164 Console credential with
more PVE authority than individual action names. A compromised broker or host
root can use that credential directly. The operator must independently establish
that Codex cannot become that UID/root or read its files. No client-side filter
around an agent-readable token would provide the required boundary.

**Installed compatibility:** public upstream API/xterm sources guided the adapter.
No installed PVE endpoint, token/WebSocket compatibility, tty idle/reconnection,
systemd network filter, seccomp guest behavior or actual cross-UID DAC was tested.
The actual guest service may have different mount-namespace metadata; its summary
does not certify PID1's mounts or satisfy a root Gate6K isolation qualification.

**Audit durability:** real SQLite commit/reopen/process-exit tests passed offline.
They do not establish power-loss/host-loss/filesystem durability. Local hash chains
are not external anti-rollback authority; retain independent checkpoints. There
is deliberately no automatic replay reset, reconciliation or uncertain-action retry.

**Catalog scope:** all actions inspect public metadata and write only private audit
state. Privileged/mutating commands and Gate6K qualification require independent
approval, new reviewed code/digests and an explicit separate authority interface;
a configuration edit cannot add them to this catalog.

## Disposition

Proceed to operator review of the pinned candidate and restricted-identity setup.
Do not grant PVE permissions, install/start services or alter VM164 under Phase3
authority. Live safety acceptance is a future gate, not implied by any offline PASS.
