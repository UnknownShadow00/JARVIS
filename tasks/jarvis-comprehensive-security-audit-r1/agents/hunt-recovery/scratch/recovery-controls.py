"""Parent-sandbox only: bounded synthetic enrollment/restore/permit controls."""
import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
import pytest
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','--basetemp=/scratch/recovery-tests',
 '/target/tests/test_authority_enrollment.py::test_enroll_genesis_receipt_restart_verification',
 '/target/tests/test_authority_enrollment.py::test_invalid_new_store_admission_is_refused[permit]',
 '/target/tests/test_authority_enrollment.py::test_invalid_new_store_admission_is_refused[scope]',
 '/target/tests/test_authority_enrollment.py::test_enrolled_store_requires_external_witness',
 '/target/tests/test_authority_enrollment.py::test_branch_continuity_proposal_is_readonly_and_preserves_unknown',
 '/target/tests/test_audit_disaster.py::test_restore_reconstructs_exact_disabled_artifact',
 '/target/tests/test_audit_disaster.py::test_default_restore_requires_external_reference_and_explicit_grant',
 '/target/tests/test_operator_ledger.py::test_operator_permit_payload_and_lifetime_are_strict']))
