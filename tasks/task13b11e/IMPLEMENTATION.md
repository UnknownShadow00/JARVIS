# Task 13B11E — Implementation Notes

Production phase **P3 (first unit)** of `tasks/task13b11a/IMPLEMENTATION_PHASES.md`. Passive and
unwired: the canonicalizer exists, is fully tested, and nothing calls it.

Production commit `e7432431b5aaa18eb692b94a5520bdb9184dde62` on `main` in `/home/jarvis/JARVIS`,
parent `b9a557b4460daf240cc26f6ae932db476a5c4315` (13B11D, P2 provenance). Three files added,
**970 insertions, 0 deletions, 0 files modified**. Not pushed.

## 1. What was added

| File | Lines | sha256 |
|---|---|---|
| `app/execution/canonicalize.py` | 270 | `80b3a9c3974723f0a52d4ffd7cab0756a272f6b4c6bb507397e5336c1123abde` |
| `tests/execution/canonicalize_test.py` | 491 | `ca763c53b440560c8944d07b58bd4b89aa5b385207017e5ee69bb5849f292559` |
| `tests/execution/canonicalize_non_activation_test.py` | 209 | `10b49a1bb0ffb93ebd1104b7b8a91246ecb330f9e76995e410511ec443f69095` |

Public surface: `AliasRule`, `AppliedRule`, `CanonicalizationResult`, `CanonicalizationError`,
`canonicalize`, `rules_for`, `declared_scopes`; constants `CANONICALIZATION_VERSION`,
`MATCH_EXACT_CASEFOLD_TRIMMED`, `RULES`, `RULE_INDEX`.

## 2. Design decisions and why

**The rule table is data, not code.** `RULES` is a tuple of frozen `AliasRule` records, indexed once
at import into a read-only `RULE_INDEX` keyed by `(tool, field)`. Adding, changing or removing a
rule is a data edit; emptying the tuple turns canonicalization into the identity function without
touching a line of logic. That is the cheapest possible rollback and it is why the rule table was
not expressed as `if` branches.

**One rule, and it was not invented.** The table holds exactly the alias the frozen contract §9.2
records as validated — `vs code` / `visual studio code` / `vscode` → `vscode` on `apps.app` — which
is also the substitution production already performs today inside `extract_app_name`, discarding the
raw value as gap G-07 records. Every rule in the table is therefore grounded in two pre-existing
sources. The spec's instruction not to invent a broad alias library was taken literally: no editor,
browser, URL, path, deploy-target or shell-command rule was added.

**Matching is set membership, deliberately.** `_lookup_key` is `value.strip().casefold()` and
`AliasRule.matches` is `_lookup_key(value) in self.aliases`. There is no regex — the module does not
import `re` — no prefix or suffix test, no substring test, and no similarity scoring. A static test
asserts `difflib`, `rapidfuzz`, `fuzzywuzzy`, `Levenshtein` and `numpy` are absent, and that
`startswith(`, `endswith(`, `SequenceMatcher` and `get_close_matches` do not appear in the source.
`VS Cod` and `vs-code` are unknown values and are returned untouched.

**Raw and canonical are both first-class.** `CanonicalizationResult` carries `raw_arguments` and
`canonical_arguments` as two separate read-only mappings plus `version` and the `applied_rules` that
fired. This is INV-006 in structural form: the arguments the model proposed can never be
overwritten by the arguments that would run. `_copy_value` deep-copies nested mappings into
`MappingProxyType` and sequences into tuples, so a caller mutating its own nested dict afterwards
cannot reach either side, and neither side can be written through.

**Unknown values are preserved exactly, including case and spacing.** `"  My Custom App  "` comes
back as `"  My Custom App  "`. Normalization is only ever the *lookup* key, never the output. This
is what keeps INV-005/INV-011 true: an unrecognized target stays unrecognized so the router and the
response layer must report it rather than substitute a near neighbour.

**Errors are for undescribable input only.** A non-string or empty `tool_name`, a non-mapping
argument object, or non-string keys raise `CanonicalizationError`. An unknown tool, an unknown
field, an empty argument mapping and a non-string *value* in a scoped field are all legal and pass
through untouched — deciding that an argument has the wrong type is validation, which belongs to
P4/P5, not here.

**Zero application imports.** The module imports exactly `__future__`, `dataclasses`, `types` and
`typing`. Not the settings object, not the registry, not the audit writer, not the provenance
ledger. That is why no test can claim a hidden side effect: there is no reachable code to have one.
Purity was measured too — 500 identical calls produced one distinct output with the input mapping
unmodified.

**`AppliedRule` grants nothing.** It records which rule fired for a reviewer's benefit. It is not a
trust signal, it is not provenance, and P6 must not read it as authority for a claim.

## 3. What was deliberately not done

No wiring into any request or dispatch path; `app/brain/tool_params.py` is byte-identical, so the
legacy extraction still runs exactly as before. No classifier, router, lane policy, permission
engine, confirmation machine, dispatcher wrapper, obligation engine or Hermes adapter. No audit
event emitted and no audit schema change. No provenance interaction. No widening of the frozen P0
`ToolInvocation`, which already had `raw_arguments`, `canonical_arguments` and
`canonicalization_version` and was used as it stands. `ProvenanceSource` was **not** extended for
TIMEOUT. The three operator decisions named in the spec — lane as an audit field, the redaction
secret-key list, TIMEOUT as a provenance source — were left open, and a test asserts they are still
in their pre-task state (schema version 3, 17 contract fields with `lane` absent, 8 provenance
sources).

## 4. Verification

`pytest -q` went 642 → **758 passed**, 11 deselected, 0 failed; `tests/execution` 225 → 341; the 116
new tests pass on their own. The deterministic golden ran 12/20 before and after with the same eight
failing IDs. The legacy probe, carried byte-identically from 13B11B/C/D
(`bb4624f9…`), produced `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291` at
`b9a557b` before installation and the identical digest at HEAD after the commit — captured by
checking out the parent commit in a detached worktree, not by re-running the same tree twice.

All 18 critical production files hash identically before and after. `canonicalize(` call sites
outside the module: 0. `canonicaliz` outside `app/execution/`: 0. `app.execution` outside the
package: 1, the P0 line `app/config.py:14`. Execution mode `legacy`, `hermes_brain=False`,
`hermes_enabled=False`; Hermes at `2237be35`, clean, 0 processes; shared Ollama `{"models":[]}`
throughout — no model was loaded for this task.
