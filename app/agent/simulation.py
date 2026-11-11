"""Explicitly enabled synthetic SQLite effects only. No external execution hook."""
import uuid

from app.agent.authority import AuthorityError, identifier


class Simulator:
    def __init__(self, authority):
        if not authority.allow_simulation:
            raise AuthorityError("simulation_disabled")
        self.authority = authority

    def _task(self, task_id, scope):
        task = self.authority._get("task", task_id, scope)
        # The effect table proves only this legacy SQLite protocol. It cannot
        # authorize or reconcile an ExecutionPipeline operation.
        if "execution" in task:
            raise AuthorityError("execution_protocol_mismatch")
        return task

    def claim(self, actor, request_id, task_id):
        a = self.authority
        identifier(task_id)
        def effect(scope):
            task = self._task(task_id, scope)
            row = a._conn.execute("SELECT state FROM outbox WHERE task_id=?", (task_id,)).fetchone()
            if row[0] != "held" or task["cancel_requested"]:
                raise AuthorityError("not_claimable")
            claim = str(uuid.uuid4())
            task["status"] = "simulating"
            a._put("task", task_id, scope, task)
            a._conn.execute("UPDATE outbox SET state='simulating',claim_id=?,generation=? WHERE task_id=?", (claim, a.generation, task_id))
            return {"task_id": task_id, "claim_id": claim, "generation": a.generation}
        return a._mutate(actor, request_id, "simulation_claim", {"task_id": task_id}, effect)

    def apply(self, actor, request_id, task_id, claim_id, generation):
        a = self.authority
        def effect(scope):
            task = self._task(task_id, scope)
            row = a._conn.execute("SELECT * FROM outbox WHERE task_id=?", (task_id,)).fetchone()
            if row["state"] != "simulating" or row["claim_id"] != claim_id or row["generation"] != generation or generation != a.generation:
                raise AuthorityError("stale_claim")
            if a._conn.execute("SELECT 1 FROM simulation_effects WHERE task_id=?", (task_id,)).fetchone():
                raise AuthorityError("effect_already_applied")
            if task["cancel_requested"]:
                task["status"] = "cancelled"
                a._conn.execute("UPDATE outbox SET state='cancelled' WHERE task_id=?", (task_id,))
                a._put("task", task_id, scope, task)
                return {"effect_applied": False}
            a._conn.execute("INSERT INTO simulation_effects VALUES(?,?)", (task_id, claim_id))
            return {"effect_applied": True}
        return a._mutate(actor, request_id, "simulation_apply", dict(task_id=task_id, claim_id=claim_id, generation=generation), effect)

    def acknowledge(self, actor, request_id, task_id, claim_id, generation):
        a = self.authority
        def effect(scope):
            task = self._task(task_id, scope)
            row = a._conn.execute("SELECT * FROM outbox WHERE task_id=?", (task_id,)).fetchone()
            if row["state"] != "simulating" or row["claim_id"] != claim_id or row["generation"] != generation or generation != a.generation:
                raise AuthorityError("stale_claim")
            applied = a._conn.execute("SELECT 1 FROM simulation_effects WHERE task_id=?", (task_id,)).fetchone() is not None
            state = "simulated_completed" if applied else "cancelled" if task["cancel_requested"] else "unknown"
            task["status"] = state
            a._put("task", task_id, scope, task)
            a._conn.execute("UPDATE outbox SET state=? WHERE task_id=?", (state, task_id))
            return {"status": state, "cancel_requested": task["cancel_requested"]}
        return a._mutate(actor, request_id, "simulation_ack", dict(task_id=task_id, claim_id=claim_id, generation=generation), effect)

    def reconcile(self, actor, request_id, task_id):
        a = self.authority
        def effect(scope):
            task = self._task(task_id, scope)
            row = a._conn.execute("SELECT state,claim_id FROM outbox WHERE task_id=?", (task_id,)).fetchone()
            if row["state"] != "unknown" or row["claim_id"] is None:
                raise AuthorityError("not_unknown")
            # SQLite is the complete synthetic effect system. This inference
            # cannot be transferred to real tools/providers/VM operations.
            applied = a._conn.execute("SELECT 1 FROM simulation_effects WHERE task_id=?", (task_id,)).fetchone() is not None
            state = "simulated_completed" if applied else "cancelled"
            task["status"] = state
            a._put("task", task_id, scope, task)
            a._conn.execute("UPDATE outbox SET state=? WHERE task_id=?", (state, task_id))
            return {"status": state, "evidence": "synthetic_sqlite_effect_table", "resubmitted": False}
        return a._mutate(actor, request_id, "simulation_reconcile", {"task_id": task_id}, effect)
