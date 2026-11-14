# Independent reproduction methodology

The untouched original Astra R2 tests/replay.py negative phase was run first in a disposable copy, importing the original51-method source:35 pass/16 fail, exit1, no errors/skips. This is new execution, not a quoted engineering count. tests/ORIGINAL-ASTRA-PROBES.py preserves that exact source; its digest is in ORIGINAL-R2-PROCESS.json.

Then the339 reported methods were replayed against applicable sources: original71; prior audit30 via existing compatible fixtures; R2 design3+regression92; latest engineer-port51; new engineer92. All339 pass. Independent inspection verifies original assertion-call ASTs in the engineer51/92 ports match their originals. Fixture adaptations are disclosed; no assertion was relaxed. The published twelve-case artifact passes the pure validator and actual bounded artifact loader, but this is parser consistency, not operational feasibility or live evidence.

A separate independent replay imports the untouched original Astra methods against R3 modules, substitutes the published valid R3 seed, uses an independently implemented complete sealer, and adapts only two old-fixture-specific mutations. All51 pass, including all16 prior defects. The positive control passes through the full validator. Every result-validator call/rejection is recorded. Root lexical and collision-renderer probes exercise their actual entry points, rather than substituting a mocked pass. This replay does not count51 new logical methods.

Fresh probes were independently authored around incomplete cross-observation checks found in source inspection. Final39 methods yield24 pass/15 fail, zero errors/skips, exit1. Fourteen negative inputs are accepted as PASS_SYNTHETIC_ONLY; one positive input required by the procedure (an earlier retained owned timer) is incorrectly blocked. Exact method names and tracebacks are in FRESH-RESULTS.json/FRESH.log; mutations are in tests/fresh_probes.py. The known passing seed is retained as SYNTHETIC-SEED.json. The sealer recomputes all command/envelope/case digests so these tests exercise meaning, not damaged hashes. No live data or credentials are used.

Additional controls cover coherent late creation/stale capture/late cancellation receipts/post-expiry callbacks, correctly bound canceled callbacks, absent effective inactivity, failed/partial cleanup, wrong boot, wrong generation, duplicate raw properties, leaked cgroup processes, missing review inputs, network/ambiguous NSS, untrusted runtime environment, oversized/truncated input, gzip expansion and expired read deadlines. These reject. The new failures are enumerated in SECURITY-FINDINGS.json and are not weakened or marked expectedFailure.

Safety harnesses deny subprocess/network/signaling and NSS functions during tests, block private host-path reads and limit writes to disposable/audit artifacts. Actual command strings, timer code and installer are inspected/rendered only. R21 uses lexical/fake-filesystem tests. Outer standard-library orchestration starts only local isolated Python test processes with finite timeouts. No package/provider/API call occurs.

For reproducibility, use a new disposable copy of this audit folder and the pinned reviewed task trees. Set that copy's evidence/WORKSPACE.json disposable_copy to the new task-copy root; keep reviewed Git sources immutable. Run:

```text
python3 -I -B -S <DISPOSABLE_AUDIT>/tests/run_original_against_r3.py
python3 -I -B -S <DISPOSABLE_AUDIT>/tests/run_fresh.py
```

The first exits0; the second must exit1 with the15 retained failures. Existing copied R3 tests/replay_after.py phases baseline/r2/negative/adversarial reproduce reported suites; copied preceding audit-r2/tests/replay.py negative reproduces historical16 failures. The sealed Host Enforcement verifier also requires its tracked earlier bootstrap/readiness folders and task-log prefix. Exact actual invocations/exits are in evidence/*PROCESS*.json. Do not run writing replay scripts in the reviewed worktree or overwrite sealed audit evidence. No live command is part of reproduction.
