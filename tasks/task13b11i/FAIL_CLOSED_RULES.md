# Fail-closed rules

Every abnormal input produces **no execution**. The production outcome is
`PermissionOutcome.DENY`; there is no other "refuse" value and none was invented.

| Condition | Outcome | `PermissionReason` | Review §29 row |
|---|---|---|---|
| `PrimaryAction.MULTI_ACTION_UNSUPPORTED` | `DENY` | `MULTI_ACTION_UNSUPPORTED` | §30 |
| `PrimaryAction.UNKNOWN_ACTION` | `DENY` | `UNKNOWN_ACTION` | yes |
| `PrimaryAction.NONE` | `DENY` | `ACTION_NOT_EXECUTABLE` | §33 |
| `DEPLOY` / `DELETE_PATH` / `GET_DATABASE_STATUS` — no executable capability | `DENY` | `CAPABILITY_NOT_REGISTERED` | D-08 |
| `target_resolved is False` (ambiguous or missing target) | `DENY` | `TARGET_UNRESOLVED` | yes |
| routed action and capability key disagree | `DENY` | `CAPABILITY_ACTION_MISMATCH` | implied by §24 |
| capability absent from the table | `DENY` | `NO_POLICY_ROW` | yes |
| row exists but no production tool implements it | `DENY` | `CAPABILITY_NOT_REGISTERED` | yes |
| `files.move` with `overwrite=None` (state not determined) | `DENY` | `OVERWRITE_STATE_UNKNOWN` | D-03 |
| `files.move` with `overwrite=True` | `DENY` | `OVERWRITE_DENIED` | D-03 |
| a required constraint is not satisfied | `DENY` | `CONSTRAINT_NOT_SATISFIED` | D-04 |
| policy table empty or a row malformed at import | import fails loudly | — | "no unsafe config fallback" |
| invalid API input (wrong type, enum-as-text, model object) | **`PermissionPolicyError` raised** | — | §28 |
| any unexpected internal error | propagates; there is no `except: return ALLOW` | — | §29 |

## Properties asserted by test

1. **No default allow.** `ALLOW` is reachable only from a row whose `base_outcome` is `ALLOW`, with
   every constraint satisfied and after tightening. Asserted by enumerating every reason: only
   `ROW_MATCHED` can carry `ALLOW`.
2. **Absence is never permission.** An unknown capability string, an empty string, and a
   near-miss key (`"files.mov"`, `"FILES.MOVE"`, `"files.move "`) all deny.
3. **No exception path returns a decision.** The module contains no bare `except`, and no
   `except` clause returns or constructs a `PermissionDecision`.
4. **`DENY` is absorbing** under every `approval_mode`.
