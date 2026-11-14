# Exact offline test results

All tests use local standard-library fixtures/file reads and temporary test files. Process launch, network sockets, os.system and signaling are trapped in the replay harness. Guard execution is only in-process with mocked clock/identity/environment/boot-file reads; it does not inspect pve or activate a service. Generated command bodies are compiled or inspected, never run. Bytecode generation is disabled.

| Group | Unique assertions in group | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|---:|
| Original preparation suite, unchanged, against sealed preparation source |71|71|0|0|0|
| Original audit probes, unchanged, against rejected R1 |30|20|10|0|0|
| Additional design regressions against original catalogue |3|0|3|0|0|
| Same original30 audit assertions against R2 |30|30|0|0|0|
| Same3 design assertions against R2 catalogue |3|3|0|0|0|
| New R2 regression suite |92|92|0|0|0|

There are **196 distinct test methods**:71 original,30 audit,95 new. The baseline/red and R2 replays are not additional unique tests. The final reported six-group campaign has229 executions:216 passes and13 deliberate reproduced safeguard failures on the original candidate, zero errors/skips. These are actual assertion failures retained in the original-red logs, not weakened assertions or expectedFailure decorators. Repeated development runs are not counted again. All applicable final offline gates pass: original71 retained, corrected audit30, new95.

The original ten failed audit methods exactly match the rejection: malformed collision string; cleanup missing boot; cleanup wrong current name; callback missing host boot; fired rearm-a accepted; missing operator/authorization; missing case bindings; ordinary success accepted as expected-negative; preallocation policy-read bound; streaming decompression bound. Additional original-red design assertions expose NSS/sudo calls, absent complete command-cap categories and incomplete environment assignments. All pass against R2.

Replay adaptation is explicit in tests/run.py and tests/fixtures.py: original test method source is imported unchanged; R2-positive identity/session/ownership fixtures carry the newly required fields. The old fixture's states assignment updates synthetic raw show state. A dictionary conversion represents its serialized wire form before invoking the unchanged production cleanup predicate. No negative assertion or expected result is changed. Additional R2 tests mutate otherwise complete records to avoid relying only on missing-new-context rejection.

New coverage includes files/gzip size, truncation, malformed payloads, decompression bombs, MemoryError, early timeout, partial reads and metadata changes; local NSS network/ambiguous sources, groups/policy/manager/runtime environment; namespace/consumed-generation/collision proof; all twelve outcomes, wrong UID/boot/generation/raw pairing, missing/duplicate callback, interrupted/duplicate cleanup, remaining active/process state, expired cleanup, wrong statuses, unknown clocks, manifest/file tampering, journal selection/epoch, and non-root guard expiry/UID/environment/boot rejection. The complete positive synthetic12-case record is independently validated, and its actual artifact bytes are retained.

Commands executed **offline only**, from this new packet in the isolated worktree:

- `python3 -I -B -S tests/reproduce.py` — baseline71/audit30 and original integrity verifiers.
- `python3 -I -B -S tests/run.py` — original-red design checks, corrected audit30/design3/regression92; exits nonzero for any unexpected green failure/error/skip.
- `python3 -I -B -S tools/build_artifacts.py` — inert catalogue, templates, synthetic artifacts and validation result.
- `python3 -I -B -S src/verify_packet.py` — after sealing, read-only packet/predecessor/source/first-action checks.

Logs and structured totals are in evidence/. The R3 verifier's historical294 tests are retained history, **not additional executions here**. Prior preparation29, R396 and audit15 files are checked byte-for-byte against the start inventory. Existing R3 source/callback pins and predecessor-chain verification pass. No successful synthetic test establishes systemd257 behavior, authentic operator evidence or guaranteed expiration.
