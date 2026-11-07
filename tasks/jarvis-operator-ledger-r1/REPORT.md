# JARVIS V2 sprint2: operator recovery and ledger hardening

Implemented and validated offline on2026-11-05 America/Chicago (UTC evidence
2026-11-06). Functioning source, actual application integration and persistent
synthetic SQLite fixtures are delivered. Real execution, production startup,
real-state migration, credentials, infrastructure and privileged Gate6K remain
untouched. No proposal is described as implemented and no offline result is
live security qualification.

## Working capabilities

`app/agent/recovery.py` provides bounded read-only task, occurrence, schedule,
receipt, audit and outbox inspection with safe explanations. It identifies failed,
UNKNOWN, cancel_requested, held, claimed and unpublished operations. It shows
admission UUID/operation, expected and actual phase receipts, payload hashes,
audit presence, nominal occurrence links, overdue schedules, ownership/control,
inconsistent state, and recommendations. It distinguishes admission/dispatch
from completion, and never recommends automatic retry of uncertain work.

`GET /operator/diagnostics` requires an explicitly configured bearer token even
when ordinary routes permit anonymous local access. `jarvis recovery` consumes
it and returns nonzero on unavailable/inconsistent state, without service-start
or local-mutation fallback. The new provider-free `app.agent.operator_cli` can
inspect a quiesced store through SQLite mode=ro and existing locks, with a key
only through an explicit inherited descriptor. It never advances ownership,
creates a database/lock/anchor, enrolls state or resolves checkpoints. Actual
reporting and readiness expose integrity/consistency and unresolved counts.
There is no public recovery mutation, completion, export-path or grant endpoint.

`LedgerGuard` adds an opt-in separate protected HMAC checkpoint journal to the
existing Authority. Schema version1/table set remain unchanged. New records kinds
carry the mandatory guard marker, evidence and archive decisions. A guarded store
refuses opening without the key/anchor; existing unguarded stores refuse implicit
enrollment. Only disposable stores were created. The guard authenticates schema,
all ordered SQLite table rows/rowids, ownership, control, receipts/events and
outbox. Chained sequence, prior/intended digest and last event/request identity
bind each checkpoint. HMAC authentication is not a public-key signature.

The external intent commits before SQLite COMMIT. A final record commits before
success acknowledgement. Restart can resolve one terminal pending intent only
when the actual database matches authenticated prior or intended state. Invalid
HMAC, missing/gapped/truncated anchors, changed state or rolled-back DB fails
closed. Ambiguous I/O poisons the owner. Publication uses atomic no-replace Linux
rename plus file/directory fsync; traversal/symlink paths are rejected before
creation. No missing anchor is reconstructed from a nonempty database.

`RecoveryActions` supports short-lived (max300s) HMAC permits bound to principal,
scope, UUID4, command, payload hash and exact checkpoint. Supported local actions
publish only existing validated synthetic evidence, disable an exact overdue
schedule without catch-up, admit/export snapshots, and prepare archive eligibility.
They commit authoritative receipts/events in Authority. Same-ID replay preserves
the durable decision; changed payload/principal conflicts. No retry, force-complete,
delete, reset, real execution or import/restore action exists. Export audit-only
reconciliation may continue the original durable authenticated admission after
permit expiry, with exact destination and anchored complete manifest, never a
new copy. Key issuance and all real credentials remain outside this sprint.

## Export, retention and continued hardening

Exports are deterministic `state.jsonl` plus an authenticated `COMPLETE.json`
manifest with SHA256, bytes/rows, state digest, checkpoint sequence/hash and event
range/order. Verification checks exact inventory, metadata shape, table/row order,
protected historical checkpoint and matching durable admission/audit publication.
Partial exports are rejected and same-ID regeneration is refused. Keys are absent
from exported ledger state. Snapshot manifests are reproducible for identical
captured state, export ID and key; fresh runs have their own real timestamps/UUIDs.

