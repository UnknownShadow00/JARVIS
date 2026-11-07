# JARVIS V2 sprint 5 — durable recovery decisions and protected witness renewal

Implemented functioning offline source changes in the existing application. Both
requested workflows operate on disposable SQLite databases and separately supplied
synthetic keys/identities. Verified restores and approved proposals remain inert.
UNKNOWN work is preserved without redispatch. No production service, real executor,
provider, trust key, database migration, Proxmox/VM or privileged qualification ran.

## Implementation

`app/agent/recovery_decisions.py` adds a separate bounded persistent SQLite registry
backed by externally protected append-only intent/commit evidence. Stable canonical
v4 proposal IDs preserve original authority/branch/restore identity, archive and
manifest, checkpoint generation/head, database digest and original request, task
and occurrence UUIDs. Branch/restore duplication, conflicting payloads and UUID
collisions fail closed. Initialization uses recoverable staged schema publication;
all indexed events use FULL-synchronous SQLite transactions.

Offline operator permits authenticate principal, scope, request ID, command, exact
payload, checkpoint and validity. Complete proposal verification results and later
proposal decisions have explicit operator-signed hash bindings. Every restart
independently verifies both checkpoint and operator evidence; a checkpoint-key
holder cannot fabricate approvals with a forged operator identity. PENDING,
APPROVED, REJECTED, EXPIRED and REVOKED decisions retain receipts/history. Historical
replay projects predecessor expiry at each event's admission time. Acknowledging an
old receipt does not refresh its authorization or activate anything.

Witness renewal verifies the prior externally retained reference and full trusted
checkpoint ancestry, then binds the next witness to the exact current head/key/
epoch/rollover hash. One renewal advances at most one epoch, retains prior history,
and requires checkpoint or generation progress. Compare-and-swap rejects competing
renewals and stale witness substitution. The same disposable key is retained; no
production key generation/rotation is implemented. Expired custody is visible as
WITNESS_EXPIRED, with historical integrity reported separately; fresh mutations and
configured application readiness fail closed.

`operator_cli.py` provides authenticated inherited-descriptor initialization,
publication, decisions, renewal, exact-operation reconciliation and read-only
inspection. `authority.py`, `recovery.py`, `api.py`, `runtime.py` and `reporter.py`
integrate readiness, diagnostics, status and shutdown verification/cleanup.
Readiness returns aggregate counts, not proposal identities or archive paths.
Detailed diagnostics require explicit bearer authentication even in anonymous
loopback configuration. No public approval/completion/renewal/activation endpoint
is mounted. `branch_verification.py` retains original identity arrays and archive
bindings; proposals reverify actual inert restored artifacts. `checkpoint_epochs.py`
preserves valid generation-link witnesses after their generation gains checkpoints.

[CHANGES.json](CHANGES.json) and [SOURCE.patch](SOURCE.patch) compare final source
against this sprint's actual captured starting tree, preserving prior uncommitted
work. [source/](source/) contains exact changed files; [SOURCE-SHA256.json](SOURCE-SHA256.json)
and per-run input manifests bind the source and exercised helpers. The original
application schema and real stores are not migrated.

## Demonstrated workflows

[RECOVERY-DECISIONS-DEMONSTRATION.json](RECOVERY-DECISIONS-DEMONSTRATION.json) records
actual offline CLI FD handoff and actual application ASGI lifespans:

1. Explicitly enroll a disposable source with synthetic external custody.
2. Retain held tasks, one UNKNOWN/cancel-requested operation and a real original
   schedule occurrence. Export an audited archive and reconstruct an inert restore.
3. Verify its lineage, original UUIDs and archive binding; publish a durable
   proposal through authenticated CLI with the exact verification-result digest.
4. Record an authenticated synthetic approval and durable receipt; restart the
   CLI registry and independently verify receipt HMAC/identity/payload bindings.
5. Advance held source history into exactly the next protected checkpoint epoch.
   Renew against the previous externally retained witness and inspect after restart.
6. Start the disposable application with the explicitly bound registry. Verify
   aggregate readiness, authenticated detailed diagnostics, anonymous redaction,
   absent public mutation endpoints and unchanged UNKNOWN state. Shutdown verifies
   the registry and releases source ownership. A further interrupted committed
   revocation blocks actual application startup, releases ownership and requires
   explicit original-ID CLI receipt reconciliation. Restored activation remains refused.

[CRASH-RECOVERY.json](CRASH-RECOVERY.json) additionally links 22 actual independent
SIGKILL cases: proposal, decision and renewal each at intent, pre-SQL-commit,
post-SQL-commit and final receipt; four initial schema/publication boundaries; and
two torn witness-file boundaries, plus four real hot SQLite rollback-journal cases with
uncommitted spilled/overwritten pages and valid/missing-anchor/foreign-custody/
external-rollback recovery prerequisites. Read-only inspection preserves the hot
journal; wrong-permit recovery is refused; only the exact durable authenticated
admission can authorize SQLite rollback before full history validation and retry. Exact canonical retries finish safe local
publication. Torn file content remains preserved and blocks renewal pending manual
forensic quarantine; it is never adopted as trusted evidence.

## Validation and engineering follow-through

[RESULTS.json](RESULTS.json) is the canonical final fresh-run inventory. It includes
all final counts, run IDs, source hashes, elapsed time and resource observations.
[REPRODUCE.md](REPRODUCE.md) gives exact sequential commands. Historical passing
runs are not counted again as new results; intermediate development failures and
superseded revisions are retained explicitly under `runs/`.

