# Owner and boundary

`shadow_context.py` will own the association between authoritative JARVIS conversation sessions, accepted turns and existing P2 ledgers. An instance-owned LedgerStore maps session IDs to separate ledgers; it is not a global cross-session ledger. Internal mutable state never crosses the settled-turn boundary.

`shadow_ingress.py` will consume settled context and exact untrusted request text, composing an immutable envelope only. It cannot resolve sessions, mint turns, own a store, infer trust, schedule work or evaluate a model. No module-level singleton is authorized. Instantiation and lifecycle wiring require later implementation review.
