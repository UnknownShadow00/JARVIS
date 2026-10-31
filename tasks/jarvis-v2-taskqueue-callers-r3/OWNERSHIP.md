# Task queue caller and ownership map — source-only R3

This source review finds one canonical queue singleton per Python interpreter,
but **no enforced single owner across interpreters, processes, or containers**.
Atomic snapshot replacement prevents partial final JSON writes; it does not
prevent stale writers from replacing another process's committed queue. No
exactly-once enqueue or task execution guarantee follows from the current code.

Profile: `workspace-write`, solely to create this document. The parent is changing
caller code concurrently; the identities below bind this observation, including
the final R3 typed persistence/audit API responses and scheduler changes.
Earlier text-only observations preceded those changes; conclusions below describe
the final source identities listed at the end, rather than that earlier baseline.
No application imports, runtime/process/container inspection, startup, tests,
network calls, credential reads, state access, or infrastructure actions occurred.
Only public source text was read. This review changes no code, service, lock,
state schema, sealed packet, loop log, or manifest.

## Production construction, callers, and consumers

Search scope: all Python under the current `app/` and `scripts/` trees, root
launchers, Docker/Compose source, and shipped frontend sources. Historical
`tasks/` payloads and test fixtures are not production callers. Search expressions
included TaskQueue, task_queue, agent_tasks.json, every queue method name,
launcher workers/reload options, and frontend task/schedule/retry references.

| Source | Queue relationship and observed behavior |
| --- | --- |
| `app/agent/task_queue.py` (DEFAULT_TASK_STORE, TaskQueue.__init__, _get_lock) and module-final `task_queue = TaskQueue(DEFAULT_TASK_STORE)` | Sole production `TaskQueue(...)` construction found. Absolute store derives from this source checkout: `data/agent_tasks.json`. Construction loads a private in-memory snapshot immediately; asyncio lock and quarantine flags belong to this instance. `TaskQueue()` without persistence is available, but production source uses the default persisted singleton. |
| `app/server.py` (queue import and create/list/get/update/delete_task) | Imports that singleton. POST `/tasks` calls `add_task`; GET `/tasks` calls `list_tasks`; GET `/tasks/{task_id}` calls `get_task`; PATCH calls `update_status`, then separately `get_task`; DELETE calls `delete_task`. These are all direct API mutations/reads found. |
| `app/agent/scheduler.py` (queue import and _run_job) | Imports the same singleton; `_run_job` enqueues `job.goal` once per callback invocation. It does not execute the goal. It is the only direct non-API production queue mutation found. |
| `app/agent/reporter.py:7,15–36,65–69` | Imports the singleton and reads `_tasks.values()` directly when no public `tasks` attribute exists. Counts `pending` and `in_progress`; neither acquires the queue lock nor reloads disk. No import/use of this Reporter from another app source was found, so existence of this consumer does not establish that it is running. |
| `app/boot.py:21,158,187–188,263–284` and `app/brain/morning_report.py:13–26,58–64` | Boot imports server, indirectly constructing the queue; their displayed pending counts instead read task-planning `tasks/state.json`/`tasks/todo.md` in their code. They do not read `agent_tasks.json` or drain this queue. No state files were opened during this review. |
| `app/server.py:624` (`_process`), `app/brain/complexity_router.py:36`, `app/brain/planner.py:21`, `app/voice/audio_stream.py:20–28` | Chat/voice/tool planning is separate. The server routes messages and calls registered tools/LLM paths; the standalone Planner returns a TaskPlan. None of these paths calls the queue. No production dequeue, claim, lease, task executor, automatic transition to in_progress/done, or queue-draining loop was found in the searched application source. |

Queue records therefore expose manually updateable status; enqueuing is not
proof that any goal ran. Arbitrary status strings remain accepted. Searches
cannot rule out separately supplied external callers, plugins, manual Python
imports, or alternate import aliases outside this source tree.

## Intended topology and unenforced ownership

- `app/main.py:7–11` reexports the server and calls uvicorn.run without an explicit
  workers/reload argument. `Dockerfile` starts `python -m app.main`. Compose
  declares one backend service/container and a Uvicorn command at
  `docker-compose.yml:37–59`, also without an explicit worker count. These are
  launch intentions, not observations of a live process count or dependency
  defaults. Environment, overrides, external launchers, and framework behavior
  were not inspected or executed.
- Server lifespan (`app/server.py:110–148`) starts/stops its local scheduler.
  Resource wake/sleep (`app/resource_manager.py:365–391`) also starts/stops that
  local scheduler. Within a canonical interpreter import these imports normally
  reference the same object. There is no cross-process election or fencing.
