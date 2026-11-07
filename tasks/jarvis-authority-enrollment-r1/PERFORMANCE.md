# Bounded offline performance measurements

All seven cases use the final99 application hashes and unchanged cage/resource
limits. Raw samples: [BENCHMARKS.json](BENCHMARKS.json) (four state/history cases)
and [ENROLLMENT-BENCHMARKS.json](ENROLLMENT-BENCHMARKS.json) (three actual ceremonies).
The latter use real enrollment, first owner takeover, original UNKNOWN operation,
task population, audit export, inert restore, branch proposal and restart checks.

| Held tasks (+1 UNKNOWN) | Enrollment ms | Verify enrollment ms | Verify checkpoint ms | First owner ms | Export ms | Restore ms | Branch verify ms | Restart ms | Generations | Apparent bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 118.589 | 2.849 | 0.173 | 51.535 | 197.821 | 93.455 | 5.221 | 53.378 | 3 | 202958 |
| 16 | 113.279 | 2.905 | 0.170 | 48.722 | 234.391 | 114.835 | 9.361 | 56.256 | 7 | 313968 |
| 32 | 102.386 | 2.857 | 0.164 | 52.398 | 307.986 | 128.460 | 13.927 | 67.172 | 11 | 416795 |

Each new ceremony cost is one warmed measurement per disposable case, not a
statistical percentile. File counts, apparent/allocated storage and cumulative
process peak RSS are retained in raw JSON. Population uses individual real held
task admissions; max_pending and checkpoint capacities are unchanged. All seven
cases preserve UNKNOWN; uncertain reexecution count is zero.

The four history regressions retain17/129/513-task snapshots and256 control
mutations, three warmed verification/query samples, checkpoint/rollover commit
overhead, export/restore throughput and startup/reconciliation. Their legacy
setup uses explicit trusted synthetic compatibility capabilities, not the new
genesis ceremony. Protected full-state/history verification remains linear.
No cold-cache, production SLO, million-row scale, physical power loss or unlimited
retention claim is made. No resource guard fired or limit was increased.
