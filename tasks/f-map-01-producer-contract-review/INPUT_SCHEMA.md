# Current P7 input inventory and minimum producer inputs

Implemented `RecordedTurn` has exactly 21 fields (`pipeline.py` and `task13b11p-r6/RECORDED_TURN_V2.md`). Classes: A raw request, B JARVIS derived/caller projection, C adapter/model data, D trusted stored state, E settled continuation. The F-MAP producer directly concerns fields **4, 13, 14** and must be consistent with field 6's advertised tool name. It does not own the whole turn.

| # | RecordedTurn field/type | Class | Future source; admission |
|---|---|---|---|
| 1 | `correlation: CorrelationContext` | B | P1 JARVIS IDs; required |
| 2 | `request: str` | A | original user text; required, untrusted data |
| 3 | `classifier_context: ClassifierContext` | D | P2 current ledger key snapshot; required |
| 4 | `router_context: RouterContext` | B | trusted available-action projection; required, live source **unfrozen** |
| 5 | `snapshot: LedgerSnapshot` | D | P2 session snapshot; required |
| 6 | `adapter_request: AdapterRequest` | B | JARVIS prompt/schema/model/turn ID; required; schema name must agree with expected tool |
| 7 | `recording: str` | C | untrusted adapter/provider response; required |
| 8 | `proposal_ids: tuple[str,...]` | B | P1 assigned IDs; required |
| 9 | `recorded_at: aware datetime` | B | JARVIS recording instant; required |
| 10 | `evaluated_at: aware datetime` | B | JARVIS evaluation instant; required |
| 11 | `lane_signals: LaneSignals` | B | JARVIS facts from route/ledger/continuation; required |
| 12 | `value: ValueProjection` | D | P2 availability/trust; optional NO_VALUE |
| 13 | `expected: CanonicalizationResult | None` | B | P3 over **JARVIS-owned** tool/raw args; conditional with 14; mapping **unfrozen** |
| 14 | `permission_projection: PermissionRequest | None` | B | JARVIS policy query; conditional with 13; policy outcome recomputed at S07 |
| 15 | `confirmation: SettledConfirmationProjection | None` | E | P4 owner observation; mode B only |
| 16 | `invocation: ToolInvocation | None` | E | P5 historical/current attempt; mode C only |
| 17 | `result: TrustedToolResult | None` | E | P5 recorded result; mode C only |
| 18 | `provenance_records: tuple[ProvenanceRecord,...]` | D | P2 selected facts; optional empty |
| 19 | `expected_fact_key: str | None` | B | JARVIS selected ledger key; optional |
| 20 | `supporting_result: TrustedToolResult | None` | E | historical P5 evidence; paired with 21 |
| 21 | `supporting_invocation: ToolInvocation | None` | E | historical P5 linkage; paired with 20 |

Minimum conceptual producer inputs, where a live source is authorized: original request `str` (A, required); same-turn `CorrelationContext` (B/P1, required for association); current `ClassifierContext` and `LedgerSnapshot` (D/P2, required if deriving classification and route); an explicit JARVIS-owned available-action/capability inventory (B, required but **source unapproved**); JARVIS-owned current policy context for `PermissionRequest` (`ApprovalMode`, satisfied constraints and overwrite only when their existing owners prove them); a closed action→capability→tool→target/required-arguments binding specification (**not frozen**). P3 `Classification` and `RouteResult` are derived with existing functions from those inputs, not accepted as client fields. No provider, dispatcher, store handle or confirmation machine is a producer input. Values must be immutable snapshots and must remain identical across the producer and P7 recomputation.

| Producer input | Type | Owner / trust / source | Required | Validation before derivation |
|---|---|---|---|---|
| `request` | exact `str` | user text, untrusted; validated transport | yes | preserve original text; no embedded authority decoding |
| `correlation` | `CorrelationContext` | P1 JARVIS, trusted for association | yes | exact type and well-formed session/turn IDs; same session as snapshot |
| `snapshot` | `LedgerSnapshot` | P2 store observation, trusted for current records | yes for this P7 handoff | exact type/session; immutable record view |
| `classifier_context` | `ClassifierContext` | P2 key projection, trusted for known keys | yes | existing constructor validation; derived from same snapshot |
| `available_capabilities` | **TYPE/SOURCE UNFROZEN** | JARVIS capability owner, not client/model/schema advertisement | yes for live executable projection | must be independently validated, intersected with P4 registered actions; no default-vocabulary grant |
| `approval_mode` | `ApprovalMode` | existing operator safety config/P4, trusted only for tightening | yes for `PermissionRequest` | exact enum; no client override |
| `satisfied_constraints` | `frozenset[Constraint]` | existing deterministic constraint check owners | optional empty | include only independently proved constraints, never model/client assertions |
| `overwrite` | `bool | None` | existing deterministic owner for applicable P4 row | optional when irrelevant | exact type and capability-specific proof; unknown not guessed |
| `binding_specification` | **TYPE/CONTENTS UNFROZEN** | future operator-signed JARVIS map | yes for executable route | closed action/capability/tool/target/argument schema and version; reject missing or ambiguous row |

Derived `Classification` and `RouteResult` are intermediate P3 results, not new caller-controlled inputs. `canonicalize` yields `CanonicalizationResult`; it does not take a model-owned expected map. The two bold unfrozen inputs prevent a complete schema freeze here.
