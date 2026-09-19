# Audit and Provenance Compatibility — Task 13B11L

Nothing was emitted, written, or changed. Verified unchanged at `a0cc4d3`:
`app/execution/audit_events.py`, `app/execution/provenance.py`, `app/logs/audit.py` — all
byte-identical (`09-production-non-change.txt`).

## Audit — for the implementation

Schema v3 already carries `response_obligation` as one of the seventeen contract fields, and
`ExecutionAuditEvent.RESPONSE_OBLIGATION` ("response.obligation") already exists with
`REQUIRED_FIELDS_BY_EVENT[RESPONSE_OBLIGATION] = {"response_obligation"}`. The record field is
typed `ResponseObligation | None`, so an `ObligationDecision` serialises into the existing
envelope with **no schema change and no new event**. `final_response_source` is typed
`OperationalResponseSource | ConversationalResponseSource | None`, which is exactly the pair
`SOURCE_SEMANTICS.md` uses.

So P6 needs nothing from P1 that does not already exist, and the compatibility test is a shape
check with no writer call — the same pattern 13B11K used.

## Provenance — for the implementation

The engine must not touch the ledger (task §44). It consumes the availability + trust-class
projection described in `DECISION_INPUT.md` §3. `TrustClass` (`SUPPLIED` / `VERIFIED` /
`CONTROL`) already exists in `types.py` and is what keeps `ACKNOWLEDGE_FACT` and
`REPORT_UNVERIFIED_STATUS` distinct from `REPORT_TOOL_SUCCESS` — contract §9.3's requirement that
`USER_FACT`/`USER_REPORTED` and `TOOL_SUCCESS` *"remain distinguishable at all times"*.

`ProvenanceSource` stays at 8 members. No `TIMEOUT` source is added here or anywhere.
