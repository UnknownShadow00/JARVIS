# Exact turn ordering

1. Constructor establishes the JARVIS-minted session and instance-owned store.
2. An explicit `create_turn` validates required owner/trace input and calls existing `new_turn_context` with that session.
3. The same-session P2 `for_session(...).snapshot()` runs after minting.
4. Exact correlation/snapshot association is validated and the immutable settled value is returned.

No evaluator, binding projection, adapter or pipeline is called. The captured P2 object is the one in the settled view. `test_turn_then_real_snapshot_then_settlement_exact_order` checks the sequence; `turn-order-proof.json` separately logs real constructor/mint/snapshot operations. One operation creates one P1 turn. Identical traces and repeated calls create new turns. There is no retry, deduplication or transport policy.

Failures propagate within this unwired passive API and produce no settled value/fake fallback. Future transport code must provide its separately reviewed shadow-local failure boundary; no REST/WS exception handler was added.
