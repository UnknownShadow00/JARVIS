# Exact future REST capture point

`app/server.py::chat`: after successful ensure_awake_for_interaction and current_token.reset, inside the existing try immediately before `reply, intent_result = await _process(req.message)` at line 370. The start_trace context at line 359 is active. Deep-sleep early returns at lines 360-368 do not create a shadow envelope.

At that point the future transport boundary obtains the authoritative owner-settled context (session → turn → snapshot) and passes req.message unchanged to the pure composer. Read the server trace in the active context, before settling; do not pass the Request or ChatRequest object. Capture failure is contained locally, then the original _process invocation and response construction proceed unchanged. Context/envelope capture is not permission to run an evaluator there.

The existing finally resets current_token (:379-380), but is not a general shadow exception handler. Required new isolation is specified in FAILURE_ISOLATION.md. Actual continuation extraction and validation remain a separate pre-wiring decision.
