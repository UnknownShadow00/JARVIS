"""Parent OS-sandbox only: eight bounded current-source synthetic checks."""
from pathlib import Path
import sys, unittest
base=Path('/target/tasks/proxmox-automation-phase3-review-r1')
sys.path[:0]=[str(base/'src'),str(base/'tests')]
checks=[
 'test_boundaries.BoundaryTests.test_no_client_supplied_authority_or_arguments',
 'test_boundaries.BoundaryTests.test_actual_pve_state_drift_refuses',
 'test_boundaries.BoundaryTests.test_source_or_activation_revocation_before_and_after_send',
 'test_review_r1.ReviewRegressions.test_receipt_retains_operation_lock_against_real_contender',
 'test_review_r1.ReviewRegressions.test_stale_or_unsynchronized_ready_never_reserves_an_action',
 'test_review_r1.ReviewRegressions.test_precheck_cannot_construct_or_read_real_transport_or_ledger',
 'test_transport.TransportTests.test_http_duplicate_ambiguous_length_and_size_abuse',
 'test_transport.TransportTests.test_websocket_fragment_mask_control_and_size_abuse',
]
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in checks)
result=unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
