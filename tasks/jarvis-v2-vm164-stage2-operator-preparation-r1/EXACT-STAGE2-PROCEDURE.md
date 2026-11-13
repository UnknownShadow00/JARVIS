# Exact supervised Stage 2 procedure — NOT AUTHORIZED

This is an offline operator packet. No command below has been run on pve.
Stage 2 remains NOT AUTHORIZED. Use only a separately approved existing local
administrator console; do not obtain credentials, open a root shell, connect over
SSH, or use a Proxmox API. The operator executes individually reviewed commands
through that console. VM164 stays stopped with no NIC; no VM command is included.

## Command notation and execution contract

`COMMAND-CATALOG.json` is the normative complete argv catalogue, including the
literal Python bodies. Every array item is one argument. No shell interpolation,
`eval`, pipe, wildcard expansion, PATH lookup, or command substitution is needed.
The read-only systemctl list patterns are literal systemctl filter arguments;
**mutation commands never use patterns**. Python bodies are passed as ONE `-c`
argument. `src/packet.py` produces exact per-case timer argv; it never runs it.
`src/proposals.py` contains the exact inspection/install/verification bodies.
These sources are part of this packet's integrity manifest, not modifications to R3.

Angle-bracket fields are mandatory refreshed inputs, not example host values.
All must be resolved before their command is approved. Do not execute the JSON
as a batch, install any of these helper files on pve, or copy fixture constants.
Only the separately approved pinned callback file may be installed. A reviewed
console/workstation can render argv offline, then submit one array at a time.

The existing console recorder is a **mandatory prerequisite**: it must retain
exact argv bytes, raw stdout and stderr separately, actual process exit code or
signal/timeout, UTC and BOOTTIME before/after, boot ID, and command sequence. Its
storage location and custody must be specified and reviewed before the session.
Use a new exclusive evidence destination; no overwrite, truncate, journal vacuum,
redaction-in-place or deletion. Host storage changes beyond the public callback
are not implicitly approved: prefer existing approved console-side evidence
storage. If capture is unavailable, STOP before installation or unit creation.
No generic command-execution wrapper is supplied or authorized by this packet.

For R01–R21 and all show/journal calls: use a 10-second console deadline,
separate bounded streams (maximum 8 MiB each), no interactive input, no prompts.
An overflow, nonzero exit, unsupported command/property or timeout is a blocker
except the explicitly reviewed negative cases below. Preserve partial output.
The console may terminate its own stuck client; it must **never** infer that a
manager transaction was canceled because the client died. Stop requests use a
5-second console deadline. No timer/service is activated by a read command.

## 0. Fill finite approval and identity inputs

Before the session, independent reviewer and operator fill a copy of
`templates/PREFLIGHT-INPUT.json`, the authorization fields in
`AUTHORIZATION-REQUEST.md`, the privilege inventory in `SECURITY-REVIEW.md`, and
the console evidence plan. Keep the original null template unchanged.

Required concrete fields include:

- UTC start and UTC expiration in `YYYY-MM-DDTHH:MM:SSZ`, at most 2700 seconds
  apart, and a fresh 32-character lowercase hexadecimal session nonce generated
  by an approved local random source. No example nonce is host evidence.
- Host boot UUID, kernel, Python exact version, fresh package versions, resolved
  binary paths/SHA256/owner/mode/symlink chains, policy-review evidence digests,
  active unit/file collisions and the full unit search path.
- Fresh initial BOOTTIME anchor and tight BOOTTIME–MONOTONIC offset bounds;
  callback source pin and root-controlled staged source path (must already exist
  through a separately approved custody channel; this packet has no transfer step).
- Named operator/reviewer, exclusive administrative control during the window,
  complete credential/VM-authority inventory, and evidence recorder limits.

The finite approval includes only this packet's named negative cases and owned
unit stop actions within the same window. It never approves Stage 3/4, root
bootstrap, forced stop, Gate 6K, JARVIS or production changes. An approval with
blank dates or with a deadline already passed is invalid. No fixed future date
is invented in this packet. Before every action compare both UTC and BOOTTIME
against the approved limits; expiry of either closes admission.

