# Exact existing pipeline projection

Canonical pipeline.py:29-80 defines AdmissionMode, PipelineStage and PipelineStopReason; :129-156 defines PipelineStop; :159 defines the TurnOutcome union. Use those values unchanged. A response return is completion of passive candidate construction, not external execution or delivered text. Do not add envelope_failed, binding_failed, adapter_unavailable, model_absent, completed_success or other invented terminal enums.

_stop(:197-202) receives a private guard assertion label but discards it from the public PipelineStop. V1 therefore contains no guard string. Use existing stop stage/reason and optional upstream full-match boolean. component_reason is excluded: the coarse existing reasons suffice for this minimum record and arbitrary error/guard text must not leak. F-P7R1-03 coarse diagnostics remain deferred.

Lane/action/permission are projected only from available actual return/state/settled owner data. If both stop.state and route/permission supply a fact, they must agree; disagreement rejects. Completion supplies no uniform permission field, so optional settled PermissionDecision is required to observe it. A stop's obligation_state is not an ObligationDecision: candidate_obligation remains None. Never call obligations.derive, response.build, P3 or P4 to fill a gap.

Reject a PipelineStop with executed=True, any result object, or state claiming a result/confirmation. Correlation/response turn must match exactly. Inert V1 uses only INITIAL_TURN with no child invocation/confirmation IDs, as distinct from the existing synthetic result-replay/confirmation-continuation test alternatives. Legacy processing/response is not an input or output of this producer.
