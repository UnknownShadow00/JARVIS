# Offline application execution and readiness

Release-candidate update: **all authority routes, including /ready, require a
configured bearer even on loopback and in an embedded router**. Empty-token
anonymous authority access is retired. The current protected-ancestry, WebSocket,
default and release contract is [release_candidate.md](release_candidate.md).
Historical Sprint 6 details below are superseded wherever they describe anonymous
held-task/readiness access. No deployment or live authorization is granted.


Sprint 6 joins the actual FastAPI lifespan, Authority, queue, scheduler, execution
worker, receipts, enrollment, recovery registry and protected witness. The evidence
packet is [the source-bound readiness report](../tasks/jarvis-end-to-end-readiness-r1/REPORT.md).
All demonstrations use disposable databases, identities and keys inside a networkless
sandbox. Stock unprovisioned startup continues to refuse missing authority admission.

## Execution contract

The default worker remains pure synthetic execution. A trusted embedding can supply
an exact `SyntheticTransport` instance to `bind_offline_execution`; environment
variables, HTTP flags and real tool metadata cannot construct or enable it.
Only `synthetic.local.echo-v1` and `synthetic.local.hash-v1` exist. The transport uses
bounded AF_UNIX socketpair frames and kernel peer credentials. It has no network,
URL, shell, provider, Proxmox or arbitrary adapter operation.

A transported submission needs both the configured API bearer and an independently
HMAC-authenticated synthetic operator permit. That permit binds the original UUID,
actor scope, store, checkpoint, exact goal hash, execution spec, endpoint and validity
period. Operator, request, response and checkpoint keys must be distinct. Supply
keys through trusted in-memory configuration or the documented CLI file descriptors;
never command-line values, public task responses or logs. The symmetric keys and
endpoint deliberately share one trusted process: this fixture demonstrates protocol
and durable state correctness, not privilege separation from a compromised owner.

The Authority is the only SQLite writer. Before computation the endpoint commits a
reservation and receipt. It then commits its signed report and receipt. The worker
records verified evidence and separately publishes a terminal receipt. Duplicate
canonical UUIDs with identical payload return the original receipt; conflicts fail.
Cancellation, expired grants, missing witnesses, wrong history keys or uncertain
replies cannot silently dispatch again. A signed endpoint report is not completion.
History verification has a lifetime bound of 128 transported grants per authority;
reaching the bound refuses new grants without deleting history.

## Recovery and operator interface

`python -m app.agent.operator_cli --help` describes read-only inspection and
explicit offline mutations. Two new mutually exclusive actions are
`--reconcile-transport-report TASK_UUID` and
`--publish-transport-evidence TASK_UUID`. They require an existing database,
protected ledger, enrollment witness, recovery registry/reference, `--commit`,
canonical operation UUID and a matching authenticated recovery permit. Supply the
transport operator/request/response keys using `--transport-operator-key-fd`,
`--transport-request-key-fd` and `--transport-response-key-fd`, and the exact
`--synthetic-endpoint-id`. Existing ledger, registry and operator key FD controls
also apply. The permit binds the verified pre-open checkpoint; writer takeover
must be exactly the next generation. Validation happens before writer acquisition
and again at the effect point. Exact committed receipt retries need no new writer.

Report reconciliation authenticates the original durable grant, request and report,
creates evidence, and marks it as requiring separate publication authorization.
A restart between these two commands keeps the task UNKNOWN. A second independent
permit can publish that evidence without calling the endpoint. A reservation with
no report remains UNKNOWN and cannot use this recovery path. No automatic retry,
new UUID workaround, endpoint invocation or fabricated success is allowed.

Archive verification and restoration remain inert. A durable proposal and approved
decision record do not activate restored tasks, executors or schedules. Missing
external anchors, conflicting ancestry or incomplete renewal block readiness.

## Closed legacy paths

Real `ToolRegistry.call`, `execute`, lazy callables and metadata getters refuse
execution before importing real tools, regardless of safety/confirmed flags.
Chat, streaming and native voice processing refuse tool/vision intents. `/confirm`
is absent. Clipboard/type dictation helpers return false without desktop imports.
Direct dormant library helpers are not supported execution interfaces; future
adapters must review them before exposing them.

Host resource mutation HTTP routes return 403 even with a bearer. CLI sleep, wake
and shutdown require a successful authenticated server response; disconnected,
denied and uncertain responses never trigger local process/model operations.
`--offline` is retained as a compatibility flag and grants no host control. Empty
API-token `/stop` is refused. Actual service process termination is limited to
in-memory child leases with PID, creation time, executable, cwd and parent checks;
command-line marker matches grant no ownership. These leases do not survive restart.

WebSocket input is bounded and validated and always disconnects from its manager.
Validation errors do not reflect rejected secret input. VAD recording and wake-word
queues are bounded; cancellation and absolute/frame deadlines apply during speech.
Optional microphone/desktop/model integrations are not qualified by these tests.

## First authorized live read-only stage — prerequisites, not authorization

No real adapter exists in this application. A future stage first requires all of:

1. Explicit operator approval for a separately reviewed, exact release and finite
   read-only action catalog; implementation and independent review of the narrow
   real adapter, including cancellation, report provenance and UNKNOWN handling.
   This packet does not enable real tools or host controls.
2. Protected independent signing custody, separate restricted OS principals and
   effective filesystem/socket/process/device/egress isolation. Current co-located
   HMAC fixtures cannot establish these facts. Validate protected time/expiry and
   key provisioning without putting secret content in evidence.
3. An admitted current Authority with verified external witness, checkpoint and
   recovery registry ancestry; no unresolved reservation, conflicting branch or
   expired approval. Explicitly decide how overdue schedules remain held. No
   automatic adoption, restored activation, history deletion or real migration.
4. A nonempty configured API credential even on loopback, a documented caller
   identity/scope policy and verified ingress/origin protections. Authority routes
   require the configured bearer, including held-task reads, cancellation and
   detailed readiness in independently embedded routers. Qualify startup/shutdown and
   private data/log handling without invoking production startup now.
5. Physical filesystem/WAL/fsync/rename/quota and actual power-loss qualification
   on the intended storage. SIGKILL plus disposable SQLite tests are insufficient
   for hardware power-loss claims. Establish restart-safe service ownership;
   current in-memory native child leases cannot adopt another process's service.
6. For any Proxmox serial bridge, satisfy the separately retained broker packet's
   [preissuance and acceptance order](../tasks/proxmox-automation-phase3-review-r1/LIVE-ACCEPTANCE.md).
   Verify the independent release/CA pins, installed API/schema/filter support,
   actual restricted caller/broker/worker UIDs, root-controlled expiring grants,
   preissuance no-transport/canary qualification and effective VM.Audit+VM.Console
   scope for VM164 only. Nexus administrative group membership is an unresolved
   boundary until independently separated. Match VM164 UUID
   `faeb1db8-0df9-482d-b3e4-f6ccc1602193`, disk/serial0/machine/boot identities through
   trusted observations. VM164 must retain no NIC, only loopback, no guest agent,
   shared host socket, setup media or root serial console. Verify raw TTY worker
   ownership and guest role isolation under separate authorization. Do not infer
   any of these live facts from synthetic tests. VM162, VM163, the AI server and
   privileged Gate 6K qualification remain excluded.
7. An independently approved bounded acceptance and stop/revoke plan preserving
   broker RESERVED/REPORTED/UNKNOWN/ACKED history, with no resend after uncertainty.
   The existing broker is a reviewed reference, not connected by this milestone.

No production keys were created or rotated, no production service was started,
and no provider or live infrastructure integration was performed.
