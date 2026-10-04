# Truthful durable acceptance

Accepted=True requires one complete, validated, explicitly versioned entry, its order and integrity metadata to be committed to durable local storage and recoverable after process/Core restart. Committed means the future backend's persistence barrier is satisfied before returning success. Object construction, enqueue, scheduled task, buffered write or ordinary close without a demonstrated durability contract is insufficient.

Exact file-sync, directory-sync, framing, atomic commit/transaction and concurrent-writer mechanics are implementation details that must be reviewed and fault-tested before implementation acceptance. No particular database or file engine is selected. Do not reuse current writers' lack of fsync as a durability guarantee. Normal restart/process crash and interrupted write are covered; hardware destruction or an unauthorized off-Core replication promise is not asserted.

If durability cannot be established, return nonaccepted, including COMMIT_UNCERTAIN when bytes may exist but commitment is unknown. Do not claim the record absent in that case, retry blindly, or delete possibly durable evidence. A lost success receipt can coexist with a durable entry; later reconciliation must resolve it. A returned failure is not a successful durable failure log, and a successful write is not evidence of upstream coverage.
