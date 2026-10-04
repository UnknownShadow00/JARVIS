# Independent sessions

Two independent owners have different canonical session IDs, distinct stores and distinct per-session ledgers. A fixture fact in owner A is absent from B's snapshot; B cannot obtain A's ledger through its store. Independent writes in B's isolated fixture do not change A. Repeated turns in one owner keep its ledger/session.

`test_two_owners_isolate_all_mutable_p2_state` exercises both directions with actual P2 fixture data. `cross-session-proof.json` separately records store/ledger identity and empty foreign lookup. Every passive construction and snapshot call remains guarded against trusted mutation. Cross-worker sharing, concurrent-turn admission and restoration are not provided.
