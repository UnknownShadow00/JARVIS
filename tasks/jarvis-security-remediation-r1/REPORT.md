# Security remediation and verified offline baseline

Implemented and validated the requested remediation against the active JARVIS V2 source. **168 distinct selected pytest cases passed**, plus **four integrated scenario groups** and a real isolated-loopback comparison using a separate client process. Prior audit and Sprint6 pass totals are not counted as new.

Primary source: `f4cac30259a7bf4610add2063679ae49138ee637+dirty:e5774287b42dd9ad227ec2fe281dd5e48d07ba23fff9366d79d7cc7739024069`; 398 public files, 102 application Python files. [Exact identity](SOURCE-IDENTITY.json), [source hashes](SOURCE.sha256), [manifest](final-2-manifest.json), [run results](RESULTS.json).

## Changes and observed behavior

- `/ue5` no longer leaves stale entries on binary/malformed input, disconnect, cancellation, exceptions, partial registration, audit failure or failed/slow policy close. Cleanup is synchronous and idempotent; valid text and broadcasts survive. Policy-close delivery is limited to two seconds. The 32-slot active-plus-accepting limit and slot reclamation are tested. The sibling `/ws` registration/audit gap was also closed.
- Authority routes now require a configured nonblank matching Bearer credential, even on loopback and in independently embedded routers. `/ready` has no identity exception. Missing/invalid/malformed/query-only credentials are refused. The tiny authorization dependency is async, avoiding a worker thread per check. Valid read/cancel/receipt replay behavior remains functional.
- Private storage creation now validates retained parents before descriptor-relative no-follow creation. Unsafe ancestors cause refusal before descendants appear; new nested directories are 0700 even under umask 000. Existing owner/inode/mode fences remain fail closed. This is not an atomic SQLite VFS or a hostile-owner guarantee.
- API regression callers now supply explicit synthetic credentials; the authenticated missing-store test still reaches and verifies storage refusal rather than hiding it behind 401. Public configuration/docs explain the new contract. `.dockerignore` limits build context to Dockerfile COPY inputs and excludes nested runtime/secret material.

Key implementation: [app/server.py:556](final-2/app/server.py#L556), [app/server.py:547](final-2/app/server.py#L547), [app/agent/api.py:11](final-2/app/agent/api.py#L11), [app/agent/storage_paths.py:21](final-2/app/agent/storage_paths.py#L21), [app/agent/ledger.py:57](final-2/app/agent/ledger.py#L57).

## Authority-access investigation

The pre-fix source genuinely started with explicitly admitted dummy authority state inside an unshared network namespace. A separate native HTTP process read and cancelled an operator-owned dummy task without a token:200/200. This resolves the prior *synthetic serving reachability* uncertainty; it does not prove a production or distinct-UID attack. Unprovisioned stock startup still refused `authority_unenrolled_or_missing` before creating state.

The final source served the same admitted-empty-token fixture, but task read, cancellation and `/ready` returned 401 and the task stayed pending. Configured-token requests rejected missing/wrong/malformed/query credentials; the valid-token control read and cancelled successfully. The actual lifespan and scheduler ran; only unrelated provider/hardware/background housekeeping was inert. [Before](agents/authority/artifacts/authority_socket_probe.txt), [after](agents/authority/artifacts/authority_socket_final_checked.txt).

Host is not an identity allowlist: arbitrary native Host/Origin values cannot replace a missing credential; a valid credential works regardless of those headers. Foreign-origin preflight returned 400 without allow-origin. No actual browser was run. Distinct UIDs were infeasible: only one UID is mapped, and changing to another fails with errno 22; no privileged mapping helper or host identity was created. [Qualification](agents/authority/artifacts/namespace_probe.txt).

All credential holders still share the one operator's service actor. Other non-authority assistant routes retain their local-mode behavior when the token is empty; configure a token for the whole deployment. No multi-user or hostile same-UID process isolation is claimed.

## Fresh validation

| Batch | Passed cases | Evidence |
|---|---:|---|
| HTTP, WebSocket, authentication and ancestry | 109 | [output](agents/regression/artifacts/http_regressions_updated_final.txt) |
| Execution, scheduler, receipts, CLI and lifecycle | 33 | [output](agents/regression/artifacts/execution_regressions_updated_final.txt) |
| Signed transport and offline publication | 13 | [output](agents/regression/artifacts/transport_regressions_updated_final.txt) |
| Ledger, rollover, restoration and witness renewal | 13 | [output](agents/regression/artifacts/durability_regressions_final.txt) |

The integrated replay used one shared enrolled history: API admission, signed pure transport, real nominal scheduler callbacks, durable receipts, cancellation, witness renewal, lost reply/UNKNOWN, actual FD-only operator reconciliation, restart publication hold, separately permitted publication, inert archive restore and durable nonactivating approval. The four scenario groups passed with zero real-adapter activation. [Full retained demonstration](agents/integration/artifacts/sprint6_replay_final.txt). Existing Sprint6 fixture code was copied; only scratch-root literals were adapted, with hashes in fixture-manifest.json. Background provider/hardware housekeeping was inert; authorization/storage/recovery operations were real product code.

Every execution was sequential and network-isolated, with empty allowlisted environment, readonly target/toolchain, explicit umask0077 and fixed CPU/memory/process/disk/output limits. No new packages were installed. The runtime snapshot is `final`; the final package adds only `.dockerignore`, with every runtime-tested source/test/config byte identical. Docker context was reviewed statically against [Docker's documented matching rules](https://docs.docker.com/build/concepts/context/#dockerignore-files); no image build or daemon call occurred.

## Reconciliation and evidence integrity

[RECONCILIATION.md](RECONCILIATION.md) covers the exact frozen-audit-to-current delta. All ten original excluded paths were reviewed; new auth, WS, ancestry, docs and tests are included. Twelve key lifecycle/crypto implementations and all 43 public current-broker files are byte-identical to the audit snapshot. Core decisions, receipts, witnesses and inert restoration were exercised again, not inferred from old totals.

All 2,531 prior audit files were read and hashed without modification. Source and public evidence from the completed Sprint6 packet were reviewed. A separate, concurrently assembled release-review record does not match all final source pins, so its PASS is not inherited as approval of this baseline; see related-review-pin-check.json. Original sealed reports/snapshots remain unchanged. This packet is a remediation/delta assessment, not a new independent whole-repository penetration test.

## Limits and remaining work

No production config, real database/credential, model/provider, actual desktop/audio, Proxmox/VM, NIC, guest console, power operation or privileged Gate6K qualification was used. No real executor was enabled. No commit, push or deployment was performed.

Actual different-UID/browser/ingress/TLS behavior, multiworker/global admission, pre-ASGI frame bounds, independent token/key/time/witness custody, deployment ACL/mount/SQLite/WAL/fsync/power-loss semantics and installed broker identities remain unqualified. History is still lifetime-capped and scan-based; canonical Unicode output can conservatively hit the transport frame bound and remain UNKNOWN. Actual dependency advisory/binary provenance was not re-audited or invented from source manifests. These are explicit limits, not confirmed exploits. [Security assessment](SECURITY-ASSESSMENT.md), [reproduction](REPRODUCE.md), [operator/client contract](../../docs/security_baseline.md).
