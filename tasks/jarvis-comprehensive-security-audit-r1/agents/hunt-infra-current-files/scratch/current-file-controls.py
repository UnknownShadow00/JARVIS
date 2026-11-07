"""Parent sandbox only: mocked gate failures and scratch-local storage checks."""
from pathlib import Path
import sys,unittest
base=Path('/target/tasks/proxmox-automation-phase3-review-r1')
sys.path[:0]=[str(base/'src'),str(base/'tests')]
checks=[
 'test_preissuance.PreissuanceTests.test_each_binding_must_match_exact_grant_and_exact_type',
 'test_preissuance.PreissuanceTests.test_time_age_expiry_and_grant_expiry_are_bounded',
 'test_preissuance.PreissuanceTests.test_marker_presence_or_metadata_failure_blocks_before_record_read',
 'test_preissuance.PreissuanceTests.test_issuance_gate_failure_precedes_token_output_prompt_and_network',
 'test_preissuance.PreissuanceTests.test_prompt_delay_revalidates_expiry_markers_config_ca_and_release_before_network',
 'test_storage.StorageTests.test_symlink_hardlink_writable_parent_wrong_mode_refused',
 'test_storage.StorageTests.test_missing_state_is_not_silently_recreated',
 'test_storage.StorageTests.test_initialization_never_overwrites_existing_state',
 'test_storage.StorageTests.test_corrupt_audit_refuses_open_without_repair',
 'test_storage.StorageTests.test_missing_or_wrong_client_receipt_cannot_clear_halt',
]
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in checks)
result=unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
