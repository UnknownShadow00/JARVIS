# Pipeline data only

Exact imports from pipeline: AdmissionMode, PipelineStage, PipelineStopReason, PipelineStop, TurnOutcome. No pipeline function is imported or called and no authoritative input/state is constructed. Stops must match P1 correlation and be executed=False/result=None; available state cannot claim result/confirmation. Response turn must match. No obligations.derive or response.build call. Model source on a stopped terminal is not a candidate and is rejected.
