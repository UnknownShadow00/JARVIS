# Formal P7 evidence retention

Successfully durable P7 observations and their integrity/order information are append-only. No automatic deletion, numeric TTL, background pruning or destructive rotation is authorized. Retain them through all three gates: (1) applicable formal P7 window completion; (2) construction and sealing of its exit bundle; (3) explicit operator acknowledgement and cleanup authorization. Window end, rollback, restart, full disk or completed sealing alone does not authorize removal.

An implementation may segment data only if every prior durable entry remains available and its order/integrity is preserved; no segment size/cadence is selected. A later correction adds separate evidence under separately defined semantics; it cannot overwrite an existing observation into another meaning. Corrupt/partial material is preserved for diagnosis, excluded from valid accepted entries, never silently edited/deleted as recovery.

Finite capacity is handled by explicit evidence failure/incomplete coverage, not deletion or fabricated success. Further-shadow pause/admission/resource bounds belong to D07. P7 retention is not a forever product-wide retention policy. Post-P7 retention/deletion, privacy review and any cleanup command require a later operator decision. No existing trace rotation, restic pruning or snapshot schedule is changed.
