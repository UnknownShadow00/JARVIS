# Observed retry architecture and unresolved selection

Canonical adapter has no provider operation, retries, clock, random/ID minting, cache or scheduling. Each parse_recorded_response invocation validates exactly one complete recording and returns all ordered proposals; that is not a one-response-per-turn/provider-attempt guarantee. run_recorded_turn invokes the parser at most once when it reaches S05 and does not request a provider response.

Existing separate legacy LLMClient (app/brain/llm_client.py:27,286–326) has _RETRY_DELAYS=(1,2,4), connection-recovery request/stream loops and speak_error on the first connection failure. It emits operational LLM audit events elsewhere and deep_reasoning may switch a configured model. ResourceManager also has recovery/load ownership. None is frozen as the future shadow provider path. Do not inherit its retries, audio, model substitution or audit side effects silently.

One JARVIS accepted turn may later have several attempted provider operations if retry/stream/cancellation policy permits it. D02/D07 must decide the authoritative attempt identity/selection and duplicate accounting; D06 inventories transport/SDK retries and complete-response boundaries. No earliest/latest/first-success choice, best-of selection, retry ordinal or silent cache reuse. An exact one-recording parser input does not resolve which response belongs in it.

Until that policy is frozen, multi-response selection cannot support a complete formal measurement. Preserve all associated failure/unknown/retry evidence under future accounting and keep legacy unchanged; no runtime scheduling or retry implementation here.
