# Exact archival disposition and independent probes

| Historical path | Required current counterpart | Decision |
|---|---|---|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_agent_stubs.py`|`tests/test_agent_stubs.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_enrollment_app.py`|`tests/test_enrollment_app.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_execution_pipeline.py`|`tests/test_execution_pipeline.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_release_security.py`|`tests/test_release_security.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_scheduler.py`|`tests/test_scheduler.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_scheduler_reliability.py`|`tests/test_scheduler_reliability.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_server_auth.py`|`tests/test_server_auth.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_server_integration.py`|`tests/test_server_integration.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_task_queue_callers.py`|`tests/test_task_queue_callers.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_task_queue_persistence.py`|`tests/test_task_queue_persistence.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_task_queue_store_safety.py`|`tests/test_task_queue_store_safety.py`|Byte-identical forensic evidence; never executed|
|`tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests/test_ue5_security.py`|`tests/test_ue5_security.py`|Byte-identical forensic evidence; never executed|

All12 also match prior canonical test blobs. See DISCOVERY-PROBES.json for exact commands/exits from inert fixtures. Thirteen ordinary variants reject with4/no imports; three intentionally defeating the policy import only an inert marker. No actual unsafe code or private configuration is used.

The guard cannot secure an arbitrary interpreter against operator disabling conftest/config or executing files directly. Supported full gates accept no pytest flags, clear child environment and disable plugin autoload. New unreviewed tests/ modules and new workflows fail preflight; historical directories have separately pinned membership and byte hashes.