Final validation: **443 distinct pytest passed, 0 failed, 0 skipped** (254 core,
59 enrollment/branch, 72 new recovery-decision cases, 58 app regressions), plus
16 actual app scenario groups, 3 native probes and 10 benchmark cases. All five
final modes bind identical 100 application source hashes and the same runner.
No resource guard fired; observed peak aggregate RSS was below 116 MiB. Twenty-two
new independent SIGKILL cases are included in the 72 focused tests, not added to
the pytest total. The final app run retains two upstream warnings and 30 expected
synthetic startup warning lines.

| Mode | Final run | Result | Wall seconds |
|---|---|---:|---:|
| focused | `20261106T060908471294Z` | 72 passed | 68.353 |
| full-app | `20261106T061036551040Z` | 58 passed | 18.620 |
| benchmark | `20261106T061055269265Z` | 10 benchmark cases | 35.877 |
| core | `20261106T061131243965Z` | 254 passed | 93.683 |
| enrollment | `20261106T061305023858Z` | 59 passed | 20.026 |

Focused coverage includes concurrent proposals/decisions/renewals, duplicate/replay
and conflicting UUIDs, independently forged receipts, wrong keys, expired/revoked
or rejected decisions, absent/expired custody, stale writers, source and registry
rollback/corruption, missing anchors, incomplete histories, injected publication
ENOSPC, actual SQLite max-page disk-full rollback, read-only byte preservation,
crash reconciliation and nonactivation. Broader core, enrollment and actual app
regressions rerun the existing offline lifecycle and prior crash workflows on the
final source. The complete repository and optional provider/device suite are not
claimed as qualified.

The first focused attempt had 47 fixture setup errors because a nested fixture was
not imported; this was corrected before any passing result. An application run
then exposed an offline diagnostic adapter missing the new status method; the
adapter now explicitly reports registry unconfigured without supplied inputs.
Independent review closed restart operator-authentication and complete-result
binding gaps, first-schema crash publication, readiness disclosure, historical predecessor
expiry, full protected-prefix validation before hot-journal writable recovery and
all publication-time permit/witness/context/predecessor expiry boundaries. Expanded tests cover every closure. No failed evidence was
removed or recast as a pass. A later 69-case run retained 66 passes/3 failures
because safe zero-header journals were initially treated as unresolved hot journals.
The fix proves the SQL prefix read-only, then lets SQLite retire its own non-hot
journal during the exact original transaction. A subsequent 71-case run retained
70 passes/1 failure from an overly generic expected error code; the test now checks
the exact witness-expiry refusal. The final focused run supersedes both.

After the requested workflows functioned, follow-through work fixed generation-link
continuity, expired-witness readiness repeated-history verification costs and authenticated hot-journal rollback after
actual SQLite page spill.
[PERFORMANCE.md](PERFORMANCE.md) reports the measured bounded 32-renewal inspection
improvement from about 174 ms to 7.1 ms while retaining all integrity checks. Ten
benchmark cases include seven existing workload shapes executed anew.

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records the separate read-only static
review with nine source hash pins, closed findings and accepted limits. The reviewer
inspected earlier retained result metadata and reviewed final source; all runtime
tests and the final reported counts were produced by the primary.
The prior Cloudflare anonymous-loopback hypothesis was applicable to new recovery
history exposure and closed with aggregate readiness and ASGI tests. The separate
comprehensive audit observed during this task was still running on an earlier
snapshot; it was not edited, interrupted or represented as a current-source pass.
[SEPARATE-AUDIT-OBSERVATION.json](SEPARATE-AUDIT-OBSERVATION.json) records the scope.

All runtime work ran in the retained namespace/network-isolated bubblewrap cage
with copied read-only source/dependencies and private disposable output. Existing
resource limits were retained: 1 GiB address space/process, 768 MiB observed
aggregate RSS, 120/121 CPU seconds, 120 wall seconds, 64 MiB/file, 64 FDs, zero
core dumps, 20000 controlled files/256 MiB and at most two payload processes plus
supervisors. There was no install/download, real config/credential read or resource
limit increase. Source snapshots, prior evidence and canonical log prefix remain
preserved: 41647 predecessor files across the three read-first packets were
rehashed with zero changes. [EVIDENCE-VERIFICATION.json](EVIDENCE-VERIFICATION.json) gives exact counts.

## Remaining limits and next milestone

Separate protected external keys, latest reference, private directory/OS custody,
secure time and trusted Python remain prerequisites. HMAC is symmetric, not public-
key nonrepudiation. Coordinated rollback of all custody or hostile same-UID key/path
control is outside this local model. No cross-UID/physical power-loss/live readiness
claim is made. Two retained upstream TestClient deprecations remain visible.

Event capacity is finite (4–256), evidence/file bounds are enforced and protected
history is never pruned. Torn/foreign partial files require explicit quarantine;
expired or generation-skipping witness custody cannot be silently renewed from
local state. Receipt delivery cannot prove whether the caller received an
acknowledgment. UNKNOWN external effects remain UNKNOWN.

Recommended next authorized offline milestone: a synthetic externally custodied
expiry/quarantine recovery protocol and portable registry audit export, with
independent rollback/capacity tests and no protected deletion or automatic branch
activation. Then qualify larger bounded histories and a separately verified offline
dependency compatibility closure. Actual branch activation, production enrollment/
migration, real trust rotation and executor/deployment qualification require their
own authorization and protected custody; none is implied by this offline milestone.
