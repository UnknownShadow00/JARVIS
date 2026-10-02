# RESULT REPLAY

Mode C. Admits one `ToolInvocation` and the one `TrustedToolResult` the P5 dispatcher
produced for it, so the pipeline can resume **after** execution and build the response the
result supports. No execution occurs, and none can.

## What may be admitted

`turn.result` must satisfy `type(turn.result) is TrustedToolResult` and `turn.invocation`
must satisfy `type(turn.invocation) is ToolInvocation`. Exact type identity, not
`isinstance`, so a subclass, a `Mapping`, a namespace object, a `ModelDraft`, a
`ToolProposal`, a dict with the same keys or a caller-created success boolean is refused by
type rather than coerced. There is no `from_dict`, no generic promotion and no
model-payload path into either field.

## Authenticity limit (recorded, not papered over)

`TrustedToolResult` is an ordinary constructible dataclass, and from phase P5 only the
dispatcher is *permitted* to construct it — a contract rule, not an enforced one. P7 v1
cannot authenticate a result's origin. What it can and does enforce is: exact type
identity; exact invocation linkage (C-01…C-08 below); agreement between the replayed
invocation's settled authority fields and the authority the frozen engines actually decide
for this turn, so a forged `ALLOW` or `permission_class` is rejected; and the existing P6
contradiction checks, which refuse an internally impossible result. The remaining trust
rests with the caller — in P7 v1 always a fixture or a test-owned P4/P5 setup, never a live
provider. V1 already states that type identity alone is not authenticated origin; this
contract adds no claim beyond it, and the gap is recorded as F-P7R1-01.

## Admission preconditions (S01)

- **C-00 shape.** `invocation` and `result` are present together, and `confirmation` is
  absent (ADMISSION_MODES.md).
- **C-00a dispatchable action.** `turn.invocation.action_type not in
  dispatch.NON_DISPATCHABLE_ACTIONS`. P7 v1 does not replay a
  `BLOCKED`/`invocation_not_dispatchable` refusal: such a result is genuine, but the frozen
  guard order routes `NONE`/`UNKNOWN_ACTION`/`MULTI_ACTION_UNSUPPORTED` to an early P6
  terminal before S06, and attaching a result there would need a P6 priority judgement no
  operator has signed. Deliberate v1 exclusion, recorded as F-P7R1-02, not a silent drop.
- **C-00b turn/session association.** `turn.invocation.turn_id ==
  turn.correlation.turn_id` and `turn.invocation.session_id ==
  turn.correlation.session_id`. This is S01's own "exact same session" rule, so it is
  checked at S01 rather than deferred.

Failure of C-00/C-00a/C-00b → `PipelineStop(stage=S01_INPUT, reason=invalid_input,
executed=False, result=None)`.

## Association guards (all at S09; order is normative)

1. **C-01 result↔invocation identity.** `result.invocation_id == invocation.invocation_id`,
   and `is_well_formed_id` holds for it. A result from invocation A can never satisfy
   invocation B.
2. **C-02 result↔invocation description.** `result.tool_name == invocation.tool_name` and
   `result.action_type == invocation.action_type`. A genuine dispatcher result copies both
   from the invocation, so this only ever rejects a hand-built one.
3. **C-03 correlation child.** If `turn.correlation.invocation_id` is present it equals
   `invocation.invocation_id`.
4. **C-04 route agreement.** `invocation.action_type == route.primary_action` from the
   actual S03 result, the route is a single resolved supported action, and
   `route.target_resolved is not False`.
5. **C-05 expected-binding agreement.** `invocation.tool_name == turn.expected.tool_name`
   and `invocation.canonical_arguments == turn.expected.canonical_arguments` by exact
   value and scalar type. The authoritative canonical form is the caller's expected
   projection; the invocation may not substitute its own.
6. **C-06 version agreement.** `invocation.canonicalization_version ==
   canonicalize.CANONICALIZATION_VERSION == turn.expected.version` and
   `invocation.policy_version == permissions.PERMISSION_POLICY_VERSION`. A replay recorded
   under superseded rules is refused, not re-interpreted.
7. **C-07 authority agreement.** `invocation.permission_outcome` equals the outcome the
   actual S07 `permissions.decide` call returns for this turn, and
   `invocation.permission_class` equals that decision's `permission_class`. This is the
   check that stops a replay carrying a forged permissive outcome: the policy is
   re-decided from JARVIS-owned inputs every run and the replay must agree with it.
8. **C-08 historical support linkage.** If `supporting_result` or `supporting_invocation`
   is present, both are present, `supporting_result.invocation_id ==
   supporting_invocation.invocation_id`, and that id differs from
   `invocation.invocation_id`. The historical role stays separate from the current one, so
   an unrelated invocation can never be attached to a current response.

