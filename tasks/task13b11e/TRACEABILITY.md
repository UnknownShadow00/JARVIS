# Task 13B11E — Contract Traceability

| Canonicalizer artifact | Contract clause | Invariant | P0/P1 field it satisfies | Future consumer |
|---|---|---|---|---|
| `CanonicalizationResult.raw_arguments` — the input kept verbatim, never overwritten | **§9.1** ("retain the model's raw arguments verbatim for audit") | **INV-006** | `ToolInvocation.raw_arguments`, audit `raw_arguments` | P5 dispatcher, audit writer, P4 confirmation binding |
| `CanonicalizationResult.canonical_arguments` — recorded separately | **§9.1** ("record the canonical arguments separately") | **INV-006** | `ToolInvocation.canonical_arguments`, audit `canonical_arguments` | P5 dispatcher (what actually runs) |
| `CANONICALIZATION_VERSION` | §9.1 ("versioned rules") | INV-006 | `ToolInvocation.canonicalization_version`, audit `canonicalization_version` | P4 confirmation re-derivation (R-07), audit replay |
| `AliasRule` with declared `tool`, `field`, `aliases`, `canonical`, `match` | §9.1 ("deterministic, exact, versioned rules") | INV-006 | — | P3 router, P5 dispatcher |
| unknown values returned untouched | **§9.1** ("leave unknown values unmodified — no fuzzy matching, no trimming, no guessing") | INV-005, INV-011 | — | P3 router, P6 response (an unknown app is reported, not guessed) |
| no similarity library, no regex, no substring or prefix matching | §9.1 | INV-005 | — | all |
| tool + field scoping | §9.1, §5.2 | INV-011 ("unsupported actions cannot be silently mapped to unrelated tools") | — | P3 router, P4 permissions |
| input mapping never mutated; raw and canonical are separate copies | §9.1 | INV-006 | — | P4 confirmation binding, audit |
| determinism, no clock/model/network/filesystem/locale/environment | §9.1 ("apply only deterministic rules") | INV-006 | — | audit replay, P8 conformance |
| `AppliedRule` (informational only, grants nothing) | §9.1 | — | — | reviewers; P6 must not read it as authority |
| `CanonicalizationError` on undescribable input, pass-through otherwise | §9.1; §11/§12 (validation is elsewhere) | — | — | P4 permissions, P5 dispatcher |
| no provenance, audit or registry import | §3.3, §18.1 | INV-002, INV-003 | — | keeps P2/P5 the only sources of trust |

## The four traces the task required

* **Raw argument retention** → §9.1 → **INV-006** → `ToolInvocation.raw_arguments` and the P1 audit
  `raw_arguments` field → consumed by P5 and by the audit writer.
* **Canonical argument** → §9.1 → **INV-006** → `ToolInvocation.canonical_arguments` and the P1
  audit `canonical_arguments` field → consumed by P5 as the arguments that actually run.
* **Versioned deterministic rule** → §9.1 → the canonicalization contract → `canonicalization_version`
  on both the invocation and the audit event → consumed by P4 when re-deriving canonical arguments
  at approval time, which is the mitigation for risk R-07.
* **Unknown value preservation** → §9.1's no-fuzzy-substitution rule → INV-005 and INV-011 → no
  field; it is the absence of a transformation → consumed by the P3 router and the P6 response
  layer, which must report an unrecognized target rather than invent a near one.

## Deferred, with the phase that owns it

| Deferred | Owner |
|---|---|
| wiring canonicalization into a dispatch path | P5 |
| re-deriving canonical arguments at confirmation time (R-07) | P4 |
| any second match policy, or rules for URLs, paths or deploy targets | a future rule version, with operator sign-off |
| whether the initial rule table should be empty instead | operator decision; a data-only change |
| lane as an audit field, the redaction key list, TIMEOUT as a provenance source | operator decisions, untouched by this phase |
