# Feature Flag and Rollback Plan

**Status:** plan only. `agent.hermes_enabled` remains `false` and unread by code.

## 1. Flag model

A single enum, not a set of booleans, so that impossible combinations cannot be configured:

```
execution:
  mode: legacy            # legacy | shadow | control_plane
  shadow_sample_rate: 1.0 # only meaningful in shadow
  hermes_brain: false     # whether the model behind the adapter is Hermes/Granite or the legacy model
```

| Mode | Legacy path | New control plane | Tools executed by | User sees |
|---|---|---|---|---|
| `legacy` (**default**) | runs | not entered | legacy `registry.call` | legacy reply |
| `shadow` | runs and answers | runs in parallel, **inert** | legacy only | legacy reply |
| `control_plane` | not entered | runs | `app/execution/dispatch.py` | deterministic operational reply / conversational prose |

Three modes are the minimum that supports the required phases: run as today, compare without
risk, then switch. `hermes_brain` is separate because swapping the model and swapping the control
plane are independent changes and must be independently reversible.

## 2. Rules

1. Default is `legacy`. A missing or unparsable `execution` section means `legacy`
   (fail to the known-good path), enforced by the pydantic `StrictModel` default.
2. The new path is entered from exactly one place in `app/server.py` — a single branch at the top
   of `_process` — so the blast radius is one function and the flag cannot leak into tools.
3. `shadow` must be structurally incapable of executing: the shadow pipeline receives an inert
   dispatcher implementation, not the real one (see the shadow-mode plan).
4. The flag is read once per turn and carried in the turn context, so a mid-turn config reload
   cannot produce a half-legacy, half-new turn.
5. Every audit event records the mode, so any log line can be attributed to a path.

## 3. Rollback

Preferred order, fastest first:

| Level | Action | Time | Effect |
|---|---|---|---|
| 1 | set `execution.mode: legacy` (config edit + restart, or a `/resource`-style admin endpoint if one is added) | seconds | new path no longer entered; code stays installed |
| 2 | set `hermes_brain: false` | seconds | keep the control plane, revert the model |
| 3 | revert the feature commit(s) | minutes | code removed; legacy untouched because the new path is additive |
| 4 | restore `config.yaml` from git | minutes | configuration back to `2d7a2ec8` state |

Properties required of the implementation so that level 1 is always sufficient:

* The new path is **additive**: no legacy function is deleted or rewritten during phases 0-6.
* No schema migration is required to run in `legacy` mode (see the migration section of the
  integration plan — v1 introduces JSON files, not a database).
* Pending confirmations created by the new path are readable but inert in legacy mode; on
  rollback they expire rather than executing.
* Rollback never deletes evidence, contract artifacts, provenance logs or models.

## 4. What rollback does not cover

If the new path has already executed a real mutating tool, rollback stops future executions but
does not undo the effect. That is why the phase order puts real mutating tools last, behind
confirmation, after shadow and read-only phases have passed.
