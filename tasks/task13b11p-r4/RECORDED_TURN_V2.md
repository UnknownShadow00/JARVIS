> **DRAFT — NOT FROZEN. P-B05 prevents final contract and fixture freeze. P-B04 authorization is separately resolved.**

# RecordedTurn V2 — complete schema

Frozen/slotted P7-local data type; entry `run_recorded_turn(turn: RecordedTurn) -> TurnOutcome`. V1 required/optional/absent columns, defaults, immutable snapshot rules and field ownership remain binding except field 15.

| # | Field | V1 definition | V2 definition | Changed? | Reason |
|---|---|---|---|---|---|
| 1 | `correlation` | `CorrelationContext` | `CorrelationContext` | No | Preserved byte-for-byte type and meaning. |
| 2 | `request` | `str` | `str` | No | Preserved byte-for-byte type and meaning. |
| 3 | `classifier_context` | `ClassifierContext` | `ClassifierContext` | No | Preserved byte-for-byte type and meaning. |
| 4 | `router_context` | `RouterContext` | `RouterContext` | No | Preserved byte-for-byte type and meaning. |
| 5 | `snapshot` | `LedgerSnapshot` | `LedgerSnapshot` | No | Preserved byte-for-byte type and meaning. |
| 6 | `adapter_request` | `AdapterRequest` | `AdapterRequest` | No | Preserved byte-for-byte type and meaning. |
| 7 | `recording` | `str` | `str` | No | Preserved byte-for-byte type and meaning. |
| 8 | `proposal_ids` | `tuple[str, ...]` | `tuple[str, ...]` | No | Preserved byte-for-byte type and meaning. |
| 9 | `recorded_at` | `datetime`, tz-aware | `datetime`, tz-aware | No | Preserved byte-for-byte type and meaning. |
| 10 | `evaluated_at` | `datetime`, tz-aware | `datetime`, tz-aware | No | Preserved byte-for-byte type and meaning. |
| 11 | `lane_signals` | `LaneSignals` | `LaneSignals` | No | Preserved byte-for-byte type and meaning. |
| 12 | `value` | `ValueProjection` | `ValueProjection` | No | Preserved byte-for-byte type and meaning. |
| 13 | `expected` | `CanonicalizationResult \| None` | `CanonicalizationResult \| None` | No | Preserved byte-for-byte type and meaning. |
| 14 | `permission_projection` | `PermissionRequest \| None` | `PermissionRequest \| None` | No | Preserved byte-for-byte type and meaning. |
| 15 | `confirmation` | `ConfirmationRecord \| None` | `SettledConfirmationProjection \| None` | Yes | Replace lifecycle record with immutable owner observation; name remains confirmation. |
| 16 | `invocation` | `ToolInvocation \| None` | `ToolInvocation \| None` | No | Preserved byte-for-byte type and meaning. |
| 17 | `result` | `TrustedToolResult \| None` | `TrustedToolResult \| None` | No | Preserved byte-for-byte type and meaning. |
| 18 | `provenance_records` | `tuple[ProvenanceRecord, ...]` | `tuple[ProvenanceRecord, ...]` | No | Preserved byte-for-byte type and meaning. |
| 19 | `expected_fact_key` | `str \| None` | `str \| None` | No | Preserved byte-for-byte type and meaning. |
| 20 | `supporting_result` | `TrustedToolResult \| None` | `TrustedToolResult \| None` | No | Preserved byte-for-byte type and meaning. |
| 21 | `supporting_invocation` | `ToolInvocation \| None` | `ToolInvocation \| None` | No | Preserved byte-for-byte type and meaning. |

Fields 1–11 are required in every mode. `value` defaults to NO_VALUE and `provenance_records` to (). Remaining optional fields default to None. Fields 13/14 must be present together at the supported-action S06 gate; neither is derived. Fields 20/21 form a historical pair; S09 enforces association and distinction from current invocation. V1 owner/trust/consuming-stage table is incorporated verbatim for the twenty unchanged fields.

Exactly three derived modes, using presence of fields confirmation/invocation/result:

| confirmation | invocation | result | Mode |
|---|---|---|---|
| absent | absent | absent | A INITIAL_TURN |
| present | absent | absent | B CONFIRMATION_CONTINUATION |
| absent | present | present | C RESULT_REPLAY |
| all other five combinations | | | S01 invalid_input |

No fourth mode or caller-set mode. Exact type checks remain on all three discriminators: SettledConfirmationProjection, ToolInvocation, TrustedToolResult respectively. No duck typing, generic promotion or subclass acceptance. Mode B and C are mutually exclusive.

No dispatcher, executor capability, registry, store, clock, session object, callable or authority shortcut boolean. The existing TrustedToolResult.executor is a descriptive string, not an executable dependency. Existing lane flags and value projections remain frozen facts, not new authority inputs. P7 constructs no confirmation projection, invocation or result. Invalid correlation is still P1 caller misuse; admitted semantic failures are closed PipelineStop values.
