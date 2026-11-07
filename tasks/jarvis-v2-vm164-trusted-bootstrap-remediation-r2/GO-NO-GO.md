# Explicit gates

## Current verdict

**GO: completed offline engineering/review only. NO-GO: start VM164 for root.**
All receipts from these tools deny real boot authority, even if every supplied
claim is internally consistent. There is no deployable host fence runtime backend
in this packet. Offline JSON saying backend_qualified=true is only a simulation.
User-reported disk-only boot correction removes that reported configuration
problem; it does not discharge H1–H4 or provide independent live readbacks.

## Q gate — prerequisites before any supervised non-root qualification

Every item must be concretely available, reviewed and explicitly authorized:

1. Fresh trusted pve/VM164 current config, status/current and pending observations,
   exact UUID/original64GiB disk/serial, no NIC/agent/extra channel, hotplug0,
   protection1, onboot0, disk-only order=scsi0, correct effective view semantics.
   No ambiguous/saved/pending-only/stale record is sufficient.
2. Installed host PVE/QEMU/systemd versions and supported fixed-target commands
   recorded without secrets; an implemented/reviewed host expiry backend under
   root-protected existing administrator custody. Its source/package hash and
   actual invocation paths must be pinned in a NEW execution/qualification packet.
   **This backend is missing today. Do not improvise it from this policy model.**
3. Backend cannot be disabled by guest root, guest cleanup, console loss or death
   of the bootstrap launcher. Both independent enforcement jobs are created,
   read back active with exact fixed actions/target and deadlines while VM164 is
   stopped. Boolean is-active alone is insufficient. Missing/failed worker means
   no start. Worker/timer ownership, restart/persistence and clock semantics are
   part of qualification, not assumed systemd behavior.
4. Deadlines bound to host boot/session/target/config and suspend-inclusive time:
   graceful revocation request at arm+540s; hard-stop escalation at arm+600s;
   actual stopped proof required by arm+630s. No renewal, cancellation while
   running, unscoped retries, host/guest automatic restart or retargeting. Arm to
   first start <=15s or do not start. Define identity-loss behavior before trial.
5. Explicit operator approval of VM164-only hard termination and crash/preservation
   risk, approved recovery if it fails, trusted console and bounded resources.
   No entire-host power operation or another VM may be used as a fallback.

Without all five, **NO-GO even for the qualification boot**. Next work may collect
separately approved read-only facts; that is not a permission to install a fence.

## R gate — prerequisites before the revised root session

Q must have passed through real supervised non-root trials, with independently
retained evidence, rather than only assertions or command acknowledgments:

- Deadline firing, true stopped state, supported API/current/pending semantics,
  launcher loss, console loss, guest shutdown failure and isolated cleanup-worker
  failure cases all qualified. A hanging guest or stop failure is not a PASS.
  Fault methods must have their own preservation scope; do not use root to test
  whether the first protection works. No root/debug arguments in these trials.
- Host backend source/custody and hardware/config/version applicability reviewed;
  hard-stop latency within the specified observation deadline. No blanket claim
  about every kernel/hypervisor failure; unknown required assumptions stay blockers.
- Explicit NEW finite root-session approval binds the reviewed backend hash,
  target, exact new ISO/helper/probe pins, one root boot, observation deadlines,
  cleanup, accepted emergency hard-stop action and a final stopped state.
- While stopped, perform separately approved media-only swap from the retained
  old r4 ISO to candidate09185f1f69108ab1. Preserve both objects and original disk.
  Recheck order=scsi0 (do not infer/reissue a correction), current config/content/
  pending and fresh digest. The old guard is not silently relaxed; use the r2
  state gate with its fixed new image identity for consistency only.
- Prearm a NEW fixed host fence for that approved boot, inspect it and bind the
  new digest while still stopped. Do not borrow a timer from a qualification boot.
  No root start until the actual enforcement and stop/recovery controls exist.

## D gate — attached diagnostic completion

Required: correct trusted root/host session, full medium/helper/probe hash checks
before execution, immutable read-only media, unchanged raw probe output with
optical_media_present=true, same observed boot-id, captured rows/hash, independent
cleanup evidence, fresh true stopped readback and no pending changes. Missing
record or failed validation means INCOMPLETE. Do not convert it to media-free
preflight. Original installer must continue to reject it (regression-tested).

No live ejection occurs; stop first, then any media detach under explicit scope.
Clean normal-boot verification requires its own explicitly permitted boot/generation
and newly prearmed fixed fence while stopped, after retiring the previous fence
against stopped proof. It must not extend an active root lease. Keep no NIC/agent,
inspect unsaved kernel arguments and locked login, and finish stopped/empty.
Any unauthenticated root, persistent debug indicator or unverifiable final state
is NO-GO; do not repair credentials or boot files within this procedure.

## Installation / Gate6K gate

Always **NO-GO from this packet**. Diagnostic data may inform later engineering,
but optical absence, native/runtime/rootfs/bwrap/mount/isolation compatibility,
existing restricted identities, protected custody, exact package/source pins and
fresh installation-boot bindings remain separate. No ROOT/GO JSON file grants
JARVIS installation, activation, provider access, real executor or Gate6K rights.
