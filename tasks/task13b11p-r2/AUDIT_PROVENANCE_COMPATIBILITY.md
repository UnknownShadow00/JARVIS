# AUDIT AND PROVENANCE COMPATIBILITY

No audit event was emitted, no audit schema was modified, and no provenance record was
written or superseded. Audit schema v3 is byte-identical.

## Provenance

The pipeline consumes `LedgerSnapshot` and selected `ProvenanceRecord` values read-only.
It writes nothing, supersedes nothing, and promotes nothing: a `SUPPLIED` value never
becomes `VERIFIED` by passing through, and a model claim never becomes a record. S10 is
selection and linkage validation only. `provenance_non_activation_test.py` already excludes
`app/execution/`, so the pipeline needs no change there.

## Audit

The S13 projection stays `(lane, obligation | None)` plus caller correlation, held in
fixtures. It is never a validated or emitted `ExecutionAuditRecord`; the implementation must
not call the audit entry serializer with `validated=True` and must not mutate the required-
field map. A conversational turn's obligation is Python `None`, never a sentinel enum
member.

**F-AUDIT-01 remains open and BEFORE LIVE AUDIT WIRING.** The current schema-v3 validator
requires a non-null `response_obligation` on every turn summary, which is wrong for a
conversational turn; the correct external representation is to omit the field under the
existing None-omission convention. Nothing in this task touched it, and the passive
pipeline must not depend on serializing a conversational summary under today's validator.

Admission facts that would eventually be available to audit, recorded and emitted by
nothing: correlation identifiers; the classifier, router, lane, canonicalization, permission,
confirmation-state-machine and dispatcher version strings; the derived admission mode; the
lane decision; the obligation decision or `None`; for a result replay the invocation id,
result status, `executed` flag and audit reference; and for a stop its stage, reason and
`component_reason`.
