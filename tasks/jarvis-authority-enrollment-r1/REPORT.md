# JARVIS V2 sprint 4 — authority enrollment and restored-branch verification

Implemented working offline enrollment and branch-proposal workflows in the
existing application. Normal opens never create missing authority state. The new
ceremony admits only an explicitly disposable destination under a supplied trust
reservation, produces deterministic genesis and durable receipts, and requires an
external witness on restart. Restored branches remain inert and produce read-only
proposals; actual re-anchoring and real execution are absent.

## Implemented files and behavior

[CHANGES.json](CHANGES.json) lists29 project files (seven application modules,
16 test/helper files and six documentation files). [source/](source/) contains
exact resulting files and [SOURCE.patch](SOURCE.patch) compares them with the
actual captured starting workspace in [before/](before/), preserving prior
uncommitted implementation. [SOURCE-SHA256.json](SOURCE-SHA256.json) binds current
source, exercised tests and runners. This is not a patch against git HEAD.

`enrollment.py` implements the authenticated local ceremony, dedicated external
custody, reservation/UUID/path/policy/key binding, deterministic FULL transaction,
genesis publication, signed intent/prepared/final records, explicit continuation,
physical/logical verification and external witness checks. First owner takeover
starts from a non-live generation0 sentinel and records generation1 only after
verified enrollment. Failed or suspicious preparation is retained, never erased.

`branch_verification.py` verifies original protected checkpoint history, archive
publication attestation, restore phases, inert database bytes/semantics and original
operation identities. It compares an exact externally expected current source head,
key, generation and restore identity, checks duplicate/conflicting branch IDs and
produces a reproducible proposed re-anchoring manifest. It writes no database,
checkpoint, registry, approval or sidecar. Historical snapshots are explicitly not
continuations of the current source head.

`authority.py` now refuses missing/zero/schema-only databases before bootstrap,
uses no O_CREAT/DDL on normal opening, requires enrolled-store witness/custody
verification, and rechecks evidence before subsequent admission. A lost final
receipt or uncertain identity blocks dispatch. An explicit legacy compatibility
capability is required for existing unmarked stores; no implicit legacy opening
or default key/approval lookup remains.

`operator_cli.py`, `recovery.py`, `api.py` and `reporter.py` integrate read-only
status, explicit bounded enrollment/reconciliation, branch proposal, public
unavailable errors and truthful enrollment reporting. No HTTP enrollment, restore,
completion or branch-activation mutation endpoint is mounted.

[The operator guide](../../docs/authority_enrollment.md) gives exact reservation,
permit, witness, CLI descriptor, phase and deployment contracts. README, current
status and previous development guides now point to the changed startup contract.

## Working demonstrations

[ENROLLMENT-DEMONSTRATION.json](ENROLLMENT-DEMONSTRATION.json) records actual offline
CLI calls and real `app.main`/server lifespans with synthetic configuration:

1. A disposable external fixture provisions separate private custody/checkpoint
   directories, synthetic keys and a fresh expected empty-store reservation.
2. Read-only CLI reports UNENROLLED; mutation without explicit commit is refused.
3. Authenticated CLI consumes the original enrollment UUID, creates deterministic
   genesis, publishes the exclusive target and returns a durable final witness.
4. CLI re-verifies enrollment, then the ordinary Authority constructor uses the
   explicit witness and current checkpoint history. Actual readiness and
   authenticated operator diagnostics report VERIFIED. Real execution is false.
5. Admit held work and preserve an original UNKNOWN/cancel_requested operation.
   Produce an audited archive, then stop the disposable source application.
6. Verify the archive, restore through authenticated offline CLI, and verify the
   inert branch through read-only CLI against original checkpoint lineage.
7. Emit [BRANCH-PROPOSAL.json](BRANCH-PROPOSAL.json), requiring a separate operator
   decision. The verification leaves all storage byte-for-byte unchanged.
8. Refuse Authority activation of the restored artifact. Restart the legitimate
   enrolled source and confirm UNKNOWN remains UNKNOWN with the original UUID.

Earlier actual execution, operator and disaster workflows were rerun on this same
revision; their demonstrations are retained alongside the new one. No real runtime
configuration, production database, real key, provider, listener or VM was used.

## Exact validation results

