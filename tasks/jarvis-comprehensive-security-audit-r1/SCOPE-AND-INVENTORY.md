# Scope and exact source inventory

**Revision limit:** ongoing implementation changed 9 captured paths and added 1 public path after the cutoff. Those later bytes are unreviewed; see [exact post-cutoff list](POST-CUTOFF-CHANGES.md). Findings apply to the frozen revision.

Final source identity: `f4cac30259a7bf4610add2063679ae49138ee637+dirty-snapshot:e20fe0c97a670b1ad6b6655334ca117b488011c8a27b95078893d90897e7f910`. Base HEAD: `f4cac30259a7bf4610add2063679ae49138ee637` with dirty/uncommitted bytes captured. Cutoff: 2026-11-06T07:13:57.665340+00:00. HEAD alone does not identify this source. [source-manifest-packaged.json](source-manifest-packaged.json) records path, SHA256, bytes and observed source mode; [source-packaged.sha256](source-packaged.sha256) verifies readonly snapshot-packaged.

Dirty-source suffix is SHA256 of the ordered sha256sum file: `e20fe0c97a670b1ad6b6655334ca117b488011c8a27b95078893d90897e7f910`. SHA256 of the JSON manifest itself: `d5e6d6de931ab745c128a639fdb2747cee0ae243b20b618cd7bd1714108a2dcd`.

| Capture | Files | Selection/revalidation |
|---|---:|---|
| snapshot | 339 | Comprehensive first capture plus recorded public supplements |
| snapshot-current | 342 | 17 concurrent recovery/authority paths recaptured |
| snapshot-final | 342 | Further registry source/test/doc changes revalidated |
| snapshot-expanded | 385 | Adds 43 public current broker successor files |
| snapshot-latest | 388 | Revalidates 15 safety/authority/transport paths |
| snapshot-packaged | 390 | Final bounded 16-path transport/recovery/CLI/safety delta |

Every earlier snapshot and sealed evidence remains intact. Capture transitions, stable-read consistency and exact deltas are retained. Captures are per-file stable and rehashed, not atomic across files. source-stability-packaged.json compares packaged files to the active worktree and lists later drift.

Final capture: 390 files, 2021462 bytes. repository-path-inventory.json contains metadata-only inventory of 56,613 paths, including historical artifacts.

| Root | Files |
|---|---:|
| .env.example | 1 |
| .github | 4 |
| .gitignore | 1 |
| AGENTS.md | 1 |
| CLAUDE.md | 1 |
| CONTRIBUTING.md | 1 |
| Dockerfile | 1 |
| HANDOFF.md | 1 |
| Modelfile.nothink | 1 |
| PHASE_0_TASKS.md | 1 |
| PHASE_1_TASKS.md | 1 |
| PROJECT_STATUS.md | 1 |
| README.md | 1 |
| SESSION_STARTER.md | 1 |
| app | 101 |
| assets | 1 |
| config | 1 |
| config.yaml.example | 1 |
| docker-compose.yml | 1 |
| docs | 19 |
| evals | 7 |
| frontend | 13 |
| jarvis.cmd | 1 |
| jarvis.py | 1 |
| pytest.ini | 1 |
| requirements-core.txt | 1 |
| requirements-desktop.txt | 1 |
| requirements.txt | 1 |
| scripts | 10 |
| skills.md | 1 |
| tasks | 90 |
| tests | 122 |

Active scope includes all maintained app/client/script/evaluator code, root task utilities, Electron lock, tests/docs/dependency/deployment definitions, phase2/older phase3 baseline and current tasks/proxmox-automation-phase3-review-r1 source/deploy/release design. PROJECT_STATUS89-94 identifies the successor. Historical evidence and binaries were excluded from active implementation conclusions.

Runtime config.yaml/.env/data/logs, real databases/credentials, installed credential-bearing observer helper, models and binaries were not opened. Public examples and dummy test keys were included. One public upstream MSS writer was inspected statically through GitHub; no package/advisory downloads or installed-version inference followed. No production/provider/desktop/audio/PVE/guest operation occurred. Application source and Git index were not modified by this audit; the audit directory and append-only project completion log are its only writes.
