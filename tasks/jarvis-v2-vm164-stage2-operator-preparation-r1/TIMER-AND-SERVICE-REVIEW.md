# Timer and service review

Scope: source/arguments/retained local documentation. No live systemd observation.
Local primary manuals are systemd 259-era documentation, not proof of the reported
257.13 host. Hashes and relevant text are retained in
`evidence/LOCAL-MANUAL-EXCERPTS.json`; R3's earlier independent review is in
`../jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/evidence/OFFLINE-PREREQUISITE-REVIEW.md`.
No web retrieval was performed because this task prohibits network operations.

## Timer argv and actual clocks

`src/packet.py::timer_argv` and `COMMAND-CATALOG.json.create` contain every argument.
They target the system manager explicitly; use `--unit=<exact base>` to name
`<base>.timer` and `<base>.service`. `--on-boot` is a duration since host boot,
not a delay since timer creation. Compute its absolute value from a fresh
BOOTTIME sample plus30s, with six decimal places. No `OnStartupSec`, relative
restart, `--user`, `--scope`, `--collect`, `--wait` or shell worker is substituted.
The `--` separator terminates systemd-run options before the absolute executable.

| Timer property | Required setting/readback and reason |
|---|---|
| WakeSystem | yes. Documented to use suspend-advancing CLOCK_BOOTTIME. Existing authorized root configures the system timer; callback UID stays65534. |
| OnBootSec / TimersMonotonic | Exactly one OnBootUSec entry equal to planned absolute boot microseconds. Capture all other timer scheduling fields; no extra calendar/active/unit-active trigger. |
| AccuracySec | 1us; read AccuracyUSec=1us/equivalent exact parsed microsecond. This is timer coalescing tolerance, not a latency guarantee. |
| RandomizedDelaySec | 0; read RandomizedDelayUSec zero. |
| RemainAfterElapse | yes; retains elapsed timer for inspection, not permanent evidence storage. |
| Persistent | no. Calendar catch-up is not relied on for boot-relative timers. |
| Unit | Exact paired service, never an existing service. |
| ActiveState/SubState/Result | Before ordinary firing loaded/active/waiting/success; LastTriggerUSecMonotonic zero. Failed/inactive/fired/not-found cannot admit a trial as armed. |
| NextElapseUSecMonotonic | Positive raw timestamp; domain must be qualified below. Never infer from the property's name alone. |
| Requires/After | Only failedtimer adds its absent same-namespace dependency. Read back dependencies; all other cases may contain normal manager defaults but no unreviewed trigger/action/credential dependency. |

The installed systemd257 interface and actual readback must establish support for
WakeSystem, all timer/service properties, and transient unit creation. A rejected
WakeSystem=yes or missing alarm-clock capability blocks the proposed mechanism.
**Do not fall back to WakeSystem=no.** Successful creation/readback/firing with
WakeSystem=yes establishes only this ordinary awake-host trial. It does not prove
physical wake from suspend. No suspend, reboot, reexec or restart is permitted.
The serialized fields may normalize values; review documented equivalents and
preserve raw bytes. Unknown serialization remains failure for the strict R3 codec.

## Clock convention decision

The local `systemd.timer(5)` describes WakeSystem=yes as selecting BOOTTIME;
`org.freedesktop.systemd1(5)` describes the exported next-elapse timestamp as
MONOTONIC. R3 supports either *qualified* readback convention. Its configured
OnBootUSec remains the exact intended BOOTTIME duration.

For each capture record B1, M, B2, yielding offset interval L=B1−M, H=B2−M.
Use the envelope of before/after samples around show. Require L≥−1000us,
L≤H, H−L≤1000us and no offset change outside that envelope throughout the trial.
Do not constrain the total historical suspend offset to zero. Let D be planned
BOOTTIME deadline and R be raw NextElapseUSecMonotonic:

| Observation | Decision |
|---|---|
| R+L ≤ D ≤ R+H, and R != D | MONOTONIC is consistent; repeat across both waiting captures and second ordinary case; require no contradictory matching-version interface evidence. |
| R == D, and D not in [R+L,R+H] | BOOTTIME is consistent; repeat and investigate any documentation conflict. |
| Both hypotheses hold (common when clocks are equal/close) | UNKNOWN from measurement. A reviewer may resolve only with retained exact installed-version interface/source evidence specifying this property and matching observations. A 259 manual alone is insufficient. Otherwise FAIL/UNKNOWN. |
| Neither holds, value zero/infinity/missing, capture skew too wide, offset drift, host boot changes | FAIL; no clock qualification. |
| Exact-version documentation contradicts the observed unique hypothesis | FAIL pending a new review; do not choose the convenient hypothesis. |

