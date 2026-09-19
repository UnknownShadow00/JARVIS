# Operator Decisions D-01…D-10 — as signed off

Source: the operator sign-off issued for task 13B11I, which answers the ten decisions raised in
`tasks/task13b11i-review/PERMISSION_MATRIX_REVIEW.md` §E. Where the sign-off differs from the
review's recommendation, **the sign-off governs** and the difference is stated.

| ID | Decision as signed off | Review had recommended | Encoded as | Named test |
|---|---|---|---|---|
| **D-01** | Application launch / PC control → `REQUIRE_CONFIRMATION`. Do **not** use automatic `ALLOW`. | `ALLOW` for `apps open` | row `apps.open` = `REVERSIBLE_ACTION` / `REQUIRE_CONFIRMATION` | `test_d01_app_launch_requires_confirmation` |
| **D-02** | `apps close` → `PermissionClass.REVERSIBLE_ACTION`, outcome `REQUIRE_CONFIRMATION`. Not `DESTRUCTIVE_ACTION`. TTL differences belong to the confirmation phase. | same | row `apps.close` | `test_d02_app_close_is_reversible_and_confirmed` |
| **D-03** | Non-overwriting move → the reversible-action policy. **Overwrite → `DENY` by default.** A reversible move permission must never authorize an overwrite. | forbid overwrite | rows `files.move` and `files.move.overwrite`; unknown overwrite state fails closed | `test_d03_move_overwrite_denied`, `test_d03_move_overwrite_state_unknown_denies` |
| **D-04** | A caller-supplied fetch target must not gain authority to reach loopback, RFC1918/private, link-local or equivalent internal targets. Passive task: **do not build networking code**; encode the requirement so future integration cannot treat arbitrary fetch as unrestricted `ALLOW`. | constrain fetch | row `web_search.fetch` carries required constraint `EGRESS_TARGET_POLICY`; unsatisfied → `DENY`, never a bare `ALLOW` | `test_d04_fetch_without_egress_constraint_denies`, `test_d04_fetch_is_never_unconditional_allow` |
| **D-05** | Webcam capture → `REQUIRE_CONFIRMATION`. | same | row `vision.webcam` (screen capture stays `ALLOW`) | `test_d05_webcam_requires_confirmation` |
| **D-06** | System-originated messaging egress → **`DENY`** for v1. No autonomous outbound message may bypass user confirmation. | a system-egress rule | rows `messaging.system_egress` and `messaging.send`, both `EXTERNAL_COMMUNICATION` / `DENY` | `test_d06_system_originated_messaging_denied` |
| **D-07** | `/resource/*` capabilities are never agent-reachable → `DENY`. | same | row `resource.control` | `test_d07_resource_control_denied` |
| **D-08** | Capability state **must** come from the real production inventory. `DEPLOY`, `DELETE_PATH`, `GET_DATABASE_STATUS` have no executable capability and remain unavailable. No invented capability. | same | `UNAVAILABLE_ACTIONS` gate before any table lookup; rows `deploy.execute`, `files.delete`, `database.status` all `DENY` | `test_d08_*` (four tests) |
| **D-09** | `approval_mode` is **tightening only**: never `DENY`→`ALLOW`, never `REQUIRE_CONFIRMATION`→`ALLOW`, never weakens a row. | same | `tighten()` over a total strictness order; exhaustively tested | `test_d09_approval_mode_is_monotonic_over_every_pair` |
| **D-10** | `PERMISSION_POLICY_VERSION = "1"` exactly. | same | module constant, carried in every decision | `test_d10_policy_version_is_exactly_one` |

## One tension recorded, not silently resolved

D-01 is worded "application launch / **PC control** → REQUIRE_CONFIRMATION", and the review question
it answers was specifically about `apps open`. The signed-off matrix keeps `browser.open` and
`browser.search` at `ALLOW` (review rows 12–13, status AGREE, never raised as a decision).
Opening a URL does launch a browser window, so an operator who reads "PC control" broadly might
expect those gated too.

This implementation follows the signed-off matrix literally: `apps.open` is confirmation-gated,
`browser.open`/`browser.search` are not. Changing `browser.*` would be a policy change with no
sign-off behind it, so it is **not** made here. Raised as an open question for the confirmation
phase; a one-line operator answer flips two rows and two tests.
