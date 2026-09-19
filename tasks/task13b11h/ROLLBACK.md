# Task 13B11H — Rollback

## 1. Runtime rollback: none required

The router is passive and unwired. `execution.mode` is `legacy`, `hermes_brain` and
`hermes_enabled` are both `False`, nothing in `app/` imports the module, and the legacy
behavioural probe is byte-identical before and after. No running system's behaviour depends on
this commit, so there is nothing to roll back at runtime and no feature flag to flip.

## 2. Source rollback: revert one commit

```
cd /home/jarvis/JARVIS
git revert 03cab4960156220fe9b6c3a444fa7a41265c01e0
```

The commit adds four files and modifies none, so the revert deletes four files and touches nothing
else. HEAD returns to the content of `d4eb171d45cc7d55ec18edfa40d2a324889c96de`.

Expected after the revert: `pytest -q` back to 1565 passed / 11 deselected / 0 failed;
`tests/execution` back to 1148; golden still 12/20 with the same eight failures; the legacy probe
still `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`.

Nothing has been pushed — the commit is local, ahead of `origin/main` by 7 along with the six
prior foundation commits — so a revert affects no remote and no other clone.

## 3. What is *not* required

No database rollback: the router persists nothing.
No provenance migration: it writes no provenance record and reads none.
No audit migration: it emits no schema-v3 event and the schema version is unchanged at 3.
No dispatcher or registry change to undo: `registry.call` has the same four callers and
`app/tools/registry.py` is byte-identical.
No permission or confirmation state to unwind: neither exists yet.
No model cleanup: no model was loaded; the shared Ollama reported `{"models":[]}` throughout.
No Hermes cleanup: Hermes was never started, and its repository is unchanged at
`2237be355906fbe6065ce1815711eee52b2d646e`, clean.
No configuration rollback: `config.yaml` is byte-identical at `247633cb…`.

## 4. Workspace rollback

The task documents, the loop-log entry and the `CLAUDE.md` "Current Status" update are a separate
workspace commit. Reverting it removes `tasks/task13b11h/`, the log entry and the status
paragraph; it has no effect on production, whose copy of `CLAUDE.md` is byte-identical at
`662ab5dd…` and was not touched. The sealed evidence bundle at
`/home/jarvis/.hermes-poc/evidence/task13b11h-action-router/` is append-only history and is not
reverted — prior bundles are never modified.

## 5. Partial rollback

There is none to design. The commit is one indivisible unit: a module and its tests, with no
modified file and no consumer. Removing part of it would leave tests importing a module that no
longer exists.

## 6. Rolling back the whole of P3

If the phase as a whole had to go, the four commits revert cleanly in reverse order —
`03cab496` (router), `d4eb171d` (classifier), `a69f33e0` (lane policy), `e7432431`
(canonicalizer) — because each adds files only and none imports a later one. The router imports
the classifier, so the router must be reverted first; nothing else in P3 has an intra-phase
dependency.
