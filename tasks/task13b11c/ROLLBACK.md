# Task 13B11C — Rollback

## 1. Runtime rollback: nothing to do

P1 is passive and unwired. No production code path constructs, validates, serializes or writes an
execution-contract audit event, so there is no runtime behaviour to revert. The effective mode is
`legacy` and was never read by this phase.

## 2. Source rollback

```
cd /home/jarvis/JARVIS
git revert eb4c5db1985033f2c7464fbd1bd3ae9a385199d0     # or: git reset --hard 521969e
```

The commit adds five files and modifies none, so a revert deletes exactly what it added:
`app/execution/audit_events.py`, `app/execution/correlation.py` and the three test files. The P0
foundation (`app/execution/types.py`, `ExecutionConfig`, the `execution:` config block) is
untouched and stays in place.

## 3. What is not required

| Not required | Why |
|---|---|
| audit-log migration | no v1 event was ever written; `logs/audit.jsonl` contains only schema 2 lines |
| log rotation / retention change | `app/logs/audit.py` and `app/observability/tracing.py` are byte-identical to baseline |
| database migration | there is no database, and this phase introduced no persistence |
| config change | `config.yaml` and `config.yaml.example` are byte-identical to baseline |
| model cleanup | no model was loaded; the shared Ollama reported `{"models":[]}` throughout |
| Hermes rollback | Hermes was not started, not configured and not modified (`2237be35`, clean) |
| consumer coordination | no existing reader was asked to understand schema 3 |

## 4. Verification after a rollback

```
git rev-parse HEAD                                  # 521969e…
.venv/bin/python -m pytest -q                       # 483 passed, 11 deselected
.venv/bin/python -m evals.runner --mode deterministic   # 12 passed / 8 failed, same eight
```
