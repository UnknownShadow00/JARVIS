# Permission Matrix Plan

**Status:** plan only. No policy was changed; `SAFETY_LEVEL` constants and `approval_mode` in
production are untouched.

## 1. Model

Today a permission is one integer per *tool module* (`SAFETY_LEVEL`), thresholded globally by
`settings.safety.approval_mode` (`app/tools/registry.py:236`). The contract requires a class per
*action + target*, decided before dispatch (§11).

Planned decision function:

```
permission_of(action_type, target, session) -> PermissionDecision
  PermissionDecision = { class, outcome: ALLOW | CONFIRM | DENY, reason, policy_version }
```

The table below is the proposed initial policy, derived from the currently installed tools and
from the operator's previously stated direction (reads automatic; mutating calendar, messaging, PC
control, deletion, purchases, power actions confirmed; learned permissions only when explicitly
approved).

## 2. Proposed matrix for currently installed capabilities

| Capability (current tool / action) | Permission class | Default | Confirmation | Additional constraints | Audit |
|---|---|---|---|---|---|
| `system_stats` | READ_ONLY | allow | no | — | tool_call/result |
| `calendar` read (`app/tools/calendar.py`, L0) | READ_ONLY | allow | no | read-only window | tool_call/result |
| calendar **create/move/delete** (not implemented today) | REVERSIBLE_ACTION | confirm | **yes** | must name event + time in the confirmation | full chain |
| `web_search` (L0) | READ_ONLY | allow | no | result text is untrusted content (§21) | tool_call/result |
| `screenshot` (L0) | READ_ONLY | allow | no | local file path only | tool_call/result |
| `vision` (L0) | READ_ONLY | allow | no | image content is untrusted | tool_call/result |
| `kasa` status (L0) | READ_ONLY | allow | no | — | tool_call/result |
| `kasa` control (stub, L0 today) | REVERSIBLE_ACTION | confirm | **yes** | mismatch with current L0 — see §4 | full chain |
| `apps` open (L0) | REVERSIBLE_ACTION | allow | no | canonical app name required; unknown name → no dispatch | raw+canonical args |
| `apps` close (L0) | REVERSIBLE_ACTION | confirm | **yes** | closing may lose user work | full chain |
| `browser` open URL (L1) | REVERSIBLE_ACTION | allow | no | absolute URL only; no credentials in URL | raw+canonical args |
| `browser_use` agent (L1, stub) | PRIVILEGED_ACTION | confirm | **yes** | acts with the user's real session/cookies | full chain + goal text |
| `files` read/list (L1) | READ_ONLY | allow | no | inside configured safe roots only | path audited |
| `files` move (L1) | REVERSIBLE_ACTION | confirm | **yes** | source and destination both named | full chain |
| file **delete** (not implemented today) | DESTRUCTIVE_ACTION | confirm | **yes** | exact absolute path; no globs; no invented path | full chain |
| `obsidian` read/search (L1) | READ_ONLY | allow | no | vault scope | tool_call/result |
| `obsidian` create/append (L1) | REVERSIBLE_ACTION | allow | no | vault scope; append is recoverable | raw+canonical args |
| `shell` (L2) | PRIVILEGED_ACTION | confirm | **yes** | existing blocklist retained; command quoted verbatim in the confirmation | full chain + command |
| `computer_use` / `mouse_keyboard` (L2) | PRIVILEGED_ACTION | confirm | **yes** | PC control per operator direction | full chain |
| `cad` print (L2) | DESTRUCTIVE_ACTION | confirm | **yes** | physical output; verify STL first | full chain |
| `mcp_client` (L1, stub) | PRIVILEGED_ACTION | confirm | **yes** | whitelisted servers only; server output is untrusted | full chain |
| `cli` harness (L1, stub) | PRIVILEGED_ACTION | confirm | **yes** | per-harness allowlist | full chain |
| Discord / Telegram send (`app/comms/*`) | EXTERNAL_COMMUNICATION | confirm | **yes** | recipient + full message body shown before sending | full chain + recipient |
| shutdown / restart / sleep of the host | SYSTEM_POWER | confirm | **yes** | never inferred from prose | full chain |
| purchase / payment (not implemented) | FINANCIAL_PURCHASE | **deny** in v1 | n/a | no tool exists; must stay `UNKNOWN_ACTION` | capability-unavailable |
| deploy / infra mutation (not implemented) | PRIVILEGED_ACTION | **deny** in v1 | n/a | no tool exists | capability-unavailable |

## 3. Rules that accompany the table

1. The class is a property of **action + target**, not of the module: `files` read and `files`
   move differ; `kasa` status and `kasa` control differ.
2. `approval_mode` (`safe` / `balanced` / `strict`) stays as a *global tightening* control: it may
   raise a decision from ALLOW to CONFIRM, never lower one.
3. A capability with no authorized tool is never DENY-by-permission; it is `UNKNOWN_ACTION` and is
   answered by `REPORT_CAPABILITY_UNAVAILABLE` (§13).
4. Learned or remembered permissions ("always allow X") are out of scope for v1. If added later,
   each must be an explicit, user-approved, auditable record with its own expiry — never inferred
   from behaviour.
5. The policy table is data (`config/permissions.yaml`), versioned, with `policy_version` recorded
   in every decision and audit event.

## 4. Mismatches with current production policy (declared, not changed)

| Item | Current | Proposed | Note |
|---|---|---|---|
| `apps` close | `SAFETY_LEVEL = 0` → runs without confirmation | REVERSIBLE_ACTION + confirmation | closing an app can lose unsaved work |
| `kasa` control | module-level `SAFETY_LEVEL = 0` | REVERSIBLE_ACTION + confirmation | today's stub conflates status and control |
| `browser_use` | `SAFETY_LEVEL = 1` → runs without confirmation | PRIVILEGED_ACTION + confirmation | it acts with real cookies/sessions |
| `mcp_client`, `cli` | `SAFETY_LEVEL = 1` | PRIVILEGED_ACTION + confirmation | arbitrary external servers / processes |
| Destructive verbs | caught by a router regex → `confirm_action` *text*, not by permission | permission class at the action level | the regex is a prose gate, not an execution gate |

These are recorded as **planned changes requiring explicit approval**, not as defects to be fixed
silently. Nothing in this task modifies a `SAFETY_LEVEL`.

## 5. Failure behaviour

Permission store unavailable, policy version unknown, or action not in the table → **deny and do
not execute**, obligation `REPORT_CAPABILITY_UNAVAILABLE` or `REQUEST_CONFIRMATION` as
appropriate, with the failure audited. No default-allow path may exist.
