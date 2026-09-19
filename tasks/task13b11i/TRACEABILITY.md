# Traceability

## Contract clauses

| Clause | Requirement | Where it lives | Test |
|---|---|---|---|
| §11.1 | at least the seven permission classes | `PermissionClass` imported unchanged from `types.py` | `test_the_shared_enums_were_not_extended` |
| §11.2 | no model self-authorizes; decided from action + target, before dispatch | no model field exists in `PermissionRequest`; `decide()` is pure | `test_the_request_has_no_field_a_model_could_fill`, `test_a_model_draft_cannot_be_passed_as_authority` |
| §11.2 | a denial is not overridable by prose | arguments never influence the outcome | `test_a_denial_is_not_overridable_by_any_supplied_text`, `test_argument_values_never_change_the_outcome` |
| §12.1 | confirmation is JARVIS-owned state; requiring it is not having it | `REQUIRE_CONFIRMATION` is an outcome; no record, id, store or clock exists | `test_no_confirmation_machinery_exists_here` |
| §12.2 | "proceeding"/"confirmed" is never confirmation | affirmative text changes nothing | `test_affirmative_text_is_never_read_as_approval` |
| §13.1 | no authorized tool → capability unavailable | unregistered rows deny with `NO_CAPABILITY` | `test_d08_*`, `test_every_unregistered_row_denies` |
| §13.2 | no nearest-tool substitution | one declared action↔capability map, two entries, enforced both ways | `test_action_and_capability_must_agree_in_both_directions` |
| §17.1 | an ambiguous target is never invented | `target_resolved=False` denies; no target is synthesized | `test_unresolved_target_denies`, `test_permission_layer_never_invents_a_target` |
| §19.1 | the permission decision is one of the seventeen audit fields | `to_mapping()` matches the existing `permission_decision` field | `test_a_future_permission_decision_event_can_carry_this_result` |
| §19.2 | no chain-of-thought in audit | the mapping carries no deliberation field | `test_mapping_contains_no_model_deliberation_field` |

## Invariants

| Invariant | Statement | Test |
|---|---|---|
| INV-004 | confirmation-required actions cannot execute before valid confirmation | `test_d01_*`, `test_d02_*`, `test_no_confirmation_machinery_exists_here` |
| INV-005 | ambiguous required targets cannot be invented | `test_permission_layer_never_invents_a_target` |
| INV-011 | unsupported actions cannot be silently mapped to unrelated tools | `test_d08_a_routed_abstraction_cannot_borrow_a_registered_capability` |
| INV-012 | multiple actions cannot be silently partially executed | `test_non_executable_actions_deny_before_any_row[MULTI…]` |
| INV-013 | production side effects require JARVIS permission policy | the whole module; `test_only_row_matched_can_carry_a_non_deny_outcome` |
| INV-014 | destructive actions require deterministic confirmation policy | `cad.print`, `files.move.overwrite`, `files.delete` rows + their tests |

## Operator decisions

Every one of D-01…D-10 has at least one named test; the mapping is the last column of
`OPERATOR_DECISIONS.md`. 46 tests in `permissions_decisions_test.py`.

## Plan documents

| Document | What was taken from it | Deviation |
|---|---|---|
| `PERMISSION_MATRIX_PLAN.md` | the matrix shape, the action+target rule, approval_mode as tightening, learned permissions out of scope, fail-closed | outcome spelling (`CONFIRM` → `REQUIRE_CONFIRMATION`); YAML deferred |
| `PERMISSION_MATRIX_REVIEW.md` | the 35 authoritative rows, the nine mismatches, the real inventory, the fail-closed table, the version recommendation | rows 7 and 10 amended by D-05 and D-01 |
| `IMPLEMENTATION_PHASES.md` | P4 entry criterion and scope | P4 split: permission engine now, confirmation manager separately |
| `TARGET_COMPONENT_MAP.md` line 22 | `app/execution/permissions.py`, `RouteResult` + policy table → `PermissionDecision` | the route is supplied as fields, not as a `RouteResult` object, so permissions never imports the router |
| `CONFIRMATION_STATE_PLAN.md` | the TTL values and the boundary | TTLs are not implemented; enforcement belongs to the confirmation phase |
| `AUDIT_PLAN.md` / schema v3 | the `permission.decision` event and `permission_decision` field | unchanged; nothing is emitted |

## The nine mismatches from the review, preserved as context

M-01 `apps close`, M-02 `kasa` control, M-03 `browser_use`, M-04 `mcp_client`/`cli`,
M-05 destructive-verb prose regex, M-06 `files move`, M-07 `browser search`, M-08 `files search`,
M-09 messaging inventory. Each is a row in the table whose policy differs from today's legacy
behaviour, **and none of them changes production behaviour yet** — the engine is unwired, and the
legacy `SAFETY_LEVEL` gate is byte-identical. M-05 is the one with no row of its own: it is a
property of `app/brain/router.py`, which this task does not touch.
