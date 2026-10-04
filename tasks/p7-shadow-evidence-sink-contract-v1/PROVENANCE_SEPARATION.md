# Separate from trusted P2 provenance

Sink entries/receipts remain observational even when Core-produced and durable. No LedgerStore creation/mutation, record_tool_result, provenance write/promotion, mutable snapshot access or result reconstruction. Never store them as P2 operational truth on sink failure. They are not trusted tool results and cannot enable obligations or permissions. P2 and its source/schema remain unchanged.
