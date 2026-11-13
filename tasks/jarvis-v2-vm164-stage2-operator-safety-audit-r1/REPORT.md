# Independent Stage 2 operator safety audit

**Verdict: REJECT.** The reviewed R1 packet is not ready to request authorization
for the complete proposed live procedure. Prepare a corrected, separately versioned
packet and repeat the affected offline checks before presenting it for approval.
This verdict grants no host action and does not modify either reviewed packet.

The core systemd argv is substantially sound, and the written scope is careful.
The rejection is based on concrete input-validation and case-contract defects,
incomplete finite-command controls, and a missing explicit precondition preventing
NSS/policy inspection from contacting external services. It is not based on the
absence of live evidence that this task expressly forbids obtaining.

## Scope, independence and evidence

Read/hashed every file in the preparation packet: **29 files including its manifest
and seal**, and read/indexed the96 R3 predecessor files. Inspected the actual pinned
canary, systemd codec, preflight/native interfaces, complete generated command
catalogue, every proposed case and all retained test/evidence records. Both trees
are byte-identical to the audit's initial inventory after testing.

This is a separate technical audit pass with newly authored adversarial probes,
not a claim that a distinct human operator/reviewer has signed live evidence.
The same conversation contains preparation history; the required distinct-human
preflight and result signoffs remain outstanding. No model identity is asserted
as evidence of independence or authority.

Task profile: strict/read-only review of the target trees; only the expressly
requested separate audit artifacts and mandatory append-only project log are
written. No Proxmox connection, network, credential access, callback installation,
unit activation, VM/guest operation, host modification, package/provider operation,
JARVIS installation or Gate6K action was performed. Tools executed only local
standard-library tests, reads and artifact writes. No systemd/PVE command was run.

## Requested pass/fail decisions

| Review area | Decision | Basis |
|---|---|---|
| Proposed Stage2 commands as a complete safe operator protocol | **FAIL** | Core timer/service syntax and non-VM payloads are sound at documented-interface level; preflight NSS ordering and unbounded privileged reads/client operations need correction (F01–F02). Environment isolation remains incomplete (F06). |
| Privilege-separation design | **PASS, design only** | Requires actual VM-authority/credential denial, rejects passwd-only conclusions, fixes numeric UID/GID, protects source ancestry and creates exclusively. No live UID proof exists. Manager environment must also be covered before claiming complete isolation (F06). |
| Twelve-case completeness and result correctness | **FAIL** | `rearm-a` positive callback is accepted despite its no-callback cancellation contract; missing callback epoch and incomplete result structures can pass helper checks (F05, F07). Missingexec/failedtimer may legitimately remain unobserved. |
| Bounded cleanup | **FAIL** | Written scoped stop/recovery policy is appropriately restrictive, but cleanup helper accepts missing boot binding and contradictory current identity; all command deadlines/recovery admission must be concrete (F02, F04). |

These are readiness decisions for this exact R1 packet, not claims that a VM was
endangered in this audit or that the harmless callback can operate a VM.

## Exact independent test results

| Executed group | Tests | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|---:|
| Original preparation suite, imported unchanged |71|71|0|0|0|
| Newly authored independent controls and negative probes |30|20|10|0|0|
| **Total newly executed** |**101**|**91**|**10**|**0**|**0**|

The10 failures are assertions of required safeguards that the implementation
currently does not satisfy, not tool errors or expected-failure annotations.
Their names, tracebacks and input code are retained under evidence/ and tests/.
They exercise pure Python or inspect literal command bodies; they do **not**
prove anything about running systemd257. The original tests passed without being
changed or having their recorded results overwritten.

The independent harness rejects subprocess/network/signaling operations and
installs an audit hook rejecting writes/mutations to both reviewed trees.
`tests/run_audit.py` exits1 because it found safeguard gaps; evidence is retained.
The original `tests/run_offline.py` was read but not executed in its sealed folder,
since that runner would overwrite reviewed evidence.

