# Audit separation

ShadowObservationRecordV1 is not AuditEventV3, ExecutionAuditRecord, turn.summary or operational audit truth. It is not serialized to audit-v3 and has no edge to app/logs/audit.py or to_audit_entry. F-AUDIT-01 remains open.

The older plan says shadow results are audit-only; operator C1 and this task require truthful separate observational evidence wherever operational audit cannot represent it. No event name or schema is changed. S13_AUDIT in PipelineStop remains an existing internal pipeline stage code, not proof that an audit event was emitted. A candidate source label does not assert operational success. CT-001 draft-retention requirements are not fulfilled by this raw-text-free record.
