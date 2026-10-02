# S08 — BLOCKED

S08 is the one stage this task cannot implement. Its mode-A and mode-C behaviour is
settled; its mode-B behaviour depends on frozen `RecordedTurn` field 15, which is
unimplementable as frozen (BLOCKER_ANALYSIS.md, P-B02).

| Mode | S08 behaviour | Status |
|---|---|---|
| `INITIAL_TURN` | actual `REQUIRE_CONFIRMATION` -> waiting (first ask, `P6-01b` -> `REQUEST_CONFIRMATION`); actual `ALLOW` -> eligible; `DENY` never arrives, S07 routes it to the existing P6 terminal | implementable as frozen |
| `CONFIRMATION_CONTINUATION` | guards B-01…B-07 over the admitted record; pass -> waiting; fail -> `STOP(S08_CONFIRMATION, confirmation_invalid)` | **blocked**: B-02, B-03, B-05 and B-07 require `ConfirmationState`, `TERMINAL_STATES`, `is_fresh_at`, `execution_started` and `NON_CONFIRMABLE_ACTIONS`, all forbidden under `app/` |
| `RESULT_REPLAY` | nothing to validate; pass through to S09 | implementable as frozen |

What S08 must never do, and what the repair must preserve: zero calls to the confirmation
store's `confirm`, `claim_for_dispatch`, `deny`, `cancel`, `expire` or `create_confirmation`;
no record construction or mutation; no TTL chosen; no resting approved state; no
`authorized` / `ready_to_execute` / `confirmation_verified` boolean; and no edge from a
confirmation observation to S09. The required proofs listed in §23 — valid observation
path, mismatch, wrong session, no claim, no dispatcher, no execution, no automatic S09 edge
— all remain required, and all remain unwritten.

The recommended repair keeps every one of those properties and strengthens the last one:
with no import of the confirmation machine, "P7 performs no confirmation mutation" rests on
absence rather than on an allowlist.
