"""Package final disposable evidence; refuses to overwrite a finished packet."""
from datetime import UTC, datetime
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
PACKET=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()

def write(name,value):
    with (PACKET/name).open('x') as stream:stream.write(value)

def data(name,value):write(name,json.dumps(value,indent=2)+'\n')

assert not (PACKET/'SHA256SUMS').exists(),'packet already packaged'
core_name='20261106T022910563451Z'
full_name='20261106T023203780679Z'
core=json.loads((PACKET/'runs'/core_name/'RUN.json').read_text())
full=json.loads((PACKET/'runs'/full_name/'RUN.json').read_text())
assert core['status']==full['status']=='PASS'
assert core['source_sha256']==full['source_sha256']
assert core['runner_sha256']==full['runner_sha256']==sha(PACKET/'run_checks.py')
assert core['child']['tests']==dict(collected=140,failed=0,skipped=0,exitstatus=0)
assert full['child']['regressions']==dict(collected=46,failed=0,skipped=0,exitstatus=0)
assert len(full['child']['cases'])==7
for name,digest in core['source_sha256'].items():assert sha(ROOT/name)==digest,name
for run in [core_name,full_name]:
    base=PACKET/'runs'/run
    for line in (base/'INPUT-SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert sha(base/'input'/name)==digest,name
for name in ['test_execution_pipeline.py','execution_process_actor.py']:
    assert sha(ROOT/'tests'/name)==sha(PACKET/'runs'/core_name/'input/tests'/name)
assert sha(PACKET/'full_app_child.py')==sha(PACKET/'runs'/full_name/'input/child.py')

changed=['app/agent/admission.py','app/agent/execution.py','app/agent/api.py','app/agent/authority.py',
         'app/agent/runtime.py','app/agent/scheduler.py','app/cli.py','app/resource_manager.py','app/server.py',
         'tests/test_execution_pipeline.py','tests/execution_process_actor.py','docs/task_api.md','README.md','PROJECT_STATUS.md']
base_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
baseline={};patch=[]
for name in changed:
    original=subprocess.run(['git','show',f'HEAD:{name}'],cwd=ROOT,capture_output=True)
    old=original.stdout if original.returncode==0 else b''
    current=(ROOT/name).read_bytes()
    dest=PACKET/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb') as stream:stream.write(current)
    if original.returncode==0:
        before=PACKET/'before'/name;before.parent.mkdir(parents=True,exist_ok=True)
        with before.open('xb') as stream:stream.write(old)
    baseline[name]={'before_sha256':hashlib.sha256(old).hexdigest() if original.returncode==0 else None,'after_sha256':sha(ROOT/name)}
    patch.extend(difflib.unified_diff(old.decode().splitlines(True),current.decode().splitlines(True),fromfile='a/'+name if old else '/dev/null',tofile='b/'+name))
write('SOURCE.patch',''.join(patch))
prior_names=['jarvis-authority-readiness-r1','jarvis-client-compatibility-r1','proxmox-automation-phase3','proxmox-automation-phase3-review-r1']
preserved={name:sha(ROOT/'tasks'/name/'SHA256SUMS') for name in prior_names}
log=ROOT/'tasks/loop-log.md'
data('BASELINE.json',{'git_head':base_head,'files':baseline,'preserved_prior_seal_identities':preserved,
    'prior_log_bytes':log.stat().st_size,'prior_log_sha256':sha(log),
    'preservation_scope':'seal identities recorded; prior packet contents untouched, no new whole-packet requalification'})

write('DEMONSTRATION.json',(PACKET/'runs'/full_name/'output/DEMONSTRATION.json').read_text())
data('RESULTS.json',{'at_utc':datetime.now(UTC).isoformat(),'status':'OFFLINE_EXECUTION_INTEGRATED_REAL_EXECUTION_DISABLED',
    'core':f'runs/{core_name}/RUN.json','full_app':f'runs/{full_name}/RUN.json','pytest_passed':186,'pytest_failed':0,'pytest_skipped':0,
    'core_pytest':core['child']['tests'],'application_pytest':full['child']['regressions'],
    'full_application_scenarios':full['child']['cases'],'native_checks':full['child']['native_execution'],
    'core_independent_process_cases':14,'additional_actual_app_independent_crash_recovery_scenarios':1,
    'historical_runs_not_summed':True,'full_repository_suite_claimed':False,'real_execution_enabled':False,
    'app_source_sha256':core['source_sha256'],'runner_sha256':core['runner_sha256'],
    'dependency_manifest':'../jarvis-authority-readiness-r1/runs/20261031T090522534346Z/TARGET-SHA256SUMS',
    'dependency_manifest_sha256':sha(ROOT/'tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/TARGET-SHA256SUMS'),
    'warnings':{'pytest_dependency_deprecations':2,'startup':'four lifespan startups each report missing synthetic Piper binary/model and unserved loopback Ollama probe'},
    'files_changed':changed+['tasks/jarvis-offline-execution-r1/','tasks/loop-log.md']})

write('REVIEW.md','''# Source review of the offline execution sprint

Primary engineer static review plus source-bound runtime tests. No independent
reviewer or live security qualification is claimed for this revision.

| Finding | Implemented closure | Evidence |
|---|---|---|
| Queue had no integrated dispatcher | Explicit built-in-only registry, simulated policy, fenced claim/dispatch, evidence and publication | 60 new pipeline cases; actual app workflow |
| Lost result publication could strand work | Startup publishes existing evidence; no evidence leaves UNKNOWN | Six new SIGKILL boundaries and actual app startup after independent SIGKILL |
| Untrusted result could forge completion | Exact operation/capability/schema/output verification; no public completion route | Five hostile response cases; actual PATCH 405 |
| Public UUID could reserve predictable phase receipt | Public mutation UUID4 namespace; internal occurrence/phase UUID5 namespace | Public create/cancel/schedule reservation attempts return 422 |
| Stale authorization or ownership | Current policy, scope/capability consistency, generation, PID/file/database fencing | Revocation, inconsistent decisions, stale owner, independent owner exclusion |
| Audit or database failure before dispatch | Claim/dispatch and audit receipt commit before computation; storage ambiguity stops worker | Trigger-induced audit failure, lock contention and poisoned-owner checks |
| Sleep and stop did not know about worker | Worker stops before scheduler/storage cleanup; start after scheduler; no stopped admission | Actual app stop/sleep/wake/readiness scenarios |
| Admission could allocate unbounded JSON | Byte/chunk/deadline limits before decoding, strict bounded fields and Unicode checks | Length/chunk/slow-body cases and actual middleware auth-before-limit assertions |
| Polling and task lookup materialized full history | Active outbox polling, direct task lookup, bounded API pages and CLI pagination | Tests forbid fallback to full list materialization |

Local Python and database owners remain trusted. Registry restrictions do not
sandbox malicious same-UID code. SQL/audit/outbox transactions protect the local
contract, not future network effects. No exactly-once external effect is claimed.
''')

write('LIVE-ACTIVATION-PREREQUISITES.md','''# Exact live prerequisites — none performed or approved by this sprint

There is no real adapter or enable-real switch in this implementation. A future
real adapter needs its own source-bound protocol, authority/capability review,
external operation-ID reconciliation, failure/cancellation semantics and separate
operator authorization. Synthetic evidence cannot qualify a real effect.

The existing serial candidate remains exactly the source/archive named by
`../proxmox-automation-phase3-review-r1/RELEASE.json`: 13 source files, manifest
9e5bdd0ea59fa36021f462f4388597fefd4b65f9cee32024e86ba5d33d700301,
archive e2ab01927aeeff20d6e6a6e602aee112b3d1e99a79aaaf88d9263182e6a142f1.
Its APPROVAL-PACKET.md, INSTALLATION.md, LIVE-ACCEPTANCE.md and
STOP-AND-REVOKE.md remain the operator procedures. This packet changes none.

1. Bind observed restricted submitting and separate broker numeric UIDs/GIDs,
   protected installed source/config/units, paths and complete disabled grant.
   The actual submitting process must lack sudo/docker/lxd/root/service-management,
   ptrace, privileged capabilities/handles and broker-file access. A new account
   by itself is insufficient. Protect state/ledgers and confirm the real launch
   boundary. Perform separately approved no-transport credential-canary denial
   probes before any real issuance; retain grant/source-bound acceptance max600s.
2. Supply actual guest machine-id, worker and role UIDs/GIDs, filesystem identity,
   CA/node/address/expiry bindings, and independently trusted installed-root
   bootstrap access. These facts remain unknown here. Without trusted installed
   root, any exact maintenance media/partition/preservation/lifecycle operation
   needs separate approval. No root credential is delegated to JARVIS.
3. Only after those gates and explicit authorization may a human privately issue
   the fresh separated PVE164-only principal/token: VM.Audit plus VM.Console,
   /vms/164 only, propagate0, initially max3600s. Existing observer unchanged.
   Secret goes directly to protected broker storage; never Codex, logs or env.
4. Separately authorize installing only the pinned non-root worker/config/unit
   and exclusive ttyS0 through the trusted guest-root context. No packages, SSH,
   password unlock, guest-agent commands, NIC or privileged/mutating catalog.
5. Verify exact target: node pve, VM164 UUID faeb1db8-0df9-482d-b3e4-f6ccc1602193,
   downloads:164/vm-164-disk-0.raw, hardware serial g6k164-12821f6b54a2, 64GiB,
   serial0 socket/ttyS0, no NIC, qemu-ga disabled. Only after actual DAC, identity
   and transport gates pass, separately approve a timed read-only live acceptance
   window. Routine catalog remains identity, kernel and isolation-summary.
6. Privileged Gate6K qualification, arbitrary commands, new mutating catalog,
   real JARVIS executor wiring and production launch remain separate decisions.
   Preserve all queue/receipt/source identities and reviewed revocation procedure.

VM162, VM163, the AI server, real queue/scheduler migration, real providers and
V3 deployment remain outside scope. Stop/revoke closes accepting sockets and
active channels, revokes only the new token/ACL and, if approved, stops only the
new worker. Preserve ledgers. Token deletion alone may not close a console.
No automatic reset/reboot/media change/getty restoration or credential export.
''')

report=f'''# JARVIS V2 offline execution sprint

Implemented and verified 2026-11-05 America/Chicago (evidence UTC 2026-11-06).
This is working source and offline application integration; real execution,
production startup, real-state migration and live security qualification remain
unperformed. All state below is persistent disposable synthetic SQLite state.

## Implemented architecture and integration

`app/agent/execution.py` adds a disabled-by-default executor interface and a
registry that accepts only the exact built-in SyntheticExecutor class. There
are no tool/provider imports or real callbacks. Bounded echo, SHA256 and an
explicit synthetic failure capability return data only. SimulatedPolicy issues
scope/capability/revision-bound decisions; default policy allows echo and SHA256.
A disallowed request records a durable denied task and never dispatches.

The existing fenced Authority owns admission, outbox, audit/event and immutable
receipts. Execution evidence uses a new record kind in the existing records
table: no schema version change, alternate database or production migration.
Submission uses the same UUID4 as request_id, task_id and operation_id. Scheduled
operations use the existing deterministic occurrence UUID5 as task_id. Derived
UUID5 phase keys identify internal receipts; they are not new logical operations.
Public mutations require UUID4 so callers cannot reserve internal receipt keys.
Existing records and historical replay results retain their original identities.

The lifecycle is request → simulated authorization → pending/held outbox →
fenced claim and current policy/deadline/cancellation recheck → pure synthetic
execution → durable validated evidence → durable result/receipt publication →
status → restart reconciliation. State, audit and receipts commit in Authority
transactions. A claimed operation is never replayed into an executor invocation.
Lost acknowledgements use the original request or phase receipt ID. No exactly-once
external execution claim is made.

`runtime.py` exposes a trusted-local explicit synthetic binding hook.
`server.py` starts/stops that worker in the actual application lifespan.
`POST /execution/tasks` validates typed bounded requests. Optional synthetic
execution templates on `/schedule/jobs` survive durable schedule and occurrence
admission; the actual DateTrigger callback feeds the same worker. Plain tasks
and schedules stay held. The worker cannot be enabled through HTTP. Public result,
completion, claim and reconciliation-write endpoints do not exist.

Task status uses direct lookup and bounded pages. `execution.receipt_ids` makes
phase reconciliation discoverable. `jarvis tasks` reads pages, individual tasks
and receipts, uses configured bearer auth and exits nonzero on unavailable state.
The existing Reporter was exercised unchanged: it preserves denied, synthetic,
UNKNOWN and cancel_requested states. Resource sleep and `/stop` now stop the
worker; wake starts the explicitly bound worker after scheduler startup. Readiness
reports worker failures separately from resource ACTIVE and health.

Expiry before dispatch is timed_out with no computation. Confirmed pre-dispatch
cancellation is cancelled. Cancellation after a result keeps completion plus
cancel_requested. Dispatch exceptions, invalid responses and post-dispatch timeout
remain UNKNOWN without result evidence. Ownership takeover turns abandoned claims
UNKNOWN. Startup may publish existing evidence; absent evidence stays UNKNOWN.
It never automatically repeats an uncertain operation.

Admission is bounded at 256KiB, 1024 body chunks and five seconds before JSON
parsing. Fields and Unicode are validated. Manual synthetic admission defaults
to128 unresolved requests; the authority caps total unresolved work at1000.
The worker dispatches at most one task per20ms, reads active outbox rows, and
stops on storage/audit failure. Completed history is not materialized by polling
or single-task API lookup. Retention and large-ledger SQL costs remain future work.

## Actual demonstration

[DEMONSTRATION.json](DEMONSTRATION.json) retains actual API admission, policy denial,
current result, publication receipt, reporter and CLI status, cancellation,
restart snapshot and startup reconciliation of an independently SIGKILLed worker.
The actual `app.main`/`app.server` lifespan runs through ASGI, without a listener.
One canonical operation ID connects its admission, task, output and phase receipts.
A separately killed process has durable evidence but no published result; the
actual application startup publishes it while its executor is instrumented to
fail on any invocation. No invocation occurs. A synthetic failure is explicitly
reported as simulated_failed in focused tests, not a successful external effect.

## Final source-bound validation

| Run | Passed | Failed | Skipped | Elapsed | Aggregate RSS peak |
|---|---:|---:|---:|---:|---:|
| Core, API, scheduler, process and security pytest |140|0|0|{core['elapsed_seconds']:.3f}s|{core['peak_observed_rss']} bytes|
| Existing application regression pytest |46|0|0|part of full-app run|part of full-app run|
| Actual full-app lifespan/scenario groups |7|0|0|{full['elapsed_seconds']:.3f}s total|{full['peak_observed_rss']} bytes|
| Native Pydantic/PyYAML/psutil probes |3|0|0|part of full-app run|part of full-app run|

186 pytest cases passed in the final two runs; seven application scenario groups
and three native probes are additional checks, not extra pytest cases. The core
includes80 predecessor contract cases rerun against this implementation and60
new pipeline/security cases. Its process helper changes only the occurrence/task
identity expectation to the new canonical ID; the historical helper is untouched.
There are14 actual independent-process cases in core (eight inherited plus six
new SIGKILL boundaries) and one additional actual-app independent-crash scenario.

Final runs: `runs/{core_name}/RUN.json` and
`runs/{full_name}/RUN.json`. They bind identical {len(core['source_sha256'])} application Python
source files and the same runner. INPUT-SHA256SUMS binds each copied input,
including test helpers and child programs. SOURCE-SHA256SUMS pins the current
application, public example, tests, docs and packet source. `source/` contains
implemented changes, `before/` retains the baseline, and SOURCE.patch is reviewable.

Core stderr is empty. Full-app pytest retains two dependency deprecations
(Starlette httpx TestClient and the AnyIO BlockingPortal alias). Four synthetic
lifespan startups each retain expected missing Piper binary/model and unserved
loopback Ollama warnings. These are inspected and preserved, not suppressed.
Intermediate122/126/135/140-case runs and earlier full-app runs are retained;
their counts are not summed into final coverage. No failed pytest run occurred
in this sprint. This is not a current full-repository-suite or hardware/provider
feature qualification.

Each payload starts inside the existing verified unprivileged bubblewrap cage:
fresh namespaces, read-only copied source/dependencies, private disposable output,
zero capabilities, NoNewPrivs and IPv4/IPv6 unreachable canaries before imports.
Only the retained exact28-distribution target is reused. No install, download,
package upgrade, real configuration or credentials are needed. Bounds remain
1GiB AS/process,768MiB observed aggregate RSS,120/121s CPU,64MiB/file,64 FDs,
zero cores,120s wall,20000 controlled files/256MiB per run and at most two payload
processes. No guard was enlarged and no guard fired. These are process/fixture
bounds, not a hostile same-UID isolation or disk-quota qualification.

## Crash, reliability and security evidence

The retained independent-process fixtures exercise lifetime writer exclusion,
precommit rollback, committed admission with lost acknowledgement, atomic scheduler
occurrence/task/last_run/receipt, and interrupted simulator claims. Six new SIGKILL
cases stop after claim, after computation, before evidence commit, after evidence
commit, before publication commit and after publication. Restart leaves the first
three UNKNOWN with no retry, publishes evidence for the next two, and preserves
published completion in the last case. The actual-app crash scenario additionally
proves lifespan/worker startup performs that reconciliation without redispatch.

Focused cases cover duplicate and conflicting operations, two-thread same-key
admission, stale owner/generation checks, SQL lock contention and poisoned-instance
reopening, audit-trigger failure before dispatch, policy revocation, unauthorized
capabilities/scope, inconsistent decision fields/types, five hostile executor
responses, capacity refusal, invalid UUIDs/Unicode/deadlines/payloads, cancellation
before/after claim and after result, pre/post-dispatch timeouts, response loss,
public phase-key reservation, oversized/chunked/slow/empty-stream requests, and
bounded lookup/polling. Actual app tests cover configured bearer enforcement,
auth-before-body-limit ordering, forbidden completion, readiness, CLI failure
semantics, reporting, stop/sleep/wake, shutdown cleanup and overdue-schedule refusal.
[REVIEW.md](REVIEW.md) records the primary engineer review and resolved findings;
no independent review of this new implementation is claimed.

## Remaining limits and next engineering priorities

Real executors, broker/provider/tool effects, multiuser authorization and hostile
local Python isolation remain absent. The optional existing bearer policy is
unchanged; SERVICE_ACTOR is a trusted single-service namespace. Synthetic pure
computation evidence cannot prove an external effect. Clocks and local SQLite
ownership/storage are trusted; SIGKILL proves process recovery, not physical
power-loss or multi-host durability. UNKNOWN without evidence requires operator
investigation and cannot be cleared to success/cancellation through public routes.

The complete repository suite was not run. Optional voice, model, device, browser,
communications and live infrastructure paths are outside the retained dependency
closure and this offline qualification. No coverage percentage or live security
qualification is claimed. Two dependency deprecations remain. Overdue enabled
schedules intentionally require the existing explicit owner-quiesced recovery;
no catch-up or ledger reset is implemented. Resource ACTIVE remains a resource
state; `/ready` must be checked for scheduler/worker readiness.

Recommended next autonomous offline sprint: bounded ledger retention/export and
large-ledger index/latency measurements without erasing receipts; explicit operator
recovery tooling for overdue schedules and evidence-less UNKNOWNs; broader optional
module regressions when an approved offline dependency closure is available.
Real adapter engineering and live activation remain separately scoped work.

## Reproduction and live prerequisites

From this project root, sequentially:

```sh
python3 -I -B -S tasks/jarvis-offline-execution-r1/run_checks.py --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
python3 -I -B -S tasks/jarvis-offline-execution-r1/run_checks.py --mode full-app --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Run only the guarded workflow for application imports. Each reproduction creates
new disposable evidence and performs fresh resource/canary checks. No production
service is started. Preserved earlier runs and dependency materialization are
read-only inputs. BASELINE.json records unchanged predecessor seal identities.

[LIVE-ACTIVATION-PREREQUISITES.md](LIVE-ACTIVATION-PREREQUISITES.md) records the exact
remaining principal, protected install, public bindings, credential-canary,
VM164-only Audit+Console grant, trusted guest setup, timed acceptance and separate
Gate6K/real-adapter gates. None is authorized by this offline pass. VM164 hardware
and no-NIC status, VM162/163 and the AI server were untouched. No credentials,
permissions, real databases, services, broker code or sealed predecessor evidence
were changed. No commit, push or deployment was performed.
'''
write('REPORT.md',report)
# Pin current source, frozen inputs and all implementation/test/runner sources.
source_names=set(core['source_sha256'])|set(changed)|{'config.yaml.example'}
source_names.update(str(p.relative_to(ROOT)) for p in PACKET.glob('*.py'))
source_names.update(str(p.relative_to(ROOT)) for p in (PACKET/'tests').glob('*.py'))
write('SOURCE-SHA256SUMS',''.join(f'{sha(ROOT/name)}  {name}\n' for name in sorted(source_names)))
data('SYMLINKS.json',[{'path':str(p.relative_to(PACKET)),'target':str(p.readlink())} for p in sorted(PACKET.rglob('*')) if p.is_symlink()])
# Current packet only: no historical artifact is opened for mutation.
write('SHA256SUMS',''.join(f'{sha(p)}  {p.relative_to(PACKET)}\n' for p in sorted(PACKET.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='SHA256SUMS'))
print(json.dumps({'packet':str(PACKET.relative_to(ROOT)),'seal_sha256':sha(PACKET/'SHA256SUMS'),'report_sha256':sha(PACKET/'REPORT.md'),'source_manifest_sha256':sha(PACKET/'SOURCE-SHA256SUMS'),'pytest_passed':186,'full_app_scenarios':7},indent=2))
