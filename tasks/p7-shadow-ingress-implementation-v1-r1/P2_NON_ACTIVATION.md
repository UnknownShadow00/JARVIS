# No P2 activation

Ingress never constructs LedgerStore/ProvenanceLedger/LedgerSnapshot, selects a ledger, reads private ledger/owner state, or acquires another snapshot. It retains the settled snapshot exactly and calls only settled validation.

Runtime traps cover every real recorder, `_append`, `_supersede_locked`, `_build`, store drop/clear, store/ledger/snapshot constructors, ledger lookup and snapshot acquisition. All ingress counters are zero. Static exact imports/calls and mutable-owner/store rejection cases reinforce the boundary.

Two independent proof fixture writes and focused immutability fixture writes populate/change isolated in-memory P2 state outside guarded ingress. They are upstream test setup, not production trusted writes. No live owner, persistent P2 data, session storage or lifecycle change is created. No cleanup is required.
