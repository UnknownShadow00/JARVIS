# Offline audit continuity and disposable restore

Current [enrollment and branch verification](authority_enrollment.md) adds a
separate explicit genesis ceremony and read-only restored-branch proposals.
Normal missing-store creation is disabled. The earlier legacy bootstrap crash
limitation below is now handled by that ceremony when deterministic committed
seed evidence exists; arbitrary partial SQL still requires quarantine.

This is an opt-in local embedding capability. It enables no real executor,
provider, production service or runtime migration. Reproduction and exact results
are in [the sprint 3 packet](../tasks/jarvis-audit-disaster-recovery-r1/REPORT.md).

## Checkpoint generations

`LedgerGuard(..., rollover=True, epoch_capacity=9999, max_epochs=16,
recovery=True)` retains every original checkpoint and advances the global
sequence across generations. Capacity is explicitly bounded: 4–9999 checkpoints
per generation and 1–16 generations. With rollover disabled, the original single
9999-checkpoint limit applies. Exhaustion refuses further writes; no cleanup or
chain reset occurs. Changing the policy after rollover is rejected.

Generation zero retains its existing flat intent/final files. Each later
`epoch-NNNN/LINK.json` and root rollover intent/commit binds the previous terminal
head, prior transition hash, store identity, same-key identity and policy. Intent,
linked and committed are distinct states. An authenticated unique pending LINK
can finish on startup. An intent without LINK requires explicit operator recovery.
An authenticated recovery admission is durable before continuation; after a crash
it can finish the same operation even after the original short-lived permit
expires. It cannot authorize another operation. Committed recovery links bind
their admission receipt hash, so deleting the receipt is detected.

Every read checks file ownership/mode/link constraints and hashes fresh bytes.
The bounded 2048-entry decode/HMAC cache is keyed by that content hash; returned
objects are copied. It skips repeated decoding of unchanged content, never file
reads, hashing, chain validation or complete logical database verification.

## External trust context

Archive restoration requires an independently supplied reference containing
`store_id`, `key_id`, `epoch`, `rollover_hash`, `head`, `valid_from`, `expires_at`.
The head contains sequence, logical-state SHA256 and checkpoint hash. Validity
is bounded to 24 hours and checked against the local clock. The reference is an
expected ancestor, allowing legitimate descendant history while rejecting a
missing ancestor, wrong generation/key, expired reference or older chain.

`trust_reference()` produces a public witness; storing it beside the ledger does
not establish independent custody. Its provenance, external protection, secure
clock and HMAC key custody are caller responsibilities. Local HMAC files do not
defeat key compromise or privileged/same-UID coordinated database-and-anchor
rollback. This implementation uses one key; key rotation and hardware anchors
remain future work. No synthetic key in a test is a production credential.

## Export and restore

Recovery-enabled exports use a version 2 manifest with generation lineage. A
protected completion attestation is issued only after the source export-complete
receipt and checkpoint are durable. A subsequent source receipt binds the
attestation hash. Missing attestations block archive acceptance, and removing an
attestation after recorded success also fails source readiness. A manifest alone
cannot claim audited publication.

Archive verification requires the expected manifest hash, exact file inventory,
ordered record hashes, supported fixed schema, source publication attestation and
the expected external trust reference. It reports schema compatibility separately
from semantic reconstruction verification. Version 1 exports remain verifiable
through the earlier interface but cannot be restored through this workflow.

Restore requires a canonical UUID4, explicit disposable destination and a fresh
`OperatorPermits` authorization bound to actor, command, target, manifest and
current checkpoint. No archive SQL is executed. One SQLite FULL-synchronous
transaction reconstructs the trusted schema and explicit ordered rows, then
checks SQLite integrity, complete logical digest, store marker and task/receipt/
outbox/scheduler consistency. UNKNOWN work, original identities, cancellation
uncertainty and held outbox records remain intact.

The protected phases are intent, prepared and final. Preparation fsyncs the
complete artifact before signing a prepared receipt. Linux `renameat2` with
`RENAME_NOREPLACE` publishes its exclusive directory; final publication is then
recorded. Reconciliation can publish an exactly verified prepared artifact,
including after the original source/archive becomes unavailable. Partial targets
without a prepared receipt require manual quarantine; they are never rebuilt by
inference. Any error after a mutation reports reconciliation required.

Each artifact has a read-only `state.sqlite`, signed `RESTORE.json` and
`DISPOSABLE.json`. `verify_restored()` rechecks current bytes, protected phase
links, inventory and semantic state. Application diagnostics report receipt
status, explicitly separate from current artifact verification. `Authority`
refuses these artifacts before creating a writer sidecar. Restoring historical
data does not create a runnable branch or resume execution. A future separately
authorized branch/re-anchor ceremony would be required for runtime use.

## Operator interface

The provider-free `app.agent.operator_cli` defaults to read-only. It uses existing
exclusive journal locks and refuses an active application owner. No public
restore/completion endpoint exists. Supply checkpoint/store identity and key
through `--key-fd` (inherited FD >=3); the public trust JSON uses `--trust-fd`.
Key bytes and permits are not command-line/environment values. See the guarded
full-application demonstration for actual FD handoff rather than opening real
runtime data to reproduce this feature.

Read-only modes are `--checkpoint-status`, `--verify-archive DIR` with
`--expected-manifest-sha256 HASH`, and `--verify-restored DIR`. Opt in using
`--rollover-enabled` and the original capacity/policy; diagnostic database mode
can also specify `--disaster-recovery-enabled`.

New restore admission additionally requires `--restore-archive DIR`,
`--disposable-target-parent DIR`, `--operation-id UUID`,
`--expected-manifest-sha256 HASH`, `--operator-key-fd`, `--permit-fd` and
`--commit-recovery`. The permit command is `restore_archive`; payload is exactly
`export_id`, `manifest_sha256`, absolute `target_parent` and `restore_id`.
`--resume-rollover --operation-id UUID --commit-recovery` requires a new scoped
permit unless the same durable admission already exists. Its command is
`resume_rollover`, payload is the recorded rollover `operation_id`.
`--reconcile-restore UUID --commit-recovery` only continues a protected prepared
admission and requires no new permit. Neither continuation reconstructs unknown
missing state or authorizes execution.

## Bounds and deployment limits

Logical snapshots remain capped at 32MiB/100000 rows. Restore parents allow at
most four artifact/staging directories with 64MiB accounting; protected journals
allow at most 64 restore admissions and 256 export attestations. Existing export
limits remain 16 directories/64MiB. Partial artifacts consume capacity. These are
application bounds, not a filesystem/SQLite WAL quota. No protected deletion,
automatic retention cleanup or key provisioning is implemented.

Verification remains linear in protected history and logical state. The packet
benchmarks bounded synthetic histories; it makes no production SLO or million-row
claim. SIGKILL tests exercise process interruption and fsync ordering, not actual
hardware power-loss durability. A crash before initial genesis intent still
requires manual quarantine. Live activation requires independently protected OS
identities/storage, externally custodied keys/anchors and clock, approved policy,
qualified dependencies, enrollment/branch recovery and separately authorized
deployment/executor qualification. This guide authorizes none of those actions.

## Subsequent offline recovery milestone

[Durable recovery decisions and witness renewal](recovery_decisions.md) adds a
separate synthetic SQLite registry and authenticated non-activating operator
decisions. Source/archive/manifest/generation and original UUID bindings remain
protected. Existing sealed evidence and original enrollment witnesses are retained;
renewal advances a separately custodied checkpoint minimum, without key rotation
or branch activation.
