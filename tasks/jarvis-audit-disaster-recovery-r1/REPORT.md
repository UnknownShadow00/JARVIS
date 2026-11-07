# JARVIS V2 offline audit disaster recovery — implementation report

Implemented and verified in the existing application. This sprint adds bounded
checkpoint generations and transactional archive reconstruction into exclusive,
inert disposable artifacts. It preserves all prior source/evidence identities,
UNKNOWN work, held outbox data and original operation UUIDs. Real execution stays
disabled. This is offline engineering evidence, not production/live qualification.

## Source and integration

[CHANGES.json](CHANGES.json) lists 18 changed/added project files: ten application
modules, three new test/helper files and five development documentation files.
[source/](source/) contains exact resulting files. [SOURCE.patch](SOURCE.patch)
is against the captured actual starting workspace in [before/](before/), rather
than git HEAD, preserving the previous uncommitted implementation. Unrelated
existing changes are untouched. [SOURCE-SHA256.json](SOURCE-SHA256.json) binds all
97 application Python sources, exercised project tests and reproduction helpers.

- `checkpoint_epochs.py` implements same-key opt-in generations, immutable
  intent/LINK/final continuity, explicit interrupted-transition recovery, policy
  binding, finite capacity and caller-supplied external ancestor references.
- `audit_attestations.py` binds source export completion to protected signed
  attestations, source attestation-marker receipts and ordered restore phases.
  Deleting previously acknowledged evidence fails source readiness.
- `archive_restore.py` verifies manifest inventory/order/content, expected hash,
  v2 lineage, supported trusted schema, source publication attestation and external
  trust context. It reconstructs through fixed SQL and one FULL-synchronous SQLite
  transaction, checks physical/logical/semantic consistency and publishes with
  Linux no-replace rename. No archive SQL is executed.
- `ledger_schema.py` centralizes the original schema without changing SQLite
  schema identity. `ledger.py` integrates generations, strict export record types,
  fresh-byte hash-validated bounded decode/HMAC caching and shared serialization.
- `authority.py` preserves fenced ownership under read failures/missing owner,
  refuses restored artifacts before sidecar creation and reports audit readiness.
  Failed duplicate guard acquisition cannot close the first valid owner's lock.
- `recovery.py`, `operator_cli.py`, `api.py` and `reporter.py` integrate attestation,
  authenticated offline CLI admission/continuation, fail-closed availability and
  accurate receipt versus current-artifact reporting. No public restore/completion
  mutation endpoint exists. Admission/dispatch/restore never implies execution.

[Operator guide](../../docs/audit_disaster_recovery.md) documents exact configuration,
FD-only key/permit inputs, phase behavior, controls and activation prerequisites.

## Demonstrated workflow

[DISASTER-DEMONSTRATION.json](DISASTER-DEMONSTRATION.json) comes from actual
`app.main`/server lifespan and authenticated ASGI routes, followed by the actual
provider-free offline operator CLI with inherited synthetic key/permit FDs:

1. Admit held work plus a synthetic UNKNOWN operation with cancellation requested.
2. Cross checkpoint generations while retaining original generation-zero bytes.
3. Produce an audited export, source completion attestation and bounded trust
   reference; stop the disposable source application.
4. Verify archive via read-only CLI. Refuse mutation without explicit commit.
5. Admit a specifically authorized restore into a separate private disposable
   parent; reconstruct/verify/publish and verify the signed artifact/receipt.
6. Confirm source DB bytes and generation-zero bytes are unchanged by restoration.
7. Restart the legitimate source, expose restore receipt phases in authenticated
   diagnostics and retain the original UNKNOWN/cancel_requested state. No replay
   of uncertain effects occurs. Public restore POST is absent.

[EXECUTION-DEMONSTRATION.json](EXECUTION-DEMONSTRATION.json) and
[OPERATOR-DEMONSTRATION.json](OPERATOR-DEMONSTRATION.json) rerun the earlier real
application synthetic execution and operator workflows on this revision.
Prepared artifact verification/reconciliation also works after removing access to
its original disposable source/archive. A restored snapshot is not a runnable
Authority branch: activation is refused before writer-sidecar creation.

## Validation

[RESULTS.json](RESULTS.json) is the canonical exact run inventory. Final source-bound
run IDs are core `20261106T045300094243Z`, full app `20261106T045456293219Z` and
benchmark `20261106T045518994872Z`. [REPRODUCE.md](REPRODUCE.md) gives exact guarded
commands and input prerequisites. Final source-bound
results: **308 pytest passed, zero failed, zero skipped** (254 core +54 application
regressions). There are 63 new sprint cases; all245 prior cases were actually
rerun. Eleven application scenario groups, three native dependency probes and four
benchmark cases passed additionally; those are not extra pytest cases. All three
final runs bind identical97 app Python hashes and the same runner. Intermediate
passes are preserved but not added to these counts. No current full-repository or
optional hardware/provider suite pass is claimed.

All runtime payloads use the retained verified unprivileged bubblewrap harness:
read-only copied source/dependencies, fresh namespaces, private disposable output,
zero capabilities, NoNewPrivs, and IPv4/IPv6 unreachable canaries before app imports.
The exact retained28-package closure was checked without installation or downloads.
Runs are sequential and retain unchanged limits: 1GiB address space/process,
768MiB aggregate observed RSS,120/121 CPU seconds,120 wall seconds,64MiB/file,
64 FDs,zero core dumps,20000 controlled files/256MiB,at most two payload processes
(plus bubblewrap supervisors). No guard fired. Per-run headroom/resource peaks and
input manifests are retained under `runs/` and summarized in RESULTS.json.

