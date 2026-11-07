# One consolidated operator proposal — NOT AUTHORIZED / NOT RUN

Proposed next stage: one finite, independently supervised **VM164 identity-only
broker acceptance request**, after read-only prerequisite review. This is a
proposal for a future authorization window. It does not enable the JARVIS real
executor, connect an adapter, start production JARVIS, issue credentials, install
services, change permissions or alter a guest. The release binding is in
LIVE-READONLY-PROPOSAL.json and release/BUILD.json. Unknown bindings are blockers,
not placeholders that an automation script may fill.

## Stage A — operator verifies prerequisites; no target operation

The operator independently confirms and retains public evidence for all of:

- Exact candidate source/archive hashes and current broker successor release/CA
  pins, interpreter/native libraries and root-controlled installed code/config/
  unit ancestors. The candidate remains offline/inert; the existing broker is a
  separately reviewed component, not an application adapter.
- Actual submitting principal lacks sudo, polkit, docker/lxd/admin groups,
  capabilities, privileged inherited FDs, ptrace and service-management access.
  Broker and guest-worker UIDs/GIDs are distinct, nonroot and independently bound.
  Existing Nexus administrative memberships are not acceptable qualification.
- The separately authorized broker packet's preissuance **no-transport** and
  synthetic secret-canary checks already passed from that actual restricted UID,
  with external acceptance retained. No credential is issued as part of this
  proposal. If installation, a new credential/role/grant, permission expansion,
  guest setup, media/root-console work or any privileged qualification is needed,
  STOP and submit that separate exact setup request first.
- Existing unexpired approved identities, token scope and protected finite grants
  are independently qualified. Effective PVE rights are exactly VM.Audit and
  VM.Console on /vms/164 only, with separation and no propagated/wider scope;
  the original Audit-only observer is unchanged. No root/broad token is used.
- Node pve / VM164 matches UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193,
  downloads:164/vm-164-disk-0.raw, 64 GiB, hardware serial
  g6k164-12821f6b54a2 and serial0 socket, compared with independently trusted facts.
  Actual machine-id, boot-id and installed OS/worker release are supplied by the
  operator; no value is invented here or inferred from a running VM API status.
- VM164 already has no NIC, shared host socket/storage/passthrough, setup media,
  imported credentials or enabled qemu guest agent. Guest networking is loopback
  only. The reviewed worker already owns the exclusive raw TTY; no getty, root
  autologin, kernel/early console or debug shell shares it. No VM change is
  authorized to establish these prerequisites within this window.
- Actual installed Proxmox token/termproxy/WebSocket schema, TLS/CA verification,
  seccomp, systemd restrictions, device/socket DAC and egress controls passed the
  separate broker qualification. Unsupported controls block; no permission fallback.
- Current Authority/checkpoint/witness/recovery ancestry is verified for the
  reviewed candidate evidence. No UNKNOWN external work, incomplete publication,
  pending witness transition, rollback/conflict or expired grant is cleared or
  retried to make the test run. No restored task or overdue schedule is activated.

No claim in this offline packet establishes those installed/production facts.
The sealed broker approval/acceptance packet remains authoritative for its setup
ordering and limits; this proposal does not broaden or replace it.

## Stage B — one identity request, only if Stage A is complete and separately approved

The operator signs/retains the exact release pins, target, actual principals,
existing finite grant ID, UTC start/end and one **32-lowercase-hex broker request
ID** before sending. That ID is the broker protocol's identifier, not a silently
substituted 36-character JARVIS task UUID. No JARVIS-to-broker UUID bridge exists.
Freeze the exact action/payload and retain the original ID before invocation.

The sole proposed guest action is the fixed `identity` inspection. Exclude kernel,
isolation-summary, shell, qualification, packages, guest-agent, model/provider,
network/configuration, storage, power, NIC, credential and trust-anchor operations.
Never access VM162, VM163, the AI server/VM200 or another target to test denial.

After explicit authorization only, the already-installed reviewed restricted
client supports an explicit retained ID:

```text
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py client identity <approved-32-hex-request-id>
```

This is a non-executable placeholder in a proposal, not a command run by this
sprint. Do not omit the ID: the CLI's random-ID default is unsuitable for an
uncertain retry. No automated retry, reconnect resend, second/new-ID workaround,
ledger reset, service adoption or automatic restart is allowed.

Expected permitted effects are one fixed read-only worker inspection and its
already-reviewed durable broker/worker reservation/report/ack audit appends.
The guest report remains `guest_report_untrusted=true`; the operator compares its
public identity fields against independent trusted observations. REPORTED is not
proof of trusted guest truth, and client receipt does not replace broker ACKED
verification. Retain exact request/report hashes, journal sequence and source pins;
exclude tokens, tickets, raw serial/auth lines and unrelated guest data.

Timeout, cancellation, mismatch, incomplete receipt, revocation or UNKNOWN ends
the window. Preserve the original ID and state, stop further sends and use offline
operator inspection. Do not dispatch again merely because identity is read-only.
At the end, the operator closes the existing finite window through its separately
approved stop/revoke control; no unattended/boot activation or new standing grant.

## Acceptance and exclusions

PASS requires one authentic correctly bound report, independently compared public
identity, consistent RESERVED → REPORTED → ACKED audit and a closed window with no
secret exposure or unapproved target/effect. Unmet prerequisites or unsupported
controls remain BLOCKED/NOT RUN. The JARVIS application executor remains synthetic
throughout this external-broker acceptance. Connecting a real application adapter
requires a later independently reviewed integration milestone and authorization.

No approval is requested by executing this document. Review the single staged
proposal and its missing facts before deciding whether any later live window is
appropriate. Privileged Gate 6K qualification and V3 are excluded in every stage.
