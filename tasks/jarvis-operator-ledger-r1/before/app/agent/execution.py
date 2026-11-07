"""Opt-in offline execution. Only the sealed, in-process synthetic adapter exists.

Actor is a trusted server namespace. This module does not grant HTTP identity,
host isolation, or permission to run external effects. No real adapter can be
registered here. Audit, decisions, evidence and publication use Authority's
fenced transactions; publication is never a public API operation.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import threading
import time
import uuid

from app.agent.authority import AuthorityError, canonical, identifier, instant, text


CAPABILITIES = frozenset({"synthetic.echo", "synthetic.sha256", "synthetic.fail"})
TERMINAL = frozenset({"simulated_completed", "simulated_failed", "denied", "cancelled", "timed_out", "unknown"})


def phase_id(operation_id, phase):
    """Stable internal receipt key, never a replacement logical operation ID."""
    return str(uuid.uuid5(uuid.UUID(identifier(operation_id)), "offline-execution:" + phase))


def validate_spec(capability, payload, expires_at, timeout_seconds):
    text(capability, 128)
    if type(payload) is not dict or set(payload) != {"value"}:
        raise AuthorityError("invalid_execution_payload")
    text(payload["value"], 8192)
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 60:
        raise AuthorityError("invalid_execution_timeout")
    return dict(capability=capability, payload={"value": payload["value"]},
                expires_at=instant(expires_at), timeout_seconds=timeout_seconds)


@dataclass(frozen=True)
class SimulatedPolicy:
    scope: str
    capabilities: frozenset[str] = frozenset({"synthetic.echo", "synthetic.sha256"})
    revision: str = "offline-v1"

    def __post_init__(self):
        text(self.scope, 128)
        text(self.revision, 128)
        if type(self.capabilities) is not frozenset or not self.capabilities <= CAPABILITIES:
            raise AuthorityError("invalid_simulated_policy")

    def permits(self, scope, capability):
        return scope == self.scope and capability in self.capabilities


class DisabledExecutor:
    def execute(self, operation_id, spec):
        raise AuthorityError("real_execution_disabled")


class SyntheticExecutor:
    """Bounded pure computation; never imports tools or interprets goals."""
    capabilities = CAPABILITIES

    def execute(self, operation_id, spec):
        value = spec["payload"]["value"]
        capability = spec["capability"]
        if capability not in self.capabilities:
            raise AuthorityError("capability_unavailable")
        output = hashlib.sha256(value.encode()).hexdigest() if capability == "synthetic.sha256" else value
        return {"operation_id": operation_id, "capability": capability,
                "status": "simulated_failed" if capability == "synthetic.fail" else "simulated_completed",
                "output": None if capability == "synthetic.fail" else output,
                "error": "synthetic_failure" if capability == "synthetic.fail" else None}


class ExecutorRegistry:
    """No arbitrary plugins/callbacks: real executor registration is prohibited."""
    def __init__(self, *, enabled=False):
        self._executor = None
        self._enabled = enabled is True

    def register(self, executor):
        if not self._enabled:
            raise AuthorityError("execution_disabled")
        if type(executor) is not SyntheticExecutor:
            raise AuthorityError("real_execution_disabled")
        if self._executor is not None:
            raise AuthorityError("executor_already_registered")
        self._executor = executor

    def resolve(self, capability):
        if not self._enabled or self._executor is None:
            raise AuthorityError("execution_disabled")
        if capability not in CAPABILITIES:
            raise AuthorityError("capability_unavailable")
        return self._executor


class ExecutionPipeline:
    def __init__(self, authority, policy, *, enabled=False, max_pending=128, clock=None, fault_hook=None):
        if enabled is not True or not authority.allow_simulation:
            raise AuthorityError("execution_disabled")
        if type(policy) is not SimulatedPolicy:
            raise AuthorityError("invalid_simulated_policy")
        if type(max_pending) is not int or not 1 <= max_pending <= 1000:
            raise AuthorityError("invalid_pending_limit")
        self.authority, self.policy = authority, policy
        self.registry = ExecutorRegistry(enabled=True)
        self.registry.register(SyntheticExecutor())
        self.max_pending = max_pending
        self._clock = clock or (lambda: datetime.now(UTC))
        self._fault = fault_hook or (lambda stage: None)
        self._dispatch_mutex = threading.Lock()

    def schedule_template(self, actor, capability, payload, timeout_seconds=10, expires_after_seconds=60):
        """Authorize an explicitly synthetic recurring intent, rechecked at dispatch."""
        if type(expires_after_seconds) is not int or not 1 <= expires_after_seconds <= 3600:
            raise AuthorityError("invalid_execution_expiry")
        # Reuse strict payload/capability/timeout checks; expiry is occurrence-relative.
        spec = validate_spec(capability, payload, self._clock().isoformat(), timeout_seconds)
        del spec["expires_at"]
        scope = self.authority._scope(actor)
        if not self.policy.permits(scope, capability):
            raise AuthorityError("policy_denied")
        return dict(spec, expires_after_seconds=expires_after_seconds,
                    authorization=dict(allowed=True, policy_revision=self.policy.revision,
                                       capability=capability, scope=scope, at=self._clock().isoformat()))

    def submit(self, actor, request_id, goal, capability, payload, expires_at, timeout_seconds=10):
        a = self.authority
        identifier(request_id)
        if uuid.UUID(request_id).version != 4:
            raise AuthorityError("invalid_public_request_identifier")
        text(goal)
        spec = validate_spec(capability, payload, expires_at, timeout_seconds)
        def effect(scope):
            now = self._clock()
            expiry = datetime.fromisoformat(spec["expires_at"])
            if expiry <= now or expiry > now + timedelta(hours=24):
                raise AuthorityError("stale_execution_request")
            count = a._conn.execute("SELECT COUNT(*) FROM outbox WHERE state IN ('held','execution_claimed','unknown')").fetchone()[0]
            if count >= self.max_pending:
                raise AuthorityError("queue_capacity_exceeded")
            allowed = self.policy.permits(scope, capability) and capability in CAPABILITIES
            task = a._new_task(scope, request_id, goal)
            decision = dict(allowed=allowed, policy_revision=self.policy.revision,
                            capability=capability, scope=scope, at=now.isoformat())
            task["execution"] = dict(spec, operation_id=request_id, authorization=decision,
                                     receipt_ids={phase: phase_id(request_id, phase) for phase in ("claim", "dispatch", "record", "publish", "unknown")})
            if not allowed:
                task.update(status="denied", error="policy_denied")
                a._conn.execute("UPDATE outbox SET state='denied' WHERE task_id=?", (request_id,))
            a._put("task", request_id, scope, task)
            return task
        return a._mutate(actor, request_id, "execution_submit", dict(goal=goal, **spec), effect)

    def _state(self, task, state, *, result=None, error=None):
        a = self.authority
        task.update(status=state, result=result, error=error)
        a._put("task", task["task_id"], task["scope"], task)
        a._conn.execute("UPDATE outbox SET state=? WHERE task_id=?", (state, task["task_id"]))
        return task

    def _claim(self, actor, operation_id):
        a = self.authority
        def effect(scope):
            task = a._get("task", operation_id, scope)
            spec = task.get("execution")
            row = a._conn.execute("SELECT state FROM outbox WHERE task_id=?", (operation_id,)).fetchone()
            if not spec or row[0] != "held" or task["cancel_requested"]:
                raise AuthorityError("not_claimable")
            decision = spec.get("authorization")
            if type(decision) is not dict or spec.get("operation_id") != operation_id or decision.get("scope") != scope or decision.get("capability") != spec.get("capability") or decision.get("allowed") is not True:
                return self._state(task, "denied", error="inconsistent_authorization")
            now = self._clock()
            if datetime.fromisoformat(spec["expires_at"]) <= now:
                return self._state(task, "timed_out", error="expired_before_dispatch")
            if not self.policy.permits(scope, spec["capability"]):
                return self._state(task, "denied", error="policy_denied_at_dispatch")
            self.registry.resolve(spec["capability"])
            task["execution"].update(dispatch_policy_revision=self.policy.revision,
                                     deadline=min(datetime.fromisoformat(spec["expires_at"]), now + timedelta(seconds=spec["timeout_seconds"])).isoformat())
            task["status"] = "executing_synthetic"
            a._put("task", operation_id, scope, task)
            a._conn.execute("UPDATE outbox SET state='execution_claimed',claim_id=?,generation=? WHERE task_id=?", (operation_id, a.generation, operation_id))
            return task
        return a._mutate(actor, phase_id(operation_id, "claim"), "execution_claim", {"operation_id": operation_id}, effect)

    def _claimed(self, scope, operation_id, generation):
        a = self.authority
        task = a._get("task", operation_id, scope)
        row = a._conn.execute("SELECT * FROM outbox WHERE task_id=?", (operation_id,)).fetchone()
        if row["state"] != "execution_claimed" or row["claim_id"] != operation_id or row["generation"] != generation or generation != a.generation:
            raise AuthorityError("stale_claim")
        return task

    def _pre_dispatch(self, actor, operation_id, generation):
        """Final fenced cancellation/policy/deadline check before pure computation."""
        a = self.authority
        def effect(scope):
            task = self._claimed(scope, operation_id, generation)
            spec = task["execution"]
            if task["cancel_requested"]:
                return self._state(task, "cancelled")
            if self._clock() >= datetime.fromisoformat(spec["deadline"]):
                return self._state(task, "timed_out", error="expired_before_dispatch")
            if not self.policy.permits(scope, spec["capability"]):
                return self._state(task, "denied", error="policy_denied_at_dispatch")
            return task
        return a._mutate(actor, phase_id(operation_id, "dispatch"), "execution_dispatch", {"operation_id": operation_id, "generation": generation}, effect)

    def _record(self, actor, operation_id, generation, response):
        a = self.authority
        def effect(scope):
            task = self._claimed(scope, operation_id, generation)
            # Recompute bounded pure output to reject forged IDs, fields, types,
            # capabilities and values. Never evaluate response-provided code.
            expected = SyntheticExecutor().execute(operation_id, task["execution"])
            if canonical(response) != canonical(expected):
                raise AuthorityError("untrusted_executor_response")
            evidence = dict(response=response, generation=generation, operation_id=operation_id,
                            at=self._clock().isoformat(), source="synthetic_pure_computation")
            a._create("execution_evidence", operation_id, scope, evidence)
            return evidence
        return a._mutate(actor, phase_id(operation_id, "record"), "execution_record", {"operation_id": operation_id, "generation": generation, "response": response}, effect)

    def _publish(self, actor, operation_id):
        a = self.authority
        def effect(scope):
            task = a._get("task", operation_id, scope)
            evidence = a._get("execution_evidence", operation_id, scope)
            row = a._conn.execute("SELECT state,claim_id,generation FROM outbox WHERE task_id=?", (operation_id,)).fetchone()
            if row["state"] not in {"execution_claimed", "unknown"} or row["claim_id"] != operation_id or row["generation"] != evidence["generation"]:
                raise AuthorityError("invalid_execution_provenance")
            response = evidence["response"]
            return self._state(task, response["status"], result=response, error=response["error"])
        return a._mutate(actor, phase_id(operation_id, "publish"), "execution_publish", {"operation_id": operation_id}, effect)

    def _unknown(self, actor, operation_id, generation, reason):
        a = self.authority
        def effect(scope):
            task = self._claimed(scope, operation_id, generation)
            return self._state(task, "unknown", error=reason)
        return a._mutate(actor, phase_id(operation_id, "unknown"), "execution_unknown", {"operation_id": operation_id, "generation": generation, "reason": reason}, effect)

    def run_once(self, actor):
        """Dispatch at most one admitted task, never automatically retry a claim."""
        if not self._dispatch_mutex.acquire(blocking=False):
            raise AuthorityError("dispatcher_busy")
        try:
            task = next(iter(self.authority.execution_tasks(actor, "held")), None)
            if task is None:
                return None
            operation_id = task["task_id"]
            claim = self._claim(actor, operation_id)
            if claim["replayed"]:
                # A claimed request can never be replayed into adapter invocation.
                raise AuthorityError("claim_reconciliation_required")
            if claim["result"]["status"] in TERMINAL:
                return claim
            generation = claim["owner_generation"]
            self._fault("after_claim")
            dispatch = self._pre_dispatch(actor, operation_id, generation)
            if dispatch["result"]["status"] in TERMINAL:
                return dispatch
            self._fault("before_execute")
            dispatch_started = time.monotonic()
            try:
                executor = self.registry.resolve(task["execution"]["capability"])
                response = executor.execute(operation_id, task["execution"])
                self._fault("after_execute")
            except Exception:
                return self._unknown(actor, operation_id, generation, "dispatch_outcome_unestablished")
            if time.monotonic() - dispatch_started >= task["execution"]["timeout_seconds"] or self._clock() >= datetime.fromisoformat(dispatch["result"]["execution"]["deadline"]):
                return self._unknown(actor, operation_id, generation, "dispatch_timeout_outcome_unestablished")
            try:
                self._record(actor, operation_id, generation, response)
            except AuthorityError as exc:
                if exc.code in {"untrusted_executor_response", "invalid_payload", "payload_too_large"}:
                    return self._unknown(actor, operation_id, generation, "untrusted_executor_response")
                raise
            self._fault("after_record")
            receipt = self._publish(actor, operation_id)
            self._fault("after_publish")
            return receipt
        finally:
            self._dispatch_mutex.release()

    def reconcile(self, actor):
        """Publish existing evidence only. UNKNOWN without evidence stays UNKNOWN."""
        published = []
        for task in self.authority.execution_tasks(actor, "unknown"):
            with self.authority._mutex:
                self.authority._fence()
                try:
                    self.authority._get("execution_evidence", task["task_id"], self.authority._scope(actor))
                except AuthorityError as exc:
                    if exc.code == "not_found":
                        continue
                    raise
            published.append(self._publish(actor, task["task_id"]))
        return published


class ExecutionWorker:
    """Single bounded offline worker; a storage/audit error stops admission to it."""
    def __init__(self, pipeline, actor):
        self.pipeline, self.actor = pipeline, actor
        self._task = None
        self.failure = None

    async def start(self):
        if self._task is not None:
            raise AuthorityError("worker_already_started")
        self.pipeline.authority.readiness()
        self.pipeline.reconcile(self.actor)
        self.failure = None
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        try:
            while True:
                self.pipeline.run_once(self.actor)
                await asyncio.sleep(0.02)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.failure = "execution_worker_reconcile_required"

    async def stop(self):
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def readiness(self):
        return {"synthetic_execution_enabled": True, "execution_worker_ready": self._task is not None and not self._task.done() and self.failure is None,
                "execution_worker_failure": self.failure, "real_execution_enabled": False}
