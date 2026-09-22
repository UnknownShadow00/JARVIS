# Failure semantics

NOT FROZEN as a total pipeline contract. Existing component failures are evidence about a boundary, not permission outcomes or proof of a tool's world state. No automatic retry is authorized for any pipeline failure. A new operator/caller attempt, if later authorized, must re-enter all applicable gates with proper idempotency; TIMEOUT never implies safe retry.

| Failure/class | Owner / existing representation | Execution fact | Obligation/response path and stop | Audit compatibility |
|---|---|---|---|---|
| Invalid adapter input/recording | adapter AdapterError with fixed code | no P7 dispatch | stop S05; no partial output; total reply O-B03 | failure metadata only, no decoder document/reasoning |
| Classification failure | classifier ClassifierError | no dispatch | stop S02; plan says operational missing-context, but no valid Classification/state; O-B03 | cannot invent request_class for summary |
| Route failure | router RouterError | no dispatch | stop S03; plan clarification needs a valid P6 state/target; O-B03 | retain stage failure, no invented route |
| Ambiguity | deterministic Classification/RouteResult | no dispatch | S11/S12 REQUEST_TARGET when P6-04 wins; no S08/S09 | actual classification/route/decision |
| Unsupported capability | deterministic route + explicit availability | no dispatch | REPORT_CAPABILITY_UNAVAILABLE; P6-06a or 06c as applicable | not an inferred model capability claim |
| Proposal mismatch/zero/many | guard not yet frozen | no dispatch permitted | stop S06; exact typed failure/reason/obligation O-B01/O-B02 | guard schema data not frozen |
| Permission denial | P4 PermissionDecision DENY | no dispatch | stop execution at S07; P6-06b permission_denied when winning, then builder | permission.decision payload |
| Permission API failure | PermissionPolicyError | no dispatch | not a PermissionDecision; stop S07, O-B03 | never log a made-up normal DENY result |
| Confirmation required | P4 decision or P5 CONFIRMATION_REQUIRED | no executor | REQUEST_CONFIRMATION P6-01a/01b; S12; no valid claim means no execution | actual requirement vs actual state distinguished |
| Missing confirmation | P5 confirmation_absent / binding_absent / authority_unavailable | no executor | CONFIRMATION_REQUIRED; no bypass | current result error_kind |
| Mismatch / invalid confirmation | P4/P5 confirmation_binding_mismatch / confirmation_invalid_request | no executor | CONFIRMATION_REQUIRED; stop dispatch | retain machine code, not prose matching |
| Stale / wrong session / replayed claim | confirmation_expired / confirmation_not_found / confirmation_not_pending | no new executor | CONFIRMATION_REQUIRED; never silently renew or mint authority | no cross-session existence oracle |
| Dispatch blocked | P5 BLOCKED, e.g. invocation_already_dispatched | no new executor | REPORT_CAPABILITY_UNAVAILABLE if P6-06d wins; preserve higher priorities | dispatch.result with executed=False |
| Dispatch API failure | DispatchError | stage-dependent; do not assert no execution after an uncertain boundary failure | stop; O-B03; no automatic retry | bounded stage/error identity, no fabricated result |
| Tool error | P5 ERROR, executed=True means executor reached | attempt occurred, no success claim | REPORT_TOOL_ERROR / trusted_tool_error, S11→S12 | invocation-bound result only |
| Tool timeout | P5 TIMEOUT, executed=True means executor reached | outcome unknown | REPORT_TOOL_ERROR / trusted_tool_timeout, S11→S12 | no TOOL_SUCCESS/TOOL_ERROR provenance conversion |
| Provenance invalid/unavailable | P2 ProvenanceError / P6 linkage check | earlier attempt may exist | stop S10 or S12, never clear result/ledger to fake a benign state | no successful provenance.write claim |
| Obligation contradiction | P6 ContradictoryObligationState(code) | preserve supplied evidence; contradiction is not proof nothing happened | stop S11; no decision or approved reply | source code retained; fallback O-B03 |
| Response contradiction | ContradictoryResponseState(code) / ResponseInputError | preserve prior execution status | stop S12; no approved reply, model fallback or alternate P7 renderer | no response.emitted event |
| Audit incompatibility | ExecutionAuditError | pre-dispatch: none; post-dispatch: preserve result | no further execution; total outcome O-B03/O-B04 | no emitted malformed record |
| Internal pipeline invariant | no existing pipeline exception/type | unknown unless validated earlier state proves otherwise | stop; NOT a tool ERROR, missing context, approval or success by default | safe typed wrapper remains O-B03 |

The plan's “every failure ends in no side effect” cannot retrospectively undo an already-attempted execution before a response/audit failure. The safe interpretation is no *additional* execution; preserving P5 TIMEOUT uncertainty and consumed invocation IDs is mandatory. No new user-facing sentence is specified here.

D-P6-01/D-P6-02 are unchanged. Priorities are not duplicated in P7: a state with UNKNOWN_ACTION and DENY uses the existing winning rule, not an ad-hoc universal permission_denied override. The exact P6 decision and reason must be reused.
