# Filesystem and interruption qualification

Disposable storage only (`/tmp` tmpfs and `/home/jarvis/jarvis-gate6f-*` ext4 stages on Core, under Landlock + seccomp). No live backup, host filesystem or kernel setting touched.

| Brief item | Test(s) | Result |
|---|---|---|
| Atomic publication and rename | `test_checkpoint_failure_never_grants_next_permit` (3 crash points), `test_interrupted_checkpoint_is_not_valid` | PASS — unpublished staging never valid, no next permit |
| Directory fsync | source: `sync_dir` after every create/rename | Code path present; durability across power loss NOT PROVEN |
| Short writes | **6F real kernel**: `RLIMIT_FSIZE=64` during successor reservation → `os.write` returned 64 B → `RESERVATION_PARTIAL_WRITE`, no state dir; retry refused `SUCCESSOR_ALREADY_RESERVED`. 6E simulated: `test_short_reservation_preserves_hold` | PASS |
| Full disk | **6F real kernel**: `RLIMIT_FSIZE` = half the DB during checkpoint → `EFBIG`, SQLite `OperationalError`, bundle without manifest, 0 checkpoint rows, store not ready. 6E: `test_coordinated_disk_full_keeps_accepted` | PASS |
| Permission-denied writes | `test_permission_drift_blocks_checkpoint_and_next_permit` | PASS — mode drift refused by policy before any kernel EACCES; checkpoint and next permit blocked; kernel EACCES path itself not exercised |
| Symlink substitution | `test_symlink_ancestor_refused`, `test_backup_refuses_receipt_symlink`, `test_coordinated_symlink_refused`, 6F `test_symlinked_evidence_file_refused` | PASS |
| Corrupt checkpoint | `test_coordinated_corruption_refused`, `test_rehashed_incoherent_checkpoint_rejected` (4) | PASS |
| Corrupt predecessor | 6F `test_corrupt_predecessor_archive_refused_with_fixed_code` (5 mutations) | PASS, fixed refusal codes |
| Concurrent successor reservation | `test_concurrent_successor_creation_only_one_wins`, `test_competing_successor_writers` | PASS |
| Interrupted permit commit | crash-point tests incl. `permit_spent_before_insert`, `accept_before_commit` | PASS |
| Process crash before/after provider send | `test_actual_process_exit_preserves_highwater`, `test_process_crash_highwater_and_checkpoint` (real child exits) | PASS |
| Provider completed, D04 receipt missing | `test_receipt_join_fault_retains_uncertainty` | PASS — uncertainty retained |
| Legacy delivered, Granite failed | 6F `granite_failure` variant; `test_stop_granite_preserves_delivery` | PASS — delivery stays `LOCAL_SEND_COMPLETED`, attempt incomplete |
| Final checkpoint failure | `test_final_checkpoint_failure_is_incomplete` | PASS — downgrade to `CLOSED_INCOMPLETE` |
| Restore older high-water | 6F `test_partial_rollback_of_highwater_or_controller_is_refused` | PASS (detected) |
| Restore everything older together | 6F `test_coordinated_full_rollback_is_not_detectable_locally` | **NOT DETECTED** — documented limit |
| Terminal stop under partial evidence | `test_final_checkpoint_unknown_is_forensic` | PASS — forensic, never complete |

Power loss, storage-controller and VM-host crash guarantees remain **unproven**. They need separately approved infrastructure testing. Note that Core itself experienced an uncontrolled power-off on 2026-10-15; V2 shut down cleanly through its lifespan path in that event, which is one observation, not a qualification.
