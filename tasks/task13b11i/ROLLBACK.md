# Rollback

## Runtime

**None required.** The module is unreachable from the live request path: nothing under `app/`
imports it, `decide()` has no call site, and `execution.mode` is `legacy`. Deleting it would change
no production behaviour, which is the same thing as saying it changes none now.

## Source

```
git -C /home/jarvis/JARVIS revert 52c5da5d7a5d304acd4088b11e1f9bd509067069
```

One focused commit, five files added, nothing modified. The revert removes
`app/execution/permissions.py` and its three test files and the frozen table fixture, and returns
the tree to `03cab496`.

Verification after a revert: `pytest -q` back to 2113 passed, `tests/execution` to 1696, golden
still 12/20 with the same eight, legacy probe still `fc68a0b0…`.

## What is *not* needed

No database rollback — none exists and none was introduced. No confirmation cleanup — no
confirmation record can exist, because nothing here creates one. No audit migration — schema v3 is
unchanged and this task emits no event. No provenance repair — the ledger was never written. No
model or Hermes cleanup — no inference was performed and Hermes was never started. No config
change — `config.yaml` is byte-identical and `config/permissions.yaml` was never created.

## Workspace

The documentation commit in the workspace repository is independent and can be reverted separately;
reverting it changes no code.
