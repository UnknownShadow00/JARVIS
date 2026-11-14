# Fifteen historical cases

All15 exact historical assertions are reproduced as failures on R3 and pass on R4. This does not resolve the broader group-level gaps discovered by new inputs. Original R3:14 unsafe acceptances and1 legitimate retention obstruction.

| Group | Exact independent identity | R3 | R4 exact regression | Fresh variation |
|---|---|---|---|---|
| R3-A04 | `fresh_probes.Extra.test_duplicate_impossible_exit_code` | FAIL | PASS | `test_collision_signal_plus_expected_diagnostic`: PASS_BLOCKED |
| R3-A04 | `fresh_probes.Extra.test_duplicate_signal_exit_masquerades_as_refusal` | FAIL | PASS | `test_collision_unrelated_manager_error`: PASS_BLOCKED |
| R3-A03 | `fresh_probes.Extra.test_raw_clock_utc_precedes_capture_request` | FAIL | PASS | `test_guard_started_before_timer_creation`: FAIL_UNSAFE_ACCEPTANCE |
| R3-A03 | `fresh_probes.Fresh.test_callback_before_guard` | FAIL | PASS | `test_guard_started_before_timer_trigger`: FAIL_UNSAFE_ACCEPTANCE |
| R3-A05 | `fresh_probes.Fresh.test_command_receipt_untrusted_environment` | FAIL | PASS | `test_wrong_receipt_environment`: PASS_BLOCKED |
| R3-A01 | `fresh_probes.Fresh.test_completion_exit_after_capture` | FAIL | PASS | `test_plain_exit_malformed_invocation`: FAIL_UNSAFE_ACCEPTANCE |
| R3-A01 | `fresh_probes.Fresh.test_completion_exit_before_start` | FAIL | PASS | `test_plain_exit_prior_generation_invocation`: FAIL_UNSAFE_ACCEPTANCE |
| R3-A01 | `fresh_probes.Fresh.test_completion_invocation_substitution` | FAIL | PASS | `test_successful_callback_failed_service`: PASS_BLOCKED |
| R3-A01 | `fresh_probes.Fresh.test_completion_start_before_authorization` | FAIL | PASS | `test_main_wall_mono_conflict`: PASS_BLOCKED |
| R3-A03 | `fresh_probes.Fresh.test_final_start_timestamp_text_before_authorization` | FAIL | PASS | `test_changed_clock_domain`: PASS_BLOCKED |
| R3-A06 | `fresh_probes.Fresh.test_later_namespace_must_allow_retained_owned_unit` | FAIL | PASS | `test_retained_journal_loses_diagnostic_at_admission`: FAIL_UNSAFE_ACCEPTANCE |
| R3-A05 | `fresh_probes.Fresh.test_receipt_wrong_operation` | FAIL | PASS | `test_receipt_unexpected_field`: PASS_BLOCKED |
| R3-A02 | `fresh_probes.Fresh.test_waiting_control_process_present` | FAIL | PASS | `test_guard_started_during_never_invoked_waiting`: FAIL_UNSAFE_ACCEPTANCE |
| R3-A02 | `fresh_probes.Fresh.test_waiting_executed_trailer` | FAIL | PASS | `test_post_stop_leaked_process`: PASS_BLOCKED |
| R3-A02 | `fresh_probes.Fresh.test_waiting_failure_exit_status` | FAIL | PASS | `test_timer_never_fired`: PASS_BLOCKED |

TRACE files contain actual validator calls and reconstructable JSON patches, with source/fixture hashes. The original39 harness/source were copied verbatim from the independently sealed R3 audit and ran on a copy of the exact R3 packet. The R4 port preserves all10 assertion/fail AST calls. Two fixture adaptations are explicit: populate the timestamp mutation in the now-populated field, and supply complete retained raw evidence/ledger for the positive A06 case. The old A06 summary alone remains insufficient. PROBE-PORT.diff records exact changes. Full-record bytes cannot be identical across newly mandatory schemas; semantic hostile changes are preserved.

Fourteen targeted R4 inputs raise ValueError with BLOCKED. A06 returns true for the valid complete retained-prefix case. No relevant validator path is bypassed. Positive full-record and plain-exit controls independently pass. Unknown real-host timing/text may legitimately block and has not been qualified. Individual group reassessment remains stricter than these15 historical assertions.

