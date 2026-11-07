import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
import pytest
raise SystemExit(pytest.main(['-q', '--tb=short', '-p', 'pytest_asyncio.plugin', '-p', 'no:cacheprovider', '--basetemp=/scratch/pytest', '/target/tests/test_operator_ledger.py::test_guarded_pipeline_readiness_and_read_only_diagnostics', '/target/tests/test_operator_ledger.py::test_rollback_against_external_checkpoint_rejected', '/target/tests/test_operator_ledger.py::test_checkpoint_initialization_rejects_symlink_before_creating_children', '/target/tests/test_operator_ledger.py::test_export_path_alias_cannot_reach_checkpoints', '/target/tests/test_audit_disaster.py::test_restore_reconstructs_exact_disabled_artifact', '/target/tests/test_audit_disaster.py::test_default_restore_requires_external_reference_and_explicit_grant', '/target/tests/test_audit_disaster.py::test_restore_paths_and_existing_targets_refused', '/target/tests/test_recovery_decisions.py::test_restore_proposal_decision_receipt_restart', '/target/tests/test_recovery_decisions.py::test_witness_renewal_new_generation_restart_and_stale_substitution', '/target/tests/test_recovery_decisions.py::test_readonly_inspection_has_identical_storage_bytes']))
