# Correlation propagation

Reuse P1 SessionId, TurnId, InvocationId, ConfirmationId, AuditEventId and ProvenanceRecordId families. No new ID family. Adapter proposal IDs are caller-assigned opaque IDs under its frozen validator, never provider fields. No identifier alone grants authority.

| Stage | Identity requirements |
|---|---|
| S01–S04 | caller session/turn constant; snapshot session matches; Classification.raw_request and router input identify the same caller text |
| S05 | AdapterRequest.turn_id equals turn; requested model preserved; created_at and ordered unique proposal_ids supplied by caller |
| S06/S07 | preserve proposal identity as inert association; policy/canonicalization versions from existing owners, not echo fields |
| S08 | confirmation bound to session, action, capability, tool, target, arguments and versions; audit child adds confirmation_id |
| S09 | invocation_id allocated by caller in passive fixtures; child context preserves session/turn/confirmation; P5 result matches invocation/tool/action |
| S10 | record session/turn/source/invocation identity checked; historical supporting invocation remains distinct from current turn |
| S11/S12 | settled state and decision used together; response turn_id equals caller turn; created_at caller-owned; cited record IDs exact |
| S13 | caller event IDs/times; P1 correlation joins corresponding turn/invocation/confirmation, never re-minted from model text |

ToolInvocation exact P0 fields: invocation_id, turn_id, session_id, action_type, tool_name, raw_arguments, canonical_arguments, canonicalization_version, permission_class, permission_outcome, policy_version, requested_at, confirmation_id=None.

TrustedToolResult exact P0 fields: invocation_id, tool_name, action_type, status, facts, executed, executor, started_at, finished_at, error_kind=None, error_message=None, audit_ref=None. It has no independent result-ID field, session field or permission version; its invocation linkage supplies that context. Do not invent a result ID or pretend a turn-shaped audit_ref replaces invocation binding.

P7 must not call clock/random implicitly for a deterministic recorded replay. P1 factories exist but fixture metadata must be explicit; confirmation and dispatch constructors' optional ID generation cannot be silently used. Provider model/timestamps/IDs are not authoritative and are rejected by the current canonical adapter schema. Failure IDs and serialized TurnOutcome shape remain part of O-B03, not a new family invented here.
