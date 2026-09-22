# Composition analysis

NOT FROZEN. Sequence comes from 13B11A PRODUCTION_INTEGRATION_PLAN §2, not phase-number inference. P7 only coordinates; the named module retains authority. `F` below means stop and preserve the owner's typed failure; its total pipeline representation is O-B03.

| Stage | Input → output / authority owner | State read / written | Stop and next |
|---|---|---|---|
| S01 Snapshot | caller session-matched LedgerSnapshot → classifier/provenance projections; P2 | explicit snapshot / none in passive scope | invalid projection → F; else S02 |
| S02 Classify | request:str + ClassifierContext → Classification; classifier v2 | known_fact_keys / none | ClassifierError → F, never assume conversation; else S03 |
| S03 Route | same request + Classification + RouterContext → RouteResult; router | caller deterministic capability projection / none | RouterError → F; else S04 |
| S04 Lane | RequestClass + LaneSignals → LaneDecision via lane.explain | route and operational evidence / none | LanePolicyError → F; else S05 |
| S05 Recorded adapter | AdapterRequest → recorded request string; recording + timestamp + IDs → ModelDraft, tuple[ToolProposal,...] | caller fixture / none | AdapterError → F; no partial proposals; else S06 |
| S06 Proposal guard + canonicalization | route + proposals + capability/tool binding + canonicalize result → guard decision | immutable inputs / none | mismatch must stop dispatch; exact representation/owner O-B01/O-B02; pass → S07 |
| S07 Permission | PermissionRequest → PermissionDecision via permissions.decide | frozen policy + caller checks / none | DENY terminates execution branch before S08/S09; valid state → S11/S12. API failure → F. Otherwise S08 |
| S08 Confirmation handoff | decision + exact binding + explicit record/isolated authority | caller projection, or test-owned P4 store / only P4 if separately authorized inert composition | pending/missing → REQUEST_CONFIRMATION before execution; valid dispatch handoff → S09. No P7-created claim |
| S09 Trusted dispatch boundary | build_invocation inputs → ToolInvocation; TrustedDispatcher.dispatch → TrustedToolResult | injected clock/executor/authority, consumed IDs / P5 idempotency and P4 claim/settlement in isolated simulation only | refusal → S11; SUCCESS/ERROR/TIMEOUT → S10/S11; API failure → F |
| S10 Provenance linkage | P5 result + current/historical P2 records → evidence projection | explicit snapshot/records / none for projection-only unit | no fabricated write; TIMEOUT/BLOCKED do not become tool facts; invalid linkage → F; else S11 |
| S11 Obligation | ObligationState → ObligationDecision, or None for valid conversation | settled component state / none | contradiction → F; operational decision → S12 |
| S12 Response | ResponseBuildInput → ApprovedOperationalResponse via response.build | exact grounded evidence / none | builder refusal → F, never model prose; else S13 |
| S13 Audit compatibility | component payloads → valid schema-v3 record/projection | caller IDs/times / no emission | invalid event → F for required safety evidence; completed immutable outcome otherwise |

## Branches and omissions

Conversation without any operational signals/proposals/results: S01–S05, final lane confirmation, then ConversationalResponse through the existing cleaning/safety boundary; no S07–S12 operational authority path. Returning ModelDraft directly as an operational result is forbidden. Exact passive cleaner/failure linkage awaits O-B03; no live conversational implementation is claimed.

Unknown action, deterministic multi-action or unresolved target: preserve S02/S03/S04 facts; never S08/S09. P6 supplies capability-unavailable, multi-action-limit or target obligation respectively when the full state is consistent. Do not overwrite route fields to obtain a desired obligation.

Unavailable capability needs special projection care: P6's class-derived confirmation rule P6-01c can outrank capability when a confirmation-sensitive class has no permission decision. Therefore an early execution stop does not universally mean permission evaluation can be omitted before response derivation. M07 records this unresolved binding/projection case under O-B01; use an actual P4 denial where applicable, never synthesize it or reorder P6 priorities.

Lane timing: §4 of 13B10D and LaneSignals require proposal/result presence to force operational handling even after the initial S04 call. A future composition must re-use lane.explain with accumulated deterministic signals before choosing a conversational return, and again for settled obligation state if new result/confirmation evidence exists. No copied class table, forced conversational downgrade or interpretation of model prose as a lane decision. A pre-adapter lane is provisional, not an exemption from the final policy check.

The full-plan S10 ledger write and S13 audit emission are intentionally absent from the passive projection contract. They must be marked absent, not simulated by P7 constructing trusted records. Isolated P5/P4 simulation is supported by the shadow/inert plan; merely accepting arbitrary callbacks is not proof of isolation. A projection-only subset cannot claim the full successful-dispatch composition has been implemented.

Safety-critical audit compatibility belongs before the corresponding dispatch/confirmation action; S13 is final aggregation, not permission to postpone required safety checks until after execution. Actual emission/failure acknowledgement remains a future live boundary.
