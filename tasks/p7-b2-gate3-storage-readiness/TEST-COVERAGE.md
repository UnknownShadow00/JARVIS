# Gate3 offline verification

Existing focused files (787 passed, zero failures; dummy credentials, intercepted provider, isolated stores):
- tests/test_model_ownership.py
- tests/execution/shadow_controller_test.py
- tests/execution/shadow_driver_test.py
- tests/execution/shadow_pilot_test.py
- tests/execution/shadow_pilot_server_test.py
- tests/execution/shadow_pilot_backup_test.py
- tests/execution/shadow_backup_recovery_test.py
- tests/execution/shadow_deployment_staging_test.py
- tests/execution/shadow_b2_preactivation_test.py
- tests/execution/shadow_runtime_test.py
- tests/execution/shadow_provider_ollama_test.py
- tests/execution/shadow_accounting_test.py
- tests/execution/shadow_full_path_test.py
- tests/test_server_auth.py

Command: canonical .venv/bin/python -B guarded pytest on the above files, -q --capture=sys -p pytest_asyncio.plugin -p no:cacheprovider, with private --basetemp. No real credential loaded. Parent/child audit guards deny credential opens, INET sockets and outside-fixture writes; only four isolated Python -c children allowed for crash/locking tests. No package installation/audit.

| Required condition | Existing exercised case / fixture |
|---|---|
| Single owner, duplicate refusal, endpoint/model binding, same-endpoint lifecycle interference | model_ownership exclusion, resource validation, completion association and two-process/crash tests |
| Persisted unknown after restart; no TTL release; cancellation not completion | possible_remote_never_auto_clears; two_processes_and_crash_unknown |
| Exact terminal/no-send association; separate supervision; no implicit fallback/unload | security_completion_must_match; supervised_resolution_is_distinct; resource integration and ambiguous transport refusal |
| Controller initialization refusal/recovery; default LEGACY/OFF | unprovisioned_factory_refuses_without_controller; stop_boundaries reopen refusal; shadow_controller recovery; runtime/server OFF tests |
| D04 receipts, D09 accepted set, uncertain joins | shadow_controller/accounting/full_path plus backup receipt association and uncertain_receipt_and_unknown_are_independent_after_restore |
| Exclusive/versioned backup; checksum/schema/corruption rejection | v2_finalization_unique_private_and_manifest_integrity; semantic_corruption_cannot_hide_behind_recomputed_hashes |
| Consistent snapshot under sole writer/locks | source_writer_stays_open_but_sql_commit_is_excluded; d04_writer_lock_refuses_coordinated_snapshot; backup_locked_remote_work_refuses |
| Failed/interrupted backup retains partial evidence | failed_finalization_retains_sources_and_diagnostics; backup_failed_creation_retains_partial_namespace; killed_writer snapshots |
| Stopped-only restore, occupied/newer/symlink refusal | restore_never_overwrites_state and damaged_backup_rejected_preserved |
| Unknown state retained, no silent reconciliation or measurement promotion | restored_receipt_does_not_clear_d06_unknown; d06_restored_companions_preserve_or_refuse_unknown; origin/eligibility promotion refusal |
| Extra acceptance and concurrent generation | four_attempt_exact_topology_and_ineligible_truth; durable_cap_includes_all_terminal_types; concurrent_refusal_no_backlog |
| Invalid auth and continuation mismatch | server auth_denial_stops_pilot_with_no_admission; continuation_denial; intake_aborts |
| Model/profile mismatch and tools in conversational scope | native_faults_stop_with_exact_accounting; bad_policy; provider qualification and client override refusal |
| Timeout after possible transmission, late terminal association | timeout_late_terminal_resolves_only_original_resource; stop_boundaries possible_send |
| Missing D04/COMMIT_UNCERTAIN/incomplete epoch | controller_d04_faults_stop_without_false_commit; d04_outlives_bounded_drain_retains_uncertain_late_receipt; crash-like backup cases |
| Required backup failure blocks further admission | backup_failure_stops_runtime; required_checkpoint_blocks_next_acceptance_until_verified |
| Operator stop during admission/dispatch | stop_while_durable_controller_reservation_pending; stop_after_dispatch_intent_but_before_transport_is_proven_not_sent; core_owned_abort |
| Operator stop during blocked backup beyond local drain | One additional standalone private fixture rehearsal: backup paused after settled acceptance; immediate admission closure; local deadline advanced without changing approved configuration; close returns incomplete with OPEN epoch/owned worker; later safe completion leaves CLOSED_INCOMPLETE, one retained acceptance and no further provider call |
| Corrupt restore source | manifest/file/semantic corruption refusal cases above |

The additional rehearsal passed (1/1). It is evidence-only, outside canonical source/test files. Production D06 was never poisoned with test unknown state, and no production controller/receipt/epoch was initialized. Historical fixture .27 resource strings exercise synthetic identity isolation only; no operational request used that endpoint.

Consistency limit: runtime bundles use the sole controller writer, a pinned SQLite read transaction and D04/D06 locks. This is a coordinated snapshot under those assumptions, not distributed cross-component atomicity. File-write interruption preserves partial evidence and required checkpoint failure closes admission. The stopped restore argument requires independent supervisor verification. No production restore or promotion to measurement.

Fresh deterministic golden12/20; same eight failures; forbidden registry/provider/HTTP/tracing calls zero. Legacy digest inherited through unchanged bytes, not a model-capable probe. Historical full regression7110 passed/11 deselected/zero failures not rerun; no source/test change triggered it.
