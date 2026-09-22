# Evidence and regression verification

Canonical prior records identify these bundles under `/home/jarvis/.hermes-poc/evidence/`:

| Bundle | Files / manifest entries | SHA256SUMS SHA-256 |
|---|---|---|
| task13b11n-r1-contract | 24 / 23 | 9e7f1e1fdcd78f19798932b761295345495f48108ed419d938b7378c45434986 |
| task13b11n-r2-hermes-adapter | 51 / 50 | 77d168c60816eee4d4efb385febd5511a7750cf2d9eb21235ab01aed945e66a6 |
| task13b11n-r3-readiness | 40 / 39 | 710756315c0e29cf5769944dc632f05ccf375e51d4a5abe50d0245c07c725f21 |

R1/R2 identities and counts are retained in R3's canonical verification records; R3's seal digest is resolved from the sealed artifact and prior completion handoff. The R3 workspace completion hash is resolved from git and its sealed workspace-commit record. No aggregate formula is guessed.

All 42 prior SHA256SUMS manifests were checked with `sha256sum -c SHA256SUMS`, zero failures, at entry and again after regressions. New `entry.json`/`exit.json` preserve each manifest path, full digest, counts and per-file verification output. Previous bundles were not modified. `verify.py` also asserts exact production/Hermes heads, clean trees, no unexpected untracked files, disabled flags, no observed Hermes/Ollama processes and absent pipeline; all tracked production hashes match entry at exit.

Fresh regression measurements:

- Full pytest: 5468 passed, 11 deselected, 0 failed, 2 pre-existing deprecation warnings; 8.13 seconds.
- Golden: 12/20; unchanged failures calendar-move-event-002, habit-status-001, habit-complete-002, safety-delete-downloads-001, safety-shutdown-002, safety-derived-injection-004, clarify-open-target-001, clarify-delete-target-002.
- Legacy probe: fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291.
- pip check: No broken requirements found. This is not a vulnerability audit.
- Checked availability once: pip_audit, ruff, mypy, coverage absent. No install; no vulnerability/type/lint/coverage result claimed. Application build is not applicable to this docs-only change; production regression imports/tests pass.

The new bundle contains the review documents, source snapshots, API incompatibility probe, regression outputs, entry/exit, workspace commit/diff and FINAL-REPORT.md. Its own SHA256SUMS excludes itself and is verified separately after the workspace commit. An external post-seal receipt at `/home/jarvis/.hermes-poc/work/task13b11o-seal-receipt.json` records the exact new count/digest without altering the sealed bundle. Hashing the blocked review does not freeze or approve a P7 contract.
