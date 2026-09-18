# TASK 13B11E — FINAL REPORT
## Deterministic argument canonicalizer foundation (production phase P3, first unit)

## 1. Verdict

**JARVIS ARGUMENT CANONICALIZER FOUNDATION IMPLEMENTED**

The contract §9.1 canonicalizer exists in production as a versioned, deterministic, exactly-matching
module that keeps the model's raw arguments and the canonical arguments as two separate values. It
is additive and unwired: no production code path calls it, it imports nothing from the application,
and measured legacy behaviour is byte-identical before and after.

## 2. Prerequisite verification

Production `/home/jarvis/JARVIS` at entry: HEAD `b9a557b4460daf240cc26f6ae932db476a5c4315`
(required), parent `eb4c5db1985033f2c7464fbd1bd3ae9a385199d0`, branch `main`, 0 dirty, 0 untracked,
1 worktree. `execution.mode=legacy`, `execution.hermes_brain=False`, `agent.hermes_enabled=False`.
Hermes `2237be355906fbe6065ce1815711eee52b2d646e`, 0 dirty, 0 processes. Workspace at 13B11D commit
`3a750759fe140458b1f09453325a765128552798`, clean.

Four prior bundles re-verified and not modified — 13B11D 35 files / 34 entries / digest
`9b31a53b03af5caaca87478f89364b3f3b2d8ca830909234d3996966d01431cc`; 13B11C 36 / 35 /
`586db4bbe7254ad8c3ef07ad40dc8871ee8aa9a9eff4178bc870d071877b9a54`; 13B11B 32 / 31 /
`3e88750caa1a74f7091130bb051877ebf5579a1d40c1c730c8c585710bc2f16d`; 13B10D 21 / 20 /
`76f6410896485f8c512391482c81b783ea33ea2bf83fc967b43d0d472db126d0`. `sha256sum -c` on each: 0
FAILED, 0 self-references. The 13B11D digest is the canonical value recorded inside
`tasks/task13b11d/FINAL-REPORT.md` and `tasks/loop-log.md`, not a shortened conversational note.

## 3. Production baseline

Recorded in `03-production-baseline-before.txt` before any P3 file was installed: 18 critical file
hashes, `app_tree_sha256=54a3619610f0ff0c63f0ee1e2e039b5d449b4e56ee0883f6224b618306057ccf`,
`app_py_files=88`, `safety.dry_run=False`, Python 3.14.4.

## 4. P0 / P1 / P2 dependency verification

The canonicalizer consumes the frozen P0 vocabulary and must fit the P1 audit shape, so both were
verified before use. `ToolInvocation` already declares `raw_arguments`, `canonical_arguments` and
`canonicalization_version`, so it was used as it stands and **not widened**. The P1
`ExecutionAuditEvent` set already carries the same three names among its 17 contract fields. P2
provenance was verified only to confirm it stayed untouched. All four files
(`types.py 881eda40…`, `audit_events.py cac2b32c…`, `correlation.py 603674af…`,
`provenance.py f3026921…`) are byte-identical before and after.

## 5. Production files changed

Three added, none modified: `app/execution/canonicalize.py` (270 lines,
`80b3a9c3974723f0a52d4ffd7cab0756a272f6b4c6bb507397e5336c1123abde`),
`tests/execution/canonicalize_test.py` (491, `ca763c53…`),
`tests/execution/canonicalize_non_activation_test.py` (209, `10b49a1b…`). Diffstat: **970
insertions, 0 deletions**. `app_py_files` 88 → 89.

## 6. Canonicalization rule model

`AliasRule` is a frozen slotted record with `rule_id`, `tool`, `field`, `canonical`, a `frozenset`
of `aliases`, and an explicit `match` policy. Rules live in a `RULES` tuple and are indexed once at
import into `RULE_INDEX`, a `MappingProxyType` keyed by `(tool, field)`. A rule is data: adding,
changing or removing one is a table edit, not a logic change.

## 7. Rule table contents

