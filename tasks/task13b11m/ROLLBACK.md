# Rollback

Production rollback is one focused revert:

```bash
cd /home/jarvis/JARVIS
git revert --no-edit 4885c4f7ca35f2395fab3497e6ce009d36b742be
```

This removes the passive builder and focused tests and restores the prior non-activation
assertion. No runtime flag, database, persisted confirmation, provenance ledger, audit schema,
tool registry, service, or evidence bundle requires migration.

After rollback verify:

- HEAD's parent chain returns to `8a70d179…`;
- `app/execution/response.py` is absent;
- full pytest returns to 5,122 passed / 11 deselected;
- golden stays 12/20 with the same failures;
- legacy probe remains `fc68a0b0…d98291`;
- `execution.mode` is `legacy` and both Hermes flags remain false.

Do not delete or modify the sealed evidence bundle; it is historical audit evidence even after a
revert.
