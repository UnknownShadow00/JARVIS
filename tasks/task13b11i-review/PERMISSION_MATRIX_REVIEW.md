# P4 Permission Matrix — Operator Sign-Off Review

**Status: REVIEW ONLY. NO PRODUCTION CHANGE MADE.** No production file was read-modified, no
production commit exists, `app/execution/permissions.py` was not created, and no permission,
confirmation, dispatcher, registry, safety or config code was touched. This document is the
entry-criterion packet for phase P4 (`IMPLEMENTATION_PHASES.md`: *"P3 exit; permission matrix
approved by the operator"*). It does not authorize implementation.

This is a review of the existing `tasks/task13b11a/PERMISSION_MATRIX_PLAN.md` against the frozen
contract, the **real** production registry as it stands at `03cab496`, the real `SAFETY_LEVEL`
values, and the real confirmation code. Where the plan and the code disagree, the disagreement is
recorded. The plan was not edited.

---

## 0. Baseline verification

| Check | Expected | Observed | Result |
|---|---|---|---|
| Production HEAD | `03cab496…` | `03cab4960156220fe9b6c3a444fa7a41265c01e0` | PASS |
| Working tree | clean | 0 dirty, 0 untracked, 1 worktree, branch `main`, 7 ahead, 0 pushed | PASS |
| `execution.mode` | legacy | `legacy` (`shadow_sample_rate: 1.0`) | PASS |
| `hermes_brain` / `hermes_enabled` | false / false | both `false` | PASS |
| Hermes repo | `2237be35…` clean, not running | `2237be355906fbe6065ce1815711eee52b2d646e`, 0 changed, 0 processes | PASS |
| 13B11H evidence | 53 files, 52 entries, digest `ef768d69…` | 53 / 52 / `ef768d6942cbff9617dc6aa8cc21ac44d428e80ab64115741d4bf964ddc84e17`, `sha256sum -c` **0 failures** | PASS |
| Source modifications | none | none — inventory taken by AST parsing and `git`-clean inspection, no tool imported, no tool executed | PASS |

Other live values recorded because the matrix depends on them: `safety.approval_mode = "balanced"`,
`safety.dry_run = false`, `safety.confidence_threshold = 0.75`, Python 3.14.4.

---

## 1. Frozen permission vocabulary (not invented here)

Contract §11.1 requires at least seven classes. `app/execution/types.py` (P0, `881eda40…`) already
defines exactly those seven, and three outcomes. **These exact names are used throughout this
document.**

`PermissionClass`: `READ_ONLY`, `REVERSIBLE_ACTION`, `DESTRUCTIVE_ACTION`, `PRIVILEGED_ACTION`,
`EXTERNAL_COMMUNICATION`, `SYSTEM_POWER`, `FINANCIAL_PURCHASE`.

`PermissionOutcome`: `ALLOW`, `REQUIRE_CONFIRMATION`, `DENY`.

> **Vocabulary correction against the plan.** `PERMISSION_MATRIX_PLAN.md` §1 writes the outcome set
> as `ALLOW | CONFIRM | DENY` and its table column as "allow / confirm / deny". Production has no
> `CONFIRM` member; the member is `REQUIRE_CONFIRMATION`. This is a wording drift in the plan, not a
> policy difference. The matrix below uses the production spelling. **No production or plan file was
> edited to fix it** — recorded here for the implementation task.

Binding invariants: **INV-004** confirmation-required actions cannot execute before valid
confirmation; **INV-013** production side effects require JARVIS permission policy; **INV-014**
destructive actions require deterministic confirmation policy. Contract §11.2: no model may
self-authorize; the decision is taken from action type and target, before dispatch, and audited.

---

## A. Current executable tool inventory

Taken from `app/tools/registry.py` `_EXPLICIT_TOOL_MODULES` (17 entries) plus `pkgutil` discovery
over `app/tools/` (`_discover_tool_modules`, which `setdefault`s any other module and skips only
`registry`). Nothing was imported or executed; every value below comes from reading source.

| Registry key | Module | `SAFETY_LEVEL` | Action subtypes in code | External effect | Local mutation | External comms | Power | Can delete | Launches/controls apps | Shell | Read-only | Stub |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `system_stats` | `app/tools/system_stats.py` | 0 | — | no | no | no | no | no | no | no | **yes** | no |
| `calendar` | `app/tools/calendar.py` | 0 | read by date only | no | no | no | no | no | no | no | **yes** | partial (`.ics` files) |
| `web_search` | `app/tools/web_search.py` | 0 | search, `action="fetch"` | **yes** (outbound HTTP) | no | no | no | no | no | no | yes (no writes) | dependency-gated |
| `screenshot` | `app/tools/screenshot.py` → `app/computer/screenshot.py` | 0 | — | no | writes an image file | no | no | no | no | no | yes (captures) | no |
| `vision` | `app/tools/vision.py` → `app/computer/vision.py` | 0 | screen, webcam | model call | temp capture | no | no | no | no | no | yes (captures) | no |
| `kasa` | `app/tools/kasa.py` | 0 (`CONTROL_SAFETY_LEVEL = 1` declared, **not read by the gate**) | `status`, `discover` / `on`, `off`, `toggle`, `set_brightness` | yes when live | no | no | no | no | no | no | reads only | **yes**, control deferred |
| `apps` | `app/tools/apps.py` | 0 | `open` (default), `close` | no | process create/kill | no | no | unsaved work on `close` | **yes** | `subprocess.Popen(shell=True)`, `taskkill /F` | no | no |
| `browser` | `app/tools/browser.py` | 1 | `open` (default), `search` | opens a real browser | no | no | no | no | yes (browser) | no | no | no |
| `browser_use` | `app/tools/browser_use.py` | 1 | — | would act with real cookies | no | no | no | no | yes | no | no | **yes** |
| `files` | `app/tools/files.py` | 1 | `list` (default), `read`, `search`, `move` | no | **yes** on `move` | no | no | no delete path exists | no | no | on `list`/`read`/`search` | no |
| `obsidian` | `app/tools/obsidian.py` | 1 | `note_read`, `note_search`, `note_create`, `note_append` | MCP handoff when enabled | **yes** on create/append | no | no | no | no | no | on read/search | MCP path optional |
| `mcp_client` | `app/tools/mcp_client.py` | 1 | `status` (default) | would reach external servers | no | no | no | no | no | no | status only | **yes** |
| `cli` | `app/tools/cli/__init__.py` | 1 | `status` (default) / anything else → dry-run plan | would drive OBS/FFmpeg/Blender | no | no | no | no | yes | would spawn processes | `shutil.which` only | **yes** |
| `cad` | `app/tools/cad.py` | 2 | — | would drive a 3D printer | writes STL | no | no | no | no | no | no | **yes** |
| `computer_use` | `app/tools/computer_use.py` | 2 | — | **yes** (GUI control) | yes | no | no | possibly | **yes** | no | no | **yes** |
| `mouse_keyboard` | `app/tools/mouse_keyboard.py` → `app/computer/mouse_keyboard.py` | 2 | — | **yes** (GUI control) | yes | no | no | possibly | **yes** | no | no | no |
| `shell` | `app/tools/shell.py` | 2 | arbitrary command string | **yes** | **yes** | possible | blocked by pattern list | **yes** | yes | **yes** | no | no |
| `health_check` | `app/tools/health_check.py` | **absent** | — | outbound HTTP probes | no | no | no | no | no | no | yes | n/a |

**`registry` itself** is skipped by name in `_discover_tool_modules`, so it is not a capability.

### A.1 Inventory anomalies (§36)

1. **`health_check` is an orphan registry entry.** `pkgutil` discovery adds it to `TOOLS` and to
   `ToolRegistry.TOOLS`, but it defines neither `SAFETY_LEVEL` nor `execute`, so `_load_tool` raises
   `ToolError("Invalid tool module: 'health_check'")`. `list_tools()` therefore advertises it with
   `safety_level: -1`. It cannot be dispatched today, so it is not a permission hole — but it is a
   capability name visible to tool selection that no policy row can meaningfully cover.
   **Status: REVIEW.** Recommended resolution is a registry-level rule (explicit allow-list instead
   of `pkgutil` discovery), not a permission row.
2. **`kasa` declares two levels.** The module sets `SAFETY_LEVEL = 0` and `CONTROL_SAFETY_LEVEL = 1`.
   `registry.call` reads only `SAFETY_LEVEL`, so a control action is gated at level 0 today. The
   second constant is documentation, not enforcement.
3. **`mouse_keyboard` and `screenshot`/`vision` are re-export shims** for `app/computer/*`. Their
   effective `SAFETY_LEVEL` comes from the underlying module (2, 0, 0). No divergence found.
4. **`files` safe roots are host-dependent.** `config.yaml` `paths.*` are Windows paths
   (`D:/Projects`, `D:/Downloads`, `D:/Datasheets`); on the Linux host they resolve under the CWD and
   do not exist, leaving the repo root as the effective root. Not a permission-class question, but
   the P4 table must not assume the configured roots are the effective roots.

---

## B. Proposed permission matrix

Column meanings: **CURRENT BEHAVIOR** is what happens today with `approval_mode = "balanced"`
(`registry._requires_confirmation`: confirmation iff `SAFETY_LEVEL >= 2`; level ≥ 3 is blocked
outright). **DEFAULT P4 DECISION** uses the production `PermissionOutcome` names. **AUDIT** names the
schema-v3 event that must carry the decision (`app/execution/audit_events.py`).

| # | Capability (action + target scope) | Current `SAFETY_LEVEL` | Current behavior | Proposed `PermissionClass` | Default P4 `PermissionOutcome` | Confirmation? | Additional constraints | Audit requirement | Rationale | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `system_stats` | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | — | `permission.decision` + `dispatch.*` | local read, no mutation | **AGREE** |
| 2 | `calendar` read | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | read window only; no mutation path exists | `permission.decision` + `dispatch.*` | reads local `.ics` | **AGREE** |
| 3 | `web_search` search | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | result text is untrusted content (§18) | `permission.decision` + `dispatch.*` | reads the public web | **AGREE** |
| 4 | `web_search` `action="fetch"` (arbitrary URL) | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | **needs an egress constraint**: the URL is caller-supplied and unvalidated, so a fetch of `http://localhost:…`/RFC1918 reaches internal services | raw + canonical URL audited | reads, never writes — but the *target* is attacker-influenceable via retrieved content | **REVIEW** (D-04) |
| 5 | `screenshot` | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | local path only | `permission.decision` + `dispatch.*` | captures the local screen | **AGREE** |
| 6 | `vision` screen | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | image content is untrusted (§18) | `permission.decision` + `dispatch.*` | capture + describe | **AGREE** |
| 7 | `vision` webcam | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | operator may prefer a confirmation for camera capture | `permission.decision` + `dispatch.*` | read-only by class, privacy-sensitive by nature | **REVIEW** (D-05) |
| 8 | `kasa` `status` / `discover` | 0 | runs automatically | `READ_ONLY` | `ALLOW` | no | local network only | `permission.decision` + `dispatch.*` | device read | **AGREE** |
| 9 | `kasa` `on`/`off`/`toggle`/`set_brightness` | 0 (gate) | **runs automatically** | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | device named in the confirmation | full chain | physical-world effect | **CONFLICT — declared mismatch M-02** |
| 10 | `apps` `open` (allow-listed name) | 0 | runs automatically | `REVERSIBLE_ACTION` | `ALLOW` *(plan)* / `REQUIRE_CONFIRMATION` *(operator "PC control" direction)* | **undecided** | canonical app name required; unknown name → no dispatch (already true: `_APP_MAP` miss returns an error) | raw + canonical args | the plan and the stated policy direction disagree | **CONFLICT (D-01)** |
| 11 | `apps` `close` | 0 | **runs automatically** | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | `taskkill /F` — unsaved work is lost; consider `DESTRUCTIVE_ACTION` (D-02) | full chain | irreversible for unsaved data | **CONFLICT — declared mismatch M-01** |
| 12 | `browser` `open` URL | 1 | runs automatically | `REVERSIBLE_ACTION` | `ALLOW` | no | absolute URL only; no credentials in URL | raw + canonical args | opens a window | **AGREE** |
| 13 | `browser` `search` | 1 | runs automatically | `REVERSIBLE_ACTION` | `ALLOW` | no | same constraints as row 12 | raw + canonical args | **not in the plan** — same effect as `open` | **REVIEW (new row)** |
| 14 | `files` `read` / `list` / `search` | 1 | runs automatically | `READ_ONLY` | `ALLOW` | no | inside effective safe roots only (see A.1.4) | path audited | no mutation | **AGREE** |
| 15 | `files` `move` | 1 | **runs automatically** | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | src and dst both named; `shutil.move` **overwrites** an existing dst — see D-03 | full chain | mutates the filesystem | **CONFLICT — undeclared mismatch M-06** |
| 16 | file **delete** | — | **no tool exists** (`files.py`: "Does not delete") | `DESTRUCTIVE_ACTION` | `DENY` today, `REQUIRE_CONFIRMATION` if ever built | n/a today | must stay `UNKNOWN_ACTION` → `REPORT_CAPABILITY_UNAVAILABLE` (§13.1) | capability-unavailable | no capability to authorize | **AGREE** |
| 17 | `obsidian` `note_read` / `note_search` | 1 | runs automatically | `READ_ONLY` | `ALLOW` | no | vault scope | `permission.decision` + `dispatch.*` | reads notes | **AGREE** |
| 18 | `obsidian` `note_create` / `note_append` | 1 | runs automatically | `REVERSIBLE_ACTION` | `ALLOW` | no | vault scope; append is recoverable | raw + canonical args | low-risk additive write | **AGREE** |
| 19 | `mcp_client` `status` | 1 | runs automatically | `READ_ONLY` | `ALLOW` | no | no server call in the stub | `permission.decision` + `dispatch.*` | status only | **AGREE (split from the plan's single row)** |
| 20 | `mcp_client` tool call (not implemented) | 1 | stub returns a plan | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | whitelisted servers only; server output untrusted | full chain | arbitrary external capability | **CONFLICT — declared mismatch M-04** |
| 21 | `cli` `status` / readiness | 1 | runs automatically | `READ_ONLY` | `ALLOW` | no | `shutil.which` only | `permission.decision` + `dispatch.*` | probe | **AGREE (split)** |
| 22 | `cli` harness run (not implemented) | 1 | stub returns a plan | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | per-harness allow-list | full chain + command | spawns external processes | **CONFLICT — declared mismatch M-04** |
| 23 | `browser_use` agent | 1 | **runs automatically** (stub today) | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | acts with the user's real session/cookies | full chain + goal text | acts as the user | **CONFLICT — declared mismatch M-03** |
| 24 | `shell` | 2 | confirmation required | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | existing `_BLOCKED_PATTERNS` retained; cwd root check retained; command quoted verbatim in the confirmation | full chain + command | arbitrary execution; see §C-composite | **AGREE** |
| 25 | `computer_use` | 2 | confirmation required | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | PC control per operator direction | full chain | GUI control | **AGREE** |
| 26 | `mouse_keyboard` | 2 | confirmation required | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | PC control per operator direction | full chain | GUI control | **AGREE** |
| 27 | `cad` design/export/print | 2 | confirmation required | `DESTRUCTIVE_ACTION` | `REQUIRE_CONFIRMATION` | **yes** | physical output; verify STL first; printing is out of project scope today | full chain | irreversible physical effect | **AGREE** |
| 28 | Discord / Telegram **send**, user-requested | — | **no registry tool** | `EXTERNAL_COMMUNICATION` | `DENY` today (no capability), `REQUIRE_CONFIRMATION` when built | n/a today | recipient + full body shown before sending | full chain + recipient | nothing to authorize yet | **REVIEW — plan overstates the inventory** |
| 29 | Discord / Telegram send, **JARVIS-originated** (confirmation prompt at `server.py:656-663`, completion notice at `820-827`, `reporter.send_report`) | — | **sends automatically, no confirmation** | `EXTERNAL_COMMUNICATION` | out of P4 action scope; needs an explicit system-egress rule | n/a | message content is JARVIS-authored, but the *egress* is real and unconfirmed | must be audited | real external communication exists today and is not covered by the plan | **REVIEW (D-06)** |
| 30 | Host shutdown / restart / suspend | — | **no tool**; `shell` `_BLOCKED_PATTERNS` rejects `shutdown`/`reboot` | `SYSTEM_POWER` | `DENY` | n/a | never inferred from prose | capability-unavailable | no capability; the blocklist is the current control | **AGREE** |
| 31 | JARVIS process/resource power (`POST /resource/sleep/*`, `/resource/wake`, `/resource/shutdown`, `app/cli.py shutdown`, kill-switch voice triggers) | — | **HTTP/CLI operator surface, no confirmation** | `PRIVILEGED_ACTION` if ever agent-reachable | `DENY` for any agent-initiated path | n/a | these are operator controls, not agent actions | audited if wired | not reachable from the tool registry; must never become an agent action implicitly | **REVIEW (D-07)** |
| 32 | Purchase / payment / checkout / transfer | — | **NONE CURRENTLY REGISTERED** | `FINANCIAL_PURCHASE` | `DENY` | n/a | must stay `UNKNOWN_ACTION` | capability-unavailable | no tool exists anywhere in `app/` | **AGREE** |
| 33 | Deploy / infrastructure mutation | — | **no tool** | `PRIVILEGED_ACTION` | `DENY` | n/a | must stay `UNKNOWN_ACTION` | capability-unavailable | no tool exists | **AGREE** |
| 34 | Database status query (`GET_DATABASE_STATUS`) | — | **no tool** | `READ_ONLY` if ever built | `DENY` today | n/a | see the capability-projection finding in §C.3 | capability-unavailable | the router's *default* context claims this action is supported; production has no such tool | **REVIEW (D-08)** |
| 35 | `health_check` | none | not callable (`Invalid tool module`) | n/a | n/a | n/a | fix at the registry layer, not with a permission row | — | orphan discovery entry | **REVIEW (A.1.1)** |

Rows 1–35 cover every registry key and every action subtype found in source, plus the four
contract-named capabilities that have no tool. **No capability appears twice; no wildcard row
exists.**

### B.1 Rules carried over from the plan, verified as still correct

1. The class is a property of **action + target**, not of the module (`files` read vs `files` move;
   `kasa` status vs `kasa` control; `mcp_client` status vs a real MCP call). Confirmed necessary by
   rows 9, 14/15, 19/20, 21/22.
2. `approval_mode` stays a **global tightening** control: it may raise `ALLOW` to
   `REQUIRE_CONFIRMATION`, never lower a decision. Today it can also *lower* the effective gate
   (`strict`/`safe`/`balanced` move one threshold for every tool at once) — P4 must keep only the
   tightening direction.
3. A capability with no authorized tool is **not** a permission `DENY` at the action layer; it is
   `UNKNOWN_ACTION` answered with `REPORT_CAPABILITY_UNAVAILABLE` (§13.1). Rows 16, 28, 32, 33, 34
   are written as `DENY` **of any dispatch**, reached through the capability path, not by inventing a
   policy prohibition. See §G.
4. Learned/remembered permissions are out of scope for v1 (§27 below).
5. The table is **data**, versioned, with `policy_version` in every decision and audit event.

---

## C. Mismatches

### C.1 The five declared mismatches (`PERMISSION_MATRIX_PLAN.md` §4) — all still present

| ID | Capability | CURRENT | PLANNED | WHY | RISK IF LEFT UNCHANGED |
|---|---|---|---|---|---|
| **M-01** | `apps` `close` | `SAFETY_LEVEL = 0` → runs with no confirmation | `REVERSIBLE_ACTION` + `REQUIRE_CONFIRMATION` | `close_app` runs `taskkill /IM <image> /F`; a force kill discards unsaved work | silent data loss on a misheard or mis-routed close; the user is never asked |
| **M-02** | `kasa` control (`on`/`off`/`toggle`/`set_brightness`) | module `SAFETY_LEVEL = 0`; the declared `CONTROL_SAFETY_LEVEL = 1` **is not read by the gate** | `REVERSIBLE_ACTION` + `REQUIRE_CONFIRMATION` | one module conflates a read and a physical-world write | unconfirmed physical actuation once the stub goes live; the declared constant gives false assurance |
| **M-03** | `browser_use` | `SAFETY_LEVEL = 1` → runs with no confirmation in `balanced` | `PRIVILEGED_ACTION` + `REQUIRE_CONFIRMATION` | it acts inside the user's authenticated browser session | an agent acting as the user with real cookies, unconfirmed, once the stub goes live |
| **M-04** | `mcp_client`, `cli` | `SAFETY_LEVEL = 1` → runs with no confirmation | `PRIVILEGED_ACTION` + `REQUIRE_CONFIRMATION` | arbitrary external servers / local processes | untrusted external capability reachable without a gate once the stubs go live |
| **M-05** | Destructive verbs | caught by a **prose** regex in `app/brain/router.py:186` (`delete\|format\|wipe\|…\|purchase\|buy`) that returns the `confirm_action` *intent*, i.e. a sentence, not an execution gate | permission class at the action level, decided before dispatch | the regex gates what JARVIS *says*, not what it *does*; a tool call that arrives by another route is not stopped by it | a destructive dispatch that never passes the prose path is ungated; conversely harmless words ("send", "install") force confirmation sentences |

All five survive verbatim. **None disappeared.**

### C.2 Mismatches found in this review that the plan does not declare

| ID | Capability | CURRENT | PROPOSED | WHY IT MATTERS |
|---|---|---|---|---|
| **M-06** | `files` `move` | `SAFETY_LEVEL = 1` → **runs with no confirmation** under `balanced` | `REVERSIBLE_ACTION` + `REQUIRE_CONFIRMATION` (plan's own table says "confirm") | The plan's §2 row already proposes confirmation, but its §4 mismatch list omits it, so the count "five" understates the change. `shutil.move` also silently **overwrites** an existing destination, which makes "reversible" optimistic (D-03). |
| **M-07** | `browser` `search` | `SAFETY_LEVEL = 1` → runs automatically | `REVERSIBLE_ACTION` + `ALLOW` | The action subtype is not in the plan at all. No behaviour change is proposed, but an undeclared subtype is an orphan row (§36). |
| **M-08** | `files` `search` | `SAFETY_LEVEL = 1` → runs automatically | `READ_ONLY` + `ALLOW` | Same: a real subtype the plan never lists. It reads file *contents* across the safe roots, so it belongs in the read-only inventory explicitly. |
| **M-09** | Messaging inventory | the plan lists "Discord / Telegram send (`app/comms/*`)" as a capability | there is **no registry tool**; the only sends are JARVIS-originated (rows 28/29) | The plan implies a user-requested messaging capability exists. It does not. Conversely, real unconfirmed egress *does* exist and the plan does not mention it. |

**Cause of the count change, as §35 requires:** the five declared mismatches are all still real and
none was removed. Four additional rows (M-06…M-09) come from reading the current source rather than
the plan's summary: two are action subtypes the plan never enumerated (`browser search`,
`files search`), one is a mismatch the plan states in its matrix but omits from its mismatch list
(`files move`), and one is an inventory error in the plan (messaging). The correct count against
today's source is **five declared + four newly identified = nine**.

### C.3 Capability-projection finding (input to P4/P5, not a permission row)

`app/execution/router.py` has `SUPPORTED_ACTIONS = {OPEN_APP, OPEN_URL, DEPLOY, DELETE_PATH,
GET_DATABASE_STATUS}` and `DEFAULT_ROUTER_CONTEXT.supported_actions` is that same set — the frozen
13B10C4 corpus set, correct for the passive module and documented as such in 13B11H. **Production
has tools for only two of those five**: `OPEN_APP` (`apps`) and `OPEN_URL` (`browser`). There is no
deploy tool, no delete capability and no database tool.

Consequence for P4: the capability projection handed to the router **at wiring time must be derived
from the real registry**, not from the default. If the default is used, `DEPLOY`, `DELETE_PATH` and
`GET_DATABASE_STATUS` would reach the permission engine as *supported* actions instead of becoming
`UNKNOWN_ACTION` → `REPORT_CAPABILITY_UNAVAILABLE` (§13.1, INV-011). Recorded as **D-08**.

---

## D. All REVIEW / CONFLICT rows in one place

| Row | Capability | Status | What must be decided or fixed |
|---|---|---|---|
| 4 | `web_search` fetch | REVIEW | egress constraint on a caller-supplied URL (D-04) |
| 7 | `vision` webcam | REVIEW | camera capture: automatic or confirmed (D-05) |
| 9 | `kasa` control | CONFLICT | M-02 — raise from the level-0 gate to `REQUIRE_CONFIRMATION` |
| 10 | `apps open` | CONFLICT | D-01 — plan says `ALLOW`, policy direction says PC control is confirmed |
| 11 | `apps close` | CONFLICT | M-01 — and D-02, whether the class is `REVERSIBLE_ACTION` or `DESTRUCTIVE_ACTION` |
| 13 | `browser search` | REVIEW | M-07 — add the subtype explicitly |
| 15 | `files move` | CONFLICT | M-06 + D-03 — confirmation, and overwrite semantics |
| 20, 22 | `mcp_client` call, `cli` run | CONFLICT | M-04 |
| 23 | `browser_use` | CONFLICT | M-03 |
| 28, 29 | messaging | REVIEW | M-09 + D-06 — system-originated egress is unconfirmed today |
| 31 | resource/power endpoints | REVIEW | D-07 — must stay unreachable from any agent path |
| 34 | database status | REVIEW | D-08 — capability projection must come from the registry |
| 35 | `health_check` | REVIEW | registry-layer fix; not a permission row |

No row is left unclassified, and no row was silently changed in the plan.

---

## Per-topic findings

### §10 Read-only actions — verified

`system_stats`, `calendar` read, `web_search` search, `screenshot`, `vision`, `kasa` status,
`files` read/list/search, `obsidian` read/search, `mcp_client` status, `cli` status. Each was
checked against the six tests in the review brief: none mutates external state, sends a message,
controls the PC, deletes, changes power state or purchases. Two carry qualifications rather than a
clean pass, and are marked REVIEW rather than guessed: `web_search` `fetch` (caller-supplied URL,
D-04) and `vision` webcam (privacy, D-05). `screenshot` and `vision` write a capture file locally;
that is an artefact of reading, not a mutation of user state, so the class stays `READ_ONLY`.

### §11 App / PC control

Current: `apps` is `SAFETY_LEVEL = 0` — both `open` and `close` run automatically. The operator's
stated direction is "PC control: confirmation required". `close` is unambiguous and is M-01.
`open` is where the plan and the direction disagree: the plan proposes `ALLOW` because the app name
must hit the `_APP_MAP` allow-list and an unknown name already returns an error without dispatching.
This review does **not** resolve that; it is **D-01**. The legacy level 0 is recorded as current
behaviour, not as justification.

### §12 Shell / command execution

`shell` is **arbitrary** command execution: the command string is passed through, `shlex.split` on
POSIX and `shell=True` on Windows. It is constrained only by a fourteen-pattern regex blocklist
(`rm -rf /`, `rm -rf ~`, `format`, `shutdown`, `reboot`, `mkfs`, `dd if=`, fork bomb, `> /dev/sda`,
`sudo rm`, `net user … /add`, `reg delete`, `rmdir /s`, `del /s`), a cwd root check, a 120-second
cap and truncated output. It can mutate the filesystem, spawn processes and change system state.

**The permission class cannot safely be uniform, and this review does not make it uniform.** A
single `PRIVILEGED_ACTION` + `REQUIRE_CONFIRMATION` for every shell command is the correct and
conservative v1 answer, because the alternative — deciding a class from the command text — is
exactly the semantic analysis the contract forbids the permission layer to perform. What the
confirmation can predeclare reliably is the **verbatim command string, the resolved cwd and the
timeout**; what it cannot predeclare is the *effect*. Recorded as a **P4/P5 design issue**: a
blocklist is not a permission model, and `shell` remains the largest single-capability risk in the
inventory. No command-semantics analysis is proposed or implemented here.

### §13 File operations

Production separates cleanly today: `read`/`list`/`search` are read-only, `move` mutates, and
**delete does not exist**. So the split the brief asks for is already available at the action
subtype, not only at the tool name — which is exactly why **the permission decision must bind to
the action subtype, not to the registry key `files`**. `move` must be confirmation-gated (M-06), and
its overwrite behaviour needs a decision (D-03). Delete must remain absent and, if ever added,
`DESTRUCTIVE_ACTION` + `REQUIRE_CONFIRMATION` with an exact absolute path, no globs, no invented
path (§17.1, INV-005).

### §14 Calendar

`app/tools/calendar.py` reads `.ics` files for a date. **There is no create, update, move or delete
path in production.** Read → `READ_ONLY` + `ALLOW` (row 2). Mutation → not a capability; if built,
`REVERSIBLE_ACTION` + `REQUIRE_CONFIRMATION` naming the event and time. No current-vs-plan mismatch:
the plan already marks calendar mutation "not implemented today". `registry._capability_for` maps
the tool unconditionally to `calendar_read`, which is accurate today and would silently mislabel a
future mutation — noted for P4.

### §15 Messaging

No user-invocable messaging tool exists. `app/comms/discord_bot.py` and `telegram_bot.py` expose
`send_message` / `send_status`, called from three JARVIS-originated places: the confirmation prompt
(`app/server.py:656-663`), the completion notice (`820-827`) and `app/agent/reporter.send_report`.
Reading messages is not implemented at all, so the read/send split the brief requires is trivially
preserved. Two distinct findings: the plan's inventory is wrong (M-09), and real outbound
communication happens today without a permission decision (row 29, D-06). Both are recorded; neither
is fixed here.

### §16 System power

No host power capability exists, and `shell` explicitly blocks `shutdown` and `reboot`. Class
`SYSTEM_POWER`, decision `DENY`, reached as capability-unavailable. Separately, `POST
/resource/shutdown`, `/resource/sleep/light`, `/resource/sleep/deep`, `/resource/wake`, `app/cli.py
shutdown` and the kill-switch voice triggers (`shutdown jarvis`, `kill jarvis`, `emergency stop`,
`power down`) affect **JARVIS's own process and model residency**, not the host. They are operator
surfaces, not tool-registry actions, and must not become agent-reachable implicitly (D-07).

### §17 Financial / purchase

**NONE CURRENTLY REGISTERED.** A source-wide search found the words only in the legacy router's
confirm-prose regex, in the classifier's action-verb lexicon and as the `FINANCIAL_PURCHASE` enum
member. No purchase, payment, checkout or transfer capability exists in `app/`. Class
`FINANCIAL_PURCHASE`, decision `DENY`, reached as capability-unavailable. No tool was invented.

### §18 Destructive

Present-day destructive or partially irreversible surfaces: `apps close` (force kill, unsaved work),
`files move` (overwrites the destination), `shell` (arbitrary), `cad` print (physical, out of scope
today). File delete does not exist. Where reversibility is ambiguous the conservative class is
proposed and the ambiguity is named rather than resolved silently: `apps close` (D-02) and
`files move` overwrite (D-03).

### §19 Privileged

`shell`, `computer_use`, `mouse_keyboard`, `browser_use`, `mcp_client` (real call), `cli` (harness
run). Deliberately **not** classified privileged: `system_stats`, which reads CPU/RAM/disk/GPU via
`psutil`, and `health_check`-style probes — reading system information is not an elevated
operation. No tool in the inventory requests elevation, sets credentials or edits security
configuration; `sudo rm` is blocklisted in `shell` but `sudo` in general is not, which is part of
the §12 finding.

### §20 Composite / dynamic tools

| Tool | Why the name is not enough | Proposed P4 decision input |
|---|---|---|
| `shell` | one key, unbounded effect | action type + the **verbatim command** + resolved cwd; class fixed at `PRIVILEGED_ACTION`, never derived from the command text |
| `files` | read and write behind one key | action **subtype** (`read`/`list`/`search`/`move`) + canonical source and destination paths |
| `apps` | open and force-kill behind one key | action subtype (`open`/`close`) + canonical app name |
| `kasa` | read and physical actuation behind one key | action subtype (read set vs control set) + device target |
| `browser` | `open` vs `search` | action subtype + canonical URL |
| `obsidian` | read/search vs create/append | action subtype + vault-relative path |
| `mcp_client`, `cli` | status vs real external invocation | action subtype + server/harness identity + the command |
| `web_search` | search vs arbitrary fetch | action subtype + the canonical URL (D-04) |
| `computer_use`, `mouse_keyboard` | free-form GUI control | class fixed; arguments audited, never used to lower the class |

The general rule the matrix implies: **a permission row is keyed by (action subtype, target scope),
and the registry key alone is never the key.** Nothing above is implemented here.

### §21 Permission decision input

Reviewed against `TARGET_COMPONENT_MAP.md` line 22 (`RouteResult`, tool metadata, policy table →
`PermissionDecision`) and `TOOL_INVOCATION_CONTRACT.md` §1. The input must bind:

* `action_type` — `PrimaryAction` from the router, never the model's wording;
* `action_subtype` — **new requirement from this review**; the router's five `PrimaryAction` members
  do not distinguish `files read` from `files move`, so the subtype must be part of the key;
* `target` — raw and canonical (see §25);
* `canonical_arguments` + `canonicalization_version`;
* `session_id` / `user_id` — required for confirmation binding (§12.3) and therefore available at
  the decision;
* `policy_version`.

The decision must be computable from those alone. Model prose is not an input.

### §22 Model non-authority — frozen for the sign-off packet

The model, Hermes included, **cannot**: choose its own `PermissionClass`; downgrade a class; return
`ALLOW` as an authority; bypass confirmation; alter the matrix; or mark itself trusted. Permission
policy is JARVIS-owned deterministic state (contract §11.2, §2.2). A permission denial is not
overridable by model prose, by user prose asserting authority, by retrieved content or by tool
output text.

### §23 Permission vs confirmation

Kept distinct. P4 decides *whether* confirmation is required and emits `REQUIRE_CONFIRMATION`. It
does **not** decide whether an approval has been received. In particular P4 must never treat "yes",
"do it", "go ahead" or "confirmed" in request text as approval — contract §12.2 forbids exactly
that, and `RequestClass.CONFIRMATION_SENSITIVE_ACTION` from the classifier means *this needs
confirmation*, never *this is confirmed*.

### §24 Permission vs routing

P4 consumes the structured route. It must not re-parse natural language: the router already owns
`PrimaryAction`, `target`, `target_resolved`, `ReportingIntent`, `multi_action` and
`capability_available`. Re-parsing would create the "second recogniser" the contract forbids (§15.3)
and would let two components disagree.

### §25 Permission vs canonicalization

Contract §9.1 requires both raw and canonical to be auditable. For security-sensitive matching the
canonical value is preferred **where a rule is declared** — and today `app/execution/canonicalize.py`
(`CANONICALIZATION_VERSION = "1"`) declares exactly **one** scope: `apps.app`, mapping
`{visual studio code, vs code, vscode} → vscode`. There is no path, URL or device canonicalization.

So P4 must: match on the canonical value where a rule exists; match on the **raw** value everywhere
else; and never assume a path or URL has been normalized. Both values go into the audit record.
No new canonicalization rule is created by this review.

### §26 Deny rules

`DENY` is reserved and deliberately narrow. Proposed `DENY` causes:

1. **No authorized tool for the action** — rows 16, 28, 30, 32, 33, 34. Note the nuance the plan
   states and this review preserves: this is *capability unavailability* (§13.1), so the user-facing
   answer is `REPORT_CAPABILITY_UNAVAILABLE`, and the permission layer's job is only to ensure no
   dispatch happens.
2. **Target cannot be validated** — unresolved or invented target (§17.1, INV-005).
3. **Malformed arguments** — canonicalization error, missing required argument.
4. **Unknown or unmapped action** — `UNKNOWN_ACTION`, and no nearest-tool substitution (§13.2,
   INV-011).
5. **Policy prohibition** — `FINANCIAL_PURCHASE` in v1, and any agent-initiated power action.
6. **Engine failure** — see §G.

No broad deny category beyond these is proposed.

### §27 Learned permissions

**Recommendation: NO — defer.** `PERMISSION_MATRIX_PLAN.md` §3.4 already states that learned or
remembered permissions ("always allow X") are out of scope for v1, and that if added later each must
be an explicit, user-approved, auditable record with its own expiry, never inferred from behaviour.
The operator's stated direction says the same. The initial P4 table is therefore **static and
deterministic**: a versioned data file, no runtime learning, no per-user overrides, no persistence
of "allow next time".

### §28 Policy version

`PERMISSION_MATRIX_PLAN.md` §3.5 requires a `policy_version` in every decision and audit event but
does **not** specify its initial value. Following the established convention in this series —
`CANONICALIZATION_VERSION = "1"`, `LANE_POLICY_VERSION = "1"`, `CLASSIFIER_VERSION = "1"`,
`ROUTER_VERSION = "1"` — the recommendation is:

**`PERMISSION_POLICY_VERSION = "1"`**, a module constant in `app/execution/permissions.py`, carried
in every `PermissionDecision` and every `permission.decision` audit event, and bumped whenever a row
changes class or outcome. The table itself lives in `config/permissions.yaml` per the plan; the
version string is the joint identity of the table and the rules that read it.

### §29 Fail-closed rule

Frozen expectation for every abnormal input — **NO EXECUTION**, and the exact production outcome is
`PermissionOutcome.DENY`:

| Condition | Outcome | Response obligation |
|---|---|---|
| Unknown action (`PrimaryAction.UNKNOWN_ACTION`) | `DENY` | `REPORT_CAPABILITY_UNAVAILABLE` |
| Action not present in the policy table | `DENY` | `REPORT_CAPABILITY_UNAVAILABLE` |
| Malformed or unresolved target (`target_resolved = False`) | `DENY` | `REQUEST_TARGET` |
| Malformed arguments / canonicalization error | `DENY` | `REPORT_CAPABILITY_UNAVAILABLE` |
| Invalid or unknown permission class | `DENY` | `REPORT_CAPABILITY_UNAVAILABLE` |
| Policy file missing, unparseable, or version unknown | `DENY` | `REPORT_CAPABILITY_UNAVAILABLE` |
| Permission-engine exception | `DENY` | `REPORT_CAPABILITY_UNAVAILABLE` |
| Audit write for the decision fails | `DENY` (fail-closed, per R-09) | `REPORT_CAPABILITY_UNAVAILABLE` |

**No default-allow path may exist**, and the absence of a row is never an implicit `ALLOW`.

### §30 Multi-action

`PrimaryAction.MULTI_ACTION_UNSUPPORTED` must produce **no executable permission result**. P4 must
not decompose the result and authorize component actions individually — the router deliberately does
not expose a preferred first action, and INV-012 forbids silent partial execution. Recommended
outcome: `DENY`, obligation `REPORT_MULTI_ACTION_LIMIT`.

### §31 Ambiguity

An ambiguous or missing target must not receive executable authorization, and the permission layer
must not invent or fill a target (§17.1, INV-005). The router already reports `target_resolved =
False` while preserving the user's own words; P4 consumes that flag. Recommended outcome: `DENY`,
obligation `REQUEST_TARGET`.

### §32 Unknown action

`PrimaryAction.UNKNOWN_ACTION` must never become authorized, and no nearest supported action may be
substituted (§13.2, INV-011). Recommended outcome: `DENY`, obligation
`REPORT_CAPABILITY_UNAVAILABLE`.

### §33 NONE

`PrimaryAction.NONE` means the turn carries no executable action at all. It must never produce a
dispatchable `ALLOW`. The exact passive outcome recommended: **the permission engine is not invoked
at all** for a `NONE` route — there is no action to authorize — and if it is invoked defensively it
returns `DENY` with a reason naming the absent action, never `ALLOW`. The turn's answer comes from
the obligation engine (P6), not from permissions.

### §34 Legacy `SAFETY_LEVEL` migration

Current vocabulary: an integer 0–3 per **module**, thresholded by `approval_mode`
(`strict` → confirm at ≥ 0, `safe` → ≥ 1, `balanced` (live) → ≥ 2), with ≥ 3 blocked outright.

**The mapping is not one-to-one and must not be implemented as one.**

| Legacy | Live behaviour (`balanced`) | Contract v1 | Migration implication |
|---|---|---|---|
| `SAFETY_LEVEL = 0` | automatic | `READ_ONLY` **or** `REVERSIBLE_ACTION` | splits: `system_stats` is read-only, `apps close` and `kasa` control are not. Level 0 cannot be mapped to `ALLOW` |
| `SAFETY_LEVEL = 1` | automatic | `READ_ONLY`, `REVERSIBLE_ACTION` **or** `PRIVILEGED_ACTION` | splits three ways: `files read` vs `files move` vs `browser_use`. The most dangerous current gap sits here — level 1 runs unconfirmed |
| `SAFETY_LEVEL = 2` | confirmation required | `PRIVILEGED_ACTION` or `DESTRUCTIVE_ACTION` | closest to a clean mapping; behaviour is preserved, the class becomes explicit |
| `SAFETY_LEVEL = 3` | blocked outright | no v1 equivalent; nearest is a policy `DENY` | no tool currently declares level 3 |
| absent (`health_check`) | not callable | n/a | registry-layer fix |
| `approval_mode` | moves every threshold at once, up **or** down | tightening only | `balanced` must be the floor, not a dial |

The one-line summary for the operator: **the risk concentrates in legacy level 1**, which runs
without confirmation today and contains both read-only and privileged capabilities.

### §36 Completeness

Every registry key appears exactly once at the correct semantic level. The 17 explicit keys expand
to **24 implemented action-scoped rows** (1–15, 17–19, 21, 23–27). Three further rows name subtypes
that exist in the contract or the plan but have no working implementation behind them: row 16 (file
delete, no tool at all), rows 20 and 22 (the real `mcp_client` call and the real `cli` harness run,
both stubs today). Rows 28–34 are the contract-named capabilities with no tool — messaging, host
power, JARVIS resource power, purchase, deploy, database status. Row 35 is the single
unclassifiable discovery entry, marked REVIEW. Coverage check: `apps` 10/11, `browser` 12/13,
`browser_use` 23, `cad` 27, `calendar` 2, `cli` 21/22, `computer_use` 25, `files` 14/15,
`kasa` 8/9, `mcp_client` 19/20, `mouse_keyboard` 26, `obsidian` 17/18, `screenshot` 5, `shell` 24,
`system_stats` 1, `vision` 6/7, `web_search` 3/4, `health_check` 35 — 18 of 18 discovered modules.
No orphan, no duplicate, no wildcard.

### §37 Confirmation TTL ownership

`CONFIRMATION_STATE_PLAN.md` §6 proposes 5 minutes for `REVERSIBLE_ACTION` and
`EXTERNAL_COMMUNICATION`, 2 minutes for `DESTRUCTIVE_ACTION` / `SYSTEM_POWER` /
`PRIVILEGED_ACTION`, configurable per class.

**Recommended separation, which this review endorses:** the **value** is per-class policy data and
belongs beside the matrix in `config/permissions.yaml`; **enforcement** — clock, expiry sweep,
`EXPIRED` transition, expiry-on-load — belongs to the confirmation state machine, not to P4's
permission engine. P4 may *declare* `REQUIRE_CONFIRMATION` and *carry* the class's TTL value into
the confirmation record. **No TTL is implemented here.**

### §38 Audit requirements

`app/execution/audit_events.py` (schema v3, `EXECUTION_AUDIT_SCHEMA_VERSION = 3`) already provides
what is needed; **no schema change is proposed and none was made.** The permission decision maps to
the existing `ExecutionAuditEvent.PERMISSION_DECISION` (`"permission.decision"`), whose
`REQUIRED_FIELDS_BY_EVENT` entry is `{"permission_decision"}`, one of the seventeen
`CONTRACT_AUDIT_FIELDS`.

The `permission_decision` mapping must carry at least: `action_type`, `action_subtype`, `target`
(raw) and a reference to canonical arguments, `permission_class`, `permission_outcome`,
`confirmation_required`, `reason`, `policy_version`. Correlation (`session_id`, `turn_id`, and
`invocation_id` / `confirmation_id` when present) comes from `CorrelationContext`, so no new
correlation field is required. `FORBIDDEN_REASONING_FIELDS` continues to apply: no model
deliberation in the record.

---

## E. Decisions requiring operator approval

Only genuinely unresolved items appear here. Anything the contract already freezes (classes,
model non-authority, fail-closed, deny-before-dispatch, no learned permissions in v1) is **not** a
choice and is not listed.

| ID | Question | Recommended option | Alternatives | Security effect | Behaviour effect |
|---|---|---|---|---|---|
| **D-01** | Is launching an allow-listed application (`apps open`) `ALLOW` or `REQUIRE_CONFIRMATION`? | **`ALLOW`** — the `_APP_MAP` allow-list is a real constraint, an unknown name already fails without dispatch, and launching is trivially reversible | confirm every launch (matches "PC control: confirmation required" literally) | low: bounded to 19 known applications, no arguments passed | keeps "open VS Code" a one-step voice action; confirming it would make the most common action two-step |
| **D-02** | Is `apps close` `REVERSIBLE_ACTION` or `DESTRUCTIVE_ACTION`? | **`REVERSIBLE_ACTION` + `REQUIRE_CONFIRMATION`** (the plan's position) | `DESTRUCTIVE_ACTION` + `REQUIRE_CONFIRMATION` | identical today — both confirm | differs only later, when per-class TTL applies: 5 min vs 2 min, and destructive wording in the prompt |
| **D-03** | May `files move` overwrite an existing destination? | **No** — refuse when the destination exists, and require a distinct confirmation for an explicit overwrite | allow overwrite inside the confirmation | prevents a "reversible" move from destroying a file | a move onto an existing name fails with a clear message instead of silently replacing |
| **D-04** | Should `web_search action="fetch"` be constrained? | **Yes** — deny loopback, link-local and RFC1918 destinations, non-HTTP(S) schemes and redirects that leave those bounds; keep `ALLOW` for public URLs | leave unconstrained; or raise to `REQUIRE_CONFIRMATION` | closes an internal-network read reachable from untrusted retrieved content | no effect on normal research use |
| **D-05** | Is `vision` **webcam** capture automatic like screen capture? | **`REQUIRE_CONFIRMATION` for webcam**, `ALLOW` for screen | both automatic (today's behaviour, and the plan's) | camera capture becomes a deliberate act | one extra confirmation on webcam requests only |
| **D-06** | JARVIS-originated Discord/Telegram sends (confirmation prompts, completion notices, morning report) — are they in the permission model? | **Out of the P4 action matrix, but governed by an explicit system-egress rule**: allowed only for JARVIS-authored status text, never for user or tool content, and audited | bring them under `EXTERNAL_COMMUNICATION` + confirmation (would make the confirmation prompt itself need confirmation) | prevents the notification path becoming an exfiltration channel for tool output | none for normal use |
| **D-07** | `POST /resource/*`, `app/cli.py shutdown` and the kill-switch triggers — agent-reachable? | **Never.** `DENY` for any agent-initiated path; they stay operator-only surfaces | expose sleep/wake as an agent capability later, under `PRIVILEGED_ACTION` | keeps the agent unable to power-manage its own host process | none today |
| **D-08** | What capability set does the router receive once wired? | **Derive it from the real registry** — today `{OPEN_APP, OPEN_URL}` only | keep the frozen default `{OPEN_APP, OPEN_URL, DEPLOY, DELETE_PATH, GET_DATABASE_STATUS}` | with the default, three tool-less actions would reach the permission engine instead of becoming `UNKNOWN_ACTION` | "deploy to staging" / "delete X" / "check the database" correctly answer capability-unavailable |
| **D-09** | `approval_mode` in the new model | **Tightening only**: `balanced` becomes the floor; `strict`/`safe` may raise a decision, never lower it | keep today's symmetric threshold | removes a single setting that can disable every confirmation at once | `strict` still works; no way to loosen below the matrix |
| **D-10** | Confirm the policy version string | **`PERMISSION_POLICY_VERSION = "1"`** | any other initial value | none | matches the four existing `"1"` version constants |

---

## F. Policy-version recommendation

`PERMISSION_POLICY_VERSION = "1"` (see §28), recorded in every `PermissionDecision` and every
`permission.decision` audit event, with `config/permissions.yaml` carrying the table. Awaiting D-10.

## G. Fail-closed rules

Frozen in §29 above: eight conditions, all `PermissionOutcome.DENY`, all **no execution**, no
default-allow path, an absent row is never an implicit allow, and a failed audit write of the
decision is itself a deny.

## H. Confirmation boundary

P4 declares `REQUIRE_CONFIRMATION` and nothing more. It does not create, store, match or expire
confirmations; it does not read approval from request text; it does not hold the clock. TTL values
are policy data, TTL enforcement is the confirmation state machine (§37). `registry.call(...,
confirmed=True)` remains the only bypass of the legacy gate, and P4 does not call it.

## I. P4 implementation scope, if approved

**In scope:** `app/execution/permissions.py` (pure function over action, subtype, target, canonical
arguments and the policy table); `config/permissions.yaml` (the approved matrix as data);
`PERMISSION_POLICY_VERSION`; a frozen `PermissionDecision` result type reusing the P0
`PermissionClass` / `PermissionOutcome`; the fail-closed table from §29; tests including CT-004 and
CT-015; passive and unwired, exactly as P0–P3 were.

**Explicitly out of scope for the permission unit:** the confirmation manager and its store, state
machine, binding and TTL enforcement (`IMPLEMENTATION_PHASES.md` bundles both into P4 — this review
recommends splitting them into two commits, permission engine first, because the permission engine
is pure over action and target while the confirmation manager needs a clock and a store); any
dispatcher change; any `SAFETY_LEVEL` change; any registry change; any live wiring; `approval_mode`
semantics (D-09) if the operator defers it.

**Entry criterion for that task:** operator sign-off of this packet, including D-01…D-10.

## J. Production non-change statement

**NO PRODUCTION CHANGE MADE.** Production `/home/jarvis/JARVIS` remains at
`03cab4960156220fe9b6c3a444fa7a41265c01e0`, clean, 0 untracked, 7 ahead of origin, nothing pushed,
`execution.mode = legacy`, `hermes_brain = false`, `hermes_enabled = false`. No production file was
created, modified or deleted; no tool was imported or executed; the inventory was produced by AST
parsing and source reading. `app/execution/permissions.py` does not exist. Hermes remains at
`2237be35…`, clean, with no process started. The 13B11H evidence bundle re-verified with 0 failures
and its digest is unchanged.

### J.1 Measured non-change proof

Taken after the review was written, on `192.168.0.162`:

```
HEAD                      03cab4960156220fe9b6c3a444fa7a41265c01e0
git status --porcelain    0 lines
app/execution/permissions.py     does not exist
config/permissions.yaml          does not exist
app/execution/                   __init__ audit_events canonicalize classifier
                                 correlation lane provenance router types   (9 files, unchanged)
```

Critical-file hashes, identical to those recorded in the 13B11H evidence bundle
(`12-legacy-non-change-proof.txt`):

```
e70d4d50cc11395253648194a82506bb5a2a53be446f47bb7d00f7a720b99b41  app/tools/registry.py
a41127209add60d196ffacf9db655953108e31e1d69f6a7159ef9baf97c4c887  app/computer/safety.py
b1448ed13d5e1d8d9a6afdd00630e394f7c330ec25bd1a63a0ce35ecf3797a70  app/server.py
247633cbd58a6297cbf94e7b293da905fbe521f1f2964b33bfa10d91c41875a3  config.yaml
881eda40dd8007600d38170904388c41856c88cc4d4b780bd43309aedcc6e598  app/execution/types.py
cac2b32c34367e2aefbe1b6eb63efc62bd155b9bfcc8c1be4c5ed4da3cc918e8  app/execution/audit_events.py
d44ebf3eedda8456d6ea606897dadb83a433b448dd6e2260912cc87d05a3ace3  app/brain/router.py
```

`git reflog` shows no commit after `03cab49` (the 13B11H amend).

## K. Workspace / document changes made by this review

1. **New:** `tasks/task13b11i-review/PERMISSION_MATRIX_REVIEW.md` — this packet. The directory is
   named `task13b11i-review` precisely so it cannot be mistaken for the implementation task's
   `tasks/task13b11i/`.
2. **Modified, documentation only:** `CLAUDE.md` "Current Status" — four lines recording that this
   sign-off packet exists and that P4 remains not started. `CLAUDE.md` instructs that Current Status
   be updated at the end of every session; a review session is a session, and leaving the status
   claiming only "P4 next, not started" would omit that the entry criterion is now packaged and
   awaiting ten operator decisions. The change is **workspace clone only** — production's copy stays
   byte-identical — and states no implementation.
3. **Modified:** `tasks/loop-log.md` — one entry recording the review.

Nothing else. `tasks/task13b11a/PERMISSION_MATRIX_PLAN.md` was **not** edited: every divergence
found is recorded here instead, exactly as the review brief requires.
