# Audit compatibility — O-B04 unresolved

No emission or schema change. Legacy schema stays 2; execution schema stays 3. Existing envelope: timestamp, event_type, data, session_id, trace_id. P1 validate/to_audit_entry construct and validate data only; they are not audit writers.

Every candidate ExecutionAuditRecord needs event_id, event_type, occurred_at, correlation, execution_mode; schema_version=3. IDs/time/mode are caller JARVIS facts, not model output or a request to activate that mode. Do not label a real legacy request CONTROL_PLANE merely because a passive fixture exists.

| Planned point / event | Additional required schema-v3 fields |
|---|---|
| S01 turn.request | user_request |
| S02 turn.classified | request_class |
| S03 turn.routed | primary_action, reporting_intent |
| S05 model.proposal | raw_model_tool_proposal |
| S06 guard.decision | proposal_guard_decision (meaning awaits O-B01/O-B02) |
| S07 permission.decision | permission_decision |
| S08/P5 confirmation.created/confirmed/denied/expired/cancelled | confirmation_state and correlation.confirmation_id |
| S09 dispatch.invoked | dispatched_tool, raw_arguments, canonical_arguments and correlation.invocation_id |
| S09 dispatch.result | tool_result and correlation.invocation_id |
| S10 provenance.write | provenance_updates; do not construct an event claiming a write that did not happen |
| S11 response.obligation | response_obligation |
| S12 response.emitted | final_response_source, final_user_visible_response; compatibility projection is not emission |
| S13 turn.summary | request_class, lane, primary_action, response_obligation, final_response_source, safety_outcome |

The seventeen contract fields remain exactly the current CONTRACT_AUDIT_FIELDS set. lane, canonicalization_version, model_draft, redactions and detail remain existing schema fields; this task does not revise their policy. ModelDraftAuditRef supports digest_sha256, blocked, model=None, excerpt=None, excerpt_chars=None. A future digest-only reference avoids copying raw provider internals or reasoning. No excerpt limit or new secret-key list is chosen. Adapter reasoning rejection applies at source; validation by P1's smaller forbidden-name set must not weaken it.

## Concrete incompatibility

AUDIT_PLAN §2 requires one turn.summary per turn. For a valid conversational ObligationState, obligations.derive returns None by design. Current P1 REQUIRED_FIELDS_BY_EVENT requires a non-null response_obligation on TURN_SUMMARY, and validate rejects None. A read-only synthetic check produced exactly:

`turn.summary is missing required fields: ['response_obligation']`

Evidence: api-probe.py / api-probe.json. Zero dispatch and zero audit emissions. Assigning MISSING_CONTEXT to conversation would falsify the P6 outcome; silently omitting a required summary changes the plan; relaxing schema-v3 validation is forbidden in this task. O-B04 requests a scoped architectural resolution. It blocks a complete contract now, not merely future audit transport.

Pre-execution safety-event compatibility failures must stop the execution path; final aggregation must not hide them. Actual enqueue/durability behavior is future live integration, including the impossibility of undoing execution on a later result-audit failure.