[RESULTS.json](RESULTS.json) is the canonical run inventory and resource summary.
Final unique pytest counts are **371 passed,0 failed,0 skipped**:254 historical
core regressions,59 new enrollment/branch cases and58 application regressions.
There are63 new sprint cases; all308 prior cases were rerun with explicit fixture
setup for the changed opening contract. Thirteen actual application scenario groups,
three native dependency probes and seven benchmark cases additionally passed;
these are not extra pytest cases. Intermediate passes are not summed.

| Final mode | Run ID | Pytest pass/fail/skip | Wall seconds |
|---|---|---:|---:|
| Core regressions | `20261106T052306740768Z` |254/0/0|72.871|
| Enrollment/branch | `20261106T052048890683Z` |59/0/0|17.346|
| Full application | `20261106T052023170164Z` |58/0/0|16.855|
| Benchmark | `20261106T052133594998Z` |7 benchmark cases, no pytest|29.532|

Final core/focused/application/benchmark runs bind identical99 application Python
hashes and the same runner. Exact run IDs, input manifests, stdout/stderr and child
boundaries are retained under `runs/`. [REPRODUCE.md](REPRODUCE.md) gives exact
commands. Broad regressions exercise selected supported offline application
components; no complete repository, optional device/provider or live qualification
pass is claimed.

Each runtime payload ran in the retained verified unprivileged bubblewrap cage:
fresh namespaces, read-only copied source/dependencies, private disposable output,
zero capabilities, NoNewPrivs and unreachable IPv4/IPv6 canaries before imports.
The retained exact28-package closure was verified without install/download.
Tests ran sequentially. Limits remained1GiB address space/process,768MiB observed
aggregate RSS,120/121 CPU seconds,120 wall seconds,64MiB/file,64 FDs,zero core
dumps,20000 controlled files/256MiB and at most two payload processes (plus bwrap
supervisors). Core and new focused cases were separated to preserve headroom under
the wall limit; no limit was increased and no guard fired.

Two upstream TestClient deprecations remain visible, with27 expected synthetic
startup warning lines. [DEPRECATIONS.md](DEPRECATIONS.md) records read-only source/
hash reinspection. No warning suppression, dependency patch or unsafe replacement
was used. A new verified offline compatibility closure remains future work.

## Failure, recovery and security coverage

[CRASH-RECOVERY.json](CRASH-RECOVERY.json) links13 new independent SIGKILL cases:
intent, stage, database creation, pre-commit, committed seed, genesis intent,
genesis publication, prepared, pre-publication, target publication, final, and
checkpoint before/after publication. The live parent also attempts competing
checkpoint ownership while a child enrollment is paused. Core reruns40 earlier
independent-process cases; actual application startup separately reruns an
execution-process crash. SIGKILL demonstrates process interruption and fsync/SQLite
recovery ordering, not physical power-loss durability.

Intent-only/empty-stage reconciliation can complete the same admitted ceremony.
Exact committed seed state can finish authenticated genesis. Unknown partial SQL
is preserved for manual quarantine rather than rebuilt. Prepared state can publish
only the exact verified target, and published state can finalize only its original
receipt. FINAL plus missing/substituted DB never recreates anything. Continuation
uses the original durable admission, not a fresh authorization after expiry.

Negative tests cover default missing-store refusal, zero/schema-only state,
existing destinations/history, malformed actors, wrong permit/scope/identity,
incorrect external anchor/policy, consumed enrollment, missing witness/custody
phases, modified marker/receipt/database, wrong HMAC key, physical genesis rewrite,
symlink substitution, stale/copy/duplicate branches, request-ID collisions, wrong
key/generation/restore/digest/context, activation requests, bounded external registry,
and a verify/reopen replacement race. UNKNOWN and cancellation uncertainty survive
archive restoration/proposal/startup. Injected ENOSPC/EACCES preserve prepared
evidence and recover after the fault; the shared host disk was never filled.

API tests prove missing identity/evidence returns unavailable before admission and
does not add a task receipt. Default runtime missing-store access creates no path.
Reporter labels VERIFIED enrollment without describing execution as completed.

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records a separate read-only security
review, findings, closures and final seven module hashes. Runtime tests were run
by the primary in the cage; the reviewer performed static review and evidence
spot checks, not independent live qualification.

