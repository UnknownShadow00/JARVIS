# Task 13B11C — Execution Audit Schema v3

## 1. Version

`EXECUTION_AUDIT_SCHEMA_VERSION = 3`, defined once in `app/execution/audit_events.py`, per
`AUDIT_PLAN.md` §4. It applies **only** to execution-contract events written by a future phase.

Not done, deliberately: legacy events keep `schema_version: 2`; no existing log line is rewritten,
reclassified or migrated; no existing reader is asked to understand version 3. `app/logs/audit.py`
is byte-identical to its baseline (sha256 `835fb246…`), as is `app/observability/tracing.py`
(`e6defa78…`).

## 2. Envelope

The same envelope the JSONL audit log already writes, so a consumer filtering on `event_type` is
unaffected and only the version number distinguishes the two families:

```json
{"schema_version":3,"timestamp":"…","event_type":"turn.routed","data":{…},
 "session_id":"…","trace_id":"…"}
```

`trace_id` carries the **turn id**, because that is exactly what the existing per-request trace id
already identifies (`AUDIT_PLAN.md` §2).

## 3. `data` block

Fixed key order; fields that do not apply are **omitted**, not written as `null`.

| Key | Always | Meaning |
|---|---|---|
| `event_id` | yes | this event's opaque id |
| `contract`, `contract_version` | yes | `jarvis.agent-execution-contract`, `v1` |
| `execution_mode` | yes | the mode the turn ran under (`legacy` today) |
| `turn_id` | yes | duplicated inside `data` so the block reads on its own |
| `invocation_id` | dispatch events | one tool attempt |
| `confirmation_id` | confirmation events | one confirmation record |
| the 17 contract fields | per event | see `REQUIRED_FIELDS_BY_EVENT` |
| `lane`, `canonicalization_version`, `model_draft`, `redactions` | when set | supporting fields |
| `detail` | when non-empty | event-specific structure, **nested** |

`detail` is nested rather than merged so a payload cannot shadow the event type, the identifiers,
the permission outcome, the trust class or the confirmation state. A test supplies a `detail` that
tries to override all of them and asserts the top-level values win.

## 4. The seventeen required fields (contract §19.1)

`CONTRACT_AUDIT_FIELDS` holds them in contract order. All seventeen are covered by the vocabulary;
`contract_field_coverage()` proves it in a test.

Typing follows what the contract already fixes:

* Fields whose vocabulary exists in P0 `types.py` are typed with those enums — `request_class`,
  `primary_action`, `reporting_intent`, `response_obligation`, and `final_response_source`
  (`OperationalResponseSource | ConversationalResponseSource`, which is how INV-010 becomes a type).
* Fields whose vocabulary is owned by a later phase — `proposal_guard_decision` (P7),
  `permission_decision` (P4), `confirmation_state` (P4), `tool_result` (P5), `provenance_updates`
  (P2), `safety_outcome` (§20 metrics) — are **structured mappings**, never free-form text. Inventing
  enums for them here would be writing P4/P5/P7's policy a phase early.
* `user_request`, `dispatched_tool`, `final_user_visible_response` are strings.

Every contract field is optional on the record and required **per event**, because events occur at
different points in a turn. A field that does not apply stays `None`; nothing is filled with a
placeholder to satisfy typing.

## 5. Raw vs canonical arguments (INV-006)

`raw_arguments` and `canonical_arguments` are separate fields on `dispatch.invoked` and both are
required there, with `canonicalization_version` recording which rule set produced the canonical
form. They are never collapsed. No canonicalizer logic exists in this phase — P3 owns it — so the
sample records construct both forms by hand.

## 6. Model output and redaction

`ModelDraftAuditRef` implements the retention plan in `AUDIT_PLAN.md` §5: a sha256 digest always,
`blocked` always, and an `excerpt` only where a safety review needs one — a blocked draft. A draft
that was simply not selected is recorded as a digest with a `NOT_RETAINED` marker, so a gap in the
log is never read as "nothing happened". `RedactionMarker` + `RedactionReason`
(`SECRET_VALUE | NOT_RETAINED | TRUNCATED | HASH_ONLY`) are passive types only; no redaction engine
is implemented, and choosing which keys are secret is deferred with the rest of P4-P7.

## 7. Validation

`validate(record)` is deterministic and total, and returns the record unchanged when it holds.
It rejects: a wrong schema version; a non-enum event type or execution mode; a malformed
`event_id`; a naive timestamp; a missing per-event required field; a dispatch event without an
invocation id; a confirmation event without a confirmation id; a look-alike string where a contract
enum belongs; a non-mapping where structure belongs; non-string mapping keys; and any
chain-of-thought field name at any depth. Nothing is coerced, defaulted or dropped silently — an
event that cannot be described correctly must not be written at all.

## 8. Serialization

`to_audit_entry(record)` validates (unless told the record is already validated) and returns a
JSON-safe mapping. Enums become their values, datetimes ISO-8601, read-only mappings plain dicts,
tuples lists. Key order is fixed, so the same record always produces the same JSON text; a test
asserts `json.dumps` equality across calls and round-trips every sample through `json.loads`.
**The serializer writes nothing anywhere** — no file, no queue, no writer.