Both integrity verifiers passed. R3's historical294 tests are verified retained
history, **not** additional tests executed during this audit. Pins verified:

```text
R3 source tree:
43ea91000e251b9cf34fadf0466cb5135042a3232686c155de1b4ab5ee1ad3d1
Callback source:
a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa
Preparation manifest:
181620771c9d84aa7874af20b30a632d4e0e53e095678ba1001f34cffb38ba32
R3 manifest:
dd03f4fc5c3b7bf0cd7a5a5beebbabdad5e06ffd4397ab114af280d6fcfc15ea
```

## Severity-ranked findings

### F01 — HIGH: non-network behavior is not established before NSS/policy commands

Evidence: EXACT-STAGE2-PROCEDURE.md step1.4 invokes R06–R09 (`getent`, `id`) before
step1.5's full policy review. R15 invokes `sudo -n -l -U nobody`. The packet warns
that opaque external NSS blocks qualification, but does not make a verified local,
non-network NSS/initgroups/sudo-plugin configuration an explicit precondition of
these invocations. A local executable is not necessarily a local-only operation.

Retained primary `nsswitch.conf(5)` documents pluggable sources, LDAP/winbind and
initgroups; `sudo.conf(5)` documents policy/audit plugins and network group queries.
On an otherwise plausible host configuration these commands can consult external
identity/policy sources before the operator discovers the scope conflict. This
is a potential boundary breach, **not an observation that pve uses such sources**.

Required correction: move bounded file-only review of NSS databases and their
modules/actions, initgroups/group sources, sudo plugins/policy includes and any
remote lookup/logging behavior before getent/id/sudo. Require explicit evidence
that those exact calls cannot initiate network or credential operations; otherwise
stop. Do not disconnect networking, change NSS/ACLs, or test a network service.
Existing prior reviewed evidence can satisfy this only if freshly bound and complete.

### F02 — HIGH: privileged inspection is not actually bounded before allocation

Evidence: src/build_catalog.py:28–29. R19 calls `Path.read_bytes()` and only then
asserts ≤1MiB. R20 reads and fully decompresses gzip bytes before asserting ≤8MiB.
The8MiB stdout limit cannot limit those memory allocations. There is no pre-open
regular-file guard or streaming decompression bound in these bodies. A mistaken,
changed, huge or expanding input can consume resources on the shared host despite
being labeled read-only. No such input was read on pve in this audit.

Two independent static probes fail: whole-file allocation and whole decompression
precede the guard. In addition, EXACT-STAGE2-PROCEDURE.md:36 assigns10s client
limits to R01–R21/show/journal and5s to stops, but supplies no explicit client
limit for **installation, systemd-run creation/duplicate or R22**. A service's
RuntimeMaxSec does not bound a pending manager job, the client, a root installer,
or the preflight interpreter. A command started just before expiry is not clamped
to the remaining authorization duration either.

Required correction: bounded regular/no-follow reads and streaming decompression
with an output ceiling; finite resource-safe input handling before allocation;
an exact timeout/output-budget table for every command including installer,
creation, duplicate and R22; admission based on remaining UTC/BOOTTIME budget.
Specify client interruption and unknown-transaction reconciliation. Do not claim
that a killed client proves a canceled manager transaction or completed fsync.

### F03 — MEDIUM: malformed collision inventory bypasses the collision predicate

Evidence: src/packet.py:143–151. Passing `occupied_units` as a JSON string equal
to the exact already-occupied service name succeeds: `set.intersection(string)`
compares individual characters instead of unit names. No shape check rejects the
string. The existing tests cover a list, not malformed inventory types.

Independent probe fails because `plan()` emits argv despite the reported collision.
The manager may still reject a real duplicate; this is **not** evidence it would
overwrite an existing unit. It is a lost fail-closed admission safeguard.

