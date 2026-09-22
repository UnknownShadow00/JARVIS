# Trust Boundary

The frozen invariant is clear even though the parser contract is incomplete:

- Hermes/provider input is untrusted data.
- Adapter output may only be the existing passive `ModelDraft` and `ToolProposal` types.
- A proposal is not a `ToolInvocation` and grants no execution authority.
- Adapter content cannot create a `TrustedToolResult`, permission decision, confirmation,
  provenance trust, obligation decision or approved operational response.
- The adapter must not call P3–P6 engines, registry, dispatcher, audit writer or a live provider in
  this passive unit.

No boundary code was written because its exact input/validation contract is not frozen.
