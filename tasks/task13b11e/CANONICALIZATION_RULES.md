# Task 13B11E — Canonicalization Rules

Production module: `app/execution/canonicalize.py`. Location from the target component map.

## 1. The rule table at version "1"

| Rule id | Tool | Field | Canonical | Match policy | Aliases |
|---|---|---|---|---|---|
| `apps.app.vscode` | `apps` | `app` | `vscode` | `EXACT_CASEFOLD_TRIMMED` | `vscode`, `vs code`, `visual studio code` |

**One rule. That is the whole reach of version 1** — `declared_scopes()` returns
`(("apps", "app"),)` and nothing else.

## 2. Why this rule and no other

Two independent grounds, both pre-existing:

* Contract §9.2 records it as the validated map — "an exact, case-insensitive alias lookup on one
  field: `vs code` / `visual studio code` / `vscode` → `vscode`" — and calls it an example of the
  rule shape rather than a production requirement.
* Production **already performs this substitution today**: `extract_app_name`
  (`app/brain/tool_params.py`) lower-cases the message and replaces `"visual studio code"` with
  `"vscode"`. Gap G-07 records that as canonicalization happening with the raw value thrown away and
  only the final `params` audited.

So the rule is not new behaviour being invented; it is behaviour production already has, made
explicit, scoped, versioned and raw-preserving — which is precisely what closes G-07.

No alias was added because it appeared in a benchmark run. `PyCharm`, `Sublime Text`,
`IntelliJ IDEA` and `JetBrains Rider` appear in the tests only as values that must come back
unchanged.

**If the operator prefers an empty initial table**, emptying the `RULES` tuple disables all
canonicalization without touching a line of logic, and every other test still passes except the
alias ones. That is a one-line, data-only change.

## 3. The single transformation class

`EXACT_CASEFOLD_TRIMMED`, named on the rule rather than implied, so a second policy would be a
visible versioned addition:

| Step | Behaviour |
|---|---|
| lookup key | `value.strip().casefold()` |
| match | exact membership in the rule's declared alias set |
| on match | the value is replaced by the rule's declared canonical string |
| on no match | the value is returned **untouched** — original case, original spacing |

Aliases are stored already normalized, and a test asserts each alias equals its own lookup key, so
an unreachable alias cannot be added by accident.

## 4. Case

Only a *recognized* alias is case-folded. `VS CODE` → `vscode`; `My Custom App` stays
`My Custom App` and never becomes `my custom app`. Nothing is lower-cased globally — which is the
one place the new module deliberately differs from the legacy `extract_app_name`, whose global
lower-casing is extraction behaviour rather than canonicalization.

## 5. Whitespace

Leading and trailing whitespace is ignored **when comparing against an alias**, and that tolerance
is part of the declared, versioned match policy. It is not applied to values generally: an unknown
value keeps its spacing exactly, including `"  My Custom App  "`. No internal whitespace is ever
collapsed — `"vs  code"` (two spaces) is not an alias and is returned unchanged.

## 6. What has no rule, and therefore is preserved exactly

| Kind | Behaviour |
|---|---|
| URLs (`browser.url`) | exact. No scheme insertion, host rewriting, slash normalization, query sorting, path lower-casing or tracking-parameter removal |
| Paths (`files.path`) | exact. No `~` expansion, no `realpath`, no resolution, no existence check — the filesystem is never touched |
| Deploy targets | exact. `prod` does **not** become `production`, `stage` does not become `staging` |
| Shell commands | exact, including internal spacing and quoting |
| Every other tool and field | exact |

## 7. Scoping is part of the rule

Each rule names its tool **and** its field, and lookup is keyed on the pair. `Visual Studio Code`
passed as `browser.app`, `files.app` or `apps.query` is returned unchanged. There is no global
string-replacement table and no tool-independent alias.

## 8. No runtime learning

`RULES` is a tuple, `RULE_INDEX` a `mappingproxy`, each `AliasRule` is frozen with a `frozenset` of
aliases. Nothing observes model output, user behaviour, ledger history, prior tool success, the
environment or benchmark results. There is no cache that could change a decision.