Retention eligibility explicitly protects held, UNKNOWN, claimed, cancellation
and unresolved evidence. Plans include cutoff, totals, complete-list flag,
deterministic decision hash and checkpoint. Archive preparation refuses >200
eligible tasks and rejects snapshots missing the exact current candidate records.
It audits the bounded complete decision and performs no deletion. All tasks,
receipts, events, occurrences and outbox/history remain present even when eligible.
No cleanup process receives checkpoint access or any deletion implementation.

Beyond the primary milestone, fixed schedule stop/remove/disable rewriting
completed historical cancellation flags; both normal and operator bulk paths now
preserve terminal records. Added protected pre-dispatch structural checks and
result revalidation at automatic/manual publication. Added a dedicated export
root cap of16 directories/64MiB, free-space refusal and partial-export accounting.
Read-only/operator APIs remain bounded and fail closed. Lexical-path alias and
pre-creation symlink bugs found during final review are fixed and regression-tested.

## Demonstrations and current results

[OPERATOR-DEMONSTRATION.json](OPERATOR-DEMONSTRATION.json) contains actual
UNKNOWN-with-recorded-evidence diagnosis, authenticated recovery receipt with
unchanged operation/phase IDs and no registered executor call, real app bearer
checks, failed/UNKNOWN/cancellation explanations, readiness/reporting/CLI output,
verified snapshot/manifest, archive decision protecting uncertain work, and
quiesced CLI inspection with unchanged database/checkpoint contents.
[EXECUTION-REGRESSION-DEMONSTRATION.json](EXECUTION-REGRESSION-DEMONSTRATION.json)
retains the prior execution workflow rerun against this new implementation.

| Final source-bound run | Passed | Failed | Skipped | Elapsed | Peak aggregate RSS |
|---|---:|---:|---:|---:|---:|
| Core/process/security pytest |194|0|0|31.989s|115687424 bytes|
| Actual-application regression pytest |51|0|0|included below|included below|
| Existing app scenario groups |9|0|0|5.346s full-app total|108326912 bytes|
| Native Pydantic/PyYAML/psutil probes |3|0|0|included in full-app|included in full-app|

245 pytest cases passed in the final pair, with no failures/skips. Nine scenario
groups and three native checks are additional checks, not extra pytest cases.
There are59 new pytest cases (54 core plus five app integration);186 prior cases
were rerun against this revision rather than credited from historical evidence.
Core includes25 independent-process cases:14 inherited execution/authority cases
plus11 new real SIGKILL ledger/export/archive/reconciliation boundaries. The full
app additionally reruns independent execution-process crash startup recovery.
No current complete repository-suite, optional device/provider or live security
qualification is claimed.

Final runs are `runs/20261106T033626577872Z/RUN.json` and
`runs/20261106T033759354138Z/RUN.json`. They bind identical93 application Python sources and
the same runner. INPUT-SHA256SUMS binds copied source, tests, helpers and child
programs. Core stderr is empty. Full app preserves15 expected offline startup
warning lines (Piper binary/model and unreachable synthetic loopback Ollama)
and two upstream TestClient deprecations. These are inspected, not suppressed.
[DEPRECATIONS.md](DEPRECATIONS.md) records why adding httpx2/changing Starlette
requires a new verified offline closure rather than patching retained dependencies.

All payloads use the existing verified unprivileged bubblewrap cage with fresh
namespaces, read-only copied source/deps, private output, zero capabilities,
NoNewPrivs and IPv4/IPv6 unreachable canaries before imports. No installation,
download, real model/provider call or production listener is used. Limits remain
1GiB AS/process,768MiB observed aggregate RSS,120/121s CPU,64MiB/file,64 FDs,
zero cores,120s wall,20000 controlled files/256MiB per run and at most two payload
processes. Final core observed 1351 controlled files/15887576 bytes;
full app observed 329 files/2476150 bytes.
No limit was enlarged and no guard fired.

## Failures preserved and fixed

