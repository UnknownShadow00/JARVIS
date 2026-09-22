# Model Non-Authority

Contract v1 and P0 already establish that model output owns only conversational reasoning,
candidate structured proposals and conversational-lane prose. It does not own execution truth,
permission, confirmation, dispatch, provenance, audit truth, obligations or final operational
responses.

Production remains unchanged. No helper exists in P7 to promote provider content into
`ToolInvocation`, `TrustedToolResult`, `PermissionOutcome`, `ConfirmationState`,
`ProvenanceRecord`, `ObligationDecision` or `ApprovedOperationalResponse`.

Hostile strings, fake success, fake permission and fake confirmation remain inert data because no
adapter implementation was introduced.
