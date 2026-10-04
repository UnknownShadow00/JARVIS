# Request-time snapshot

P2 snapshot construction occurs after the one P1 turn is minted, and before any future downstream evaluation. New sessions legitimately yield `records=()` from real `LedgerStore.for_session(...).snapshot()`. This represents unavailable facts in the context, not universal empty truth. Snapshot exceptions and mismatched/invalid inputs produce no replacement snapshot or settled view.

`snapshot-proof.json` contains actual first-session, populated later-session and post-supersession views. The populated view retains exactly the captured snapshot. Later ledger writes replace frozen records under existing P2 rules, preserving the old tuple/values. No reread is performed by the settled object.

The proof's two `record_user_fact` calls are explicitly isolated fixture setup/state changes outside guarded context operations. Passive construction/issuance write count remains zero. They are not production provenance writes or model claims.
