# Committed baseline verification

PASS for byte identity, commit scope, clean checkout and expected rejected-R2 behavior.

```text
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-r2-provenance-recovery-r1/tools/verify_baseline.py '/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-stage2-r2-provenance-baseline-r1' 5088a240943f2d39b67ca7d528ea8e5f7e51d6f9
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-r2-provenance-recovery-r1/tools/replay_checkout.py baseline
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-r2-provenance-recovery-r1/tools/replay_checkout.py r2
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-r2-provenance-recovery-r1/tools/replay_checkout.py negative
```

These are local offline commands only. The negative runner must exit 1 with the exact sixteen recorded failures; it is not a positive qualification gate. Baseline and r2 runners exit zero while explicitly counting the expected original-candidate failures. The replay wrapper pins and loads the committed independent harness, redirects only output/source-root routing and one legacy fixture read, then uses the reviewed assertions unchanged. Its inherited guards block process execution, network, signaling, NSS, host/private paths and writes outside the recovery packet. A supplementary guard rejects canonical source reads. Tests never run proposed live command bodies.

Before and after test execution, verify_baseline.py checked clean status, exact HEAD and parent, independent audit anchor and payloads, all reviewed files against independent SHA256s, exact 94 changed paths, committed blob equality and executable bits. Evidence is BASELINE-INTEGRITY-BEFORE.json and BASELINE-INTEGRITY-AFTER.json. CHECKOUT-ORIGINS-*.json lists actual imported worktree files and the single fixture redirection.

The unchanged preparation/R2 verifiers pass. Sealed Host Enforcement R3 verification rebuilds the archive identically and verifies the 247 predecessor files, five literal symlinks and original task-log prefix. Its retained count of 294 historical methods is not a new execution count. Its historical success labels do not override Astra's rejection of Stage 2.

R2's retained twelve-case synthetic record still passes the old validator. The independent 51-probe suite still proves sixteen unsafe acceptances, with failure names exactly equal to the reviewed audit (KNOWN-FAILURE-EQUALITY.json). This is the intended unchanged baseline.

The first attempt's two extra failures and two runner exceptions are retained and explained in TEST-RESULTS.md. They were caused by checkout representation and the added wrapper, not altered reviewed source. Final replays use the identical commit and test assertions.

SHA256SUMS covers regular recovery files, excluding itself. Retained synthetic fixture symlink text is sealed through evidence/RETAINED-FIXTURE-LINKS.json instead of dereferencing it. Both first-attempt residual fixture trees are retained; they are never treated as host evidence.
