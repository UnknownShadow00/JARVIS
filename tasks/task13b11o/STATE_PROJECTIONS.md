# State projections and exact existing fields

NOT FROZEN as a whole pipeline input. Existing API defaults below are observations, not permission for P7 to infer missing authority. Candidate linkage uses explicit caller-held projections and actual component outputs, not dictionaries of authority booleans.

| Existing type | Exact fields | Owner/source, mutability, omission |
|---|---|---|
| CorrelationContext | session_id, turn_id, invocation_id=None, confirmation_id=None | P1 caller-owned frozen; optional child IDs only when relevant; never provider metadata |
| AdapterRequest | model, turn_id, messages:tuple[AdapterMessage,...], tool_schemas:tuple[ToolSchema,...] | JARVIS caller-owned frozen; all required, empty tuples permitted by adapter; no live capability grant |
| Adapter parse metadata | raw:str, created_at:aware datetime, proposal_ids:tuple[str,...] | raw untrusted; others caller-owned; all required; IDs match proposal count |
| LedgerSnapshot | session_id, records:tuple[ProvenanceRecord,...] | P2 read-only public view, not a frozen dataclass or deep security seal; all required; empty is explicit, not store failure |
| ClassifierContext | known_fact_keys:frozenset[str]=frozenset() | P3 frozen; derived from validated relevant snapshot keys; empty only when truly known empty |
| Classification | request_class, reason, rule_id, raw_request, classifier_version="2" | only classifier result; immutable; no model override |
| RouterContext | supported_actions:frozenset[PrimaryAction]=SUPPORTED_ACTIONS | frozen abstract vocabulary; default is NOT D-08 live availability; passive caller supplies explicit context |
| RouteResult | primary_action, reporting_intent, target, raw_target, target_resolved, multi_action, detected_actions, capability_available, reason, selected_clause, reporting_clause, clauses, clause_analysis, router_version="1" | only router result; frozen; its nullable fields keep router meaning, no inferred tool name |
| LaneSignals | tool_proposal, tool_result, confirmation_required, active_operational_provenance, operational_correction, action_target, external_status_claim_required (each bool=False) | exact bools, frozen; assembled from component evidence, not model assertions; omitted evidence cannot mean false |
| LaneDecision | lane, request_class, reasons, policy_version="1" | lane.explain output; no manually chosen lane/reasons |
| PermissionRequest | capability, primary_action=None, target=None, canonical_target=None, raw_arguments={}, canonical_arguments={}, target_resolved=True, approval_mode=BALANCED, satisfied_constraints=frozenset(), overwrite=None | P4 frozen input; capability/binding awaits O-B01; policy state JARVIS-owned; no defaulting of target/constraints from model |
| PermissionDecision | outcome, reason, permission_class=None, matched_row=None, constraints=(), unsatisfied_constraints=(), base_outcome=None, approval_mode=BALANCED, policy_version="1", notes=(), denial_kind=None | actual permissions.decide output; not model-deserializable authority |
| ConfirmationBinding / Record | exact fields in CONFIRMATION_HANDOFF.md | P4 owner, frozen; a snapshot is NOT permission to claim execution |
| ToolInvocation / TrustedToolResult | exact P0 fields preserved in source snapshot and CORRELATION.md | P5 construction/binding; no adapter or P7 factory for trusted results |
| ValueProjection | available=False, status=None, trust_class=None, source=None, ambiguous=False | P6 frozen; derived only from validated P2 evidence; no raw value, no freshness inference from model |
| ObligationState | lane, request_class, lane_reasons, primary_action; reporting_intent=NONE, target_resolved=None, multi_action=False, capability_available=True, permission_outcome=None, confirmation_claimed=False, result=None, value=NO_VALUE | P6 frozen; every authority field from actual owner; defaults cannot hide missing required stages |
| ResponseBuildInput | session_id, turn_id, created_at, decision, state; provenance_records=(), expected_fact_key=None, supporting_result=None, invocation=None, supporting_invocation=None | P6 frozen; exact current vs historical evidence; no raw request/model prose input |

Proposed linkage: original request goes unchanged to classifier and router. Current session projection supplies known_fact_keys; selected fact key/value/source must be supplied as explicit P2-related evidence and validated by P6, never re-extracted by the response builder. Snapshot.keys() alone does not validate records or establish CURRENT status. No store outage becomes an empty snapshot. Correction semantics remain P2 supersession; P7 does not choose the latest timestamp as an alternate truth rule.

CanonicalizationResult supplies raw_arguments, canonical_arguments, version and applied_rules; neither a schema description nor successful canonicalization establishes safe arguments. Route-to-capability/tool/target linkage remains O-B01. Permission outcome/class/version pass unchanged to P4/P5. Confirmation_claimed cannot be inferred from a model bool, mere record presence or EXECUTING state unrelated to the invocation; use the P5/P4 handoff evidence.

Successful output types already exist: ApprovedOperationalResponse(text, turn_id, obligation, source, provenance_record_ids, created_at, lane=OPERATIONAL) and ConversationalResponse(text, turn_id, model, created_at, source=MODEL_RAW, lane=CONVERSATIONAL). They are mutually exclusive branches, not optional competing replies. A proposed immutable TurnOutcome would carry exactly one successful branch OR a separately typed failure with no approved reply. The latter is NOT authorized as a replacement for the plan's mandatory operational fallback: O-B03. No new P0 type is added here.
