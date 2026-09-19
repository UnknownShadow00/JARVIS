# Source Semantics — Task 13B11L

**Design, not frozen.**

Contract §15.1 and INV-010: every operational response records a non-model source. The
obligation and the source must agree (CT-012). `types.py::OperationalResponseSource` already has
exactly the ten members the validated design used, and `MODEL_RAW` is absent from it *by
construction* — the enum's own docstring: *"on the operational lane there is no enum value that
means 'the model said so'."*

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
validated design froze it. Both mean "JARVIS is acknowledging something the user said or asked
for, and claiming nothing about the world" — an acknowledged fact and an acknowledged intent
differ in what they acknowledge, not in what they assert.

## Attribution (§16)

`ACKNOWLEDGE_FACT` and `REPORT_UNVERIFIED_STATUS` exist so that user-supplied state is never
silently promoted to verified state. The obligation is what carries that distinction into the
response builder: a `TrustedToolResult` grounds `REPORT_TOOL_SUCCESS`, and nothing else does.
The `TrustClass` split (`SUPPLIED` / `VERIFIED` / `CONTROL`) already in `types.py` is what the
provenance projection reports, so the engine never has to infer it.

## Conversational

`ConversationalResponseSource.MODEL_RAW` is the only member of its enum, and it is reachable only
on `Lane.CONVERSATIONAL`. The engine records it there and asserts no operational claim.
