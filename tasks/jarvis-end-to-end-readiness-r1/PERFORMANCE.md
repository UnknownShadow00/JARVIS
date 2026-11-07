# Bounded current-source performance

Final benchmark run: `20261106T072022021388Z`, PASS, 48.97 seconds.
Thirteen cases: four existing execution/ledger sizes, three enrollment, three
recovery/witness, and three new actual signed IPC cases. See the four *BENCHMARKS.json
files for raw measurements. These were rerun on current source; they are not copied
historical timing claims. No throughput SLA or production scale claim is made.

| Cumulative signed tasks | Admission median ms | Dispatch + durable publication median ms | Authenticated readiness median ms | Readiness max ms |
|---:|---:|---:|---:|---:|
| 1 | 43.51 | 248.24 | 28.73 | 29.19 |
| 4 | 54.05 | 350.83 | 149.27 | 152.43 |
| 8 | 90.23 | 394.52 | 448.04 | 449.18 |

Each dispatch used actual framed socketpair IPC and the single Authority writer;
endpoint invocations equalled task count. Readiness samples authenticate retained
grant/report history five times per size. Each 1/4/8 case used a fresh disposable
store, not a warm production database. Timing includes protected checkpoint writes
and integrity scans. The endpoint remains pure synthetic and same-process.

The cost rises with retained state and history. The current full-scan implementation
has a 128 lifetime transported-grant cap, but this run measures up to eight, not the
cap or an unbounded history. No request is described as constant time. A future
bounded incremental verification/archival ceremony must preserve authenticated
ancestry and uncertain-effect records before extending scale. Do not delete history
or relax readiness checks to improve a benchmark.

Final test runs peaked at 121,847,808 aggregate descendant RSS bytes (116.20 MiB),
3,660 scratch files and 22,025,875 scratch bytes across per-run maxima. Limits stayed
1 GiB AS/process, 768 MiB aggregate RSS, 120/121 CPU seconds, 120 wall seconds,
64 MiB/file, 64 FDs, core0, 20,000 files/256 MiB scratch, two payload processes plus
bwrap. Guard stops were null. These observations are specific to the isolated Nexus
run and verified dependency closure; they do not qualify live hardware durability.
