# Scheduler publication and disabled/stale admission R4

Offline `workspace-write` successor. R3 and earlier sealed packets are preserved;
none of their historical receipts is relabeled as current source evidence.

## Defects demonstrated before the fix

`probe_before.py` runs frozen R3 definitions in fresh disposable files with an
inert backend and in-memory audit recorder. Its retained JSON receipt demonstrates:

- An interrupted write truncated the final scheduled-job store to the single byte
  `[`; add_job returned a job and emitted job_added despite scheduler_save_error.
- A callback retained from the backend enqueued a task after remove_job returned
  success. That was queue submission only, not goal execution.

New negative tests also expose disabled registration, stale stop/start callbacks,
pre-publication rollback gaps and ambiguous post-application/backend failures.

## Implementation

`app/agent/scheduler.py` now serializes a validated complete snapshot, writes a
same-directory restrictive temporary file, flushes/fsyncs, closes and replaces
the final path, then attempts supported POSIX directory sync. Add/remove restore
prior memory on pre-publication failure and leave backend registrations unchanged.
If replacement occurred but directory durability is uncertain, the applied state
remains and this instance blocks future writes/start/admission. No optimistic
rollback or automatic retry is attempted.

Malformed/unreadable/nonregular or partially accepted stores are preserved and
write/admission blocked. Duplicate keys/IDs, unknown fields, invalid types and
nonfinite constants cannot be silently overwritten. Valid persisted enabled=false
is retained as false. Minimal valid legacy fields and exact whitespace in nonempty
strings roundtrip. Identifier generation has32 bounded attempts. Blank/invalid new
records are deliberately rejected before publication. Cron rejection happens before
save when the actual parser is available; stub mode stores nonempty cron text
without claiming to validate it.

Backend and audit failures after applied add/remove state have explicit typed
outcomes and quarantine admission. Start validates enabled jobs before constructing
the backend, registers before starting, and cleans up failed starts locally. Failed
cleanup retains the backend reference for an explicit stop attempt. Stop invalidates
admission before attempting shutdown. No operation clears uncertainty automatically.

The backend now registers an owner-bound callback with a lifecycle generation.
Admission requires the same live job object, enabled=true, matching generation,
running owner/backend and no load/persistence/runtime quarantine. Removed,
disabled, replaced and prior-lifecycle callbacks cannot newly submit tasks. Stub
mode has no backend and cannot dispatch. The module helper _run_job also rejects
disabled jobs; production backend callbacks go through the full owner gate.

**An already-admitted enqueue may finish after remove/stop returns.** Its queue
operation can await a queue lock while removal/stop occurs. Tests explicitly
demonstrate that permitted boundary, then reject later stale callbacks. This is
not cancellation, cross-component commit fencing or exactly-once execution.

## Caller/error contract

Schedule create/delete routes catch `SchedulerOperationError` and return fixed,
sanitized outcome metadata: operation/job_id, phase, state_applied, publication,
uncertain, automatic_retry=false and reconcile_required. Validation gets400,
applied errors409, other errors503. Exception strings, private paths and goals are
not included. Publication differentiates not_published, memory_applied, published
and published_durability_unknown. Successful job dictionaries and deleted booleans
remain compatible. A quarantined missing-delete rejects rather than asserting
absence from a store that could not be loaded.

Retry fields are advisory. No HTTP idempotency, scheduler occurrence receipt,
transactional outbox or cross-process owner is added. ResourceManager can continue
to report ACTIVE after catching scheduler start failure; that state is not a
scheduler readiness assertion. The full source-only caller/lifecycle limitations
are in `CALLERS-AND-LIMITS.md`.

## Verification

```sh
python3 -B tasks/jarvis-v2-scheduler-reliability-r4/run_checks.py
python3 -B tasks/jarvis-v2-scheduler-reliability-r4/run_checks.py --save-evidence
python3 -B tasks/jarvis-v2-scheduler-reliability-r4/run_checks.py --baseline --save-evidence
python3 -B tasks/jarvis-v2-scheduler-reliability-r4/probe_before.py
```