The first development run observed154 pass/one failure and was invalidated when
the primary edited recovery.py during verification; the runner's source identity
assertion rejected it. Its stale-permit fixture also used different random payload
IDs; binding refusal was correct. The full input/output and INVALIDATED.json are
preserved. A later185-pass/one-failure run expected the wrong error after reducing
the logical capacity constant below existing checkpoint metadata. The guard's
earlier checkpoint_invalid refusal was correct; the test now separately verifies
logical digest bounds and historical-checkpoint refusal. No guard/control was
weakened. Intermediate176/191 passes and earlier full-app run remain preserved
but are not summed into final counts. RESULTS.json records exact run identities.

## Independent review and remaining limits

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) and its JSON pin the separate
reviewer-role agent's read-only findings, closures and eight final source hashes.
Verdict: no unresolved HIGH correctness/security findings. Reviewer spot-checked
final outputs; runtime tests were run by the primary, not independently executed
by the reviewer. Same-UID trust and activation limits are explicit.

Remaining limits are intentional and material:

- Local Python, HMAC key custody and external anchor protection are trusted.
  Key compromise, same-UID check/create attacks, coordinated DB+anchor rollback,
  multi-host consensus and hardware antirollback are not covered. No key rotation.
- A crash between initial schema DDL and the first genesis intent fails closed
  and requires manual quarantine/recovery. Arbitrary-point enrollment recovery
  is not claimed. Existing nonempty stores are never auto-enrolled.
- Logical state is capped at32MiB/100000 rows, checkpoint history at9999 entries,
  staging at32 files, exports at16 dirs/64MiB and archive selection at200 tasks.
  Verification scans history/state; no production throughput benchmark or physical
  SQLite/WAL quota is claimed. Quarantined partial exports consume capacity.
- Retention is archive-copy preparation only. Protected history deletion,
  automatic cleanup, restore/import, missing-evidence UNKNOWN resolution and
  blind retry are absent. UNKNOWN without evidence remains UNKNOWN.
- The complete repository suite and optional voice/model/hardware/communication
  paths are outside this offline dependency qualification. Two upstream warnings
  remain. Resource ACTIVE is not scheduler/worker integrity readiness.
- The CLI/server operator credential is not a multiuser authorization system.
  Local mutation APIs require externally trusted permit/key provisioning and
  actual protected OS launch/storage boundaries before real deployment.

Next autonomous offline priorities: checkpoint epoch/rollover and incremental
verification performance without pruning audit evidence; explicit recoverable
empty-store enrollment ceremony; archive restore verification into a new
isolated target (never a real store); approved offline dependency closure for
warning-free TestClient compatibility and wider optional regressions. Destructive
retention needs independently verified continuity and a separately approved policy.

## Source, preservation and activation prerequisites

`source/` contains the15 implemented/test/documentation changes, SOURCE.patch is
against the actual sprint-start working tree, and `before/` preserves that tree's
public sources. The starting tree already contained uncommitted sprint1 changes;
none was reverted. SOURCE-SHA256SUMS pins current application/tests/docs/runner
sources, and SHA256SUMS pins this packet's regular artifacts with symlink metadata
separately recorded. BASELINE.json records the unchanged five predecessor seal
identities and canonical log prefix. Historical source/evidence is not overwritten.
No commit, push, deployment, package install or real database migration occurred.

Actual activation would require separate external key/FD provisioning (separate
ledger and operator keys), correct private separate checkpoint/export/database
paths, restricted OS identity/cleanup access, Linux renameat2 verification, disk
monitoring, backup/recovery drills and approved archive policy. The original
serial-broker/VM164/no-NIC/guest/grant/live/Gate6K prerequisites in the prior packet
remain unchanged and unperformed. VM162, VM163, VM164 hardware/guest, the AI server,
credentials and all real execution/providers were untouched. Real executor
registration remains prohibited.

Reproduce sequentially from this project root with the retained read-only exact28
target, using only these guarded entrypoints for application imports:

```sh
python3 -I -B -S tasks/jarvis-operator-ledger-r1/run_checks.py --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-operator-ledger-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Each call creates new timestamped disposable evidence; existing run files,
checkpoint history and dependency targets are not overwritten. Fresh resource
and isolation checks must pass before test imports.
