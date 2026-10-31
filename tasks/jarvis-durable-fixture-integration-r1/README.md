# Durable-store fixture interoperability R1

**Passed:7 new disk-backed integration cases, zero failures/warnings, exit0.**
One fresh guarded interpreter ran in1.109s; no installer, dependency change or
previous suite rerun. **No application source changed.**

[RUN.json](RUN.json) records the exact invocation, source/dependency bindings,
child guards, results and synthetic state hashes. [Stdout](durable.stdout.txt)
contains the seven-test summary; [stderr](durable.stderr.txt) is empty.
[Identities and preservation](IDENTITIES-AND-PRESERVATION.json) pins all inputs,
current source/run hashes and prior packet digests.

## Seven distinct new boundaries

| Case | What actually passed |
| --- | --- |
| Task ASGI→disk→reconstruction | Real POST/PATCH/DELETE wrote the actual JSON store; newly constructed read-only TaskQueue objects reloaded created/updated records and confirmed deletion. |
| Schedule ASGI→disk→reconstruction | Real schedule POST/DELETE published the actual job store; reconstructed Scheduler objects observed matching records and removal. |
| Registered callback→durable task | Actual AsyncIOScheduler registered the current source's bound callback. Explicit invocation created a task that reconstructed readers reloaded. last_run changed in memory but stayed null in the saved job record; a later normal add_job snapshot incidentally persisted it. |
| Task prepublication fault | Real temp write/file sync reached an injected replace EIO; ASGI returned503/not_published, old bytes/memory/reconstructed state survived and temp cleanup completed. |
| Task uncertain publication | Real replacement occurred before an injected directory-sync EIO; ASGI returned409/published_durability_unknown with reconciliation/no-retry metadata. Reconstruction saw the record; the original instance stayed quarantined and rejected another mutation without changing the file. |
| Schedule prepublication fault | With a real backend running, injected replace EIO produced503 and preserved disk/memory/backend registration; reconstruction still contained only the seed. |
| Schedule uncertain removal | Real replacement removed the job before injected directory-sync EIO;409 reported uncertainty. The backend retained its callback, but owner quarantine/membership rejected its invocation and created no task. Reconstruction saw the empty snapshot; new mutation stayed blocked. |

This tests real filesystem publication paths through real FastAPI/Pydantic/httpx
ASGI responses and actual APScheduler registration. Faults are explicitly injected
at replace/directory-sync boundaries, not physical disk failures or process kills.
The callback is explicitly invoked from its actual registered job; no new clock/
DateTrigger test repeats the preceding16-test unit.

**last_run was observed, not repaired.** It remains transient enqueue metadata,
persisted only incidentally by a later complete job snapshot. There is no new
dispatch receipt/outbox transaction or guarantee that task/job state commits
together. Successful post-replace readback establishes current visibility and
reconstruction, not power-loss/crash durability. Reconstructed objects only read;
they never write/start, compete with an owner, clear its quarantine or authorize
restart reconciliation. No multiwriter/exactly-once/cancellation claim follows.

## Existing environment reused without mutation

The preceding private22-package target was hash-checked against its1,022-file
materialized manifest and mounted **read-only as /deps**. Manifest identity:
`6701baa39697b9e250429f8b77938fa3032ac747b1d9798fdee0196e11937a7d`.
Closure identity remains
`c33e6a6d1b55691d2ccb32896fc8bc60ebaf213e0060275aadbfd230cfff0ac8`.
No reinstall, copy of that environment, path change outside the child, network,
download, source build or wider closure. The fresh interpreter had no pip modules
or installer hooks; no bootstrap ran.

Recognized Python3.14.4 and bubblewrap0.11.1 binaries matched retained hashes
`52e0a13e…` and `523da3e7…`; full identities are in the JSON. Pydantic's native
extension loaded from /deps and still hashes to
`189fe5feb2b829cb99ea089c7372c2b1a8592b2f2df6b46b4113af2dc61bcdac`.
All recorded framework modules originated under /deps. This is not full native
feature/OS/library or installed-origin qualification for another machine.

The old stdlib boundary function was reused **as data** with only that one
function compiled; old installer/tests/top-level statements were not executed.
Fresh synthetic checks passed before candidate imports: separate namespaces,
CapEff0/no_new_privs1, read-only input EROFS, hidden outside canary ENOENT,
IPv4/IPv6 ENETUNREACH, only the three explicitly owned stdio handles, and resource
limits. Kernel statvfs additionally confirmed /deps read-only. No real credential
file or protected host path was used as a probe.

## Bounds, collection and extraction limits

[RESOURCE-CHECK.json](RESOURCE-CHECK.json) records six CPUs, low load, ample memory/
disk and one JARVIS worktree/no old fixture runner at observation. The parent
coordinated other projects; only this new JARVIS-private tree was written, with no
GPU/model/build/shared tmp/cache/runtime/service change.

One sequential top-level payload,1.109s,19 work-tree files/98,402 bytes;
address-space1GiB, CPU120/121s, per-file64MiB, FD64 and core0 limits were checked in
the child. The parent used conservative private-tree monitoring and a180-second
wall stop, all below the authorized2GiB/100000-file/two-child/20-minute bounds.
Aggregate file/storage accounting is controlled-workload monitoring, not an
OS malicious-payload quota. No safety stop fired.

Stdout/stderr were direct owned files, not pipes. There was no deadlock/drain
intervention or rerun. Seven pytest-created virtual /work links are preserved
in [SYMLINKS.json](SYMLINKS.json) as metadata, not dereferenced on the host; regular
artifacts and that metadata are sealed.

Handlers/models and queue/scheduler definitions are extracted from the exact
current source with real audit imports/module singletons and server decorators/
initialization excluded. Routes are attached to a fixture-only FastAPI instance;
audit is recorded in memory and every writable record is synthetic. Real
app.server/lifespan/config/voice/provider/audit singleton namespace stayed empty.
No HTTP service or goal/tool/model executor ran. This is not full-app readiness,
full app dependency closure, production, process-crash, concurrency, cron cadence,
misfire/overlap or cancellation qualification.

## Preservation and stop

Current queue/scheduler/server remain50d1a4…/71183f…/613a3b…; all14 recorded public
source/test/context identities and12 prior manifest digests are unchanged. Source
extraction is not a source mutation. No new material application/security question
required another reviewer; no prior review/audit/test was repeated.

Privileged gates remain pending: actual restricted executor/protected broker
installation and pre-credential denial, VM164-only PVE grant, truthful guest
identity/root/bootstrap/worker setup, explicit live activation and separate Gate6K.
No PVE/guest/VM162/163/AI or credential/security/identity/grant access/change.
Ownership, idempotency/occurrence/outbox, already-admitted cancellation and executor/
tool-authority recommendations remain unimplemented product decisions. Ordinary
fixture success creates no new broad approval request or privileged authority.
Stop after this bounded durable interoperability milestone.
