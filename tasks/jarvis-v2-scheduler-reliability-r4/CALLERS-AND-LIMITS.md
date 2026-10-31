# Scheduler callers and limits — source-only R4

R4 changes scheduler publication and callback admission within one Scheduler
instance. It does not make scheduling, queue submission, audit delivery, or goal
execution exactly once. **Removal and stop reject future admissions; they do not
undo an enqueue whose admission already happened.** A previously admitted
callback can still finish after remove/stop while awaiting the queue lock.

Profile: `workspace-write`, solely to write this document. Source-only observation:
2026-10-30T22:47:58.873383+00:00. The implementation was read after the parent's R4 edit settled,
while independent review was pending. The hash table below binds these claims;
any later source change needs reconciliation. Earlier baseline observation at
2026-10-30T22:41:47Z had scheduler `696a32…` and server `6e9f1a…` (pre-R4);
those bytes are not the implementation described below.

No actual scheduler/backend/app start, application import, package execution,
dependency inspection/install, network/provider call, process/container/VM
inspection, credential access, or runtime data read/write occurred in this review.
No tests ran here. Only this new document was written; parent owns tests, review,
canonical logging and seals. Prior sealed packets remain untouched.

## Callers and startup outcomes

| Source reference | Behavior supported by source |
| --- | --- |
| `app/agent/scheduler.py`: module singleton and Scheduler.__init__ | One production `Scheduler(DEFAULT_JOB_STORE)` construction was found. Its store is checkout-root `data/scheduled_jobs.json`; construction loads local memory. Additional explicit instances are possible. This is not a process-wide or cross-process ownership lock. |
| `app/server.py`: scheduler import, create/list/delete_scheduled_job, _schedule_write_error | POST `/schedule/jobs` calls synchronous add_job; DELETE calls remove_job; both catch SchedulerOperationError and construct a typed JSON response. GET converts list_jobs' current objects to dicts; it is not a backend health or durability readback. There is no schedule-update/enable execution API in these sources. |
| `app/server.py::lifespan` | Awaits scheduler.start before entering its yield/try-finally region. A scheduler start exception prevents successful lifespan startup; scheduler.start must clean up any partially started backend itself. Normal teardown awaits scheduler.stop after other cleanup. Exceptions in earlier startup/teardown audit/resource calls can prevent the later scheduler call; this review does not claim unconditional lifecycle cleanup by server. |
| `app/resource_manager.py`: _start_required_services, _stop_background_services, wake | Calls local scheduler.start/stop and catches exceptions into action entries plus audit reporting. wake continues to mark the resource state ACTIVE after _start_required_services returns. ACTIVE is therefore not proof the scheduler is healthy, running with a real backend, or accepting callbacks. The catch's own audit can also raise. |
| `app/server.py`: resource_wake/light_sleep/deep_sleep endpoints | Delegate to ResourceManager and return its transition. They do not expose a dedicated scheduler reconciliation/health contract. |
| `app/cli.py`: _wake, _post; `app/resource_manager.py::start_server_process`; `app/boot.py::ensure_server_running` | CLI can launch a server, or locally call resource_manager.wake after any failed HTTP/status/JSON result. That can construct/start a separate local Scheduler. Boot similarly probes then launches another interpreter. None acquires scheduler-store ownership. No actual overlapping process was inspected or asserted. |
| `app/main.py`, Dockerfile, docker-compose.yml | Source launches a backend without an explicit worker-count argument and Compose binds `./data` into `/app/data`. These intentions do not prove the live worker count or exclude a second host/container owner. Runtime environment, overrides, supervision and dependencies were not checked. |

The actual backend registration now points at the owning instance's
`_dispatch_job`, not directly at the module-level `_run_job`. Search of current
production app source found no other direct _run_job caller. The helper remains
callable by internal Python code and only checks enabled itself; calling private
helpers or mutating internal objects bypasses the full owner admission model.
This is not a sandbox against arbitrary code inside the interpreter.

## Publication, load quarantine, and typed outcomes

`Scheduler.add_job` checks instance health, chooses an unused local identifier
with 32 bounded attempts, validates record fields, and prepares a cron trigger
when the backend parser is available. It snapshots the prior dictionary, saves
the candidate state, then registers with an existing backend and submits the
success audit. `remove_job` checks health **before** an unknown-ID lookup, removes
and saves first, then removes from the backend and audits. A quarantined store
therefore cannot be reported as a trustworthy missing-delete result.

`_save` serializes the complete record list before filesystem writes, rejects
nonfinite/lossy records, writes a same-directory temporary file, flushes/fsyncs it,
closes it, replaces the final path, and attempts POSIX directory sync. Before
replacement, a failure restores the previous in-memory add/remove state and does
not apply backend changes. After replacement, a sync failure retains the applied
state and marks publication uncertain. Further mutation/start and callback
admission on that instance are blocked. No rollback or automatic retry of that
possibly published change is performed. Temporary cleanup is best effort.

