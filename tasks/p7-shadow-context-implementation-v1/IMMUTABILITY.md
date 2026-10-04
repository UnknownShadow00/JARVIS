# Settled value immutability

`SettledShadowTurnContextV1` is a frozen, slotted dataclass with exactly `correlation`, `snapshot`, `transport_trace_id`. Its P1 correlation is the existing frozen/slotted value. Its P2 snapshot retains the existing public read-only API, tuple records and frozen record values. Recursive boundary validation rejects mutable value containers and callables; no callback, service locator, owner/store/ledger reference is stored.

Frozen tests reject assignments to settled fields, correlation IDs and public snapshot properties. They alter returned serialization mappings, original nested fixture inputs, later ledger supersession, the owner store/identity and private ledger record list. The already-issued view stays unchanged. `immutability-proof.json` records these independently.

Existing P2 `LedgerSnapshot` is not a frozen dataclass, and private slot assignment/object.__setattr__ or malicious in-process Python is not hardened by this contract. No P2 type change or duplicate wrapper snapshot is authorized. Callable leakage refers to values/handles in the data graph; existing read-only snapshot and P1 convenience methods remain their canonical APIs.
