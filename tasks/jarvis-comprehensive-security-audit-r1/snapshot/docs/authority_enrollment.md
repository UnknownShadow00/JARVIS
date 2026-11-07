# Explicit offline authority enrollment and branch verification

Current implementation and exact reproduction evidence are in the
[sprint 4 packet](../tasks/jarvis-authority-enrollment-r1/REPORT.md).
No production startup, runtime migration, real executor, provider or actual
restored-branch re-anchoring is authorized or performed.

## Normal opening is never enrollment

`Authority(path)` refuses missing, zero-byte and schema-only databases. Missing
paths are rejected before mkdir, writer-lock or checkpoint creation. Its opening
path uses no O_CREAT or schema DDL. `LedgerGuard(initialize=True)` is not permission
to create a new Authority or silently replace a missing store.

Enrolled stores require an explicitly supplied `enrollment_context` witness and
the correct guard before owner takeover. Missing/altered custody phases, marker,
original receipt or genesis continuity block opening. Subsequent operations check
the same custody evidence before admission/dispatch. Default runtime startup does
not load or generate keys, witnesses or approvals: a trusted offline embedding
must bind an already verified Authority. Unprovisioned default startup fails closed.

Pre-existing unmarked stores also refuse normal opening by default. A trusted
embedding may explicitly supply a fresh `legacy_approval=(OperatorPermits, permit)`
capability for `open_legacy_authority`. Its payload binds the absolute database
path, exact logical state and execution_disabled; its checkpoint binds the verified
current head (or EMPTY_HEAD for an unguarded legacy store). The owner-acquired audit
event records the admitted request and authorization fingerprint. Diagnostics say
`LEGACY_APPROVED`, `verified=false`, `new_store_enrollment_proven=false`.

This caller-supplied verifier is a trusted in-process capability, not independent
authentication of historical legacy provenance. There is no automatic approval,
environment bypass, public issuance endpoint or legacy-opening CLI mutation. Local
Python code and verifier/key provisioning remain trusted. Explicit test fixtures
use this compatibility admission only for historical queue regressions; new
enrollment/security tests use the real ceremony and ordinary constructor directly.

## External reservation and custody

`OfflineEnrollment` accepts only an explicitly disposable offline reservation.
The caller provisions separate private checkpoint and custody directories, an
exclusive absent destination under a private parent, a store key, and an independent
expected reservation. The product creates no replacement key/trust context.

Reservation format is `jarvis-empty-store-reservation-v1`; fields are `enrollment_id`,
`store_id`, `trust_id` (distinct UUID4s), `key_id`, absolute `destination`, `custody`,
`checkpoints`, `policy`, `initial_checkpoint`, `issued_at`, `expires_at`, and
`disposable_only=true`. Policy binds original fixed-schema hash, rollover flag,
epoch capacity, max generations and recovery flag. The initial checkpoint is
sequence0, sha256=null, checkpoint_hash=64 zeroes. Reservation validity is at most
300 seconds. The expected reservation is an external trust assertion, not proof
that locally missing files have never existed.

Admission additionally requires a fresh local-service `OperatorPermits` grant for
`enroll_authority`, same enrollment UUID, empty checkpoint and exact payload:
`reservation`, `reservation_sha256`, `execution_enabled=false`. The custody intent
permanently consumes that admission in this dedicated directory. Existing targets,
stages, consumed/conflicting identities, prior checkpoint history, unsafe paths
and incompatible policies fail closed. Checkpoint and custody locks serialize
independent processes. Ordinary opens cannot acquire a new store during any phase.

## Genesis and recovery phases

Intent is signed and durable before stage/database creation. A fixed trusted SQL
schema, metadata, disabled control, ledger marker, enrollment record, committed
receipt and matching audit event are constructed in one FULL-synchronous DELETE
journal transaction. All seed values come from the admitted reservation/decision;
no retry chooses a new UUID, owner or timestamp. The initial owner is an explicitly
non-live generation0 sentinel. Genesis authenticates this complete deterministic
logical state; it does not anchor an unaudited empty schema.

PREPARED binds intent, genesis checkpoint, logical digest and physical database
hash. Stage bytes/identity and signed ENROLLMENT marker are checked before atomic
no-replace directory publication, followed by target revalidation and FINAL.
The resulting externally retained witness binds the final hash, genesis, store,
enrollment UUID, key, destination, reservation and policy. The first ordinary open
requires this witness and advances the non-live owner to generation1 with a new
checkpoint. It does not enable execution or resume restored work.

Recovery is explicitly bounded:

