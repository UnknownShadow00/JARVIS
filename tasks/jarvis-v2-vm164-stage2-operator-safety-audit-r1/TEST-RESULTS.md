# Independent test accounting

Actual safe invocation from the JARVIS project root:

```text
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r1/tests/run_audit.py
```

Exit status1 reports discovered safeguard gaps; the harness itself had no errors.
The reviewed source tests were imported unchanged and their normal evidence-writing
runner was not invoked. Python bytecode output was disabled. Process/network/
signal tripwires and a reviewed-tree write/mutation audit hook were active.

| Group | Run | Passed | Failed | Errors | Skipped |
|---|---:|---:|---:|---:|---:|
| Original tests |71|71|0|0|0|
| Independent controls |20|20|0|0|0|
| Independent safeguard-gap probes |10|0|10|0|0|
| Total |101|91|10|0|0|

Failed independent assertions map to findings as follows:

| Probe | Actual observed behavior | Finding |
|---|---|---|
| collision_input_string_must_be_rejected | Exact colliding service supplied as string still yields creation proposal |F03|
| cleanup_missing_boot_binding_must_be_rejected | Both boot fields absent still yield scoped stop argv |F04|
| cleanup_mismatched_current_name_must_be_rejected | Contradictory current name ignored if other copied fields match |F04|
| callback_outcome_missing_host_boot_must_be_rejected | Positive callback with no host_boot_id accepted |F05|
| rearm_a_firing_must_not_be_accepted_as_expected | Canceled-arm case accepts a successful fired callback |F05|
| reviewed_record_requires_operator_and_authorization | Reviewed-result structure accepted without these required bindings |F07|
| reviewed_record_requires_case_names_and_observations | Reviewed-result structure accepted without per-case identities/observations |F07|
| expected_negative_not_valid_for_ordinary_success | All cases, including ordinary success, may be called EXPECTED_NEGATIVE |F07|
| policy_read_has_preallocation_bound | Whole-file allocation occurs before the asserted size ceiling |F02|
| manual_decompression_has_streaming_bound | Whole decompression occurs before the asserted size ceiling |F02|

The final two are static command-body checks, not executions of large inputs or
host stress tests. Other probes use only synthetic in-memory records. No fixture
is presented as actual pve evidence. F01 and F06 are documented-interface/design
findings, not claims that pve uses external NSS or contains private environment
variables. The absence of a new test for those host facts is not a hidden skip.

Evidence:

- `evidence/reviewed-71-rerun.log`: all original test names/results.
- `evidence/independent-negative-probes.log`: controls and exact failing assertions.
- `evidence/TEST-RESULTS.json`: machine-readable totals, pins and verifier outputs.
- `evidence/INPUT-INVENTORY.json`: all29 preparation and96 R3 file byte hashes.
- `evidence/PRESERVATION-CHECK.json`: end-of-audit unchanged-tree result.
- `evidence/LOCAL-PRIMARY-DOCUMENTATION.json`: local manual paths/hashes/excerpts;
  different-version evidence, not systemd257 host qualification.

Both packet verifiers passed. Their historical294-test count is retained history,
not newly executed tests. Original source and evidence remained unchanged. Do not
rerun this harness in this sealed audit directory and overwrite these results;
use a new audit revision if repeating the run.
