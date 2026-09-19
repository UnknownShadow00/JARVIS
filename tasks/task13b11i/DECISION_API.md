# Decision API

`app/execution/permissions.py`. Pure, passive, unwired. One public entry point.

```python
decide(request: PermissionRequest) -> PermissionDecision
```

## PermissionRequest — the deterministic input

Frozen, slotted, hashable. Every field is structured state a future dispatcher already holds; none
of it is prose and none of it is model output.

| Field | Type | Default | Why |
|---|---|---|---|
| `capability` | `str` | required | the real-inventory key, e.g. `"files.move"` (§10, §11). Never a `PrimaryAction` |
| `primary_action` | `PrimaryAction` | required | the router's structural verdict; gates before the table (§25, §26) |
| `target` | `str \| None` | `None` | raw, exactly as the user wrote it (§32) |
| `canonical_target` | `str \| None` | `None` | canonical where a rule exists; the caller canonicalizes, permissions never calls `canonicalize()` |
| `raw_arguments` | `Mapping[str, Any]` | `{}` | audited, never used to pick a class |
| `canonical_arguments` | `Mapping[str, Any]` | `{}` | what would actually run |
| `target_resolved` | `bool` | `True` | from the router; `False` fails closed (§25) |
| `approval_mode` | `ApprovalMode` | `BALANCED` | tightening only (§24, D-09) |
| `satisfied_constraints` | `frozenset[Constraint]` | `frozenset()` | constraints a future validator has **already** discharged (D-04) |
| `overwrite` | `bool \| None` | `None` | move only: `False` non-overwriting, `True` overwrite, `None` **not determined** → denied (D-03) |

There is deliberately **no** field for model confidence, a model "safe" flag, a model permission
recommendation, a claim that the user confirmed, or free-form prose (§30).

## PermissionDecision — the frozen output

| Field | Type | Meaning |
|---|---|---|
| `outcome` | `PermissionOutcome` | `ALLOW` / `REQUIRE_CONFIRMATION` / `DENY` — production enum, reused |
| `permission_class` | `PermissionClass \| None` | `None` only where no class applies (row 40, or a structural denial before any row matched) |
| `confirmation_required` | `bool` | derived, always `outcome is REQUIRE_CONFIRMATION`; never set independently |
| `reason` | `PermissionReason` | machine-readable, one per rule |
| `matched_row` | `str \| None` | the policy key, or `None` when the denial happened before lookup |
| `constraints` | `tuple[Constraint, ...]` | the row's required constraints, satisfied or not |
| `unsatisfied_constraints` | `tuple[Constraint, ...]` | non-empty ⇒ the outcome is `DENY` |
| `base_outcome` | `PermissionOutcome \| None` | the row's outcome before `approval_mode` tightening |
| `approval_mode` | `ApprovalMode` | the mode used |
| `policy_version` | `str` | always `"1"` |
| `notes` | `tuple[str, ...]` | the row's recorded tool-side constraints, for a future confirmation prompt |

There is no execution authority object, no callback, no tool name, no callable (§37).
`is_dispatchable` is a read-only property, true only for `ALLOW` with no unsatisfied constraint.

## Evaluation order (frozen)

Structural gates run **before** any table lookup, so a bad route can never reach a permissive row.

```
 0. input validation                     -> raise PermissionPolicyError   (invalid API use)
 1. primary_action MULTI_ACTION_UNSUPPORTED -> DENY MULTI_ACTION_UNSUPPORTED
 2. primary_action UNKNOWN_ACTION           -> DENY UNKNOWN_ACTION
 3. primary_action NONE                     -> DENY ACTION_NOT_EXECUTABLE
 4. primary_action in UNAVAILABLE_ACTIONS   -> DENY CAPABILITY_NOT_REGISTERED   (D-08)
 5. target_resolved is False                -> DENY TARGET_UNRESOLVED
 6. action/capability disagree              -> DENY CAPABILITY_ACTION_MISMATCH
 7. capability not in the table             -> DENY NO_POLICY_ROW
 8. overwrite resolution (files.move)       -> DENY OVERWRITE_STATE_UNKNOWN, or row .overwrite
 9. row.registered is False                 -> DENY CAPABILITY_NOT_REGISTERED
10. required constraints unsatisfied        -> DENY CONSTRAINT_NOT_SATISFIED   (D-04)
11. base outcome, then approval_mode tightening -> final outcome               (D-09)
```

Only step 11 can produce `ALLOW`, and only from a row that explicitly declares it.

## Invalid input versus valid-but-denied (§28)

`PermissionPolicyError` means **the caller misused the API**: a non-string capability, an `Enum`
passed where text belongs (the 13B11G failure mode — `PermissionClass` and `PrimaryAction` are
`str` enums, so a member would otherwise be accepted as a capability string), a wrong enum type,
a non-mapping argument bundle, or a `ModelDraft` / `ToolProposal` handed in as authority. It is
raised, never returned, and there is no decision object to mistake for an answer.

A **valid-but-denied** request returns a normal `PermissionDecision` with `outcome = DENY` and a
reason. The distinction matters because a future caller may legitimately catch the second and must
never catch the first and continue.

## What this module never does

No dispatch, no tool lookup, no `registry.call`, no confirmation record, no confirmation id, no
interpretation of "yes", no TTL, no clock, no learned or persisted permission, no audit emission,
no provenance access, no `router.route()`, no `canonicalize()`, no model call, no I/O of any kind.
