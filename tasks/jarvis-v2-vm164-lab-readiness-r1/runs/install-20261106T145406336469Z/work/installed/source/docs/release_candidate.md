# JARVIS V2 offline release candidate

The source-bound release packet is [jarvis-v2-unified-rc1](../tasks/jarvis-v2-unified-rc1/REPORT.md).
Its candidate is for controlled offline security testing. It does not authorize
production startup, real adapters, providers, credentials, database migration,
Proxmox/VM changes or privileged Gate 6K work.

Every authority HTTP route, including task read/cancel, schedules, receipts,
execution status and detailed /ready, now requires a nonblank configured bearer.
The dependency applies to independently embedded routers as well as the main app.
An empty or whitespace-only configured token refuses authority access. /health remains an unauthenticated
liveness response; it is not proof of authority admission or execution readiness.
Browser clients without a secure credential channel cannot use authority endpoints.
No anonymous compatibility fallback is provided.

Protected directory creation walks components with directory-relative no-follow
opens and creates missing directories only under already validated parent handles.
Ancestors must be owned by root or the current trusted UID and have no group/world
write permission, except root-owned sticky directories protecting existing owned
entries. Authority and checkpoint ownership retain ancestry identities and reject
replacement even when original leaf inodes were moved into a replacement ancestor.
This is not an atomic SQLite VFS. Root/same-UID compromise, coordinated external
anchor rollback and hostile filesystem implementations remain outside the contract.
Actual installed identities, ACLs/mounts and physical storage semantics require
independent operator qualification; no production custody paths were probed here.

Both WebSocket paths use text-only messages, 8 KiB byte/character bounds, 32 admitted
or pending connections per manager/process, and two-second send/close bounds.
Handler exit owns deregistration: a slow peer cannot free its count merely by
failing a broadcast. Audit failure, binary input, cancellation and disconnect clean
up registrations. Configure an upstream frame-size limit before ASGI allocation,
use one worker, and account for sequential fanout time. These application bounds
are not global distributed admission or TLS qualification.

Public example defaults select dry-run, disable boot, dictation, automatic resource
management and interaction tracing, and do not provision an API token or authority.
Defaults cannot start a real executor. Do not substitute the example for an enrolled
production configuration or assume a bearer alone authorizes real execution.
The real-tool registry, compatibility getters, confirmation, desktop dictation and
host mutation controls remain closed as documented in the Sprint 6 contract.

The candidate source archive uses sorted members, fixed metadata and content hashes;
it contains only allowlisted public source, tests, examples and documentation.
It excludes real config.yaml/.env, databases, logs, keys, model files, runtime state
and sealed evidence. Archive publication refuses replacement, and a second in-memory
rebuild must produce identical bytes. Hashes detect changes; same-UID chmod/write
control is not WORM storage or cryptographic public-key signing.

The exact minimal offline application/test environment has a 28-distribution verified
base and three additional retained, RECORD-verified wheels (NumPy, BeautifulSoup and
SoupSieve). Retained upstream metadata and wheel hashes are bound to the packet.
No host package installation or download occurred. This is not the full optional
desktop/provider deployment graph or a fresh advisory audit. The Electron lock and
Docker/action references are inventoried; installed binaries and mutable image/action
origins still require qualification before any deployment.

Use the packet's reproduction runner, which copies public examples and disposable
fixtures into a networkless, capability-free namespace with unchanged resource
limits. The canonical log and every predecessor evidence packet remain outside test
mutation authority. See the packet for current tests, exact unexecuted cases,
independent static review and the single staged live read-only proposal.

For an authenticated readiness check use `python -m app.cli ready` with protected
`JARVIS_API_TOKEN` configuration. The command fails closed without starting or
retrying services. The unified startup check also refuses whitespace-only
credentials before a bound synthetic transport can start.
