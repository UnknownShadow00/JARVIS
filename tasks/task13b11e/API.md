# Task 13B11E — API

`app/execution/canonicalize.py`. Pure functions and frozen data. The module imports nothing from
the application — not provenance, not audit, not the registry, not settings — so its purity is a
property of its import list, not a promise.

## 1. `canonicalize(tool_name, raw_arguments) -> CanonicalizationResult`

The planned signature from the target component map (`tool name, raw args → canonical args,
applied rules`), returned as one frozen result so the version and the raw arguments travel with it.

| Input | Requirement |
|---|---|
| `tool_name` | non-empty string; an unknown tool is **not** an error — whether a tool exists is validation, not canonicalization |
| `raw_arguments` | a mapping with string keys |

Behaviour per field:

* a field with no declared rule → passed through untouched;
* a field with a rule whose value is not a declared alias → passed through untouched, case and
  spacing intact;
* a field whose value is not a string → passed through untouched (type policing is validation);
* a field whose value matches an alias → replaced by the rule's canonical value, and an
  `AppliedRule` is recorded.

## 2. `CanonicalizationResult`

Frozen, with read-only mappings.

| Member | Meaning |
|---|---|
| `tool_name` | the tool the rules were looked up for |
| `raw_arguments` | exactly what came in, copied, never modified |
| `canonical_arguments` | exactly what would run |
| `version` | the rule-set version that produced them |
| `applied_rules` | tuple of `AppliedRule`, empty when nothing changed |
| `changed` | property — whether anything changed at all |
| `changed_fields` | property — the fields whose values differ, in order |
| `to_mapping()` | JSON-safe form with `canonicalization_version` named as the audit field names it |

`applied_rules` is informational. It explains a change; it grants no trust, no permission and no
authority to execute.

## 3. `AppliedRule`

`rule_id`, `tool`, `field`, `raw_value`, `canonical_value` — enough for a reviewer to see which
declared rule fired and on what, without re-running anything.

## 4. `AliasRule` and the table

`AliasRule(rule_id, tool, field, canonical, aliases, match)`, frozen, aliases a `frozenset`.
`RULES` is a tuple; `RULE_INDEX` maps `(tool, field)` to its rules as a `mappingproxy`.
`rules_for(tool, field)` and `declared_scopes()` expose them read-only.

## 5. `CanonicalizationError`

Raised for input that cannot be described: an empty or non-string `tool_name`, a non-mapping
`raw_arguments`, or non-string keys. Never raised for an unknown tool, an unknown value or a value
of an unexpected type — those are pass-through, because canonicalization is not validation.

## 6. Copy semantics

`raw_arguments` and `canonical_arguments` are separate mappings. Nested mappings become read-only
and nested sequences become tuples, so neither side shares mutable structure with the caller or with
the other. Mutating the caller's original dict afterwards cannot change either.

## 7. What the module explicitly does not do

It does not decide whether a tool exists, whether an action is allowed, whether a target is
ambiguous, whether confirmation is required, whether an argument is safe, or whether execution
should occur. It does not read natural language, infer an action or classify intent. Those belong to
the classifier, the router, the permission engine, the confirmation manager and the dispatcher.
