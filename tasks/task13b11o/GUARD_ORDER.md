# Guard order and reachability

Supported dependency constraints, NOT a complete executable guard contract:

`G01 → G02 → G03 → G04(initial) → G05 → G04(final signals) → G06 → G07 → G08 → G09/G10 → G11 → G12 → G13 → G14(final)`

G14 compatibility for safety-critical pre-execution events must also precede the relevant G09/G10 operation. The full plan's final audit stage aggregates the turn; it does not move safety gates after dispatch.

G07 precedes permission binding: authorization for one route cannot authorize a mismatched proposal. Canonicalization uses the existing versioned API before canonical target/arguments are bound to permission and confirmation. G08 must precede confirmation so DENY cannot be converted to a user-approvable action. P5's seven internal gates remain exactly as frozen in 13B11K AUTHORITY_GATES.md; P7 must not pre-claim confirmation separately and then call dispatch.

Branch exits are in COMPOSITION.md and PIPELINE_MATRIX.md. Early operational stops may reach G12/G13 only with a consistent existing state. No skipped guard counts as passed. An injected successful result cannot backfill a guard that never ran. Conversely, an observed historical result is not evidence of current-turn dispatch.

No implementation reachability proof is claimed: G07 is missing, so the proposed dispatch path is CLOSED. The design obligation is that every route to S09 requires deterministic classification/routing/capability, authoritative proposal binding, permission and required confirmation; no proposal→dispatcher edge exists in an acceptable implementation.
