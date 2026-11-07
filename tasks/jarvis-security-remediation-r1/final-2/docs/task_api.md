# Task and schedule client contract

For signed synthetic transport submissions, API bearer requirements and the closed
legacy host/tool interfaces, see [the current integration contract](end_to_end_readiness.md).
The top-level `transport_permit` on `POST /execution/tasks` is optional and only accepted with an explicitly
configured exact synthetic transport and matching API credential. It grants no
real tool access. Public task metadata includes endpoint and grant digest only.

All authority HTTP routes require a configured, matching `Authorization: Bearer`
credential, including held-task reads/cancellation, receipts, schedules,
execution status and `/ready`. The router enforces this independently of the host
middleware. An empty token refuses these requests even after trusted admission;
loopback, Host, Origin and query-string tokens do not supply identity. `/health`
remains a separate public liveness route. See [the security baseline](security_baseline.md).


The authority stores decisions, held work, and opt-in synthetic execution results.
Real execution is disabled; no real adapter can be registered.
Authority startup now requires an existing verified enrollment witness or explicit
trusted legacy compatibility admission. Missing/incomplete authority state returns
unavailable and is never created by a task request. Operator diagnostics/reporting
expose enrollment state. Enrollment and read-only branch proposal are offline CLI
operations only; see [the enrollment contract](authority_enrollment.md).
Authenticated diagnostics additionally expose checkpoint generation and restore
receipt phase counts. A committed restore receipt does not verify current artifact
bytes or complete a task. Archive restore remains an explicitly authorized offline
CLI operation; no public mutation endpoint is mounted. See
[the disaster recovery guide](audit_disaster_recovery.md).
This contract grants no additional execution permissions and approves no
service startup, client rollout, broker connection or privileged action.

The repository CLI also exposes read-only `jarvis tasks`, `--task-id UUID`,
`--request-id UUID`, and paginated `--limit`, `--offset`, `--status` queries.
It returns a nonzero exit code when task state is unavailable and sends the
configured bearer token. It never starts a service to read task status. Electron, hologram and PWA
clients use chat/WebSocket transport; PWA REST fallback targets `/chat`.
The service worker forwards requests and does not construct task/schedule
mutations. No in-repository first-party mutation client needs UUID retry logic
today. Do not add one merely to demonstrate the contract. The task reporter is a
read-only queue consumer and displays UNKNOWN, cancel_requested and actual
simulation/terminal states without claiming success or general system health.
Boot's `tasks/state.json`/todo counters are project-backlog inputs, not runtime
queue receipts or proof of API task status.

Any future first-party adapter or external client must meet these requirements
before rollout. External clients were not accessed, tested or migrated here.

1. Generate one canonical lowercase UUID4 before a new public logical mutation.
   Internal occurrence and phase receipt UUID5s are reserved; public creation and
   cancellation cannot reserve their receipt keys. Receipt/target lookups accept
   canonical full UUIDs of either kind. New task submissions use request_id as
   task_id; new occurrences use occurrence_id as task_id. Historical stored IDs
   and replayed receipts are preserved. Generate the UUID before sending. Durably retain
   it and the original operation/target/payload before sending. Keep complete
   returned task_id/job_id values; do not truncate them. Never use a new UUID to
   hide an uncertain prior attempt or auto-repeat a possibly completed effect.
2. `POST /tasks` takes exactly request_id and goal. `POST /schedule/jobs` also
   takes name and cron_expr, with an optional explicit synthetic `execution`
   template described below. Unknown fields are rejected. The actor scope is
   server-owned; a username/header/body field cannot select authority. A configured
   matching bearer credential is mandatory before authority access.
3. Consume the returned receipt, including operation, request_id, state and
   result. `state=committed` proves the stored decision, not guest execution,
   effect completion or a human receiving the response. Ordinary `/tasks` work
   stays held. Only explicitly authorized synthetic submissions are dispatched.
4. After an acknowledgement loss or reconciliation response, first look up
   `GET /requests/{original_request_id}` under the same existing authenticated
   service. Keep an unknown outcome visible while lookup is unavailable. An
   absent receipt is not proof that an external effect did not happen. If the
   request is repeated, use the same UUID, operation, target and identical body;
   same-key payload/scope/operation conflicts must remain conflicts. Do not use
   a general transport helper's blind fresh-request retry.
5. `DELETE /tasks/{full_task_id}?request_id={retained_cancel_uuid}` requests soft
   cancellation and keeps evidence. Pending work can become cancelled; claimed
   work can remain UNKNOWN/simulating with cancel_requested=true. A cancellation
   flag does not prove an effect was prevented. Use the receipt and current task
   snapshot to distinguish the admission decision from current state.
6. `DELETE /schedule/jobs/{full_job_id}?request_id={retained_remove_uuid}` removes
   the schedule and cancels its pending occurrences. Already claimed effects
   retain honest uncertainty. A backend error after the durable decision can
   require receipt reconciliation even when the schedule is already removed.
