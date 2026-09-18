# Task 13B11E — Test Plan and Results

116 new tests (106 + 10); `tests/execution` totals 341.

| File | Tests | Covers |
|---|---|---|
| `tests/execution/canonicalize_test.py` | 106 | rule vocabulary, aliases, unknown values, no-fuzzy, scoping, URL/path preservation, immutability, determinism, invalid input, audit and `ToolInvocation` compatibility |
| `tests/execution/canonicalize_non_activation_test.py` | 10 | no live wiring, purity, no provenance contact, frozen enums and schema untouched |

## 1. Rule vocabulary

The table is written out literally in the test rather than derived from the module, so changing a
rule fails a test instead of passing one. Asserted: the version literal `"1"` and its type; the
exact rule set; rule-id uniqueness; no alias mapping to two canonical values within a scope; every
alias stored in its own lookup form (so an unreachable alias cannot be added); every rule declaring
tool, field, canonical value and match policy; `RULES` a tuple, `RULE_INDEX` a read-only mapping,
each rule frozen and its alias set a `frozenset`; and `declared_scopes() == (("apps", "app"),)`.

## 2. Authorized aliases

Nine parametrized forms — the three declared aliases plus case variants (`VS Code`, `VSCODE`,
`Visual Studio Code`, `vS cOdE`) and whitespace-padded forms — all canonicalize to `vscode` while
the raw value is retained. An already-canonical value reports no change; a changed value reports the
rule id, tool, field, raw value and canonical value that fired.

## 3. Unknown values

Ten parametrized unknowns (`PyCharm`, `Sublime Text`, `IntelliJ IDEA`, `JetBrains Rider`,
`My Custom App`, `notepad`, `Firefox`, `Terminal`, empty and whitespace) all come back identical
with no rule applied. A separate test asserts case and spacing survive: `"  My Custom App  "` is
returned exactly, never `"my custom app"`.

## 4. No fuzzy matching

Fifteen parametrized near misses — `VS Cod`, `Visual Studio Cod`, `vscod`, `vs  code`, `vs-code`,
`vs_code`, `vscode2`, `visualstudiocode`, `code`, `Visual Studio`, `vs code editor`,
`the vs code app`, `VSCode Insiders`, `visual studio`, `v s code` — none canonicalize. A static test
asserts `difflib`, `rapidfuzz`, `fuzzywuzzy`, `Levenshtein`, `numpy` and even `re` are not imported,
that `get_close_matches`, `SequenceMatcher`, `ratio(`, `startswith(` and `endswith(` do not appear,
and that alias recognition is set membership.

## 5. Scoping

Six tools and six fields are parametrized: `Visual Studio Code` under `browser`, `files`, `shell`,
`web_search`, `vision` or `apps_v2`, and under `apps.query`, `apps.application`, `apps.name`,
`apps.app_name`, `apps.target` or `apps.command`, is never transformed. One test shows the scoped
field canonicalized while its neighbours in the same call — including a `query` containing the same
words — are left alone.

## 6. URLs, paths and other sensitive values

Five URLs (mixed case, double slashes, fragment, scheme-less, tracking parameter), six paths
(`~/Downloads`, a `..` segment, a relative path, a Windows path, a trailing slash, bare `~`), four
deploy targets (`prod`, `stage`, `Production`, `staging `) and a shell command with irregular
internal spacing all come back byte-identical with no rule applied. No filesystem call is made.

## 7. Raw preservation and immutability

The input mapping is unchanged both when a value changes and when nothing does. Raw and canonical
are distinct read-only mappings. Nested mappings and lists are copied, so mutating the caller's
nested dict afterwards does not reach either side, and the copies cannot be written through. The
result object is frozen.

## 8. Determinism

Fifty repeated calls produce an identical serialization, version, changed-field tuple and applied
rule list. Key order is preserved so `json.dumps` is stable. A static test asserts the module's
imports are exactly `__future__`, `dataclasses`, `types` and `typing` — no clock, no environment, no
locale, no I/O.

## 9. Invalid input

Five bad tool names and five non-mapping argument objects raise `CanonicalizationError` naming the
problem; non-string keys raise. Six non-string values in the scoped field pass through unchanged,
because deciding an argument has the wrong type is validation. Empty arguments are legal. An unknown
tool is not an error.

## 10. Audit and `ToolInvocation` compatibility

One test builds a P1 `dispatch.invoked` record from the result and asserts the serialized entry
carries distinct `raw_arguments` and `canonical_arguments` plus
`canonicalization_version: "1"`, and round-trips through JSON — with no event emitted. Another
builds a P0 `ToolInvocation` from the result and asserts both argument forms and the version
survive `to_mapping`, with no dispatch. A third asserts the `ToolInvocation` type still has those
three fields and was not widened.

## 11. No live wiring

No module outside `app/execution/` names any of eight canonicalizer symbols; there are zero
`canonicalize(` or `CanonicalizationResult(` call sites in `app/`; `canonicalization_version`
appears only where P0 and P1 declare it as a field; `server.py`, `router.py`, `tool_params.py`,
`prompts.py`, `response_cleaner.py`, `registry.py`, `safety.py`, `resource_manager.py`,
`logs/audit.py` and `observability/tracing.py` contain no reference; the module imports nothing from
`app.*` and uses no `eval`/`exec`/`open`/`__import__`/`getattr`/`setattr`; no identifier in it
matches provenance, ledger, trust or audit; there is no module-level mutable state; the P1 audit
schema still has 17 fields, 17 events and version 3, with `lane` still not among the fields; the
frozen `ProvenanceSource` still has its 8 members with no TIMEOUT source; and canonicalizing with
the legacy audit writer monkeypatched to raise proves it is never called.

## 12. Results (production venv, Python 3.14.4)

| Run | Before (b9a557b) | After (e743243) |
|---|---|---|
| `pytest -q` | 642 passed, 11 deselected, 0 failed | **758 passed, 11 deselected, 0 failed** |
| `tests/execution` | 225 passed | 341 passed |
| `evals.runner --mode deterministic` | 12 passed / 8 failed | **12 passed / 8 failed, same eight IDs** |
| legacy probe | sha256 `fc68a0b0…` | **sha256 `fc68a0b0…` — byte-identical** |

Collection 758/769 with 11 deselected by the `pytest.ini` marker expression, unchanged. No new
failures. The eight known golden failures are unchanged: `calendar-move-event-002`,
`habit-status-001`, `habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.
