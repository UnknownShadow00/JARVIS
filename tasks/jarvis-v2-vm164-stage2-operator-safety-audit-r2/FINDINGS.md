# Remaining defects and independent reproductions

All probes operate on disposable data copied from R2's published SYNTHETIC-12-CASE.json. No reviewed file is modified. Unless stated otherwise, affected case bytes and manifests are recomputed before validation; the expected result is still BLOCKED because the data are contradictory or incomplete. A correct digest does not make the observations valid. The full51-test source and failure traces are retained under tests/ and evidence/.

All confirmed validator defects below are **MEDIUM severity, blocking authorization readiness**: they can falsely approve qualification evidence or admit a proposal without the required fresh proof. They do not demonstrate root escalation, VM actuation or a live incident. The root-path defect is **LOW severity operational completeness**, also blocking this exact procedure. Unproven live privilege/custody prerequisites remain high-risk admission conditions, not newly observed host vulnerabilities.

## R2-A01 — MEDIUM: evidence chronology and freshness are not cross-bound

Sources: R2 `src/binding.py:52` (capture validation), `src/binding.py:180` (journal parser), `src/results.py:44` (waiting/final observations), `src/results.py:51` (journal receipt), `src/results.py:59` (mutation receipts), `src/results.py:91` (collision).

`verify_pair` compares a claimed observed_boot_us to the outer sample, but never binds the timer/service receipt samples to that observation interval. `results.validate` checks each receipt fits the overall authorization window, not the sequence it purports to prove. Journal coverage endpoints are assertions unrelated to the capture receipt; the parsed journal monotonic stamp is assigned then discarded.

Failing probes:

- `test_stale_show_receipt_must_not_prove_current_cleanup`: final sample at session+1000s, raw-show receipts at+121s; record still passes.
- `test_old_cancellation_journal_must_not_prove_no_late_firing`: rearm-a empty journal receipt at creation+1s, before cancellation/deadline; coverage still asserted through closure and accepted.
- `test_creation_receipt_after_deadline_must_fail`: success creation receipt+170s, scheduled deadline+150s, waiting observations+121/+122s; accepted despite impossible ordering.
- `test_duplicate_after_firing_must_not_pass_waiting_collision`: duplicate receipt D+10s while before/after waiting snapshots remain earlier; accepted.
- `test_journal_timestamp_before_session_must_fail`: trusted __MONOTONIC_TIMESTAMP set to0 while public payload clocks remain fresh; accepted.

Correction criteria: bind every capture to its actual start/end bracket and raw stdout; enforce ordered creation, waiting, duplicate/refusal, callback/exit, stop and final capture. Normalize and compare journal timestamp domain to the measured clock offset and payload/window. A journal captured before a purported coverage endpoint cannot prove that endpoint. Require explicit complete capture/cursor provenance, not a later timestamp label.

## R2-A02 — MEDIUM: cancellation and late-result predicates do not enforce action/window timing

Sources: R2 `src/binding.py:164`, `src/results.py:59`, `src/results.py:95`, `src/packet.py:269` (outcome).

The cancellation predicate checks cancel_boot_us but does not tie it to either stop receipt. The late predicate has a lower lateness bound but no upper relationship to authorization expiry, service runtime or final capture. Cancellation allows an unexpected failed/resources service with no recorded invocation to count as expected cancellation.

Failing probes:

- `test_stop_receipt_after_deadline_must_fail_cancellation`: claimed cancel at D−25s remains; both stop receipts moved to D+10s; accepted.
- `test_canceled_service_failure_must_not_be_expected_cancellation`: rearm-a final service failed/failed with Result=resources is accepted as EXPECTED_NEGATIVE.
- `test_late_callback_after_authorization_expiry_must_fail`: late canary BOOTTIME at session+2800s and matching MONOTONIC, exceeding the2700s grant and final capture+1000s; accepted as expected-late rejection rather than a failed out-of-window result.

The original direct `outcome('rearm-a', successful_callback)` false positive is fixed and reproduced as blocked against R2. Wrong-generation guard and wrong UID/boot controls also pass. These do not establish absence of a late canceled invocation when capture chronology is invalid.

Correction criteria: derive cancellation timing from acknowledged exact-unit stop receipts/checkpoints and their end clocks; require them before D−5s. Preserve and reject unexpected failure states even without a callback. Bind every callback and journal event to the approved window and capture chronology; the intentional2s delay does not permit arbitrary or post-expiry execution. Require A's proven cancellation before B's creation and continued A coverage through B closure.

## R2-A03 — MEDIUM: collision admission can use stale or timed-out evidence

Sources: R2 `src/render.py:16`, `src/collision.py:6`, `src/results.py:40`.

