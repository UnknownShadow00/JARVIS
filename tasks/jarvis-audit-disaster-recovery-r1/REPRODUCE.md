# Reproduce the offline checks

Run from the JARVIS project root. Use only the retained guarded runner, which
verifies its historical harness/interpreter/bwrap/dependency inputs before imports.
Do not run application imports, test helpers or the full-app child directly on
the host. The runner refuses missing verified inputs or inadequate headroom;
it installs nothing and makes no external network call.

Run these sequentially, with no application source edits while a run is active:

```sh
python3 -I -B -S tasks/jarvis-audit-disaster-recovery-r1/run_checks.py --mode core --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-audit-disaster-recovery-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-audit-disaster-recovery-r1/run_checks.py --mode benchmark --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Each invocation creates a new timestamped `runs/` directory with copied read-only
inputs, fresh synthetic state, headroom, input hashes, resource limits/peaks and
complete stdout/stderr/result. No real runtime config, database or credentials
are used. The app workflow exercises actual offline CLI FD handoff and real ASGI
lifespans inside the cage. The benchmark uses valid held synthetic historical
fixtures without changing admission limits.

This packet's seal describes the original evidence inventory. New reproduction
runs are additional development evidence and are not retroactively covered by
the original SHA256SUMS. Do not rewrite sealed runs or regenerate this packet's
evidence/seal after preservation. `build_evidence.py` documents how the original
report artifacts were assembled using only stdlib file reads; it is not a runtime
restore command or an instruction to overwrite preserved evidence.

Inspect source/runner hashes against `SOURCE-SHA256.json`, then verify this packet
using `sha256sum -c SHA256SUMS` from this directory. Checksums detect changes
relative to a separately retained expected seal; local checksums alone do not
provide privileged-attacker protection.