Exactly one rule: `apps.app.vscode` — on tool `apps`, field `app`, aliases `{"vs code",
"visual studio code", "vscode"}` → canonical `vscode`. It is grounded twice over: contract §9.2
records it as the validated example, and production's own `extract_app_name` already performs this
substitution today while discarding the raw value (gap G-07). No broad alias library was invented;
no editor, browser, URL, path, deploy-target or shell rule was added. `declared_scopes()` returns
`(("apps", "app"),)` — one scope, verified by test.

## 8. Match semantics

`MATCH_EXACT_CASEFOLD_TRIMMED`. The lookup key is `value.strip().casefold()` and matching is
`key in rule.aliases` — set membership, nothing else. `re` is not imported. There is no prefix,
suffix, substring, token or similarity test anywhere in the module.

## 9. Scoping

A rule applies only to its declared `(tool, field)` pair. `Visual Studio Code` under `browser`,
`files`, `shell`, `web_search`, `vision` or `apps_v2` is untouched, and under `apps.query`,
`apps.application`, `apps.name`, `apps.app_name`, `apps.target` or `apps.command` is untouched. In
one call, `apps.app` canonicalizes while a sibling `query` containing the same words does not. This
is what keeps INV-011 true: an unsupported action cannot be silently mapped onto an unrelated tool.

## 10. Version constant

`CANONICALIZATION_VERSION = "1"`, a string, asserted literally by test. It travels on every result
and into `to_mapping()` as `canonicalization_version`, which is the field P4 will re-derive against
at approval time (risk R-07) and which makes an audit record replayable against a known rule set.
`VERSIONING.md` records the bump policy: any change to the rule table, the match policy or the
scoping model is a new version.

## 11. Raw argument preservation

`CanonicalizationResult.raw_arguments` is a read-only copy of exactly what was passed in. It is
never overwritten, and it exists whether or not a rule fired. This is INV-006 in structural form:
the arguments the model proposed survive alongside the arguments that would run.

## 12. Canonical argument construction

`canonical_arguments` is built by copying the raw mapping and replacing only the fields a declared
rule matched. Key order is preserved, so serialization is stable. When no rule fires the two
mappings are equal in content but remain distinct objects.

## 13. Unknown value handling

Ten parametrized unknowns — `PyCharm`, `Sublime Text`, `IntelliJ IDEA`, `JetBrains Rider`,
`My Custom App`, `notepad`, `Firefox`, `Terminal`, empty, whitespace — come back identical with
`applied_rules == ()`. Case and spacing are preserved: `"  My Custom App  "` returns exactly that,
never `"my custom app"`. Normalization is only ever the lookup key, never the output.

## 14. No fuzzy matching

Fifteen near misses refuse to match: `VS Cod`, `Visual Studio Cod`, `vscod`, `vs  code`, `vs-code`,
`vs_code`, `vscode2`, `visualstudiocode`, `code`, `Visual Studio`, `vs code editor`,
`the vs code app`, `VSCode Insiders`, `visual studio`, `v s code`. Static proof:
`difflib`, `rapidfuzz`, `fuzzywuzzy`, `Levenshtein`, `numpy` and `re` are not imported;
`get_close_matches`, `SequenceMatcher`, `ratio(`, `startswith(`, `endswith(`, `re.compile`,
`re.sub`, `re.match` and `lower()` all report **0 hits**. The only normalizing calls in the file are
the single `strip()` and `casefold()` on line 75.

## 15. URLs, paths and other sensitive values

Five URLs (mixed case, double slashes, fragment, scheme-less, tracking parameter), six paths
(`~/Downloads`, a `..` segment, a relative path, a Windows path, a trailing slash, bare `~`), four
deploy targets (`prod`, `stage`, `Production`, `staging `) and a shell command with irregular
internal spacing all return byte-identical with no rule applied. No path is resolved, no filesystem
call is made, `Path(` and `open(` report 0 hits.

## 16. Input immutability

The caller's mapping is unchanged whether or not a value was rewritten — asserted both ways, and
again after 500 calls. Nested mappings and lists are copied into read-only forms, so mutating the
caller's nested dict afterwards reaches neither `raw_arguments` nor `canonical_arguments`, and
neither can be written through.

## 17. Result immutability

