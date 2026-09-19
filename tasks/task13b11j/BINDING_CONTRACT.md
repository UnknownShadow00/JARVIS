# Binding Contract — Task 13B11J

**Status: FROZEN BEFORE IMPLEMENTATION.**

Contract §12.3 (NORMATIVE):

> Confirmation state **MUST** carry enough identity to bind the approval to: action type; target;
> arguments; and the requesting user/session. Where implemented, it **MUST** also carry expiry or
> freshness.

`agent-execution-contract.yaml`: `binding_fields: [action_type, target, arguments,
requesting_user_or_session]`.

## 1. The twelve binding fields

`ConfirmationBinding` is a frozen dataclass. Every field is write-once at construction and is
compared for **exact equality** at approval. Each row traces to a normative source.

| # | Field | Type | Source |
|---|---|---|---|
| 1 | `confirmation_id` | `ConfirmationId` (opaque, 128-bit) | plan §2 row 1; §12.3 identity |
| 2 | `session_id` | `SessionId` | plan §2 row 2; §12.3 "requesting user/session" |
| 3 | `user_id` | `str \| None` | plan §2 row 2 writes "`session_id` / `user_id`"; production has no user identity today, so it is optional and `None`, but it is part of the binding whenever it is present |
| 4 | `action_type` | `PrimaryAction` | plan §2 row 3; §12.3 "action type" |
| 5 | `capability` | `str` | the P4 permission-table key — the action *subtype* (`files.move` vs `files.read`). Five routed actions cannot tell them apart, and a binding that cannot tell them apart is not a binding. |
| 6 | `tool_name` | `str` | plan §2 row 7 "the dispatcher entry point" |
| 7 | `target` | `str \| None` | plan §2 row 4 "normalized target"; §12.3 "target" |
| 8 | `canonical_arguments` | frozen mapping | plan §2 row 5 "exactly what would run"; §12.3 "arguments" |
| 9 | `raw_arguments` | frozen mapping | plan §2 row 6 "audit + mismatch detection"; contract §9.1 / INV-006 |
| 10 | `permission_class` | `PermissionClass` | plan §2 row 8 "which rule required confirmation" |
| 11 | `policy_version` | `str` | plan §2 row 8 |
| 12 | `canonicalization_version` | `str` | `RISK_REGISTER.md` R-07 mitigation: *"store `canonicalization_version`; compare at approval"* |

### 1.1 Non-binding fields of the record

Carried by `ConfirmationRecord`, **not** compared at approval because they are lifecycle or
linkage, not identity of the action:

| Field | Type | Source |
|---|---|---|
| `state` | `ConfirmationState` | plan §2 row 10 |
| `created_at`, `expires_at` | aware UTC `datetime` | plan §2 row 9; §12.3 freshness |
| `resolved_at` | aware UTC `datetime \| None` | when a terminal state was reached; `None` while `PENDING` |
| `audit_ref` | `CorrelationContext` | plan §2 row 12 "correlation id — joins the whole chain" |
| `provenance_ref` | `str \| None` | plan §2 row 11 "turn / event id — links the request that produced it" |
| `invocation_id` | `InvocationId \| None` | plan §2 row 13 "set on execution (idempotency)". **Always `None` in this phase**; only the P5 dispatcher may set it. |

## 2. The approval rule

`CONFIRMATION_STATE_PLAN.md` §4:

> Approval applies to **one** pending record and only if all of the following match at approval
> time: `confirmation_id`, `session_id`, `action_type`, `target`, `canonical_arguments`, and
> `state == PENDING`, and `now < expires_at`.

Implemented as, in this order:

1. the record exists **and** belongs to `session_id` — otherwise `ConfirmationNotFound`;
2. `state == PENDING` — otherwise `InvalidConfirmationTransition`;
3. `now < expires_at` — otherwise the record moves to `EXPIRED` and `ConfirmationExpired` is
   raised (see `EXPIRY_AND_FRESHNESS.md`);
4. the supplied `ConfirmationBinding` equals the stored one, **all twelve fields** — otherwise
   `ConfirmationBindingMismatch`;
5. only then, `ConfirmationDispatcherUnavailable`.

The plan names five binding fields as the minimum; all twelve are compared. A stricter check can
never authorize something the plan's check would refuse, and the task's own §34 requires that a
changed capability subtype, permission class or policy version invalidate the approval — which the
five-field list alone would not catch.

## 3. Two design decisions the plan left open, resolved here

`CONFIRMATION_STATE_PLAN.md` §4 says: *"Any mismatch → no execution, record moves to `CANCELLED` or
stays `PENDING` (design decision at implementation time)"*. Both are resolved and both are tested.

### 3.1 Binding mismatch leaves the record `PENDING`

A mismatched approval attempt is either an attacker who already knows the id, or a buggy client.
If a mismatch cancelled the record, anyone holding the id could **destroy a legitimate pending
approval** by sending one wrong argument — a denial of service on the real user's decision. Nothing
executes either way, so the safer choice is the one that preserves the honest path: the record
stays `PENDING` and the attempt raises. The alternative is recorded here and is a one-line change
if the operator prefers it.

### 3.2 A session mismatch is reported as "not found"

Session A asking about session B's record gets `ConfirmationNotFound`, not a distinguishable
"wrong session" error. A distinguishable error is an oracle: it confirms that a given opaque id
exists. Fail-closed and non-leaking.

## 4. Argument change invalidates approval

A changed target, canonical argument, capability, permission class, policy version or
canonicalization version produces a binding that is not equal to the stored one, so approval fails
at step 4. There is no API that rewrites a stored binding — the dataclass is frozen, the store
never mutates binding fields, and a changed action requires a **new record with a new id**.

Deep equality is exact: nested mappings are frozen to `MappingProxyType` and nested sequences to
tuples at construction, on both the stored binding and the supplied one, so comparison is by value
and is not affected by whether the caller passed a `list` or a `tuple`.

## 5. Model non-authority in the binding

`ModelDraft` and `ToolProposal` are rejected as argument values, including nested inside
`raw_arguments` and `canonical_arguments`. No binding field can hold model prose, model confidence
or a model-asserted confirmation. `permission_class` and `policy_version` are copied from the P4
`PermissionDecision`, never accepted from the caller, so no caller can declare a class the policy
engine did not decide.