## Discovered defects and engineering follow-through

The first32 focused cases passed. Expanding the real application path exposed a
strict-owner-event schema regression:47 cases then reported22 passes,11 failures
and14 setup errors. The consistency checker now strictly accepts the new VERIFIED
and LEGACY_APPROVED subobjects while preserving historical four-field events.

Independent review also closed a schema-only legacy bypass, missing physical
genesis binding, verify/reopen branch race and identity-collision checks. Normal
unguarded/unmarked opening now requires an explicit trusted-local compatibility
capability and reports its limited provenance honestly. Protected compatibility
admission binds the current verified head rather than the empty checkpoint.

The first broad301-case run retained250 passes/51 failures while migrating old
fixtures: subprocess helper lookup, class-method monkeypatch binding, old error
expectations and fresh legacy approvals before checkpoint reconciliation. These
fixtures now explicitly seed only known synthetic legacy data and obtain an exact
post-reconciliation capability. No product bootstrap bypass/constructor override
was introduced to pass tests. A later301-case run passed, then the final split
reran254 core cases plus the expanded59 cases with full input identity evidence.

The first58-case application run retained45 passes/13 failures because old tests
still relied on default implicit startup. Explicit disposable bindings fixed those
fixtures; all58 and all13 real application scenarios subsequently passed. Every
failure/input remains preserved and is not described as a final success.

## Performance

[PERFORMANCE.md](PERFORMANCE.md), [ENROLLMENT-BENCHMARKS.json](ENROLLMENT-BENCHMARKS.json)
and [BENCHMARKS.json](BENCHMARKS.json) retain costs for three real enrollment cases
with0/16/32 held tasks plus one UNKNOWN, and four retained growing-state/history
cases up to513 tasks/256 control mutations. They measure enrollment, initial
checkpoint/verification, first ownership, export/restore, branch verification,
restart, storage and memory. Every case confirms no uncertain re-execution.

No speculative optimization weakened integrity. The earlier fresh-byte hash cache
remains bounded and full state/history scans remain dominant. Enrollment costs
are individual warmed measurements, not statistical tail latencies or production
SLOs. Physical storage/WAL quotas, million-row scale and unbounded retention are
not qualified.

## Remaining limits and authorization requirements

The external reservation, final witness, latest checkpoint reference, registry,
HMAC/permit keys, local Python and secure time remain trusted. Local signed files
do not defeat privileged/same-UID key compromise or coordinated rollback. A caller
can manufacture its own in-process verifier; the legacy tuple is a trusted-local
compatibility capability, not independently authenticated legacy provenance.
There is no automatic verifier trust root, key generation or provisioning path.

A genesis witness proves a minimum ancestor, not that no later history existed.
Use externally custodied newer minimum/current references for later rollback and
branch staleness checks. The stateless branch verifier detects duplicates only
against its supplied trusted registry and exact bound target; it does not maintain
a globally fresh registry or grant operator approval. Proposals are hashed reports,
not signed re-anchoring authorization.

Partial unknown SQL/staging remains quarantined and consumes capacity. Arbitrary
damaged-genesis repair is not implemented. Existing finite checkpoint, snapshot,
export and restore bounds/no-deletion policy remain. No key rotation, hardware
anchor, multi-host consensus or restored-branch activation was implemented.

Default startup now intentionally fails closed without trusted provisioning/binding;
passing synthetic lifespans is not general production startup readiness. Actual
live activation requires fresh authorization, protected OS identities/directories
and external custody/time, real operator/permit provisioning, approved enrollment/
legacy/capacity/retention policy, qualified dependency closure and broader tests,
explicit deployment review, and separately authorized real migration/branch
re-anchoring/executor qualification as applicable. No production genesis reset,
real authority re-anchoring, real store migration, credential change, provider call,
Proxmox/VM action, privileged Gate6K run, V3 deployment or production startup occurred.

Recommended next autonomous offline sprint: a durable externally witnessed branch
proposal/decision registry with replay/conflict testing and explicit signed operator
decisions that remain non-activating; then independently protected witness renewal
and key-transition protocols. Continue larger bounded reconciliation/performance
tests and a newly verified warning-free offline dependency closure. Actual branch
activation and production trust changes still require separate authorization.
