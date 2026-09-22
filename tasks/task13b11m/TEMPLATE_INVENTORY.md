# Template Inventory

Deterministic user-facing templates are part of this builder. They were frozen before the module
and identified by:

```text
tests/execution/response_templates.json
SHA-256 657443b39cb49b93207358f1a895ceaba487898750c84be8204fbc19f4e37d1b
28 templates
```

Families: confirmation, error, timeout, success, five target clarifications, multi-action limit,
four capability/refusal reasons, six attributed ledger-value sources, generic and attributed fact
acknowledgements, generic and attributed unverified status, intent without execution, and missing
context.

No response/template version field was introduced. Task 13B11A defines none; the frozen inventory
digest is the audit identity. Wording was not tuned against golden results, which remain unchanged.

Templates do not include opaque confirmation IDs, raw/canonical arguments, arbitrary result
facts, error messages, paths, internal identifiers, model text, or candidate targets.
