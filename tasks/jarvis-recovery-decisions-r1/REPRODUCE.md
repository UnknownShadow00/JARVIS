# Reproduce offline

Run from the JARVIS project root. Use the retained guarded runner; never invoke
children or application imports directly against host runtime state. Every run
creates a new timestamped private directory and copies source before execution.
The runner verifies the retained interpreter, bubblewrap and exact offline
dependency closure, enforces unchanged resource bounds, and proves network isolation
before importing the application. No dependencies are installed or downloaded.

```sh
python3 -I -B -S tasks/jarvis-recovery-decisions-r1/run_checks.py --mode focused --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-recovery-decisions-r1/run_checks.py --mode enrollment --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-recovery-decisions-r1/run_checks.py --mode core --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-recovery-decisions-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-recovery-decisions-r1/run_checks.py --mode benchmark --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Run sequentially; do not modify source during a run. Final counts and run identities
are recorded in RESULTS.json. Older failed development outputs are preserved and
are not final passing results. Each run includes the complete source input hashes,
stdout/stderr, resource observations, copied tests, disposable SQLite state and
boundary proof. CRASH-RECOVERY.jsonl is emitted by actual independent-process
SIGKILL tests, including a hot rollback journal after real uncommitted SQLite
page spill. It proves process interruption recovery, not physical power loss.

The full-app run includes actual inherited-descriptor CLI ceremonies, verified
archive/inert restore, occurrence and UNKNOWN identity preservation, durable
proposal/approval, portable HMAC receipt verification, witness renewal, actual ASGI
startup/readiness/authenticated diagnostics and shutdown, without network listeners.
Detailed proposal history is excluded from anonymous readiness. Mutation endpoint
absence is tested. No executor is dispatched by either recovery workflow.

Benchmark mode runs historical state/history and enrollment benchmarks afresh plus
bounded new registry/witness cases. Measurements are individual warmed local runs,
not production tail-latency SLOs. A fresh externally protected latest reference is
required to detect coordinated local rollback; local HMAC/checksum files alone do
not supply that custody.

Do not regenerate predecessor evidence. The baseline pins prior packet bytes and
canonical log prefix. Source.patch compares actual starting files with final files,
not git HEAD (the starting tree already contained uncommitted earlier sprints).
