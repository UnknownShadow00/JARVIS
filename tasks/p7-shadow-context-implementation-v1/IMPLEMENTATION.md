# Passive Shadow Context V1 implementation

Canonical source: Core `/home/jarvis/JARVIS`. Entry parent: `d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c`, clean, 361 tracked files and zero unexpected untracked files. Context, ingress and observation were absent. The separate documentation checkout entered at `5986d0cff6b3d1270405560e470855a9f8301e5c`.

`app/execution/shadow_context.py` adds `ShadowContextV1()` and the frozen, slotted `SettledShadowTurnContextV1`. An internal owner mints its P1 session without accepting identity/store input. `create_turn(*, transport_trace_id=None)` mints one existing P1 correlation context with that session, reads the owner's actual P2 ledger snapshot, validates it, and returns exactly correlation/snapshot/transport_trace_id. Exceptions issue no replacement context. No request text, transport admission or continuation API exists.

The initial frozen corpus failed on the missing module. Its expectations were unchanged. New focused cases: 54; focused context plus existing provenance gates: 62 passed; full regression: 5775 passed, 11 deselected, zero failed, two existing dependency warnings. Golden: 12/20, unchanged eight failures. No P1/P2 source, package export, server, adapter, lifecycle, policy or audit change.

Evidence is outside the production repository at `/home/jarvis/.hermes-poc/evidence/p7-shadow-context-implementation-v1/`. Production and documentation commits are recorded there separately. Runtime rollback needs no action; source/test rollback is one production commit revert. Formal P7 exit remains incomplete and P8 blocked.
