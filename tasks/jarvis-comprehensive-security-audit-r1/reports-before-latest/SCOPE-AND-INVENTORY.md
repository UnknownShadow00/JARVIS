# Scope and source inventory

Final reviewed source identity: `f4cac30259a7bf4610add2063679ae49138ee637+dirty-snapshot:ac7ab490e6e3fa3900f26cfc8e8ab50e86e3e14482a8d2ec1f3024e33252581b`. Base HEAD is `f4cac30259a7bf4610add2063679ae49138ee637`; current uncommitted files are included. HEAD alone does not identify this source. Exact bytes are retained in snapshot-expanded/ with source-manifest-expanded.json and source-expanded.sha256.

| Capture | Files | Selection/revalidation |
|---|---:|---|
| snapshot | 339 | Comprehensive first capture plus recorded public fixture supplements |
| snapshot-current | 342 | 17 concurrent Sprint 5 changed/added paths recaptured and independently reviewed |
| snapshot-final | 342 | Three further recovery source/test/doc changes reviewed with final expiry and journal checks |
| snapshot-expanded | 385 | All final application bytes preserved; 43 files from documented current broker successor added and independently reviewed |

Capture timestamps, exact transitions and equality checks are in run-metadata.json, source-delta.json, source-delta-final.json and source-infra-extension.json. Every capture used stable individual reads and rehash; this is not an atomic cross-file filesystem snapshot. Final stability verification compares all 385 files to the active worktree.

Final capture: 385 files, 1961347 bytes. Repository-path-inventory.json lists 56,613 paths at inventory time, including historical artifacts, without reading their data contents.

| Root | Captured files |
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
| app | 100 |
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
| tests | 118 |

Active scope includes all maintained app/client/script/evaluator code, Electron lockfile, current tests/docs, dependency/deployment definitions, task-root utilities, phase 2/older phase 3 baseline, and the documented current tasks/proxmox-automation-phase3-review-r1 source/deploy/release design. The current source pointer is PROJECT_STATUS.md:89–94. Older broker evidence does not qualify the current revision. Historical sealed evidence and binary archives remain excluded from implementation conclusions and were never rewritten.

Runtime config.yaml, .env, data/, logs/, real databases/credentials, installed observer helper, models and binary assets were not opened. Public examples and synthetic test keys are included. No live application/provider/infrastructure or real desktop/audio was accessed. Public MSS v9.0.1 writer source was read statically through GitHub, without installation/execution or a deployed-version claim.

All new artifacts stay in this directory. Application source and Git index were not modified. The project completion log is the only append-only write outside this directory.
