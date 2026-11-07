# Bounded synthetic performance evidence

Final run: `runs/20261106T045518994872Z/RUN.json`. Raw samples, storage, memory,
query/reconciliation times and logical throughput: [BENCHMARKS.json](BENCHMARKS.json).
Same 97 application hashes as final core and full-app runs. Four sequential cases;
unchanged 120s wall/768MiB aggregate/1GiB per-process limits. No network or service.

| Case | Tasks | Checkpoint sequence | Generations | Verify uncached ms | Verify cached ms | Commit median ms | Rollover commit median ms | Export ms | Restore ms | Startup ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| state16 | 17 | 17 | 2 | 1.440 | 1.009 | 35.129 | not sampled | 200.569 | 104.407 | 44.123 |
| state128 | 129 | 41 | 3 | 7.132 | 3.049 | 38.796 | 81.839 | 211.818 | 135.664 | 61.614 |
| state512 | 513 | 73 | 5 | 9.392 | 7.087 | 53.397 | 101.283 | 272.872 | 182.373 | 68.738 |
| history256 | 17 | 265 | 9 | 22.238 | 14.312 | 65.559 | 131.586 | 413.343 | 230.109 | 96.180 |

Three warmed verification/query samples per case. Uncached refers to disabled
decode/HMAC memoization, not a physically cold filesystem. The cache still reads,
hashes and validates every file and hashes complete logical SQLite state. Returned
values are copied. The 2048-entry cache is bounded. Tampering after cache warmup
is independently tested. Checkpoint commit measurements include transaction,
intent/final durability; rollover samples include generation transition overhead.

State scaling uses one synthetic batch of held historical fixtures under a fenced
mutation; the normal max_pending=128 gate is unchanged. One real synthetic UNKNOWN
operation is created before the batch and retained across restore/startup/reconcile.
History scaling uses 256 individually checkpointed control mutations. No fabricated
completed task, automatic retry or migration of real state occurs. The first
benchmark fixture incorrectly tried to admit after the held batch; conservative
queue-capacity refusal stopped it. Reordering fixture setup fixed it without
raising capacity. That failed run is retained.

The longest history shows the measured HMAC/JSON cache benefit, but verification
and protected queries still scan all history/state. Raw SQL component timings
are included to show this cost, not proposed as a bypass. RSS is a cumulative
process maximum; apparent and allocated storage are separately reported. Run
aggregate RSS includes supervisors. No production SLO, million-row throughput,
cold-cache, power-loss or unbounded retention claim is made.