Failure of C-01…C-08 → `PipelineStop(stage=S09_RESULT, reason=result_invalid,
executed=False, result=None)`. The admitted result is **not** retained in that stop: an
association failure means the object was never established as this turn's result, and
retaining it would be the attachment the guards just refused.

## Status

The actual `ToolResultStatus` inventory is used unchanged: `SUCCESS`, `ERROR`,
`CONFIRMATION_REQUIRED`, `BLOCKED`, `TIMEOUT`. No status is invented, renamed or merged.
`TIMEOUT` stays distinct from `ERROR`.

S09 deliberately does **not** re-check `status`/`executed`/`facts` consistency. That rule
is already owned by P6's `_check_result_shape` (`REFUSAL_CLAIMS_EXECUTION`,
`EXECUTION_STATUS_WITHOUT_EXECUTION`), and duplicating it in P7 would copy a frozen
component's logic. An inconsistent replayed result therefore surfaces as
`PipelineStop(stage=S11_OBLIGATION, reason=obligation_failed,
component_reason=<the existing P6 contradiction code>)`, with the owner's code preserved.

Per-status disposition, all with zero executor calls:

| Status | `executed` | Disposition |
|---|---|---|
| `SUCCESS` | `True` | S10 → S11 → `REPORT_TOOL_SUCCESS` / `tool_success`, values only from `result.facts` |
| `ERROR` | `True` | `REPORT_TOOL_ERROR` / `trusted_tool_error` |
| `TIMEOUT` | `True` | `REPORT_TOOL_ERROR` / `trusted_tool_timeout` (D-P6-02). Outcome unknown; no success and no failure is claimed, no timeout provenance is written, no re-dispatch occurs, and the separate confirmation `EXECUTING` lifecycle issue stays deferred — P7 admits no confirmation record in mode C and settles nothing. |
| `CONFIRMATION_REQUIRED` | `False` | `REQUEST_CONFIRMATION` via the existing `P6-01a` rule. `executed=False` is preserved and is never converted into a tool failure. The dispatcher's own refusal code (`confirmation_absent`, `confirmation_binding_absent`, `confirmation_authority_unavailable`, or any `CLAIM_REFUSAL_KINDS` member) survives in `result.error_kind` and is not renewed, re-asked or repaired. |
| `BLOCKED` | `False` | `REPORT_CAPABILITY_UNAVAILABLE` / `dispatch_blocked` where that existing rule wins. `executed=False` preserved; not a tool failure; no new execution. |

## Replay must not re-execute

When a result is admitted the pipeline resumes after execution. It must not, and in P7 v1
structurally cannot:

- enter `TrustedDispatcher` — no dispatcher is constructed, imported for use, or reachable
  from `RecordedTurn`;
- call an executor — `RecordedTurn` holds no callable;
- claim a confirmation again — `claim_for_dispatch` is never called, and mode C admits no
  confirmation record to claim;
- create a second invocation — `invocation` is admitted, never minted; P7 calls no
  `new_invocation_id` and no `build_invocation`;
- construct a `TrustedToolResult` — P7 is not the dispatcher and never constructs one, in
  any branch, including every failure branch.

Downstream direction is exactly the frozen stage structure:
`TrustedToolResult` → S10 provenance → S11 obligation → S12 response.

## `confirmation_claimed` in mode C

`ObligationState.confirmation_claimed` is derived, never admitted:

```
confirmation_claimed = (
    turn.result.executed is True
    and turn.invocation.permission_outcome is PermissionOutcome.REQUIRE_CONFIRMATION
)
```

This is forced by the frozen production code, not chosen. `TrustedDispatcher.dispatch`
reaches an executor only after gate 6, and gate 6 is the step that performs the claim for a
`REQUIRE_CONFIRMATION` invocation; every path that returns before gate 6 returns
`executed=False`. So `executed=True` with `REQUIRE_CONFIRMATION` implies a completed claim,
and nothing else does. The two frozen P6 contradiction checks confirm the mapping is the
only non-contradictory one: `_check_execution` rejects `executed=True` with
`REQUIRE_CONFIRMATION` and `confirmation_claimed=False`
(`CONFIRMATION_EXECUTED_WITHOUT_AUTHORITY`), and `_check_settled_state` rejects
`confirmation_claimed=True` with any other outcome (`APPROVAL_WITHOUT_REQUIREMENT`).

Note what is *not* used: `invocation.confirmation_id is not None` is **not** sufficient.
Gate 5 can return `CONFIRMATION_REQUIRED` with `confirmation_absent`,
`confirmation_binding_absent` or `confirmation_authority_unavailable` while the invocation
carries a confirmation id and no claim ever happened. Deriving the flag from the id alone
would manufacture an approval; deriving it from `executed` cannot.
