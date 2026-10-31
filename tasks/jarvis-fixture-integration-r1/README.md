# Conditional Nexus fixture integration R1 — runtime milestone

**Passed:16 narrow real-framework tests, zero failures; child exit0.** The existing
unprivileged isolation prerequisite passed before any installer/candidate import.
The exact22-wheel closure was then materialized and executed only inside a guarded
task-local child. **No application source changed and no full app was imported.**
No further unit or privileged action follows this completion.

Authoritative records: [PREFLIGHT.json](PREFLIGHT.json),
[INTEGRATION.json](INTEGRATION.json),
[source/environment/limits](SOURCE-ENVIRONMENT-AND-LIMITS.json) and the preserved
child [RESULT.json](work/integration-output/RESULT.json).

## Recognized installer/runtime and conditional execution

Installed Ubuntu bubblewrap0.11.1 (package0.11.1-1ubuntu0.3), root-owned0755,
non-setuid/non-setgid and no file capabilities, provided the existing mechanism.
Its binary SHA-256 is
`523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6`;
the local installed-package checksum matched. That is installed-tool provenance,
not a fresh publisher-signature qualification.

Runtime: Ubuntu CPython3.14.4, `/usr/bin/python3.14`, SHA-256
`52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41`.
Installer: existing public PyPA pip26.2.1 wheel, SHA-256
`71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e`.
Its retained Gate6L record names the files.pythonhosted.org origin and prior
PEP740 verification; this task verified the exact artifact hash, not a fresh
signature. Historical ACQUIRED_AND_INSTALLED_EXACT in that record describes the
old Gate6L rehearsal, not a preexisting Nexus pip installation.

The closure lock remains
`c33e6a6d1b55691d2ccb32896fc8bc60ebaf213e0060275aadbfd230cfff0ac8`.
All22 exact versions were installed with hash-required, no-index, no-deps,
binary-only, no-compile, no-cache flags into the new `/work/site-packages` target.
No downloads, source builds, version substitutions or global/user-site installs.
The child ran Python isolated/no-site/no-bytecode, with only explicit fixture
paths added after guard validation. Recognized pip was bootstrapped from its
pinned wheel using stdlib runpy **inside that child only**; no candidate import
trick was used during the earlier metadata-only phase.

The six roots have no extras: FastAPI, Pydantic, APScheduler, pytest,
pytest-asyncio and httpx. The narrow closure excludes pydantic-settings/full-app
dependencies. The running host's normal interpreter still cannot discover those
four framework packages; the new target was not installed into an existing env.

## Real child-boundary proof before payload execution

Both the stdlib-only preflight and the integration child checked fresh synthetic
canaries before any installer/candidate import. Bubblewrap supplied separate user,
mount, PID, network, IPC and UTS namespaces; no custom sandbox, Docker/LXD/admin
channel or persistent host policy was introduced. Integration narrowed the OS
read-only allowlist to `/usr/bin`, `/usr/lib`, zoneinfo and loader aliases.

- Read-only synthetic input was readable but write attempts failedEROFS30.
- A new synthetic outside file was hiddenENOENT2; no existing credential value
  was used or read as a probe. Writes were confined to the private fixture output;
  child `/tmp` resolved there, not to the host's shared tmp.
- IPv4/IPv6 documentation-address canaries failedENETUNREACH101 in the new
  network namespace. These intentional negative checks are successful boundaries,
  not denied required setup operations or reasons for a fallback.
- Effective capabilities were zero and no_new_privs1. Only stdin/dev/null and
  the two owned stdout/stderr pipes remained; a deliberately inheritable synthetic
  parent handle did not enter the child. Environment was cleared; no HOME,
  credential environment, host container socket or privileged handle was supplied.
- Address-space1GiB, CPU120/121s, per-file64MiB, open-FD64 and core0 limits were
  checked inside the integration child. The initial stdlib probe used stricter
  small file/CPU bounds. Namespace-local mappings did not create/change a host
  account, group, credential, service or security setting.

These are actual Nexus child canary/kernel observations. They do not qualify the
future broker's submitting UID, root-owned credential protection, PVE authority,
guest isolation or Gate6K. The administrative parent identity still exists;
this temporary child is not an approved production executor identity.

## Exact16-test framework scope

The tests use the **real** selected FastAPI/Pydantic/Starlette/httpx/APScheduler
packages. Exact current source is copied read-only and parsed into a fixture
namespace: queue/scheduler audit imports and default singletons are excluded;
server selection includes only the three request models, task/schedule handlers
and their error helpers. Original decorators/global initialization are excluded,
then routes are mounted on a new minimal FastAPI instance. Audit is an in-memory
recorder; task/schedule records use in-memory stores.

| Cases | Actual coverage |
| --- | --- |
|1|Native pydantic-core SchemaValidator and current request model behavior. |
|1|Task CRUD, real ASGI routing/response serialization, missing404 and schema422. |
|6|Create/update/delete prepublication vs applied-uncertain error metadata through real ASGI, using injected persistence exceptions. |
|3|Already-applied in-memory audit submission failures through real ASGI. |
|1|Actual CronTrigger parsing, invalid-cron400, schedule schema422 and CRUD. |
|2|Injected scheduler persistence outcomes through real ASGI. |
|1|Actual AsyncIOScheduler start/stop/restart/registration, direct calls to its registered owner callbacks, disabled/removed/stale-generation rejection. |
|1|An actual50ms DateTrigger dispatch through AsyncIOScheduler to the current owner callback, creating exactly one synthetic task within the bounded observation. |

