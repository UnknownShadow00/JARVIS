# Rollback — Task 13B11B

Rollback is trivial because nothing was activated: the mode is parsed and never entered, so there
is no behaviour to switch off.

| Level | Action | Time | Effect |
|---|---|---|---|
| 0 | do nothing | — | the effective mode is already `legacy`; the installed code is unreachable |
| 1 | set `execution.mode: legacy` (already the value) or delete the `execution:` block | seconds | identical behaviour; a missing block resolves to legacy |
| 2 | `git revert 521969e051f5cd725415fded0fbc8221e41c842f` in `/home/jarvis/JARVIS` | minutes | removes the package, the config model and the tests; the tree returns to `2d7a2ec8` content |
| 3 | `git checkout 2d7a2ec8 -- config.yaml config.yaml.example app/config.py && rm -rf app/execution tests/execution` | minutes | same result without a revert commit |

## What rollback does not have to cover

* **No data migration.** No database was introduced, no schema changed, no file format written.
* **No state cleanup.** The new types are never constructed at runtime, so no records exist.
* **No model cleanup.** No model was pulled, loaded, unloaded or reassigned; the AI VM was untouched.
* **No Hermes rollback.** Hermes was never enabled: `agent.hermes_enabled` is still `false`, the pin
  is still `2237be355906fbe6065ce1815711eee52b2d646e`, and its repository is clean.
* **No audit or evidence deletion.** Rollback removes code, never evidence bundles or contract
  artifacts.

## Verification after a rollback

1. `git rev-parse HEAD` and a clean `git status`.
2. `.venv/bin/python -m pytest -q` → 417 passed, 11 deselected.
3. `.venv/bin/python -m evals.runner --mode deterministic` → 12/20 with the same eight failures.
4. `.venv/bin/python -c "from app.config import settings; print(settings.agent.hermes_enabled)"` → `False`.
