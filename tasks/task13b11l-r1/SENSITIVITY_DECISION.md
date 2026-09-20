# Sensitivity decision — the operator's split of the twenty

Transcribed verbatim from task section 1 and frozen in
`02-frozen-tables.json → operator_decision` before `classifier.py` was edited. It was
not reinterpreted, extended or narrowed.

## The split

**Added to `SENSITIVE_ACTION_VERBS` (14):**
`clear` `commit` `flush` `merge` `modify` `patch` `pull` `reset` `restore` `revert`
`rollback` `scale` `upgrade` `upload`

**Deliberately NOT added (6):**
`backup` `build` `download` `fix` `roll` `rotate`

`14 ∪ 6 = 20`, `14 ∩ 6 = ∅`. Both asserted in the test file.

## What the split actually decides

Only which action class the request carries. Both classes are action-bearing, both are
members of `ALWAYS_OPERATIONAL_CLASSES`, and both route to `UNKNOWN_ACTION`:

| verb family | class | rule | lane | action | executable? |
|---|---|---|---|---|---|
| the 14 sensitive | `CONFIRMATION_SENSITIVE_ACTION` | `R-02-action-sensitive` | `OPERATIONAL` | `UNKNOWN_ACTION` | no |
| the 6 ordinary | `ACTION_REQUEST` | `R-03-action-explicit` | `OPERATIONAL` | `UNKNOWN_ACTION` | no |

Measured 14/14 and 6/6 through the real chain. Section 14's requirement that the six
"remain action-bearing without being promoted merely by this change" is met: all six are
in `ACTION_VERBS`, none is in `SENSITIVE_ACTION_VERBS`, and all six reach
`UNKNOWN_ACTION` + `OPERATIONAL`.

## What the split does not decide

Recognising `CONFIRMATION_SENSITIVE_ACTION` is not a confirmation requirement. Contract
§5.1 separates the two, and `app/execution/permissions.py` was not touched: no permission
row moved, `approval_mode` is still tightening-only, and `PrimaryAction.UNKNOWN_ACTION`
is a member of `permissions.NON_EXECUTABLE_ACTIONS` and of
`dispatch.NON_DISPATCHABLE_ACTIONS`. None of the forty-one verbs has an authorized tool.

## Precedence note — `reset the service`

Section 16 names `reset the service`. It classifies `AMBIGUOUS_ACTION`, not
`CONFIRMATION_SENSITIVE_ACTION`, because `"the service"` is a frozen member of
`AMBIGUOUS_REFERENTS` and `R-01-action-ambiguous` outranks `R-02-action-sensitive`. That
is the existing frozen semantics, and task section 8 explicitly says not to force one
`RequestClass` blindly. It satisfies section 16 regardless: `AMBIGUOUS_ACTION` is
action-bearing, always-operational, and routes to `UNKNOWN_ACTION`. `reset the cache`,
whose target is not an ambiguous referent, does classify `CONFIRMATION_SENSITIVE_ACTION`.
The frozen table records this row explicitly rather than smoothing it over, and a test
asserts it by name.

## Observation for the operator — `roll` vs `rollback`

The split puts `rollback` in the sensitive set and `roll` outside it. Both are separate
members of the router's frozen `UNSUPPORTED_VERBS`, so both were added, and the frozen
decision was applied exactly as written. Measured consequence:

```
rollback the last deployment    CONFIRMATION_SENSITIVE_ACTION   R-02-action-sensitive
roll back the deployment        ACTION_REQUEST                  R-03-action-explicit
```

Two spellings of the same intent carry different action classes. **Nothing was changed
to smooth this over** — task section 1 froze the decision and task section 5 forbids
redesigning classification. It is recorded here because it is the kind of thing an
operator would want to decide knowingly rather than discover later. It is latent: both
rows are action-bearing, both are `OPERATIONAL`, both are `UNKNOWN_ACTION`, and neither
is executable or confirmable. If the operator wants `roll` moved into the sensitive set,
that is a one-line follow-up under its own authorization.