Final current receipt `evidence-20261030T224808335328Z.txt`: **39 methods /54
subtests, zero failures/errors/skips**, forbidden application/framework imports or
guarded parent-network attempts. It combines25 new scheduler methods with13
relevant R3 caller regressions and one existing-agent regression method containing
ten existing functions as subtests. Scheduler/server changed, justifying these
focused regressions. Pure queue/broker/historical baseline suites were not rerun.

The final frozen predecessor run (`baseline-20261030T224816522804Z.txt`) deliberately
exits1:25 methods, six failing cases/39 errors against the new contract. It is defect
evidence, not a current regression failure. Exact predecessor and test hashes are
in the receipt. Intermediate receipts are preserved and clearly precede the final.

New cases cover12 add/remove failures across mkdir/temp-create/write/flush/file-sync/
replace, sync ordering, post-replacement quarantine, audit/cleanup error reporting,
unsupported directory sync, ID collisions, malformed/partial/nonregular/I/O stores,
bounded FIFO read protection, exact legacy/whitespace roundtrip, persisted disabled
jobs, stale objects/lifecycles, stop and failed-start cleanup, post-application
backend/audit failures, typed HTTP outcomes, stub/idempotent start and the admitted-
before-removal boundary.

Tests execute actual source definitions with dependency/singleton wiring excluded,
fresh files, audit/HTTP response recorders and an **inert BackendRecorder**. Its
start/shutdown methods only change fixture fields; it creates no timer, thread,
framework instance or service. A bounded child checks FIFO construction using the
isolated loader. No actual app/backend/scheduler/framework startup occurred.
This is not FastAPI/ASGI, Pydantic, APScheduler grammar/timing, live isolation or
deployed integration validation. Required runtime dependencies remain absent and
were not installed or imported from inspected bundles.

The existing independent GPT-6 Astra/high reviewer inspected the implementation
read-only and found no blocking issue in the bounded scope. It confirmed rollback,
applied-state quarantine, owner/object/generation checks and startup/stop ordering,
while retaining the already-admitted/no-cancellation limitation. It ran no tests
and changed no files. Source compile and git diff whitespace checks pass.

## Preserved limits and next safe work

Directory sync is skipped off POSIX or for explicit unsupported errors; new parent
directories are not individually synced. Temp cleanup is best effort. Normal
returns are not a storage-hardware/power-loss qualification. Quarantine and
generation are instance-local, so stale independent writers can still overwrite
snapshots. Mutable job references and internal Python helpers are not an isolation
boundary. No multi-thread qualification is claimed.

last_run remains transient enqueue acknowledgement, not persisted occurrence or
execution proof. Callback queue/audit exceptions retain R3 behavior: they propagate
and do not themselves set Scheduler runtime quarantine. A queue persistence
uncertainty can block its own later writes; a later distinct cron fire can follow
an audit-applied callback. No deduplication or unconditional halt-on-callback-error
policy is claimed. Real backend shutdown, misfire/overlap/recurrence, cron parser,
framework middleware/response handling and resource readiness need separate
dependency/environment integration. See the existing ownership proposal instead
of inventing a hash-check lock or migrating stores automatically.

Next safe unit: source-level ResourceManager readiness/error propagation fixtures,
or specify durable scheduler occurrence/outbox/owner semantics before a separately
authorized migration. Stronger cancellation needs a shared admission/commit design.

No deployment, app/service startup, dependency install, real provider/model/network/
Proxmox/guest/AI access, credentials/identities/ACLs/tokens, protected install/
bootstrap/activation, Gate6K qualification or shared mount/cache/tmp-policy change.
The existing staged broker setup and missing trusted guest bootstrap facts remain
pending. Parent appends only the canonical project log before completion.
