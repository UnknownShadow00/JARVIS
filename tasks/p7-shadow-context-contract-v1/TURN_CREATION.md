# Turn creation and order

For each accepted logical user turn: (1) resolve/create authoritative session; (2) call existing new_turn_context with that explicit session, minting one turn; (3) capture that session ledger's snapshot; (4) validate and settle context; (5) later compose ShadowIngressEnvelopeV1. Do not call new_turn_context without a session for every request.

A WS user input creates one turn before its stream/fallback fork. Output tokens/chunks and fallback from _process_stream to _process reuse it and mint zero additional turns. Same text is not evidence of the same logical turn. V1 neither creates an idempotency protocol nor promises network retry deduplication: deciding whether a retransmission is a new accepted turn requires the future continuation/admission protocol. Never infer retry identity from text or trace.

Turn IDs establish association, not chronological ordering. P2 locking protects its own mutations; no total ordering or cross-worker session design is asserted. Shadow failure abandons that shadow attempt without a replacement fake ID or impact on legacy.
