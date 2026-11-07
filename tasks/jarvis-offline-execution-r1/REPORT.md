# JARVIS V2 offline execution sprint

Implemented and verified 2026-11-05 America/Chicago (evidence UTC 2026-11-06).
This is working source and offline application integration; real execution,
production startup, real-state migration and live security qualification remain
unperformed. All state below is persistent disposable synthetic SQLite state.

## Implemented architecture and integration

`app/agent/execution.py` adds a disabled-by-default executor interface and a
registry that accepts only the exact built-in SyntheticExecutor class. There
are no tool/provider imports or real callbacks. Bounded echo, SHA256 and an
explicit synthetic failure capability return data only. SimulatedPolicy issues
scope/capability/revision-bound decisions; default policy allows echo and SHA256.
A disallowed request records a durable denied task and never dispatches.

The existing fenced Authority owns admission, outbox, audit/event and immutable
receipts. Execution evidence uses a new record kind in the existing records
table: no schema version change, alternate database or production migration.
Submission uses the same UUID4 as request_id, task_id and operation_id. Scheduled
operations use the existing deterministic occurrence UUID5 as task_id. Derived
UUID5 phase keys identify internal receipts; they are not new logical operations.
Public mutations require UUID4 so callers cannot reserve internal receipt keys.
Existing records and historical replay results retain their original identities.

The lifecycle is request → simulated authorization → pending/held outbox →
fenced claim and current policy/deadline/cancellation recheck → pure synthetic
execution → durable validated evidence → durable result/receipt publication →
status → restart reconciliation. State, audit and receipts commit in Authority
transactions. A claimed operation is never replayed into an executor invocation.
Lost acknowledgements use the original request or phase receipt ID. No exactly-once
external execution claim is made.

`runtime.py` exposes a trusted-local explicit synthetic binding hook.
`server.py` starts/stops that worker in the actual application lifespan.
`POST /execution/tasks` validates typed bounded requests. Optional synthetic
execution templates on `/schedule/jobs` survive durable schedule and occurrence
admission; the actual DateTrigger callback feeds the same worker. Plain tasks
and schedules stay held. The worker cannot be enabled through HTTP. Public result,
completion, claim and reconciliation-write endpoints do not exist.

Task status uses direct lookup and bounded pages. `execution.receipt_ids` makes
phase reconciliation discoverable. `jarvis tasks` reads pages, individual tasks
and receipts, uses configured bearer auth and exits nonzero on unavailable state.
The existing Reporter was exercised unchanged: it preserves denied, synthetic,
UNKNOWN and cancel_requested states. Resource sleep and `/stop` now stop the
worker; wake starts the explicitly bound worker after scheduler startup. Readiness
reports worker failures separately from resource ACTIVE and health.

Expiry before dispatch is timed_out with no computation. Confirmed pre-dispatch
cancellation is cancelled. Cancellation after a result keeps completion plus
cancel_requested. Dispatch exceptions, invalid responses and post-dispatch timeout
remain UNKNOWN without result evidence. Ownership takeover turns abandoned claims
UNKNOWN. Startup may publish existing evidence; absent evidence stays UNKNOWN.
It never automatically repeats an uncertain operation.

Admission is bounded at 256KiB, 1024 body chunks and five seconds before JSON
parsing. Fields and Unicode are validated. Manual synthetic admission defaults
to128 unresolved requests; the authority caps total unresolved work at1000.
The worker dispatches at most one task per20ms, reads active outbox rows, and
stops on storage/audit failure. Completed history is not materialized by polling
or single-task API lookup. Retention and large-ledger SQL costs remain future work.

## Actual demonstration

[DEMONSTRATION.json](DEMONSTRATION.json) retains actual API admission, policy denial,
current result, publication receipt, reporter and CLI status, cancellation,
restart snapshot and startup reconciliation of an independently SIGKILLed worker.
The actual `app.main`/`app.server` lifespan runs through ASGI, without a listener.
One canonical operation ID connects its admission, task, output and phase receipts.
A separately killed process has durable evidence but no published result; the
actual application startup publishes it while its executor is instrumented to
fail on any invocation. No invocation occurs. A synthetic failure is explicitly
reported as simulated_failed in focused tests, not a successful external effect.

## Final source-bound validation

| Run | Passed | Failed | Skipped | Elapsed | Aggregate RSS peak |
|---|---:|---:|---:|---:|---:|
| Core, API, scheduler, process and security pytest |140|0|0|13.985s|107720704 bytes|
| Existing application regression pytest |46|0|0|part of full-app run|part of full-app run|
| Actual full-app lifespan/scenario groups |7|0|0|2.813s total|106233856 bytes|
| Native Pydantic/PyYAML/psutil probes |3|0|0|part of full-app run|part of full-app run|

186 pytest cases passed in the final two runs; seven application scenario groups
and three native probes are additional checks, not extra pytest cases. The core
includes80 predecessor contract cases rerun against this implementation and60
new pipeline/security cases. Its process helper changes only the occurrence/task
identity expectation to the new canonical ID; the historical helper is untouched.
There are14 actual independent-process cases in core (eight inherited plus six
new SIGKILL boundaries) and one additional actual-app independent-crash scenario.

