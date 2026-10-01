# TURN INPUT SCHEMA — `RecordedTurn`

One immutable P7-local type, declared in the later passive implementation task alongside
`PipelineStop` (F-TYPE-01), in the same frozen/slotted style. It is passive data: no
method with an effect, no callable field, no store, no clock, no identifier minting.

Every field below is required by a stage the frozen guard order already names. No field
is speculative, and no field exists for a future phase. Owner "caller" means the JARVIS
composition caller or the test fixture that stands in for it; owner "P3"/"P4"/"P5" means
the named frozen engine produced the value.

Trust column: **T** = JARVIS-owned control-plane data; **U** = untrusted recorded/model
data. Column `A` = allowed on an initial turn, `B` = on a confirmation continuation,
`C` = on a result replay. `R` = required, `O` = optional-with-declared-default,
`—` = must be absent.

| # | Field | Exact type | Owner | Source of truth | Trust | A | B | C | Consumed by |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `correlation` | `CorrelationContext` | caller / P1 | P1 identifier family | T | R | R | R | S01, every stage's association |
| 2 | `request` | `str` | caller | the original user turn text | U | R | R | R | S02 `classify`, S03 `route` |
| 3 | `classifier_context` | `ClassifierContext` | caller | P2 ledger key projection | T | R | R | R | S02 |
| 4 | `router_context` | `RouterContext` | caller | explicit static capability projection | T | R | R | R | S03, S06 capability |
| 5 | `snapshot` | `LedgerSnapshot` | caller / P2 | one session's current records | T | R | R | R | S01 session identity, S10 |
| 6 | `adapter_request` | `AdapterRequest` | caller | JARVIS prompt/tool-schema inputs | T | R | R | R | S05, S06 tool advertisement |
| 7 | `recording` | `str` | caller | one complete recorded response | U | R | R | R | S05 `parse_recorded_response` |
| 8 | `proposal_ids` | `tuple[str, ...]` | caller | P1 identifiers, positional | T | R | R | R | S05, S06 association |
| 9 | `recorded_at` | `datetime`, tz-aware | caller | when the recording was produced | T | R | R | R | S05 `created_at`, conversational response time |
| 10 | `evaluated_at` | `datetime`, tz-aware | caller | the single evaluation instant | T | R | R | R | S08 freshness, S12 `created_at` |
| 11 | `lane_signals` | `LaneSignals` | caller | deterministic pre-adapter signals | T | R | R | R | S04, final S04 base |
| 12 | `value` | `ValueProjection` | caller / P2 | availability and trust, never the value | T | O `NO_VALUE` | O | O | S11 `ObligationState.value` |
| 13 | `expected` | `CanonicalizationResult \| None` | caller + P3 | authoritative expected binding | T | O | O | O | S06 projection/match, S09 |
| 14 | `permission_projection` | `PermissionRequest \| None` | caller | the proposed policy query | T | O | O | O | S06 projection, S07 `decide` |
| 15 | `confirmation` | `ConfirmationRecord \| None` | P4 | `ConfirmationStore` observation | T | — | R | — | S08 |
| 16 | `invocation` | `ToolInvocation \| None` | P5 | the authorized attempt that ran | T | — | — | R | S09, S12 linkage |
| 17 | `result` | `TrustedToolResult \| None` | P5 | the dispatcher's observed result | T | — | — | R | S09, S11, S12 |
| 18 | `provenance_records` | `tuple[ProvenanceRecord, ...]` | caller / P2 | selected current/historical evidence | T | O `()` | O | O | S10, S12 |
| 19 | `expected_fact_key` | `str \| None` | caller | the key a ledger answer reports | T | O | O | O | S12 ledger renderers |
| 20 | `supporting_result` | `TrustedToolResult \| None` | P5 | a *historical* `TOOL_SUCCESS` result | T | O | O | O | S12 ledger-value attribution |
| 21 | `supporting_invocation` | `ToolInvocation \| None` | P5 | that historical result's invocation | T | O | O | O | S12 |

Twenty-one fields. Fields 15–17 are the mode discriminators; everything else is common.
`—` is enforced, not advisory: a field marked `—` for the derived mode makes the admission
invalid (ADMISSION_FAILURES.md A-03), never silently ignored.

## Fields that deliberately do not exist

No `mode`, `shape` or `kind` field: the mode is derived (ADMISSION_MODES.md), so neither a
caller nor a model can author it. No `confirmed`, `approved`, `authorized`, `executed`,
`success` or `claimed` boolean: each would be an authority assertion the caller is not
entitled to make. No `permission_outcome`, `permission_decision`, `lane`, `classification`,
`route` or `obligation` field: those are outputs of the frozen engines, recomputed every
run from fields 1–4 and 11, never transported. No `candidate` canonicalization result: P7
calls `canonicalize(proposal.tool_name, proposal.raw_arguments)` itself, so the candidate
form can never be caller-authored. No `now`-producing clock, no `executor`, no
`ConfirmationStore`, no `LedgerStore`, no `TrustedDispatcher`, no session object, no
callback and no retry policy. No raw provider envelope, reasoning field or model identity
beyond `adapter_request.model`.

## Immutability and snapshot rules

`RecordedTurn` is frozen and slotted. Every contained value must already be a stable
immutable snapshot under its existing constructor: `ToolProposal`, `ToolInvocation`,
`TrustedToolResult` and `ConfirmationBinding` freeze their own mappings;
`CanonicalizationResult`, `PermissionRequest` and `LedgerSnapshot` expose read-only
mappings and tuples. `proposal_ids` and `provenance_records` are tuples. No mutable alias
may remain that could change a comparison after a gate passed, and holding the type
confers nothing: construction performs no I/O and reaches no engine.

Type identity is checked exactly — `type(x) is T`, not `isinstance` — for fields 15, 16
and 17, so a subclass or a look-alike with the same attribute names is refused rather than
coerced. As V1 already records, type identity alone is not authenticated origin; see
RESULT_REPLAY.md "Authenticity limit".

## Required-together rules (summary; normative text in ASSOCIATION_RULES.md)

- Fields 1–11 are required in every mode. Field 12 defaults to `NO_VALUE` and field 18 to
  `()`; absence is absence, never an empty substitute for unavailable state.
- Fields 13 and 14 are required together once a supported, resolved, single primary action
  reaches S06; neither alone is admissible there, and a missing one stops with
  `projection_missing` rather than being derived (F-MAP-01 stays unfrozen).
- Fields 16 and 17 are required together. One without the other is an invalid shape.
- Fields 20 and 21 are required together when either is present, and describe a historical
  invocation distinct from field 16.
