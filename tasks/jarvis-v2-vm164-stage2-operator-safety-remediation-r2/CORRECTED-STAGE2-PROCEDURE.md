# Proposed supervised Stage 2 procedure — R2

**NOT AUTHORIZED. Do not execute these host commands now.** The immediate action is a new independent offline Astra audit of this packet. Every command below is a future proposal for the existing local administrator console after separate finite authorization. There is no connection, credential, root-shell startup or automatic executor step. No VM, guest, production, Gate 6K, reboot, suspend, manager restart/reexec or JARVIS operation is permitted.

The authoritative exact argv arrays are in `COMMAND-CATALOG.json`; `src/catalog.py`, `src/inspection.py` and `src/proposals.py` preserve the complete literal Python bodies. Variable arguments are mandatory fresh inputs, not shell substitutions. `src/render.py` prints exact per-case argv and bounded command envelopes locally and never executes them. Names and deadlines cannot be prefilled without inventing host facts. `evidence/SYNTHETIC-12-CASE.json` is only a regression artifact, never an execution plan.

## 0. Finite authorization and recorder prerequisites

Obtain independent review first, then a separate human authorization tied to this packet's manifest and source hash. Fill the immutable original-null `templates/PREFLIGHT-INPUT.json` in a new external evidence record. Mandatory inputs:

- Named operator and distinct reviewer; signed authorization reference; precise `starts_utc` and `expires_utc` in `YYYY-MM-DDTHH:MM:SSZ`, at most 2,700 seconds apart; fresh 32-lowercase-hex nonce. No example timestamp or nonce is usable.
- Existing local pve console identity and trusted clock/boot baseline through approved console custody; expected boot UUID; initial BOOTTIME and MONOTONIC bracket. R01 refreshes and binds these, but cannot retroactively supply permission for itself.
- Fresh hostname/kernel, exact Python 3.13 patch version and package versions; executable/loader/library paths, symlink chains, hashes, modes, capabilities, ACLs and custody. Reported host facts are historical, not new measurements.
- Complete local mounts/NSS/PAM/sudo/polkit/Proxmox/credential-access review; existing nobody/65534 with no supplementary privileged membership or other processes; manager/default/drop-in environment and command-source review with no secret output.
- Complete UnitPath and namespace absence proofs, callback staging path/hash/custody and approved destination absence; exact installed documentation and clock-domain basis; cgroup/journal/recorder support.
- A console-side recorder independently reviewed for exclusive evidence creation, no secret output, null stdin, minimal environment, bounded output, process/resource timeouts and exact process-exit/clock capture. No generic root shell or unbounded execution wrapper is supplied here.

If any prerequisite is missing or cannot be established without prohibited access, mark BLOCKED. Do not request credentials or change policy. Before every future command compare both UTC and BOOTTIME with the original limits. Require the entire command cap plus two seconds remaining; never shorten a timeout into presumed success or move expiry. No creation/duplicate/install after minute35 or with less than six minutes remaining. All trials are sequential. Maximum case budget: 90 seconds, including observation and scoped cleanup; final full-session archival review uses the reserved closure period. If the complete remaining budget does not fit, do not start that case.

Use only this parent environment, with no inherited arbitrary values:

`{"LANG":"C.UTF-8","LC_ALL":"C.UTF-8","PATH":"/usr/sbin:/usr/bin:/sbin:/bin"}`

See BOUNDED-INPUT-AND-TIMEOUT-REVIEW.md for the exact cap of every command. Do not use `env -i` as an unreviewed substitute that starts under an already hostile loader environment; the trusted recorder must construct the child environment directly before exec. Do not dump environment values.

## 1. First read-only action and local gate (target minutes 0–10)

The first host argv is **exactly** `FIRST-SUPERVISED-ACTION.json.argv`, byte-for-byte equal to Astra's R01 array:

`["/usr/bin/python3","-I","-B","-S","-c",<fixed CLOCK_CODE>]`

Its whole body is in that JSON file, not a placeholder to improvise. Preconditions: corrected packet re-reviewed; separate finite approval; confirmed existing local console identity; trusted Python/loader; recorder active; both bounds valid and 12 seconds available. Capture raw stdout/stderr, exit, argv and receipt time. Require exit0, valid boot UUID matching console custody, finite UTC and B1/M/B2, and `0 <= B2-B1 <= 1000 us`. Use B2 as the conservative boot sample; retain actual fractional UTC, with the normalized seconds value and raw bytes. The validator allows at most one second UTC/boot rounding drift. Do not install or query NSS next automatically.

