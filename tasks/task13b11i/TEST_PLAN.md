# Test plan

462 new tests across three files, all passing. `pytest -q` 2113 → 2575.

## `permissions_test.py` — 330 tests

1. **The table is the signed-off matrix.** The frozen `policy-table.json` is committed next to the
   tests; its digest is recomputed, and all 40 rows are compared field for field, one test per row.
   Row count, unique keys, no wildcard, no extra or missing key, every reviewed registry module
   covered, every unregistered row denying, and the table and its index proven immutable.
2. **Every row decides its signed-off outcome** — one test per row, plus per-row checks that
   `confirmation_required` is derived rather than stored and that only `ALLOW` is dispatchable.
3. **Structural gates** — `NONE`, `UNKNOWN_ACTION`, `MULTI_ACTION_UNSUPPORTED`, the three
   unavailable actions against four capabilities each, unresolved target, action/capability
   mismatch in both directions, and eight near-miss capability strings.
4. **Invalid input versus valid-but-denied** — every member of all seven enums rejected as a
   capability, twelve malformed field shapes, non-request objects, and the confirmation that a
   denied-but-valid request still returns a decision.
5. **Determinism** — 200 repeated calls, frozen decisions, frozen requests, and the proof that
   argument values (including `{"outcome": "ALLOW"}` and `{"safe": True}`) never move a result.
6. **Constraints** — the only constraint in v1, unsatisfied denies and names itself, satisfied is
   still recorded, and unsatisfied always implies `DENY` across the whole table.
7. **`tighten()` in isolation** — every (outcome × class × mode) triple, mode monotonicity, and the
   frozen approval-mode table asserted cell by cell.
8. **Audit compatibility** — the mapping carries what a `permission.decision` event needs, is JSON
   round-trippable, and contains no deliberation field.

## `permissions_decisions_test.py` — 46 tests

One named test per operator decision, at least three for each of D-01…D-09. Highlights: app launch
is not `ALLOW` under any mode; overwrite stays denied under every mode and every misleading
argument; six URLs — loopback, localhost, two private ranges, link-local and a public address — all
deny without the egress constraint, including the public one, because the engine does no network
reasoning; `DENY` never becomes anything else for any row under any mode; every decision carries
`policy_version == "1"`.

## `permissions_non_activation_test.py` — 86 tests

1. **No live wiring** — no importer anywhere under `app/`, no call site, fourteen public symbols
   each with zero references outside the module, eleven named live-path modules clean, and the
   package `__init__` not exporting it.
2. **Purity** — a forbidden-construct scan over *executable code only* (comments and string
   literals stripped by `tokenize`, because the docstring legitimately names what the module
   refuses to do), the exact import set, no `except` clause at all, and a CPython audit hook over
   360 decisions observing zero sensitive events.
3. **Model non-authority** — no field a model could fill, `ModelDraft` and `ToolProposal` rejected
   as arguments, and seven claim strings that change nothing.
4. **Permission is not confirmation** — no confirmation machinery in executable code, no class
   named for it, and six affirmative words that are not read as approval.
5. **The rest of the control plane is untouched** — schema v3 intact at seventeen fields, `lane`
   still not among them, `ProvenanceSource` still eight members with no `TIMEOUT`, the shared enums
   unextended, no parallel `CONFIRM`, and the router, classifier and canonicalizer entry points
   monkeypatched to raise while the whole table is decided.

## Regression baselines

| | before | after |
|---|---|---|
| `pytest -q` | 2113 passed, 11 deselected | 2575 passed, 11 deselected, 0 failed |
| `tests/execution` | 1696 | 2158 |
| golden | 12/20, eight named failures | identical |
| legacy probe | `fc68a0b0…` | byte-identical |
