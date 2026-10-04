# Deterministic failure

Malformed request/context produces no envelope and no repair/coercion. Exact type checks reject request subclasses, mutable values, owners, stores, ledgers, standalone snapshots, transport objects and callables. Existing settled validation rejects invalid P1 IDs/child association, wrong-session snapshot/records, invalid trace and mutable/callable record values.

No session/turn/trace/snapshot/request/result is fabricated. No exception is translated to a pipeline outcome. This unwired API propagates validation errors; the frozen future transport caller must contain them locally while preserving legacy processing, cancellation and disconnect semantics. No blanket BaseException handler or legacy fallback is added.
