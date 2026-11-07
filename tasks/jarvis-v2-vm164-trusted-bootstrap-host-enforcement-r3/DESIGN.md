# R3 design — host-owned expiration candidate, Stage1 only

Implemented runtime scope is **Policy A, Stage3, non-root VM164 qualification**.
There is no trusted-root admission and no executable forced-stop path. Stage1
work may pass while the requested real expiration guarantee remains NO-GO.

## Target and trust boundary

Fixed target is node pve/VM164, jarvis-g6k-clean-164, UUID
faeb1db8-0df9-482d-b3e4-f6ccc1602193, volume downloads:164/vm-164-disk-0.raw,
serial g6k164-12821f6b54a2,64GiB, seabios/q35, disk-only order=scsi0,
hotplug0/agent0/onboot0/protection1, serial0 socket, VGA std, no NIC/extra device,
no pending change and the exact old r4 diagnostic ISO. These facts are supplied
by the operator, not independently observed by Codex. The reported host is
pve-manager/9.2.5, kernel7.0.14-6-pve, systemd257 (257.13-1~deb13u1).

The candidate's trusted side is existing host root, protected code/evidence and
system-manager units, outside routine guest root control. It creates no account,
credential, grant, guest network, agent or broker. It cannot defend against hostile
host root, a compromised hypervisor or unauthorized external VM controllers.
Shared storage/HA/autostart/exclusive-controller assumptions require actual review.

## Source components

| Source | Responsibility |
|---|---|
| src/model.py | Strict current snapshot/approval/unit predicates, fixed deadlines, lifecycle and both policy models |
| src/store.py | Exclusive global operator lock, persistent immutable plans, hash-chained events, phase locks/two-attempt bounds, approval replay prevention, evidence-preserving retirement |
| src/host_adapter.py | Default-inaccessible native adapter, root custody/review/qualification/package pins, exact allowlisted argv, bounded process-group execution; native force always refuses |
| src/systemd_codec.py | Conservative systemctl-show parsing, clock-domain normalization and exact timer/service command builder |
| src/preflight.py | Independent, pure prerequisite-record assessment; no host operations or authority |
| src/cli.py | Default dry-run; explicit future host flag plus reviewed installed-path/authorization gates; source/session/grant binding |
| src/stage2_canary.py | Standalone public hash-pinned NON-ROOT/NON-VM callback, no subprocess/network/manager/private-grant interface |
| src/sim.py | Injected fixture backend and virtual clocks, never a live transport |

No native backend is created in dry-run or fixture simulation. The current source
copy in the repository cannot pass the live installed-path/root custody gate.

## Arm and start protocol

1. Verify finite reviewed source, Stage2 record and review-record hashes and scope;
   current host boot identity, exact kernel, root custody and pinned binaries.
   Recheck fixed local package-version output against reviewed pve-manager,
   systemd, qemu-server and pve-qemu-kvm versions. Unknown/missing data blocks.
2. Obtain fresh explicit-current config/status/pending, exact ISO storage mapping,
   regular root-protected ISO bytes/hash/size and actual stopped status. All fields
   are mandatory; no missing-agent/console default or unrecognized device passes.
3. Reserve the one active session and consume its approval digest before unit
   creation. Interrupted setup creates a blocking tombstone, never a fresh empty
   slot. Nonblocking operator lock prevents two concurrent prepare/start/cleanup
   transactions. No operator wait queue can silently run a stale start later.
4. Check unique nonce-bound unit names for collisions. Run a separately named
   bounded Type=exec root selfcheck in Stage3. This canary is not VM termination
   proof. Stage2 callbacks use a separate unprivileged standalone script.
5. Create two distinct transient timer/service pairs, grace and deadline, bound to
   one arm time. Services use Type=exec, fixed absolute source path/session/phase,
   root/root, no restart, private umask, finite runtime/start/stop limits,
   control-group kill,128MiB/16task limits and journal output. No collect/reset-
   failed hides evidence. No arbitrary command strings or shell interpolation.
6. Read back BOTH timer and paired service identities/state/command/deadline and
   execution properties. Timer creation/active-waiting/Type=exec alone is not
   future execution proof. Refuse already-fired, inactive, failed, aliased,
   mismatched, stale, drifting or slow setup. Check VM still stopped afterward.
7. Persist ARMED plus immutable marker only after checks. Start is a separate
   finite action, <=15s from arm. It rechecks current config/digest, stopped status,
   source/session/grant and both unit proofs. Persist START_REQUESTED BEFORE the
   fixed VM164 start; a lost acknowledgment consumes that generation. No retry
   start, root permission, renewal or automatic rearm is inferred.

