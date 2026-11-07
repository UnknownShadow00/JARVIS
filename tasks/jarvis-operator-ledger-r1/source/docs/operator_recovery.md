# Offline operator recovery and ledger protection

Real execution remains disabled. This interface never retries uncertain work,
accepts caller completion results, restores a ledger, or deletes protected history.
The reproduction harness uses only disposable databases and synthetic credentials.

## Read-only inspection

`jarvis recovery [--task-id UUID] [--limit 100] [--offset 0]` reads
`GET /operator/diagnostics`. This route requires a configured bearer credential
even if ordinary routes allow anonymous local access. It returns only diagnostic
metadata, not goals, payload values, keys, or mutation capabilities. No operator
write endpoint is mounted. A missing credential or unavailable state is a nonzero
CLI result; no service starts and no retry/fallback mutation occurs.

Diagnostics show task state versus outbox state, admission UUID and operation,
receipt identity/state/payload hash/audit presence, expected phase receipts,
occurrence/task/nominal bindings, schedule last/next nominal, overdue blockers,
failed and UNKNOWN counts, cancellation uncertainty, recorded versus published
results, export publication gaps, and safe recommendations. Admission and claim
are never represented as completed effects. Invalid/inconsistent records remain
blocked rather than being repaired by inference.

For a quiesced store whose application cannot start, `app.agent.operator_cli`
provides a separate provider-free entrypoint. Its required database path is
explicit; it has no real-runtime default. Checkpoint configuration requires the
separate checkpoint directory, store UUID and an explicitly inherited key FD
(number >=3). Key bytes are never accepted in arguments or environment variables.
The module uses SQLite mode=ro and the existing writer lock, refuses a running
owner, and does not advance ownership, finalize pending checkpoints or enroll a
store. It reports pending/corrupt/missing state and exits nonzero. SQLite's
read-only connection semantics are used; this is not a hostile-process filesystem
sandbox qualification.

Use the guarded reproduction below for development rather than importing the
application/dependency target on the host. The full-app demonstration also runs
the quiesced CLI and verifies unchanged database/checkpoint contents.

## Protected checkpoint model

`LedgerGuard` is an explicitly supplied local embedding dependency. A new
`Authority(..., ledger=guard)` receives an external HMAC key and store UUID;
`initialize=True` permits initial creation only. Existing unguarded ledgers refuse
implicit enrollment. A marker in the existing records table makes a guarded
store refuse opening without its guard. No schema migration or key provisioning
of a real store is performed by these APIs or this sprint.

The authenticated checkpoint journal must be a separate private directory outside
both database and export trees. It contains a monotonically ordered, chained
intent/final sequence. Each transition binds full logical SQLite state (schema,
ordered table rows and rowids), prior digest, intended digest, and latest durable
event/request identity. Audit receipts and events are part of that state.

An intent is durable before SQLite COMMIT, and its final record is durable before
success acknowledgement. On restart, exactly one terminal pending intent may be
resolved only when the database matches the authenticated prior or intended
state. Any other mismatch, missing anchor, invalid HMAC, gap, wrong key, changed
schema, or rollback is rejected. A failed/ambiguous publication poisons the owner;
only explicit reopen can reconcile it. No missing anchor is reconstructed from
an existing nonempty database. Publication uses Linux renameat2(RENAME_NOREPLACE),
file fsync and directory fsync; it never overwrites a checkpoint.

This uses HMAC authentication, not public-key signatures. Trusted local Python,
key custody and the protected anchor directory are assumptions. Same-UID key
compromise or coordinated rollback of both database and trusted anchors is not
prevented. No key rotation, hardware monotonic counter or multi-host consensus
is claimed. A kill after first schema DDL but before the first genesis intent is
fail-closed/manual quarantine; arbitrary-point first-enrollment recovery is not
claimed. Normal transaction, export, archive and reconciliation crash boundaries
are exercised with real independent processes.

## Bounded local recovery actions

`RecoveryActions` accepts a short-lived HMAC permit from a separately trusted
`OperatorPermits` issuer. The permit binds principal, scope, request UUID4,
command, payload hash, exact protected checkpoint, issue time and expiry
(maximum five minutes). There is no issuance endpoint and no credential generator.
The verified authorization decision and mutation receipt commit in Authority.
Same-ID replay preserves the original decision; changed command/payload/principal
conflicts. Stale/expired/forged grants fail closed.

Supported actions are:

- Publish an existing validated synthetic result for an UNKNOWN task, preserving
  the original operation and phase receipt IDs. It never invokes the registered
  executor. No evidence means no success/cancellation inference.
- Disable an exact overdue schedule without catch-up. Held occurrences become
  cancelled; uncertain/claimed work receives cancellation intent. Terminal task
  records are preserved byte-for-byte. The ordinary bulk stop/remove path now
  follows the same history-preserving rule.
- Admit and export a ledger snapshot, publish its audit receipt, and prepare an
  archive-copy eligibility record. No protected state is removed.

Export audit reconciliation may finish an already durable authenticated admission
after the original permit expires. It requires the exact stored destination and
a complete anchored manifest, and performs audit publication only. It never
regenerates a missing/partial export. This is continuation of the original durable
authorization, available only through the trusted-local API.

## Export and archive retention

Exports contain deterministic `state.jsonl` plus an HMAC-authenticated
`COMPLETE.json` manifest. Verification checks exact inventory, member SHA256,
bytes/rows, schema/row ordering, event range/continuity, logical state digest and
the historical checkpoint still retained in the protected journal. The local
recovery layer additionally requires matching durable export admission and audit
publication. A manifest alone is not authorization or current database state.
No import/restore implementation is provided.

Crash-partial exports remain quarantined and same-ID regeneration is refused.
No automatic cleanup exists. A dedicated export root admits at most16 directories
and64MiB accounted files, including incomplete exports, and checks free space.
Each logical state/export is bounded at32MiB/100000 rows. The journal is bounded
at9999 transitions and32 staging files; capacity errors fail closed. These logical
bounds do not constitute a filesystem quota or a physical SQLite/WAL size limit.

Retention eligibility explicitly protects held, claimed, UNKNOWN, cancellation
and unresolved receipt evidence. A plan includes cutoff, totals, complete-list
flag, deterministic decision hash and exact checkpoint. Archive preparation
refuses more than200 eligible tasks and rejects exports that do not cover the
current eligible task records exactly. The bounded full decision is audited.
Receipts, events, occurrences, tasks and outbox records are never deleted, even
when eligible for archive copying. A future deletion policy requires separately
verified integrity, checkpoint continuity and approved retention semantics.

## Reproduction and remaining activation gates

Run sequentially from the project root:

```sh
python3 -I -B -S tasks/jarvis-operator-ledger-r1/run_checks.py --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-operator-ledger-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Read the new task's REPORT.md, OPERATOR-DEMONSTRATION.json, RESULTS.json and
INDEPENDENT-REVIEW.md for source-bound evidence and known failures/warnings.
Existing real databases are not enrolled or migrated. Actual key/FD provisioning,
protected OS principal/storage separation, backup/restore drills, quarantine disk
operations and any future destructive retention policy require their own scope.
All prior serial-broker/VM164/no-NIC/Gate6K prerequisites remain unchanged. Real
execution, providers, production startup, credentials and infrastructure are not
authorized or activated by an offline pass.
