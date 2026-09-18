# Task 13B11B — Implementation Record

**Phase:** P0 of the 13B11A integration plan — typed vocabulary and execution-mode flag.
**Production commit:** `521969e051f5cd725415fded0fbc8221e41c842f` (parent `2d7a2ec8…`).
**Runtime effect:** none. Nothing reads the mode; no legacy function was modified.

## 1. What was added

| File | Lines | Purpose |
|---|---|---|
| `app/execution/__init__.py` | 6 | package docstring stating the package is not reachable from the request path |
| `app/execution/types.py` | 383 | the contract vocabulary: 13 enums, 8 frozen records, the frozen obligation priority table, one serialization helper |
| `app/config.py` (modified, +76) | — | `ExecutionConfig`, `normalize_execution_section`, the `execution` field on `Settings`, and the normalization step in `load_settings` |
| `config.yaml` (+9) | — | explicit `execution:` block with `mode: "legacy"` |
| `config.yaml.example` (+9) | — | the same block, documented for operators |
| `tests/execution/{types,config,non_activation}_test.py` + `__init__.py` | 490 | 66 tests |

Total: 9 files, 973 insertions, **0 deletions**. The change is purely additive apart from four
insertion points inside `app/config.py`.

## 2. Design decisions and why

**The vocabulary lives in `app/execution/types.py`, not in `app/brain/`.** These are control-plane
concepts. Keeping them in one package makes the trust boundary reviewable in one place, exactly as
`TARGET_COMPONENT_MAP.md` specified.

**Enums are `str`-mixin enums with the contract's own spellings** (`TOOL_SUCCESS`,
`REQUEST_CONFIRMATION`, …). Stable machine-readable values matter because these strings will appear
in audit records from P1 onward, and a rename later would silently break log queries. Values were
taken from `agent-execution-contract.yaml`, not re-derived.

**`MODEL_RAW` is absent from `OperationalResponseSource` by construction.** There is no enum member
on the operational lane meaning "the model said so"; the only place the token exists is
`ConversationalResponseSource.MODEL_RAW`. That is the type-level third of the raw-prose lock
described in the integration plan §5, arriving before the pipeline and audit thirds.

**`TrustClass` is separate from `ProvenanceSource`.** The question a response template must answer is
"may I state this as observed?", and one field answers it. The test suite asserts the two value sets
do not overlap, so a source can never be mistaken for a trust level.

**`facts` on `TrustedToolResult` is a mapping of explicitly returned values.** It is what makes the
minimal-result principle enforceable in P6: a response may state a value only if the key is present.
`SUCCESS` with empty `facts` is legal and means "it ran and returned nothing to report".

**`ObligationDecision` is an addition, not a rename.** The contract's `ResponseObligation` is the
enum of the eleven families; the C5 evidence showed the *decision* also needs a priority and a
reason, so the record that carries all three is named `ObligationDecision`. The contract name is
used for the contract concept.

**One helper function, `to_mapping`.** `dataclasses.asdict` cannot serialize the read-only mappings
these records use (it fails with `cannot pickle 'mappingproxy' object`), and P1 needs exactly one
obvious conversion to an audit record rather than one per call site. It converts enums to values and
datetimes to ISO-8601 strings; it holds no policy.

## 3. Deliberately not implemented

Routing, canonicalization, permissions, confirmation, dispatch, provenance storage, obligation
selection, response construction, Hermes adapter, shadow mode, new audit events, and any
constructor restriction on `TrustedToolResult` (that lands with `dispatch.py` in P5). No C3/C4/C5
harness file was copied; the concepts were re-implemented as production types.

## 4. Boundary compliance

* No operational call path switched: `app/server.py`, `app/brain/router.py`, `app/brain/tool_params.py`,
  `app/brain/response_cleaner.py`, `app/tools/registry.py`, `app/computer/safety.py`,
  `app/logs/audit.py`, `app/resource_manager.py` and `app/main.py` are byte-identical to `2d7a2ec8`.
* No tool, `SAFETY_LEVEL`, MCP server, model assignment or lifecycle behaviour was touched.
* `agent.hermes_enabled` remains `false` and is still read only by the legacy code that already
  read it.
* CI runs Python 3.11; the new modules were compiled and exercised under 3.11 as well as the
  production 3.14 venv.
