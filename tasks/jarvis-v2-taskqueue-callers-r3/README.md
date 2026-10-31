# TaskQueue caller failure propagation R3

Offline `workspace-write` successor, with no application import or startup. Prior
broker, queue and provenance packets remain sealed and unchanged. Current source
has moved beyond R2; historical test/source identities are not silently relabeled.
`source-snapshot/` preserves the seven exact public application/test files and its
own source manifest; these copies were not imported or installed. Frozen prechange
sources and `source-diff.patch` retain the predecessor-to-successor comparison.

## Concrete defects and changes

The source audit found one canonical TaskQueue per interpreter, imported by the
HTTP server, scheduler and reporter. It found no task-queue executor. Independent
processes/containers can still load separate snapshots of the same JSON store.
`OWNERSHIP.md` maps direct callers, launch paths, CLI wake fallback, consumers,
remaining risks and a proposed transaction/ownership design. No single-owner
service, lock, migration or deployment has been introduced.

Three failure paths are now explicit:

1. Queue persistence exceptions carry the attempted operation and task ID,
   including the new ID from a failed create. Rollback/publication behavior stays
   unchanged. HTTP POST/PATCH/DELETE catch these exceptions rather than losing the
   outcome inside a generic500 error.
2. Queue success-audit submission can fail after the mutation was applied. A new
   `TaskQueueAuditError` carries its operation/ID and whether a store was published.
   It does not call this a persistence failure, roll back a committed snapshot or
   repeat the mutation. HTTP and scheduler callers handle this separate outcome.
3. Scheduler `last_run` is assigned only after add_task returns successfully.
   Typed enqueue failures retain the prior timestamp, emit a best-effort
   `job_enqueue_failed` and re-raise the original exception without retry. The
   existing `job_executed` event name is retained for compatibility, with the task
   ID and `outcome=enqueued_only`. If that event's submission fails after enqueue
   returned, a typed audit error retains the task ID and the updated timestamp.

Successful API response shapes, missing update404 and delete false behavior stay
unchanged. The new failure JSON omits exception messages, private filesystem paths
and task goals:

| Failure | HTTP | `publication` | Reconcile |
| --- | --- | --- | --- |
| Write failed before replacement or blocked load/uncertainty |503|`not_published`|false for this attempted write |
| Replacement occurred but directory-sync durability is uncertain |409|`published_durability_unknown`|true |
| Applied persisted mutation; success audit submission threw |409|`published_audit_failed`|true |
| Applied in-memory-only mutation; audit submission threw |409|`memory_applied_audit_failed`|true |
| Identifier attempts exhausted |503|`not_published`|false |

Each body includes fixed `error`, `operation`, `task_id` (null for identifier
exhaustion), `publication`, `automatic_retry=false` and `reconcile_required`.
There is no retry loop or Retry-After instruction. These fields are advisory to
clients, not an HTTP idempotency mechanism. A later blocked write reporting
not_published describes that attempt; it does not settle an earlier uncertain
publication. A missing-delete false response also does not certify prior disk
durability. Readbacks use the current in-memory snapshot and do not prove durable
storage, completion or goal execution.

## Evidence and reproduction

```sh
python3 -B tasks/jarvis-v2-taskqueue-callers-r3/run_checks.py
python3 -B tasks/jarvis-v2-taskqueue-callers-r3/run_checks.py --save-evidence
python3 -B tasks/jarvis-v2-taskqueue-callers-r3/run_checks.py --baseline --save-evidence
```

Current receipt `evidence-20261030T223312529709Z.txt` passes **42 unittest methods
/82 subtests**, zero failures/errors/skips, forbidden module imports or guarded
parent-network attempts. This combines thirteen new caller methods with the29
relevant existing queue regressions, rerun because their actual queue/scheduler
source changed. It does not rerun the broker or historical baseline suites.

The final frozen-R2 baseline runs only thirteen new methods and intentionally
exits1 (five failing cases/nineteen errors), demonstrating prior unhandled outcome
exceptions, missing context and premature scheduler timestamps. Earlier baseline
and implementation receipts are preserved. `before-tests.txt` is an initial
fixture AST-location error and **is not defect evidence**; the corrected receipt
and final frozen-source run supersede it. No source defect is inferred from that
fixture mistake.

Tests execute actual queue methods and scheduler callback definitions using fresh
files and an in-memory audit recorder. HTTP handler/helper definitions come from
the actual server source, with imports/application setup/decorators excluded and
JSONResponse replaced by a response recorder. They test handler status/content,
not FastAPI routing, middleware, Pydantic models, response serialization or ASGI.
The bounded FIFO child from existing queue tests uses its isolated source loader.
No real app/audit/config/server modules, runtime state, services or provider/model
calls are loaded. `SOURCE-IDENTITY.json` records exact source hashes and absent
FastAPI/Pydantic/pytest/APScheduler discovery; no dependencies were installed or
inspected package payloads imported to make integration possible.

New cases cover real file failures before/after publication for every API mutation,
no internal retry, original bytes on failed writes, exact reconciliation IDs,
quarantined loads, identifier exhaustion, successful/missing-task compatibility,
scheduler timestamps and exception identity, and persisted/in-memory postcommit
audit failures for all three mutations. Syntax/source compile and git diff
whitespace checks also pass without imports.

## Independent review and limits

The existing separate GPT-6 Astra/high reviewer inspected these caller changes
read-only and reported no blocking issue. It confirmed explicit per-attempt
outcomes, no internal retries, scheduler timestamp ordering and compatibility.
It did not run tests or modify code. Its residual limits are retained: retry flags
are advisory; recurring scheduling is not deduplication; audit submission is not
proof of durable audit storage.

There is no transactional outbox, durable occurrence/idempotency key, request
deduplication or cross-process store lock. A committed HTTP response can still be
lost and an external client can repeat POST after a restart. The scheduler's
enabled flag and scheduled-job store have separate preexisting defects described
in OWNERSHIP.md. `last_run` still means acknowledged enqueue in memory and is not
automatically saved by the callback. APScheduler retry/overlap/restart behavior and
full dependency/application integration were not executed. No exactly-once or
durable-audit guarantee is claimed. Existing returned-object, sync-I/O and power-
loss limitations remain.

## Next safe unit and authorization boundary

Review scheduler disabled-job admission and scheduled-job persistence using fresh
failure fixtures, or refine the proposed owner/idempotency/outbox migration
contract. Do not install a service, auto-migrate or treat hashes as a lock.

No package install, service start/restart, deployment, privileged identity/ACL/token
change, Proxmox/guest/AI access, protected install/bootstrap/activation, shared
resource change or Gate6K qualification. The existing sealed broker setup packet
and missing trusted-bootstrap facts remain pending, not newly approved.
