# Executor Seam — Task 13B11K

**Status: FROZEN before the module was written.**

## 1. Shape

```python
class ToolExecutor(Protocol):
    def __call__(self, invocation: ToolInvocation) -> ExecutorOutcome: ...
```

A structural protocol over a single call. No service locator, no registry lookup, no import of
any tool module, no name-to-callable table. `TARGET_COMPONENT_MAP.md` §1: the dispatcher *"must
never be bypassable by importing a tool module."* The only way to reach an effect is an object
the constructor was handed.

## 2. No default — fail closed

`TrustedDispatcher(executor=..., clock=...)` requires both. There is no default executor, no
`None` fallback and no lazy import. Omitting the executor raises `DispatchError` at
construction. `PRODUCTION_INTEGRATION_PLAN.md` §19: *"Dispatcher unavailable → no execution."*

The clock is injected for the same reason `confirmation.py` injects `now`: the started/finished
timestamps on a trusted result must be reproducible in a test, and the module must read no
ambient state.

## 3. `ExecutorOutcome` — untrusted until wrapped

```python
@dataclass(frozen=True, slots=True)
class ExecutorOutcome:
    status: ToolResultStatus
    facts: Mapping[str, Any] = {}
    error_kind: str | None = None
    error_message: str | None = None
    invocation_id: str | None = None
```

`status` reuses the P0 `ToolResultStatus`; no second status vocabulary is introduced. An
executor may only report one of `EXECUTOR_REPORTABLE_STATUSES` = {`SUCCESS`, `ERROR`,
`TIMEOUT`}. `BLOCKED` and `CONFIRMATION_REQUIRED` are control-plane verdicts about authority,
not observations about a tool, so an executor claiming either is a contract violation — this is
the seam that stops an executor from manufacturing a refusal, or a refusal-shaped success.

`invocation_id` is optional and exists only so a mismatch is detectable: if it is present and
differs from the invocation being dispatched, the outcome is discarded (§32). The executor
cannot name a different invocation and have the result attached to it.

Anything that is not an `ExecutorOutcome` — a dict, a look-alike object, a `ModelDraft`, a
`ToolProposal`, `None` — is a contract violation, not a result.

## 4. Contract violations

A contract violation produces `ERROR` / `executor_contract_violation` / `executed = True` /
empty facts. `executed` is true because the executor was in fact invoked and may have had an
effect; claiming otherwise would be the fabrication this whole layer exists to prevent. No
facts survive, because nothing trustworthy was returned.

## 5. What the dispatcher owns, not the executor

Invocation association, status mapping, `executed`, timestamps, the executor name, the audit
reference, and the identity of the trusted result. The executor contributes only `facts` on a
`SUCCESS`, and `error_kind` / `error_message` on an `ERROR`.
