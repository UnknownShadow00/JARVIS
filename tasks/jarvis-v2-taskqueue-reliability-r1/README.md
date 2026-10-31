# Offline task queue persistence reliability R1

This bounded core change addresses the task queue portion of PROJECT_STATUS.md's
“Run long-lived scheduler and task queue validation” backlog. It improves local
JSON publication and error handling. It does not complete long-lived scheduler
validation or provide evidence for production deployment.

Profile: `workspace-write`. Baseline HEAD:
`7f4ae164261b792262eb9b818421c444c2d4ccff`.

## Change and observable behavior

`app/agent/task_queue.py` now serializes before opening the output file, writes to
a uniquely named temporary file in the destination directory, flushes and fsyncs
that file, closes it, then atomically replaces the final path. On POSIX it attempts
to fsync the containing directory. Explicit filesystem “unsupported” errors
(`EINVAL`, `ENOTSUP`/`EOPNOTSUPP`, `ENOSYS`) allow operation without directory sync;
other directory errors are failures. Temporary files use tempfile's restrictive
permissions; replacement does not preserve the previous inode or its metadata.

Add/update/delete operations raise `TaskQueuePersistenceError` on persistence
failure and suppress their normal success audit event. Existing public method
signatures, AgentTask fields, update object identity, success events, in-memory-only
queues, and the current load/invalid-shape behavior remain unchanged.

| Failure | Final file and memory | Retry behavior |
| --- | --- | --- |
| Serialization, directory/temp creation, write/flush, file fsync, or replace failure before publication | Prior final file remains; the attempted in-memory mutation is restored | Retry is allowed after the underlying problem is addressed |
| Directory sync/close failure after replacement | Published state remains in memory; `exception.published` is true and durability is uncertain | This instance blocks further mutations; inspect the store, then explicitly construct a new instance when appropriate |
| A blocked instance is asked to write again | No file write; attempted mutation is restored to the already published state | Exception reports `published=False` for this new attempt; prior uncertainty remains set |

The existing save-error audit event includes `published` and
`durability_uncertain`. Failure of error reporting cannot hide the persistence
exception or prevent rollback. Temporary cleanup is best effort: an unlink error
must not mask the original error and can leave an orphaned temporary file.

## Reproduce locally

From the project root, with the Python standard library only:

```sh
python3 tasks/jarvis-v2-taskqueue-reliability-r1/run_checks.py
python3 tasks/jarvis-v2-taskqueue-reliability-r1/run_checks.py --save-evidence
```

The second command creates a new, exclusive timestamped `evidence-*.txt` artifact;
it never overwrites earlier evidence. Each artifact records Python version, HEAD,
source SHA-256 hashes, test output, and the absence of actual application module
imports. The harness disables bytecode generation. The test file can also run as
a standard-library unittest module.

## Validation and isolation

The suite executes 13 unittest methods, including all 10 existing functions in
`tests/test_agent_stubs.py` as subtests. Tests include:

- Success/reload/delete semantics, object identity, audit event compatibility,
  missing-task return values, and in-memory-only queues.
- Add/update/delete rollback for each of six injected failure stages: parent mkdir,
  temporary creation, write, flush, file fsync, and replace (18 fault cases).
- Non-JSON and recursive serialization failure before temporary file creation.
- Same-directory complete JSON publication and file-sync/replace/directory-sync order.
- Add/update/delete post-publication uncertainty, published file/memory consistency,
  blocked subsequent writes, and explicit reload into a new instance.
- Unsupported directory sync versus actual I/O errors, audit reporting failure,
  ordinary temporary cleanup, and cleanup failure preserving the original exception.
- Unchanged invalid-store behavior with no automatic rewriting, plus 40 concurrent
  local add/update operations and 20 deletes followed by reload.

These are offline source-level checks, **not full application integration**.
`load_definitions` compiles the actual TaskQueue/AgentTask source after removing
only the real audit import and default singleton assignment. The audit object is
an in-memory recorder. Existing scheduler regressions similarly use the actual
Scheduler source definitions with audit/task-queue imports and its default singleton
isolated. Existing tests run in an exclusive temporary working directory with an
in-memory default queue. The app/config/audit/scheduler modules are not imported;
there are no production data reads/writes, audit threads, services, scheduler start,
network calls, model/provider calls, installation, or dependency modifications.

All injected file operations target fresh temporary directories. Tests do not run
against repository `data/` or existing task persistence artifacts. No Phase 2/3,
guest, host, VM, credential, ACL, or user operations are part of this work.

## Limits and follow-up

No power-loss or storage-hardware durability guarantee is claimed. Directory sync
is skipped off POSIX and where unsupported. Newly created ancestor directories
are not individually synced. No process-kill/faulty-filesystem qualification was
performed. The instance's uncertain-state flag is in memory, so restart/recreation
requires operator judgment rather than a persisted cross-process quarantine.

The asyncio lock protects cooperating calls on this queue instance; it provides no
cross-process locking or lost-update protection between independent instances.
Public APIs still expose mutable AgentTask/result objects, so external mutation
can bypass persistence. File I/O remains synchronous under the instance lock and
full snapshots are rewritten per mutation. Existing malformed-store acceptance
and audit success failures after a successful write are outside this bounded fix.

A separate authorized environment with the application's dependencies is needed
for full API/lifespan integration and attended long-lived scheduler validation.
No deployment or service restart was performed. The parent task owner appends the
required canonical completion entry to the project `tasks/loop-log.md`.
