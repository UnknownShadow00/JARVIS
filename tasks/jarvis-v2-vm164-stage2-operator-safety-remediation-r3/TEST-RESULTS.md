# Baseline replay only — no R3 after-fix results

| Executed target/suite | Tests | Pass | Fail | Error | Skip |
|---|---:|---:|---:|---:|---:|
| Original preparation |71|71|0|0|0|
| Original audit against rejected R1 |30|20|10|0|0|
| Original design checks against old catalogue |3|0|3|0|0|
| Previous audit against unchanged R2 |30|30|0|0|0|
| R2 design checks |3|3|0|0|0|
| R2 regression suite |92|92|0|0|0|
| Latest independent probes against unchanged R2 |51|35|16|0|0|
| **Replay executions** |**280**|**251**|**29**|**0**|**0**|

There are247 distinct methods, with the30 audit and3 design methods counted only once across targets. The29 assertion failures comprise13 reproduced original-candidate failures and16 current R2 defects. R2's95 regression/design methods all pass, but do not establish the missing safeguards. The latest16 failure names exactly match the sealed rejection audit. These are preserved before-fix failures, not successful R3 regression results.

The R2 published synthetic12-case record was independently loaded/rehashed and passes its existing consistency validator. It remains explicitly synthetic and is known to lack the rejected checks. Original/R2 integrity verifiers pass; R3 predecessor archive/chain verification passes. Their retained historical test totals are not additional executions.

R3 candidate suites, new R3 adversarial tests, after-fix16-probe acceptance and complete R3 twelve-case validation are **NOT RUN / BLOCKED**, not unittest skips. Zero test skips does not mean these mandatory gates were completed. No fixes or new implementation were supplied because the required source commit is unavailable.

Commands run locally from canonical JARVIS root:

```text
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r3/tests/replay.py baseline
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r3/tests/replay.py r2
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r3/tests/replay.py negative
```

The two scripts are unchanged copies of the independent audit harness and probe source. Only their new location redirects output/temporary fixtures into this task directory. Original assertions, test semantics and historical output files were not edited. The negative replay exits1 with16 failures, as required for honest baseline preservation. No future host command body was executed; the R21 probe evaluates only the original pre-open lexical rule using synthetic input.