- `app/boot.py:77–98` first probes HTTP health, then can spawn another interpreter
  with Uvicorn. The boot interpreter already imported server and loaded its own
  queue. HTTP readiness does not acquire ownership of the queue store, and a
  concurrent launch can pass through the same check. A losing TCP bind is not a
  queue-file exclusion mechanism.
- `jarvis.py`/`jarvis.cmd` call `app.cli`; `_wake` at `app/cli.py:85–103` may launch
  a server, then falls back to local `resource_manager.wake` whenever `_post`
  returns None. `_post` (`165–172`) collapses transport, HTTP-status, and JSON
  errors into None; it does not prove the server is absent. Local wake starts
  another local scheduler. This is a source-supported route to possible overlap,
  not evidence that overlap occurred. CLI asyncio.run teardown and unknown
  scheduled fire times bound its actual lifetime; no durable CLI daemon is assumed.
- Compose binds host `./data` into `/app/data` (`docker-compose.yml:49–55`). A
  host interpreter and backend container can consequently target the same file
  if launched against that mapping. No container or mount was inspected to
  establish actual use.

There is no process-shared lock, database transaction, generation compare,
owner identity, lease/fencing token, or read-before-every-write in TaskQueue.
A and B can both load snapshot S; A saves S+A; B saves stale S+B, erasing A.
Both atomic replacements and both success audit events can succeed. Their
in-memory reads continue to disagree. The 32-attempt identifier check sees only
one instance's dictionary, so it does not establish cross-process uniqueness.
An uncertain/load-error quarantine also affects only the instance that saw it.
Restart/recreation is not an automatic safe reconciliation strategy.

## Failure and acknowledgement propagation observed in R3

| Boundary | What source now does | What remains unproven or risky |
| --- | --- | --- |
| Queue mutation before publication | `TaskQueuePersistenceError` restores that attempted in-memory mutation; R3 attaches operation/task_id. Identifier exhaustion raises its own error before saving. | Other live instances can still overwrite data; a nonpublished attempt does not prove that an earlier request/other caller never committed. |
| Replacement followed by sync failure | Retains visible in-memory state, raises `published=True`, and blocks later writes on that instance. | Public file visibility is not proof of power-loss durability. Another process is not quarantined by this flag. |
| API typed failures | `app/server.py::_task_write_error` constructs 409 for published/durability-unknown and applied/audit-failed outcomes, 503 for nonpublished/identifier exhaustion. Responses include operation/task_id, publication state, automatic_retry false, and reconcile_required for applied/uncertain outcomes. All three mutation routes catch TaskQueuePersistenceError and TaskQueueAuditError; create also catches identifier exhaustion. No retry is implemented. | This is an advisory application response contract, not client enforcement. A proxy/client can retry a 503 or 409, ignore metadata, lose the response, or repeat a POST. Runtime/framework transport behavior was not qualified by this static review. |
| Scheduler callback | `app/agent/scheduler.py::_run_job` logs job_enqueue_failed best effort for persistence, identifier, or audit errors and rethrows the original typed error without local retry. last_run changes only after add_task returns, and job_executed says enqueued_only with task_id. Failure of that scheduler success-event audit raises TaskQueueAuditError with task ID; last_run is already set because enqueue returned. | If the queue success audit throws after commit, add_task raises TaskQueueAuditError and last_run remains unchanged even though the task was applied; the typed failure identifies this case. last_run is not saved by this callback. A later add/remove may incidentally snapshot it, but restart can lose metadata. APScheduler exception/misfire/coalescing/overlap/default policy and later schedule firings were not measured. |
| Postcommit success audit | Queue `_audit_mutation` wraps success audit submission after the applied mutation in a separate TaskQueueAuditError, with operation/task_id and published bool. It does not roll back applied state. API and scheduler catch that type; the API reports409, task_queue_audit_failed, reconcile_required true, and published_audit_failed or memory_applied_audit_failed. AuditLogger.log (`app/logs/audit.py:51–65`) constructs/enqueues an event; its background writer is separate. | The earlier generic/untyped success-audit failure gap is fixed in this source. A returning audit submission still is not a durable audit-write acknowledgement; later background writer failure is not reported by this return. No transactional outbox exists. If the typed response is lost or ignored, external replay can still duplicate an applied create. |
| Reads/status/reporting | API converts returned AgentTask objects to dicts. get/list expose mutable task/result references; Reporter bypasses the lock. PATCH's update and subsequent read use separate method calls. | No immutable committed snapshot or revision precondition is returned. In-process code can mutate fields without persistence. Other calls may interleave between PATCH operations; another process's reads may remain stale indefinitely. |

