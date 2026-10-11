# Authoritative lineage and global attempt ledger — proposed schema 4

Use one protected lineage authority rooted at the real V2 epoch606a991a06b74fd79ed72b308417cc3f. Preserve the schema3 predecessor as a sealed immutable archive; never insert a second epoch into its DB. Proposed V3 storage is a new versioned namespace `p7-b2-pilot-controller-v2` under a protected service data root. This name/schema is a proposal, not an initialized production namespace.

## Two distinct persistence authorities

The privileged deployment helper exclusively owns a root-protected **successor reservation manifest**. It binds root epoch, predecessor archive hash, explicit retirement/transition approval, exactly one fixed successor UUID, reviewed release/config, migration identity and reservation state. The service may read but cannot create or replace this authority. A fixed root-owned lock serializes control/deployment competitors. Use no-follow descriptors, exclusive creation, fixed approved paths, single-link checks and immutable-parent ownership. Codex/jarvis never writes it.

The dedicated runtime is the sole D09 writer. Its schema4 DB mirrors the pinned reservation identity and stores ancestor accepted IDs/counts, epoch identity/status, grants, permits, attempts, transport ordinals, named provider substeps, D04 joins, terminal/backup facts and input completeness. The helper sends bounded requests to that owner; it does not become a second SQLite writer. One controller transaction spans permit consumption and acceptance. No split auxiliary counter or receipt-derived count is authoritative.

| Record | Required constraint |
| --- | --- |
| Reservation | Unique predecessor/root → one successor; fixed UUID survives partial initialization; archive hash and approval are mandatory |
| Accepted set | Immutable globally unique attempt ID; unique lineage ordinal1–4; lineage/epoch/transport/session/permit association; LIVE, eligible=false |
| Transport | Approved order REST, REST, WS, WS; cap2 each; transport stored durably, not reconstructed from process counters |
| Permit | Unique nonce and ordinal, one runtime/process/challenge binding, one exact request/session/transport commitment; spent flag monotonic |
| Generation substeps | Distinct legacy-router/legacy-response/Granite labels where approved; exact resource, possible-send/terminal/unknown state; no automatic retry |
| Checkpoint | Exact accepted set/high-water, terminal set, source/config/runtime/control ledger, D04/D06 associations; validated before next permit |

## Initialization and crash boundaries

1. Under the privileged exclusive lock, validate terminal zero-use predecessor and sealed archive; create PREPARED reservation with fixed successor ID via exclusive temp creation + file fsync + atomic no-replace publication + parent-directory fsync. No service can accept while PREPARED. If an existing reservation is present, refuse a different UUID rather than try a fresh directory.
2. Initialize only that reserved schema4 namespace under exclusive writer ownership; persist schema/lineage/context and imported accepted truth using SQLite FULL synchronous durable transactions. Fsync directory entries for newly created files. Namespace remains unready until complete validation and checkpoint. Missing/corrupt existing files never mean “start fresh.”
3. Independently validate CLOSED zero-use startup and new checkpoint. Publish root READY authority only for the exact initialized DB/checkpoint hashes after all components are durable. Cross-file steps are a journaled protocol, **not an imaginary atomic transaction across SQLite and filesystem**. A crash between phases leaves a preserved hold. Explicitly authorized continuation may finish the same known zero-use reservation after validation; it cannot mint a replacement successor, silently repair corruption or accept work during reconciliation.
4. On any new process start, runtime admission is CLOSED and all old runtime challenges/permits are unusable. D09 spent/high-water truth remains. An old OPEN audit event is never startup authority. Default first-pilot policy is no interrupted recovery; any future recovery contract must preserve the same V3 epoch and cannot reopen a terminal stop/abort.

## Opening, acceptance and settlement

Operator opening commits an authenticated audit record bound to release/config/PID/start/boot/invocation/epoch/checkpoint and unique challenge before acknowledging HOLD. HOLD has no turn capacity. A separate one-use permit arms one exact ordinal. Repeated opens/refreshed nonces do not reopen the runtime.

Admission validates all bindings under the one owner and reserves the global next ordinal. In one BEGIN IMMEDIATE transaction: recheck global accepted count (including all ancestor IDs) <4, transport quota/order, epoch nonterminal, permit unspent and exact binding; mark permit spent; insert accepted attempt and immutable LIVE/false fact. Commit durably before intake acknowledgment, any legacy/router/Granite provider preparation that could dispatch, D06 lease or task creation. A storage error terminally holds; no queue/backlog or automatic retry. Concurrent REST/WS cannot both consume a permit; unexpected ingress refuses and closes future admissions without erasing already accepted work.

Before commit, SQLite rollback means no accepted row; an ambiguous commit means preserve/inspect, never refund or automatically retry. After commit, a crash before provider work still consumes the attempt. Never fabricate “remote not sent” unless exact local dispatch-order evidence proves it; lost proof is uncertainty. A timeout after possible send retains D06 unknown even if no runner remains. Checkpoint failure, proposal, operator stop or uncertainty permanently closes future grants.

Global count is the cardinality of the union of immutable accepted IDs across the fixed lineage, with collision/ordinal mismatch rejected. Every failed/not-started/unknown accepted attempt consumes budget. Narrow V2 transition requires ancestor count0; synthetic nonzero-ancestor tests separately test defense in depth, **not eligibility for migrating a used predecessor**. There can be no second successor after failure/abort or another root lineage masking an earlier attempt. Root authority replacement requires a new explicit policy decision and cannot be runtime recovery.

Power-loss durability depends on actual filesystem/storage honoring fsync and SQLite journal ordering. Future qualification must inject disk-full/I/O errors, torn journal/publication, power interruption and two-process races in the real implementation. The new offline SQLite model validates logical transaction boundaries only. Local checksums are not privileged-tamper or host-loss protection; the original limited local host-loss acceptance needs explicit renewal for changed storage/identity.