`CanonicalizationResult`, `AliasRule` and `AppliedRule` are all frozen; `RULES` is a tuple,
`RULE_INDEX` a `mappingproxy`, each rule's `aliases` a `frozenset`. There is no module-level mutable
container, no `global`, no `nonlocal` and no runtime rule learning.

## 18. Determinism and purity

500 identical calls → **1 distinct output**, with the input mapping unmodified. Fifty repeated calls
produce identical serialization, version, changed-field tuple and applied-rule list. Imports are
exactly `['__future__', 'dataclasses', 'types', 'typing']` and **none from `app.*`** — no clock, no
locale, no environment read, no network, no filesystem, no model.

## 19. Invalid input handling

Five bad tool names and five non-mapping argument objects raise `CanonicalizationError` naming the
problem; non-string keys raise. An unknown tool is not an error, an empty argument mapping is legal,
and six non-string values in the scoped field pass through unchanged — deciding that an argument has
the wrong type is validation and belongs to P4/P5.

## 20. Error semantics

`CanonicalizationError` subclasses `ValueError`, so a caller that only knows the standard hierarchy
still handles it. It is raised for input that cannot be described at all — never for input the rule
table simply does not recognize, which is the ordinary pass-through case.

## 21. Applied-rule reporting

`applied_rules` is a tuple of `AppliedRule` records (`rule_id`, `tool`, `field`, `raw_value`,
`canonical_value`), with `changed` and `changed_fields` derived from it. It is informational: it
grants no trust, creates no provenance, and must not be read by P6 as authority for a claim.

## 22. `ToolInvocation` compatibility

A `ToolInvocation` built from a result carries both argument forms and the version through
`to_mapping()` intact, with no dispatch performed. A separate test asserts the frozen P0 type still
declares those three fields and was not widened by this task.

## 23. Audit compatibility

A P1 `dispatch.invoked` record built from a result serializes with distinct `raw_arguments` and
`canonical_arguments` plus `canonicalization_version: "1"` and round-trips through JSON — with **no
event emitted**. Schema-v3 emission sites in production remain **0**; the 204 legacy `audit.log(`
call sites are untouched.

## 24. Serialization

`to_mapping()` returns plain JSON-serializable dicts (no `mappingproxy` leaks), preserving key
order, so repeated `json.dumps` output is stable — the property an audit replay depends on.

## 25. Privacy and no chain-of-thought

The module stores argument values only. It has no field for reasoning, rationale, deliberation or
model thought, and it never sees a model draft. The P1 `FORBIDDEN_REASONING_FIELDS` guard is
unchanged and still enforced by its own tests.

## 26. No provenance interaction

`app/execution/provenance.py` is byte-identical. Provenance writes from `app/`: **0**. Checked on
AST identifiers rather than raw text, the canonicalizer contains no identifier matching
provenance, ledger, trust or audit — the words appear only in the docstring, which states what the
module avoids. Canonicalization asserts nothing and therefore grounds nothing (§3.3).

## 27. Deferred decision — lane as an audit field

Untouched. The P1 contract audit field list is still **17** entries and `lane` is still **not** among
them, asserted by test. The lane policy remains a P3 sibling, not this task.

## 28. Deferred decision — redaction secret-key list

Untouched. `RedactionReason`/`RedactionMarker` are unchanged and no key list was introduced. The
canonicalizer performs no redaction and no secret detection.

## 29. Deferred decision — TIMEOUT as a provenance source

Untouched, and explicitly so. The frozen `ProvenanceSource` still has exactly **8** members with no
TIMEOUT source, asserted by test. The spec's §54 prohibition was honoured: the enum was not
extended.

## 30. Tests — rule vocabulary

The rule table is written out literally in the test rather than derived from the module, so changing
a rule fails a test instead of silently passing. Asserted: version literal and type, exact rule set,
rule-id uniqueness, no alias mapping to two canonical values in a scope, every alias stored in its
own lookup form, every rule declaring tool/field/canonical/match, container types and frozenness,
and the single declared scope.

## 31. Tests — authorized aliases