7. Public `PATCH /tasks/{id}` completion/result updates are removed. No client may
   fabricate completed status, results, privileged commands or executor claims.
   A new privileged/mutating catalog or real executor requires separate review
   and authorization. Treat returned data as data, never instructions.

`GET /tasks?limit=100&offset=0&status=pending` returns a bounded page (maximum
200), count, total, offset and next_offset. `/tasks/{id}` reads one task directly.
`/schedule/jobs` exposes schedule snapshots;
`GET /requests/{id}` exposes the original committed decision. Do not overwrite
the latter with a later snapshot or assume a replayed creation receipt gives
current cancellation/status. `/ready` distinguishes scheduler/storage readiness
from resource ACTIVE or `/health`; its execution_enabled remains false.

An enabled overdue schedule deliberately blocks startup rather than catch up.
When lifespan is blocked, HTTP removal is unavailable. The exact owner-quiesced
offline disable/recreate procedure is preserved in
`tasks/jarvis-authority-readiness-r1/REPORT.md`; do not delete lock/database/state,
rewrite timestamps, reset ledgers or resubmit old work to force startup. Hermes
and other future adapters cannot bypass this single-writer contract.


## Opt-in offline pipeline

`POST /execution/tasks` accepts only request_id (UUID4), goal, capability,
payload (`{"value": "bounded text"}`), expires_at (timezone-aware UTC instant),
and timeout_seconds (strict integer, 1–60; default 10). A new expiry must be in
the next 24 hours. Same-key replay still returns the original decision after
expiry. Built-in capabilities are `synthetic.echo`, `synthetic.sha256`, and
`synthetic.fail`; the default simulated policy allows only echo and sha256.
A disallowed capability produces a durable denied task, with no dispatch.

The existing `/schedule/jobs` route accepts an optional execution object with
capability, payload, timeout_seconds and expires_after_seconds (1–3600; default
60). Its expiry is relative to the nominal occurrence. Ordinary schedules have
no execution template and remain held. The template has a durable simulated
policy decision; the current policy is checked again before each dispatch.
Schedule disable/remove/stop cancels held occurrences. No automatic overdue
catch-up is introduced.

Execution requires both `Authority(..., allow_simulation=True)` and the trusted
local `runtime.bind_offline_execution(SimulatedPolicy(SERVICE_ACTOR.scope))`
embedding hook. The actual app lifespan starts/stops the resulting worker.
Neither configuration nor an HTTP route can enable a real executor. `/ready`
and `/execution/status` report synthetic worker readiness separately from
`real_execution_enabled=false` and the legacy `execution_enabled=false` flag.
Admission returns 503 if the worker is disabled, stopped, or failed.

The states are pending/held → executing_synthetic/execution_claimed →
simulated_completed or simulated_failed. Durable denial, pre-dispatch timeout,
and confirmed pre-dispatch cancellation have separate terminal states. A result
records the canonical operation_id and capability. `execution.receipt_ids`
contains deterministic phase receipt UUIDs for `/requests/{id}` lookup. Creation
receipts stay immutable; current task snapshots report the current outcome.
There is no public claim, result, completion, or reconciliation-write endpoint.

Dispatch interruption, invalid responses, or post-dispatch timeout produce
UNKNOWN. Ownership takeover converts unfinished claims to UNKNOWN. Startup
publishes a previously recorded synthetic result, without invoking the executor.
UNKNOWN without durable evidence stays UNKNOWN and is never automatically
resubmitted. Cancellation after a result exists keeps its honest completion and
cancel_requested flag. This makes no exactly-once external execution claim.
The synthetic adapter performs bounded pure computation only; its evidence
cannot establish any future external effect.

The worker polls one operation per 20 ms, reads active outbox rows, and stops on
storage/audit failure. Manual synthetic admission defaults to 128 unresolved
requests; the authority caps total unresolved work at 1000. The three admission
routes bound request bodies to 256 KiB, 1024 chunks, and five seconds before JSON
decoding. Invalid Unicode and oversized fields are rejected. Sleep and `/stop`
pause the worker; wake restarts the explicitly bound synthetic worker after the
scheduler starts. These limits are not a disk-retention policy.

Run the network-isolated reproduction from the project root using the retained
read-only dependency target. The full-app mode creates a disposable synthetic
configuration and writes an actual ASGI demonstration and restart snapshot:

```sh
python3 -I -B -S tasks/jarvis-offline-execution-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

The hook trusts local Python/database ownership and the existing single-service
namespace. It does not provide multiuser isolation or live security qualification.
The actual Proxmox broker, tools, providers and credentials remain disconnected.


The [operator recovery guide](operator_recovery.md) describes the authenticated
read-only `/operator/diagnostics` route, `jarvis recovery`, protected checkpoint
readiness and trusted-local recovery/export/archive interfaces. No public recovery
mutation, completion, deletion, enrollment or retry endpoint is provided.