Final app stdout retains two upstream TestClient deprecations and stderr retains
21 expected synthetic startup lines. [DEPRECATIONS.md](DEPRECATIONS.md) records
current source inspection and hashes. No warning filter, patched retained package
or unsafe dependency replacement was used. A verified offline compatibility closure
is still required before those upstream warnings can safely be removed.

## Crash and security evidence

[CRASH-RECOVERY.json](CRASH-RECOVERY.json) links 15 new independent SIGKILL cases:
four rollover boundaries, nine transactional restore/publication boundaries,
export completion before attestation, and admitted rollover recovery before
continuation. Core also reruns25 earlier independent-process cases. The full-app
workflow separately reruns an actual execution-process crash/restart scenario.

Before prepared state, partial restore stays quarantined and cannot be inferred
complete. After prepared state, only the exact verified existing artifact can be
published/reconciled. A durable recovery admission survives its original permit
expiry without creating a new authorization. Missing LINK prevents automatic
rollover; unique authenticated LINK can finish. Uncertain work is never retried.
These tests exercise real process interruption and SQLite/fsync ordering; no
physical power-loss, controller-cache or hardware durability guarantee is claimed.

Negative cases include missing/reordered/duplicate/modified records, wrong HMAC
key, wrong/expired/replaced trust reference, missing/rolled-back anchors, incompatible
signed schema, legacy manifest without lineage, altered receipts, source publication
gaps, missing protected phases/attestations/recovery admission, duplicate IDs,
path/symlink/overlap and competing publication, cache-warm tampering, dual guard
ownership, concurrent access, actual disposable SQLite page bit corruption, bounded
capacity, and injected ENOSPC/EACCES at durable publication. Earlier process tests
retain storage contention/stale owner/audit failure/UNKNOWN restart coverage.
ENOSPC/EACCES are deterministic syscall-failure simulations, not filling Nexus disk.

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records a separate read-only reviewer,
findings and final ten module hashes. Runtime execution was performed by the primary
inside the cage; the reviewer performed independent static review and evidence
spot checks. No unresolved scoped correctness/security finding remains.

## Performance and fixes

[PERFORMANCE.md](PERFORMANCE.md) and [BENCHMARKS.json](BENCHMARKS.json) measure
increasing17/129/513-task state and a separate256-mutation history, with real
checkpoint/export/restore/startup/reconciliation paths. They include individual
samples, rollover overhead, protected/raw query times, logical throughput,
apparent/allocated storage and cumulative process RSS. The decode/HMAC cache uses
SHA256 of every fresh file read; no mtime-only fast path or integrity bypass exists.
The longest history shows measurable cached-verification improvement. Full state
and history scans remain the dominant protected-query cost. No production SLO or
million-row scalability claim is made.

Two failing development runs are retained. The first exposed stale inventory after
completing an interrupted LINK: verification now validates the unique pending set
and restarts complete history verification. The first benchmark attempted new
admission after a large held fixture and correctly hit max_pending=128. Creating
its uncertain operation before the synthetic historical batch fixed the workload;
no queue limit was raised. Independent review also drove strict restore phase
linkage, archive/source-independent prepared recovery, same-process serialization,
minimum-anchor generation checking, post-admission expiry continuation, durable
attestation-deletion detection and explicit v2-only restoration. Focused and broad
checks were repeated after fixes; earlier source results are not final claims.

## Remaining limits and next milestone

- Keys, local Python, external anchor custody and secure time are trusted. Local
  HMACs do not defeat compromised keys or privileged/same-UID coordinated rollback.
  No HSM, independent witness service, key rotation or multi-host consensus exists.
- All original history remains. Rollover is bounded to16 generations of at most
  9999 checkpoints and eventually refuses writes. Logical state remains bounded
  to32MiB/100000 rows; application accounting is not a physical SQLite/WAL quota.
  Partial artifacts consume quota; no automatic cleanup or protected deletion.
- Restore parents have4 directories/64MiB bounds; protected restore admissions64,
  export attestations256 and export parents16 directories/64MiB. Full-history
  verification is linear; benchmarks are small synthetic bounded experiments.
- A pre-genesis schema-to-first-intent interruption requires manual quarantine.
  Existing nonempty stores are never silently enrolled. Restored historical data
  requires a future separately authorized lineage/fork/re-anchor ceremony for
  runtime use. No current restore artifact can resume real or synthetic execution.
- Two upstream warnings remain, along with unqualified optional device/provider
  dependencies and the wider repository test inventory.

Recommended next autonomous offline milestone: implement and adversarially test
an explicit recoverable empty-store enrollment ceremony, then a separate inert
branch/re-anchor design and implementation that preserves old evidence and UNKNOWN
identities. Continue measured verification/index optimization at larger bounded
histories and establish a newly verified offline warning-free dependency closure.
Destructive retention requires independently verified continuity and separately
approved policy; it is not part of this sprint.

Exact live-activation prerequisites: independently protected execution identities,
checkpoint paths and externally custodied key/anchor/time context; approved
retention/capacity/key-rotation policy; qualified offline dependencies and broader
application tests; explicit real-store enrollment/migration and restored-branch
approval; secure operator permit provisioning; controlled deployment with
resource/storage monitoring; separate executor policy/adapter and privileged
Gate6K qualification under fresh authorization where applicable. No production
service, real executor, provider, credential, infrastructure or VM was touched,
and this report grants no activation authorization.
