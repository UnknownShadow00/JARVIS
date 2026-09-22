# Operational Response Builder Contract

The builder is the P6 operational-response lock required by Agent Execution Contract v1 §§3,
4, 14–18.

## Inputs

Only existing typed control-plane objects are accepted. `ModelDraft`, `ToolProposal`, raw model
text, raw request text, model confidence, rationale, status, error explanations, and confirmation
claims are absent from the public API. A mapping or look-alike object is rejected.

The caller supplies time; the builder reads no clock. The caller supplies exact records and
invocations; the builder reads no ledger or store.

## Output

The only output type is the existing frozen P0 `ApprovedOperationalResponse`:

```text
text, turn_id, obligation, source, provenance_record_ids, created_at, lane
```

The lane is always `OPERATIONAL`. Source comes from P6's frozen `source_for()` mapping. No
`MODEL_RAW` member exists in `OperationalResponseSource`.

## Fail closed

Malformed input raises `ResponseInputError`. Incompatible structured truth raises
`ContradictoryResponseState` with a stable `ResponseContradiction` code. There is no empty output,
generic success, model fallback, conversational downgrade, sanitizer, or response-cleaner pass.

## Authority boundaries

The builder does not select another obligation, execute or dispatch, decide permission, create or
mutate confirmation, read/write provenance, emit audit, canonicalize, classify, route, parse the
request, or call a model.