## 1. Read-only preflight; no installation yet (target minutes 0–10)

Each numbered ID below is the exact argv in `COMMAND-CATALOG.json.read`. Preconditions
for all: separate finite approval has been recorded, existing console identity
is confirmed out-of-band as pve, evidence capture works, and no host maintenance
or concurrent administrator changes are occurring.

1. `R01-clock`: record boot ID, UTC and B1/M/B2. Require `0 <= B2-B1 <= 1000us`.
   Record `[B1-M,B2-M]`. Use B2 as conservative `boot_us`. At start record the
   anchor with UTC rounded down to seconds (the validator allows ≤1 second skew).
   Read again around every command affecting or observing a trial. A boot change,
   clock regression, offset drift over 1000us or wall/boot elapsed drift over
   1 second stops qualification. Never move expiry to compensate.
2. `R02-host-binaries`: inspect fixed paths and hashes without executing VM tools.
   Require node `pve`, fresh kernel evidence, Python 3.13 with exact patch version
   retained, root custody at every lexical/resolved component and symlink target,
   no group/other write, regular binary targets and no changes during hash reads.
   Follow and review every intermediate symlink, not merely the final target.
   `R14` checks ACLs on each relevant ancestor. Unexpected file capabilities or
   set-ID mode require review; sudo's expected setuid-root status is part of the
   privilege review, not permission to execute it as nobody. Errors block.
   Python itself must be trusted via existing console custody before using it
   to inspect other files: a program cannot independently attest its own safety.
3. `R03-packages`, `R04-systemd-version`, `R05-python-version`, `R16-manager`:
   require pve-manager 9.2.5, qemu-server 9.2.1, pve-qemu-kvm 11.0.2-2 and systemd
   257.13-1~deb13u1. `${Package}` and `\\n` in JSON are literal dpkg format input,
   not shell variables; preserve real output to verify serialization. Nonempty
   Virtualization indicating container semantics or unknown manager status blocks
   this bare-host OnBootSec procedure. Record any preexisting degraded state;
   never repair unrelated units to obtain a clean baseline.
4. `R06-account`, `R07-numeric-account`, `R08-group`, `R09-memberships`,
   `R10-processes`: nobody must map to UID/GID 65534 both by name and number, with
   no other effective supplementary group, no preexisting processes and no
   process-inspection errors. NSS ambiguity, duplicate UID mappings discovered
   in policy review, new activity, or privileged group membership blocks. Repeat
   R10 immediately before installation and each case (exclude only positively
   identified processes of an already owned case while observing that case).
5. Complete SECURITY-REVIEW.md: inspect nonsecret authority policy and metadata,
   not credential contents. `R15-sudo-policy` is a noninteractive root-side list
   of nobody's privileges; it does not run a command as nobody. Independently
   review policy inclusions and error meanings. `R19` reads only a concrete,
   approved nonsecret policy file; never `/etc/shadow`, key/token/credential bytes,
   environments or arbitrary paths. `R21` and one `R14` per inventory path and
   ancestor capture metadata/ACLs. Identify every socket and backing storage
   route in that inventory. Missing tools, incomplete inventory, custom policy,
   opaque external NSS or inability to prove denial means **BLOCKED_NO_UID_PROOF**.
   Do not test VM access with `qm`, `pvesh`, API logins, tokens or credentials.
6. `R11-loaded-units`, `R12-unit-files`, `R17-unit-search-paths`: inventory the
   entire Stage 2 prefix and every system unit search directory. For **each exact
   proposed timer, service and failedtimer dependency name**, run the catalogue `collision_readback` minimal show argv
   (no environment/credential/command dump from a foreign unit), plus R21 metadata for that basename under EVERY directory from
   UnitPath, including symlinks/masks/generator/transient locations. Require
   `LoadState=not-found`, inactive, no fragment/source/names/alias collision and
   no files/symlinks, queued job or active process. Review raw `Job`, `Names`,
   `FragmentPath`, `SourcePath`, `Transient` fields. A not-found show exit must be
   reconciled with its raw fields and file checks; arbitrary nonzero is not absence.
   Empty `list-units` alone is insufficient. If another session in this Stage 2
   prefix exists, block and preserve it. Never stop a collision.
