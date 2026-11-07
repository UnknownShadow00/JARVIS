import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
import pytest
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','--basetemp=/scratch/registry-controls',
 '/target/tests/test_recovery_decisions.py::test_restore_proposal_decision_receipt_restart',
 '/target/tests/test_recovery_decisions.py::test_replay_identical_only_and_branch_duplicate',
 '/target/tests/test_recovery_decisions.py::test_invalid_authorization_fails_before_admission[forged]',
 '/target/tests/test_recovery_decisions.py::test_invalid_authorization_fails_before_admission[wrong_operator_scope]',
 '/target/tests/test_recovery_decisions.py::test_forged_receipts[wrong_key]',
 '/target/tests/test_recovery_decisions.py::test_witness_renewal_new_generation_restart_and_stale_substitution',
 '/target/tests/test_recovery_decisions.py::test_registry_corruption_rollback_and_incomplete_history[external_ahead]',
 '/target/tests/test_recovery_decisions.py::test_checkpoint_key_cannot_forge_operator_authorization_on_restart',
 '/target/tests/test_recovery_decisions.py::test_stale_custody_lock_before_commit_is_fenced',
 '/target/tests/test_recovery_decisions.py::test_authorization_expiring_during_validation_never_publishes_intent']))
