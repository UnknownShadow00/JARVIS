# Frozen updated pipeline matrix

Pre-implementation expectations for P7 PIPELINE CONTRACT V1. No pipeline scoring run is claimed. `STOP(reason)` means PipelineStop; unless explicitly marked post-attempt, executed=False, result=None, no ApprovedOperationalResponse and no operational model fallback. All rows permit zero real effects. Stage names and exact guard order are in UPDATED_GUARD_ORDER.md.

`MATCH` requires the complete caller/static projection, actual P3 output and exactly one matching proposal. `P6` means actual derive/require → response.build on valid existing evidence, never a hand-selected obligation. Result rows are recorded P5/P6 projection fixtures, not assertions that a fabricated ALLOW or result can bypass earlier stages.

| ID | Input / condition | Last gate or branch | Exact expected disposition |
|---|---|---|---|
| N01 | GENERAL_EXPLANATION, NONE, zero proposals, no operational signals | final lane / conversation | conversational content remains untrusted; no permission/result/operational obligation |
| N02 | OTHER, NONE, zero proposals, no operational signals | final lane / conversation | same as N01 |
| N03 | supported resolved action, zero proposals | S06_CARDINALITY | STOP(proposal_required) |
| N04 | supported action, one exact proposal, apps.open policy query | MATCH → actual P4 → waiting branch | REQUIRE_CONFIRMATION preserved; no execution; P6 REQUEST_CONFIRMATION |
| N05 | supported action, one wrong tool | S06_MATCH tool | STOP(proposal_tool_mismatch) |
| N06 | supported action, one wrong target encoded in args | S06_MATCH arguments | STOP(proposal_arguments_mismatch) |
| N07 | supported action, one wrong canonical arg or extra arg | S06_MATCH arguments | STOP(proposal_arguments_mismatch) |
| N08 | supported action, two identical proposals | S06_CARDINALITY | STOP(multiple_proposals), never deduplicate |
| N09 | supported action, one exact plus one wrong proposal | S06_CARDINALITY | STOP(multiple_proposals), never pick matching member |
| N10 | supported action, multiple differing proposals | S06_CARDINALITY | STOP(multiple_proposals), no planning/execution loop |
| N11 | proposal names arbitrary unavailable tool while caller expected a different available tool | S06_MATCH tool | STOP(proposal_tool_mismatch); model name cannot alter caller capability |
| N12 | expected capability absent in caller projection/registration | S06_PROJECTION capability, if not already terminal route | STOP(capability_unavailable); zero dispatch |
| N13 | no authoritative expected binding supplied | S06_PROJECTION | STOP(projection_missing), no invented mapping |
| N14 | wrong proposal ID/turn/model association | S06_MATCH association | STOP(proposal_association_mismatch) |
| N15 | mismatched canonicalization version or inconsistent caller target/action | S06_PROJECTION / P3 linkage | STOP(projection_invalid) |
| N16 | fake permission field on proposal/root structured object | S05_ADAPTER | STOP(adapter_invalid), component_reason=invalid_response |
| N17 | fake confirmation field on proposal/root object | S05_ADAPTER | STOP(adapter_invalid), component_reason=invalid_response |
| N18 | fake success/executed/result structured field | S05_ADAPTER | STOP(adapter_invalid), component_reason=invalid_response |
| N19 | hostile permission/confirmation claim only inside extra raw argument | S06_MATCH arguments | inert data; extra key mismatch gives STOP(proposal_arguments_mismatch); never an authority value |
| N20 | “tool succeeded” in draft, zero operational proposals | S06_CARDINALITY | STOP(proposal_required); draft never substitutes a result |
| N21 | exact proposal + hostile prose | MATCH → actual permission | same permission/confirmation behavior as benign draft; no truth from prose |
| N22 | pre-dispatch classifier exception, admitted correlation | S02_CLASSIFY | STOP(classification_failed), no invented Classification or obligation |
| N23 | pre-dispatch route/permission API failure | S03_ROUTE / S07_PERMISSION | STOP(routing_failed) / STOP(permission_failed), not fake DENY or tool ERROR |
| N24 | conversation-class request with operational proposal and deterministic NONE | final lane → non-action guard | lane OPERATIONAL via existing policy; STOP(unexpected_proposal); no model-selected action |
| N25 | conversational internal audit projection | S13_AUDIT | obligation None; eventual schema data omits response_obligation; no emission now |
| N26 | conversational audit projection with any operational obligation | S13_AUDIT | STOP(audit_invalid); no invented applicability |
| N27 | operational normal summary without its required actual obligation | S13_AUDIT | STOP(audit_invalid); no conversational exemption |
| N28 | deterministic UNKNOWN_ACTION, including unsupported verb sweep | early route terminal → P6 | REPORT_CAPABILITY_UNAVAILABLE / explicit_action_without_tool; no raw operational prose |
| N29 | ambiguous/unresolved target | early route terminal → P6 | REQUEST_TARGET; no invented target or dispatch |
| N30 | actual distinct multi-action request | early route terminal → P6 | REPORT_MULTI_ACTION_LIMIT; reject all proposals for execution |
| N31 | valid P4 DENY settled-state/P6 fixture | permission terminal → P6 | REPORT_CAPABILITY_UNAVAILABLE / permission_denied when winning; no confirmation/dispatch |
| N32 | valid pending/missing confirmation fixture | confirmation terminal → P6 | REQUEST_CONFIRMATION; no execution |
| N33 | wrong/stale/replayed/cross-session confirmation fixture | P4/P5 refusal projection → P6 | no executor; existing CONFIRMATION_REQUIRED + exact refusal code, no renewal |
| N34 | matching P5 SUCCESS with ALLOW or valid required claim | result/provenance → P6 | REPORT_TOOL_SUCCESS only from existing linked result; no invented fact |
| N35 | matching P5 ERROR | result/provenance → P6 | REPORT_TOOL_ERROR / trusted_tool_error; invocation-scoped evidence |
| N36 | matching P5 TIMEOUT, required claim if applicable | result → P6 | REPORT_TOOL_ERROR / trusted_tool_timeout; outcome unknown, no timeout provenance, EXECUTING lifecycle unchanged |
| N37 | P5 BLOCKED/idempotency refusal fixture | result → P6 | REPORT_CAPABILITY_UNAVAILABLE / dispatch_blocked when winning; no new execution |
| N38 | contradictory P6 execution/permission/lane/target/capability state | S11_OBLIGATION | STOP(obligation_failed), original P6 contradiction code; preserve valid existing result |
| N39 | wrong current/historical provenance/result linkage or builder failure | S10_PROVENANCE / S12_RESPONSE | STOP(provenance_invalid) / STOP(response_failed); no retry/raw fallback |
| N40 | current supplied/reported/corrected value query | non-action → P6 | ANSWER_LEDGER_VALUE with exact attribution, no trust promotion |
| N41 | declarative fact | non-action → P6 | ACKNOWLEDGE_FACT; never independently verified |
| N42 | external-status request without trusted result | non-action → P6 | REPORT_UNVERIFIED_STATUS |
| N43 | missing-context request without higher grounded source | non-action → P6 | MISSING_CONTEXT only under existing priority |
| N44 | request for read capability lacking a current P3 action | deterministic containment, not a fabricated route | no full supported-read E2E claim; P4-only read coverage remains separate; no vocabulary extension |
| N45 | canonical alias accepted by actual apps.app P3 rule, complete map otherwise exact | MATCH | guard pass; original raw retained, expected canonical args used; no permission granted |
| N46 | boolean/number or integer/float substitution, unknown-key omission, reordered array | S06_MATCH arguments | STOP(proposal_arguments_mismatch); no implicit equivalence |
| N47 | proposal matches expected tool but caller did not advertise that name | S06_MATCH tool | STOP(proposal_tool_mismatch); expected binding and advertisement must agree, neither grants execution |

## Preservation of old matrix coverage

13B11O M01–M02 → N01–N02; M03/M12/M16 → N04/N32/N34; M04 → N44; M05 → N34; M06 → N31; M07 → N12/N13/N28 with the actual RouterContext/P4 projection rule; M08–M10 → N28–N30; M11 → N03; M13–M15 → N05–N10; M17–M20 → N33/N37; M21–M22 → N35–N36; M23–M24 → N16–N21; M25–M29 → N38 with existing codes; M30 → N39; M31–M34 → N40–N43; M35–M36 → N22–N23/N39. No old security category was removed or turned into an alternative expected value.

P6 state fixtures are not claims that all such states are reachable through today's two mapped action/capability pairs. In particular, do not mock P4 to make a whole-turn apps.open ALLOW/DENY case reachable. Whole-turn cases must use the actual frozen policy; component replay coverage is labeled separately. New contradiction fixtures are in contradiction-corpus.json, with zero new dispatcher calls.
