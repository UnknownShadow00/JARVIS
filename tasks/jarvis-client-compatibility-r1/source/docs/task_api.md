# Task and schedule client contract

The current authority stores decisions and held work. Real execution is disabled.
This document changes no authentication policy or permissions and approves no
service startup, client rollout, broker connection or privileged action.

The repository CLI only calls health/resource routes. Electron, hologram and PWA
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

1. Generate one canonical full UUID before a new logical mutation. Durably retain
   it and the original operation/target/payload before sending. Keep complete
   returned task_id/job_id values; do not truncate them. Never use a new UUID to
   hide an uncertain prior attempt or auto-repeat a possibly completed effect.
2. `POST /tasks` takes exactly request_id and goal. `POST /schedule/jobs` also
   takes name and cron_expr. Unknown fields are rejected. The actor scope is
   server-owned; a username/header/body field cannot select authority. Existing
   optional bearer enforcement still applies where configured.
3. Consume the returned receipt, including operation, request_id, state and
   result. `state=committed` proves the stored decision, not guest execution,
   effect completion or a human receiving the response. Pending work stays held.
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

`GET /tasks`, `/tasks/{id}` and `/schedule/jobs` expose current snapshots;
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
