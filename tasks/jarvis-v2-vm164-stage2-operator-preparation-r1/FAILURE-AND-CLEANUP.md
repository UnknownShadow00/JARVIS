# Failure, cleanup and recovery — evidence retained

All commands are proposals for the separately approved session. No cleanup has
been needed or run on pve in this task. Cleanup changes only proved-owned Stage 2
transient timers/services. It never changes VM state, accounts, permissions,
packages, manager state or other units. The installed public canary is retained
inert for review; file removal would need separately reviewed authorization.

## Hard stop conditions

Stop admission immediately for: lost supervision/capture, approaching cutoff,
expired UTC or BOOTTIME bound, host/boot/clock/package/binary/source drift,
UID/group/process or privilege uncertainty, changed ACL/custody, unit collision,
unrecognized property/command output, missing/ambiguous clock proof, unexpected
callback UID/path/hash/mode, early or late ordinary callback, unexpected exit,
queued job or process surviving the bounded limit, unsupported WakeSystem,
partial setup, evidence write/full/overflow error, or external host maintenance.
Expected named negative outcomes may continue only after fresh owned-inactive
proof and retained evidence. Never retry a consumed case to erase a failure.

## Ownership ledger

Before each creation, retain a pending record of exact session/case/base, complete
argv/digest, source and binary pins, intended deadline, host boot UUID, approved
UTC expiration and description `JARVIS-Stage2-<nonce>-<case>`. After creation retain
full raw properties, Transient, Id/Names, paired Unit, description, exact ExecStart,
User/Group, deadline and InvocationID when it exists. Names alone are not proof.
Descriptions must match the actual paired unit readback; do not assume description
inheritance if the installed systemd behaves differently. Unexpected mismatch
blocks ownership and is investigated rather than rewritten.

If creation exits nonzero or loses acknowledgment, **do not resubmit**. Read both
exact names, the dependency name where applicable, journal and jobs. If the
service and timer prove this pending transaction's exact owned contract, record
partial ownership and perform scoped cleanup. If one half is missing, stop the
remaining half only when its own complete definition can be matched to the
pending record; for an orphan timer, paired Unit plus exact source/deadline/
description/creation evidence must establish the transaction. If uncertain,
quarantine the names in evidence and stop qualification. Never adopt a foreign
collision or infer ownership from a matching prefix.

## Exact cleanup sequence

Preconditions for any stop: unexpired authorization specifically covers scoped
cleanup; same host/boot; evidence preserved before action; pending/owned record
and fresh show establish exact identity, argv/deadline, UID and property custody.
No other session shares the nonce; no ambiguity or active administrator race.

1. Capture R01, `observe.<case>.timer`, `.service`, `.journal` and R22-cgroup,
   all from COMMAND-CATALOG.json. Preserve raw Result/exit/InvocationID before
   stopping: a stop can change observable state. Absence or already-terminal
   state is not itself an error but requires evidence.
2. For an owned active timer only, execute exactly:

   ```text
   /usr/bin/systemctl --system --no-ask-password stop <EXACT_OWNED_BASE>.timer
   ```

   Wait no more than five seconds for the client. Capture show and clocks.
   Confirm no queued start job and timer inactive/failed or proven unloaded.
   Do not assume this stopped an already-dispatched service.
3. Re-read service ownership. For the owned service that is active, activating,
   or may have been dispatched by that timer, execute exactly:

   ```text
   /usr/bin/systemctl --system --no-ask-password stop <EXACT_OWNED_BASE>.service
   ```

   It has KillMode=control-group, TimeoutStopSec2s and SendSIGKILL=yes. The
   command is narrowly scoped even if the callback was dispatched between
   readbacks. A five-second client timeout is UNKNOWN, not confirmed stopped.
   In an activating/deactivating state take at most one further fresh readback
   after the bounded stop interval; do not loop or infer success. The pure
   offline cleanup planner refuses transitions pending this manual review.
4. Capture raw show, case journal, R22-cgroup, R10-processes and clocks again.
   Require timer no longer active/waiting, service inactive or failed, MainPID0,
   ControlPID0, no Job and no owned live cgroup process. For existing cgroup require
   `cgroup.events` populated0 and empty cgroup.procs; populated is hierarchical.
   R22 absent_or_partial alone is not absence proof: corroborate exact directory
   absence with R21, and reject missing individual cgroup files as incomplete.
   Unloaded units require prior ownership/exit evidence, not-found inactive raw
   readback, no queued job and absent cgroup plus process census. Distinguish
   failed-but-dead (retained negative evidence) from still running. If terminal
   result was lost before capture, mark incomplete even if currently inactive.
5. Append CLOSED_EVIDENCE_RETAINED only after all owned entries pass. Repeat
   cleanup by reading states: inactive/failed with no processes => no mutation.
   If timer is already inactive but service active, issue only its exact stop.
   Do not reset-failed or unload units to make a second cleanup look clean.
6. Archive console-side raw files and a new result manifest with hashes and
   failure dispositions. Do not delete, collect, truncate, vacuum, unlink,
   overwrite or move existing evidence. Retain the consumed-name ledger and
   installation receipt; callback remains read-only and inert.

No glob is permitted in `stop`. Never run broad `systemctl stop`, disable,
reset-failed, daemon-reload/reexec, killall/pkill, reboot, suspend, qm or API commands.
No unrelated service can be stopped to help a Stage 2 case pass.

## Finite recovery table

| Failure | Required handling |
|---|---|
| Preflight incomplete/UID privilege uncertain | Stop before installation/activation; retain read-only evidence and report blocker. |
| Exclusive directory/source write fails | Leave partial directory/file intact. Record stage/exception. No retry/adoption/repair and no timers. A later separately reviewed recovery decision owns removal. |
| Creation timeout/nonzero | Capture exact pair; do not retry. Reconcile pending ownership; clean only proved-owned half/pair. Unknown owner => quarantine, not stop. |
| Expected service exit7/import/exec/timeout | Retain failure state, journal, raw exit and clocks. Owned cleanup then continue only if the expected observation was actually obtained. |
| Late/early ordinary firing | Reject timing qualification even if exit0. Record measured latency and clean up. No new deadline under the same case. |
| Collision refusal | Preserve foreign units untouched. Intentional owned collision requires unchanged definitions and exactly one callback; otherwise abort. |
| Cancellation interrupted | Resume from recorded pending cancellation with fresh expiry/boot/ownership checks. Stop remaining active owned half. Never rearm or erase checkpoint. |
| Stop client timeout/remaining live process | Preserve unknown/failed cleanup. No additional kill privilege, broad stop, host reboot or VM action. Existing operator coordinates separately authorized recovery. |
| Console/evidence loss | No more tests. If existing supervisor retains sufficient ownership evidence and current authority, perform exact owned cleanup; otherwise report orphaned/unknown. Do not recreate missing evidence. |
| Manager unavailable, reboot, suspend or expiry | Session fails. No renewed deadline or inferred grant. Further host actions require separate operator authority; never silently continue this expired session. |

The planned schedule leaves time for cleanup, but no software command can promise
a hard bound through kernel/manager/storage failure. The canary lacks its own
UTC/BOOTTIME authorization gate; a delayed job could still run harmless code
later if cleanup fails. This limitation is explicit, not guaranteed expiration.
