# Task 13B11F — Contract Traceability

| Lane artifact | Contract clause | Invariant | Future consumer |
|---|---|---|---|
| `decide()` returns `Lane` from structured inputs only | **§4.1** ("assigned deterministically … MUST NOT be made by a language model") | **INV-016** | P6 obligations, P7 pipeline |
| OPERATIONAL turns never expose raw model prose — the lane is what marks them | **§4.2** | **INV-001**, **INV-010** | P6 response engine, the raw-prose lock |
| no branch or input downgrades OPERATIONAL to CONVERSATIONAL | **§4.2** ("MUST NOT be re-labelled conversational") | INV-001, INV-010 | P6, P7 |
| the seven always-operational classes | §4.3, yaml `always_operational_classes` | INV-001 | P3 classifier output feeds it |
| `GENERAL_EXPLANATION` default CONVERSATIONAL | §4.3, yaml `always_conversational_classes`; §4.1 CONVERSATIONAL list | — | P6 conversational path |
| the seven escalating conditions | §4.3, yaml `additional_operational_conditions`; §4.1's "includes" list | INV-001, INV-010 | P3 router, P4 confirmation, P5 dispatcher, P2 projection |
| `OTHER` conditional on operational state | §4.3 (frozen C3/C4/C5 lane semantics) | INV-001 | P3 classifier |
| `LaneReason` tuple on every decision | **§14.1** ("derived deterministically from frozen inputs only: … and lane reasons") | — | **P6 obligation engine** |
| `LanePolicyError` instead of a fallback lane | §4.1 determinism; fail-closed | INV-001 | P7 error path |
| no model-authority parameter exists | **§2.3** control-plane ownership; §3.3 | **INV-016**, INV-002 | all |
| no ledger read; provenance arrives as a boolean | §3.2, §9.3 | INV-003 | P2 stays the only ledger owner |
| lane is not in the 17 audit fields | §19.1 | — | deferred operator decision |

## The four traces the task required

* **Operational raw-prose containment** → §4.2's "MUST NOT be raw model prose" and "MUST NOT be
  re-labelled conversational" → **INV-001** (operational raw prose is never final) and **INV-010**
  (every operational response has a non-model-raw source) → the lane is the flag the P6 response
  engine and the raw-prose lock read. This phase's contribution is that the flag can only ever move
  toward OPERATIONAL: 896 of the 1,152 rows are operational by class regardless of signals, and
  0 rows with any operational condition come back conversational.
* **Deterministic lane ownership** → §2.3 (the control plane owns classification, routing, lane and
  response construction) and §4.1 → **INV-016** → consumed by P7, which must call this function
  rather than read a model's opinion. The proof is structural: the entire input surface is one
  closed enum and seven booleans, and no parameter or field names a model, draft, prose,
  confidence, prompt or reasoning concept.
* **`GENERAL_EXPLANATION` conversational allowance** → §4.1's CONVERSATIONAL list ("general
  explanations, definitions, non-operational technical discussion and ordinary conversation") and
  §4.3 → consumed by P6, which may hand model prose to the user on that lane. This phase preserves
  that allowance exactly: with no operational state the class is conversational, which is 1 of the
  only 2 conversational rows in the whole table.
* **`OTHER` operational override** → §4.3's frozen C3/C4/C5 lane semantics → consumed by the P3
  classifier, which may legitimately return `OTHER` for a turn that nevertheless carries a tool
  result or a pending confirmation. `OTHER` behaves identically to `GENERAL_EXPLANATION` on all 128
  condition combinations, which is asserted directly.

## Deferred, with the phase that owns it

| Deferred | Owner |
|---|---|
| calling the lane policy from a live turn | P7 pipeline/adapter |
| supplying `RequestClass` | P3 classifier |
| supplying `tool_proposal`, `action_target`, `external_status_claim_required` | P3 router |
| supplying `confirmation_required` | P4 confirmation |
| supplying `tool_result` | P5 dispatcher |
| projecting `active_operational_provenance` and `operational_correction` from the ledger | P6/P7 |
| turning a lane plus reasons into exactly one obligation | P6 (§14.1) |
| lane as one of the 17 audit fields; the redaction key list; TIMEOUT as a provenance source | operator decisions, untouched |
