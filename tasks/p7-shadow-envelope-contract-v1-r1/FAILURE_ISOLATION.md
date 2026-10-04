# Failure isolation contract

A context or composer exception suppresses only the shadow attempt. No exception escapes into the legacy request solely due to capture. Preserve the original _process/_process_stream selection, token cleanup, stream and reply. No raw model fallback, fake success, synthetic context or response replacement.

Existing REST try/finally is token cleanup; WS outer except handles WebSocketDisconnect only. A future narrow shadow-local exception boundary is required at each capture point. Cancellation and disconnect semantics must remain those of the existing server; the contract does not authorize blanket BaseException suppression. Diagnostic emission/storage failure must also remain shadow-local. No audit-v3 event is invented for a pre-context failure that cannot truthfully name a turn.
