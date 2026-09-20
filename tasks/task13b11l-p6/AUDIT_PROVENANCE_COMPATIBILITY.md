# Audit and Provenance Compatibility — Task 13B11L-P6

## Audit

**Nothing is emitted.** `task13b11a/AUDIT_PLAN.md` row 14 lists `response obligation` as a
missing audit field owned by this component, and `response.obligation` as a planned event
name. Neither is created here: this phase is passive, and audit schema v3 is unchanged.

What exists is the *shape* such an event would carry. `ObligationState.to_mapping()` returns
a plain JSON-safe mapping — enum values, no datetimes, no nested objects — and
`ObligationDecision` already converts through `types.to_mapping()`. Both are methods that
emit nothing and know no audit writer; a test monkeypatches every public callable in
`app/logs/audit.py` to raise and drives the engine through all eleven ranks without a hit.

An audit record of a decision should carry `obligation_engine_version` (`"1"`, already in
the mapping) alongside the classifier's `"2"`, so a decision can be replayed against both
the rules that classified the request and the rules that chose the obligation. That is what
R2 established the version discipline for.

## Provenance

**Nothing is written, and the ledger is never read.** The engine receives a
`ValueProjection`, a frozen five-field dataclass built from `ProvenanceStatus`,
`TrustClass` and `ProvenanceSource` — availability and trust, never the value, never a
record id, never a fact key. Contract §15.3 forbids a second recogniser in the response
layer, and there is nothing here for one to grow from.

No trust is promoted: `TrustClass` is carried, not recomputed, so a `SUPPLIED` value cannot
become `VERIFIED` by passing through (§16.1, INV-008). No source is mutated. Supersession is
honoured rather than repaired — `answers_now` is false for a `SUPERSEDED` record, so a stale
value never grounds rank 7 (§10.1, INV-019).

`TIMEOUT` is **not** added to `ProvenanceSource`; that remains the deferred item P5 recorded.
A timeout reaches rank 2 with reason `trusted_tool_timeout` and changes no enum.

A test monkeypatches the provenance surface and drives every rank without a hit; the
import-budget test proves `app.execution.provenance` is not imported at all.

## Confirmation and permission

Neither is mutated and neither is recomputed. The engine consumes a settled
`PermissionOutcome` and a settled `confirmation_claimed` projection. It calls no
`permissions.decide()`, owns no confirmation edge, and — see `DECISION_INPUT.md` §3 —
imports neither module, so the P4 confirmation machine keeps the zero importers P5 left it
with.
