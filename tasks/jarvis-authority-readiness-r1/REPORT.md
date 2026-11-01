# Transactional authority and existing-app offline readiness

Scope: Nexus-local source engineering and disposable offline fixtures. Real task
execution, serial broker activation, provider/tool dispatch, production startup,
real-store migration, Proxmox and guest operations remain disabled/unperformed.
This packet supersedes the earlier queue/scheduler design gaps, not their sealed
historical evidence or the separate privileged/live gates.

## Implementation

`app/agent/authority.py` owns task, schedule, occurrence, receipt, event, outbox and
synthetic-effect state in one SQLite database. A lifetime nonblocking flock on a
stable lock file excludes a second independent owner. Each acquisition advances
a durable generation; mutation transactions check owner, PID and database/lock
identity. Closing takes the transaction mutex. BEGIN IMMEDIATE, foreign keys,
WAL, synchronous FULL and bounded busy timeout define the storage contract.
This is process-crash evidence, not physical disk/controller power-loss proof.

Every mutation requires a canonical full UUID. Canonical payload, operation and
server-owned scope bind its durable receipt. Same request replays the original
decision; changed payload/operation/scope conflicts without revealing a receipt.
State, receipt, event and held outbox commit together. Lost acknowledgements are
reconciled by the original key. SQL/storage ambiguity poisons that instance;
there is no blind automatic retry, fresh-key substitution or success inference.
Reads return detached snapshots in stable admission order. Identifier collisions
fail without overwriting an existing record, including across scopes.

`runtime.py` shares one lazy authority across the existing server and local
facades; there is no independent JSON writer. A second process refuses ownership,
not an alternate queue. Existing optional bearer enforcement is unchanged.
Without a separately authenticated caller identity, scope is the server constant
`local-service`; submitted scope/header/username cannot select it. All callers
within that service share its namespace. Idempotency is not authorization or
multiuser isolation; trusted local Python/database ownership is not a sandbox.

The router requires request IDs for creates and cancellations and exposes
`GET /requests/{request_id}`. Public PATCH completion/result mutation is removed.
DELETE retains records/receipts and requests cancellation. These are intentional
API changes: old clients must retain UUIDs and inspect receipts, and legacy tests
for eight-character IDs, JSON writers or arbitrary status updates are historical,
not current-contract passes. Unrelated app routes and authentication remain.

Schedules retain stable UUID/revision and nominal UTC time. One-shot real
APScheduler timers capture that nominal identity and lifecycle epoch. Occurrence,
task, receipt, held outbox, last_run and next nominal commit together. last_run
means accepted nominal occurrence, not completed effects. The occurrence
fingerprint includes its explicitly committed next nominal; create retries reuse
the original server-derived next date across clock changes. Expected removed,
disabled or stale callbacks do nothing. Timer failure after admission preserves
the committed occurrence, reports reconciliation and prevents further admission.

Stop/remove/disable cancel pending scheduled outbox entries transactionally.
Already claimed work receives cancel_requested; a committed effect is never
reported as no-effect cancellation. Stop invalidates local callbacks and attempts
owned backend cleanup even when the durable stop fails; it propagates that error
and does not claim the database stop committed. Backend removal errors return a
sanitized reconciliation response with the original durable receipt retained.

`simulation.py` is explicitly opt-in and absent from public execution routes.
Its only effect is a unique SQLite marker. Claim/effect/acknowledgement are
durable; abandoned claims become UNKNOWN on restart, never pending for retry.
Reconciliation requires synthetic claim provenance; imported legacy UNKNOWNs
cannot be declared cancelled because they lack synthetic markers. These rules
cannot prove the outcome of a future external tool, model, provider or VM action.
No actual executor or external-effect callback exists in this implementation.

`migration.py` requires two explicit source paths, validates captured bytes before
the atomic empty-target import, and preserves original files, exact IDs, hashes
and deterministic UUID5 mappings. No-follow regular-file reads, strict UTF8/JSON,
duplicate/unknown field rejection, finite numbers, 1MiB per source and 1000 total
records bound capture; the authority also caps canonical transaction payloads at
1MiB. Pending imports stay held; historical nonpending tasks stay UNKNOWN, and
all schedules are disabled with historical values retained as metadata. No real
store was read/migrated. Existing unsupported database evidence is probed
read-only before DDL/journal changes; zero-byte/partial stores cannot bypass the
legacy migration gate. Cross-file source consistency requires quiesced writers.

## Qualification and evidence

