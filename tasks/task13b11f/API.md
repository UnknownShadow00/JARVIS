# Task 13B11F — API

`app/execution/lane.py`. Import path `from app.execution.lane import ...`. Nothing imports it.

## Constants

| Name | Value |
|---|---|
| `LANE_POLICY_VERSION` | `"1"` |
| `ALWAYS_OPERATIONAL_CLASSES` | `frozenset` of the seven contract classes |
| `DEFAULT_CONVERSATIONAL_CLASSES` | `frozenset({GENERAL_EXPLANATION, OTHER})` |
| `SIGNAL_REASONS` | read-only mapping, condition field name → `LaneReason`, in contract order |
| `NO_SIGNALS` | a shared `LaneSignals()` with every condition false |

## `LaneSignals`

Frozen, slotted, seven `bool` fields, all defaulting to `False`:
`tool_proposal`, `tool_result`, `confirmation_required`, `active_operational_provenance`,
`operational_correction`, `action_target`, `external_status_claim_required`.

Each field is validated with `is True` / `is False`, so `1`, `"yes"` and truthy objects raise
`LanePolicyError`. An unknown keyword raises `TypeError` from the dataclass itself.

| Member | Returns |
|---|---|
| `any_operational` (property) | `True` when at least one condition holds |
| `operational_reasons()` | the conditions that hold, as `LaneReason`, in declared order |
| `to_mapping()` | a plain `dict[str, bool]` of all seven |

## `LaneReason`

`str` enum, nine members: `ALWAYS_OPERATIONAL_CLASS`, one per condition
(`TOOL_PROPOSAL`, `TOOL_RESULT`, `CONFIRMATION_REQUIRED`, `ACTIVE_OPERATIONAL_PROVENANCE`,
`OPERATIONAL_CORRECTION`, `ACTION_TARGET`, `EXTERNAL_STATUS_CLAIM_REQUIRED`), and
`NO_OPERATIONAL_STATE`.

## `LaneDecision`

Frozen: `lane: Lane`, `request_class: RequestClass`, `reasons: tuple[LaneReason, ...]`,
`policy_version: str = LANE_POLICY_VERSION`. `to_mapping()` returns plain JSON-serializable data
with keys `lane`, `request_class`, `reasons`, `lane_policy_version`.

## Functions

```python
decide(request_class: RequestClass, signals: LaneSignals) -> Lane
explain(request_class: RequestClass, signals: LaneSignals) -> LaneDecision
```

Both are pure and total over valid input. `signals` is **required**: there is no implicit
all-false default, because a caller that forgot to pass its state would otherwise silently get the
conversational lane. `decide` is `explain(...).lane`.

## `LanePolicyError`

Subclasses `ValueError`. Raised when `request_class` is not a `RequestClass` member, when `signals`
is not a `LaneSignals` instance, or when a condition field is not a `bool`. It is never raised for
a legitimate combination of values — every one of the 1,152 valid rows returns a lane.

## Worked examples

```python
decide(RequestClass.GENERAL_EXPLANATION, NO_SIGNALS)
# Lane.CONVERSATIONAL

decide(RequestClass.GENERAL_EXPLANATION, LaneSignals(tool_result=True))
# Lane.OPERATIONAL

explain(RequestClass.ACTION_REQUEST, LaneSignals(action_target=True)).to_mapping()
# {'lane': 'OPERATIONAL', 'request_class': 'ACTION_REQUEST',
#  'reasons': ['ALWAYS_OPERATIONAL_CLASS', 'ACTION_TARGET'], 'lane_policy_version': '1'}

decide("VALUE_QUERY", NO_SIGNALS)
# LanePolicyError: request_class must be a RequestClass member, got str
```

## Imports

`__future__`, `dataclasses`, `enum`, `types`, `typing`, and `app.execution.types` — nothing else.
No clock, no environment, no filesystem, no network, no model.
