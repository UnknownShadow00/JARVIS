# Separate from operational audit

Persisted observation entries and receipts are not AuditEventV3 or operational audit truth. Never serialize them as audit-v3, invoke audit.log/to_audit_entry, reuse the audit worker/sink, or claim executed, tool success, external mutation, confirmation claim or legacy replacement. A copied permission/candidate enum is only an observation label.

If evidence persistence fails, do not write a fallback operational audit event. F-AUDIT-01 remains open. Existing audit source/schema/queues/rotation are untouched. P1 utc_now/ISO conventions can be reused without using its audit record machinery.
