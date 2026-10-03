# Security invariants

1. JARVIS owns IDs, classification, route, lane, expected binding, permission query and all policy outcomes; model/provider/client/UI values remain data.
2. A live capability requires an approved JARVIS inventory and P4 registration. Advertised `ToolSchema` and abstract router defaults grant nothing.
3. Closed tool/required-argument/target-field mapping must be signed before producing an executable expected binding. Unknown or ambiguous maps fail closed.
4. P3 canonicalizer is the only normalizer; exact version and entire map are preserved. No fuzzy match, repair, dropped extra argument or model-selected target.
5. P4 is the only permission decision owner; browser D-01 and all current policy rows remain unchanged.
6. P4 confirmation owner supplies only the V2 settled projection; no machine import, `CONFIRMED` state or claim in the producer.
7. P5 alone owns invocation/result; no producer dispatch, registry call, executor entry, retry or `TrustedToolResult` construction.
8. Projection creation is passive: zero network, subprocess, model/provider/Ollama, registry, dispatch, confirmation/provenance/audit writes or clock/random selection. Required settled state is supplied by its owner.
9. Same immutable request/state/version inputs produce identical projection; no mutable alias survives handoff.
10. No operational model prose is exposed; a stopped turn remains non-renderable pending separate live fallback/audit contracts.

No production implementation, shadow traffic, policy or audit schema change was made to claim these invariants as runtime-proven for a future producer. They are acceptance constraints.
