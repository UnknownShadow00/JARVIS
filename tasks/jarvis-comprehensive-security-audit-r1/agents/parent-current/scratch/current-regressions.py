import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
import pytest
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','--basetemp=/scratch/current-regressions',
 '/target/tests/test_operator_ledger.py::test_state_tamper_rejected_before_dispatch',
 '/target/tests/test_audit_disaster.py::test_cached_checkpoint_bytes_are_still_hash_verified',
 '/target/tests/test_audit_disaster.py::test_trust_reference_rejects_rolled_back_checkpoint_generation',
 '/target/tests/test_authority_enrollment.py::test_enroll_genesis_receipt_restart_verification',
 '/target/tests/test_authority_enrollment.py::test_branch_continuity_proposal_is_readonly_and_preserves_unknown',
 '/target/tests/test_server_auth.py::test_auth_disabled_by_default',
 '/target/tests/test_server_auth.py::test_valid_token_accepted']))
