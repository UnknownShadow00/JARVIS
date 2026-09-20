# Rollback

## What landed

One production commit on `main` in `/home/jarvis/JARVIS`:

```
ea0cb32040a0e24d0b80de706929086b6dd36b66   fix: bump classifier rule version after lexicon repair
  parent  9ace0e3a0855708d992467a179d08f6affef43e1
```

**Not pushed.** `origin/main` unchanged.

```
M  app/execution/classifier.py                                 +16 −6   (1 code line)
M  tests/execution/classifier_test.py                           +6 −3
M  tests/execution/classifier_non_activation_test.py            +1 −1
M  tests/execution/classifier_lexicon_reconciliation_test.py    +9 −2
M  tests/execution/permissions_decisions_test.py               +12 −3
M  tests/execution/router_non_activation_test.py               +13 −7
A  tests/execution/classifier_version_test.py
A  tests/execution/classifier_version_identity.json
```

## Rolling back

```bash
cd /home/jarvis/JARVIS
git log --oneline -2                 # confirm ea0cb32 is HEAD
git reset --hard 9ace0e3a0855708d992467a179d08f6affef43e1
git status --porcelain               # expect 0
```

Confirm the restored state:

```bash
sha256sum app/execution/classifier.py
# expect 3a7db13392db5f88206dab3860c2c07fcafb34349f42ce8a678b0a045935ad00
PYTHONPATH=$PWD .venv/bin/python -c \
  "import app.execution.classifier as C; print(C.CLASSIFIER_VERSION, len(C.ACTION_VERBS))"
# expect: 1 64
PYTHONPATH=$PWD .venv/bin/python -m pytest -q       # expect 3464 passed, 11 deselected
PYTHONPATH=$PWD .venv/bin/python -m evals.runner    # expect 12 passed, 8 failed
```

`git reset --hard` also removes the two added files, since the same commit tracks them.

## What a rollback restores, and what it re-opens

It restores `CLASSIFIER_VERSION = "1"` **with the repaired 64-verb lexicon still in place**
— which is exactly the audit defect this task closed. Classification behaviour would be
unaffected; the reproducibility problem returns.

It does **not** roll back the R1 lexicon repair. To do that, reset to `a0cc4d3c…` instead
and see `tasks/task13b11l-r1/ROLLBACK.md`, which describes what that re-opens (a latent
contract §13.1 violation).

## Risk if it is kept

None measurable on behaviour. 520 snapshot rows across 16 fields are byte-identical with
the version field removed, 0 non-version fields moved, the full suite is 3744/0, golden is
unchanged at 12/20 with the same eight IDs, and the legacy probe is byte-identical. The
only observable difference is the value of `classifier_version` in a serialized
`Classification` — and nothing consumes it yet, because `execution.mode` is `legacy` and
the live request path imports no `app.execution` module.

The one thing to know: any artifact stored elsewhere that records a classification as
version `"1"` produced by the repaired rules — i.e. captured between `9ace0e3` and
`ea0cb32` — is now mislabelled. No such artifact exists: nothing was wired, nothing was
pushed, and no audit record was emitted in that window.

## Non-production artifacts

The evidence bundle and `tasks/task13b11l-r2/` are records, not state. Neither the R1
bundle nor the R2 bundle needs touching to roll back, and R1's was verified unmodified at
both entry and exit.
