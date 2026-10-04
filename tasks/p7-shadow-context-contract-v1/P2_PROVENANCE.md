# P2 source authority

`app/execution/provenance.py:241-266` owns a per-session ProvenanceLedger. `:522-531` returns its current-record snapshot; `:546-560` supersedes by replacing frozen records; `:563-599` exposes LedgerSnapshot; `:602-646` owns the instance-scoped LedgerStore. Existing value freezing uses tuples and MappingProxyType, and rejects ModelDraft/ToolProposal (`:122+`). Validate record/session association using existing validation, as the binder already does (`binding_projection.py:55-78`).

Canonical `tasks/task13b11d/LEDGER_API.md` §§2,3,5,6 defines snapshots unaffected by later writes, one ledger per session, in-memory lifetime, and defers concurrent-turn serialization. Existing tests `tests/execution/provenance_test.py:589-598` verify old snapshots survive later writes. No new trust class or provenance source is introduced.
