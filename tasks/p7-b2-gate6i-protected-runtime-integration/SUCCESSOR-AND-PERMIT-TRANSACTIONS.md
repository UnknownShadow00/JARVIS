# Successor, signed claims and accepted attempts

Succession: fixed terminal proof → signed canonical payload/expiry/identity → second proof read → single RUNTIME_SUCCESSOR append under BEGIN IMMEDIATE → commit → acknowledgment. The existing explicit zero-use retirement and unattributed-stop exception fields are preserved. All examples are fixture predecessor identities. No historical V2 retirement or actual V3 successor exists.

Opening/permit: signed APPROVE event → runtime validates current local/coordinated prerequisites → durable CLAIM → local control/permit commit. CLAIM cannot be repeated even after local controller rollback. Lost local effect after CLAIM is an incomplete transaction and blocks progress.

Acceptance: exact unspent local permit and protected signed approval → CHECK → CONSUME (protected ACCEPT event) → D09 Store.accept transaction → BIND exact actual D09 ID → provider eligibility. Accepted ordinal derives from the single protected history, maximum four globally, fixed REST/REST/WS/WS order and one session per transport. No refunded failed attempt, replaced expired permit, automatic next permit or retry.

The helper's independent fixed reader compares actual local signed control rows with protected claims, accepted IDs with BIND, commitments and expiry with signed permits, and every provider substep with SEND. Interrupted CONSUME/BIND cannot be repaired by reducing the counter or restoring an older backup. Future recovery is human-reviewed, not an implemented convenience API.

Coordinated snapshot contains a derived highwater SQLite projection solely to preserve existing backup validators. The protected append-only history is authoritative; the projection has no writeback or restore path. Service graph has no protected database handle.