7. `R13-path-metadata`: `/` and `/opt` root:root and nonwritable to group/other;
   `/opt` mode 0755; both proposed directory and leaf absent (ENOENT only).
   R14 on `/` and `/opt`: no ACL/default ACL granting unexpected access. Existing
   directory, dangling link, permission error or unknown absence means STOP.
8. `R20-manual-gzip-read` for approved installed manuals (or R19 for plain text):
   systemd.timer(5), systemd-run(1), systemd.service(5), systemd.exec(5),
   systemd.resource-control(5), org.freedesktop.systemd1(5), systemctl(1), and
   installed nonsecret qm manual/help **files only**. Record their exact paths,
   package ownership/version and hashes with the same bounded binary-inspection
   body applied to each regular manual file. Do not run qm. Matching docs absent
   or uncertain readback semantics stay UNKNOWN. No downloads/package installs.

Stop preflight without writes if any mandatory admission fact fails. Do not
paste hashes from HOST-FACTS.md into a field requiring a fresh measurement.

## 2. Exclusive public callback creation (target minutes 10–12)

Preconditions: step 1 passes, privilege denial independently reviewed, exact
source/staging path and installation argv reviewed under separate authorization,
window valid, destination still absent, root/operator control exclusive.

Execute exactly the catalogue `install` array after replacing only the staged
source argument. Its fixed Python body:

1. Requires existing UID/eUID 0 and effective GID 0 for **setup only**.
2. Walks source ancestry using directory descriptors and O_NOFOLLOW; requires
   root:root/nonwritable ancestry, no default directory ACL, a bounded single-link
   regular source, stable metadata and the exact callback SHA256.
3. Opens `/opt` through protected descriptors, uses exclusive `mkdir` with no
   `exist_ok`, creates `canary.py` with O_EXCL/O_NOFOLLOW, writes only verified
   bytes, sets new directory 0755 and new file 0444, and fsyncs file/directories.
4. Does not replace, chown, delete, repair or adopt any preexisting object.
   Any partial failure leaves evidence intact and **prohibits activation**.

Run R18-public-verification and R14 on directory/leaf. Verify exact SHA256
`a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa`, 2441 bytes,
root:root, leaf 0444/nlink1, directory0755, no symlinks/non-root-writable ancestry.
Retain device/inode identities to catch replacement before every later creation.
The pinned source is unchanged. Do not copy the full R3 runtime or any grants.

## 3. Render and admit each named case (target minutes 12–35)

Run the offline renderer on the console-side workstation, never by installing
it into the host:

```text
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-preparation-r1/src/render.py --input <FRESH_INPUT_JSON> --case <ONE_CASE>
```

This local command prints proposed argv only; it gives no execution authority.
Use an actual fresh R01 sample. `deadline_boot_us = B2 + 30,000,000` and
`--on-boot=seconds.six_digits s` (without a space before `s`). This is absolute
host uptime, never the literal `30s`. Names are exactly
`jarvis-vm164-r3-stage2-<SESSION_NONCE>-<CASE>.timer` and `.service`.

One case at a time. Append a pending ownership record with name, argv, deadline,
boot ID, source/binary pins, description and session before submitting creation.
Mark its name consumed before the call; an acknowledgment loss cannot permit a
retry. Recheck all collisions and callback inode/hash, current package/binary
pins, namespace, UID evidence and both session clocks. Apply `freshness()` with
fresh sample immediately before launch: at least 5 seconds and no more than
30 seconds must remain to its absolute deadline. No start after minute 35 or
with less than six minutes before expiry. Stale proposal => STOP case, no automatic
reanchor. A new session/approval is needed for a failed-case retry.