Required correction: strict array/set-of-canonical-unit-name schema for occupancy
and consumed names; reject strings, mappings, null, invalid entries, duplicates
where ambiguity matters, and unknown/missing capture provenance. Keep native
collision refusal as a second barrier, not a replacement for preflight.

### F04 — MEDIUM: cleanup accepts absent epoch and contradictory current identity

Evidence: src/packet.py:224–246. When both records omit boot_id, `None == None`
satisfies the ownership check and stop argv is emitted. The current record's
`name` is ignored; a contradictory `current.name='unrelated.service'` can also
pass if other copied fields match. Two independent negative probes fail.

The emitted commands remain in the fixed Stage2 namespace; the helper is pure
and never executes them. Written manual ownership/expiry checks would still
protect a careful operator. Nevertheless this is not a reliable implementation
of the ownership proof it is meant to support.

Required correction: require correctly typed, nonempty, matching boot UUIDs,
exact current timer/service identities and paired Unit, fresh capture timestamps,
complete reconstruction of expected properties and source/argv binding. Tie
cleanup rendering to current finite cleanup authority, or explicitly remove any
claim that this helper validates it. Cover partial ownership and transition cases
without ever stopping a foreign collision.

### F05 — MEDIUM: rearm-a and callback-epoch helper checks contradict the procedure

Evidence: src/packet.py:194–219 and EXACT-STAGE2-PROCEDURE.md:234. The procedure
requires canceling rearm-a and proving no invocation. `outcome('rearm-a', ...)`
accepts a successful fired callback as EXPECTED_OBSERVATION. Independently,
`outcome('success', ...)` accepts a callback with no host_boot_id at all. Two
independent probes fail.

Required correction: a distinct cancellation/no-invocation outcome for rearm-a;
only rearm-b can be the success arm. Require expected boot/session/unit/invocation
context for any callback acceptance and retain actual exit/clock data. This is
not satisfied merely by putting a host_boot_id string in a synthetic result.

### F06 — MEDIUM: unit-local empty Environment is not full environment isolation

Evidence: service argv in src/packet.py:22–35 and TIMER-AND-SERVICE-REVIEW.md:78.
The packet checks empty Environment/EnvironmentFiles and uses Python `-I -B -S`.
Those are useful but do not establish absence of manager DefaultEnvironment,
pass-through environment or other manager-generated inputs. Python isolation
does not neutralize the dynamic loader before Python starts. Empty unit-local
properties alone do not prove that a service received no private environment data.

Retained systemd.exec primary documentation describes multiple environment sources
and final UnsetEnvironment processing. No actual host environment was inspected,
no secret was read, and no environment injection was executed in this audit.

Required correction: an explicit preactivation, nonsecret/redacted review of
manager/default environment, relevant drop-ins and PAM/pass-through/credential
sources, with a safe approved minimal environment contract or fail-closed denial.
Do not dump environment values or private credentials to establish it. Ensure
identity and command isolation are checked before any possibly inherited command
can execute; a post-arm property check is not a substitute for this baseline.

### F07 — MEDIUM: “reviewed” result structures can omit mandatory bindings

Evidence: src/results.py:8–39 versus RESULT-FORMAT.md. A record can validate as
LIMITED_OBSERVATIONS_REVIEWED without operator, authorization reference, packet
manifest digest, case unit names, deadlines or observations. It can label the
ordinary success case EXPECTED_NEGATIVE. Three independent negative probes fail.
The structural-only disclaimer is correct, but even the required structure is
not enforced. No test result here authenticates an operator or creates authority.

Required correction: enforce the documented mandatory fields and case-specific
status schema; bind evidence categories/names/invocations/deadlines to each case;
require complete cleanup ownership/disposition. Retain the distinction between
schema consistency, independently rehashed evidence and authentic live provenance.

## Systemd semantics and uncertainty

