# Task 13B11D — Ledger API

Three classes in `app/execution/provenance.py`, plus module-level helpers. Nothing is instantiated
at import time: there is no module-level ledger or store, so importing the module creates no shared
state.

## 1. `ProvenanceLedger(session_id)`

One conversation session's trusted operational state.

### Recording

| Method | Creates | Notes |
|---|---|---|
| `record_user_fact(turn_id, fact_key, value)` | `USER_FACT` / `SUPPLIED` | never becomes verified, however often it is repeated |
| `record_user_reported(turn_id, fact_key, value)` | `USER_REPORTED` / `SUPPLIED` | stays attributed for life; no promotion path exists |
| `record_tool_result(turn_id, result)` | `TOOL_SUCCESS` or `TOOL_ERROR` / `VERIFIED` | requires a real `TrustedToolResult`; returns a tuple of records |
| `record_confirmation_required(turn_id, fact_key, detail=None)` | `CONFIRMATION_REQUIRED` / `CONTROL` | the stored value always carries `executed: False`, and a caller cannot override it |
| `record_control_state(turn_id, fact_key, value, source)` | `ROUTER_STATE`, `CAPABILITY_STATE` or `CORRECTION_STATE` / `CONTROL` | refuses any other source |

No recorder takes a `trust_class` parameter. All accept an optional `created_at` for deterministic
tests; the default is `correlation.utc_now()`.

`record_tool_result` returns `()` for a `SUCCESS` with empty `facts` — "it ran and returned nothing
to report" — and raises for `CONFIRMATION_REQUIRED`, `BLOCKED` and `TIMEOUT`.

### Lookup

| Method | Returns |
|---|---|
| `current_records(fact_key)` | every current record for the key, newest first |
| `current(fact_key, *, trust_class=None)` | the single current record, or that trust class's; raises `AmbiguousProvenance` if several stand and none was named |
| `history(fact_key)` | every record ever written for the key, newest first |
| `all_records()` | the whole session, oldest first |
| `snapshot()` | a `LedgerSnapshot` of the current records |
| `len(ledger)` | number of records held |
| `.session_id` | the session this ledger belongs to |

## 2. `LedgerSnapshot`

Immutable view: `.session_id`, `.records`, `len()`, `.keys()`, `.records_for(fact_key)` and
`.to_mapping()` (JSON-safe). Taken at a moment in time and unaffected by later writes — this is what
the classifier, obligation engine and response builder will be handed in later phases.

## 3. `LedgerStore`

Holds one ledger per session so facts from different conversations cannot mix:
`for_session(session_id)` (creates on first use), `get(session_id)`, `sessions()`,
`drop(session_id)` and `clear()`.

`drop` and `clear` exist for tests and for future lifecycle management. **They are not wired to
anything**: `LIGHT_SLEEP`, `DEEP_SLEEP` and every other lifecycle event are untouched by this phase,
and no production code constructs a store.

## 4. Module-level helpers

| Name | Purpose |
|---|---|
| `SOURCE_TRUST` | the frozen source → trust table |
| `TOOL_SOURCES` | the two sources that require an invocation id |
| `GROUNDING_STATUSES` | the two tool statuses that ground provenance |
| `validate_fact_key(key)` | key rules |
| `freeze_value(value)` | passive-data rules; rejects model artifacts |
| `validate_record(record)` | the full record check, returns the record unchanged |
| `to_audit_payload(record)` | the JSON-safe mapping a future `provenance.write` event will carry |
| `ProvenanceError`, `AmbiguousProvenance` | the only exceptions raised |

## 5. Concurrency

The ledger and the store each hold a `threading.Lock` for their own mutations, so a stray concurrent
write cannot corrupt the supersession chain. That is the floor, not a design for concurrent turns:
deciding that two turns of one session may not interleave belongs to the integration phase, and is
recorded here as that phase's responsibility.

## 6. Scope and lifetime

In memory, per session — the scope the integration plan selected, and the shape the C3/C4/C5 runs
actually measured. No database, no file, no JSONL mirror, no migration. Provenance does not survive
a process exit in v1, so a later response layer must read an empty ledger as "not available in this
context" rather than "nothing is true". Persistence is a separate, later decision.
