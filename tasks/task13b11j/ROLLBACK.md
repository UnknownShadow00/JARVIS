# Rollback — Task 13B11J

## 1. Runtime rollback: none required

Nothing changed at runtime. `execution.mode` is `legacy`, `hermes_brain` and `hermes_enabled` are
`false`, and no module under `app/` imports the new one — measured, 0 importers and 0 references to
any of nineteen public symbols. The legacy `_pending_confirmations` path in `app/server.py` is
byte-identical and still handles every real confirmation. The behavioural probe over the legacy
path is byte-identical before and after (`fc68a0b0…`), and all 24 critical files hash the same.

If the module were deleted this instant, no request would behave differently.

## 2. Source rollback

```
cd /home/jarvis/JARVIS
git revert --no-edit c321cb8958935fa74db0916ec47e56f052410663
```

Or, since the commit is not pushed and is `HEAD`:

```
git reset --hard 52c5da5d7a5d304acd4088b11e1f9bd509067069
```

Reverting removes five files and restores one line in
`tests/execution/canonicalize_non_activation_test.py`. Nothing else is touched.

## 3. What a revert does not have to clean up

| | |
|---|---|
| database | none created |
| persisted state | none — the store is in-memory and nothing is written to `data/` |
| migration | none |
| config change | none — `config.yaml` is byte-identical |
| audit log entries | none emitted |
| provenance records | none written |
| background job / timer / thread | none started |
| Hermes | untouched: `2237be35…`, clean, 0 processes |
| model / Ollama | no inference; the shared Ollama reported `{"models":[]}` before and after |

## 4. Verification after a rollback

```
PYTHONPATH=/home/jarvis/JARVIS .venv/bin/python -m pytest -q            # expect 2575 passed
PYTHONPATH=/home/jarvis/JARVIS .venv/bin/python -m evals.runner         # expect 12/20, same eight
PYTHONPATH=/home/jarvis/JARVIS .venv/bin/python \
  /home/jarvis/.hermes-poc/evidence/task13b11j-confirmation-foundation/scripts/probe.py \
  | sha256sum                                                           # expect fc68a0b0…
```

## 5. Partial rollback

There is no partial rollback and none is needed: the commit is one module plus its tests plus one
additive line in an allow-list. The module has no internal feature flag because it has no live
effect to flag off.
