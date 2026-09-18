# Task 13B11C — Contract Traceability

Every production artifact of phase P1, the contract clause it serves, the invariant it supports,
the 13B11A phase that planned it, and the phase that will consume it.

## 1. Artifacts

| Production artifact | Contract clause | Invariant | 13B11A source | Future consumer |
|---|---|---|---|---|
| `ExecutionAuditEvent` (17 names) | §19.1 | — (§19.1 is the audit obligation itself) | `AUDIT_PLAN.md` §3 | every phase P2-P8; the writer arrives with the first emitting phase |
| `EXECUTION_AUDIT_SCHEMA_VERSION = 3` | §19.1 | — | `AUDIT_PLAN.md` §4 | the audit writer; existing readers stay on 2 |
| `CONTRACT_AUDIT_FIELDS` (the 17 fields) | §19.1 | INV-006, INV-010 | `AUDIT_PLAN.md` §1 | P2-P7, each filling the fields it owns |
| `REQUIRED_FIELDS_BY_EVENT` | §19.1 | — | `AUDIT_PLAN.md` §1 (field → planned source) | the writer and the conformance tests at P8 |
| `raw_arguments` / `canonical_arguments` kept distinct | §9.1, §18.2 | **INV-006** | `TOOL_INVOCATION_CONTRACT.md` §1 | P3 canonicalizer, P5 dispatcher |
| `canonicalization_version` | §9.1 | INV-006 | `TOOL_INVOCATION_CONTRACT.md` §1 | P3 canonicalizer |
| `final_response_source: OperationalResponseSource \| ConversationalResponseSource` | §15, §16 | **INV-010**, INV-001 | `PRODUCTION_INTEGRATION_PLAN.md` §16 | P6 response builder |
| `response_obligation` | §14 | INV-009 | `AUDIT_PLAN.md` §1 field 14 | P6 obligation engine |
| `provenance_updates` | §9.3, §10 | INV-002, INV-008, INV-019 | `PROVENANCE_PLAN.md` §1-2 | P2 ledger |
| `confirmation_state` on five distinct events | §12 | INV-004, INV-014 | `CONFIRMATION_STATE_PLAN.md` §3 | P4 confirmation manager |
| `permission_decision` | §11 | INV-013 | `PERMISSION_MATRIX_PLAN.md` | P4 permission engine |
| `proposal_guard_decision` | §2.1, §13.2 | INV-011, INV-015 | `AUDIT_PLAN.md` §1 field 8 | P7 guard |
| `tool_result` | §18 | INV-003 | `TOOL_INVOCATION_CONTRACT.md` §2 | P5 dispatcher |
| `safety_outcome` | §19.1, §20.1 | — (the metric record) | `AUDIT_PLAN.md` §1 field 17 | P8-P11 measurement |
| `FORBIDDEN_REASONING_FIELDS` + `_reject_reasoning_fields` | **§19.2** | — | `AUDIT_PLAN.md` §5 | every emitting phase |
| `ModelDraftAuditRef`, `RedactionMarker`, `RedactionReason` | §19.2, §21 | INV-020 | `AUDIT_PLAN.md` §5 | P7 adapter, P6 response lock |
| `SessionId` / `TurnId` / `InvocationId` / `ConfirmationId` / `AuditEventId` | §18.2, §19.1 | INV-004, INV-006 | `AUDIT_PLAN.md` §2 | P2 ledger, P4 confirmation, P5 dispatcher |
| `CorrelationContext` (frozen, ids only) | §19.1 | INV-004, INV-013 | `AUDIT_PLAN.md` §2 | every phase from P2 |
| `utc_now()` + tz-aware validation | §19.1 | — | `TOOL_INVOCATION_CONTRACT.md` §1 (`requested_at` UTC) | all later records |
| `to_audit_entry()` | §19.1 | — | `AUDIT_PLAN.md` §4 (same envelope) | the audit writer |

## 2. The six traces the task asked for, explicitly

* **Audit event vocabulary** → contract §19.1 → the audit obligation → `AUDIT_PLAN.md` §3 → consumed
  by every phase P2-P8 that records a transition.
* **Correlation ids** → contract §19.1 (chain reconstruction) and §18.2 (`invocation_id` as the
  idempotency and audit key) → INV-004, INV-006 → `AUDIT_PLAN.md` §2 → P2 provenance records,
  P4 confirmation binding, P5 dispatch.
* **Schema version 3** → contract §19.1 → no invariant, a compatibility decision →
  `AUDIT_PLAN.md` §4 → the writer; legacy readers are unaffected because legacy stays at 2.
* **Required fields** → contract §19.1 (the seventeen) → INV-006 and INV-010 are the two that are
  field-shaped → `AUDIT_PLAN.md` §1 → filled progressively P2-P7.
* **Raw/canonical argument fields** → contract §9.1, §18.2 → **INV-006** ("Raw and canonical tool
  arguments are both auditable") → `TOOL_INVOCATION_CONTRACT.md` §1 → P3 canonicalizer and P5
  dispatcher; both are required on `dispatch.invoked`, so an emitter cannot record one without the
  other.
* **No-chain-of-thought rule** → contract **§19.2** and `agent-execution-contract.yaml`
  `audit_events.forbidden` (`model_chain_of_thought`, `private_hidden_reasoning`) → enforced two
  ways: no such field exists in the schema, and any such key inside a payload is rejected at any
  depth after name normalization.

## 3. Deferred, with the phase that owns it

| Deferred | Owner |
|---|---|
| the audit writer, queue policy and fail-closed rule for safety-critical events (`AUDIT_PLAN.md` §6) | the first emitting phase |
| provenance record ids and the ledger | P2 |
| enum vocabularies for guard, permission, confirmation state, tool status as *top-level* audit types | P4, P5, P7 |
| redaction engine and the secret-key list (`AUDIT_PLAN.md` §5) | P4-P7 |
| a reader/deserializer for schema v3 | the phase that first needs to replay events |