`_load` preserves the original file and quarantines malformed/unreadable,
nonregular, dangling-link, duplicate-key/ID, nonfinite, invalid-shape or lossy
records. Diagnostic list reads may retain valid records from a mixed file;
that list does not clear the write/admission block. There is no automatic reset,
repair, credentialed operation, or source-authorized migration here.

| Failure stage | Local result and source response |
| --- | --- |
| Validation or real-parser cron rejection | No candidate save/backend mutation. Schedule mutation routes construct 400 with phase validation. Stub mode is different: no cron parser is available, so it stores nonempty cron text without claiming cron validity. |
| Prepublication persistence failure | Previous dictionary restored; applied/published false. Schedule routes construct 503 with operation/job_id/phase, not_published, automatic_retry false. |
| Post-replace persistence failure | Applied/published true, uncertain true; admission quarantined. Schedule routes construct 409 and published_durability_unknown with reconciliation required. |
| Backend register/remove failure after a successful snapshot | Applied state remains; _runtime_uncertain blocks admission/mutations/start. Routes construct 409 with backend phase and published or memory_applied state. A backend side effect may have occurred before its exception; no optimistic undo/retry is attempted. |
| Add/remove success-audit submission failure | Same applied-state retention/quarantine; typed audit-phase 409. A returning audit.log is only an asynchronous submission, not proof the background writer durably recorded the event. |
| Existing load/persistence/runtime quarantine | New admission/mutation/start rejects with phase admission, uncertain true. A new rejected attempt can be not_published while the instance still requires review for an earlier problem. List is diagnostic, not clearance. |

`_schedule_write_error` uses fixed public fields rather than exception text:
error, operation, job_id, phase, state_applied, publication, uncertain,
automatic_retry and reconcile_required. Status is 400 for validation, 409 for an
applied operation, otherwise 503. These are advisory client semantics; they do not
force a client/proxy to avoid retrying. An HTTP response can still be lost after
commit, and another create generates another identifier. There is no durable
request/occurrence key or authoritative operation receipt lookup.

## Backend lifecycle, disabled jobs, and stale callbacks

`start` first checks health. If already running it returns. With a real backend,
it prepares all enabled-job triggers before constructing/starting the backend,
increments the lifecycle generation, registers owner-bound callbacks, starts,
then marks running and audits. Disabled jobs are excluded from trigger preparation
and registration. Backend failure or startup-audit failure invokes
_failed_start_cleanup: running false, generation invalidated, runtime quarantined,
and best-effort backend shutdown. If cleanup itself throws, a reference is retained
for an explicit stop attempt; no backend termination proof is implied.

When APScheduler is unavailable, start marks a stub running state and audits
backend stub; it does not create a backend or validate cron grammar. The dispatch
entry requires a non-None backend, so stub mode cannot dispatch scheduled work.
It is storage/control compatibility, not evidence of timed scheduling. A stub
startup-audit failure also quarantines the instance.

`stop` sets running false and increments generation before shutdown(wait=False).
Backend shutdown or stop-audit errors are typed and quarantine admission. A later
explicit stop may attempt cleanup; it does not automatically clear quarantine or
prove the old backend was terminated. Recreating a Python object after an
uncertain backend is not a source-supported safe reconciliation procedure.

The dispatch gate requires all of these at admission:

- The owner is running with a backend and has no load, persistence, or runtime
  uncertainty.
- The registered lifecycle generation equals the current generation. Retained
  callbacks from stop/start or failed-start cleanup are rejected.
- The dictionary still contains the exact same ScheduledJob object, with enabled
  true. Removed/replaced objects and disabled jobs cannot newly admit work.

A stale callback reaching this gate returns without queue submission or last_run
updates. Backend registrations are owner bound, so stopping/removing/changing one
instance does not authorize another instance's callback.

The separate admitted-callback boundary is essential: once the gate passes,
_dispatch_job awaits _run_job, which can await task_queue.add_task and its instance
lock. During that await, remove/stop can commit and invalidate the owner. The
already-admitted enqueue can then resume and persist its task afterward. The code
does not revalidate the owner inside the queue transaction, cancel an admitted
operation, delete its task, or guarantee absence of post-stop enqueue completion.
A task may also be applied before a queue success-audit failure is raised.

If the product requires **no enqueue may commit after removal/stop returns**, this
implementation does not meet that stronger requirement. That would require an
explicit shared admission/commit transaction or cancellation/reconciliation
protocol across scheduler and queue. It cannot be obtained by documenting the
current object/generation check as an undo or exactly-once guarantee.

