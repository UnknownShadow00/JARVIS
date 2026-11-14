# Independently executed test results

| Suite / target | Executions | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|---:|
| Original preparation71, unchanged source |71|71|0|0|0|
| Original independent audit30 against R1 |30|20|10|0|0|
| R2 design3 against original catalogue |3|0|3|0|0|
| Original audit30 assertions against R2 |30|30|0|0|0|
| R2 design3 against R2 |3|3|0|0|0|
| R2 regression92 |92|92|0|0|0|
| New independent R2 probes |51|35|16|0|0|
| **Final campaign executions** |**280**|**251**|**29**|**0**|**0**|

The29 failures comprise13 reproduced original-candidate failures and16 newly detected R2 safeguard failures. The original13 are expected for baseline confirmation; the16 R2 failures are unresolved defects and drive REJECT. No assertion was weakened or marked expectedFailure to produce a green result.

There are **247 distinct test methods**, counting original audit/design methods only once across their red/green targets:196 reported engineering methods plus51 independent methods. On their applicable retained/corrected targets, the196 engineering methods do pass. The247-method applicable-target view is231 pass/16 fail, zero errors/skips. Repeated development runs are not added to these totals.

R2's published complete synthetic12-case record was separately loaded from its actual twelve artifact files through its artifact loader, rehashed and validated. It returns PASS_SYNTHETIC_ONLY as reported. That is one additional artifact validation, not twelve additional test methods and not host qualification. Original preparation, R3 and R2 integrity verifiers pass. R3's retained294 historical tests are not newly executed here.

## Reproduction commands used

From the canonical JARVIS root, only these safe local replay processes were run:

```text
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2/tests/replay.py baseline
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2/tests/replay.py r2
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2/tests/replay.py negative
```

Baseline and R2-replay commands exit0 after retaining the expected original failures. The independent-negative command exits1 for the16 discovered failures. Exact names, tracebacks and machine totals are in evidence/BASELINE-RESULTS.json, R2-RESULTS.json, NEGATIVE-RESULTS.json and their logs. ACCEPTED-COUNTEREXAMPLES.json records the unexpected acceptance outputs and per-case digests for the applicable semantic probes; the two input/renderer probes and root-path probe are fully reproduced in test source/logs.

The existing R2 tests/run.py and tests/reproduce.py were read but not executed in their reviewed folder because they write evidence there. Their test modules were imported unchanged by the new harness. Audit30 R2 replay uses the documented R2 fixture migration and plain-dictionary cleanup boundary, exactly as the engineering claim specifies; no original test method is modified. New independent probes use the published synthetic artifact as a seed and their own mutation/serialization helpers, not engineering outcome helpers to determine the expected assertions.

## Safety and coverage

The harness prohibits child-process/network/signaling/NSS calls and actual private/host-identity path reads, and denies mutation outside the new audit directory. Temporary test files are confined there. Bounded read/gzip tests use small disposable files/bytes, simulated allocation failure and deadlines; they do not exhaust host memory or apply process resource limits. Future Python command resource ceilings are inspected, not tested on pve. The one executed command-validator fragment is only R21's pre-open lexical check with a synthetic `/` argument; no host file is opened.

Independent controls cover network/ambiguous NSS, missing policy/environment prerequisites, file size checked before read, malformed/truncated/concatenated gzip bombs, partial reads, memory/deadline failure, symlink evidence, declared resource/command caps, explicit timeout/missing elapsed/expiry refusal, malformed collision names, wrong pair/boot/eUID/generation, fired canceled callback, missing clock/cleanup, active units, foreign/repeated/interrupted cleanup, untrusted environment, artifact tampering and actual wrong success exit. The16 failures cover remaining chronology, cancellation, collision, state/exit, seal/raw-evidence and root-path defects.
