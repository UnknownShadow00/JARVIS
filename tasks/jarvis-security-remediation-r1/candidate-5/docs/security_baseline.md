# Offline security baseline

The remediation evidence is in
[`tasks/jarvis-security-remediation-r1/`](../tasks/jarvis-security-remediation-r1/).
It preserves the comprehensive audit and Sprint 6 evidence unchanged. The exact
tested source, failed pre-fix regressions, successful checks and limitations are
recorded separately; earlier test totals are not counted as new tests.

## Authority identity

Every authority-router endpoint requires a configured matching Bearer credential,
including task reads, cancellation, receipts, schedules, execution and `/ready`.
The router applies the check when embedded independently. Blank configuration,
missing/wrong/malformed headers and query-string credentials are refused. Trusted
enrollment or legacy admission does not authenticate an HTTP caller. Stock
unprovisioned startup still fails before creating authority state.

Use the existing private `JARVIS_API_TOKEN` launch environment or protected server
configuration to supply a credential. Do not put credentials in URLs, examples,
source, public artifacts or logs. No production configuration was changed by this
work. Clients must send the configured credential; the CLI already supports it.
The browser clients are not qualified as authenticated authority clients.

Loopback identifies an interface, not an OS user. Before the correction, an
explicitly admitted synthetic service with a genuine lifespan accepted held-task
read/cancel requests from a separate local client process without credentials.
After the correction those requests return 401 and leave the dummy task pending;
the valid-credential control still reads/cancels and replays receipts correctly.
These experiments used a network namespace, ephemeral socket and disposable state,
not a production listener or real task database.

HTTP Host is not an identity allowlist. Native clients can supply Host/Origin;
neither substitutes for the credential. Foreign-origin browser preflights are
refused by the configured CORS policy. Actual browser/local-network behavior was
not qualified, and the socket experiment used one UID. The unprivileged namespace
has only one mapped UID; changing to a second UID fails, and no host identities or
privileged mapping helpers were provisioned. No cross-UID privilege escalation is
claimed. All valid credential holders share the single operator's service actor;
this is not per-user or multi-tenant authorization.

`/health` is separate public liveness. Other non-authority assistant HTTP/WS
interfaces retain the documented local mode when the token is empty. Configure a
token for the entire deployment rather than treating that mode as user isolation.
Real tool/getter/dictation and host-control effects remain disabled independently.

## UE5 connection lifetime

`/ue5` reads ASGI frames explicitly, refuses binary/malformed input with policy
close 1008 and rejects text over 8192 UTF-8 bytes with close 1009. Registration and
connect logging are inside the cleanup scope. A synchronous `finally` removes the
manager entry after normal disconnect, malformed input, cancellation, exceptions,
partial registration, audit failure or close failure. Policy-close delivery has a
two-second timeout; the manager is cleaned even if a peer stalls that delivery.
Cleanup is idempotent and leaves other connections intact. No incoming payload,
authorization header or credential is added to these audit events.

The manager caps accepted plus accepting connections at 32 per process; cancelled
acceptance releases its reserved capacity. Tests repeat hostile sessions, check
reclaimed slots and preserve valid broadcasts. This proves the reviewed cleanup
and finite manager-state behavior, not global service availability. Multiworker
admission, upstream frame allocation, network/TLS and deployment rate limits still
need operator qualification.

## Protected storage and recovery

Ancestry checks open components relative to a retained no-follow directory
descriptor and refuse foreign/writable ancestors. Permitted root-owned sticky
temporary roots still require the subsequent protected components to pass owner
and permission checks. New private components are created relative to an already
validated parent with mode 0700, before proceeding to the next component. Unsafe
ancestors and competing symlinks are refused before descendant creation.

Authority and ledger fences verify retained ancestor identities as well as leaf
ownership; replacement poisons/refuses the writer. This is not an atomic SQLite
VFS or protection against a malicious process owner, root, privileged mounts or
unqualified filesystem/WAL semantics. Independent key/witness/reference custody,
time, real ACLs, rename/fsync and physical power-loss behavior remain assumptions.

The integrated replay exercises one shared history through authenticated admission,
pure signed transport, nominal scheduler callbacks, witness renewal, loss recovery,
offline FD-only operator reconciliation, explicit publication and inert archive
restoration. Approval/restoration never activates real execution. Same-process
synthetic HMAC IPC is not an isolated real executor or public-key nonrepudiation.

No provider, real desktop/audio, production database, infrastructure credential,
Proxmox/VM, NIC, guest console, power or privileged Gate 6K operation was used.
The separately reviewed broker remains unconnected and requires its existing
independent authorization and installed-identity qualification.
