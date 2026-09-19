# Task 13B11H — Frozen Action Lexicon

Taken from `tasks/task13b10c4/action-lexicon.json`, whose own status line reads
**"FROZEN BEFORE SCORING"**, and from contract §6.1. Nothing was broadened opportunistically and
nothing is learned at runtime.

## 1. The action vocabulary is the production enum

`PrimaryAction` from `app/execution/types.py`, eight members, imported and never redefined:

```
OPEN_APP  OPEN_URL  DEPLOY  DELETE_PATH  GET_DATABASE_STATUS
NONE  UNKNOWN_ACTION  MULTI_ACTION_UNSUPPORTED
```

Contract §6.1 names exactly this set as validated. §6.2 allows production to add action types
later, but each must declare its permission class, confirmation sensitivity, required targets,
canonicalization rules and provenance fields first — so no action type is added here.

**Supported** (an authorized tool exists): `OPEN_APP`, `OPEN_URL`, `DEPLOY`, `DELETE_PATH`,
`GET_DATABASE_STATUS`. The other three are outcomes, not operations.

## 2. Verbs, clause-initial only

| Verbs | Yields |
|---|---|
| `open`, `launch` | `OPEN_APP` or `OPEN_URL`, decided by target shape (`TARGET_EXTRACTION.md` §3) |
| `deploy` | `DEPLOY` |
| `delete`, `remove` | `DELETE_PATH` |
| `check`, `verify`, `inspect`, `get` | `GET_DATABASE_STATUS` if the object matches, else `UNKNOWN_ACTION` |
| 40 further verbs (below) | `UNKNOWN_ACTION` — explicitly requested, no authorized tool |

The 40 unsupported verbs, verbatim from the frozen lexicon: `restart`, `reboot`, `start`, `stop`,
`shutdown`, `install`, `uninstall`, `upgrade`, `update`, `change`, `modify`, `rollback`, `roll`,
`scale`, `reset`, `kill`, `enable`, `disable`, `create`, `rename`, `move`, `copy`, `run`,
`execute`, `build`, `push`, `pull`, `commit`, `merge`, `revert`, `fix`, `send`, `email`,
`download`, `upload`, `backup`, `restore`, `clear`, `flush`, `rotate`, `patch`.

Listing them is the point. Contract §13.2 forbids nearest-tool substitution: an unsupported action
**MUST NOT** be mapped to a different tool because the verbs, names or intent look similar. Naming
each unsupported verb explicitly is what makes `UNKNOWN_ACTION` a decision rather than a fallthrough.

## 3. The five frozen rules

Verbatim from `action-lexicon.json`:

1. An action verb counts only in clause-initial position after optional polite/temporal modifiers.
2. A clause opening with a negation (`do not` / `don't` / `never` / `no need to` / `without` /
   `avoid`) is never an action.
3. A clause opening with a reporting marker is never an action.
4. `GET_DATABASE_STATUS` additionally requires the literal object `database` (optionally
   `database status`).
5. `DEPLOY` additionally requires the exact environment word `staging` or `production`;
   `DELETE_PATH` additionally requires exactly one exact path token equal to the whole operand.

Plus: no fuzzy or semantic verb inference, no second model, no verb learned during testing.

## 4. Why clause-initial

Rule 1 is the whole defence against a mentioned verb becoming a request. "The team will publish
the notes" and "What does deploy mean?" both contain an operational verb and neither is an
instruction. The same discipline is already in the 13B11G classifier; here it additionally stops a
verb inside a reporting clause ("tell me when the deploy finishes") from creating a second action.

## 5. Capability

`RouteResult.capability_available` is `primary_action in context.supported_actions`, where the
default is the frozen supported set above. `TARGET_COMPONENT_MAP.md` line 20 lists "capability
registry" among the router's inputs; passing it as a caller projection satisfies that without the
passive router importing `app/tools/registry.py` or reading live tool inventory. It is a boolean,
never a tool name.
