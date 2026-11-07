# Reproduce safely

Run from the JARVIS project root using the guarded runner only. Do not import app
or dependencies, run helper actors, or invoke children directly on the host. The
runner verifies retained interpreter/bwrap/harness/dependency closure, checks shared
machine headroom and creates only new timestamped private synthetic run directories.
No network/install or real runtime config/database/key is used.

Run sequentially without editing app source during any active run:

```sh
python3 -I -B -S tasks/jarvis-authority-enrollment-r1/run_checks.py --mode core --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-authority-enrollment-r1/run_checks.py --mode focused --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-authority-enrollment-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-authority-enrollment-r1/run_checks.py --mode benchmark --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Core runs254 previous queue/ledger/disaster regressions. Focused runs59 new cases
separately to retain the existing120-second run cap. Full-app runs58 regressions,
13 actual scenarios and3 native probes. Benchmark runs4 history/state cases plus3
actual enrollment/restore/branch cases. Initial legacy fixtures are explicitly
seeded under tests/ and receive trusted synthetic compatibility capabilities;
new enrollment cases use the ordinary production Authority and real ceremony.
No product creation/authentication checks are overridden or monkeypatched.

`enrollment_application.py` demonstrates actual CLI memfd descriptor handoff,
enrollment, verification, source lifespan, restoration, read-only proposal and
UNKNOWN restart. Reproduce it through full-app mode, not against another store.

`build_evidence.py` documents original stdlib-only packet assembly. Do not regenerate
preserved evidence or seals. Additional reproduction runs are new evidence outside
the original sealed inventory. From this packet directory, `sha256sum -c SHA256SUMS`
checks regular file contents; SYMLINKS.json records link identities. A separately
retained expected seal is needed to detect privileged rewriting; local checksums
are not independent antirollback custody.
