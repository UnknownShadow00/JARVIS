# B1-R1 accounting acceptance requirements

This is a task acceptance matrix, not an implementation or test-pass claim.
Canonical current controller/D09 sources must be inspected before selecting
exact types, schema version, caller transitions or test expectations.

Prefer a frozen explicit `measurement_eligible: bool` accepted alongside origin,
with a fail-closed false default for any policy uncertainty. Acceptance must
receive explicit values. Use the existing closed purpose representation if
available; add a narrow enum only if one boolean loses the required distinction.
Do not add an open metadata dictionary. D04 remains a sink without classification
or measurement authority.

| Frozen preimplementation case | Required outcome |
|---|---|
| LIVE + false qualification | Accepted and included in all-attempt accounting |
| LIVE + true measurement | Representable in offline tests; never used by this B1 harness |
| SYNTHETIC + true | Rejected |
| REPLAY + true | Rejected |
| Qualification mutation after completion/window start | Rejected; stored eligibility remains false |
| Provider tries to set eligibility | Cannot control acceptance policy or stored eligibility |
| Sink receipt tries to set eligibility | Cannot control acceptance policy or stored eligibility |
| Controller/persistence failure | No silent promotion; fail closed |
| Measurement summary containing qualification | Qualification excluded from measurement denominator |
| All-attempt summary containing qualification | Qualification explicitly present and accounted |
| Reopen/recovery | Original origin/eligibility restored without inference or promotion |
| Older evidence database | Preserved; explicit version rejection or safe non-destructive handling |

Before editing any existing tests, enumerate the complete accounting/controller/
collector/origin test tree and consolidate exact structural transitions in one
table. Only mechanically required field/type changes are authorized; retain
origin, security, authority and execution assertions. Freeze first-fail outputs
before implementing the extension.

Qualification uses a new private database. A schema change must be explicitly
versioned; no old sealed evidence may be migrated destructively. Accepted facts
must not derive eligibility from response, sink success, endpoint, model, prompt,
trace or a later time window. Classification grants no execution authority.

Before any real generation: focused new tests, full relevant D09/controller tests,
persistence/recovery and origin/eligibility attack tests must pass. Create the
focused production commit and record parent, files, tests and rollback. No push.
