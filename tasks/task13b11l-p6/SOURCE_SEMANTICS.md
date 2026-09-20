# Source Semantics — Task 13B11L-P6

Contract §15.1 and INV-010: every operational response records a non-model source, and the
obligation and the source must agree (CT-012).

`types.py::OperationalResponseSource` already has exactly the ten members the validated
13B10C5 design used, and `MODEL_RAW` is absent from it *by construction* — the enum's own
docstring: *"on the operational lane there is no enum value that means 'the model said so'."*

## The map

`OBLIGATION_SOURCE`, copied verbatim from the validated
`response-obligation-design.json::obligation_to_source`:

| Obligation | Operational source |
|---|---|
| `REQUEST_CONFIRMATION` | `CONFIRMATION` |
| `REPORT_TOOL_ERROR` | `TOOL_ERROR` |
| `REPORT_TOOL_SUCCESS` | `TOOL_SUCCESS` |
| `REQUEST_TARGET` | `AMBIGUITY` |
| `REPORT_MULTI_ACTION_LIMIT` | `MULTI_ACTION_UNSUPPORTED` |
| `REPORT_CAPABILITY_UNAVAILABLE` | `CAPABILITY_UNAVAILABLE` |
| `ANSWER_LEDGER_VALUE` | `LEDGER` |
| `ACKNOWLEDGE_FACT` | `DECLARATIVE_ACK` |
| `REPORT_UNVERIFIED_STATUS` | `UNVERIFIED_STATUS` |
| `ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION` | `DECLARATIVE_ACK` |
| `MISSING_CONTEXT` | `MISSING_CONTEXT` |

Eleven obligations, ten sources: `DECLARATIVE_ACK` legitimately serves two, exactly as the
validated design froze it. Both mean "JARVIS is acknowledging something the user said or
asked for, and claiming nothing about the world" — an acknowledged fact and an acknowledged
intent differ in what they acknowledge, not in what they assert.

`ObligationDecision` has three fields and no source field, so the engine does not *carry* a
source; `source_for(obligation)` exposes the map, and the matrix test checks the pairing on
every valid row.

## Attribution (§16)

`ACKNOWLEDGE_FACT` and `REPORT_UNVERIFIED_STATUS` exist so user-supplied state is never
silently promoted to verified state. A `TrustedToolResult` grounds `REPORT_TOOL_SUCCESS`,
and nothing else does. The `TrustClass` split (`SUPPLIED` / `VERIFIED` / `CONTROL`) is what
`ValueProjection` reports, so the engine never has to infer it and cannot launder it.

## Reason codes

`ObligationDecision.reason` carries a value from the frozen `ObligationReason` vocabulary —
twenty-two machine codes, lowercase, no spaces, deterministic from the input state. No
free-form explanation, no model text, no hidden reasoning. A test asserts the shape of every
member.

The reason is also where the distinctions the eleven obligations do not draw survive:
`permission_denied`, `explicit_action_without_tool`, `capability_unavailable` and
`dispatch_blocked` are four deterministic causes behind one refusal obligation, and
`trusted_tool_timeout` is distinct from `trusted_tool_error` behind one failure obligation.

## Conversational

`ConversationalResponseSource.MODEL_RAW` is the only member of its enum, reachable only on
`Lane.CONVERSATIONAL`, exposed as `CONVERSATIONAL_SOURCE`. The engine records it there and
asserts no operational claim.
