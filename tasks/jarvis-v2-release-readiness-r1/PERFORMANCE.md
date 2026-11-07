# Current candidate bounded performance

Thirteen cases passed on the exact final 102 app source hashes: four retained
full-state/ledger shapes, three enrollment, three registry/witness, and three actual
signed IPC application sizes. This is current execution, not copied historical timing.
Raw data are the four *BENCHMARKS.json files and final benchmark RUN.json.

| Cumulative signed tasks | Admission median ms | Dispatch + durable publication median ms | Authenticated readiness median ms | Readiness max ms |
|---:|---:|---:|---:|---:|
| 1 | 36.69 | 259.15 | 32.00 | 32.35 |
| 4 | 55.48 | 296.62 | 160.72 | 161.85 |
| 8 | 100.77 | 385.46 | 534.36 | 585.67 |

Each size used a fresh disposable store and exactly one endpoint invocation per
task, actual socketpair frames and protected Authority/checkpoint publication.
Readiness was sampled five times per size and reauthenticated retained history.
Verification cost grows with state/history. The lifetime cap is128 transported
grants, but this benchmark reaches eight; no capacity-scale or throughput SLA is
claimed. Full-state and custody scans must not be bypassed to improve timings.

Maximum observed across final modes: 138985472 aggregate descendant
RSS bytes (132.55 MiB), 3661 scratch/input files,
and 21989892 controlled bytes. Guard stops were absent.
Unchanged bounds: AS1GiB/process, aggregate RSS768MiB, CPU120/121s, wall120s,
64MiB/file, 64 FDs, core0, 20,000 files/256MiB controlled storage and at most two
payload processes plus namespace machinery. NumPy uses one BLAS/OMP thread.
These measurements do not qualify actual power loss, production storage, GPU,
models, audio/desktop devices, a real network or guest execution.
