# Result and evidence format

`templates/LIVE-RESULT.json` is unfilled, NOT_RUN and not authority. Do not replace
this template with fixture output. A future capture is a new separately retained
file with kind `CAPTURED_STAGE2_LIMITED_RESULT`. `src/results.py::validate` is a
pure structural check; it cannot verify authenticity, authorization, policy
completeness or the actual host. It grants no execution permission.

Required records:

- Session: operator/reviewer, approval reference, packet manifest digest, source
  pins, nonce, host boot ID, UTC start/expiry, initial BOOTTIME and offset bounds.
- Fresh host evidence: each fact references raw artifacts with capture sequence,
  UTC/boot timestamps and SHA256. Keep reported facts distinct from measured facts.
- Per command: sequence, exact argv array and canonical argv SHA256; before/after
  clock records; stdout/stderr artifact paths; actual exit code or signal;
  timeout/overflow/acknowledgment-unknown flags. Canonical argv is UTF-8 JSON with
  sorted keys, compact separators and no NaN (array order preserved).
- Per case: name pair, absolute deadline, consumed/pending/owned disposition,
  actual states/results, callback JSON, raw journal correlations, invocation ID,
  measured latency, raw show snapshots twice while waiting and after firing,
  selected-property parser result/refusal, reason for any expected/unexpected
  failure, cleanup evidence and independent disposition.
- Artifact references have exactly `path` (relative within capture, no `..` or
  symlink escape), `sha256` (64 lowercase hex), `bytes` (nonnegative integer).
  Reviewers independently rehash actual bytes; a listed digest is not proof.
- Cleanup: owned name inventory, per-half terminal/raw evidence, empty cgroup/no
  job proof, retained callback and installation receipt, incomplete/orphaned
  entries. Never drop a failed name from this list to claim closure.

Case statuses: NOT_RUN, UNKNOWN, FAIL, EXPECTED_OBSERVATION, EXPECTED_NEGATIVE,
EXPECTED_LATE_REJECTED_NOT_TIMING_PASS, CREATION_REFUSED_EXEC_NOT_OBSERVED,
LIVE_FAILED_TIMER_STATE_UNOBSERVED. Unobserved requirements stay unresolved.
`EXPECTED_NEGATIVE` requires reviewer-confirmed raw evidence for collision,
inactive, failedtimer or cancellation; it is not a substitute for missing state.

Final results: INCOMPLETE, FAILED or LIMITED_OBSERVATIONS_REVIEWED. The last
requires independent signoff, known clock domain/basis, every case actually
accounted for with expected observations, and CLOSED_EVIDENCE_RETAINED. Even then
`live_qualification=false` denotes **no blanket R3 host qualification** and
`expiration_guaranteed=false` always. Manager-reexec, host-reboot, physical wake,
VM termination and root bootstrap remain in `unqualified`. Individual limited
awake-host facts may be recorded separately with evidence, never promoted into
all R3 prerequisites. `stage2_authorized` refers to a recorded later operator
decision only, never to this template or these offline tests.

`evidence/OFFLINE-RESULTS.json` is the actual fixture test run from this task. It
has a distinct kind, no host commands and no live claim. `MANIFEST.json` inventories
this preparation packet; `SEAL.json` records its digest. These hashes detect
accidental changes, not malicious root rewriting or independent provenance.