Nine parametrized forms including case variants and whitespace padding canonicalize to `vscode` with
the raw value retained; an already-canonical value reports no change; a changed value reports the
rule id, tool, field, raw value and canonical value.

## 32. Tests — refusal to guess

Ten unknowns pass through; fifteen near misses refuse; twelve scoping cases (6 tools, 6 fields)
refuse; case and spacing survive.

## 33. Tests — value classes that must never be rewritten

Five URLs, six paths, four deploy targets and one irregular shell command, all byte-identical out.

## 34. Tests — immutability and determinism

Input unchanged on both paths, nested structures copied and read-only, result frozen, 50 repeated
calls identical, imports statically constrained to four stdlib modules.

## 35. Tests — invalid input

Five bad tool names, five non-mapping argument objects, non-string keys → `CanonicalizationError`;
non-string values, empty mappings and unknown tools → legal pass-through.

## 36. Tests — integration shape without integration

Audit-record and `ToolInvocation` compatibility proven by construction and serialization only; no
event emitted, no dispatch, no ledger write.

## 37. No-live-wiring proof

`canonicalize(` call sites outside the module: **0**. `CanonicalizationResult(` outside the module:
**0**. The string `canonicaliz` anywhere outside `app/execution/`: **0**. `app.execution` outside
the package: **1**, the expected P0 line `app/config.py:14`. `canonicalization_version` appears only
where P0 and P1 declare it as a field (`types.py`, `audit_events.py`) — declarers, not callers.
`server.py`, `router.py`, `tool_params.py`, `prompts.py`, `response_cleaner.py`, `registry.py`,
`safety.py`, `resource_manager.py`, `logs/audit.py` and `observability/tracing.py` contain no
reference. Canonicalizing with the legacy audit writer monkeypatched to raise proves it is never
called.

## 38. Existing test-suite result

`pytest -q`: **642 → 758 passed**, 11 deselected, 2 warnings, **0 failed**. `tests/execution`
225 → 341. The 116 new tests pass standalone. Collection 758/769 with the unchanged `pytest.ini`
marker expression.

## 39. Golden before / after

`python -m evals.runner --mode deterministic`: **12 passed / 8 failed before and after**, the same
eight IDs — `calendar-move-event-002`, `habit-status-001`, `habit-complete-002`,
`safety-delete-downloads-001`, `safety-shutdown-002`, `safety-derived-injection-004`,
`clarify-open-target-001`, `clarify-delete-target-002`. No scenario changed direction.

## 40. Legacy behaviour non-change

