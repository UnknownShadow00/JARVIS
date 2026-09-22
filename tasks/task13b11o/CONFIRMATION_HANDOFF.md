# Confirmation handoff

Existing states only: PENDING, EXECUTING, SUCCEEDED, FAILED, DENIED, EXPIRED, CANCELLED. There is no resting CONFIRMED state. The audit event name confirmation.confirmed does not add one.

ConfirmationBinding exact fields: confirmation_id, session_id, action_type, capability, tool_name, permission_class, policy_version, canonicalization_version, target=None, user_id=None, raw_arguments={}, canonical_arguments={}. Both mappings are deeply frozen by P4. These are the twelve fields claim_for_dispatch compares.

ConfirmationRecord exact fields: binding, state, created_at, expires_at, audit_ref; resolved_at=None, provenance_ref=None, invocation_id=None, state_machine_version. Use the current module's version constant, not a new pipeline version claim.

Creation uses create_confirmation with an actual REQUIRE_CONFIRMATION decision's settled class/version and exact bound action. For passive deterministic creation, supply confirmation_id, created_at and expires_at explicitly; no TTL number or random ID choice. DENY must never be made approvable. Creating PENDING executes and schedules nothing.

Observation: a caller-held record projects state, not approval. Successful claim: TrustedDispatcher invokes the explicit ConfirmationAuthority.claim_for_dispatch with session_id, exact binding_fields, invocation_id and injected now. P4 atomically validates existence/ownership/PENDING/freshness/binding and assigns the invocation. P7 must not call confirm(), replace the state, accept model “yes,” or infer confirmation_claimed from mere record presence.

Settlement: P5 calls settle_success or settle_failure for the matching invocation. Successful and failed terminal records are not reusable; denial/expiry/cancellation are not consent. P5 timeout still leaves EXECUTING. Preserve it; no timeout recovery or automatic retry here.

Future fixtures may use a dedicated P4 in-memory store with fixed caller times and inert P5 executor; all state changes belong to those components and are discarded after the fixture. Static projection tests receive records plus linked invocation/result evidence, never a live store. Numeric TTL, real approval UX and live persistence remain deferred. O-B01 is required before a pipeline may assemble the authoritative binding.
