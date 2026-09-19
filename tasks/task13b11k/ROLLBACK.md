# Rollback — Task 13B11K

## Runtime

None. P5 is inert: `execution.mode` is `legacy`, nothing under `app/` imports the dispatcher,
there are no call sites, no executor is configured anywhere in production, and no state is
persisted. Reverting changes no behaviour because no behaviour was added.

## Source

```
git -C /home/jarvis/JARVIS revert <the single 13B11K commit>
```

One focused commit, 10 files. Reverting it removes `app/execution/dispatch.py`, the four test
files and the matrix fixture, and restores `app/execution/confirmation.py` and the three updated
tests to their 13B11J state. Nothing else in the tree references any of it, so the revert cannot
fail on a dependency.

After reverting, expect `pytest -q` to return to 2892 passed / 11 deselected, `tests/execution`
to 2475, golden to 12/20 with the same eight IDs, and the legacy probe to
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291` — all of which it already is,
because this task changed none of them.

## Not required

No database. No migration. No persisted confirmation state — the store is in-process and dies
with the process, deliberately. No external side effect was ever performed, by construction. No
Hermes state: it was not started, its repository is unchanged at `2237be35…`, and both flags
stay `false`. No model was called.