For all Rxx commands below: exact argv comes from the catalogue, no shell, read cap10s (R20 output8MiB, R22 cap5s), full reserve and recorded raw receipt. A nonzero exit/timeout/overflow/missing field is BLOCKED except an explicitly reconciled exact-name ENOENT/not-found result. No silent truncation.

1. Establish local path/mount and nonsecret file custody from the approved inventory. R21 reports numeric no-follow metadata for one exact path. R02 hashes one independently resolved regular file, at most32MiB, through root-controlled nonwritable ancestry. R14 uses `getfacl --numeric --absolute-names --all-effective -- <path>` to avoid name lookup. Inspect each lexical symlink and every approved resolved ancestor; no unreviewed link is followed by the bounded readers. Hash Python/loader/library targets before trusting subsequent inspection. No executable VM tools are invoked; approved qm/pvesh/pvesm files may only be inspected as files.
2. Run R02-host-identity (bounded `/etc/hostname`, `os.uname`, Python version and numeric caller IDs), R03 package query, R04 systemd-run `--version`, R05 isolated Python `--version`, R16 selected manager properties, and bounded approved hostname/kernel evidence. Require pve-manager9.2.5, qemu-server9.2.1, pve-qemu-kvm11.0.2-2, systemd257.13-1~deb13u1, Python3.13 with actual patch recorded, host pve and expected bare-host manager context. Version drift or virtualization ambiguity blocks; do not repair an unrelated degraded state.
3. R02/R21/R14 establish source hashes/custody; then R19 reads exact approved nonsecret `/etc/nsswitch.conf`. Apply LOCAL-ONLY-PRIVILEGE-GATE.md before any identity/policy action. R19 has path, size bound and expected source hash as distinct argv elements; it checks them before stdout. Next read only approved public passwd/group and nonsecret policy files. R06–R09/R15 are retired, and no getent/id/sudo substitute is permitted. All required local review fields must pass, including independently established VM-authority and private-credential denial. Unknown means BLOCKED.
4. R10 scans numeric `/proc/*/status` with count/size/time bounds. Require no nobody processes and complete evidence. Repeat immediately before installation and each creation. No process environment is read.
5. R11/R12 list the Stage2 namespace; R17 records complete UnitPath. For each exact future timer, service and failedtimer-absent name, run catalogue `collision_readback`, then R21 on that basename in **every** UnitPath directory. Require the strict absence gate, no aliases/jobs/masks/fragments or file/symlink collision. Do not inspect foreign command/environment properties. List output alone is not absence.
6. R21/R14: `/` and `/opt` root:root, nonwritable, `/opt`0755, no granting/default ACL; destination directory and leaf absent. Any existing object, uncertain absence or source custody problem blocks. Stage2 never adopts or repairs an existing path.
7. R19/R20 inspect only approved installed matching manuals for systemd-run/timer/service/exec/resource-control/unit/systemctl/D-Bus interfaces. Use R02 first for exact content hash. Gzip bytes/output are bounded. No downloads or package install. Compare new properties and ExecCondition serialization against the host's systemd257 interfaces. Unsupported syntax, unknown properties or inability to establish a safe argument means STOP, not fallback.

R02-host-identity supplies fresh hostname/kernel/Python observations without invoking an identity resolver. Its `/etc/hostname` path must already be approved as a local nonsecret regular file. R01's proc clock source is the preserved fixed first-command exception. Missing fresh kernel identity is a blocker.

## 2. Exclusive callback placement (target minutes 10–12)

This is a separate explicit checkbox in future authorization. Recheck all preflight gates, original UTC/boot bounds, nobody inactivity and destination absence. Execute only catalogue `install` with its final argument replaced by the already approved root-controlled staged callback path; cap20s, reserve2s, limits128MiB/3CPU-seconds/64FDs. The bytes must already be available through separately approved custody; R2 contains no transfer step.

The fixed installer requires existing administrator UID/eUID/GID0 for this narrow setup only, walks descriptors with O_NOFOLLOW, checks root ownership/nonwritability/default ACL, regular source/nlink1/size<=16KiB/stable metadata and the exact callback hash. Exclusive mkdir refuses any existing object. Exclusive O_EXCL/O_NOFOLLOW leaf creation writes only the verified source, then directory0755/file0444 and fsync. No replace/remove/chown/adoption. Any partial result stays intact and prohibits activation.

