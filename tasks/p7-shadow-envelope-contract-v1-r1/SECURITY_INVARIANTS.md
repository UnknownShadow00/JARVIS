# Security invariants

1. Client input can populate request only; no authority fields.
2. Context comes from the JARVIS owner, not serialized request claims.
3. P1/P2 association and snapshot ordering are preserved.
4. No store, request/socket/server, callable or execution-capable object crosses the boundary.
5. One WS input captures before stream/fallback; chunks never duplicate a turn.
6. Composition neither changes legacy output nor triggers downstream evaluation.
7. Failures remain shadow-local; no fake identity/snapshot/result fallback.
8. Adapter/model-free behavior and scheduling remain independently blocked.
9. audit-v3 remains unchanged; no inert observation claims operational truth.
10. CT-001 is not marked passed by a candidate response; P8 remains blocked.
