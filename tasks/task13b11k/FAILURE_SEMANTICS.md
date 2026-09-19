# Failure Semantics — Task 13B11K

**Status: FROZEN before the module was written.**

| Situation | Executor called | Status | `executed` | Confirmation record | Notes |
|---|---|---|---|---|---|
| executor returns `SUCCESS` | yes | `SUCCESS` | true | `SUCCEEDED` | facts are exactly the returned keys |
| executor returns `ERROR` | yes | `ERROR` | true | `FAILED` | its `error_kind`/`error_message` are preserved |
| executor returns `TIMEOUT` | yes | `TIMEOUT` | true | stays `EXECUTING` | never folded into `ERROR`; grounds no provenance |
| executor raises | yes | `ERROR` | true | `FAILED` | `executor_exception`; the exception text is not turned into a fact |
| executor returns a non-`ExecutorOutcome` | yes | `ERROR` | true | `FAILED` | `executor_contract_violation`; nothing returned is kept |
| executor reports `BLOCKED`/`CONFIRMATION_REQUIRED` | yes | `ERROR` | true | `FAILED` | an executor may not manufacture a control-plane verdict |
| executor names a different invocation | yes | `ERROR` | true | `FAILED` | outcome discarded |
| settlement raises after the executor ran | yes | unchanged | unchanged | stays `EXECUTING` | the trusted result is never lost or altered |

## No retry

Nothing in the dispatcher retries. `PRODUCTION_INTEGRATION_PLAN.md` §13: *"Retries are never
automatic for mutating actions. A `TIMEOUT` ends the turn with an explicit 'outcome unknown'
response."* One dispatch call invokes the executor at most once.

## No replay

An invocation id is recorded as claimed before the executor call and is never released,
whatever happens afterwards — success, error, timeout, exception or a raised settlement. A
second dispatch of the same invocation is `BLOCKED` / `invocation_already_dispatched` with the
executor untouched. A confirmation record can never return to `PENDING`.

## No partial execution

One `ToolInvocation` is one authorized action. `MULTI_ACTION_UNSUPPORTED` is refused at gate 2
and is never decomposed (INV-012, §8.1). There is no loop over actions anywhere in the module.
