# Task 13B11D — Source / Trust Matrix

One production location: `provenance.SOURCE_TRUST`, a `MappingProxyType`. Every helper derives the
trust class from the source; no recorder accepts a caller-supplied `trust_class`, so a user
statement cannot be labelled verified by anyone.

## 1. The table

| Source | Trust | Invocation id | Meaning |
|---|---|---|---|
| `USER_FACT` | `SUPPLIED` | forbidden | the user supplied a value |
| `USER_REPORTED` | `SUPPLIED` | forbidden | the user reported an observation |
| `TOOL_SUCCESS` | `VERIFIED` | **required** | an authorized dispatcher observed it |
| `TOOL_ERROR` | `VERIFIED` | **required** | an authorized dispatcher saw this invocation fail |
| `CONFIRMATION_REQUIRED` | `CONTROL` | forbidden | approval needed; nothing ran |
| `ROUTER_STATE` | `CONTROL` | forbidden | the control plane's own routing conclusion |
| `CAPABILITY_STATE` | `CONTROL` | forbidden | the control plane's own record of what has a tool |
| `CORRECTION_STATE` | `CONTROL` | forbidden | the control plane's own record of supersession |

All eight of the frozen `ProvenanceSource` members are covered; the three `TrustClass` members are
all used. The table is read-only at runtime.

## 2. Rejected pairs

`validate_record` rejects every source/trust pair the table does not contain — 8 × 3 = 24 pairs, of
which 8 are legal and 16 are refused, each named in the error. The two the task calls out
explicitly are covered by that rule: `USER_FACT` with verified trust and `USER_REPORTED` with
verified trust both fail.

## 3. Invocation binding

`TOOL_SUCCESS` and `TOOL_ERROR` require a well-formed invocation id, because a trusted result is
bound to the invocation that produced it (§18.2). Every other source must **not** carry one — a
supplied value cannot borrow tool correlation to look observed.

## 4. Which helper can reach which source

| Helper | Source it may create |
|---|---|
| `record_user_fact` | `USER_FACT` |
| `record_user_reported` | `USER_REPORTED` |
| `record_tool_result` | `TOOL_SUCCESS` or `TOOL_ERROR`, from a real `TrustedToolResult` only |
| `record_confirmation_required` | `CONFIRMATION_REQUIRED`, always `executed: False` |
| `record_control_state` | `ROUTER_STATE`, `CAPABILITY_STATE`, `CORRECTION_STATE` only |

There is no helper that reaches a tool source without a dispatcher result, and no helper whose name
or signature mentions the model. This table does not replace permissions — it says what a fact may
*claim*, not what an action may *do*.

## 5. Tool result status → provenance

| Status | Provenance |
|---|---|
| `SUCCESS` | one `TOOL_SUCCESS` record per key in `facts`, and nothing else (§18.4) |
| `ERROR` | one `TOOL_ERROR` record under `<tool>_error`, scoped to that invocation (§18.3) |
| `CONFIRMATION_REQUIRED` | **none** — execution has not occurred; use the confirmation helper |
| `BLOCKED` | **none** — it was stopped before running |
| `TIMEOUT` | **none** — the outcome is unknown, so neither success nor failure may be recorded |

`GROUNDING_STATUSES` is exactly `{SUCCESS, ERROR}`. The other three raise, naming the status and
why, and leave the ledger empty. Those outcomes remain auditable as `dispatch.result` events from
phase P1; they simply never become facts.