Submit only that exact `create` argv once. Capture before/after clocks and
systemd-run stdout/stderr/exit. At arm+approximately 1 and 3 seconds, capture
clock → raw show(timer) → raw show(service) → clock. If two waiting samples cannot
be retained before firing, classify incomplete. Poll no faster than once per
second through deadline+15 seconds; do not wait beyond cleanup cutoff.

Before accepting waiting state verify all properties in TIMER-AND-SERVICE-REVIEW.md,
including paired names, exact ExecStart argv, User/Group, finite limits, sandbox,
OnBootUSec and clock-normalized next deadline. The first success timer is a
**qualification probe**: UNKNOWN clock domain means it is never marked qualified
or admitted for R3 use. Collect its harmless result to resolve the convention;
if still UNKNOWN or inconsistent, stop subsequent cases and clean up. Unknown
properties other than the specifically investigated clock serialization block
and trigger owned cleanup immediately.

After every firing, retain raw show and full case journal, clocks, process-exit
status and callback JSON; verify same boot, `_SYSTEMD_UNIT`, `_SYSTEMD_INVOCATION_ID`,
`_UID=65534`, intended callback mode and exactly one callback record. `ExecMainCode`
is a waitid code (normally 1 for CLD_EXITED), not the exit status. Preserve numeric
fields plus decoded meaning. Unit/load/start success is not callback success.
Compare journal monotonic timestamps with callback and manager timestamps; never
substitute journal time for missing callback clocks. R10 captures UID/process
metadata when a process can be observed; the timeout probe emits UID/GID/groups.
No reading process environ, private file contents, or guest state is permitted.

### Fixed finite case schedule and expected observations

| Case / exact argv source | Required observation and stop/cleanup rule |
|---|---|
| `success` | Pinned callback mode success, uid/euid65534, same boot, result success, ExecMainCode1/Status0, callback BOOTTIME in [deadline, deadline+1s]. R3 parser trial on raw selected properties below. |
| `exit7` | Same callback, mode failure, one JSON record then actual exit7; service Result=exit-code, Code1/Status7. Expected failure is evidence, not a successful service. |
| `missingexec` | The nonce-bound `absent-executable-…` path must be absent (R21/R14 ancestry) and remain absent. Exact absolute missing executable in catalogue. If manager reaches exec, require service Code1/Status203 and Result=exit-code, with journal EXEC failure. systemd-run can reject missing executables during setup: preserve this as CREATION_REFUSED_EXEC_NOT_OBSERVED, block the exec qualification and do not invent 203/EXEC or install a broken executable. |
| `missingdep` | Isolated Python imports exactly the nonce-bound deliberately absent module. Require ModuleNotFoundError in journal, Code1/Status1 and Result=exit-code. If unexpectedly importable, stop all qualification; do not alter host modules. |
| `timeout` | Fixed literal Python prints UID/eUID/GID/eGID/groups, then sleeps30s, under RuntimeMaxSec3s. Require all IDs65534, groups subset{65534}, Result=timeout, signal termination evidence, MainPID0 and no live cgroup processes after stop budget. Keep actual signal/code; do not demand status124 (a shell timeout convention). |
| `late` | Literal Python delays2s then invokes the unchanged pinned canary with runpy. Require successful exit plus callback time >deadline+1s. Record EXPECTED_LATE_REJECTED_NOT_TIMING_PASS. This exercises delayed callback handling; it does not simulate host suspension or prove scheduler starvation behavior. |
| `inactive` | Arm with 30s horizon; verify waiting, then stop ONLY its timer at least5s before deadline. Capture inactive timer; untouched service must remain inactive with no invocation/callback through deadline+2s. A late operator cancellation is not an inactive-case PASS. |
| `failedtimer` | Catalogue adds Requires and After for its exact absent `<base>-absent.service`. Confirm that name and all unit-path entries are absent. Do not create/stop that dependency. Expect activation/dependency failure with no callback. The manager may leave the timer inactive rather than failed: preserve actual state; failed-state handling is fixture-tested, but mark LIVE_FAILED_TIMER_STATE_UNOBSERVED if ActiveState=failed/failed Result was not observed. No global failure injection, unsupported-property fallback or resource exhaustion. |
| `collision` | After its first valid waiting readback, submit the **identical original** creation argv once more while waiting; no regenerated deadline. Require nonzero refusal and unchanged timer/service definition, next deadline, invocation history and source. Observe exactly one eventual callback. If collision is not rejected or changes anything, stop qualification. No foreign unit is used for this negative test. |
| `cancel` | Arm, verify waiting, record pending cancellation, stop timer then service using exact owned stop argv, at least5s before deadline. Capture state after the first stop before the second; that is the recovery checkpoint (do not actually disrupt the console). Observe no callback through deadline+2s, inactive/failed units, MainPID0 and empty cgroup. Repeat cleanup readback; terminal units require no new stop. |
| `rearm-a`, then `rearm-b` | First cancel rearm-a as above, retain tombstone and verify no invocation; then create rearm-b once with a new future deadline and distinct name in the SAME approved finite window. Require successful canary for rearm-b and no change to rearm-a. No same-name restart, deadline extension or reused failed generation. |

