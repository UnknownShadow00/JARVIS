# Trusted Result Model — Task 13B11K

**Status: FROZEN before the module was written.**

## 1. The frozen type is reused

`app/execution/types.py::TrustedToolResult`, unchanged, with the frozen
`app/execution/types.py::ToolResultStatus` — `SUCCESS`, `ERROR`, `CONFIRMATION_REQUIRED`,
`BLOCKED`, `TIMEOUT`. No competing result type and no competing status vocabulary.

Fields: `invocation_id`, `tool_name`, `action_type`, `status`, `facts`, `executed`, `executor`,
`started_at`, `finished_at`, `error_kind`, `error_message`, `audit_ref`.

## 2. Only the dispatcher constructs it

There are zero `TrustedToolResult(` constructions anywhere under `app/` at the start of this
task. After it there is exactly one module with any, `app/execution/dispatch.py`, asserted by
test. `provenance.py` already enforces the other half: *"only a `TrustedToolResult` from the
authorized dispatcher may create `TOOL_SUCCESS` or `TOOL_ERROR` provenance"*, by type, not by
shape.

No promotion helper exists. There is no `trust_model_result`, `from_model`,
`promote_proposal`, `from_mapping` or `from_dict` — asserted by an explicit absence test over
the module's public names and over its AST.

## 3. Binding

Every result is built from the invocation the dispatcher was given: `invocation_id`,
`tool_name` and `action_type` are copied from it, never from the executor. Contract §18.2
requires a trusted result to be bound to the invocation id, tool name, normalized arguments, the
dispatcher that ran it, a timestamp, a status, the returned data and an audit event; the record
carries the first seven directly and `audit_ref` for the last.

An `ExecutorOutcome` that names a different invocation is discarded (§32). A result from one
invocation can therefore never be attached to another.

## 4. `executed`

`executed` means **the executor was invoked**, not "the side effect happened". It is:

* `False` for every `BLOCKED` and `CONFIRMATION_REQUIRED` result — `TOOL_INVOCATION_CONTRACT.md`
  §3.3;
* `True` for `SUCCESS`, `ERROR` and `TIMEOUT`, because in all three the executor ran.

`TIMEOUT` with `executed = True` is not a claim that anything completed: `provenance.py` already
refuses to ground `TIMEOUT` as either success or failure, which is where the uncertainty is
enforced.

## 5. `facts`

`facts` is non-empty only on `SUCCESS`, and then contains exactly the keys the executor
returned — copied, frozen, nothing added. §18.4, the minimal-result principle: a `SUCCESS` with
empty facts is legal and means "it ran and returned nothing to report".

The dispatcher never infers a fact from the absence or presence of another field, never derives
installation state, filesystem state, health, persistence or downstream effect, and never
promotes an error message into a fact.

## 6. `error_kind`

Frozen vocabulary. Control-plane kinds: `invocation_inconsistent`,
`invocation_not_dispatchable`, `invocation_malformed`, `invocation_already_dispatched`,
`permission_denied`, `confirmation_absent`, `confirmation_binding_absent`,
`confirmation_authority_unavailable`, `confirmation_not_found`, `confirmation_not_pending`,
`confirmation_expired`, `confirmation_binding_mismatch`, `confirmation_claim_failed`.
Executor kinds: `executor_error` (default when an `ERROR` outcome names none),
`executor_exception`, `executor_contract_violation`. An executor's own `error_kind` is preserved
when it supplies one — §18.3, *"preserve useful returned detail"*.
