# Conversational audit — P7-D04

Pure conversation has Lane.CONVERSATIONAL and no operational ObligationDecision/ResponseObligation. Its internal semantic value is Python None. It is not an enum member named NONE and is not REPORT_TOOL_SUCCESS, REPORT_TOOL_ERROR, REPORT_CAPABILITY_UNAVAILABLE, REQUEST_CONFIRMATION or MISSING_CONTEXT.

Smallest compatible external representation: omit response_obligation in conversational event data, using the existing to_audit_entry convention for fields whose value is None. This contract chooses absence, not a new sentinel or a new JSON serialization scheme. The lane remains explicit on turn.summary, so not-applicable is distinguishable from a malformed operational summary.

Freeze the conditional semantic rule: a conversational TURN_SUMMARY must have response_obligation=None; a non-null operational obligation is invalid there. An operational TURN_SUMMARY still requires its actual ResponseObligation. Missing/unknown lane is invalid, not a route to the exemption. Other required summary fields remain required. Event-specific pre-obligation records retain their existing field requirements: turn.request does not acquire an obligation before selection.

Current P1 already has an optional field but incorrectly requires a non-null value for every summary. Production remains unchanged in this task. Until SCHEMA_V3_FOLLOWUP is implemented, passive pipeline fixtures keep an internal optional-obligation projection; they do not call to_audit_entry with validated=True, mutate REQUIRED_FIELDS_BY_EVENT, manufacture an obligation or claim a valid emitted conversational summary.

If proposals/results introduce an operational signal, use the actual lane policy. Such a turn is not eligible for conversational not-applicable semantics merely because its initial request class was GENERAL_EXPLANATION. A failed operational PipelineStop without a renderable obligation remains a distinct stopped outcome, not a conversational summary.
