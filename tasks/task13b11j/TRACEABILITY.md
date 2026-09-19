# Traceability — Task 13B11J

## 1. Contract v1 → implementation

| Clause | Requirement | Where | Proof |
|---|---|---|---|
| §12.1 | confirmation is control-plane state; `executed = false` while pending; no execution before a valid confirmation | `ConfirmationRecord.execution_started`, `EXECUTION_STARTED_STATES` | `test_no_record_this_phase_can_build_reports_execution`, proofs §7 |
| §12.1 | the action state is `CONFIRMATION_REQUIRED` | `ToolResultStatus` / `ProvenanceSource`, unchanged | `test_the_action_state_vocabulary_is_separate_and_unchanged` |
| §12.2 | the model must not mark an action confirmed; "proceeding" is not confirmation | no text entry point exists | `test_no_module_function_compares_against_affirmative_text` (0 string comparisons), `test_prose_is_not_a_confirmation_id` |
| §12.3 | binding to action type, target, arguments, requesting user/session | `ConfirmationBinding`, 12 fields | `test_binding_carries_the_twelve_frozen_fields`, 12 mutation tests |
| §12.3 | expiry or freshness | `expires_at`, `is_fresh_at`, expire-on-access | 8 expiry tests at explicit timestamps |
| §8.1, §13.1 | multi-action and unsupported actions are not dispatchable | `NON_CONFIRMABLE_ACTIONS` | `test_creation_refuses_a_non_confirmable_action` |
| §9.1, INV-006 | raw and canonical arguments both auditable | both stored, both bound, both serialized | `test_raw_and_canonical_arguments_are_both_retained` |
| §11.2 | no model may self-authorize; a denial is not overridable by prose | outcome comes from P4, never from a caller string | `test_creation_refuses_allow_and_deny_directly`, security §7 |
| §19.1 | `confirmation_state` is one of the seventeen audit fields | `to_audit_payload()` | all five events validated and serialized |
| INV-004 | confirmation-required actions cannot execute before valid confirmation | the approval edge is a wall | security §8, `test_confirm_edge_is_never_applied` |
| INV-014 | destructive actions require deterministic confirmation policy | deterministic table, no branches | `test_next_state_matches_the_frozen_cell` × 42 |
| INV-015 | no action occurs because prose claims it should | nothing executes at all | registry/audit/provenance monkeypatch tests |
| INV-020 | untrusted content never alters control-plane policy | tables are read-only frozensets / `MappingProxyType` | `test_the_table_is_read_only` |

## 2. `CONFIRMATION_STATE_PLAN.md` → implementation

| Plan | Implemented as | Note |
|---|---|---|
| §2 record, 13 rows | `ConfirmationBinding` (12) + `ConfirmationRecord` lifecycle (7) | `user_id` optional — production has no user identity yet |
| §2 "opaque token ≥128-bit, not a truncated uuid4" | `correlation.new_confirmation_id()`, uuid4 hex, 128 bits | reused, no second scheme |
| §3 state graph | `ConfirmationState` (7), `ConfirmationEvent` (6), `TRANSITIONS` (6 edges) | exact; no resting `CONFIRMED` |
| §3 "approval transitions directly into EXECUTING under a lock" | the edge exists in the table; its application is withheld until P5 | `ConfirmationDispatcherUnavailable` |
| §4 binding rule (5 fields + PENDING + fresh) | implemented, extended to all 12 fields | strictly stronger |
| §4 "CANCELLED or stays PENDING (design decision)" | **stays PENDING**, argued in `BINDING_CONTRACT.md` §3.1 | alternative recorded |
| §5 in-process store behind `ConfirmationStore` | implemented | append-only JSON deferred with the on-load sweep |
| §6 proposed TTLs | **not** encoded | no operator sign-off; see §4 below |
| §7 surfacing | not implemented | P7 API/UI |

## 3. Risk register → mitigation

| Risk | Mitigation in this task |
|---|---|
| R-03 confirmation replay | terminal states accept no event; a used id cannot be re-registered; 5 replay attempts measured, 0 succeed |
| R-04 stale confirmation | `expires_at` + expire-on-access + expire-on-approval; cannot be revived by rewinding the clock |
| R-05 bound to the wrong action | 128-bit opaque id, full twelve-field binding check, session check; two-pending-action test |
| R-07 canonicalization mismatch | `canonicalization_version` is a bound field; a version change invalidates the approval |
| R-10 lifecycle loss of pending state | **not** mitigated — deferred with persistence. A restart loses pending approvals rather than resurrecting them, which is the safe direction |
| R-16 races | process-local lock on every mutation; the limits of that claim are stated, not implied |

## 4. Deferred, with the reason

| Item | Why | Owner |
|---|---|---|
| persistence + on-load expiry sweep | plan §5 pairs them; task §71 defers both | a later unit, before P10 |
| per-class TTL values | plan §6 marks them "proposed"; 13B11I deferred TTL enforcement and D-01…D-10 contain no TTL; `config/permissions.yaml` does not exist | operator sign-off |
| `PENDING → EXECUTING` application | claiming execution ownership needs a dispatcher | P5 |
| `SUCCEEDED` / `FAILED` | only a `TrustedToolResult` may cause them | P5 |
| re-deriving canonical arguments at approval (plan §4 recommendation) | the canonicalizer is not called from this module by design; the version is bound instead | P7 pipeline composition |
| live confirmation UI/API mapping | contract §12.2 — the server decides how a user action becomes `confirm(id)` | P7 |
| `browser.open` / `browser.search` vs D-01 | carried forward from 13B11I, untouched here | operator, before live permission wiring |
| `lane` as an audit field | carried forward | P6 |
| redaction secret-key list | carried forward | audit phase |
| `TIMEOUT` provenance source | carried forward | P5/P6 |
| P6 classifier/router unsupported-verb reconciliation | carried forward from 13B11H | P6 |

## 5. Task prompt vs frozen plan — one divergence, resolved

The prompt describes a resting `CONFIRMED` state and a `CONFIRMED → EXECUTING` transition. The plan
drops the resting state deliberately. The prompt's own §13 resolves this — *"Use the EXACT state
vocabulary from `CONFIRMATION_STATE_PLAN.md`. Do not use this prompt to guess"* — so the plan wins
and no `CONFIRMED` member exists. The prompt's §16 requirement (approval ≠ executed) is met in a
stronger form: approval reaches **no** state in this phase.

No material conflict was found between contract v1 and the 13B11A plan set.
