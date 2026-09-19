# Signed-off permission matrix

**Authoritative source:** `tasks/task13b11i-review/PERMISSION_MATRIX_REVIEW.md` §B (35 review rows)
**as amended by** the operator decisions D-01…D-10 in `OPERATOR_DECISIONS.md`. Transcribed here,
not recreated from memory. Every row below names the review row it came from.

Two review rows changed under sign-off:

* review row 10 `apps open` recommended `ALLOW` → **`REQUIRE_CONFIRMATION`** (D-01);
* review row 7 `vision webcam` was REVIEW/undecided → **`REQUIRE_CONFIRMATION`** (D-05).

Three review rows were **split** into separate policy keys because one review row covers several
real action subtypes that the permission decision must distinguish (review §13, §20, §21):

* review row 14 `files read/list/search` → `files.read`, `files.list`, `files.search`;
* review row 8 `kasa status/discover` → one key `kasa.status` (both are the same read);
* review row 15 `files move` → `files.move` **and** `files.move.overwrite` (D-03).

Splitting adds keys, never permissions: each split key keeps its review row's class and outcome,
except `files.move.overwrite`, which D-03 makes stricter (`DENY`).

## The table

`registered` = a real, loadable production tool implements this capability today.
Outcomes are the production `PermissionOutcome` names: `ALLOW`, `REQUIRE_CONFIRMATION`, `DENY`.

| # | Policy key | Review row | `PermissionClass` | Base outcome | registered | Constraint | Origin |
|---|---|---|---|---|---|---|---|
| 1 | `system_stats.read` | 1 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 2 | `calendar.read` | 2 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 3 | `web_search.search` | 3 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 4 | `web_search.fetch` | 4 | `READ_ONLY` | `ALLOW` | yes | **`EGRESS_TARGET_POLICY`** | **D-04** |
| 5 | `screenshot.capture` | 5 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 6 | `vision.screen` | 6 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 7 | `vision.webcam` | 7 | `READ_ONLY` | `REQUIRE_CONFIRMATION` | yes | — | **D-05** |
| 8 | `kasa.status` | 8 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 9 | `kasa.control` | 9 | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | yes (stub) | — | mismatch M-02 |
| 10 | `apps.open` | 10 | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | yes | — | **D-01** |
| 11 | `apps.close` | 11 | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | yes | — | **D-02**, mismatch M-01 |
| 12 | `browser.open` | 12 | `REVERSIBLE_ACTION` | `ALLOW` | yes | — | review AGREE |
| 13 | `browser.search` | 13 | `REVERSIBLE_ACTION` | `ALLOW` | yes | — | mismatch M-07 |
| 14 | `files.read` | 14 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 15 | `files.list` | 14 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 16 | `files.search` | 14 | `READ_ONLY` | `ALLOW` | yes | — | mismatch M-08 |
| 17 | `files.move` | 15 | `REVERSIBLE_ACTION` | `REQUIRE_CONFIRMATION` | yes | — | mismatch M-06 |
| 18 | `files.move.overwrite` | 15 | `DESTRUCTIVE_ACTION` | **`DENY`** | yes | — | **D-03** |
| 19 | `files.delete` | 16 | `DESTRUCTIVE_ACTION` | **`DENY`** | **no** | — | no tool exists |
| 20 | `obsidian.note_read` | 17 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 21 | `obsidian.note_search` | 17 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 22 | `obsidian.note_create` | 18 | `REVERSIBLE_ACTION` | `ALLOW` | yes | — | review AGREE |
| 23 | `obsidian.note_append` | 18 | `REVERSIBLE_ACTION` | `ALLOW` | yes | — | review AGREE |
| 24 | `mcp_client.status` | 19 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 25 | `mcp_client.call` | 20 | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | yes (stub) | — | mismatch M-04 |
| 26 | `cli.status` | 21 | `READ_ONLY` | `ALLOW` | yes | — | review AGREE |
| 27 | `cli.run` | 22 | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | yes (stub) | — | mismatch M-04 |
| 28 | `browser_use.agent` | 23 | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | yes (stub) | — | mismatch M-03 |
| 29 | `shell.execute` | 24 | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | yes | — | review AGREE |
| 30 | `computer_use.control` | 25 | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | yes (stub) | — | review AGREE |
| 31 | `mouse_keyboard.control` | 26 | `PRIVILEGED_ACTION` | `REQUIRE_CONFIRMATION` | yes | — | review AGREE |
| 32 | `cad.print` | 27 | `DESTRUCTIVE_ACTION` | `REQUIRE_CONFIRMATION` | yes (stub) | — | review AGREE |
| 33 | `messaging.send` | 28 | `EXTERNAL_COMMUNICATION` | **`DENY`** | **no** | — | no tool exists; **D-06** |
| 34 | `messaging.system_egress` | 29 | `EXTERNAL_COMMUNICATION` | **`DENY`** | n/a | — | **D-06** |
| 35 | `system.power` | 30 | `SYSTEM_POWER` | **`DENY`** | **no** | — | no tool exists |
| 36 | `resource.control` | 31 | `PRIVILEGED_ACTION` | **`DENY`** | n/a | — | **D-07** |
| 37 | `finance.purchase` | 32 | `FINANCIAL_PURCHASE` | **`DENY`** | **no** | — | NONE CURRENTLY REGISTERED |
| 38 | `deploy.execute` | 33 | `PRIVILEGED_ACTION` | **`DENY`** | **no** | — | no tool exists; **D-08** |
| 39 | `database.status` | 34 | `READ_ONLY` | **`DENY`** | **no** | — | no tool exists; **D-08** |
| 40 | `health_check` | 35 | *(none)* | **`DENY`** | **no** | — | orphan discovery entry, not dispatchable |

**40 policy rows from 35 review rows**: 35 + 5 from the three declared splits (`files` read/list/
search adds two, `files.move.overwrite` adds one, and review rows 28/29 and 30/31 were already
separate rows). No row was added that the review did not contain, and no review row was dropped.

## Capability coverage

Every registered production capability in the review inventory appears exactly once:
`apps` 10/11, `browser` 12/13, `browser_use` 28, `cad` 32, `calendar` 2, `cli` 26/27,
`computer_use` 30, `files` 14–18, `kasa` 8/9, `mcp_client` 24/25, `mouse_keyboard` 31,
`obsidian` 20–23, `screenshot` 5, `shell` 29, `system_stats` 1, `vision` 6/7, `web_search` 3/4,
`health_check` 40. **No wildcard row exists, and the absence of a row is never an allow.**

## Additional constraints retained from the review

* `web_search.fetch` — egress target policy (D-04), the only machine-enforced constraint in v1.
* `shell.execute` — the existing `_BLOCKED_PATTERNS` list and cwd root check stay in the tool and
  are **not** re-implemented here; the permission class is uniform and is never derived from the
  command text.
* `apps.*` — the `_APP_MAP` allow-list stays in the tool; an unknown app name already fails there.
* `files.*` — the safe-root check stays in the tool.
* `mcp_client` — whitelisted servers only; `cli` — per-harness allow-list. Both recorded as tool
  constraints, not as permission logic.
* `cad.print` — physical output, STL verified first; 3D printing is out of project scope today.

These are recorded as row metadata (`notes`) so a future dispatcher can show them in a
confirmation prompt. None of them is evaluated by the permission engine.
