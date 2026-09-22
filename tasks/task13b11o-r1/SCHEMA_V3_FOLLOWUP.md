# Exact future schema-v3 correction

Identifier F-AUDIT-01. Classification: BEFORE LIVE AUDIT WIRING. Not BLOCKING IMPLEMENTATION of the passive recorded core, which can hold optional obligation data without emitting or validating a final ExecutionAuditRecord.

Current defect: REQUIRED_FIELDS_BY_EVENT[TURN_SUMMARY] unconditionally includes response_obligation. validate rejects None although obligations.derive correctly returns None for pure conversation. The old sealed api-probe.json preserves that rejection; it is not edited here.

Minimal future change in app/execution/audit_events.py:

1. Make TURN_SUMMARY's response_obligation required conditional on Lane.OPERATIONAL, instead of an unconditional member of its non-null-required set. Keep request_class, lane, primary_action, final_response_source and safety_outcome required.
2. For Lane.CONVERSATIONAL summaries, require response_obligation is None; reject any supplied ResponseObligation. Do not coerce strings, nulls or missing lane into a valid lane. Existing field type validation still applies.
3. Preserve response.obligation event's non-null requirement and every unrelated event schema. Do not add an operational obligation to earlier events where none has yet been derived.
4. Keep the field annotation ResponseObligation | None and serializer omission for None. No new P0 enum, audit-only fake obligation or serializer fallback is needed; schema_version stays 3 and legacy stays 2.

Future exact tests: conversational summary with None validates and omits field; conversational summary with each of the eleven operational obligations rejects; operational summary with None rejects; operational summary with its valid actual obligation accepts; missing/invalid lane rejects; operational response.obligation with None rejects; all other required fields/type/ID/reasoning checks and legacy serialization stay unchanged.

Do not perform this production change now. It requires its own scoped implementation/evidence and deliberate updates only to tests made obsolete by P7-D04. No blanket relaxation of audit validation. Operational failed-turn audit semantics without an obligation remain F-FALLBACK-01, not permission to mislabel failure as conversation.
