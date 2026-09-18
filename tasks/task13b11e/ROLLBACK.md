# Task 13B11E — Rollback

## 1. Runtime rollback: nothing to do

The canonicalizer is passive. No production code path calls it, so there is no runtime behaviour to
revert. The effective mode is `legacy` and this phase never reads it.

## 2. Source rollback

```
cd /home/jarvis/JARVIS
git revert e7432431b5aaa18eb692b94a5520bdb9184dde62     # or: git reset --hard b9a557b
```

The commit adds three files and modifies none, so a revert deletes exactly what it added:
`app/execution/canonicalize.py` and the two test files. P0, P1 and P2 are untouched.

## 3. Narrowing instead of reverting

If the intent is to keep the mechanism but remove the alias, empty the `RULES` tuple. Every input
then canonicalizes to itself, the version stays meaningful, and no logic changes. That is a
data-only edit and does not require reverting the commit.

## 4. What is not required

| Not required | Why |
|---|---|
| database rollback | there is no database and this phase introduced no persistence |
| audit migration | no audit event was emitted; schema v3 and the 17 fields are unchanged |
| provenance cleanup | the module never touched the ledger; `provenance.py` is byte-identical |
| state cleanup | the module is stateless and holds no cache |
| config change | `config.yaml` and `config.yaml.example` are byte-identical |
| model cleanup | no model was loaded; the shared Ollama reported `{"models":[]}` throughout |
| Hermes rollback | Hermes was not started, configured or modified (`2237be35`, clean) |

## 5. Verification after a rollback

```
git rev-parse HEAD                                       # b9a557b…
.venv/bin/python -m pytest -q                            # 642 passed, 11 deselected
.venv/bin/python -m evals.runner --mode deterministic    # 12 passed / 8 failed, same eight
```