Re-run R21/R14 for all ancestry and leaf; R02 hashes the new leaf. Require exactly2441 bytes, root:root, leaf0444/nlink1, directory0755 and pinned SHA256 `a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa`. Retain dev/inode/hash and revalidate before each creation. “Immutable” here means reviewed read-only bytes under exclusive administrator custody; no immutable inode flag is changed and root cannot be cryptographically prevented from replacing the file. No R3 runtime/private authorization files are installed.

## 3. Render, admit and observe a case (target minutes 12–35)

On the existing offline evidence workstation, print the proposal only:

`python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r2/src/render.py --input <FRESH_INPUT_JSON> --case <EXACT_CASE>`

The input has mandatory session/identity/sample/collision/occupied/used fields. The renderer refuses incomplete collision proof and prints a plan plus bounded envelope and exact observation argv. Review all output; never pipe it into a shell. Deadline D is fresh B2+30,000,000 microseconds, expressed by absolute `--on-boot=<seconds>.<six-digits>s`, never literal30s. Exact base is `jarvis-vm164-r3-stage2-<nonce>-<case>`, with paired `.timer`/`.service`; the generation digest binds nonce, case and D.

Append the pending plan and consume its name before submitting the exact systemd-run array once. Recheck path/hash/identity/policy/collisions, clocks and approval; require 20–30 seconds left before D. A stale plan is not reanchored automatically. Create cap5s+2s reserve. Unknown transaction outcome consumes the name and stops qualification.

Every creation uses `--system --no-ask-password --expand-environment=no`, explicit Type=exec, User=65534, Group=65534, fixed sandbox/resource/timeout/environment assignments, absolute OnBoot, WakeSystem=yes, accuracy1us/no jitter, and the generation-bound non-root ExecCondition. The precise full property array and encoded condition body are preserved in the catalogue/source. The service starts only the pinned canary or the listed fixed harmless negative payload. A root administrator creates the transient units; the guard/payload must execute non-root. No '+' command prefix, shell or privileged fallback is allowed.

Except failedtimer, capture two distinct waiting observations before D. Exact arrays from `observation_commands` are clock R01, `systemctl --system --no-pager show --all <base>.timer`, same for service, and `journalctl --no-pager --output=json --all --boot=<boot UUID> --unit=<base>.timer --unit=<base>.service`. Clock before/after captures and journal cursor/range receipts remain in the evidence envelope. Raw show cap5s per command, journal10s; any waiting observation missed before D makes the case incomplete. Poll no faster than once a second and never beyond D+15s or the case/session bound. Do not start an unbounded polling script.

Validate complete paired raw readbacks, configuration and argv, User/Group, environment/capability/sandbox/limit resets, Jobs, PIDs, source/generation and NextElapseUSecMonotonic. Measure both clock hypotheses. WakeSystem requests BOOTTIME scheduling; the exported property domain must be independently established from matching interfaces and observed offsets. Equal clocks alone cannot decide. UNKNOWN/conflict fails and stops subsequent cases. Never suspend/reboot/reexec to create an offset. The first timer is a harmless qualification probe, not already qualified enforcement.

Capture raw journal JSON-lines and actual manager exit fields. Require one bound guard and, when required, exactly one pinned canary event with numeric UID/eUID65534, same boot, requested mode, BOOTTIME/MONOTONIC, non-VM/root-bootstrap-false fields, correct unit and InvocationID. Manager setup success is not service exit success. Stdout alone is not exit evidence. Plain traceback/EXEC diagnostics are retained in addition to callback JSON. Do not omit a prior event to make a canceled case pass.

## 4. All twelve fixed cases

All cases inherit steps0–3, exclusive namespace, complete evidence capture, 90s maximum case budget and stop-on-unexpected-result. On completion, stop only the owned timer then service as needed, retain failures and obtain final inactivity/cgroup evidence. Every stop has its own5s cap+2s reserve. Failed/inactive retained units are not reset/deleted.

