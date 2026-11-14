# Six-group security reassessment

**REJECT.** Exact historical regressions pass, but four group-level contracts remain incomplete under fresh adversarial inputs. These are qualification-assurance defects; no host compromise, privilege escalation or VM actuation is demonstrated.

| Original group | Verdict | Reason |
|---|---|---|
| R3-A01 | FAIL | The four exact completion probes pass; raw exit-row invocation contradictions remain accepted (R4-A02). |
| R3-A02 | FAIL | The three never-invoked field probes pass, but accepted guard intervals overlap that waiting state (R4-A01). |
| R3-A03 | FAIL | All three exact probes pass; guard-start/creation/trigger chronology still has counterexamples (R4-A01). |
| R3-A04 | PASS | Malformed/crashed/unrelated collision receipts reject; exact refusal and unchanged state required. Real diagnostic grammar remains unqualified. |
| R3-A05 | PASS | Closed operation/env/actor/pair/boot/session receipts reject tested conflicts and omissions; no weakened inherited environment protection found. |
| R3-A06 | FAIL | Valid owned prefix now admits and foreign/active/partial histories reject, but complete retained journal proof loses required diagnostics (R4-A03). |

## R4-A01 — MEDIUM: Guard execution can predate creation, waiting and timer firing

Sources: `src/lifecycle.py:78`, `src/lifecycle.py:86`, `src/lifecycle.py:107`, `src/proof.py:107`.

Set both completion/final ExecCondition start_time to D-60s, D-28.5s, D-1s or D-6s, retaining guard completion at D+5ms, main start at D+10ms and guard output at D+1ms. Full validation accepts. A separate first-case verified_anchor accepts the D-60s start.

Root cause: The parser brackets guard output by its own interval and orders guard end before main start, but never orders guard start after creation, last never-invoked waiting capture, or trigger; it does not constrain the guard duration to the proposed start budget.

Impact: Mutually exclusive NEW/WAITING/EXECUTING states can describe one accepted generation; a stale guard can yield an admissible completed-case anchor.

Required correction: One causal state graph must bind guard launch after timer creation/last never-invoked capture/qualified trigger, with conservative same-domain bounds and a qualified finite start-duration rule. Share that gate for per-case admission, retention and final closure.

Failing probes:

- `fresh_adversaries.NewGaps.test_guard_exceeds_reviewed_start_timeout`
- `fresh_adversaries.NewGaps.test_guard_started_before_timer_creation`
- `fresh_adversaries.NewGaps.test_guard_started_before_timer_trigger`
- `fresh_adversaries.NewGaps.test_guard_started_during_never_invoked_waiting`
- `fresh_adversaries.NewGaps.test_stale_guard_accepted_for_completed_case_anchor`

## R4-A02 — MEDIUM: Plain journal records bypass invocation and sender attribution

Sources: `src/binding.py:188`, `src/binding.py:207`, `src/proof.py:244`, `src/lifecycle.py:96`.

Append a correctly timed exit0 plain row labelled as UID65534 service output but with malformed or prior-generation _SYSTEMD_INVOCATION_ID, or _SYSTEMD_UNIT=foreign.service plus UNIT=current-owned-service. Full validation accepts after matching the raw receipt and resealing.

Root cause: Only JSON MESSAGE records become bound invocation events. Plain records take an OR over unit fields and ignore present invocation identity; journal_consistency checks message/code/status and UID only.

Impact: A favorable exit message can coexist with contradictory raw generation/unit attribution and still produce PASS_CONSISTENCY_ONLY/PASS_SYNTHETIC_ONLY.

Required correction: Define supported manager-versus-service journal record classes using documented fields. Reject contradictory present attribution, malformed invocation IDs and unrelated senders; do not require a service invocation field universally on legitimate PID1 manager records.

Failing probes:

- `fresh_adversaries.NewGaps.test_plain_exit_conflicting_unit_fields`
- `fresh_adversaries.NewGaps.test_plain_exit_malformed_invocation`
- `fresh_adversaries.NewGaps.test_plain_exit_prior_generation_invocation`

## R4-A03 — MEDIUM: Retained journal completeness excludes plain diagnostic records

Sources: `src/retention.py:19`, `src/retention.py:44`, `src/binding.py:188`.

Remove the required ModuleNotFoundError plain row from retained missingdep history in rearm-b admission. Preserve original completed case, existing anchor and ledger. Both collision.absent and complete result validation accept the truncated fresh full-journal readback.

Root cause: Anchor events_sha256 hashes selected JSON payload events only. No anchor binds the immutable raw journal prefix/cursors/plain rows, and retained validation does not require previously proved diagnostic rows.

Impact: A current claimed complete journal can omit known historical raw evidence without triggering FAIL/BLOCKED, despite the independently sealed anchor.

Required correction: Bind complete immutable journal evidence (including plain records and cursor/record identity) into prior anchors; require monotone preservation across subsequent full captures, with an explicit fail-closed policy for journal rotation/truncation. Do not delete or silently reseal missing records.

Failing probes:

- `fresh_adversaries.NewGaps.test_retained_journal_loses_diagnostic_at_admission`
- `fresh_adversaries.NewGaps.test_retained_journal_loses_required_diagnostic`

Earlier safeguards remain in the code and pass their inherited checks: local-only NSS/sudo gate, bounded preallocation/decompression, explicit command caps, numeric nonroot callback/guard, minimal environment, exact source/callback/boot/generation pins, scoped cleanup, fail-closed expiry and no VM/guest bootstrap permission. Eight inherited modules remain byte-identical to R3. This retention of safeguards does not cure the newly demonstrated evidence contradictions.