No positively invalid timer/service property syntax was established from the
available offline primary manuals. The core settings correctly express numeric
nonroot User/Group, Type=exec, paired transient units, absolute boot-relative
OnBootSec, WakeSystem=yes, accuracy/no jitter, finite service runtime, cgroup kill,
null stdin/journal output, memory/tasks/CPU/descriptor/core limits and sandboxing.
`SupplementaryGroups=` does not clear implicit NSS groups; the packet correctly
recognizes this. Type=exec proves exec setup only at service start, not timer arm.

Exact systemd257.13 property parsing, normalization, dependencies, available kernel
sandbox/wake capability, journald retention and compound show serialization remain
unverified. Local manuals are a different version. No mock or259 manual is promoted
to257 host evidence. Explicit `--all` on selected-property readback is prudent;
its absence is not asserted here to be a demonstrated257 bug, since explicit
property selection behavior must be verified against that interface.

WakeSystem's BOOTTIME scheduling and exported next-elapse clock convention must
be separately established. Equal clocks remain ambiguous without matching
interface evidence; UNKNOWN must fail. No suspend/reboot/reexec is permitted to
create a useful offset. Physical wake, manager survival and VM termination remain
outside this qualification. The [case matrix](CASE-REVIEW.md) assesses all twelve
cases, configured budgets, evidence, failure and cleanup requirements.

## Forty-five-minute boundary and recovery

The **written authorization policy passes** these checks: explicit UTC expiration,
≤2700s duration, independent BOOTTIME checks, creation cutoff at35min, cleanup
reserve, no automatic extension, failure evidence preserved, no VM stop/guest root,
no reboot/suspend/reexec. Blank/expired approvals cannot be used. It correctly
forbids commands under an expired grant and does not invent unlimited emergency
privilege. Further cleanup needs a **new separately finite, exact owned-unit-only
recovery authorization**, not a renewal of testing or a broad root permission.

The **implemented/proposed operational bound is incomplete**: F02's client/input
bounds and F04's ownership checks need correction. The pinned canary has no
expiry argument/check, so a queued activation may run after expiry when a manager
recovers; RuntimeMaxSec bounds active runtime, not elapsed authorization. This is
openly disclosed in R1, not a newly discovered hidden VM-control path. It cannot
be called prevention of all post-expiry execution. Before approval, define the
payload-expiry contract and, if expiry refusal is required, add a separately
reviewed bounded launcher/guard in a new packet while preserving the pinned canary.
No software guard supplies a hardware-level guarantee through host failure.

## Missing host prerequisites and readiness conditions

All historical operator facts must be refreshed: identity/kernel/boot, versions,
actual paths and hashes/ACLs/capabilities, local NSS/policy behavior, nobody groups
and processes, independently established absence of VM authority and private
credential access, callback/staging custody and exclusive destination, complete
unit paths/aliases/jobs/collisions, installed matching interfaces, cgroup mount/
ControlGroup layout, WakeSystem/kernel support, clocks, evidence recorder and
its exact budgets/custody, supervisor/reviewer, nonce and fixed UTC/boot bounds.
No new UID, permission alteration or credential probe is an allowed workaround.

R3's reboot/reexec/private-install/VM-specific prerequisites must stay false or
unqualified. A favorable awake-host session cannot promote them. Correct F01–F07
in a new preparation revision, rerun the original and independent probes, reconcile
the twelve-case outcomes, and review the concrete finite authorization/recovery
fields. Only then reconsider whether to present that revision for human approval.

## Precise first supervised operator action

**Now: no host action.** Correct and re-review the offline packet; Stage2 is not
authorized. After a corrected revision receives separate finite approval and the
operator confirms console identity and starts the approved evidence recorder,
the first host command is exactly the existing **R01-clock** argv: `/usr/bin/python3
-I -B -S -c <the fixed CLOCK_CODE body>`, reading only boot ID and paired clocks.
The complete byte-for-byte array and preconditions are preserved in
[FIRST-SUPERVISED-ACTION.json](FIRST-SUPERVISED-ACTION.json). It is a proposal, not
permission. Do not install the callback, invoke getent/sudo or create a timer first.