| Case | Exact payload/extra argv source | Required outcome and evidence | Observation/cleanup deadline |
|---|---|---|---|
| success | `callback('success')` in plan | One bound canary; Result=success, ExecMainCode1/Status0; BOOTTIME D..D+1s | Observe through D+15s; scoped cleanup within90s |
| exit7 | `callback('failure')` | One bound canary then actual exit7, Result=exit-code, Code1/Status7; expected failure retained | Same |
| missingexec | Absolute `/opt/jarvis-vm164-r3-stage2/absent-executable-<nonce>` | Fresh absence proof; bound guard, EXEC journal diagnostic, Code1/Status203, Result=exit-code | If creation is refused before service exec, mark BLOCKED_EXEC_NOT_OBSERVED; no substitute executable |
| missingdep | Isolated Python imports exact `jarvis_stage2_intentionally_absent_dependency_<nonce>` via fixed encoded `-c` | Bound guard, ModuleNotFoundError naming exact module, Code1/Status1, no canary | Unexpected import success stops session; no module changes |
| timeout | Fixed encoded Python prints UID/eUID/GID/eGID/groups, then sleep30 | One guard/probe; RuntimeMaxSec3s; Result=timeout; actual signaled code2/status9 or15; no canary; zero PIDs/empty cgroup | D+15s observation ceiling, stop budget as above |
| late | Fixed encoded Python sleep2 then runpy unchanged canary | One bound canary, successful exit, callback>D+1s; disposition EXPECTED_LATE_REJECTED_NOT_TIMING_PASS | Delay is expected rejection, not timing qualification |
| inactive | Normal canary argv, canceled before execution | Waiting then timer stop no later than D−5s; no trigger/invocation/guard/callback through D+2s and final closure; service cleanup only exact owned scope | Preserve original deadline; late cancellation fails |
| failedtimer | Adds Requires and After for `<base>-absent.service`; no dependency created | Fresh dependency absence; raw loaded timer actually failed with non-success Result, no invocation/callback. No waiting samples required | Creation refusal or inactive-only timer is BLOCKED_FAILED_TIMER_UNOBSERVED; no global failure injection |
| collision | Identical original create argv submitted one extra time while waiting | Nonzero duplicate refusal, raw before/after pair unchanged, exactly one eventual guard/canary | Duplicate cap5s; timeout/change/second invocation fails |
| cancel | Normal argv, timer then service stop by D−5s | Post-first-stop checkpoint, no invocation/guard/callback through D+2s and closure, empty cgroup; repeated cleanup produces no commands | Interrupted sequence resumes only still-needed owned stop while authority remains |
| rearm-a | Same cancellation contract as cancel | No execution, tombstone retained; any late callback fails even if rearm-b succeeds | Final rearm-a readback/journal after rearm-b closure |
| rearm-b | New distinct name/generation and fresh D, normal success payload | Prior rearm-a cancellation proof required; one new bound callback and actual exit0, no prior failure cleared | Must fit same original window; no reuse/extension |

Any missingexec/failedtimer unobserved behavior is an incomplete qualification, not a passing substitute. Abort further trials after an unexpected result. Never retry a failed/uncertain generation or weaken a parser in-session.

## 5. Final closure and independent verification (minutes 35–45)

At minute35 cease creation. Begin final cleanup by minute40, earlier on any hard stop. Follow COLLISION-AND-CLEANUP-REVIEW.md: timer then service, each exact-owned proof and fresh budget, no deletion. Capture final raw show/journal/cgroup/process evidence, no queued jobs, zero PIDs and inactive/failed states. No absent/unloaded unit shortcut is accepted by the strict validator. Final observations must be fresh to the closure sample (at most180s); rearm-a is checked after rearm-b. Every cancellation journal starts at creation and extends through its final readback.

At either UTC expiry or BOOTTIME duration bound no command remains admitted, including cleanup. Preserve unresolved ownership and partial receipts; request separately finite readback/stop-only recovery through the existing operator's process. No automatic emergency privilege, resumed test or expiration guarantee exists.

Create twelve immutable `cases/<case>.json` artifacts containing raw show/journal/clock and command receipts plus decoded summaries; attach the manifest and its independently retained seal, source pins, actual operator/authorization/reviewer and fresh session/identity records. `artifacts.load` performs bounded no-follow rehashing; `results.validate(record, artifacts, expected_manifest_sha256=<independent evidence seal>, expected_packet_manifest_sha256=<independent packet seal>)` rechecks full consistency and expected per-case status. Failures/NOT_RUN/unknown cases remain archived and cannot produce LIMITED_OBSERVATIONS_REVIEWED. All synthetic records remain explicitly SYNTHETIC. Even a complete captured record returns consistency-only, never authorization or blanket live qualification.
