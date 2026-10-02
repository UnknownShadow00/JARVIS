# ASSOCIATION RULES

All control-plane identifiers remain JARVIS-owned and come from the existing P1 family
(`SessionId`, `TurnId`, `InvocationId`, `ConfirmationId`, `ProvenanceRecordId`). This
contract introduces no new identifier family, no derived identifier, no prefix scheme and
no mint call. A model or provider may not replace any of these values: none of them has a
path from recorded content into an authority input.

`CorrelationContext` is the turn association and nothing more. It proves two facts belong
to one turn; it never states that anything was permitted, confirmed, trusted or executed.

## Required-together and absence rules

| Group | Rule | Violation |
|---|---|---|
| common | fields 1–11 of TURN_INPUT_SCHEMA.md present and of exact type | S01 `invalid_input` |
| defaults | `value` absent means `NO_VALUE`; `provenance_records` absent means `()`. Absence is absence: an empty snapshot is never a substitute for unavailable state, and an empty projection never stands in for a missing one | — |
| expected binding | `expected` and `permission_projection` are required **together** once a supported, resolved, single primary action reaches S06; one without the other is inadmissible there | S06 `projection_missing` |
| mode discriminators | exactly one of the three admissible rows of the ADMISSION_MODES.md truth table | S01 `invalid_input` |
| replay pair | `invocation` and `result` present together | S01 `invalid_input` |
| historical pair | `supporting_invocation` and `supporting_result` present together, and distinct from `invocation` | S09 `result_invalid` |
| ledger answer | `expected_fact_key` is meaningful only where the selected obligation is a ledger answer; `response.build` already owns that requirement and is not duplicated | S12 `response_failed` |

## Turn association (S01)

1. `correlation.session_id` and `correlation.turn_id` are well-formed P1 identifiers.
2. `adapter_request.turn_id == correlation.turn_id`.
3. `snapshot.session_id == correlation.session_id`.
4. `proposal_ids` entries are well-formed, unique case-insensitively, and ordered as the
   adapter requires.
5. `recorded_at` and `evaluated_at` are timezone-aware datetimes. No ordering between
   them is imposed: none is frozen anywhere upstream, and inventing one would be policy.
6. mode C only: `invocation.turn_id == correlation.turn_id` and
   `invocation.session_id == correlation.session_id` (C-00b).

An **invalid or malformed correlation is caller API misuse**, not a semantic failure: it
is rejected through the existing P1 validation boundary by raising, exactly as
PIPELINE_FAILURE_MODEL.md requires. A correlation id is never invented in order to
manufacture a `PipelineStop`. Once a turn is admitted with a valid correlation, every
further failure returns structured stopped state.

## Proposal association (S06, unchanged)

`proposal.turn_id == adapter_request.turn_id == correlation.turn_id`;
`proposal.proposal_id == proposal_ids[0]`; `proposal.proposed_by_model ==
adapter_request.model`. Exact string equality after the existing identifier validity
checks. This is task13b11o-r1/PROPOSAL_GUARD.md step 1 verbatim and is not restated as a
new rule.

## Confirmation association (S08)

The full field-by-field table is in CONFIRMATION_CONTINUATION.md B-06, over the existing
twelve `BINDING_FIELD_NAMES`. Summary of what must match exactly: session, correlation
(via `audit_ref` and any `correlation.confirmation_id`), action type, capability, tool
name, permission class, policy version, canonicalization version, target, raw arguments
and canonical arguments. No additional binding is invented; `user_id` is carried through
and not constrained by P7.

A fresh unrelated request can never consume a prior pending action's approval: B-06
compares the stored binding against *this* turn's routed action, capability, target and
canonical arguments. A record bound to a different action, target or argument set fails
regardless of how the request is phrased, and possession of the record or of its id
confers nothing.

## Invocation and result association (S09)

C-01…C-08 of RESULT_REPLAY.md. The two identity rules that make result smuggling
impossible:

- `result.invocation_id == invocation.invocation_id` — a result from invocation A never
  satisfies invocation B;
- `invocation.turn_id == correlation.turn_id` and `invocation.session_id ==
  correlation.session_id` — a result cannot cross a turn or a session.

A fresh request that arrives carrying an old result is, by derivation, not a fresh initial
turn at all: it is mode C, and C-00b/C-04 refuse it unless the invocation genuinely belongs
to this turn and matches the route the request actually produces.

## Audit-facing associations (no emission)

Which admission facts would eventually be available to the audit layer, recorded for the
later wiring task and emitted by nothing now: `correlation.to_mapping()`;
`classifier_version`, `router_version`, `LANE_POLICY_VERSION`,
`CANONICALIZATION_VERSION`, `PERMISSION_POLICY_VERSION`,
`CONFIRMATION_STATE_MACHINE_VERSION`, `DISPATCHER_VERSION`; the derived admission mode;
the `LaneDecision`; the `ObligationDecision` or `None`; for mode B the
`ConfirmationRecord` via the existing `to_audit_payload`; for mode C
`invocation.invocation_id`, `result.status`, `result.executed` and `result.audit_ref`; and
for a stop, its stage, reason and `component_reason`. Nothing is validated, serialized with
`validated=True`, or written. Audit schema v3 is not modified and the conversational
`turn.summary` obligation defect (F-AUDIT-01) remains deferred ahead of any live audit
wiring.
