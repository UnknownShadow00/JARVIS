# Contradiction policy

Inherited P6 policy, no new P7 precedence table. Existing obligations.contradiction checks result shape, lane, execution and settled-state consistency in that order. derive/require refuse contradictory states. response.build separately checks decision/evidence linkage and refuses; P7 must not discard the inconvenient field and retry.

| Isolated contradictory input | Existing P6 code |
|---|---|
| DENY + executed SUCCESS | C-01-denied-yet-executed |
| REQUIRE_CONFIRMATION + executed result without claim | C-02-confirmation-required-executed-without-authority |
| Valid conversational class/reasons + trusted result | C-03-conversational-lane-with-trusted-result |
| Ambiguous/unresolved target + executed result | C-04-unresolved-target-yet-executed |
| Multi-action + executed result | C-05-multi-action-yet-executed |
| Non-dispatchable action + executed result | C-06-non-dispatchable-action-yet-executed |
| BLOCKED/CONFIRMATION_REQUIRED + executed=True | C-07-refusal-claims-execution |
| SUCCESS/ERROR/TIMEOUT + executed=False | C-08-execution-status-without-execution |
| Unavailable capability + executed result | C-16-unavailable-capability-yet-executed |
| Claim without REQUIRE_CONFIRMATION | C-21-approval-claimed-without-a-confirmation-requirement |

Compound contradictions retain the first existing component code; the row above does not override earlier result/lane checks. C-09 is deliberately unrepresentable because ObligationState.executed is derived from result, not an independent boolean. The full twenty-member enum remains in the source snapshot; all existing contradiction tests remain enabled.

Response codes R-01 through R-15 cover upstream contradiction, conversational lane, priority/reason/evidence mismatch, result linkage, missing/ambiguous/wrong-key/stale/wrong-trust/wrong-session/wrong-invocation provenance, unsafe value shape and unexpected provenance. Reuse the actual code, not a new P7 classification of the same error.

Stop at the detecting component. No response.build after obligation contradiction, no ApprovedOperationalResponse after builder failure, no re-dispatch after either. Final failure envelope and compatibility with the plan's mandatory safe response remain O-B03. A mismatched fabricated input is not a real execution merely because its executed field says so; equally, a genuine prior result must not be erased to claim no attempt happened.
