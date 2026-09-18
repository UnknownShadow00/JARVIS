# Task 13B11D — Rollback

## 1. Runtime rollback: nothing to do

P2 is passive. No production code path creates a ledger, records a fact or reads one, so there is no
runtime behaviour to revert. The effective mode is `legacy` and was never read by this phase.

## 2. Source rollback

```
cd /home/jarvis/JARVIS
git revert b9a557b4460daf240cc26f6ae932db476a5c4315     # or: git reset --hard eb4c5db
```

The commit adds three files and modifies one. A revert deletes `app/execution/provenance.py` and the
two test files, and removes the nine added lines from `app/execution/correlation.py`
(`ProvenanceRecordId` and `new_provenance_record_id`). Nothing else in that file changes, and the
P0/P1 foundations are untouched.

## 3. What is not required

| Not required | Why |
|---|---|
| database rollback | there is no database and this phase introduced no persistence |
| audit-log migration | no provenance event was ever written; `logs/audit.jsonl` still holds only schema 2 lines |
| state migration | the ledger is in memory and per session; any test state disappears with the process |
| config change | `config.yaml` and `config.yaml.example` are byte-identical to baseline |
| model cleanup | no model was loaded; the shared Ollama reported `{"models":[]}` throughout |
| Hermes cleanup | Hermes was not started, not configured and not modified (`2237be35`, clean) |
| lifecycle cleanup | `drop`/`clear` are not wired to LIGHT_SLEEP, DEEP_SLEEP or anything else |

## 4. Verification after a rollback

```
git rev-parse HEAD                                       # eb4c5db…
.venv/bin/python -m pytest -q                            # 553 passed, 11 deselected
.venv/bin/python -m evals.runner --mode deterministic    # 12 passed / 8 failed, same eight
```
