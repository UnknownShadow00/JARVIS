# Provenance compatibility

P2 remains the owner of source→trust mapping, validation and supersession. P5 remains the only trusted-result constructor. A class instance is not cryptographic provenance: passive fixture ownership and identity linkage must be explicit, not a generic from-dict conversion of model output.

ProvenanceRecord fields remain record_id, turn_id, session_id, fact_key, value, source, trust_class, created_at, status=CURRENT, invocation_id=None, superseded_by=None. No raw model payload/reasoning or new trust field is added.

Before consuming a caller snapshot, validate its session and every record. Use current records for value projections; do not guess a winner from conflicting values. P6's ValueProjection carries availability/status/source/trust/ambiguity, not raw values. ResponseBuildInput carries the exact selected records and expected_fact_key. A historical TOOL_SUCCESS record additionally needs its supporting_result and supporting_invocation; current-turn result remains state.result and invocation. These are not interchangeable.

SUCCESS: only explicit P5 facts can support verified values. Empty facts do not imply a health/status/value. ERROR: P2's existing record_tool_result produces an invocation-scoped tool_error fact, not global service health. TIMEOUT/BLOCKED/CONFIRMATION_REQUIRED are not accepted by record_tool_result as tool facts; a confirmation-required control projection uses its distinct existing path. No TIMEOUT ProvenanceSource is invented.

User facts remain SUPPLIED, user reports remain attributed, corrections use P2's current/superseded semantics. ModelDraft and ToolProposal never enter a provenance constructor. P7 must not perform another natural-language extraction to find a convenient response value.

No ledger writes in this task or passive projection proposal. Synthetic prior records may be inspected; evidence distinguishes test origin from real-world verification. Existing P2/P5 linkage and P6 response tests are the future oracle, not copied harness code.
