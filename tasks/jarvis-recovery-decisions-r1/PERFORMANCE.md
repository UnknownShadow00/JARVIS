# Bounded offline performance

Both measurements were executed during this sprint in the same retained guarded
runner, sequentially with disposable state and the verified exact offline dependency
closure. No production SLO or tail-latency guarantee is claimed.

Before: `runs/20261106T055529446285Z/output/RECOVERY-BENCHMARKS.json`.
After: `runs/20261106T061055269265Z/output/RECOVERY-BENCHMARKS.json`.
The complete input source hashes identify the earlier and final revisions.

| Retained renewal events | Inspection median before | Inspection median after | Final renewal median | Final restart inspection |
|---|---:|---:|---:|---:|
| 0 | 0.852 ms | 0.816 ms | n/a | 0.810 ms |
| 8 | 15.989 ms | 2.664 ms | 45.949 ms | 2.521 ms |
| 32 | 173.548 ms | 7.149 ms | 55.658 ms | 7.069 ms |

Each inspection median uses 12 warmed samples; renewal medians use the stated
number of actual SQLite/protected-journal publications. The largest case retained
33 events, 32 held tasks, 9 checkpoint generations (epochs 0–8), a 147456-byte
SQLite file and 113268 bytes of custody files. Every case verifies restart and a
portable receipt without activating work.

The 32-renewal inspection was approximately 24.3 times faster in these observations.
Previously, replay rescanned the complete checkpoint chain for both references of
every renewal. It now verifies that chain once under the existing guard mutex and
process flock, and validates historical reference membership/generation against the
immutable result. Fresh renewal still verifies the live current head. Both HMAC
keys, per-event admission/expiry checks, SQL integrity/schema, complete journal,
external minimum and deterministic transition checks remain active.

The final benchmark mode additionally reruns four historical state/history cases
(up to 513 tasks and 256 history mutations) and three enrollment/restore/branch
cases with the final application source. These seven cases were rerun, not copied
as current results. The three new cases bring the mode to 10 benchmark cases.
Exact durations, storage and memory observations remain in RUN.json and the output
JSON files. Full retention at the configured maximum, disk device faults,
multi-host concurrency and physical power loss are not qualified.
