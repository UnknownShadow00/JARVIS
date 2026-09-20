# Rollback — Task 13B11L-P6

## One command

```bash
cd /home/jarvis/JARVIS
git revert --no-edit 8a70d179c527f2912522920918f70a68ee213386
```

or, since the commit is not pushed and is `HEAD`:

```bash
git reset --hard ea0cb32040a0e24d0b80de706929086b6dd36b66
```

## What it removes

Seven added files and nothing else — the commit modifies no existing file:

```
app/execution/obligations.py
tests/execution/obligation_fixture.py
tests/execution/obligation_matrix.json
tests/execution/obligations_matrix_test.py
tests/execution/obligations_non_activation_test.py
tests/execution/obligations_p3_reconciliation_test.py
tests/execution/obligations_test.py
```

## What it does not affect

Nothing. The engine is imported by no module under `app/`, `execution.mode` is `legacy`,
both Hermes flags are false, and the 24 critical production files are byte-identical to
`ea0cb32`. Reverting changes no runtime behaviour, because the module has none today.

## Expected state after a rollback

```bash
PYTHONPATH=$PWD .venv/bin/python -m pytest -q          # 3744 passed, 11 deselected, 0 failed
PYTHONPATH=$PWD .venv/bin/python -m evals.runner       # 12 passed, 8 failed (the same eight)
```

The legacy probe digest stays `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`
before and after, because it is unchanged either way.

## What a rollback re-opens

P6 unit 1 only. The P3 lexicon repair (`9ace0e3`) and the classifier version reconciliation
(`ea0cb32`) are earlier commits and are untouched, so the contract §13.1 defect the blocked
13B11L found stays fixed. Nothing downstream depends on the engine yet.
