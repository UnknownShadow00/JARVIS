# Independent security findings

**Verdict: REJECT.** Six finding groups cover fifteen fresh failing assertions. Fourteen inputs incorrectly pass consistency validation; one required retained-unit input incorrectly blocks admission. These are offline qualification-assurance defects, not demonstrations of host compromise, privilege escalation or VM actuation. All block this complete procedure.

## R3-A01 — MEDIUM: Completion and final observations need not describe the same execution

Source in the exact reviewed R3 packet: `src/proof.py:176-185; src/proof.py:107; src/results.py:49-50`.

**Reproduction:** Change only success.completion service InvocationID to a different valid 32-hex ID, or its ExecMainStartTimestampMonotonic to 1, or its exit to before start/after capture. Synchronize raw show/receipt and reseal the complete envelope. Every case returns PASS_SYNTHETIC_ONLY.

**Root cause:** case_order applies terminal() to completion but execution_interval() only to final. Completion journal events are compared with the final event list, and plain exits with final.service; completion.service invocation and execution interval are never cross-bound to those events or final.service.

**Required correction:** Validate the execution interval at every completed observation; bind each observation to the one invocation and exact exit history. Compare completion and final immutable execution facts. A later summary cannot repair an impossible earlier completion.

Fresh failing methods: `test_completion_invocation_substitution`, `test_completion_start_before_authorization`, `test_completion_exit_after_capture`, `test_completion_exit_before_start`.

## R3-A02 — MEDIUM: Waiting observations can contain execution or control-process evidence

Source in the exact reviewed R3 packet: `src/binding.py:118-125; src/binding.py:44-50; src/binding.py:111-114`.

**Reproduction:** Retain active/waiting timer and inactive service, then set ControlPID=12345, or ExecStart pid=12345/code=exited/status=7, or ExecMainCode=1/ExecMainStatus=7 in the first success waiting capture. Raw/decoded fields agree and the complete result still passes.

**Root cause:** waiting() checks service ActiveState/Result/InvocationID/MainPID but omits ControlPID, ExecMainCode/Status, execution timestamps and command trailers. Generic verify_pair validates numeric/shape only for these fields.

**Required correction:** Define and enforce a coherent never-invoked waiting matrix including both PIDs, zero invocation clocks/status, untouched ExecCondition/ExecStart trailers and no jobs. Test it at every waiting/collision observation.

Fresh failing methods: `test_waiting_control_process_present`, `test_waiting_executed_trailer`, `test_waiting_failure_exit_status`.

## R3-A03 — MEDIUM: Remaining clock and execution-order contradictions pass

Source in the exact reviewed R3 packet: `src/binding.py:44-50,70-77,148-170; src/proof.py:16-37,107-133,187-205`.

**Reproduction:** Three separate inputs pass: (1) move guard journal/payload to D+500ms while callback remains D+100us, reorder raw/events coherently; (2) supply an ExecStart start_time text in 2020 alongside 2031 monotonic/session observations; (3) move only a clock receipt actual UTC request/end by +900ms while raw clock UTC remains .000100, 899900us before the .900000 request.

**Root cause:** Membership in an invocation interval does not order guard before payload. ExecStart textual timestamps are matched but not interpreted or reconciled. Raw-clock UTC and receipt-start UTC are each checked against the same rounded second, not against each other or the precise BOOTTIME anchor.

**Required correction:** Require guard completion before main-process execution/callback, distinguish guard and main intervals, reconcile every supported timestamp representation, and bracket raw clock UTC by actual receipt UTC with an explicit bounded sampling error. Unknown serialization must block. Do not invent systemd257 ordering from fixtures.

Fresh failing methods: `test_callback_before_guard`, `test_final_start_timestamp_text_before_authorization`, `test_raw_clock_utc_precedes_capture_request`.

## R3-A04 — MEDIUM: Invalid process exit states count as collision refusal

Source in the exact reviewed R3 packet: `src/packet.py:209-220; src/results.py:66-67`.

**Reproduction:** Set the intentional duplicate receipt exit_code=-9 with signal=None, or exit_code=999. Keep timeout/overflow false and the real duplicate argv. Both complete records pass.

**Root cause:** command_receipt checks only that exit_code has int type. The collision predicate treats any nonzero value as refusal. A signal-shaped or impossible normal process return is therefore accepted as expected manager refusal.

**Required correction:** Specify one recorder process-status encoding, enforce mutually consistent normal exit/signal fields and the valid normal exit range. Require evidence of expected collision rejection, preserving other failures as failures. Do not convert a killed client into a successful collision test.

Fresh failing methods: `test_duplicate_signal_exit_masquerades_as_refusal`, `test_duplicate_impossible_exit_code`.

## R3-A05 — MEDIUM: Executed-environment and receipt-operation contradictions are ignored

Source in the exact reviewed R3 packet: `src/packet.py:192-220; src/binding.py:65-68; src/proof.py:16-37`.

**Reproduction:** Add an explicitly untrusted synthetic environment to the create receipt, or label the timer show capture operation=install while leaving its show argv intact. Both contradictions are sealed and accepted.

**Root cause:** The proposed envelope has a minimal environment, but command_receipt only checks argv digest, status/output and elapsed time. Receipt environment is not required or compared and operation is not matched in observation/cgroup/collision paths. Open receipt schemas silently ignore contradictory fields.

**Required correction:** Bind actual execution to the reviewed operation/envelope and a minimal-environment policy attestation or digest. Use closed receipt schemas. Never log arbitrary real secret values; reject conflicting metadata without echoing it. The existing safe runtime-environment gate must remain intact.

Fresh failing methods: `test_command_receipt_untrusted_environment`, `test_receipt_wrong_operation`.

## R3-A06 — LOW: Global empty-namespace gate contradicts retained twelve-case procedure

Source in the exact reviewed R3 packet: `src/collision.py:25-29; src/catalog.py:17-18; CORRECTED-STAGE2-PROCEDURE.md sections 1,4,5`.

**Reproduction:** At the second trial, report the earlier owned success timer as retained in namespace_inventory and raw loaded-unit output. Admission blocks with namespace occupied/incomplete although the new target pair is absent.

**Root cause:** Every creation requires the entire Stage2 wildcard namespace and unit-file inventory to be empty. The same procedure retains elapsed/failed units, disallows deleting/resetting them, and requires all twelve final observations LoadState=loaded. The synthetic positive supplies empty wildcard output at every later creation without reconciling earlier retained units.

**Required correction:** Separate exact new-target absence from complete namespace inventory. Explicitly validate all already-owned prior pairs, or redesign retention/closure with a reviewed finite state machine. Foreign units must still block; do not solve this with wildcard stops or deletion of evidence.

Fresh failing methods: `test_later_namespace_must_allow_retained_owned_unit`.

The complete methods, logs and accepted-result hashes are retained under tests/fresh_probes.py and evidence/FRESH*. Each negative starts from the passing published synthetic seed, changes the stated field(s), synchronizes affected raw captures, and recomputes the full seal independently. This deliberately tests semantic consistency, not a SHA256 collision or externally signed evidence forgery. The originals and reviewed implementation are untouched.

No new HIGH-severity live-host vulnerability was established. Fresh real-host privilege/custody remains an essential unproven prerequisite. Exact systemd257 serialization and lifecycle behavior were not executed or inferred from mocks.
