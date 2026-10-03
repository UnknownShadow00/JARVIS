# F-MAP-01 contract review — no implementation

This task inspected canonical Core production at `ac685a898e0fb55cf7c97a3e04e5765bf2e37a41` and the frozen task history. It wrote design and evidence only. The intended producer would be a JARVIS-owned pure composition boundary feeding the existing `RecordedTurn` fields `router_context`, `expected` and `permission_projection`; it must not create a permission decision or execution authority. No producer, path, server/API/UI consumer, registry connection, test or production code was added.

**Status: blocked for full F-MAP-01 closure.** The frozen source explicitly withholds the live capability→tool namespace, required argument schema and target-field correspondence. It also leaves the authoritative live capability inventory source open. Any concrete mapping here would invent authority. `OWNER.md` states the bounded conceptual owner and the remaining implementation-path question; `FOLLOWUPS.md` states the operator decisions.