`RESULTS.json` identifies the final source-bound core/process and full existing-app
runs. Retained earlier runs include 65-pass/one skipped process module, then75
and77-pass intermediate revisions, and a public-headroom refusal before launch.
Those are preserved, superseded evidence, not summed into final coverage.

The final focused suite covers strict IDs, detached reads, cross-scope conflicts,
SQL metacharacters as data, concurrent same-key transactions, schedule ID
collisions, stop/admission races in both orders, claimed/committed-effect
cancellation, complete occurrence fingerprints, backend failure cleanup,
idempotent migration, hostile/oversize legacy inputs and source preservation.
Eight cases use actual fresh independent interpreters and controlled SIGKILL at
commit/claim/effect boundaries: lifetime writer exclusion both directions,
precommit rollback, postcommit lost acknowledgement, UNKNOWN recovery and atomic
occurrence/task/last_run/receipt. Parent plus at most one payload child runs at a
time. These are real SQLite/process tests; they are not live VM isolation proof.

The original22-package verified target remains immutable. Data-only dependency
planning found28 exact distributions/31 active edges/1096 verified RECORD payloads,
adding click8.5.0, psutil7.2.2, pydantic-settings2.15.0,
python-dotenv1.2.3, PyYAML6.0.3 and uvicorn0.52.4. Retained official PyPI URLs,
artifact hashes, wheel tags and provenance are in DEPENDENCY-PLAN.json; no download,
source build or global install occurred. The exact full-app.lock is hash-bound.
A recognized hash-pinned PyPA pip26.2.1 wheel ran only after fresh guards in a new
private task-local target, with --no-index --no-deps --only-binary --require-hashes.
TARGET-SHA256SUMS pins every resulting file. This is retained provenance, not a
new publisher-signature or vulnerability audit.

The actual app.main entrypoint and app.server app/lifespan run in a fresh pip-free
interpreter with that target read-only. This is the existing app, not an extracted
route subset. The public example is converted to a synthetic config; providers,
voice, remote memory/comms and resource automation are disabled. The startup
probe can only attempt the synthetic unserved loopback port9 inside its fresh
network namespace. No real config, runtime state, credentials or host home is
mounted. Tests exercise readiness, unrelated safe routes, optional/configured
bearer behavior, request replay, forbidden public completion, shutdown, mandatory
storage failure and overdue-schedule startup refusal. Native pydantic-core,
PyYAML and psutil get explicit small execution checks, origins and file hashes.
This does not qualify optional voice/tool/provider features or every old test.

Each installer/test process starts under the existing verified unprivileged
bubblewrap with fresh user/mount/PID/network/IPC/UTS namespaces, capabilities zero,
NoNewPrivs, read-only source/dependencies, hidden outside sentinel and stdio-only
initial descriptors. IPv4/IPv6 documentation-address canaries are unreachable.
Limits: 1GiB address space per process, 768MiB observed aggregate RSS watchdog,
120/121s CPU, 64MiB per file, 64 descriptors, core size0, 120s wall watchdog,
20,000 controlled files/256MiB controlled tree and at most two payload processes
(plus two bubblewrap supervisors). Watchdog cleanup only signals owned descendants
whose recorded start identity still matches. File/RSS sampling is a controlled
test bound, not a hostile-workload disk quota. Every run retains fresh public
memory/load/disk/worktree headroom and measured peaks; no guard was enlarged.

Independent reviewer: existing separate gpt-6-astra/high agent, static review only.
INDEPENDENT-REVIEW.md binds eight final source hashes and ten closed findings.
Runtime results are the primary agent's evidence, not tests performed by reviewer.

Final source-bound results:80 passed, zero failed/skipped, core/process run9.470s
with102,662,144-byte observed aggregate RSS peak; final full-app/native run1.088s
with78,958,592-byte RSS peak. No safety threshold fired. The final two runs bind
the same88 application source files. SOURCE-SHA256SUMS additionally pins the public
example and test/planning/runner sources (99 files total); reviewed implementation
copies are retained under source/. The exact28 target contains1188 pinned files.
The final core stderr is empty. Full-app stderr retains the expected synthetic
startup availability warnings for absent Piper binary/model and the unserved
loopback Ollama probe; no real model/tool/provider is contacted or qualified.

Reproduce from the project root using the preserved read-only target; each call
creates fresh private input/output fixtures, checks public headroom, and stops
instead of relaxing any guard:

```sh
cd '/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS'
python3 -I -B -S tasks/jarvis-authority-readiness-r1/run_checks.py --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-authority-readiness-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Rebuilding the target, if needed, uses the same runner with `--mode materialize`.
It creates a new timestamped task target and prints its path; use that new
output/site-packages path in subsequent calls. It never overwrites the retained
target, installs globally, downloads, builds source or imports candidate code on
the host. Do not run pytest/app imports directly outside this guarded workflow.

## Recovery and remaining limits

Do not delete/reset database, WAL, writer lock, receipts or events to unblock work.
Quiesce writers before any copy/export and preserve SQLite-consistent evidence.
Keep private state within its owner boundary; do not export credentials or broad
runtime directories. An UNKNOWN response requires original-key receipt lookup
and explicit domain evidence; absence of a receipt is not proof about an external
effect. There is no external executor in this version.

An overdue enabled schedule intentionally blocks restart rather than catch up.
This also applies to resource-manager sleep/wake across its nominal time. The
HTTP disable/recreate route cannot be relied on when lifespan is blocked. The
explicit owner-quiesced offline recovery is: preserve a consistent DB checkpoint;
open its exact path through Authority under the approved application owner;
inspect list_schedules(SERVICE_ACTOR); call set_schedule(SERVICE_ACTOR, a retained
new UUID, exact job_id, enabled=False) for each independently reviewed overdue
schedule; retain receipts; close normally; then restart and recreate only intended
future schedules through the normal API. Never alter next_run/last_run directly,
resubmit historical tasks, bypass owner_busy, delete the lock or treat recovery
as authorization to run effects. This procedure was not run on a real store.

No production service is started by this packet. No broker/executor wiring,
authority expansion, permission/UID changes, secret issuance, guest bootstrap,
VM access, migration of real data or Gate6K run is included. Disk power loss,
multi-host storage, hostile same-UID code, external anti-rollback and actual
restricted principal/guest isolation remain outside these offline results.

## One staged eventual-live proposal — no execution

The reviewed serial implementation remains pinned in
`../proxmox-automation-phase3-review-r1/RELEASE.json`:13 source files, source
manifest9e5bdd0ea59fa36021f462f4388597fefd4b65f9cee32024e86ba5d33d700301,
archivee2ab01927aeeff20d6e6a6e602aee112b3d1e99a79aaaf88d9263182e6a142f1.
Its INSTALLATION.md, LIVE-ACCEPTANCE.md and STOP-AND-REVOKE.md remain the exact
limited operator procedures. No new broker hardening/requalification is claimed.

Use the existing staged APPROVAL-PACKET.md, not a blanket permission grant:

1. Establish the actual restricted Nexus submitting path/UID and separate broker
   UID, protected source/config/units and fresh disabled complete grant. Current
   Nexus sudo/docker/lxd membership is not an approved execution boundary.
   Perform actual no-transport denial probes with a synthetic credential sentinel
   before real issuance, and retain the source/grant-bound acceptance (max600s).
2. Only after that gate, privately create the fresh PVE principal/separated token
   with VM.Audit and VM.Console only on /vms/164, propagation0, initially max3600s;
   preserve the existing VM.Audit observer unchanged. The human-only provisioner
   writes the secret directly to protected broker storage, never Codex/logs/env.
3. Using an independently trusted installed-OS guest-root session, install only
   the pinned non-root worker/config/unit and exclusive ttyS0. Passwords stay
   locked; no SSH/NIC/packages/guest-agent or privileged catalog. Required actual
   machine-id, worker/role UIDs/GIDs and filesystem identity remain unknown. No
   root session means stop for exact separately approved maintenance media,
   partition identity, preservation and lifecycle transitions, not a workaround.
4. Only after actual identity/DAC/transport gates pass, explicitly approve a timed
   read-only activation/acceptance window for VM164 UUID
   faeb1db8-0df9-482d-b3e4-f6ccc1602193, exact disk and serial0/ttyS0. Routine
   catalog remains identity/kernel/isolation-summary. Reconcile negative controls
   against live evidence; offline mocks/processes are not proof of live isolation.

The smallest future PVE action is that fresh VM164-only role/user/token grant;
the smallest guest action is the protected non-root worker and exclusive serial
service setup through a trusted root context. These depend on the Nexus boundary
and complete missing public bindings first. No root credential is delegated.
Raw console passthrough, arbitrary commands, mutating catalog, privileged Gate6K
qualification and future executor wiring each remain independent decisions.

Stop/revoke: close both accepting sockets/services and active channels; revoke
only the new token's VM164 ACL/token; stop only the new guest worker if approved.
Preserve ledgers/checkpoints/public evidence. Token deletion alone may not close
an established console. No automatic reset, getty restoration, reboot, rollback,
media change, VM deletion or credential-directory export is included.
