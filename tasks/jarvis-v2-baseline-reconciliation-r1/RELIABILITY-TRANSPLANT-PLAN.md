# Minimal reviewed transplant and adaptation

Application changes imported from reviewed R3:

- app/agent/authority.py: catch UTC under/overflow as invalid_time (two-line change).
- app/agent/simulation.py: reject execution envelopes in legacy Simulator mutation paths, within existing scoped fenced transactions.
- app/agent/scheduler.py: epoch/failure fences, serialized lifecycle and retained shielded cleanup Task.
- app/agent/scheduler_backend.py: stock APScheduler coroutine executor/MemoryJobStore ownership, actual settlement, partial retry and unsupported-backend refusal.

No execution.py, runtime.py, API auth, durable receipt schema or privileged adapter change is necessary. These four files apply cleanly because current development matches RC1 at the affected original paths. The five documented sibling-baseline differences are reconciled separately; all final app Python bytes equal reviewed R3.

Tooling: R3 runner, completion protocol, pinned exact-node manifest, negative fixtures and tests are selected explicitly. New enrollment module/digest JSON cover all Python test files, with no acceptance-time regeneration. Added reconciliation mode selects only reviewed release/UE5 boundary tests and six policy/example cases. Public historical anonymous-route and ancestor-swap fixtures are mounted read-only inside the namespace to avoid two unqualified skips. They are intentionally vulnerable historical test inputs, not application routes or production code.

The maintenance proposal utility remains separate. It proposes a NEW manifest, refuses incomplete positive generation and records failure evidence only to a fresh exclusive file. Promotion here was explicit: unchanged original603 node lists were compared, the66-node additional suite reviewed, then source/inventory and independent module-policy digests updated. Its baseline field retains historical R2 lineage; actual development baseline and current content digest are recorded in BASELINE.json and VERIFICATION.json. No claim is made that current source is the old R2 revision.

No entire branch was cherry-picked and no unrelated tasks, bootstrap/host-enforcement tools or sealed packets were imported. Independently review the complete exact diff and enrollment decisions, then create a new controlled rehearsal from this candidate. Do not merge it directly into canonical development.
