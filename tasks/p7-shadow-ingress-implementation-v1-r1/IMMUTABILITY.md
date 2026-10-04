# Public immutable graph

Envelope is frozen/slotted and stores only an exact immutable string and exact validated settled view. Public assignment to envelope/context/P1 fields or snapshot properties fails. Original caller payload dictionaries/lists are not stored. Changing a payload message or metadata after construction has no effect.

Populated fixture snapshots retain their original tuple/frozen records and immutable nested values after source-list/dictionary mutation and later ledger supersession. The envelope retains the exact snapshot object; it does not copy, freeze anew, or read current ledger state. No callable, store, ledger, owner or transport handle leaks through data fields.

Existing LedgerSnapshot has a public read-only API, not a frozen-dataclass/private-slot security boundary. Hostile in-process `object.__setattr__` or private slot mutation is outside the frozen guarantee. Malformed settled graphs are rejected by reusing their existing validator. No P2 type change or competing snapshot representation is made.
