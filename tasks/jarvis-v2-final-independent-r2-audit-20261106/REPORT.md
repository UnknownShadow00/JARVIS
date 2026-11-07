# Final independent R2 security audit

**Verdict: REJECT.** Scheduler ownership and report redaction corrections pass within the tested offline boundary. The false-PASS finding remains open: collection-level skips can silently remove a required suite while the gate exits successfully.

Reviewed commit `b199acede69962919933d5bca364a587b1a2e8ca`, branch `codex/jarvis-v2-reliability-hardening-r2`, exact parent `e310e587188f6802ea8a3301d49cb796ad9788a8`, original RC1 `e9b4734740070b9e7c990735e43801e592c114c6`. Target worktree was clean before and after review. No reviewed source or commit was modified. Audit artifacts are isolated in the canonical JARVIS task directory; only its required completion log is additionally appended.

| Original Astra finding | Verdict | Independent assessment |
| --- | --- | --- |
| R1: asynchronous scheduler cleanup loses ownership | PASS | Installed APScheduler 3.11.3 cleanup failure, retained ownership, partial-resource retry, cancellation, timeout, repeated shutdown and restart fencing verified. This qualifies the default coroutine executor/memory-store path only. |
| R2: incomplete tests can produce false PASS | FAIL | Original setup-only early exit is corrected, but skipping a required module during collection still yields PASS/exit0. |
| R3: exception payload leaks into machine reports | PASS | Original leak corrected. Injected exception messages, dynamic types, parameter IDs and collection failures do not export synthetic secret text; failures remain nonzero. |

## Blocking finding — P2: collection-level skip is invisible to the release gate

Locations: `scripts/reliability_gauntlet.py:49`, `:98`; `scripts/gauntlet_protocol.py:87`.

The collector records only failed collection reports, ignoring `report.skipped`. Its expected inventory is derived from items remaining after collection. A module skipped with `pytest.skip(..., allow_module_level=True)` or `pytest.importorskip(...)` contributes no test items. If another selected module passes, both the expected inventory and pytest count shrink together; their agreement does not demonstrate that all required suites ran.

Independent reproduction used a disposable public-source copy, replacing only `tests/test_scheduler_hardening_r2.py` with:

```python
import pytest
pytest.skip('AUDIT_SYNTHETIC_SECRET_COLLECTION_SKIP', allow_module_level=True)
```

Running the unmodified candidate CLI with `--r2` produced **PASS, exit0, collected31, executed31, PASS31, SKIP0, INCOMPLETE0**. Fourteen required cases disappeared. All session success booleans were true, and the collection-error flag was false. Reproduced twice (`collection-skip.json`, `collection-skip-repeat.json`). No hostile plugin or fabricated completion report is needed; optional-dependency module skips are ordinary pytest behavior.

Required correction: make collection skips and missing required-suite coverage explicitly nonpassing. Validate required collection coverage as well as phases for surviving items; include module/package skip/importorskip, partial selection/deselection and collection interruption regressions. Preserve redaction: export safe collection status/counts, not skip reasons or arbitrary node text. The gate must return nonzero when any required suite is skipped. Do not merely hardcode 45 as a substitute for collection evidence.

`run_supplemental.py` reproduces this and the additional independent probes using temporary copies and the existing namespace runner. To repeat, copy its two Python files into a fresh output directory, since report files use exclusive creation.

## Independent execution results

All application/test execution used the inspected ordinary bwrap parent CLI: networkless namespaces, public source and existing dependencies mounted read-only, cleared environment, disposable SQLite/scratch, no host credentials or privileged operations.

| Execution | Result | Exit |
| --- | --- | --- |
| Candidate R2 suite | 45 pass, 0 fail/error/skip/incomplete | 0 |
| Original Gauntlet | 32 pass, 0 fail/error/skip/incomplete | 0 |
| Existing 24-suite selection | 507 pass, 0 fail/error/skip/incomplete | 0 |
| Authentic negative CLI contracts | 14/14 expected contracts satisfied; each nested gate nonzero | checker 0 |
| Before/after contracts | 3/3 satisfied | checker 0 |
| Original Astra real-backend ownership probe on R1 | 1 fail as expected | 1 |
| RC1 baseline replay | 19 pass, 13 fail | 1 |
| Retained legacy claims on RC1 / candidate | 2 fail / 2 pass | 1 / 0 |
| Supplemental real scheduler/version tests | 3 pass | 0 |
| Supplemental synthetic exception/parameter payload tests | 4 deliberate failures, no marker leakage | 1 |
| Supplemental module collection error | FAIL, 31 incomplete | 1 |
| Supplemental successful pytest exit during collection | FAIL, 31 incomplete | 1 |
| Supplemental module collection skip, twice | **Incorrect PASS, 31 pass, zero reported skips** | **0** |

The three positive reports contain **584 distinct case IDs**, each with successful setup/call/teardown. Source hashes in those fresh reports match the reviewed files. The 45 R2 cases comprise 12 scheduler cases, 2 retained legacy-claim cases and 31 protocol cases. They are not 45 application defects, nor 584 production qualification tests. Supplemental tests, baseline failures, seed repeats and negative contracts are excluded from 584.