The renderer validates collision evidence at its own sample and a plan at a different current sample. It does not enforce their freshness relationship. Its subsequent freshness call compares a freshly generated deadline to the same new sample, so cannot detect old collision evidence. The final result validator has a stronger creation-sample equality check, but it runs after the proposed action and cannot repair pre-admission checking.

Failing probes:

- `test_renderer_must_reject_stale_collision_proof`: collision proof at+120s, proposal sample+180s. `render.main` prints an admitted proposal/envelope rather than refusing. Only the offline renderer is invoked, never the emitted command.
- `test_collision_proof_timeout_must_fail`: an exact-name absence row has show_exit=1 and explicit timeout=true; `collision.absent` still returns true. No command receipt/timeout evidence is required by that row schema, and the contradictory field is ignored.

Original string/dict/null/duplicate/wrong-name occupancy controls now pass. Native systemd collision refusal remains an additional necessary barrier; none was tested live.

Correction criteria: require exact bounded command receipts for every collision read, complete UnitPath/namespace/file capture evidence and explicit timeout/overflow rejection. Bind collision capture age and boot to the current action and plan deadline before emitting argv. Unknown/extra contradictory status fields must not be discarded. Keep native refusal and never stop a foreign collision.

## R2-A04 — MEDIUM: failed states and contradictory exits can be reported as expected results

Sources: R2 `src/binding.py:44` (ExecStart trailer), `src/binding.py:81` (state combinations), `src/binding.py:126` (terminal states), `src/results.py:77` (failedtimer), `src/results.py:89` (outcome).

Raw state, ExecStart trailer, main-process exit and case disposition are checked separately without complete consistency. Failedtimer only proves no invocation in an earlier failure observation; a later final service invocation is not rejected.

Failing probes:

- `test_service_failed_state_cannot_be_success`: success final service ActiveState/SubState=failed/failed while Result/ExecMain fields claim success; accepted.
- `test_execstart_exit_disagreement_must_fail`: success raw ExecStart trailer code=exited/status=7 contradicts main status0; accepted.
- `test_failedtimer_later_service_invocation_must_fail`: final failedtimer service has InvocationID, Code1/Status7/Result=exit-code after the earlier no-invocation failure snapshot; accepted.

Correction criteria: define case-specific coherent state/result/exit/trigger/invocation matrices, parse execution status fields rather than matching only their shape, and enforce no invocation across the entire failedtimer/canceled interval including final closure. Preserve expected exit7 and timeout failures as expected observations without permitting unrelated failures.

## R2-A05 — MEDIUM: raw cleanup evidence and the full reviewed-result seal are incomplete

Sources: R2 `src/binding.py:126`, `src/results.py:18`, `src/results.py:25`, `src/artifacts.py:8`.

Final cgroup checks accept a summary with path, populated=0, pids=[], complete=true and absent=false, without the raw cgroup.events/cgroup.procs command bytes, exit, timing or independent absence receipt. The published positive fixture lacks these raw records for all twelve cases and still passes. Separately, the external manifest seals only case artifacts; top-level identity review references are not covered or bound back to a case/session-specific review artifact.

Failing probes:

- `test_missing_raw_cgroup_capture_must_fail`: the complete published fixture, with no raw cgroup capture for any final observation, is accepted.
- `test_changed_privilege_review_requires_new_external_seal`: replace identity.vm_authority_absent_review with a different syntactically valid digest; retain every case file and the original independent case-manifest seal. Acceptance is unchanged.

This is not a SHA256 break. Hash/byte tampering within sealed case files is correctly rejected. It is incomplete seal coverage and missing raw evidence categories. All review hashes still require authentic independent custody; adding a hash field is not a live permission proof.

Correction criteria: require and parse bounded raw cgroup/process receipts or exact corroborated absence proof; bind their time/unit/boot to closure. Seal the complete reviewed-result envelope, including identity/policy/environment/clock-basis references and failure/consumed-generation ledger. Require referenced review artifacts to be present, hashed and bound to the same session, not merely64 hexadecimal characters.

## R2-A06 — LOW: mandatory root-ancestry command rejects the root path

Sources: R2 `src/inspection.py:17`, CORRECTED-STAGE2-PROCEDURE.md step1.6 and step2.

`METADATA_BODY` requires every component in `path.split('/')[1:]` be nonempty. For `/`, that list is `['']`, so the mandatory R21 `/` inspection raises BLOCKED: canonical path before any open/stat. No documented exact fallback replaces it.

Failing probe: `test_metadata_command_must_support_required_root_path`. Only the literal pre-open lexical validator is evaluated with a synthetic argv; no root path is read and no resource limit is applied.

Correction criteria: in a new revision, explicitly support metadata inspection of the already opened root directory, and test `/`, normal directory/leaf, symlink and missing-ancestor cases. Retain fail-closed no-follow/custody behavior. This failure prevents completing preflight as written; it does not cause a live privilege escalation.
