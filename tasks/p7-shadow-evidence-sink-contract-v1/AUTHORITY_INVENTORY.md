# Canonical authority and storage inventory

All actual source references pin Core d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c; exported tracked source is checked against the unchanged 361-file baseline. Eight prior sealed bundles verify 770 checks, zero failures including all 177 observation-producer artifacts. Context/envelope/preparation authorities are retained in the autonomous sealed bundle; D03 docs are verified against the observation bundle.

| Authority | Exact source |
|---|---|
| D04 original | tasks/p7-formal-exit-preparation/OPERATOR-DECISIONS.md, f523900decbde453858e808c93d678b97657ef9b; historical packet unchanged |
| Context/identity | tasks/p7-shadow-context-contract-v1, 63984cac4bacb0d1a28ef9bff9f0ab3ee7e52200; correlation, snapshot, trace; no retry identity |
| Envelope | tasks/p7-shadow-envelope-contract-v1-r1, 4fb1d4da1342b35f7ed997550a45dccd69922eca; raw request + context only |
| Observation | tasks/p7-shadow-observation-contract-v1, 28bfd59bc75a176d9804c0aa748f550cb5357390; 18 fields, no numeric version/wire/clock/persistence, nullable facts, cardinality limits |
| Passive pipeline | tasks/task13b11p-r8/PIPELINE_API.md and FINAL-REPORT.md; sealed bundle task13b11p-r8-p7-passive-pipeline (prompt uses bundle name for this directory); actual pipeline.py three terminal alternatives |
| Formal phase/rollback | tasks/task13b11a/IMPLEMENTATION_PHASES.md P7/P8, FEATURE_FLAG_AND_ROLLBACK.md evidence never deleted |
| Local storage conventions | app/agent/task_queue.py:14; scheduler.py:19; resource_manager.py:26; config.yaml:143,234; .gitignore /data/; docs/BACKUP.md |
| Existing persistence | app/observability/tracing.py:41–81; logs/audit.py:21–91; task_queue.py:92–118; scheduler.py:103–129; resource_manager.py:490–499; none sufficient unchanged |
| Serialization/integrity | registry_metadata.py:45–53; CorrelationContext.to_mapping; audit_events.py:486; prior sealed SHA256SUMS conventions |
| Public serving | server.py:154 mounts frontend PWA, not data; no new public endpoint allowed |

Capacity inspected with df -h/-i and targeted du; Core has 64G free, local original has 2.9G free. Full old-evidence du reports inaccessible historical pyc files and therefore a partial aggregate; no deletion/permission change attempted. Required manifest checks themselves pass. Actual filesystem privacy/backups require future integration proof; no secrets/environment dumps or remote export performed.
