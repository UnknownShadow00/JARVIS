# Parallel inert shadow architecture

One accepted user request must produce one legacy execution path and, when explicitly enabled, one observational shadow attempt. Legacy still owns routing for live behavior, tool calls, model text and response. Shadow receives a copy of validated request facts and JARVIS-owned state, then constructs an immutable projection and a separately sourced untrusted model recording if authorized. Shadow outcome cannot feed legacy routing, response, confirmation or execution.

`REAL REQUEST -> legacy _process/_process_stream -> existing reply` remains unchanged. In parallel, `same request facts -> normalized envelope -> BindingProjectionV1 -> RecordedTurn adapter -> run_recorded_turn -> observation` is a target graph, not implemented code. It must not pass execution objects to the observation path. A model-free deterministic shadow may run only the binder until a non-model P7 admission mode is separately frozen; the current pipeline requires a recorded response.

Shadow failure or timeout is an observation failure and cannot alter the live result. Sampling/queue mechanics, P2 state lifetime, adapter source, measurement storage and the single insertion point remain decisions.
