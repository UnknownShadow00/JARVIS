# Offline recovery decisions and protected witness renewal

This implementation admits **disposable synthetic state only**. It never activates
restored branches, starts executors, resumes schedules or changes source tasks.
Approval is historical operator evidence; it is not an execution capability.

The separate SQLite registry indexes an append-only protected intent/commit journal.
Supply a private registry-data directory, a separate private custody directory, an
existing checkpoint guard, externally retained configuration and latest registry
reference, and distinct checkpoint and operator HMAC verifiers. There is no default
key, trust discovery, production enrollment, schema migration or public mutation API.
The operator must retain the returned current reference outside registry authority.
Same-UID/key compromise, secure time and coordinated rollback of all external
custody remain explicit trust assumptions. HMAC is shared-key authentication, not a
public-key signature. Neither ordinary files nor a local checksum prove external
custody against a privileged attacker.

## Data and authorization

Each proposal has a caller-retained canonical v4 UUID distinct from branch/source
identities. The original authority, branch, restore, archive path/manifest digest,
checkpoint generation/head, database digest and original request/task/occurrence
UUIDs remain bound to the verified report. Conflicting branch or restore identities
are refused. The proposal permit binds `verification_sha256`, the hash of the
complete `{proposal, summary}` result, as well as the original verification request
and restore path. Import and verification never imply approval.

Every mutation has a separate short-lived operator HMAC permit bound to request ID,
command, exact payload, local-service scope, principal and source checkpoint. Replay
requires the identical UUID, payload and original permit. Fresh commands require
fresh authorization. Historical evidence is authenticated independently with the
operator key at every restart, even after expiry; expiry never refreshes on replay.

Proposal states are PENDING, APPROVED, REJECTED, EXPIRED and REVOKED. Decisions use
compare-and-swap against the previous decision UUID and bind the complete proposal
hash. Pending decisions record review without approval. Approval/rejection require
an unresolved pending proposal; approval can subsequently be revoked. Expired
authorization remains historical and can be revoked. Rejected and revoked proposals
cannot be reapproved. Decision validity is at most 300 seconds and cannot outlive
the authorizing permit. Restart evaluates predecessor expiry at each historical
admission time, so a later genuine permit cannot bypass an expired predecessor.
No decision changes activation status.

## Commit, interruption and reconciliation

Publication order is signed intent + fsync, SQLite FULL transaction commit, signed
commit receipt + fsync, then response. First-time SQLite schema creation uses a
dedicated staged database and atomic no-replace publication. Only exact empty or
schema-only authenticated initialization stages can continue; arbitrary contents
are quarantined without deletion.

Read-only inspection distinguishes absent request, admitted but never committed,
committed with receipt/acknowledgment unknown, and durable receipt with acknowledgment
unknown. HTTP delivery cannot establish whether an acknowledgment reached its caller.
A hot SQLite rollback journal is reported as
`recovery_sqlite_reconciliation_required`; read-only inspection performs no rollback.
Only the exact independently authenticated last durable admission, matching original
UUID/command/payload/permit and no final receipt, can authorize SQLite to roll back
its own uncommitted spilled pages. Full protected-history and SQL validation then
run before the original event is republished.

An incomplete tail blocks new mutations until its original operation is explicitly
reconciled. Continuation authenticates the original durable admission and only
finishes its exact local SQL/receipt publication. It never invokes external work.
UNKNOWN effects stay UNKNOWN and never generate an automatic retry.

Missing anchors, SQL/journal conflicts, rolled-back databases, foreign custody
inventory, stale locks, incorrect keys and external references fail closed. Partial
publication files are preserved and require explicit forensic quarantine; they are
never treated as an intent or receipt. Replay reuses one completely verified checkpoint-history snapshot while holding
the guard mutex; it does not rescan the same protected chain for each renewal.
Capacity is finite (4–256 events), with no
pruning or deletion. SQLite files are bounded to 32 MiB and evidence to 65 KiB/event.

## Witnesses

A registry reference contains its registry UUID, committed sequence/event digest and
latest witness. Renewal verifies the previous externally retained witness and full
protected checkpoint ancestry, then binds the next witness to the exact current
source head, key and epoch/rollover hash. One renewal can advance at most one epoch.
A new committed checkpoint or epoch is required. Missing or expired custody cannot
be silently replaced with local state. Inspection reports WITNESS_EXPIRED while
retaining a separate historical-integrity result; fresh mutations and configured
application readiness refuse expired witnesses. This retains the same synthetic key; it does
not rotate production keys or replace the original enrollment witness.

Witness publication uses the same SQLite/journal transaction protocol. Concurrent
renewals compare the prior witness, so only one can win. Preserve the old reference
and renewal receipt; obtain the newly verified reference through offline inspection
and transfer it into external custody. Renewal receipts can be independently
verified with `verify_receipt`, trusted expected identities/digests and both HMAC
verifiers. Historical verification alone never authorizes activation.

## CLI and application

`python -m app.agent.operator_cli` exposes these additional modes:

- `--initialize-recovery-registry`
- `--publish-recovery-proposal /absolute/disposable/restore`
- `--record-recovery-decision`
- `--renew-recovery-witness`
- `--reconcile-recovery-operation`
- `--recovery-registry-status`

Supply existing checkpoint flags plus `--registry-config-fd`,
`--registry-reference-fd` and `--operator-key-fd`, including for read-only historical
authentication. Mutation additionally requires `--commit-recovery`, `--operation-id`,
`--permit-fd` and `--recovery-payload-fd`. Reconciliation's payload is an object with
`command` and the original `payload`; use the original permit unchanged. Descriptor
values are inherited explicitly; there is no credential-path/environment fallback.
See the retained synthetic CLI demonstration for exact JSON examples and handoff.

Trusted offline embedding may supply `recovery_registry=` to `Authority`, bound to
the identical checkpoint guard. Startup/readiness verifies it and blocks incomplete
publication. Shutdown performs a final read-only inspection while still releasing
storage ownership on failure. Readiness returns aggregate counts only. Detailed
history appears in authenticated operator diagnostics and read-only offline CLI.
Reporter text explicitly distinguishes approvals from activation. Existing archive
verification remains read-only and proposal publication re-verifies the restored
artifact; neither creates an executable branch. No HTTP approval/completion/witness
mutation route is mounted.

SIGKILL and injected ENOSPC tests demonstrate process crash and transaction recovery,
not physical power-loss qualification or production readiness.