The 14 negative CLI modes cover early setup/call/teardown, final-case exit, runtime skip, successful abrupt OS exit, interrupt, exception leak, parameter leak, empty collection, worker kill, partial JSON, mismatched count and interrupted session finish. All behaved as claimed; none covers a skipped module alongside a successful module.

Before/after independently reproduced: scheduler regression fails1 on R1 and passes1 on R2; setup-only early exit incorrectly passes1/exit0 on R1 and becomes incomplete1/exit1 on R2; synthetic leak fixture fails on both, leaking only on R1. These historical contracts do not cover the newly discovered collection skip.

RC1's exact 13 failing IDs match REGRESSION-CLASSIFICATION.json. Source inspection supports **10 behavioral and 3 diagnostic-only**: fabricated held-task apply/acknowledge/reconcile already refuse on RC1, with different diagnostic codes. The two retained valid-claim state checks fail on RC1 and pass on R2, substantiating the behavioral boundary separately. These are deliberately reconstructed local database states, not production exploit or backend qualification evidence.

## Scheduler and authorization assessment

The original deferred failure is real: installed AsyncIOScheduler queues shutdown with call_soon_threadsafe; BaseScheduler sets STOPPED before closing executors/stores. The original probe reproduces lost ownership. R2 avoids using either enqueue return or running=False as completion evidence.

OwnedAsyncIOScheduler snapshots default resources, records completed closures, retains pending coroutine Tasks until they settle and closes stores afterward. Scheduler retains one shielded cleanup Task and backend handle across caller cancellation/timeout, observes late task failure, serializes start/stop and clears ownership only after successful cleanup. Durable-stop failure remains fenced independently. Retrying a stopped backend retries unfinished resource work. Explicit restart creates a fresh backend only after confirmed cleanup.

Fresh R2 tests cover real executor failure, real partial store failure, immediate restart, caller cancellation/timeout, concurrent shutdown, late errors, combined durable/local failure, cancellation-suppressing tasks, closed-backend reopening refusal, raw deferred backend refusal and non-Task future refusal. Additional independent tests use the actual MemoryJobStore with an injected asynchronous failure after cancellation, then repair/retry; concurrent start stays blocked until delayed cleanup settles. APScheduler version 3.11.3 was asserted inside the isolated execution.

No new execution capability, authorization bypass, schema change or provider route was found. Dispatch still checks epoch/failure and Authority admission. authority.py and simulation.py are unchanged from R1. Public Scheduler method signatures are preserved, but stop now waits or raises with retained ownership; unsupported backends/resources intentionally refuse. Custom executors/stores, threads/native jobs, cross-loop recovery and exhaustive concurrency are not qualified.

## Redaction and evidence integrity

Protocol2 exports allowlisted exception categories instead of arbitrary exception text, dynamic class names, traceback or missing-module regex captures. Parameter values are omitted even from ID hash inputs. Parent validation reconstructs status and accepts only schema-conforming evidence; ordinary malformed/missing/partial completion and mismatched counts fail nonzero.

Four independent injected exception classes/messages and parameter IDs produced FAIL4/exit1 without exporting the synthetic marker or payload text. Collection-error and interruption probes also kept their synthetic reasons out of JSON. Required-module skips also hide their reasons, but incorrectly hide their failure status; that defect belongs to R2 above, not a text disclosure.

Inspected the original independent report and R2 reports/source/tests/helpers. Inventoried all 221 packet files, parsed JSON evidence, and verified all **228 SHA256SUMS entries** with no mismatch. The complete committed diff has 229 paths: 8 source/test/helper paths and 221 packet files. No unexplained application changes were found. Older ACCEPTED/initial evidence is historical; FINAL-R2 has45, while earlier accepted R2 evidence had42. Final counts reproduce, so this is not positive-count inflation. Recorded seed repeats were inspected, not independently rerun in this audit. `git diff --check` passes.

The claims that no skipped/incomplete required verification can PASS and that all three findings are fully remediated are too broad given the new reproduction. This does not invalidate the 584 fully phased tests that actually ran.

## Integration conditions and remaining risks

Do not treat this branch's gate as authoritative for integration until the collection-skip defect is corrected and independently reviewed. Then rerun all positive suites, all 14 negative contracts, the three before/after contracts and the new collection probes on the exact combined candidate.

Protocol2 deliberately breaks report-consumer assumptions about IDs, diagnostics and executed versus attempted counts. Adapt consumers explicitly. APScheduler adapter uses protected 3.x internals: retain the tested version boundary and requalify dependency changes. Cancellation-suppressing tasks may remain owned indefinitely; timeout does not authorize dropping resources or restarting. Process/event-loop shutdown recovery and server lifespan Authority closure remain separate operational limitations.

Read-only inspection of the canonical VM164 host-enforcement-r3 report/source manifest found separate packet paths and no direct changed-file overlap. This is not qualification of combined behavior or permission to execute that packet. Canonical JARVIS remains at f4cac30259a7bf4610add2063679ae49138ee637 with preexisting dirty application files, including scheduler/runtime/authority. Do not copy this branch into that tree; use a separately authorized RC1-compatible integration checkout and coordinate shared-file changes. VM164 configuration/NIC, VM162, VM163 and AI server were untouched.

No network, installation, credential access, Proxmox/VM/provider/production action, privileged qualification, merge, rebase or push occurred. No dependency advisory, coverage, native executor, physical-power-loss or live deployment qualification is claimed. This audit grants no production deployment authorization.
