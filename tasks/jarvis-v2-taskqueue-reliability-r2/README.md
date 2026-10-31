# TaskQueue collision and damaged-store preservation R2

Offline `workspace-write` continuation of the core backlog. This does not modify,
install or activate the Proxmox broker. Historical R1 packets remain sealed.

## Result and behavior

The frozen R1 source demonstrates deterministic identifier overwrite and damaged
store replacement. New tests against that snapshot fail as expected; those are
defect demonstrations, not a failed current regression. Current source passes
**29 unittest methods /65 subtests, zero failures/errors/skips**. Thirteen methods
are the prior focused regressions (including ten existing agent/scheduler tests
as subtests); sixteen methods cover this successor change. Exact source identities
and intermediate/final receipts are retained rather than overwritten.

- Generate/check the eight-character identifier inside the instance lock. Retry
  at most32 times; `TaskQueueIdentifierError` means no mutation/publication/success
  audit occurred. Existing identifiers and return signatures stay unchanged.
- Invalid JSON/UTF-8, duplicate object keys, nonfinite JSON constants, non-list or
  partial/duplicate/lossy records and unreadable/non-regular stores block writes.
  Compatible records remain available for diagnostic reads; partial data is not a
  complete recovered queue. Invalid bytes and unknown fields are never repaired,
  renamed, deleted or overwritten automatically.
- A blocked add/update/delete raises `TaskQueuePersistenceError(published=False)`
  before a temporary snapshot is created. Existing rollback restores prior memory,
  including the same task object on failed updates, and suppresses success events.
  An unavailable audit reporter cannot remove the block.
- Exact stored whitespace in valid goals/IDs and empty string status/created_at
  fields survives reload. Minimal legacy records with ID+goal remain compatible;
  missing optional fields receive the existing defaults. Unknown fields stay
  write-blocking because silently dropping them would lose evidence.
- Persisted records must be reloadable before publication. Blank/invalid new goals
  and invalid field types fail the mutation with rollback; in-memory-only queues
  retain their prior behavior. `allow_nan=False` rejects nested NaN/Infinity before
  publication. Finite results roundtrip normally.
- Store reads check regular-file type before opening and recheck the descriptor
  with `fstat`. `O_NONBLOCK` prevents a FIFO swapped between stat/open from hanging.
  A real FIFO regression runs in an exclusive child with a five-second deadline.

## Tests and reproduction

From the project root, no installation or app configuration is needed:

```sh
python3 -B tasks/jarvis-v2-taskqueue-reliability-r2/run_checks.py
python3 -B tasks/jarvis-v2-taskqueue-reliability-r2/run_checks.py --save-evidence
python3 -B tasks/jarvis-v2-taskqueue-reliability-r2/run_checks.py --baseline --save-evidence
```

The baseline command intentionally exits1. Its final sixteen-method run has
30 failing cases and7 errors because R1 lacks the new contract; the log includes
individual cases and the frozen source hash. Earlier ten-method receipts are
retained as intermediate work. The final current regression receipt is
`evidence-20261030T222357610970Z.txt`; a later verification would create a new file,
never replace it. `SOURCE-IDENTITY.json` records the current and frozen source.

Fixtures cover repeated/last-attempt/exhausted/concurrent ID collisions; sixteen
damaged-store byte sequences; update/delete rollback on partial loads; load I/O
and audit errors; absent/empty/minimal legacy stores; FIFO and path-swap rejection;
nonfinite serialization; whitespace/empty-status roundtrips; and explicit reload
after a fixture repair. The existing18 injected publication-failure combinations
and local concurrency regressions remain covered.

The source-level loader compiles the actual queue/scheduler definitions after
excluding their real audit imports and default singletons. Its audit recorder is
in memory. No real app/config/audit module, persisted runtime data, scheduler,
provider or model is imported/started. The parent harness guards IP socket creation,
connect/bind/DNS and recorded zero attempts. The bounded FIFO child executes only
the same isolated source loader. These are offline checks, not app integration,
host-principal isolation or live VM evidence.

## Independent review

The existing separate GPT-6 Astra/high reviewer inspected R2 read-only, without
running tests or editing code. Initial review found two medium blockers: valid
whitespace/empty status could quarantine self-generated records, and direct path
reads could block on a FIFO. Both are fixed and directly covered. Its targeted
closure reports: “No remaining blocking issue identified within this targeted
scope.” No Claude or broader qualification is claimed.

## Known stale-writer limitation and next work

`known_stale_writer_limitation` in the final receipt demonstrates two independent
queue instances loading the same absent store. A sequential write from the second
stale instance replaces the first instance's snapshot, losing its task on disk.
This is **unfixed** and is not counted as a passing integrity test. Atomic replace
prevents torn snapshots; the asyncio lock protects one cooperating instance only.
A hash comparison would not provide cross-process locking.

Before supporting multiple writers, choose a single owner or a transaction/lock
design covering read/validate/mutate/durable publication in every writer. Candidate
options are a dedicated queue service, a transactional SQLite store with reviewed
migration, or a separate stable-inode OS lock with reload/merge and crash policy.
Specify task identity/ownership, legacy unknown fields, explicit conflict errors,
process-kill recovery and evidence retention first. Keep this a separate proposal;
do not deploy a hash-check substitute or auto-migrate existing data.

The load block is instance-local. An external edit does not unblock that instance;
preserve the original evidence, explicitly repair/review a separate copy, then
construct a new instance. Already-loaded queues do not detect later external
changes. R1's synchronous I/O, mutable returned objects, unsupported-directory-fsync
and power-loss limitations remain. Regular-file input size is not newly bounded.
Full API/lifespan and long-lived scheduler checks require a separately authorized
dependency environment; no historical 7741-test baseline is reused as current proof.

## Infrastructure boundary

No Proxmox/VM/AI-server access, credential read, package installation, identities,
groups, ACLs, token change, sudo, services, guest/bootstrap changes, activation or
Gate6K privileged qualification. The unchanged pending broker setup request remains
`../proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md`. Public source/dependency
comparison is a separate successor packet at `../jarvis-offline-provenance-r1/`.
