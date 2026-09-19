# Task 13B11H — Router API

`app/execution/router.py`. Everything below is passive: holding a result changes nothing,
and nothing in `app/` calls any of it.

## 1. The one entry point

```python
route(request: str,
      classification: Classification,
      context: RouterContext = DEFAULT_ROUTER_CONTEXT) -> RouteResult
```

Pure, deterministic, total over valid input, side-effect free. No clock, no filesystem, no
network, no subprocess, no environment, no settings, no session, no registry, no model.

## 2. Input model

**`request`** — the raw text. Segmented and matched; never rewritten, and never used to look up
policy.

**`classification`** — the `Classification` produced by `app/execution/classifier.py`. Required,
with no default: an implicit one would let a caller that forgot to classify still obtain a route.
`route` never calls `classify()`.

**`context`** — the capability projection:

```python
@dataclass(frozen=True, slots=True)
class RouterContext:
    supported_actions: frozenset[PrimaryAction] = SUPPORTED_ACTIONS
```

`TARGET_COMPONENT_MAP.md` lists a capability registry among the router's inputs; passing it in
keeps the router passive — it never imports `app/tools/registry.py` and never reads live tool
inventory. Members must be real operations: `NONE`, `UNKNOWN_ACTION` and
`MULTI_ACTION_UNSUPPORTED` are rejected, because an outcome is not a capability. An action outside
the set becomes `UNKNOWN_ACTION` with reason `action_not_in_capability_set` (§13.1), never a
silently dropped request.

## 3. Result

```python
@dataclass(frozen=True, slots=True)
class RouteResult:
    primary_action: PrimaryAction          # from app.execution.types — never redefined
    reporting_intent: ReportingIntent      # from app.execution.types — never redefined
    target: str | None                     # the operand after the frozen strips
    raw_target: str | None                 # the operand exactly as written
    target_resolved: bool | None           # whether the action's target rule was satisfied
    multi_action: bool
    detected_actions: tuple[PrimaryAction, ...]
    capability_available: bool
    reason: RouteReason
    selected_clause: str | None
    reporting_clause: str | None
    clauses: tuple[str, ...]
    clause_analysis: tuple[ClauseAnalysis, ...]
    router_version: str = "1"
```

Fourteen fields, each traceable to contract §5.2's five concepts plus the auditability §5.3
requires. `to_mapping()` serializes to plain JSON-safe data for future audit use; no audit event is
emitted here.

## 4. What the result does not contain

No tool name, no registry key, no Python callable, no MCP identifier, no tool result, no permission
class, no permission outcome, no confirmation state, no `Lane`, no `ApprovedOperationalResponse`,
no execution status, no dispatch callback, no canonical arguments, no provenance. Asserted against
a forbidden-name list over both `RouteResult` and `ClauseAnalysis`, and by a test that no field
value is callable.

## 5. Per-clause detail

```python
@dataclass(frozen=True, slots=True)
class ClauseAnalysis:
    text: str          core: str          kind: ClauseKind
    primary_action: PrimaryAction         raw_target: str | None
    target: str | None target_resolved: bool | None      reason: RouteReason
```

`ClauseKind` is `ACTION`, `REPORTING`, `NEGATED` or `NONE`, decided in that frozen order.
Contract §5.3 requires the segmentation to be auditable; keeping the per-clause analysis is how a
route can be explained after the fact without re-running anything.

## 6. Vocabulary

| Symbol | What it is |
|---|---|
| `ROUTER_VERSION` | `"1"` — routing-semantics version. Changing the lexicon, grammar, target rules or selection order bumps it. |
| `RouteReason` | 17 members. Metadata: grants no permission, selects no tool, creates no provenance. |
| `SUPPORTED_ACTIONS` | the five operations contract §6.1 validated. |
| `NON_OPERATION_ACTIONS` | `NONE`, `UNKNOWN_ACTION`, `MULTI_ACTION_UNSUPPORTED`. |
| `ACTION_BEARING_CLASSES` | the four request classes that can carry an action. |
| `RouterError` | a `ValueError`. Raised for malformed input; there is no fallback route. |

Helpers `normalize`, `split_clauses`, `connectors_present`, `reporting_intent` and
`analyze_clause` are exported so tests and later phases can inspect the segmentation without
re-deriving it.

## 7. Errors

`RouterError` for: a non-string request; any `Enum` passed as the request (`PrimaryAction`,
`ReportingIntent` and `RequestClass` all subclass `str`, so a member would otherwise be segmented
like prose — the 13B11G lesson); an empty or whitespace-only request; a `classification` that is
not a real `Classification`, including a duck-typed look-alike; a `context` that is not a
`RouterContext`; a capability set that is not a set of real operations.

None of these returns `PrimaryAction.NONE`. `NONE` is a routing outcome for a well-formed request,
not an error channel.
