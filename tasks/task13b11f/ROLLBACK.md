# Task 13B11F — Rollback

## 1. Runtime rollback: nothing to do

The lane policy is passive and unwired. No production code path calls it, so there is no runtime
behaviour to revert. The effective mode is `legacy` and this phase never reads it.

## 2. Source rollback

```
cd /home/jarvis/JARVIS
git revert a69f33e00a62050aaecf941b93e7beaa0394fffd     # or: git reset --hard e743243
```

The commit adds three files and modifies none, so a revert deletes exactly what it added:
`app/execution/lane.py` and the two test files. P0, P1, P2 and the P3 canonicalizer are untouched.

## 3. Narrowing instead of reverting

The policy is a table plus three lines. To change which classes are unconditionally operational,
edit `ALWAYS_OPERATIONAL_CLASSES`; to change which conditions escalate, edit `SIGNAL_REASONS` and
the matching `LaneSignals` fields. Any such edit is a policy change and requires a
`LANE_POLICY_VERSION` bump and a re-derivation of `TRUTH_TABLE.md`, because the table is the
contract of record and the tests transcribe it by hand.

There is deliberately no switch that widens the conversational lane. Narrowing the operational lane
is a contract change, not a configuration change.

## 4. What is not required

| Not required | Why |
|---|---|
| database rollback | no database and no persistence was introduced |
| audit migration | no event was emitted; schema v3, the 17 fields and `lane`'s absence from them are unchanged |
| provenance cleanup | the ledger was never read or written; `provenance.py` is byte-identical |
| canonicalizer cleanup | `canonicalize.py` is byte-identical and was never imported |
| state cleanup | the module is stateless, holds no cache and has no module-level mutable container |
| config change | `config.yaml` and `config.yaml.example` are byte-identical |
| model cleanup | no model was loaded; the shared Ollama reported `{"models":[]}` throughout |
| Hermes rollback | Hermes was not started, configured or modified (`2237be35`, clean) |

## 5. Verification after a rollback

```
git rev-parse HEAD                                       # e743243…
.venv/bin/python -m pytest -q                            # 758 passed, 11 deselected
.venv/bin/python -m evals.runner --mode deterministic    # 12 passed / 8 failed, same eight
```