| Durable state | Behavior |
|---|---|
| No intent | UNENROLLED; fresh reservation/admission required |
| Intent only or empty stage | Explicit reconciliation may finish the same deterministic admission |
| Partial SQL/zero DB/unexpected stage inventory | INCOMPLETE/BLOCKED; preserve for manual quarantine, no rebuild/reset |
| Exact committed seed, genesis incomplete | Finish only authenticated matching genesis/checkpoint publication |
| PREPARED and exact stage | RECONCILIATION_REQUIRED; verify and publish with no replace |
| Target published, final missing | Verify exact prepared bytes and finish the same final receipt |
| FINAL, database missing/substituted | BLOCKED; never recreate |
| FINAL, matching descendant ledger | VERIFIED against current checkpoints and original enrollment evidence |

An admitted decision can continue after its short permit expires; it cannot admit
a different operation. Partial files/checkpoints are never deleted to clear a
failure. Storage/permission failures preserve evidence. A pending state is not an
established success. SIGKILL tests cover these transitions; physical power-loss
durability is not claimed.

## Offline CLI

The provider-free `app.agent.operator_cli` accepts `--enrollment-status`,
`--enroll-store`, and `--reconcile-enrollment`. Supply the original checkpoint
policy, `--custody`, and public expected reservation JSON via `--reservation-fd`.
Checkpoint keys use `--key-fd`. Mutations require `--commit-recovery`; new admission
also requires `--operator-key-fd` and `--permit-fd`. Descriptors must be inherited
FDs >=3, with bounded reads. Key/permit bytes are not CLI/environment values.
All trust directories must already exist; none are provisioned by these modes.
Read-only database diagnostics can accept `--enrollment-witness-fd`.

The guarded application demonstration exercises actual FD handoff and CLI calls.
Do not point development commands at real stores or sealed evidence. No HTTP
enrollment/restore/completion endpoint is mounted.

## Restored-branch verification

`BranchVerifier` and CLI `--verify-branch DIR --branch-context-fd FD` are read-only.
They require the original store key, external checkpoint trust reference, protected
restore intent/prepared/final evidence, source completion attestation and a fresh
external branch-verification request. The request supplies branch UUID4, operator
label, exact expected current source head, restore ID, database hash, key identity,
generation lineage and externally maintained reserved branch IDs (max64). Its
validity is at most300 seconds and decision must be `PROPOSE_ONLY`.

The verifier rechecks archive provenance through the protected manifest attestation,
restore continuity, current inert artifact bytes and original identities. It
rejects stale source references, incompatible anchors/generations, copied targets,
damaged receipts/DB, replacement races and IDs conflicting with store/restore/
original request identities or the supplied registry. All original UUIDs, UNKNOWN,
held work and cancellation uncertainty are preserved. The source/archive medium
need not still be available when the protected prepared evidence is intact; this
does not claim the medium's current bytes were checked again.

Output includes detailed consistency summary and a reproducible proposal hash.
The manifest binds the historical parent checkpoint/lineage, current source head,
restore-final hash, database digest, original-request-ID digest, expected external
contexts, operator label and policy. It explicitly states a historical parent
snapshot is not continuation of the source head. `activation_authorized=false`,
`execution_enabled=false` and a separate operator decision is required. No branch
registry, database, checkpoint, lock sidecar or re-anchored history is written.

The operator label is metadata, not a granted execution identity. A read-only
proposal is not a signed approval. Registry freshness/completeness and external
context custody are operator responsibilities; duplicates absent from that
trusted inventory cannot be globally detected by a stateless verifier. Actual
branch admission/re-anchoring remains a separate authorization boundary.

## Limits and activation prerequisites

Local HMAC files, in-process capabilities and colocated receipts do not defeat
privileged/same-UID key compromise or coordinated DB-and-anchor rollback. Keep
the reservation, final witness, latest checkpoint reference, registry, keys and
clock under independently protected custody. A genesis witness proves only its
ancestor; supply a newer protected minimum reference to detect later rollback.

Existing snapshot/restore/export/checkpoint limits and no-deletion policy remain.
Enrollment accepts only the small deterministic seed (1MiB read bound before
publication); later verification is subject to the32MiB logical/source read bound.
These bounds are not a physical filesystem/WAL quota. Unrecognized partial stages
require investigation; no arbitrary damaged-genesis repair or key rotation exists.

Live use still requires explicit authorization, independently protected OS
identities/storage/custody/time, real permit/key provisioning, qualified dependency
closure, broader regressions, approved enrollment/capacity/retention policy and
deployment review. Real restored-branch re-anchoring, production genesis resets,
real migrations and executor activation are not implemented or authorized here.
