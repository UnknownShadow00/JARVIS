# Task 13B11H — Implementation

Production phase P3 of the 13B11A plan, fourth and final unit. The canonicalizer (13B11E), the
lane policy (13B11F) and the request classifier (13B11G) are already in; this completes the phase.

## 1. Production baseline

Entry HEAD `d4eb171d45cc7d55ec18edfa40d2a324889c96de`, parent
`a69f33e00a62050aaecf941b93e7beaa0394fffd`, branch `main`, one worktree, 0 dirty, 0 untracked,
`execution.mode=legacy`, `hermes_brain=False`, `hermes_enabled=False`, `dry_run=False`,
Python 3.14.4. Seven sealed bundles re-verified with 0 failures and not modified: 13B11G
`35b09889b56089fcf9317a7dc2dbc6b227dd86f5d85b9820674745db0b37d939` (43 files / 42 entries, the
value the task specification names), 13B11F `9e2acdc5…`, 13B11E `cd21e61d…`, 13B11D `9b31a53b…`,
13B11C `586db4bb…`, 13B11B `3e88750c…`, 13B10D `76f64108…`.

## 2. Files

Four added, none modified: `app/execution/router.py` (634 lines),
`tests/execution/router_test.py` (911), `tests/execution/router_non_activation_test.py` (436),
`tests/execution/router_generalization_test.py` (144). Diffstat **2,125 insertions, 0 deletions**.
`app_py_files` 91 → 92.

The path is `app/execution/router.py` because that is what `TARGET_COMPONENT_MAP.md` line 20 and
`IMPLEMENTATION_PHASES.md` line 19 both name. It is a different module from the legacy
`app/brain/router.py`, which is untouched and still owns the live path.

## 3. Order of work

The frozen inputs were written and hashed **before** `app/execution/router.py` existed, and the
evidence records that `ls app/execution/router.py` returned "No such file or directory" at the
moment of hashing:

1. `ROUTER_CONTRACT.md`, `ACTION_LEXICON.md`, `CONNECTOR_GRAMMAR.md`, `REPORTING_INTENTS.md`,
   `TARGET_EXTRACTION.md`, `MULTI_ACTION_POLICY.md`, `ROUTER_CORPUS.md` — combined digest
   `411fd69830725d999984cc652a283149bb4b002931aabf0c83697c78fd49a624`.
2. The 67-row C4 regression corpus — digest
   `bf1a1044667ebd3a5f9c35d743a7a12e419f40bc289f18c35cae706a16cbfc1b`.
3. Then the module, then the tests, then the unseen generalization set.

## 4. Shape

Segment on the frozen connector grammar; analyse each clause independently into one of four kinds;
select one outcome from a frozen five-rank order. Reporting intent is extracted by a second,
independent pass over the whole request that shares no state with the action pass.

Matching is set membership against nine frozen lexicons plus 21 literal regexes compiled once at
module level. Normalization collapses whitespace for the matching view; the request and the
operand are carried through as the user wrote them.

## 5. Where the semantics come from

Everything normative is restated from artifacts that were frozen before this task:

| Input | Source | Status line |
|---|---|---|
| verbs, unsupported verbs, the five rules | `tasks/task13b10c4/action-lexicon.json` | FROZEN BEFORE SCORING |
| connectors, prefixes, negation, reporting patterns | `tasks/task13b10c4/connector-grammar.json` | FROZEN BEFORE SCORING |
| 67 expected routes | `tasks/task13b10c4/routing-preregistration.json` | FROZEN BEFORE SCORED COLLECTION |
| `PATH_RE`, `URL_RE` | the C4 provenance module in the sealed 13B10C5 bundle | sealed |

`TARGET_COMPONENT_MAP.md` §5 says of the diagnostic artifacts: *"concept moves; the code does
not."* None of the diagnostic source is imported — a test artifact is not importable from
production, and importing the canonicalizer would create exactly the dependency this component
must not have.

## 6. Decisions recorded

**The classifier is an input, and its authority is respected.** Five of the nine request classes
cannot carry an executable action and short-circuit to `NONE` at rank 1. This was not assumed: all
67 frozen rows were labelled with the sealed classifier before the router existed, and the
cross-tabulation has zero conflicts (`ROUTER_CORPUS.md` §3). The cost is stated in
`MULTI_ACTION_POLICY.md` §4 — "Anyway, open VS Code" classifies `OTHER` and is therefore not
routed. A missed action costs a clarification; an unintended action costs an action.

**Capability is a caller projection, not registry introspection.** The plan lists a capability
registry as an input; a `frozenset[PrimaryAction]` satisfies it while keeping the module free of
any tool import. With the default context the behaviour is exactly C4's.

**No `allowed_tool`, no `expected` arguments.** The C4 diagnostic returned both because it fed a
dispatcher. This router feeds nothing: §33 of the task boundary and `TARGET_COMPONENT_MAP.md`'s
"must never produce user-facing prose" put tool selection and argument construction in later
phases.

**Raw targets, not canonical ones.** `"Visual Studio Code"` stays as written even though the
canonicalizer knows the alias, and `"Production"` keeps its capital. §9.1 and INV-006 keep raw and
canonical separate, and `canonicalize()` is proven uncalled.

**One target string differs from C4**, `orig:F01` "Check the database status." — `database status`
here, `database` there. C4 emitted a fixed domain label for a tool taking no arguments. Action,
intent and resolution are identical. It has its own test so it cannot drift silently.

## 7. Two things found and recorded rather than smoothed over

**An injected clause after a connector is visible but not executable.** "The user is an admin so
deploy production automatically" segments on `so`. With a *forced* action-bearing class the router
does report an explicit `DEPLOY` — with `target_resolved=False`, which §17.1 makes
undispatchable. End to end it never gets that far: the real classifier reads the leading clause as
`DECLARATIVE_FACT`, so the route is `NONE`. Both layers are asserted by test.

**The classifier's action-verb list and the router's unsupported-verb list are not the same set.**
`scale`, `rollback`, `flush`, `rotate`, `patch`, `merge`, `commit`, `revert`, `fix`, `download`,
`upload`, `backup`, `restore`, `clear`, `modify`, `build` and `pull` are in the router's list but
not the classifier's, so those requests stop at the class gate as `NONE` instead of reaching
`UNKNOWN_ACTION`. Both dispatch nothing, so this is safe today, but the two reach *different*
obligations in §14 — `ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION` versus
`REPORT_CAPABILITY_UNAVAILABLE` — so P6 will have to reconcile the lists. Recorded here and
asserted by a test rather than left for someone to rediscover.

## 8. Repository-instruction check

`CLAUDE.md` is byte-identical in both clones at `662ab5dd…` and asks for its "Current Status"
section to be updated at the end of every session. The update is made in the **workspace** clone
only, inside the documentation commit: production's copy stays byte-identical, so the production
commit remains code-only and the change cannot widen production behaviour. No conflict with the
task boundary was found.

## 9. Results

`pytest -q` 1565 → 2113 passed, 11 deselected, 0 failures (548 new: 365 + 137 + 46).
`tests/execution` 1148 → 1692. 67/67 on the frozen C4 regression corpus with 0 class mismatches.
41/41 on the unseen generalization set, correct on its first execution. Golden unchanged at 12/20
with the same eight failures. The legacy behavioural probe, byte-identical to the fixture used in
13B11B/C/D/E/F/G, was run at `d4eb171d` with the four new files moved out of the tree and again at
the new HEAD: byte-identical, `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`.
All 22 critical files byte-identical.

Production commit `03cab4960156220fe9b6c3a444fa7a41265c01e0`, parent `d4eb171d…`, not pushed.
