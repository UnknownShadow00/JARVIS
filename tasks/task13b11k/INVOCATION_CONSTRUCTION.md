# Invocation Construction — Task 13B11K

**Status: FROZEN before the module was written.**

## 1. The frozen type is reused

`app/execution/types.py::ToolInvocation`, unchanged. No `DispatchInvocation`,
`ExecutableRequest` or `ToolCallRecord` is created. Its thirteen fields, verified from the
module rather than from a prompt:

`invocation_id`, `turn_id`, `session_id`, `action_type`, `tool_name`, `raw_arguments`,
`canonical_arguments`, `canonicalization_version`, `permission_class`, `permission_outcome`,
`policy_version`, `requested_at`, `confirmation_id`.

It is a frozen slots dataclass whose `__post_init__` already wraps both argument mappings in
`MappingProxyType`.

## 2. `build_invocation(...)`

A keyword-only builder in `dispatch.py`. It exists so the invariants that make an invocation an
*authority record* are checked in one place instead of at each construction site.

* mints `invocation_id` from the P1 family (`new_invocation_id`) — a uuid4 hex, opaque,
  non-semantic, carrying no request, target, tool or model text. No second id scheme (§43);
* takes `session_id` and `turn_id` from a `CorrelationContext`, so the invocation is joinable to
  the rest of the turn;
* takes the permission decision as its three settled values — `permission_outcome`,
  `permission_class`, `policy_version` — never as a computed judgement and never by importing
  the engine (the 13B11J precedent);
* requires `confirmation_id` when the outcome is `REQUIRE_CONFIRMATION` and forbids it
  otherwise (`TOOL_INVOCATION_CONTRACT.md` §1);
* refuses `NONE`, `UNKNOWN_ACTION` and `MULTI_ACTION_UNSUPPORTED`;
* refuses a `ModelDraft` or `ToolProposal` anywhere in the argument mappings, at every depth —
  the same funnel `confirmation.py` uses;
* copies both argument mappings by value so a caller's later mutation cannot reach the record,
  and keeps raw and canonical separate and both retained (INV-006);
* takes `requested_at` from the caller; it reads no clock.

Building an invocation authorizes nothing and executes nothing. A `DENY` invocation is
constructible on purpose: the dispatcher has to be able to refuse one and say why.
