# V2 transactional authority — implementation contract

Current base is3baba67546d7d21ee1b4dcb251f0f730fe113172; ENTRY.json binds ancestry
and carried source fixes. Historical seals remain immutable. Resource hold for
the specific2048MiB Nexus experiment applies to heavy/multiprocess tests, not
editing/static work. No production/external execution is enabled.

## Chosen mechanism

One standard-library SQLite authority owns queue, schedules, occurrences,
idempotent receipts, outbox and simulation/reconciliation state. A process-lifetime
nonblocking stable-file flock excludes simultaneous writers; durable generations
and transaction-time identity checks fence stale owners. No daemon/account/install.
SQLite BEGIN IMMEDIATE, bounded busy timeout, foreign keys, WAL and synchronous
FULL define database commit boundaries, not a hardware power-loss guarantee.

All mutation requests carry a canonical full UUID and a trusted actor scope.
Public scope is server-owned and never a submitted username/scope/header. Preserve
the existing optional bearer policy: validate it where configured; otherwise use
an explicit local-service scope under current access policy. All clients sharing
that scope also share its idempotency namespace; this is not multi-user isolation
or authorization. No authentication setting/policy changes are made.
Same UUID/scope/operation/canonical payload returns the durable original receipt;
scope/payload/operation mismatch conflicts without revealing the original receipt.
The receipt is committed in the same transaction as state/events/outbox; a lost
HTTP acknowledgement is reconciled by that key, not a new blind request.

Schedules have stable full UUIDs/revisions. Occurrences use schedule UUID,
revision and normalized nominal UTC time for deterministic full UUID identity.
Occurrence acceptance, task creation, last_run and outbox/receipt commit together.
Stop/remove/disable invalidate admission atomically and cancel pending scheduled
dispatch. Already claimed simulation work becomes cancel_requested/unknown;
possible effects are never retrospectively declared cancelled.

Real dispatch is unavailable. A separately enabled test-only Simulator can claim,
record an effect entirely inside SQLite, acknowledge, crash or reconcile. Startup
turns abandoned claimed work into UNKNOWN; it never returns it to pending dispatch.
Reconciliation cannot silently resubmit. No public endpoint can fabricate success
or access simulation transitions. Local Python code is trusted; this is not a
sandbox against a malicious process controlling the database owner.

Legacy JSON import is explicit, transactional and synthetic-testable; never an
automatic runtime migration. Preserve old bytes and mapping/receipt evidence;
historic completed/in-progress work is imported unknown, schedules disabled.

## First files/responsibilities

- app/agent/authority.py: durable authority, ownership, receipts/admission/cancel.
- app/agent/simulation.py: no-I/O-effect simulator/reconciliation only.
- app/agent/task_queue.py and scheduler.py: compatibility/facade integration, no
  independent JSON writer or stale callback admission path.
- Actual application factory/API/readiness: all task/schedule mutations use the
  authority; execution unavailable and mandatory storage startup failures propagate.
- New private packet fixtures: independent-process/crash/race/replay/recovery,
  explicit migration and actual app/factory lifespan/readiness under existing cage.

Final report must distinguish new contracts from historical suites, process-kill
evidence from physical disk power loss, and reliability readiness from disabled/
unqualified real execution. Exact dependency blockers do not stop independent
core implementation. No protected/PVE/guest/real-provider action is authorized.
Preserve unrelated application functionality. A standalone V2 router/factory alone
does not qualify full existing app startup; actual entrypoint/lifespan must be
tested in synthetic/offline configuration or carry its exact dependency blocker.

Final implementation note: the parent cleared the specific2048MiB experiment
hold after exit/cleanup evidence (BUILD-RESULT.json SHA256
498fb224e38fc53a975a78a04149d4bfeb047e699b52bbe78bd0d5371d451364).
Fresh headroom and fixed guards applied to each later test; an interim load
refusal launched nothing and was preserved. REPORT.md/RESULTS.json describe the
implemented contracts and final evidence; this initial design is not a live grant.