A creation/readback failure attempts cancellation of each attempted, verified-owned
pair. Unknown ownership or failed cancellation is quarantined/orphaned evidence,
not a claim of clean rollback. No ARMED marker/start is permitted. Existing foreign
collision units are never replaced or cancelled.

## Deadlines and distinct clocks

One host CLOCK_BOOTTIME arm anchor yields grace+540s, deadline escalation+600s,
and required stopped observation by+630s. These are qualification criteria, not
observed guarantees. They never restart at the guest prompt or after a retry.

Timers use absolute FUTURE `OnBootSec=(arm boot time + offset)`, NOT literal540s/
600s host-boot offsets. `WakeSystem=yes` requests a suspend-advancing clock,
AccuracySec1us/RandomizedDelaySec0; neither setting guarantees scheduler latency.
OnStartupSec is not substituted. Absolute construction avoids a drifting anchor
between separately created pairs; past values would fire immediately and refuse
admission.

Operational CLOCK_BOOTTIME and exposed `NextElapseUSecMonotonic` must not be
assumed equal. A hash-bound Stage2 record must establish the actual257 readback
clock domain. Native reads pair BOOTTIME/MONOTONIC samples around show capture,
rejects >1000us uncertainty/offset change, and converts raw deadline to a narrow
boot-time interval. Core checks configured OnBootUSec, raw/offset consistency and
that the exact planned deadline lies inside that interval. Both MONOTONIC and
BOOTTIME output conventions are modeled; UNKNOWN refuses. Historical suspend
may create a large offset; only sample width is constrained, not total suspend.
Actual serialization, wake capability and clock behavior still require Stage2.

## Expiration and concurrency

Timer callbacks bind expected nonce, approval hash and source hash on the exact
immutable plan used by the action. Subsequent store paths stay pinned to that
session directory; old callbacks cannot follow a newly replaced active pointer.
Each phase uses a separate nonblocking execution lock, maximum two durable action
attempts and a terminal marker only after a terminal result. Pre-action interface
failures do not burn the sole opportunity. A retry never changes a deadline.

Before every action, exact current identity/config/digest/media is revalidated.
A durable ACTION_INTENT must succeed; write failure means no command. After a
command, fresh full readback determines observed stopped status, including natural
poweroff/lost-ack races. Errors, missing proof and late triggers remain blockers.
No successful qm exit, service exit or guest receipt proves actual termination.

Grace and deadline have distinct jobs but share host PID1, Python, storage,
Proxmox tools and kernel; they are not independent host failure domains. Current
Policy A deadline reports unexpired-access blocker if grace failed. Modeled B
can propose a separately authorized force, but native runtime cannot do it.

Cleanup first proves actual stopped state, records CLOSING, verifies owned-unit
identity, stops only those units and confirms inactivity. CLOSED requires worker
locks idle and a final stopped snapshot. A worker cannot cross CLOSING/CLOSED into
a replacement generation. CLOSED is absorbing; duplicate cleanup/late callbacks
are historical no-ops, not fresh VM observations. Cleanup interrupted halfway is
resumable only against fresh stopped proof, not while running.

Retirement requires CLOSED, idle workers/inactive units, fresh stopped/config
proof and a distinct finite reviewed approval. It archives the active-pointer
bytes into the old session directory, fsyncs both directories and retains all
journal/plan/approval-use evidence. The same approval digest cannot create another
lease. No timer cancellation/retirement may extend a running session.

## Native boundary and limitations

Only exact argv reconstructions are allowed. All VM selectors are literal164.
No qm stop, unlock, skiplock, protection setter, reset, config mutation, guest
command or generic shell execution is allowlisted. The proposed shutdown argv
includes explicit forceStop0 and must be confirmed against installed help before
Stage3; unsupported syntax fails, with no fallback. Native B raises unconditionally.

Authorization/review/qualification JSON is protected host-root operator attestation,
not a cryptographic signature or independent measurement. Synthetic record kinds
are rejected natively. Source/package changes, expired authority, missing units,
boot-id changes and damaged state fail closed. Do not update code, grants or
qualification records during an active lease. Authorized cleanup/retirement of a
stopped session has separate finite scope; changing a grant cannot reuse an arm.

Transient monotonic units have no demonstrated reboot guarantee. Manager reexec,
unit disappearance/cancellation, host faults and external controllers can defeat
enforcement; verification detects inconsistent supplied/current state but is not
an autonomous redundant hardware fence. PVE snapshots/commands are not atomic
with each other; external API tasks may outlive a killed client. These remain
Stage2/3 blockers, especially for any strict root-expiration claim. No code here
claims to eliminate those host assumptions.