R3 distinguishes postcommit audit failure from an uncommitted write whenever
its typed response reaches the caller. Lost HTTP acknowledgements, process
interruption after commit, or a client ignoring the applied/reconcile response can
still leave the caller uncertain although a task exists. A repeated POST generates
a fresh identifier and can add another task for the same goal.
There is no caller idempotency key, operation lookup, durable receipt, request
body fingerprint, or scheduler occurrence key. Neither the new error context nor
random identifiers establishes exactly-once behavior. Known task IDs permit
readback, but current GET reads this process's memory and cannot establish a
cross-process durable decision or durability after a post-replace failure.

The scheduler's own scheduled_jobs.json persistence remains independent of this
queue: `_save` at scheduler.py:121–129 truncates directly and suppresses OSError;
add/remove mutate first. `_register_job` at `90–100` ignores the persisted enabled
flag and registers after a job was added/saved; invalid cron or registration errors
can therefore leave a stored job despite a caller error. These are source findings
for separately scoped follow-up, not fixes or live reproductions in this review.
The remaining limits are explicit: old scheduled-store writes, disabled-job
registration, no durable occurrence deduplication, unenforced multiowner access,
and lost HTTP response/replay. R3 caller errors and last_run ordering do not solve
those separate transaction/ownership problems.

## Client and framework retries: evidence and unknowns

The shipped frontends have no `/tasks` or `/schedule/jobs` caller in the searched
sources. PWA app.js:342–394 reconnects its WebSocket with backoff. Its sendMessage
at `415–437` sends once on an open socket; otherwise it makes one REST `/chat`
fallback request, then displays a manual try-again message on failure. No queued
message replay is shown. The service worker caches static assets only
(`frontend/pwa/sw.js:33–59`). Hologram app.js:95–137 reconnects a display socket;
Electron preload.js:33–58 opens a WebSocket without task API operations. These
connection behaviors are not queue idempotency and do not prove user messages
or external clients never retry.

Framework automatic retries, ASGI disconnect/cancellation semantics, process
worker count, APScheduler execution defaults, browser/network/proxy replay, user
repeat submissions, external API clients, and restart supervision effects remain
unknown. `requirements-core.txt` uses broad minimum versions for FastAPI,
Uvicorn, HTTPX, requests, and APScheduler; installed versions were not imported or
inspected. Boot/readiness loops and CLI wake fallback are distinct from a queue
write retry. No source retry loop around add/update/delete was found. No inference
of exactly-once processing, execution, delivery, or audit durability is warranted.

## Proposed ownership and transaction design — not implemented

A future single-host design can use a dedicated queue owner with a transactional
store; all ASGI workers, scheduler triggers, CLI, and reporters would call that
owner instead of loading/writing private snapshots. This is a proposal requiring
separate implementation/validation; no service, socket, database, lock, migration,
or ownership configuration is created by this document.

1. Establish exclusive owner admission with a stable dedicated lock identity and
   a persistent monotonically increasing fencing generation; hold ownership for
   the owner's lifetime and check the generation on every transaction. Do not
   lock the replaced JSON inode or use an unfenced stale PID file. CLI/server
   unavailability should return an unavailable result, not silently create a
   second local queue owner. Container and host launchers must share the same
   ownership scope or use separate explicitly named stores.
2. Store canonical tasks and operation receipts transactionally, for example in
   an approved local SQLite design. Every write reads/checks current state inside
   its transaction; no stale whole-file snapshot overwrites. Require database
   uniqueness for full-size task IDs and authenticated operation keys, and
   revision preconditions for updates/deletes. A process lock alone around the
   existing stale dictionary is insufficient.
3. Persist a caller operation key, authenticated caller identity, canonical request
   digest, resulting task ID/version, and receipt in the same transaction. A
   repeated key with the same request returns the existing receipt; a changed
   request is a conflict. Define key retention/expiry explicitly. After a lost
   acknowledgement, query that receipt instead of generating a new create.
   An uncertain commit must be reconciled under the owner before admitting more
   writes; a new Python object alone does not resolve it.
4. Give scheduled firings a durable key such as job ID, schedule revision, and
   scheduled instant. Commit the accepted occurrence, task, and accepted-at
   metadata together. Define missed-fire, overlap, cancellation, and catch-up
   policy explicitly. Do not call enqueue completion goal execution.