Normalize MONOTONIC to `[R+L,R+H]`; normalize BOOTTIME to `[R,R]` after verifying
sample quality. D must lie inside. Compare callback BOOTTIME directly to D:
ordinary success must satisfy 0≤callback−D≤1,000,000us. Late is never a timing
PASS; the dedicated 2s-delay case passes only as a *negative detection* result.
Journal timestamps use their own documented domain; retain them separately.
Actual CLOCK_MONOTONIC/BOOTTIME readings do not prove survival across host faults.

## Service contract and readback

All service properties below are exact argv values. Capture full show output
and compare them, and capture `ExecMainCode`, `ExecMainStatus`, `ExecMainPID`,
`ExecMainStartTimestampMonotonic`, `ExecMainExitTimestampMonotonic`, `MainPID`,
`ControlPID`, `ControlGroup`, `Job`, `InvocationID`, `Description`, `Names`,
`FragmentPath`, `SourcePath`, `CollectMode`, `SuccessExitStatus`,
`RestartPreventExitStatus` and `Result`. No alternate executable or extra command
is acceptable. `Environment`, `EnvironmentFiles`, `ExecCondition`, `ExecStartPre`,
`ExecStartPost`, `ExecStop`, `ExecStopPost`, credential-loading/import settings,
OnFailure and OnSuccess must be empty; unexpected inherited settings block.

| Properties | Required values |
|---|---|
| Type/User/Group | exec / 65534 / 65534; callback JSON and journal must independently confirm uid/euid. |
| SupplementaryGroups | Empty requested list; this does NOT remove implicit NSS memberships. Preflight must prove the only resolved group is65534; timeout probe checks actual groups. |
| Restart | no; no on-failure restart, looping or retry. |
| RuntimeMaxSec | 10s normally;3s for timeout. Read RuntimeMaxUSec. |
| TimeoutStartSec / TimeoutStopSec | 5s /2s; read USec equivalents. These are manager limits, not guaranteed kernel deadlines. |
| KillMode / SendSIGKILL | control-group /yes; termination is limited to this owned service's cgroup. No manual signal to unrelated PIDs. |
| UMask | 0077. |
| MemoryMax / TasksMax | 134217728 bytes /16. No stress testing of these limits on shared pve. |
| CPUQuota / LimitNOFILE / LimitCORE | 10% (CPUQuotaPerSecUSec=100ms equivalent),64/0; retain soft/hard and accounting context. |
| StandardInput / StandardOutput / StandardError | null /journal /journal. No tty, console, interactive credentials or user input. |
| NoNewPrivileges / RestrictSUIDSGID | yes /yes. |
| CapabilityBoundingSet / AmbientCapabilities | empty /empty. Review actual timeout process CapEff, CapPrm, CapInh and CapAmb zero; bounding set should be zero. |
| PrivateNetwork / PrivateDevices / PrivateTmp | yes /yes /yes. No external networking; private network namespaces alone do not hide filesystem UNIX sockets. |
| ProtectSystem / ProtectHome / RestrictNamespaces | strict /yes /yes. |
| InaccessiblePaths | -/etc/pve -/var/lib/pve-cluster -/run -/root -/home; missing paths permitted by dash prefix. Inaccessible namespace views supplement, never replace, the underlying nobody permission audit. |

Type=exec detects process setup/execve failure when the service is actually
started, not at timer creation. Successful exec of Python does not prove script
completion or import success. RuntimeMaxSec is appropriate to Type=exec; a
oneshot substitution would change semantics and is forbidden.

The sandbox additions restrict the Stage 2 probe. They do **not** qualify R3's
root worker security contract or prove that every systemd resource limit was
stress-tested. A denied namespace/sandbox setup is a blocker; do not remove a
property to get a green canary. No property is added/changed in the sealed R3.

## Exact R3 selected-property captures

Timer comma list:

```text
Id,LoadState,ActiveState,SubState,Transient,Result,Unit,WakeSystem,AccuracyUSec,RandomizedDelayUSec,LastTriggerUSecMonotonic,NextElapseUSecMonotonic,TimersMonotonic,RemainAfterElapse
```

Service comma list:

```text
Id,LoadState,ActiveState,SubState,Transient,Result,Type,User,Group,Restart,KillMode,RuntimeMaxUSec,TimeoutStopUSec,ExecStart,ExecStartPre,ExecStartPost,ExecCondition,InvocationID,Environment,EnvironmentFiles,UMask,MemoryMax,TasksMax,SendSIGKILL,StandardInput,StandardOutput,StandardError,TimeoutStartUSec
```

R3's selected raw output bound is65536 bytes. Preserve larger full show output
separately; do not feed arbitrarily truncated bytes to the parser. Run parser
analysis only on captured files on the offline review workstation. It performs
no host calls. Any parser refusal is retained, not “fixed” by changing raw bytes.
