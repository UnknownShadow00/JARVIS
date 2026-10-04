# Shadow-local failure

Session resolution, turn creation, snapshot construction/validation and required correlation association failures produce no settled context and no envelope. No fake IDs, no client ID promotion, no empty fallback on error. Legacy processing and its response remain unaffected.

Future transport integration needs a shadow-local exception boundary because current server try/finally blocks reset tokens but do not swallow arbitrary exceptions. Cancellation/disconnect must retain existing legacy semantics; swallowing cancellation globally is not a solution. Observational diagnostic storage and error vocabulary are deferred. This contract does not map context failure into a PipelineStop with fabricated required correlation.
