# Source Compatibility

The builder consumes P6's frozen source mapping unchanged.

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

For ledger values the supported provenance sources are `USER_FACT`, `USER_REPORTED`,
`TOOL_SUCCESS`, `CORRECTION_STATE`, `ROUTER_STATE`, and `CAPABILITY_STATE`. A tool value also
requires its exact historical `ToolInvocation` and executed `SUCCESS` result. `TOOL_ERROR` and
`CONFIRMATION_REQUIRED` records are not rendered as value answers.

User acknowledgements and unverified status responses may carry zero or one current
`USER_FACT`/`USER_REPORTED` record. No caller can supply an operational response source; the
builder derives it from the obligation, preventing source promotion by construction.
