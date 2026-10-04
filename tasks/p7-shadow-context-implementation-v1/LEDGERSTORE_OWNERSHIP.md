# Instance-owned P2 allocation

Each `ShadowContextV1` constructor creates one `LedgerStore` in `self._store`. A separately minted session selects the actual ledger through `for_session(session_id)`. That canonical P2 get-or-create association is made when the snapshot is requested, after turn minting. No global, module singleton, shared owner factory, externally injected store or shared mutable session map is introduced.

An owner maintains one internal session. Repeated turns reuse its session and ledger. Different owners allocate separate stores and separate ledgers; they cannot select each other's state through public APIs. The settled value holds neither owner nor store nor ledger. No public getter admits a store handle or a caller-created session.

`ledgerstore-allocation-proof.json`: two owners, two real stores, two real ledgers, three turns and three snapshots. Actual constructor allocation succeeds with every recorder/mutation surface trapped. These are test-process allocations, with no persistent P2 data and no live owner. Retention/drop/clear triggers and cross-worker concurrency remain deferred.