Do not continue after an unexpected failure. Named expected negatives can continue
only after ownership, inactivity and evidence are established and reviewed.
If less than the required budget remains, mark remaining cases NOT_RUN and stop.

## 4. Raw parser and clock evidence

Retain full raw `show --all` outputs. Separately capture exact R3 properties with:

```text
/usr/bin/systemctl --system --no-pager show --property=<COMMA_JOIN_OF_R3_TIMER_PROPS> <EXACT_BASE>.timer
/usr/bin/systemctl --system --no-pager show --property=<COMMA_JOIN_OF_R3_SERVICE_PROPS> <EXACT_BASE>.service
```

The two exact comma lists are in TIMER-AND-SERVICE-REVIEW.md and the catalogue's
`parser_readback` entries. Do not filter/rewrite the output; load those bytes into
the sealed `systemd_codec.timer()` and `.service()` offline. It is intentionally
strict. Compare decoded `argv` with this packet's callback argv (not the R3 root
worker contract). `model.verify_unit()` and R3 `timer_command()` are **not** Stage 2
validators/builders: they demand root Stage 3 workers. Do not use them to run this
procedure. Compound serialization differences require a new reviewed candidate;
do not patch R3 or massage the evidence. Non-Python missingexec and inline-code
cases are not expected to satisfy that narrow normal-worker ExecStart parser.

Measure and compare both clock hypotheses before/after creation and twice while
waiting. Follow the decision table in TIMER-AND-SERVICE-REVIEW.md. Missing raw
next-elapse, ambiguous equal clocks without matching documented interface proof,
invalid offset, or a documentation/readback conflict means UNKNOWN => FAIL.
Never suspend/reboot/reexec to create a convenient clock difference.

## 5. Close and preserve (minutes 35–45 maximum)

At minute35 stop new trials; finish bounded observations, then stop owned active
timers and services by minute40. Reserve the last five minutes for final show,
journal, process/cgroup evidence and result manifest. The same cleanup starts
earlier on any hard stop. Follow FAILURE-AND-CLEANUP.md exactly. Require no live
owned processes, no queued job, inactive/failed or proved-unloaded owned units and
retained journals before declaring the session closed.

At the explicit UTC expiration OR BOOTTIME duration bound: no new command under
this authorization, no automatic extension, no retry and no continued qualification.
Record incomplete/orphaned state from available evidence and escalate to the
existing operator's separately authorized recovery process. This packet does
not guarantee that systemd/kernel failure can be cleaned up by that time.

Fill a new `LIVE-RESULT.json` from actual evidence, hash every raw artifact, retain
failed/unknown/not-run cases, and obtain independent review. Do not set R3's
reboot/reexec/wake/VM qualification booleans based on this bounded session. Keep
the public callback in place, inert and read-only, with its installation receipt;
removal is not part of this packet. No credential, VM, service-manager restart,
package, account, ACL or production change is permitted.
