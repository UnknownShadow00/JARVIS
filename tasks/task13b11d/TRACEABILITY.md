# Task 13B11D — Contract Traceability

| Production artifact | Contract clause | Invariant | P2 requirement | Future consumer |
|---|---|---|---|---|
| `ProvenanceSource` reused from P0, one helper per source | §3.2, §9.3 | INV-008 | source distinction | P3 classifier, P6 obligation/response |
| `SOURCE_TRUST` table, trust derived never supplied | §3.2, §9.3, §16.1 | INV-008 | trust distinction | P6 response builder (attribution wording) |
| `TrustClass` kept separate from source | §9.3, §16 | INV-008 | trust distinction | P6 |
| keyed, trust-scoped supersession; `SUPERSEDED` retained with `superseded_by` | §10.1 | **INV-007**, **INV-019** | correction / supersession | P3 classifier, P6 response |
| a user correction never supersedes a `TOOL_SUCCESS` record | §10.2 | INV-007, INV-019 | correction / supersession | P6 |
| `current()` raises rather than choosing between SUPPLIED and VERIFIED | §16.1 | INV-008 | current-value lookup | P6 decides the preference, with attribution |
| no value-only accessor | §16.1, §16.2 | INV-008 | current-value lookup | P6 |
| `record_tool_result` requires a real `TrustedToolResult` | §18.1 | **INV-003** | tool result provenance | P5 dispatcher |
| `invocation_id` required for tool sources, forbidden elsewhere | §18.2 | INV-003, INV-006 | tool result provenance | P5, audit correlation |
| `SUCCESS` records only the returned `facts`; empty facts record nothing | §18.4 | INV-003 | tool result provenance | P6 (minimal-result wording) |
| `TOOL_ERROR` scoped to `<tool>_error` for one invocation | §18.3 | INV-003 | tool error provenance | P6 |
| `TIMEOUT`, `BLOCKED`, `CONFIRMATION_REQUIRED` ground nothing | §18.3, §18.4 | INV-003, INV-015 | timeout semantics | P5 dispatcher, P6 response |
| `record_confirmation_required` forces `executed: False` | §12, §3.2 | INV-004, INV-015 | confirmation-required groundwork | P4 confirmation manager |
| `record_user_reported` with no promotion path | §16.1 | **INV-008** | user-reported attribution | P6 (CT-007) |
| `record_user_fact` remains `SUPPLIED` | §16.1, §16.2 | INV-008 | supplied stays unverified | P6 (CT-006) |
| `ModelDraft` / `ToolProposal` rejected as values; no model-named helper | §3.3, §21 | **INV-002**, INV-020 | model non-authority | every later phase |
| `history()`, `all_records()`, nothing deleted or edited | §10.1, §19.1 | **INV-019** | historical auditability | audit replay, P6 |
| `to_audit_payload()` matching the P1 `provenance_updates` field | §19.1 | INV-006 | audit compatibility | the audit writer |
| `ProvenanceRecordId` in the P1 identifier family | §18.2, §19.1 | — | one identifier scheme | P4, P5, audit |
| `LedgerStore` per-session isolation | §9.3 (session scope) | INV-008 | session identity | P7 pipeline |
| frozen records, tuple returns, read-only mapping values | §10.1 | INV-019 | immutability | all |

## Deferred, with the phase that owns it

| Deferred | Owner |
|---|---|
| the audit writer and any live `provenance.write` emission | the first emitting phase |
| persistence, the JSONL mirror, survival across a process exit | a later, separate decision |
| per-turn serialization / session locking beyond the ledger's own lock | the integration phase (P7) |
| lifecycle wiring of `drop`/`clear` to LIGHT_SLEEP / DEEP_SLEEP | the integration phase |
| whether a timeout deserves its own provenance source | operator decision; would extend the frozen P0 enum |
| the redaction secret-key list | operator decision, still open |
| whether `lane` becomes one of the 17 audit fields | operator decision, still open; the P1 schema was not touched |
