# Independent review of all twelve cases

No case was run on pve. Every case has a fixed reviewed payload with no VM tool,
API, guest or production interface. The following evaluates the proposal; only
actual future evidence could establish systemd behavior.

## Common preconditions, budgets and evidence

Common admission C: separate unexpired exact Stage2 grant; approved recorder;
fresh same-host/boot identity; independently proven nobody65534 denial of VM and
private credential authority; local-only NSS/policy behavior; source/binary/ACL
custody; exact path/hash and absent names/jobs/files/aliases; no concurrent writer;
known or explicitly investigated clock convention; sample-to-deadline margin;
creation before minute35 with ≥6min remaining. F01–F07 in REPORT.md must be resolved
before this can be treated as an authorization-ready recipe.

Common source C2: immutable pinned canary at approved public path. Ordinary
callback payloads are exactly `/usr/bin/python3 -I -B -S <public canary>
--approved-nonvm-callback --expected-source-sha256 <pinned hash> --mode <mode>`.
Timeout/late/import cases use the exact literal `-c` code in the catalogue;
missingexec uses one exact nonce-bound absent path. No arbitrary command input.

Common configured service budget B: TimeoutStartSec5s, RuntimeMaxSec10s and
TimeoutStopSec2s; **17s is only the sum of configured phase budgets, not a proved
wall-clock completion guarantee**. Timeout case uses3s active runtime (sum10s).
Timer deadline is sample BOOTTIME+30s. Neither these settings nor client timeout
bound waiting on the host manager, scheduler, kernel or storage. A universal
creation/installer/R22 client limit and remaining-authorization clamp are missing
in R1 and must be supplied. Manual observation ends by cleanup cutoff/expiry.

Common evidence E: pending/consumed ownership ledger, exact argv and hash,
before/after paired clocks and boot ID, raw stdout/stderr and actual client
exit/signal/timeout, two waiting readbacks where the timer can wait, complete
raw timer/service show, selected R3 parser bytes/refusal, all case journal rows,
actual exit fields and invocation correlation. Positive callbacks require
uid/euid65534, intended mode, same host boot and exactly one correlated message.
Missing callbacks/states must not be synthesized from creation acknowledgment.

Common cleanup K: retain pre-stop evidence; establish exact current ownership,
stop only the owned active timer then its potentially dispatched service; no
wildcards/reset-failed/collect. Verify no jobs, MainPID/ControlPID0 and recursively
empty cgroup or corroborated absence. Never stop the deliberately absent dependency
or an unknown/foreign collision. F04 must be corrected in the helper; manual
proof remains mandatory. After expiry only a new exact finite recovery decision
can permit any further host commands.

| Case | Additional exact precondition | Expected result and evidence | Configured budget / observation | Failure and cleanup assessment |
|---|---|---|---|---|
| success | C+C2; mode success; new case name | E; Code1/Status0, Result=success, canary timestamp D≤B≤D+1s, parsed deadline/clock agreement | B; observe to D+15s within cutoff | Reject early/late, wrong UID/boot, missing output or parser mismatch; K. Payload scope PASS; outcome helper lacks boot context (F05). |
| exit7 | C+C2; mode failure | E; one intended failure-mode JSON then Code1/Status7 and Result=exit-code | B; observe to D+15s | Preserve failed service. Expected failure is not a successful exit; K. Scope/design PASS pending actual semantics. |
| missingexec | C; exact `absent-executable-<nonce>` absent throughout; never install a file there | E; desired Code1/Status203 with EXEC journal and no canary | B if service reached; creation may refuse immediately | Creation rejection cannot count as live203/EXEC. Retain UNOBSERVED/blocker and reconcile partial pair with K. Scope PASS; deterministic EXEC coverage NOT established. |
| missingdep | C; isolated Python imports exactly `jarvis_stage2_intentionally_absent_dependency_<nonce>` | E; ModuleNotFoundError, Code1/Status1, Result=exit-code, no success canary | B | Unexpected successful import => stop entire qualification, no module changes. K. Scope/design PASS with root-controlled library baseline. |
| timeout | C; exact literal UID/GID/group check + printed JSON + sleep30 | E; IDs65534 and groups subset{65534}; Result=timeout, actual signal exit, dead/empty cgroup | Start5+active3+stop2s configured; sleep30 must not finish normally | Early assert/import/setup failure is not runtime-timeout proof. Surviving process is failure; K, no broader kill. Scope/design PASS; actual cgroup enforcement unproved. |
| late | C+C2; exact2s sleep/runpy wrapper | E; valid pinned canary and successful exit, callback time>D+1s | B | EXPECTED_LATE_REJECTED_NOT_TIMING_PASS; do not claim scheduler/suspend test. If not late or missing, fail; K. Scope/design PASS. |
| inactive | C+C2; proved waiting; stop timer≥5s before D | E; inactive timer, service never invoked, no callback through D+2s | No intended service runtime; B only as fallback if race | Any dispatch is failure, capture and K. Stop-only-timer distinction is valid. Scope/design PASS pending observed behavior. |
| failedtimer | C+C2; exact `<base>-absent.service` absent in every unit search path; timer Requires/After use only it | E; dependency/activation refusal; no callback; actual timer state/result | No intended runtime; B fallback if unexpected activation | May remain inactive rather than failed. Do not mark failed-state handling live-qualified. K only verified-owned pair; never absent dependency. Scope PASS; live failed-state coverage NOT established. |
| collision | C+C2; first pair proved waiting, exactly one duplicate of original argv/deadline | E; duplicate nonzero, unchanged definitions/deadline, exactly one eventual callback and actual successful exit | Two creation calls require explicit client bounds; service B | Do not retry, regenerate or replace. Any alteration/second invocation aborts; K. Scope PASS; malformed inventory guard FAIL (F03). |
| cancel | C+C2; pair waiting, record cancellation before D−5s | E; timer then service stop; retain intermediate checkpoint; no callback through D+2s; terminal/no-job/empty-cgroup proof | Two5s client stop budgets within remaining authority | A dispatch race/unknown result blocks pass; resume only verified-owned half. Do not actually disconnect console. Scope PASS; helper proof FAIL (F04). |
| rearm-a | C+C2; cancel this distinct name as cancel case | E; cancellation/no invocation, tombstone retained; never a successful fired callback | No intended runtime; observe through original D+2s | Any callback means cancellation failed. Current `outcome()` instead accepts successful firing: FAIL F05. K; no reuse of name. |
| rearm-b | C+C2; rearm-a fully proved canceled; fresh future deadline, distinct base, same original session expiry | E; one successful canary within1s, rearm-a unchanged and never revived | B and remaining original window; no new lease | No same-name restart, extension or promotion after incomplete rearm-a. K. Scope/design PASS conditional on corrected rearm-a gate. |

The matrix covers every case, but it does not supply missing257 behavior. If a
required observation is not attainable within permitted non-VM scope, preserve
UNOBSERVED and keep the affected prerequisite false. A new unsafe injection
(reboot/suspend/resource exhaustion/unrelated service stop) is not an acceptable
way to complete coverage. The present inconsistency in rearm-a/result validation
is repairable offline and should be corrected before any human authorization.
