"""Parent OS sandbox only; selected in-memory/fixture controls, no PVE/guest access."""
from pathlib import Path
import sys,unittest
base=Path('/target/tasks/proxmox-automation-phase3')
sys.path[:0]=[str(base/'src'),str(base/'tests')]
checks=[
 'test_boundaries.BoundaryTests.test_request_injection_and_privileged_catalog_denied_before_transport',
 'test_boundaries.BoundaryTests.test_no_client_supplied_authority_or_arguments',
 'test_boundaries.BoundaryTests.test_malformed_wire_and_structural_abuse',
 'test_boundaries.BoundaryTests.test_disabled_expired_unbound_overbroad_grants',
 'test_boundaries.BoundaryTests.test_actual_pve_state_drift_refuses',
 'test_boundaries.BoundaryTests.test_replay_new_id_bypass_and_restart_refused',
 'test_boundaries.BoundaryTests.test_lost_guest_response_latches_unknown_and_preserves_state',
 'test_boundaries.BoundaryTests.test_source_or_activation_revocation_before_and_after_send',
 'test_worker_runtime.WorkerRuntimeTests.test_worker_binding_cannot_change_principal_scope_or_action',
 'test_storage.StorageTests.test_independent_instances_cannot_acquire_same_operation_lock',
 'test_storage.StorageTests.test_symlink_hardlink_writable_parent_wrong_mode_refused',
 'test_storage.StorageTests.test_missing_or_wrong_client_receipt_cannot_clear_halt',
 'test_ipc.IPCTests.test_real_kernel_peer_credentials_and_group_enforcement',
 'test_ipc.IPCTests.test_production_account_policy_refuses_privileged_groups',
]
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in checks)
result=unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