## Queue submission, last_run, and remaining limits

`_run_job` honors enabled, submits once, and rethrows typed queue persistence,
identifier or audit errors after best-effort failure reporting; it has no local
retry loop. last_run changes only when add_task returns successfully. job_executed
says enqueued_only and includes task_id. Failure of that scheduler success audit
is a typed TaskQueueAuditError after last_run was set. If the queue's own audit
throws after its commit, last_run remains unchanged because add_task did not
return; the error carries task_id and applied/publication context. None of those
outcomes proves the goal ran. In this observed source, callback queue/audit
exceptions propagate through _dispatch_job but do not themselves set the owner's
_runtime_uncertain flag. The fail-closed scheduler quarantine described above
covers add/remove/start/stop side effects; it is not a claim that every callback
audit error halts later occurrences. A queue persistence uncertainty can block
later writes through the queue's own quarantine even though the scheduler remains
running. An audit-applied callback can recur on a later distinct scheduled fire;
there is no occurrence deduplication or idempotency claim. A stronger
halt-on-callback-audit-failure policy would require an additional explicit source
change.

Remaining source-supported limits:

- last_run is transient metadata. The callback does not save the schedule store;
  a later add/remove may incidentally snapshot it. Schedule state, queued tasks,
  accepted occurrence, and audit delivery are not one transaction.
- Separate processes/instances have stale private dictionaries, local ID checks
  and local quarantine/generation. There is no interprocess owner election,
  fencing, transaction or compare-and-swap; atomic JSON replacement does not
  prevent lost updates. This review's dispatch guarantees are single-instance
  only for cooperating calls through these runtime paths. No multithread safety
  qualification is claimed. The R3 ownership proposal remains a proposal, not an
  installed service.
- list_jobs returns mutable ScheduledJob references. Internal mutation of goal,
  cron fields, enabled, or identifiers can bypass normal persistence/registration
  expectations. No external Python-code isolation is claimed.
- Real APScheduler defaults for overlap, misfires/coalescing, shutdown handling,
  exception processing and recurrence were not exercised. Requirements specify
  minimum versions rather than this environment's installed parser/backend
  identity. A subsequent cron occurrence is not a deduplicated retry receipt.
- File/directory fsync calls are not a power-loss qualification. Unsupported
  directory sync is skipped and new ancestor directories are not individually
  synced. Unlink failure can leave an orphan temporary file. No cross-process,
  rollback-resistant, or root/host-security guarantee is made.
- Resource ACTIVE and schedule listing are not scheduler readiness. HTTP errors,
  retry fields, audit submissions and local last_run each describe separate
  boundaries; none is a durable exactly-once execution acknowledgement.

No additional production route bypassing the bound dispatch gate was found in
this source scope. Direct invocation of private helper code and the already
admitted asynchronous enqueue case are explicitly outside its stale-admission
protection. Any stronger cancellation/transaction requirement needs separately
scoped source changes and validation.

## Source identities

Final text-read/hash observation UTC: 2026-10-30T22:47:58.873383+00:00. Method names above are source
references for these exact bytes; no deployed instance or live state was queried.

| Source | SHA-256 |
| --- | --- |
| `app/agent/scheduler.py` | `71183f5bf54bc36f96a62abf04a1ca73566805f0eda67cdefba5f4410a726181` |
| `app/server.py` | `613a3b08ae074484f0187b0234105c05b85239c45c577eee69a2b0bd8e17052c` |
| `app/agent/task_queue.py` | `50d1a4ebd6132f2593095874b170fa895d09c5bcd9ead9c598312cbf3314fc4c` |
| `app/resource_manager.py` | `43e293d07aa7ed33b240c45033912d6a7c45658577367244503356825ec58ed6` |
| `app/cli.py` | `e8219eb4e8a9c3e41c693922d8c28e9b88287fc3f3f9ea41545b304a3b0d8902` |
| `app/main.py` | `93788adfac34fc5a4e4d6caa58e1ee4a034ffbbbd97906d3ff900f50e8ce48b8` |
| `app/boot.py` | `46a54b70338e2dd1b3a408dcda020fc0cbc080c4f33bc5acfe1d6869d6e12b9e` |
| `app/logs/audit.py` | `835fb246a4e28d02e2f4436e091b6591d490714797620981ef0a3e8447c588e1` |
| `requirements-core.txt` | `07e1f460017cf870d6a5d1ec781acdc792e738ef7a700b8d91df10380ed361a4` |
| `Dockerfile` | `c6160b87f05046edff937a11a8e31554d009f6741a521123d9ae6a917dd43d50` |
| `docker-compose.yml` | `154eea89157f2bdd77f50f98416bbf65aa5c9ef27bc5c1f54812e8037c067f32` |
