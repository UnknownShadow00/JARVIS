"""Small synthetic ledger regression subset; OS sandbox execution by parent only."""
import os,sys
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
import pytest
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','--basetemp=/scratch/pytest-ledger',
 '/target/tests/test_operator_ledger.py::test_state_tamper_rejected_before_dispatch',
 '/target/tests/test_operator_ledger.py::test_checkpoint_damage_fails_closed',
 '/target/tests/test_operator_ledger.py::test_export_path_alias_cannot_reach_checkpoints',
 '/target/tests/test_operator_ledger.py::test_checkpoint_initialization_rejects_symlink_before_creating_children',
 '/target/tests/test_audit_disaster.py::test_cached_checkpoint_bytes_are_still_hash_verified',
 '/target/tests/test_audit_disaster.py::test_trust_reference_rejects_rolled_back_checkpoint_generation',
 '/target/tests/test_audit_disaster.py::test_rollover_retains_checkpoint_identities']))
