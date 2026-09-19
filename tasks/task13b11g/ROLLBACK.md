# Task 13B11G — Rollback

## 1. Runtime rollback: none required

The classifier is passive and unwired. `execution.mode` is `legacy`, `hermes_brain` and
`hermes_enabled` are both `False`, nothing in `app/` imports the module, and the legacy behavioural
probe is byte-identical before and after. No running system's behaviour depends on this commit, so
there is nothing to roll back at runtime and no feature flag to flip.

## 2. Source rollback: revert one commit

```
cd /home/jarvis/JARVIS
git revert d4eb171d45cc7d55ec18edfa40d2a324889c96de
```

The commit adds four files and modifies none, so the revert deletes four files and touches nothing
else. HEAD returns to the content of `a69f33e00a62050aaecf941b93e7beaa0394fffd`.

Expected after the revert: `pytest -q` back to 1068 passed / 11 deselected / 0 failed;
`tests/execution` back to 651; golden still 12/20 with the same eight failures; the legacy probe
still `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`.

Nothing has been pushed — the commit is local, ahead of `origin/main` by 6 along with the five
prior foundation commits — so a revert affects no remote and no other clone.

## 3. What is *not* required

No database rollback: the classifier persists nothing.
No provenance migration: it writes no provenance record.
No audit migration: it emits no schema-v3 event and the schema version is unchanged at 3.
No model cleanup: no model was loaded; the shared Ollama reported `{"models":[]}` throughout.
No Hermes cleanup: Hermes was never started, and its repository is unchanged at
`2237be355906fbe6065ce1815711eee52b2d646e`, clean.
No configuration rollback: `config.yaml` is byte-identical at
`247633cbd58a6297cbf94e7b293da905fbe521f1f2964b33bfa10d91c41875a3`.

## 4. Workspace rollback

The task documents and the loop-log entry are a separate workspace commit. Reverting it removes
`tasks/task13b11g/` and the log entry; it has no effect on production. The sealed evidence bundle
at `/home/jarvis/.hermes-poc/evidence/task13b11g-request-classifier/` is append-only history and is
not reverted — prior bundles are never modified.

## 5. Partial rollback

There is none to design. The commit is one indivisible unit: a module and its tests, with no
modified file and no consumer. Removing part of it would leave tests importing a module that no
longer exists.
