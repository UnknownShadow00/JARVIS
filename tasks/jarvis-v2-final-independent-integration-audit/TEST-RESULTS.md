# Independent fresh results

| Suite | Pass | Fail | Error | Skip | Missing / incomplete | Gate / child exit |
|---|---:|---:|---:|---:|---:|---|
|coverage|217|0|0|0|0|0 / 0|
|reconciliation|66|0|0|0|0|0 / 0|
|r3|19|0|0|0|0|0 / 0|
|r2|45|0|0|0|0|0 / 0|
|original|32|0|0|0|0|0 / 0|
|existing|507|0|0|0|0|0 / 0|

Distinct required identities886. Seed16401. Seed42 repeats379, excluded from unique count. Both phase traces and identity sets were independently reconstructed in verify_independently.py without importing the engineering verifier/loader/application. VERIFICATION.json preserves trusted node IDs, source/Git tree bindings and both original/fresh results. The fresh run records rehearsal674aff2c; its266 input bytes match approved source da67d936. This is not a mislabeled rerun of old evidence.

EXECUTION.json records the exact fresh launcher command, cwd, timestamps and actual exit0; acceptance/RESULT.json records all14 child job commands/exits0. Per-suite JSON preserves complete setup/call/teardown, source hashes and counters. Fresh22 gate contracts,14 retained negative contracts and11 adversarial contracts all pass their expected outcomes. ATTACK-EXECUTION.json and attacks12/ preserve12 fresh attack replays; all12 reject/nonzero/no private marker leaks.

Additional-probes/SUMMARY.json preserves independently written six CLI probes: five reject despite child exit0 and one positive cleared-environment control completes217 cases. Those217 are supplemental repeats, not part of886 or379. Three report-copy tampering probes pass. A local replacement seal alone does not override the original pinned digest or execution invariants.

The before/after Astra31/45 reproduction and exact14 missing nodes are in VERIFICATION.json and acceptance/gate22/. Every intentionally negative JSON/log is retained. PASS on a contract summary means its expected rejection/control behavior was observed, not that the deliberately incomplete suite passed.

Evidence is new and stored outside both original and fresh read-only snapshots. No excluded/live suite supplies positive evidence. The two snapshots and reviewed source still match after all probes; see POST-CHECKS.json.