HTTP requests used in-process ASGITransport; **no HTTP server/service was started**.
The timed case rescheduled an otherwise future annual-cron fixture with a
DateTrigger. It proves a short real timer/callback path, not full cron cadence,
misfire/coalescing/overlap, cancellation, recovery or long-running scheduling.
The direct callback case is labeled separately from timed dispatch. Fault-injected
HTTP cases verify framework handling, not a new real disk-crash/durability test.
No goal executor, tool, shell, broker, model/provider or Proxmox operation ran.

Native pydantic-core2.46.5 was actually loaded only inside the guarded child;
its native SchemaValidator converted a synthetic integer and backed real models.
The preserved4,707,040-byte extension hashes to
`189fe5feb2b829cb99ea089c7372c2b1a8592b2f2df6b46b4113af2dc61bcdac`,
matching the original wheel RECORD. This is basic native behavior on this
interpreter/system-library set, not exhaustive ELF/library/ABI or installed-origin
certification for a guest/other host. Exact installed versions/module origins and
the1,022-file materialized manifest are retained.

## Bounds, warnings and collector intervention

The child install/test stages finished in2.146s. Runner collection took140.473s;
first preflight through final collector exit was665.070s, within the20-minute
window. Two top-level fixture payload launches were sequential (one probe, one
integration); no prior suite or fixture was rerun. Bubblewrap's internal
monitor/reaper is not counted as an independent test workload.

Precalculation:972 archive files,108 directory names,17,019,384 uncompressed bytes,
largest entry4,707,040 bytes; conservative envelope203,263,936 bytes/8,776 files.
Actual complete work tree at runner exit:24,191,819 bytes/1,061 files. Output
observed peak was17,263,266 bytes/1,025 files. The parent monitored only this new
tree with conservative256MiB/20,000-file and180-second safety stops; none fired.
Storage/file-count checks describe a controlled pinned-wheel workload, **not an
OS-enforced hostile-payload quota**. Per-process kernel limits are distinct from
that aggregate accounting; no global resource/mount/cache/tmp policy changed.

The bootstrap and frameworks shared one guarded interpreter. Restoring sys.path
and argv did not unload pip's import-warning hook/modules. Preserve **223
pytest-reported warnings plus additional stderr import-deprecation output**.
These are not silenced or misreported as a clean fresh-interpreter result;
pip26.3 may enforce its changed embedding expectations. No package/source change
or rerun was made to eliminate them.

The runner polled child exit before draining its PIPE output, causing backpressure
after tests/result recording finished. Only that owned collector's identified
stdout pipe was read to release it. Both segments are retained in
[collector-drained-stdout.txt](collector-drained-stdout.txt) and
[integration.stdout.txt](integration.stdout.txt), with their ordered concatenation
[integration.combined.stdout.txt](integration.combined.stdout.txt),
[stderr](integration.stderr.txt) and [COLLECTOR-NOTE.json](COLLECTOR-NOTE.json).
The child then exited0 normally; no kill, weakened guard, denied-method workaround,
installer retry or test rerun occurred. The preserved runner is a one-shot evidence
tool with this known collection limitation, not a pristine reusable harness.

## Preservation and remaining gates

Current application hashes are unchanged:

- Queue `50d1a4ebd6132f2593095874b170fa895d09c5bcd9ead9c598312cbf3314fc4c`.
- Scheduler `71183f5bf54bc36f96a62abf04a1ca73566805f0eda67cdefba5f4410a726181`.
- Server `613a3b08ae074484f0187b0234105c05b85239c45c577eee69a2b0bd8e17052c`.

All14 recorded source/test/context hashes and11 prior manifest digests remain
unchanged. No earlier passing suite, wheel-closure validation or historical7741/11
baseline was repeated. The existing separate GPT-6 Astra/high reviewer found no
blocker to this narrow recorded result, expressly retaining the warnings,
collection intervention and scope/resource limits. It ran no tests or payloads.

Full app.server/lifespan/config/voice/provider/audit singleton namespace was never
imported (recorded real app module list is empty). Authentication/CORS/resource
middleware, complete application readiness, production, real data and durable
state integration remain unqualified. No source migration, ownership daemon,
HTTP/occurrence idempotency/outbox, stronger admitted-enqueue cancellation or
executor/tool-authority wiring was implemented.

The existing [broker setup packet](../proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md)
and [missing-facts proposal](../jarvis-next-step-proposal-r1/PROPOSAL.md) remain
pending: actual restricted executor/protected host installation, credential denial
before issuance, VM164-only PVE Audit+Console grant, trusted guest identity/root
bootstrap/worker setup, explicit live activation and separate privileged Gate6K.
Observer unchanged; no VM162/163/AI, credential, system security or protected
installation access. No required operation was denied; expected synthetic denial
checks passed. Stop at this runtime milestone; keep the private materialized tree
as evidence, do not activate or import it from the ordinary host environment.
