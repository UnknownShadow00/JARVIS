# Contradiction Policy — Task 13B11L-P6

**FROZEN AND IMPLEMENTED.**

## 1. The rule

An impossible combination is a **caller defect**, not a policy question. The engine raises
`ContradictoryObligationState` rather than returning a decision, carrying a machine-readable
`code`. This follows the precedent set twice already: `permissions.py` — *"Passing one as
authority is an API misuse, not a permission question, so it raises rather than denying"* —
and `dispatch.py`'s split between `DispatchError` (shape) and a returned refusal (authority).

Raising is the fail-closed direction, because there is no safe obligation to return: every
member of the enum asserts something, and the caller has already said two incompatible
things about the world.

No contradiction resolves toward the model-friendly answer, and no malformed operational
state degrades to the conversational lane — that would be the §4.2 relabelling the contract
forbids, dressed as error handling.

## 2. The corpus

Twenty codes, each naming the component whose own rules make the state impossible. Checked
in this frozen order, so one impossible state always reports the same code.

### Result shape — what P5 can construct
| Code | Why impossible |
|---|---|
| `C-07-refusal-claims-execution` | `BLOCKED`/`CONFIRMATION_REQUIRED` always carry `executed=False` and no facts |
| `C-08-execution-status-without-execution` | `SUCCESS`/`ERROR`/`TIMEOUT` are reachable only once an executor ran |

### Lane — what the lane policy can decide
| Code | Why impossible |
|---|---|
| `C-10-conversational-lane-for-operational-class` | the class is in `ALWAYS_OPERATIONAL_CLASSES` |
| `C-11-conversational-lane-with-operational-reason` | any operational reason forces `OPERATIONAL` |
| `C-03-conversational-lane-with-trusted-result` | `LaneReason.TOOL_RESULT` forces `OPERATIONAL` |
| `C-12-conversational-lane-with-permission-decision` | a permission decision implies an action |
| `C-13-conversational-lane-with-confirmation-state` | a claimed approval implies an action |
| `C-14-operational-lane-without-any-operational-reason` | `NO_OPERATIONAL_STATE` is the conversational reason |
| `C-15-operational-lane-without-any-reason` | the policy always records at least one |

### Execution — what the dispatcher's gates allow
| Code | Why impossible |
|---|---|
| `C-01-denied-yet-executed` | gate 4 refuses a `DENY` with `executed=False` |
| `C-02-confirmation-required-executed-without-authority` | gate 6 is the only route to execution |
| `C-04-unresolved-target-yet-executed` | §17.1 forbids dispatching without a resolved target |
| `C-05-multi-action-yet-executed` | §8.1 dispatches nothing |
| `C-06-non-dispatchable-action-yet-executed` | §13.1/§13.2, no nearest-tool substitution |
| `C-16-unavailable-capability-yet-executed` | an unregistered capability cannot have run |

### Settled state — what P4 can decide
| Code | Why impossible |
|---|---|
| `C-17-confirmation-required-for-non-confirmable-action` | the dispatcher refuses a non-dispatchable action at gate 2, before gate 5 |
| `C-18-permissive-outcome-for-non-executable-action` | `permissions.decide` steps 1–3 DENY every one |
| `C-19-permissive-outcome-with-unresolved-target` | `permissions.decide` step 5 DENYs |
| `C-20-confirmation-record-for-non-confirmable-action` | the confirmation layer refuses to bind one |
| `C-21-approval-claimed-without-a-confirmation-requirement` | an approval exists only where the engine asked for one |

## 3. C-09 is prevented, not refused

The frozen matrix carries a C-09 row — an executed flag with no result behind it. The engine
has no code for it and needs none: `ObligationState.executed` is a *derived property* of
`result`, so the state cannot be expressed. Prevented by construction beats refused at run
time, and the matrix test asserts exactly that.

## 4. What is *not* a contradiction

Ordinary states that must be decided, not refused:

* `REQUIRE_CONFIRMATION` with no result — rank 1, the normal confirmation turn;
* `DENY` with no result — rank 6, reason `permission_denied` (decision D-P6-01);
* `TIMEOUT` — rank 2, reason `trusted_tool_timeout` (decision D-P6-02);
* a conversational turn with no operational state — no obligation, `MODEL_RAW`.

## 5. Malformed input is separate

`ObligationInputError` covers shape: a wrong type, a bare enum *value* where a member is
required (the str-enum trap — `"DENY" == PermissionOutcome.DENY`), a `ModelDraft` or a
mapping in the result slot, an incoherent `ValueProjection`. It never silently returns
conversational, unsupported, failure or `OTHER`.
