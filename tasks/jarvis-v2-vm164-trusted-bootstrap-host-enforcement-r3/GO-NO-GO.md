# GO / NO-GO

## Current result

**PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY** is the Stage1 engineering
status if the sealed packet verifier and recorded checks pass. It is not host
qualification, temporary-root authority, installation readiness or Gate6K.

- GO: local dry-run, source/integrity review, simulated tests and fixture replay.
- NO-GO: any current pve connection, host placement, real unit/timer activation,
  VM operation or guest command. No stage beyond1 is authorized by this prompt.
- NO-GO: strict guest-root expiration with current Policy A. ACPI refusal is an
  explicit hard blocker and must not silently become force.
- NO-GO: Policy B runtime. It is offlined/modeled only, absent from the native
  command allowlist and unconditionally denied by NativeBackend.force.
- NO-GO: Stage4/root bootstrap in this build even after a good Stage3/A trial.
  Runtime grant purpose/stage is restricted to Stage3/non-root/A.

## Stage2 admission checks

Require separate finite approval of the exact harmless non-VM setup, source pin,
existing unprivileged callback UID, binary custody and an exclusive destination/
unit namespace. No credential/grant creation or replacing unrelated files.
Do not assume currently unknown paths, package versions, resource behavior,
show serialization, readback clock domain or wake capability. UNKNOWN remains
missing. No real privileged timer unit is harmless enough to run without approval.

A callback/service created, active timer, Type=exec start or one canary success is
not expiration proof. Stage2 needs actual raw firing/failure/clock/state/journal
observations and independent review, not fixture output. Reboot/reexec/suspend
or shared-node impact needs separate scope; unresolved survival cannot be marked
PASS just because those tests are inconvenient.

## Stage3 admission checks

Require completed applicable Stage2 evidence plus a separate exact finite
Stage3/non-root/A approval. Fresh independently trusted current/status/pending,
exact identity/hardware/disk/ISO/config digest, stopped status, code/source/package/
binary pins, root-private custody and consumed-approval/session state all pass.
Both transient pairs and exact commands/deadlines/properties must be read back
before start; start<=15s from arm. Collision, late/stale/fired/inactive timer,
unknown source/session/grant, partial setup or evidence failure means NO START.

No additional VMID/node/device route exists. A post-arm hardware/digest change,
lock, API error, damaged journal, missing binary, manager/host change or unknown
ownership yields a blocker, not a bypass or a positive termination result.

Success of an actual trial requires correlated approved argv, invocation/result/
clock evidence, supported Proxmox task semantics and fresh actual stopped state
within the specified criterion. Command acknowledgment or favorable mock is not
sufficient. Cleanup/cancel/retire only after actual stopped, idle workers and owned
inactive units. No active-lease extension or reused approval to create a new arm.

## Persistent unresolved blockers

No real systemd257/PVE9.2.5 qualification has occurred. Additional dependency/
package-version/custody facts and exact qm shutdown/stop behavior are unknown.
Timer serialization/clock domain, WakeSystem, scheduling, execution/resource
limits, manager reexec/reboot, journal durability, locks/protection, queued API
tasks, exclusive-controller races and actual ACPI/termination all need later
approved evidence. Two jobs share host failure dependencies. Neither policy now
provides a demonstrated unconditional expiration guarantee under those faults.

Any required unresolved assumption stays a blocker. Policy B authority alone
would not turn it into PASS. A safer root-free one-shot diagnostic is a separate
possible design, not a shipped guest bootstrap in this packet.

Exact next human action: review AUTHORIZATION-REQUEST.md for Stage2-only approval;
keep VM164 stopped and unchanged until that separate scope is granted. No new
root prompt, JARVIS installation, production change, Gate6K or V3 is implied.