The probe fixture `scripts/probe.py` (`bb4624f9c9c380add3fb4130ee6ddc00902472ff4c19bad1a8b010478df099d0`,
byte-identical to 13B11B/C/D) ran at `b9a557b` in a detached worktree **before any P3 file was
installed**, and again at HEAD after the commit. Both outputs:
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`, 13,519 bytes — **byte-identical**
and equal to the digest recorded by 13B11C and 13B11D. It covers 10 routed prompts, 18 registry
tools, safety levels `[-1, 0, 1, 2]`, the policy snapshot, prompt keys and cleaner cases. It
includes the case this task is about: `'open visual studio code'` still routes through the legacy
`extract_app_name` to `{'action': 'open', 'app': 'vscode', 'query': 'open visual studio code'}` —
the canonicalizer did not replace it.

## 41. Execution-mode status

`execution.mode=legacy`, `execution.hermes_brain=False`, `agent.hermes_enabled=False`, before and
after. `config.yaml` `247633cb…` and `config.yaml.example` `8f5b2343…` are byte-identical. This
phase does not read the mode flag at all.

## 42. Hermes non-use

Hermes repo `2237be355906fbe6065ce1815711eee52b2d646e`, 0 dirty lines, **0 processes** matching
hermes/uvicorn/app.server. Shared Ollama `/api/ps` returned `{"models":[]}` before and after — no
model was loaded for this task. The string `hermes` appears **0** times in the new module.

## 43. Tool-path non-change

`registry.py e70d4d50…`, `safety.py a41127209…`, `tool_params.py a0664a15…` all byte-identical. The
four `registry.call` sites in `server.py` are unchanged at lines 639, 737, 814 and 858. No tool was
added, removed or re-registered; no tool executed during this task.

## 44. Confirmation, audit and lifecycle non-change

`server.py b1448ed1…` byte-identical, with `_pending_confirmations` and `confirm_request` unchanged
at lines 87/646/792/793. `logs/audit.py 835fb246…`, `observability/tracing.py e6defa78…` and
`execution/audit_events.py cac2b32c…` byte-identical; 204 legacy call sites, 0 schema-v3 emissions.
`resource_manager.py 43e293d0…` byte-identical — no change to model loading, unload timers or the
LIGHT_SLEEP/DEEP_SLEEP lifecycle.

## 45. Security review

Literal-string scan of the new module: `eval(`, `exec(`, `__import__`, `importlib`, `subprocess`,
`os.system`, `popen`, `socket`, `requests`, `httpx`, `urllib`, `open(`, `Path(`, `write_text`,
`pickle`, `yaml.load`, `input(`, `getenv`, `global`, `nonlocal`, `setattr(`, `getattr(` — all
**0 hits**. The single `environ` hit is the docstring line stating the module reads none. No secret,
credential, token or path is stored; the module holds only the argument values it was handed and
persists nothing. No network call, no file handle, no subprocess, no deserialization.

## 46. Contract traceability

§9.1 → INV-006 → `raw_arguments`, `canonical_arguments` and `canonicalization_version` on both the
P0 `ToolInvocation` and the P1 audit event; §9.1's no-fuzzy rule → INV-005 and INV-011 → the absence
of a transformation for unknown values; §9.2 → the single validated alias; §3.3 and §18.1 → INV-002
and INV-003, preserved by the module touching no provenance and no tool. Full matrix in
`TRACEABILITY.md`.

## 47. Rollback

`git revert e7432431…` or `git reset --hard b9a557b` removes exactly the three added files; no other
file was modified. To keep the mechanism but drop the alias, empty the `RULES` tuple — a data-only
edit that makes canonicalization the identity function. No database, audit, provenance, state,
config, model or Hermes rollback is required. Detail in `ROLLBACK.md`.

## 48. Production diff and commit

3 files, 970 insertions, 0 deletions, 0 modifications. Commit
`e7432431b5aaa18eb692b94a5520bdb9184dde62` — `feat: add deterministic argument canonicalizer`,
author `UnknownShadow00 <fastelite0972@gmail.com>`, 2026-09-18 23:21:07 +0000, parent `b9a557b`,
branch `main`, **not pushed**, 4 commits ahead of origin. Full patch in `15-production-diff.patch`.

## 49. Workspace commit and evidence

Workspace commit `docs: record task 13B11E canonicalizer foundation` adds `tasks/task13b11e/`
(`IMPLEMENTATION.md`, `CANONICALIZATION_RULES.md`, `VERSIONING.md`, `API.md`, `TRACEABILITY.md`,
`TEST_PLAN.md`, `ROLLBACK.md`, `FINAL-REPORT.md`, `authorization.txt`) and the `tasks/loop-log.md`
entry. No prior task directory or prior bundle was modified. Evidence sealed at
`/home/jarvis/.hermes-poc/evidence/task13b11e-canonicalizer-foundation/` with numbered artifacts,
`source/`, `scripts/`, `docs/`, `README.txt` and `SHA256SUMS` (excluding itself); `sha256sum -c`
reports **0 failures**. The bundle digest is recorded in `tasks/loop-log.md`, not inside the bundle.

## 50. Final state and recommendation

Production `e7432431…`, `main`, 0 dirty, 0 untracked, 1 worktree, 4 ahead of origin, mode `legacy`.
Hermes `2237be35`, clean, not running. Ollama idle. Workspace clean after the docs commit.

The canonicalizer is the smallest contract unit that can exist without changing behaviour, and it
now exists with 116 tests holding its refusal to guess in place. Recommended next: **the passive
lane policy**, `app/execution/lane.py` — a pure function from request class and capability flags to
a `Lane`, listed in `DEPENDENCY_GRAPH.md` §3 as independently buildable, with no dispatch, no
permissions and no live wiring. It is not started.
