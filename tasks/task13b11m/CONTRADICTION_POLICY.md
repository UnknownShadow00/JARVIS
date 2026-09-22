# Response Contradiction Policy

An incompatible operational response state is a caller defect, not prose to soften. The builder
raises `ContradictoryResponseState`; it never selects a replacement obligation.

Stable categories cover upstream P6 contradictions, conversational lane, decision priority or
reason mismatch, obligation/evidence mismatch, result/invocation linkage, missing or ambiguous
provenance, wrong key/session/trust/status/invocation, unsafe value shape, and unexpected
provenance.

The frozen invalid corpus includes:

- success decision with `ERROR`;
- error decision with `SUCCESS`;
- confirmation decision with executed `SUCCESS`;
- target question with executed `SUCCESS`;
- denial with executed `SUCCESS`;
- value answer without supporting provenance;
- conversational lane passed to the operational builder;
- a lower-priority intent decision attempting to override confirmation-required state;
- wrong priority or reason/obligation pairing;
- wrong fact key, superseded-only record, two current records, wrong session/trust pairing;
- result/provenance for invocation A attached to invocation B;
- compound or non-finite values requiring a deferred display/redaction policy.

Every case raises. None falls back to model prose, empty text, or a generic success.
