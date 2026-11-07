"""Freeze this sprint's disposable evidence without rewriting prior packets."""
from datetime import UTC, datetime
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PACKET=Path(__file__).resolve().parent

def sha(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):result.update(block)
    return result.hexdigest()

def write(name,value):
    with (PACKET/name).open('x') as stream:stream.write(value)

def data(name,value):write(name,json.dumps(value,indent=2)+'\n')

assert not (PACKET/'SHA256SUMS').exists(),'packet already frozen'
baseline=json.loads((PACKET/'BASELINE.json').read_text())
core_id='20261106T033626577872Z';full_id='20261106T033759354138Z'
core=json.loads((PACKET/'runs'/core_id/'RUN.json').read_text())
full=json.loads((PACKET/'runs'/full_id/'RUN.json').read_text())
assert core['status']==full['status']=='PASS'
assert core['source_sha256']==full['source_sha256']
assert core['child']['tests']=={'collected':194,'failed':0,'skipped':0,'exitstatus':0}
assert full['child']['regressions']=={'collected':51,'failed':0,'skipped':0,'exitstatus':0}
assert len(full['child']['cases'])==9
for name,digest in core['source_sha256'].items():assert sha(ROOT/name)==digest,name
for run in [core_id,full_id]:
    base=PACKET/'runs'/run
    for line in (base/'INPUT-SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1);assert sha(base/'input'/name)==digest,name
    assert json.loads((base/'RUN.json').read_text())['runner_sha256']==sha(PACKET/'run_checks.py')
for name in ['test_operator_ledger.py','ledger_process_actor.py']:
    assert sha(ROOT/'tests'/name)==sha(PACKET/'runs'/core_id/'input/tests'/name)
assert sha(ROOT/'tests/test_operator_app.py')==sha(PACKET/'runs'/full_id/'input/regressions/test_operator_app.py')
for name,digest in baseline['prior_seals'].items():assert sha(ROOT/'tasks'/name/'SHA256SUMS')==digest,name

reviewed={
'app/agent/authority.py':'eac630a3db3a3cf06d48f9f1e6058db3460c9555545763a3038f03adf0e61e9c',
'app/agent/execution.py':'c26cb1b4811fc6d1a1468b08551629614deca92afb1f3759eaf1dae20a256799',
'app/agent/ledger.py':'8bc3c2ebc6b8f3a259b58348849d7817978c46bcf994a7e5680b2d3169eef880',
'app/agent/recovery.py':'aa9e0b1688d16e2ca4110a7f0203664a3f15a246e6b9a12cc7f3e912789c35fa',
'app/agent/api.py':'1afa46732b15213d7423ddd7442c248be8444381a75572c7d10cd5ce263c8a06',
'app/agent/operator_cli.py':'96073df83f4f8dc28bb75cf616181efb0aca8740f456526b0e643dcbb9f49907',
'app/cli.py':'0c4429d31b07d67b4e64ae940cdb445c9e03b392e21318ceb0abdef1609ba95c',
'app/agent/reporter.py':'90ad00beed423af7354a5e4fc9ce459524053b5fb22314a7336a7dc3ac96a072'}
for name,digest in reviewed.items():assert sha(ROOT/name)==digest,name

current=sorted(set(list(baseline['source_sha256'])+[str(p.relative_to(ROOT)) for p in (ROOT/'app').rglob('*.py')]+[str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('*.py')]+['docs/operator_recovery.md']))
changed=[name for name in current if (ROOT/name).is_file() and sha(ROOT/name)!=baseline['source_sha256'].get(name)]
patch=[]
for name in changed:
    dest=PACKET/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb') as stream:stream.write((ROOT/name).read_bytes())
    old=(PACKET/'before'/name).read_text() if (PACKET/'before'/name).exists() else ''
    patch.extend(difflib.unified_diff(old.splitlines(True),(ROOT/name).read_text().splitlines(True),fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))
write('SOURCE.patch',''.join(patch))
write('OPERATOR-DEMONSTRATION.json',(PACKET/'runs'/full_id/'output/OPERATOR-DEMONSTRATION.json').read_text())
write('EXECUTION-REGRESSION-DEMONSTRATION.json',(PACKET/'runs'/full_id/'output/DEMONSTRATION.json').read_text())

failures=[{'run':'20261106T031618245602Z','status':'INVALIDATED_SOURCE_DRIFT','observed_passed':154,'observed_failed':1,'reason':'Primary edited recovery.py while verification ran; parent hash assertion rejected binding. Stale-permit test also used two different random payload IDs and correctly failed binding first.'},
          {'run':'20261106T032939980233Z','status':'TEST_FAILURE','passed':185,'failed':1,'reason':'Capacity test expected ledger_bound_exceeded after retroactively reducing MAX_BYTES below existing signed checkpoint size; checkpoint_invalid was the correct earlier refusal. Corrected test expectation; controls were not weakened.'}]
warning_lines=(PACKET/'runs'/full_id/'stderr.txt').read_text().splitlines()
data('RESULTS.json',{'at_utc':datetime.now(UTC).isoformat(),'status':'OFFLINE_OPERATOR_RECOVERY_LEDGER_EXPORT_PASS_REAL_EXECUTION_DISABLED',
    'core':f'runs/{core_id}/RUN.json','full_app':f'runs/{full_id}/RUN.json','pytest_passed':245,'pytest_failed':0,'pytest_skipped':0,
    'core_pytest':core['child']['tests'],'application_pytest':full['child']['regressions'],'application_scenarios':full['child']['cases'],
    'native_checks':full['child']['native_execution'],'new_pytest_cases':59,'core_independent_process_cases':25,'new_independent_crash_cases':11,
    'additional_full_app_independent_crash_scenarios':1,'app_source_sha256':core['source_sha256'],'independently_reviewed_source_sha256':reviewed,
    'known_prior_failures':failures,'intermediate_passes_not_summed':True,'full_repository_suite_claimed':False,
    'warnings':{'upstream_testclient_deprecations':2,'expected_offline_startup_warning_lines':len(warning_lines),'expected_offline_startup_warnings':warning_lines},
    'new_dependencies_installed':False,'real_execution_enabled':False,'protected_history_deleted':False,'real_store_migrated':False,
    'files_changed':changed+['tasks/jarvis-operator-ledger-r1/','tasks/loop-log.md'],
    'preserved_prior_seals':baseline['prior_seals']})
data('INDEPENDENT-REVIEW.json',{'reviewer':'/root/recovery_review','role':'reviewer','mode':'read-only static review and evidence spot-check, no independent test execution',
    'verdict':'PASS_NO_UNRESOLVED_HIGH_FINDINGS','reviewed_source_sha256':reviewed,
    'final_core':core_id,'final_full_app':full_id,'changes_made_by_reviewer':False})
write('INDEPENDENT-REVIEW.md','''# Independent source review

Reviewer: `/root/recovery_review`, separate reviewer-role agent. Read-only static
review plus retained run/evidence spot-checks; no source/evidence changes and no
independent runtime or live security qualification. The eight final application
hashes are pinned in INDEPENDENT-REVIEW.json and match both final test runs.

Final verdict: PASS, no unresolved HIGH correctness/security findings. The
reviewer checked the final lexical-path/symlink hardening delta and final194/51
pass records. An initial private_directory indentation concern was retracted
by the reviewer after confirming target-only ownership checks.

Closed findings and implemented changes:

- Durable SQLite ordering alone was not tamper/rollback proof: added separately
  protected chained full-state HMAC checkpoints; no public-key signature claim.
- Exact schema probe could self-block new tables: used existing records kinds,
  retained schema version1, and refused implicit enrollment of old real stores.
- Async/rotating JSONL audit could not establish continuity: authoritative action
  receipts/events commit in SQLite and are covered by the protected state digest.
- Owner takeover and every mutation must be covered: verify before ownership
  changes; intent before COMMIT, final checkpoint before acknowledgement. Replays
  do not advance anchors. Added genesis prior-state anchor and pending resolution.
- Hard-link publication had a two-link crash window: replaced with Linux atomic
  no-replace rename, file/parent fsync, strict files and bounded staging inventory.
- Signed malformed metadata could raise raw shape errors: strict manifest,
  checkpoint, row order, event, field and identity validation now rejects it.
- Missing receipt/occurrence relationships were invisible: bounded diagnostic
  summaries expose receipt presence/state/hash/audit, occurrence bindings, owner
  generation and scheduler control, with conservative completion explanations.
- Recovery could trust result metadata too broadly: both automatic and local
  publication revalidate exact bounded pure output and synthetic terminal states.
- Global metadata could cross caller scope: operator diagnostics require the
  exact trusted local-service namespace and configured bearer authentication.
- Expired export permit could strand audit publication: preserve durable original
  authorization, keep idempotency payload stable, and support audit-only same-ID
  reconciliation of a complete anchored snapshot without regeneration.
- Archive preview could be incomplete or stale: hold one owner mutex, include
  totals/cutoff/decision hash/checkpoint, refuse >200 eligible tasks, and require
  exact task-record coverage in the verified exported snapshot.
- Schedule bulk cancellation rewrote terminal history: filter active/unresolved
  tasks; completed records remain unchanged. Tested normal and operator paths.
- Export storage could grow indefinitely: dedicated root,16-directory/64MiB caps,
  free-space refusal and incomplete-export accounting, with no cleanup/deletion.
- Lexical `..` could defeat tree separation; mkdir preceded symlink validation:
  reject traversal and symlinks before creation and test no child is created.

Accepted remaining limits:

- First schema DDL to first genesis intent crash is fail-closed/manual quarantine.
- Same-UID key compromise, check/create races or coordinated DB+anchor rollback
  are outside the local trust model; no hardware counter, key rotation or
  multi-host consensus is provided.
- Finite checkpoint/export/selection bounds require operator capacity planning;
  no protected deletion or automatic cleanup is implemented.
- Real activation needs external key/FD provisioning, private OS-separated paths,
  Linux renameat2 support, disk monitoring, recovery drills and approved policy.
- The two upstream Starlette/AnyIO warnings cannot be safely fixed within the
  retained verified dependency closure. They remain visible, not suppressed.
''')

crashes=[('bootstrap','checkpoint_intent_durable'),('mutation','checkpoint_intent_durable'),('mutation','ledger_database_committed'),('mutation','checkpoint_published'),
         ('export','export_row_written'),('export','export_data_durable'),('export','export_before_audit_publication'),('retention','checkpoint_intent_durable'),
         ('retention','ledger_database_committed'),('reconcile','before_commit'),('reconcile','ledger_database_committed')]
data('CRASH-RECOVERY.json',{'run':f'runs/{core_id}/RUN.json','test_source':'../../tests/test_operator_ledger.py','independent_helper':'../../tests/ledger_process_actor.py',
    'new_sigkill_cases':[{'mode':mode,'stage':stage,'result':'PASS'} for mode,stage in crashes],
    'outcomes':{'precommit':'authenticated prior state, rollback/no false success','postcommit':'authenticated intended state, finalize checkpoint',
                'partial_export':'rejected; no automatic regeneration','complete_export_missing_audit':'same-ID audit-only reconciliation from durable original authorization after simulated permit expiry',
                'archive_preparation':'atomic bounded decision, no history deletion','restart_reconciliation':'UNKNOWN/evidence preserved or original publication preserved; no executor redispatch'},
    'storage_failure_tests':['checkpoint final-publication ENOSPC','export manifest ENOSPC','export quota','free-space exhaustion','logical ledger bound','staging inventory bound'],
    'corruption_tests':['physical SQLite header','task/receipt/event/outbox/owner consistency','invalid identities/nested fields/timestamps','checkpoint HMAC/truncation/gap/missing anchors','older database against current external anchors','authenticated malformed manifest']})

report=f'''# JARVIS V2 sprint2: operator recovery and ledger hardening

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
| Core/process/security pytest |194|0|0|{core['elapsed_seconds']:.3f}s|{core['peak_observed_rss']} bytes|
| Actual-application regression pytest |51|0|0|included below|included below|
| Existing app scenario groups |9|0|0|{full['elapsed_seconds']:.3f}s full-app total|{full['peak_observed_rss']} bytes|
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

Final runs are `runs/{core_id}/RUN.json` and
`runs/{full_id}/RUN.json`. They bind identical93 application Python sources and
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
processes. Final core observed {core['peak_observed_files']} controlled files/{core['peak_observed_bytes']} bytes;
full app observed {full['peak_observed_files']} files/{full['peak_observed_bytes']} bytes.
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
'''
assert len(changed)==15,changed
write('REPORT.md',report)
source_names=set(core['source_sha256'])|set(current)|{'config.yaml.example'}
source_names.update(str(p.relative_to(ROOT)) for p in PACKET.glob('*.py'))
source_names.update(str(p.relative_to(ROOT)) for p in (PACKET/'tests').glob('*.py'))
write('SOURCE-SHA256SUMS',''.join(f'{sha(ROOT/name)}  {name}\n' for name in sorted(source_names) if (ROOT/name).is_file()))
data('SYMLINKS.json',[{'path':str(p.relative_to(PACKET)),'target':str(p.readlink())} for p in sorted(PACKET.rglob('*')) if p.is_symlink()])
write('SHA256SUMS',''.join(f'{sha(p)}  {p.relative_to(PACKET)}\n' for p in sorted(PACKET.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='SHA256SUMS'))
print(json.dumps({'packet':str(PACKET.relative_to(ROOT)),'changed_files':changed,'source_manifest_sha256':sha(PACKET/'SOURCE-SHA256SUMS'),'packet_sha256':sha(PACKET/'SHA256SUMS'),'pytest_passed':245},indent=2))