Final runs: `runs/20261106T022910563451Z/RUN.json` and
`runs/20261106T023203780679Z/RUN.json`. They bind identical 90 application Python
source files and the same runner. INPUT-SHA256SUMS binds each copied input,
including test helpers and child programs. SOURCE-SHA256SUMS pins the current
application, public example, tests, docs and packet source. `source/` contains
implemented changes, `before/` retains the baseline, and SOURCE.patch is reviewable.

Core stderr is empty. Full-app pytest retains two dependency deprecations
(Starlette httpx TestClient and the AnyIO BlockingPortal alias). Four synthetic
lifespan startups each retain expected missing Piper binary/model and unserved
loopback Ollama warnings. These are inspected and preserved, not suppressed.
Intermediate122/126/135/140-case runs and earlier full-app runs are retained;
their counts are not summed into final coverage. No failed pytest run occurred
in this sprint. This is not a current full-repository-suite or hardware/provider
feature qualification.

Each payload starts inside the existing verified unprivileged bubblewrap cage:
fresh namespaces, read-only copied source/dependencies, private disposable output,
zero capabilities, NoNewPrivs and IPv4/IPv6 unreachable canaries before imports.
Only the retained exact28-distribution target is reused. No install, download,
package upgrade, real configuration or credentials are needed. Bounds remain
1GiB AS/process,768MiB observed aggregate RSS,120/121s CPU,64MiB/file,64 FDs,
zero cores,120s wall,20000 controlled files/256MiB per run and at most two payload
processes. No guard was enlarged and no guard fired. These are process/fixture
bounds, not a hostile same-UID isolation or disk-quota qualification.

## Crash, reliability and security evidence

The retained independent-process fixtures exercise lifetime writer exclusion,
precommit rollback, committed admission with lost acknowledgement, atomic scheduler
occurrence/task/last_run/receipt, and interrupted simulator claims. Six new SIGKILL
cases stop after claim, after computation, before evidence commit, after evidence
commit, before publication commit and after publication. Restart leaves the first
three UNKNOWN with no retry, publishes evidence for the next two, and preserves
published completion in the last case. The actual-app crash scenario additionally
proves lifespan/worker startup performs that reconciliation without redispatch.

Focused cases cover duplicate and conflicting operations, two-thread same-key
admission, stale owner/generation checks, SQL lock contention and poisoned-instance
reopening, audit-trigger failure before dispatch, policy revocation, unauthorized
capabilities/scope, inconsistent decision fields/types, five hostile executor
responses, capacity refusal, invalid UUIDs/Unicode/deadlines/payloads, cancellation
before/after claim and after result, pre/post-dispatch timeouts, response loss,
public phase-key reservation, oversized/chunked/slow/empty-stream requests, and
bounded lookup/polling. Actual app tests cover configured bearer enforcement,
auth-before-body-limit ordering, forbidden completion, readiness, CLI failure
semantics, reporting, stop/sleep/wake, shutdown cleanup and overdue-schedule refusal.
[REVIEW.md](REVIEW.md) records the primary engineer review and resolved findings;
no independent review of this new implementation is claimed.

## Remaining limits and next engineering priorities

Real executors, broker/provider/tool effects, multiuser authorization and hostile
local Python isolation remain absent. The optional existing bearer policy is
unchanged; SERVICE_ACTOR is a trusted single-service namespace. Synthetic pure
computation evidence cannot prove an external effect. Clocks and local SQLite
ownership/storage are trusted; SIGKILL proves process recovery, not physical
power-loss or multi-host durability. UNKNOWN without evidence requires operator
investigation and cannot be cleared to success/cancellation through public routes.

The complete repository suite was not run. Optional voice, model, device, browser,
communications and live infrastructure paths are outside the retained dependency
closure and this offline qualification. No coverage percentage or live security
qualification is claimed. Two dependency deprecations remain. Overdue enabled
schedules intentionally require the existing explicit owner-quiesced recovery;
no catch-up or ledger reset is implemented. Resource ACTIVE remains a resource
state; `/ready` must be checked for scheduler/worker readiness.

Recommended next autonomous offline sprint: bounded ledger retention/export and
large-ledger index/latency measurements without erasing receipts; explicit operator
recovery tooling for overdue schedules and evidence-less UNKNOWNs; broader optional
module regressions when an approved offline dependency closure is available.
Real adapter engineering and live activation remain separately scoped work.

## Reproduction and live prerequisites

From this project root, sequentially:

```sh
python3 -I -B -S tasks/jarvis-offline-execution-r1/run_checks.py --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-offline-execution-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Run only the guarded workflow for application imports. Each reproduction creates
new disposable evidence and performs fresh resource/canary checks. No production
service is started. Preserved earlier runs and dependency materialization are
read-only inputs. BASELINE.json records unchanged predecessor seal identities.

[LIVE-ACTIVATION-PREREQUISITES.md](LIVE-ACTIVATION-PREREQUISITES.md) records the exact
remaining principal, protected install, public bindings, credential-canary,
VM164-only Audit+Console grant, trusted guest setup, timed acceptance and separate
Gate6K/real-adapter gates. None is authorized by this offline pass. VM164 hardware
and no-NIC status, VM162/163 and the AI server were untouched. No credentials,
permissions, real databases, services, broker code or sealed predecessor evidence
were changed. No commit, push or deployment was performed.