5. Add an audit outbox record to the same commit. Logging delivery happens
   separately with a stable event ID and an explicit delivery policy; an audit
   transport error must not turn an already committed create into an apparently
   uncommitted write. Return immutable versioned results/readbacks from the owner.
6. Future actual task execution needs its own claim/lease, attempt ledger,
   recovery rules, and effect-specific idempotency. A transaction can deduplicate
   accepted enqueue operations; it cannot guarantee exactly-once arbitrary
   external side effects. Reconcile output/receipt loss and owner takeover before
   making any stronger guarantee.

Future validation should exercise two independent processes against one store,
stale-owner fencing, concurrent same-key requests, failed/lost responses after
commit, audit failure, duplicate scheduled occurrences, and crash/restart
reconciliation. Those tests and an approved migration/rollback plan belong to a
new implementation scope. Historical sealed suites and this static map do not
satisfy them.

## Source identities

Source-only hash observation UTC: 2026-10-30T22:34:43.594493+00:00. Source refs above refer to these
bytes. Earlier observation at 22:32:08Z saw intermediate queue f271ead…
(before the final audit-error wrapper); the final table supersedes that baseline.
The parent may make later changes and should bind its own final evidence.
This document is not a claim about any currently running deployment.

| File | SHA-256 |
| --- | --- |
| `app/agent/task_queue.py` | `50d1a4ebd6132f2593095874b170fa895d09c5bcd9ead9c598312cbf3314fc4c` |
| `app/agent/scheduler.py` | `696a32f6adb02fbfe0bd48688903cccdf49a125543a12e7d8ea4a4341f52b855` |
| `app/agent/reporter.py` | `ec6b4f7dc7d24eb872c1d6e0bb377f5828fe3b606fb2103d4e966d66c21000b5` |
| `app/server.py` | `6e9f1a5a8d6055617acc25976d45dcdad67f4eb67521f2f2aa6a75fb6ba9f89a` |
| `app/main.py` | `93788adfac34fc5a4e4d6caa58e1ee4a034ffbbbd97906d3ff900f50e8ce48b8` |
| `app/boot.py` | `46a54b70338e2dd1b3a408dcda020fc0cbc080c4f33bc5acfe1d6869d6e12b9e` |
| `app/cli.py` | `e8219eb4e8a9c3e41c693922d8c28e9b88287fc3f3f9ea41545b304a3b0d8902` |
| `app/resource_manager.py` | `43e293d07aa7ed33b240c45033912d6a7c45658577367244503356825ec58ed6` |
| `app/logs/audit.py` | `835fb246a4e28d02e2f4436e091b6591d490714797620981ef0a3e8447c588e1` |
| `app/brain/planner.py` | `1a6bb736c0d7b5ff9705a41af68e0b9f7d5e524d4481f0e7bb8b7f1ce0879fa2` |
| `app/brain/complexity_router.py` | `f3f3f7531bc0a54bd1292403f3affbfcc568540d6e6c239819cc52a5a732d9e6` |
| `app/brain/morning_report.py` | `fe14da5b011e0f5663c946b21c42f78f56fc51503425e855319ec39f79d24cd2` |
| `app/voice/audio_stream.py` | `60a3026396b204ffc1e905d2f58c34b3f26c9f7bd7b20d39f0d65577ccdc34c8` |
| `jarvis.py` | `bec4615393a509b66e24defceb1b5353e6f7ed838a38803faadd18ecddf50eca` |
| `jarvis.cmd` | `a60525ab730e83ee30c75d8b5b43139287c064efa3b0c0379b478f4dec6eeb5d` |
| `Dockerfile` | `c6160b87f05046edff937a11a8e31554d009f6741a521123d9ae6a917dd43d50` |
| `docker-compose.yml` | `154eea89157f2bdd77f50f98416bbf65aa5c9ef27bc5c1f54812e8037c067f32` |
| `requirements-core.txt` | `07e1f460017cf870d6a5d1ec781acdc792e738ef7a700b8d91df10380ed361a4` |
| `frontend/pwa/app.js` | `003ea4cfdf02674fd984978501105fcbe97513493c3b21c77265fd63030c8bde` |
| `frontend/pwa/sw.js` | `e2ee7691b2493f619655321013b988af8c22e93caa2eced4b1666bb23cf677de` |
| `frontend/electron/preload.js` | `8738401bab49baa4dcf421e8c6f38d4fcebbe60a7d0e6c43867589d16e05a691` |
| `frontend/hologram/app.js` | `99282e385ba8e2dc54316d6cb9d81d96230fa86a1f2f9ea0b286bd4db21ee401` |
