# Rollback

## What landed

One production commit on `main` in `/home/jarvis/JARVIS`, parent
`a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a`. **Not pushed.** `origin/main` is unchanged.

Files:

```
M  app/execution/classifier.py                                  +25 −0
M  tests/execution/router_generalization_test.py                +21 −11
M  tests/execution/router_non_activation_test.py                 +7 −1
A  tests/execution/classifier_lexicon_reconciliation_test.py
A  tests/execution/classifier_lexicon_table.json
```

## Rolling back

```bash
cd /home/jarvis/JARVIS
git log --oneline -2                 # confirm the repair commit is HEAD
git reset --hard a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a
git status --porcelain               # expect 0
```

Then confirm the pre-repair state:

```bash
sha256sum app/execution/classifier.py
# expect c554b34a24138095834287539f201cef7907168f05c926609e2234a59ce5e584
PYTHONPATH=$PWD .venv/bin/python -m pytest -q          # expect 3247 passed, 11 deselected
PYTHONPATH=$PWD .venv/bin/python -m evals.runner       # expect 12 passed, 8 failed
```

`git reset --hard` also removes the two added test files, since they are tracked by the
same commit. Nothing else needs undoing.

## What a rollback restores, and what it re-opens

It restores the pre-repair lexicon (44/26) and with it the defect: twenty of the router's
forty-one unsupported verbs return to `OTHER` / `NONE` / `CONVERSATIONAL`, where contract
§4.2 permits raw model prose for an explicit unsupported operation. That is a
contract §13.1 violation. It is **latent**, not live — `execution.mode` is `legacy`, the
live request path imports no `app.execution` module, and `UNKNOWN_ACTION` is
non-executable and non-dispatchable either way — so a rollback is safe but leaves P6
blocked again for exactly the reason 13B11L recorded.

## Risk if it is kept

Low and one-directional. The repair only moves requests *toward* the operational lane,
where the control plane builds the response. Measured: 0 requests moved
`OPERATIONAL → CONVERSATIONAL` across 2,041 probes. It grants no execution authority: no
repaired verb reaches a supported action family, resolves a target, or sets
`capability_available`, and `PrimaryAction.UNKNOWN_ACTION` is a member of both
`permissions.NON_EXECUTABLE_ACTIONS` and `dispatch.NON_DISPATCHABLE_ACTIONS`.

## Non-production artifacts

The evidence bundle
`/home/jarvis/.hermes-poc/evidence/task13b11l-r1-classifier-reconciliation/` and the
workspace docs `tasks/task13b11l-r1/` are records, not state. A production rollback does
not require touching either, and the blocked 13B11L bundle was not modified by this task
(re-verified 32/32 OK at entry).
