# Durable evidence order

Each committed entry has a positive integer durable_sequence, unique within the retained evidence collection, allocated by the future sink/backend commit boundary. Persist allocation/order so restart cannot reuse an existing committed position. Concurrency mechanics are implementation detail; backend must establish one deterministic committed order. Do not reorder by object ID, wall clock, filesystem scan or arrival inference.

Sequence is solely evidence ordering/storage reference; not an attempt ID, turn/session/correlation ID, tool execution order, permission, timestamp or scheduler decision. No collection UUID or retry ordinal is minted. Future collection/scoping layout remains backend/controller detail and must prevent sequence collision/overwriting retained history.

Contiguous numbering is not promised: interrupted attempts may leave gaps. A gap or no gap alone cannot prove record loss/coverage; do not use max(sequence) as C. Count validated committed entries and reconcile independent submissions. Clock rollback/repetition does not reorder durable entries.

D03 allows repeated producer invocations/attempts for the same turn. Turn or identical record value is not an authoritative unique attempt key. Duplicate-key/idempotent-retry disposition remains D02/D07-dependent. Preserve potential repeated associations as evidence if durably written, expose them to reconciliation, and never automatically count them as independent successful formal samples. Unresolved duplicates block complete measurement; no deduplication/discard/rewrite rule is selected. Durable sequence uniqueness prevents storage-position collision, not semantic attempt duplication.
