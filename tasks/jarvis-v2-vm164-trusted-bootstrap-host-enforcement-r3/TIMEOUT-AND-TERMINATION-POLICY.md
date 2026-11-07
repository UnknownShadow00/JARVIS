# Termination policy and timing — no guarantee from mocks

## Explicit policies

| | Policy A: preservation first | Policy B: strict-expiration proposal |
|---|---|---|
| Initial operation | Bounded VM164 ACPI shutdown request | Same bounded graceful request |
| Guest refuses/hangs | Record hard blocker; do not force | A forced VM164-only termination may be proposed |
| Disk consequence | Avoid intentional crash escalation; ordinary guest writes/shutdown can still fail | May lose data or damage Ubuntu filesystem/journal; cannot promise disk preservation |
| Current native capability | Implemented candidate, gated to separately approved Stage3/non-root qualification | **Not executable in this build**, regardless of JSON/flags |
| Authorization | New finite reviewed Stage3/A scope after Stage2 | Distinct explicit forced-stop/data-loss authorization AND a separately reviewed promoted implementation/qualification |
| Access-expiration guarantee | **NO** if ACPI fails | **NOT ESTABLISHED**; simulation is insufficient; locks/host/identity/API failures may prevent strict termination |
| Trusted-root recommendation | NO-GO for a strict lifetime requirement | NO-GO in current build, even if someone supplies an approval object |

The conflict is real: preserving guest disk state and ensuring a hard end to
uncooperative privileged guest access cannot both be promised. This packet never
silently chooses force to make the deadline pass. It never bypasses protection,
locks or Proxmox semantics. `FORCE_RUNTIME_ENABLED=False`, native force raises,
and qm stop is absent from the actual subprocess allowlist. A mode switch or
new JSON cannot activate B. A future code promotion changes source pins and needs
new independent review plus separate explicit authorization before any trial.

## Proposed immutable schedule

- Arm while stopped; first start must occur within15s, with all readbacks checked.
- Grace request due at arm+540s. Grace worker normal work budget40s including
  native authorization/package recheck; service runtime45s/stop5s/start10s.
- Deadline worker due at arm+600s. Native A observes/reports blocker; only offline
  B model proposes force. Total normal work budget25s includes authorization;
  service runtime30s/stop5s/start10s. No new budget starts after authorization.
- Actual stopped observation required by arm+630s for qualification. A request
  at600s is NOT proof of expiry by600 or630. A >1s late callback or stopped result
  beyond the criterion is LATE/failure, never an on-time pass.

Local read/show commands have <=2s communicate budgets; timer creation3s,
start8s, shutdown client17s for a proposed15s graceful request, unit stop7s,
exec selfcheck12s for its10s service. Each process-group kill/reap has one bounded
1s attempt. Every call is clamped to the shared remaining operation budget, with
1s reap reserve. Cleanup/canary overhead can consume headroom; exhaustion blocks
new work rather than extending deadlines. No hidden sleep or unlimited retry.

The shutdown flags and client/task timing are **unqualified proposals** until
installed qm help/source and real task behavior are reviewed. A killed client
is not proof that its PVE task stopped or its guest did. Errors are not silently
retried with forceStop1, skiplock, unlock or protection changes.

## Timing limits that code cannot prove

Linux scheduler latency, exec/fork and filesystem/kernel hangs, failed systemd,
OOM, damaged evidence storage, missing dependencies, package updates, host reboot,
manager reexec or task locks can invalidate a timeout assumption. systemd limits
and Python communicate timeouts do not prove an absolute hardware termination
bound. Clock normalization arithmetic is tested, but actual257 field conventions,
WakeSystem capability and observed callback/command latency remain unverified.
Two transient jobs share the same host failure dependencies.

Strict pre-action evidence is mandatory. A corrupt/full store blocks the command,
leaving a reported expiry blocker. Post-action evidence failure cannot undo an
action; the result remains incomplete. This fail-closed authorization/preservation
choice is another explicit reason no unconditional expiration guarantee is made.

A host reboot invalidates the old boot epoch and transient-unit assumptions;
source/package/grant changes invalidate the session. No automatic restart,
renewal or stale-lease recovery is authorized. External-root/HA/controller races
and queued PVE task completion need real qualification, not a favorable fixture.

## Safer direction

A hash-pinned **noninteractive read-only diagnostic**, without a passwordless tty,
login unlock, SSH/network/agent or arbitrary command channel, can avoid temporary
interactive guest-root exposure entirely. It could be delivered through a newly
reviewed one-shot boot/task path with null stdin, narrow immutable command and
private evidence. It still needs boot-chain/media/source verification and bounded
job/shutdown qualification; it is not implemented or approved by this host sprint.
If forced-stop/crash risk is unacceptable, prefer that separate engineering path
rather than pretending Policy A enforces a strict root-access expiration.
