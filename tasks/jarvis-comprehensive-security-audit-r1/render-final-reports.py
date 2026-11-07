"""Trusted parent report renderer; uses independently finalized records only."""
from pathlib import Path
import json,collections,hashlib,re
O=Path(__file__).resolve().parent
def get(n):return json.loads((O/n).read_text())
def put(n,t):(O/n).write_text((t.rstrip() if isinstance(t,str) else json.dumps(t,indent=2))+'\n')
records=get('findings.json');ledger=get('coverage-ledger.json');meta=get('run-metadata.json');manifest=get('source-manifest-packaged.json');checks=get('record-verification.json')
leads=[r for r in records if r['verdict']=='needs_validation'];rejected=[r for r in records if r['verdict']=='rejected'];confirmed=[r for r in records if r['verdict']=='confirmed'];states=collections.Counter(u['status'] for u in ledger)
assert not confirmed,'Confirmed finding requires an expanded reproduction section before rendering'
assert all(any(c['fingerprint']==r['fingerprint'] and c['decision']=='verified' and c['source_snapshot']=='snapshot-packaged' for c in checks) for r in leads)
assert all(u['status'] not in ['planned','in_progress','deferred'] for u in ledger)
rev=meta['final_source_revision_id'];cutoff=meta['packaged_source']['capture_utc']
def link(p,n):
 target=p.removeprefix('tasks/jarvis-comprehensive-security-audit-r1/') if p.startswith('tasks/jarvis-comprehensive-security-audit-r1/') else 'snapshot-packaged/'+p
 return f'[{p}:{n}]({target}#L{n})'
def trace(xs):return '\n'.join(f"{i}. {link(x['file'],x['line'])} ({x['scope']}): {x['description']}" for i,x in enumerate(xs,1))
def evidence(xs):return '\n'.join('- '+link(x['file'],x['line'])+': '+x['description'] for x in xs)

# Earlier reproduced mechanics remain evidence, with their original revisions.
historical=get('reports-before-latest/implementation-defects.json')
for d in historical:
 d['current_status']='gated' if d['id'] in ['D1','D2'] else 'fixed-at-reviewed-call-site'
 d['resolution']='Server/registry/getters refuse real effects and confirmation route is removed.' if d['id'] in ['D1','D2'] else 'Final packaged source adds native child leases, bounded/cancellable VAD, validated/finally-cleaned /ws and authenticated CLI POST with explicit offline/failure policy; see eight selected packaged safety checks. D5 /ws is fixed; /ue5 sibling cleanup is separately retained as D7.'
put('historical-defects.json',historical)
defect=dict(id='D7',title='Binary frame leaves a stale /ue5 connection entry',priority='P2',source_snapshot='snapshot-packaged',source=['app/server.py:529','app/server.py:540','app/server.py:541','app/comms/ue5_bridge.py:23'],artifact='agents/hunt-packaged-safety/artifacts/ue5_binary_cleanup.txt',harness='agents/hunt-packaged-safety/scratch/ue5_binary_cleanup.py',observed='One credentialed in-memory /ue5 session sent the single binary byte 0x78. receive_text raised KeyError and the manager retained one entry after session exit. A normal disconnect retained zero. No lifespan, real socket, browser, other UID, connection flood or shared-service outage was tested.',boundary='Per-session input/cleanup reliability defect. No unauthorized data access, authentication bypass, privilege gain or shared-service denial was demonstrated. Later broadcasts can remove dead connections.',fix='Validate the accepted frame type and always disconnect in finally, including unexpected exceptions and cancellation. Apply explicit connection/send/size limits.',regression='Send one binary frame and cancel one accepted session; assert a defined close/error and no retained entry after each.')
put('implementation-defects.json',[defect])
put('IMPLEMENTATION-DEFECTS.md','''# Current implementation defect and historical resolutions

No vulnerability severity is assigned to these mechanics. P2 is repair order. The final captured source fixes or gates all six earlier reproduced call-site defects; it retains one sibling cleanup defect.

## D7 — Binary frame leaves a stale /ue5 entry (P2)

Source: '''+', '.join(link(p.split(':')[0],int(p.split(':')[1])) for p in defect['source'])+'''.

Observed: '''+defect['observed']+'''

Scope: '''+defect['boundary']+'''

Latest [retained result](agents/hunt-packaged-safety/artifacts/ue5_binary_cleanup.txt). Reproduce from this audit directory under the bounded runner:

```sh
cp agents/hunt-packaged-safety/scratch/ue5_binary_cleanup.py agents/hunt-packaged-safety/scratch/repro_ue5_1.py
python3 sandbox-runner.py hunt-packaged-safety agents/hunt-packaged-safety/scratch/repro_ue5_1.py snapshot-packaged
```

Use a fresh basename for every replay; exclusive promotion refuses overwrite. The fixture clears only its isolated in-memory manager and uses a dummy token.

Fix: '''+defect['fix']+'''

Regression: '''+defect['regression']+'''

## Historical observations — not current exposed effects

| ID | Earlier reproduced mechanics | Final captured disposition |
|---|---|---|
| D1 | Confirmation invokes dummy effect after emergency stop | Gated: confirmation route removed; every registry/server invocation refuses real effects |
| D2 | Narration failure duplicates a note append | Gated: first tool effect is refused in normal and streaming/fallback dispatch |
| D3 | Generic argv marker selects an unrelated same-UID child for termination | Fixed: signals require in-process child lease plus PID/creation-time/executable/cwd/ppid checks |
| D4 | Continuous positive speech exceeds configured recording cap | Fixed: frame/deadline/cancel guards apply before every branch; callback/wake queues are bounded |
| D5 | Malformed /ws messages leave manager entries | Fixed for /ws: input shape/size validation and finally cleanup; /ue5 D7 remains separate |
| D6 | CLI POST omits configured credential and HTTP failures trigger local fallback | Fixed: Bearer is sent; HTTP/ambiguous outcomes refuse fallback; local control requires explicit offline intent |

Original native inputs, conditions, artifacts and precise fixes are preserved in [historical-defects.json](historical-defects.json) and [superseded report](reports-before-latest/IMPLEMENTATION-DEFECTS.md). These records describe their exact older captures. Latest controls have [six-group denial evidence](agents/hunt-latest-safety/artifacts/latest_safety.txt) and [eight packaged regression cases](agents/hunt-packaged-safety/artifacts/packaged_safety_tests.txt). No application fix was made by this audit; the concurrent implementation changed these files and was independently re-reviewed.
''')

selections=[('snapshot','agents/hunt-ledger/artifacts/ledger_controls.txt'),('snapshot','agents/hunt-recovery/artifacts/recovery-controls.txt'),('snapshot','agents/hunt-infra/artifacts/infra-controls.txt'),('snapshot-current','agents/parent-current/artifacts/current-regressions.txt'),('snapshot-current','agents/parent-registry/artifacts/registry-controls.txt'),('snapshot-final','agents/hunt-final-registry/artifacts/proposed-tests.txt'),('snapshot-final','agents/parent-final/artifacts/hot-journal-controls.txt'),('snapshot-expanded','agents/hunt-infra-current-chain/artifacts/current_chain_controls.txt'),('snapshot-expanded','agents/hunt-infra-current-files/artifacts/current-file-controls.txt'),('snapshot-latest','agents/hunt-latest-transport/artifacts/transport-selected-tests.txt'),('snapshot-packaged','agents/hunt-packaged-transport/artifacts/packaged_transport_tests.txt'),('snapshot-packaged','agents/hunt-packaged-safety/artifacts/packaged_safety_tests.txt')]
validation=[]
for snap,name in selections:
 raw=(O/name).read_text();m=re.search(r'(\d+) passed',raw) or re.search(r'Ran (\d+) tests?',raw);assert m,name
 validation.append(dict(source_snapshot=snap,case_count=int(m.group(1)),artifact=name,sha256=hashlib.sha256((O/name).read_bytes()).hexdigest(),result='passed'))
total=sum(x['case_count'] for x in validation)
put('validation-summary.json',dict(regression_invocations=validation,total_selected_cases_across_captures=total,interpretation='Separate revision-tagged bounded checks, not a single full current-suite baseline. Additional microfixtures prove or refute precise mechanics.',current_microfixtures=['agents/verify-latest-auth/artifacts/verify_auth_packaged.txt',defect['artifact']],execution='Parent-only bwrap namespace isolation/no external network, readonly source/toolchain, empty allowlisted environment, scratch32MiB, AS512MiB, CPU10s, NPROC64, FD96, file2MiB, wall25s, stdout256KiB. Only bounded predeclared files promoted through retained no-follow directory descriptors after all sandbox processes terminate.',toolchain_inventory='agents/parent-final/artifacts/toolchain-inventory.txt',toolchain_limit='Preexisting audit dependencies/Python3.14.4 are not installed deployment evidence. Early stdlib checks used Python3.11. No packages installed.',qualification_limits='No production/provider/real DB/credential/desktop/audio/PVE/VM/privileged Gate6K, physical power-loss or shared availability stress qualification.'))

nd='# Needs validation\n\nOnly independently verified source-grounded conditional leads appear here. No severity is assigned.\n'
for r in leads:
 nd+='\n## '+r['title']+'\n\nFingerprint: `'+r['fingerprint']+'`.\n\n'+r['description']+'\n\nClaimed root cause: '+r['claimed_root_cause']+'\n\n### Current trace\n\n'+trace(r['trace'])+'\n\n### Verified evidence\n\n'+evidence(r['evidence'])+'\n\n### Decisive blockers\n\n'+'\n'.join('- '+x for x in r['blockers'])+'\n\n### Safe resolution plans\n\n'+'\n\n'.join(k.capitalize()+': '+v for k,v in r['validation_plan'].items())+'\n'
put('NEEDS-VALIDATION.md',nd)
put('FINDINGS-DETAIL.md','# Confirmed security finding details\n\nNo confirmed exploitable vulnerability met the evidence gate. No severity or medium/high/critical reproduction is claimed. [Conditional authority access](NEEDS-VALIDATION.md) and [current implementation cleanup defect](IMPLEMENTATION-DEFECTS.md) remain distinct. This result does not certify deployment security or resolve external assurance limits.\n')

hyp='''# Investigated hypotheses and false-positive checks

## A — Anonymous loopback authority access

**Needs validation; no severity.** Empty-token ordinary mounted task routes use the service actor without a credential. The final synthetic bound-authority fixture read/cancelled one dummy task; configured credentials and diagnostics rejected absent credentials. Genuine stock lifespan refused missing state before database creation because the opener supplies no ledger/enrollment witness or explicit legacy approval. An actual admitted anonymous serving mode and an excluded reachable local UID remain unresolved. Browser exploitation additionally requires concrete request, SOP/local-network and Host/DNS/ingress facts.

Configuration validates bind host rather than incoming Host. Arbitrary native Host/Origin and CORS behavior do not establish a browser exploit. Both WebSocket paths independently reject disallowed present Origin. New transport-permit submission independently requires configured Bearer authentication; configured transport startup requires a token, /stop rejects empty token and host resource mutation HTTP routes deny403. These controls do not wrap ordinary task reads/cancellation. Complete current trace/blockers/plans: [NEEDS-VALIDATION.md](NEEDS-VALIDATION.md). [Latest fixture](agents/verify-latest-auth/artifacts/verify_auth_packaged.txt) used no socket/browser/otherUID.

## B — Filesystem ancestor replacement

Application protected-storage helpers use absolute paths, symlink checks and leaf no-follow/type/UID/mode/link validation, without pinning every ancestor or validating each ancestor's owner/write permissions. Another OS principal must first possess relevant ancestor replacement authority; trusted same-UID process/key control is insufficient evidence of privilege gain.

The deterministic same-UID fixture swapped an ancestor at the final writable SQLite connection and restored the expected pathname before later fences. SQLite refused construction with `OperationalError: attempt to write a readonly database`; no invented task was accepted. This exact chain was repeated against the later capture: [initial artifact](agents/hunt-ledger/artifacts/ancestor_connection.txt), [repeat](agents/parent-current/artifacts/ancestor-current.txt). Relevant storage helpers remain source-identical in the final capture. This refutes the tested chain, not every possible race.

Metadata-only repository observations found root-owned755 `/` and `/opt`, UID1000-owned755 `/opt/apps`, and UID1000-owned750 workspace/projects/JARVIS ancestors without group/world write bits. Actual configured custody/checkpoint/archive ancestors, ACL/mount/sticky/link controls and a rename-capable different UID were not qualified. No different-UID redirect or unauthorized acceptance was demonstrated; no severity is assigned. Three ledger units retain external assurance blockers.

Current broker successor securefs instead walks components through directory-relative no-follow ownership checks. Those controls cannot be transplanted to application absolute-path helpers. Prefer protected non-writable ancestors, retained verified directory descriptors for supported leaf operations, and deliberate actual SQLite connection/WAL authentication/fencing. A generic leaf no-follow flag is not an ancestor guarantee.

## Screenshot temporary output

**Rejected as a current application finding.** Capture retains a fixed temporary child and predictable PNG pathname, but server/registry/getters deny real effects; native voice enters the same refused pipeline. Full-source searches found no active independent vision/YOLO/verifier capture caller. The readiness utility forces dry-run. Manually introducing a trusted capture caller would supply the missing execution path rather than reproduce a current lower-trust application boundary. The complete rejected record is retained in findings.json. This does not certify the dormant helper safe for future reuse.

The public [MSS v9.0.1 writer](https://github.com/BoboTiG/python-mss/blob/v9.0.1/src/mss/tools.py) was inspected statically and uses ordinary pathname output. This is one upstream version, not an installed-runtime claim. mss was absent in the audit toolchain; no desktop capture or separate-UID file effect was attempted.

## Other corrected or rejected escalations

- All six earlier reproduced call-site effects are gated or fixed in the final capture; their older artifacts remain revision-tagged. /ue5 has one separate cleanup defect, without demonstrated shared-service denial.
- Same-UID process selection and finite VAD/WS mechanics were not upgraded to OS privilege escalation or proven shared outages.
- Synthetic transport remains a same-process unnamed socketpair with pure fixed endpoints. Peer PID/UID checks do not establish a restricted-identity real executor. New process actor code is a crash-test fixture, not transport isolation.
- Electron has an exact integrity-bearing source lock. Earlier blanket no-lock wording was corrected; installed binaries/Python resolution/advisory status remain unknown.
- Electron IPC forwarding has only hide/show privileged handlers; no arbitrary privileged action was established.
- Early incomplete recovery integration observations were resolved in later source, not retained as current findings.
- Historical reports, suite totals, public examples and dummy keys do not establish active vulnerabilities or leaked credentials.
'''
put('HYPOTHESES-AND-FALSE-POSITIVES.md',hyp)

dep=(O/'reports-before-latest/DEPENDENCY-AND-CONFIGURATION-RISKS.md').read_text()
dep='\n'.join('- Current registry/dictation refuse real effects regardless of legacy approval settings. Direct trusted native helper imports remain separate; future adapters need explicit validated authorization.' if line.startswith('- Validate security-control values') else line for line in dep.splitlines())
dep+='\n\nFinal integration notes: configured transport requires a token; request/response/operator/ledger keys must be independent. The socketpair is same-process synthetic scope. Preflight canonical encoded byte size: Unicode echo can exceed the response frame cap after escaping, leaving conservative UNKNOWN with durable evidence. Some legacy success tests remain stale despite the reviewed fixes; do not treat an old suite total as a current baseline. CLI wake --offline can start a server before encountering the intentionally denied resource endpoint: align/document the offline workflow without weakening the HTTP denial. No full suite was run.\n'
dep+='\n## Source evidence\n\n| Observation | Frozen source |\n|---|---|\n| Python lower bounds | [core requirements](snapshot-packaged/requirements-core.txt), [desktop requirements](snapshot-packaged/requirements-desktop.txt) |\n| Electron exact resolution/integrity | [package-lock.json](snapshot-packaged/frontend/electron/package-lock.json), [inventory](dependency-inventory.json) |\n| Image identity/runtime/COPY | [Dockerfile](snapshot-packaged/Dockerfile#L1) |\n| Host publication versus backend bind | [Compose](snapshot-packaged/docker-compose.yml#L44) |\n| Mutable CI actions | [workflow](snapshot-packaged/.github/workflows/tests.yml#L13) |\n| Voice binary/model downloads | [Piper installer](snapshot-packaged/scripts/install_piper.py#L14), [model installer](snapshot-packaged/scripts/install.py#L15) |\n| Broker source/release/qualification policy | [successor README](snapshot-packaged/tasks/proxmox-automation-phase3-review-r1/README.md), [source hash manifest](snapshot-packaged/tasks/proxmox-automation-phase3-review-r1/src/SOURCE-SHA256SUMS), [live acceptance requirements](snapshot-packaged/tasks/proxmox-automation-phase3-review-r1/LIVE-ACCEPTANCE.md) |\n\nThese links substantiate source observations; they do not establish installed versions, active settings or exploitability.\n'
put('DEPENDENCY-AND-CONFIGURATION-RISKS.md',dep)

# Preserve the full 18-area mapping; update its current source semantics.
cv=(O/'reports-before-latest/COVERAGE-AND-LIMITATIONS.md').read_text()
start=cv.index('| Required area');end=cv.index('## Practical limits')
table=cv[start:end].replace('legacy tools separately scoped','server/registry real effects refused; transport same-process pure synthetic').replace('screenshot lead conditional','screenshot current application path rejected').replace('routes and native screenshot boundary','routes and dormant screenshot helper boundary').replace('scope and authentication; CLI POST defect','scope and authentication; final POST/fallback fixes verified').replace('authority; delta-runtime | Server actor','authority; delta-runtime; packaged-transport | Server actor').replace('final-registry; delta-runtime | Final current registry','final-registry; delta-runtime; packaged-transport | Final current registry')
put('COVERAGE-AND-LIMITATIONS.md','# Coverage and limitations\n\n'+str(len(ledger))+' deterministic units: '+', '.join(f'{v} {k}' for k,v in sorted(states.items()))+'. Two candidate-status units link the one independently disposed needs-validation record; these are not unvalidated candidates. Three blocked units retain external filesystem/custody/deployment-dependency assurance facts. Screenshot unit is covered with rejected disposition. No planned/in-progress/deferred source units remain.\n\nSix hunting waves, independent post-wave critics and a distinct final-clean critic reviewed active source and every captured delta. No compatible external prior structured run existed; historical reports did not suppress current review.\n\n'+table+'''## Practical limits

390 hashed public source/test/doc/manifest files include all maintained app/client/script/evaluator code, root task utilities and the current documented broker successor. Coverage is by entrypoint/boundary/attack class, not a claim every line/test executed. Trivial initializers/reexports add no privileged action; sealed evidence and binaries are excluded from active-code conclusions.

The final bounded pass reviews the 16-path packaged delta, including transport/authority/recovery/offline CLI and process/VAD/WS/CLI fixes. Publication of operator-reconciled transport evidence now requires separate explicit authority; live state is rechecked before report commit. Process actor tests do not add an external executor identity. Eight safety and eight transport cases passed in this capture. Across all snapshots '''+str(total)+''' selected regression cases passed, plus precise microfixtures; these are separate revision-tagged checks, not a full current suite. Python3.14 audit dependencies differ from unqualified Docker3.11/native deployment stacks.

No production configuration, real database/credential, installed credential-bearing observer helper, model/provider, desktop/audio, guest/PVE endpoint, ACL/token/NIC/console/power action or privileged Gate6K qualification was used. No installation, heavy or concurrent target test, shared availability stress or physical power-loss qualification occurred.

Captures use stable per-file reads and immediate rehash, not atomic cross-file snapshots. Exact cutoff is in run-metadata.json. source-stability-packaged.json records any subsequent drift. Source edited after that cutoff is explicitly unreviewed and requires a new delta pass; the report does not silently extend its conclusions to later bytes.

Actual admitted anonymous startup, excluded local UID/browser reachability, different-UID ancestry/ACL/mount/namespace controls, installed dependency/advisory graph, binary provenance, broker role/unit/TTY/guest/API/custody enforcement and trustworthy time remain external facts, neither assumed present nor absent. This is a completed source assessment with explicit assurance limits, not deployment certification.
''')

fixes='''# Prioritized fixes and assurance work

No confirmed vulnerability severity is assigned. P1/P2 schedule source or conditional assurance work, not vulnerability severity.

| Priority / prerequisite | Precise action | Acceptance invariant |
|---|---|---|
| P1 before admitted multi-principal use | Require configured credentials for privileged task routes even on loopback; provide authenticated client transport and justified Host/unsafe-origin policy. | An excluded local UID/browser cannot inherit service-actor authority. First establish the actual admitted serving/principal facts in A. |
| P2 — current D7 | Validate /ue5 frame type and place disconnect in finally; bound sessions, frame sizes and sends. | One binary frame or cancellation leaves no manager entry and no shared resource leak. |
| P2 — protected storage assurance | Require trusted non-writable ancestors; use retained verified directory descriptors for leaf operations and deliberate SQLite/WAL connection fencing. | Another UID cannot redirect protected operations under the documented filesystem contract. B remains unconfirmed. |
| P2 — resource hardening | Bound chat/sensor/memory bodies, total history/node cardinality, scans and streamed subprocess/HTTP output; plan finite ledger capacity without trust reset. | Limits apply before expensive allocation, preserving UNKNOWN and evidence retention. |
| P2 — deployment provenance | Pin approved Python/image/action/model artifacts; verify downloaded binaries; exclude private build context; use reviewed runtime UID/mounts/limits. | Owner inventory identifies exact installed graph, binary provenance and applicable advisories. |
| Before future real adapter | Preserve deny-all registry/getter/dictation until independent authorization; require final revocation checks and one-operation retries. Harden screenshot publication with private trusted ancestors/directories and exclusive no-follow descriptor-bound write/read. | No confirmation-after-stop/retry extra effect or attacker-path redirection. Dormant screenshot helper is reassessed only with a real active adapter. |
| Before infrastructure activation | Independently qualify current source/release, restricted identities, protected files/grants/custody, effective units/filters, serial exclusivity and actual guest/API facts. | Existing operator gates stay effective; this audit grants no activation, credential, ACL, VM or privileged qualification permission. |
| Maintenance | Align stale legacy tests and explicit offline wake workflow with retired dispatch; preflight canonical transport response bytes. | Current tests expect actual refusals; accepted synthetic payload fits frame cap or is refused before dispatch. |

Retain regression controls for the six historical defects now gated/fixed. Their original repair recommendations and finite evidence remain in historical-defects.json; do not report them as current uncorrected issues.
'''
put('RECOMMENDED-FIXES.md',fixes)

summary=f'''# Executive summary

Reviewed {len(manifest)} captured public files and {len(ledger)} explicit units across JARVIS application, clients, execution/storage/recovery lifecycle, automation and the current Proxmox broker successor. Cutoff: {cutoff}. Base HEAD: `{meta['source_ref']}`. Dirty-source identity: `{rev}`.

**0 confirmed exploitable security vulnerabilities; {len(leads)} independently reviewed conditional authority lead.** No severity is assigned to unresolved or rejected claims. This result has deployment limits and is not a security certification.

Anonymous task read/cancel worked only with explicit synthetic admitted authority; genuine stock startup refused missing state. An actual admitted anonymous listener and an excluded reachable local UID/browser remain unestablished. The exact tested filesystem ancestor-swap chain failed at SQLite; different-UID filesystem replacement authority remains unqualified.

Concurrent changes gated/fixed six earlier reproduced call-site defects and were re-reviewed. One current reliability defect remains: a credentialed binary frame on /ue5 raises KeyError and leaves one stale entry. No shared outage or privilege gain was demonstrated. Prioritize all-exit cleanup there and resolve the conditional task trust model before multi-principal use.

Legacy server/registry/getter/dictation real effects are refused. The screenshot path claim is rejected as currently unreachable; its dormant helper still requires hardening before future reuse. Transport remains same-process fixed pure synthetic computation, with independent keys, permits and durable reservation/report verification. Operator-reconciled evidence needs separate explicit publication authority; no real executor was activated or qualified.

{total} selected regression cases passed across recorded captures, including 16 in the final capture, with separate bounded microfixtures. These are not a whole current-suite baseline. Application source was not modified by this audit. No production system, real database/credential, provider, real desktop/audio, Proxmox/VM or privileged Gate6K action was used. Installed identities, custody, ingress, dependency/advisory status and post-cutoff edits remain explicitly unqualified.
'''
put('EXECUTIVE-SUMMARY.md',summary)
report='# JARVIS V2 — comprehensive Cloudflare security audit R1\n\n'+summary.split('\n',1)[1]+'''\n## Scope and method

Standard profile; no strict agent budget was specified. Six hunting waves, independent post-wave source critics, a distinct final-clean coverage critic, fresh candidate validation and separate independent final-record verification. Exact installed Cloudflare skill files are hashed in skill-manifest.json. Historical evidence was not substituted for active source. No compatible previous structured audit ledger existed.

The user selected this in-repository directory. Only audit artifacts and the append-only project completion log were written. Source copies are immutable/readonly. Target execution used sequential OS-enforced isolation, synthetic state and low resource limits. Scope includes all 18 requested areas, with external assurance blocks preserved.

See [scope and hashes](SCOPE-AND-INVENTORY.md), [threat model](THREAT-MODEL.md), [coverage and limits](COVERAGE-AND-LIMITATIONS.md), [machine findings](findings.json), [final record checks](record-verification.json), and [validation summary](validation-summary.json).

## Confirmed security vulnerabilities

None met the complete boundary-and-impact evidence gate. Zero confirmed findings does not resolve deployment/custody/dependency assurance facts. [Finding details](FINDINGS-DETAIL.md) explicitly records this result.

## Needs validation

| Lead | Possible boundary effect | Exact decisive facts missing |
|---|---|---|
| Anonymous loopback task authority | Ordinary caller inherits service-actor task read/cancel | Actual admitted anonymous serving mode and an excluded reachable principal; browser policy/ingress if claimed |

[NEEDS-VALIDATION.md](NEEDS-VALIDATION.md) gives every current trace, evidence, blocker and exact synthetic/owner-observed resolution plan. No deployed endpoint should be probed.

## Current implementation defect

P2 D7: one credentialed /ue5 binary frame leaves a stale manager entry after KeyError. Normal disconnect leaves none. This is a per-session cleanup observation, not confirmed shared-service denial or privilege gain. [Exact input, retained result, command and fix](IMPLEMENTATION-DEFECTS.md). Six earlier call-site defects are gated/fixed in the final source; their historical evidence remains intact and is not reported as current exposure.

## Investigated and rejected claims

A remains conditional with stock startup refusal respected. B's exact connection-substitution chain failed; no cross-UID redirect was shown. Screenshot application reachability was refuted by current server/registry/native gates. [Hypotheses and false-positive checks](HYPOTHESES-AND-FALSE-POSITIVES.md) preserves the reasoning and limits on each negative result.

## Source controls and bounded validation

Scoped canonical receipts; lifetime writer ownership and conservative UNKNOWN; exact synthetic types; independent permit/request/response authentication; durable reservation before computation/report before reply; fresh-byte HMAC/rollover continuity; explicit genesis/witness admission; fixed-schema inert restore; and checkpoint/payload/expiry/CAS-bound recovery with no activation were traced. The final delta adds live recheck before report commit, explicit publication of operator-reconciled evidence and pre-open checkpoint pinning for offline CLI. Current broker peer/grant/preissuance/release/receipt controls were reviewed separately from its older baseline.

| Source capture | Selected cases | Retained result |
|---|---:|---|
'''+''.join('| '+x['source_snapshot']+' | '+str(x['case_count'])+' | ['+Path(x['artifact']).stem+']('+x['artifact']+') |\n' for x in validation)+'''
These are revision-tagged selections, not one full latest suite. Tiny fixtures separately tested conditional authority, denied legacy effects, earlier defects and current UE5 cleanup. No heavy/concurrent target execution, production effect or real executor activation occurred.

## Dependencies, configuration and operations

Electron has an exact integrity-bearing source lock. Python resolution, installed binaries and applicable advisory status remain unknown. Mutable images/actions/downloads, build contexts, runtime identity/mounts/limits, client token transport, independent custody/time and actually installed broker controls need owner evidence. [Dependency/configuration risks](DEPENDENCY-AND-CONFIGURATION-RISKS.md) distinguishes source facts from deployment assumptions; no CVE or supply-chain compromise was invented from floating manifests.

## Prioritized actions

Resolve the conditional authority trust model before admitted multi-principal use; fix UE5 all-exit cleanup. Preserve real-effect denial and historical regression controls. Qualify protected ancestry, dependency provenance and actual broker identities/units before rollout. [Precise fixes and acceptance invariants](RECOMMENDED-FIXES.md) are separate from vulnerability severity.

## Coverage conclusion

'''+str(states['covered'])+' covered units; '+str(states['candidate'])+' record-linked units for the independently disposed conditional lead; '+str(states['blocked'])+''' externally blocked assurance units. No planned, in-progress, deferred or independently unvalidated candidate remains. Distinct final-clean review accepted the frozen source selection. Each retained conditional record passed independent final review. source-stability-packaged.json records packaging equality and any post-cutoff changes; later source is not implicitly covered.
'''
put('REPORT.md',report)

rootcounts=collections.Counter(x['path'].split('/')[0] for x in manifest)
scope=f'''# Scope and exact source inventory

Final source identity: `{rev}`. Base HEAD: `{meta['source_ref']}` with dirty/uncommitted bytes captured. Cutoff: {cutoff}. HEAD alone does not identify this source. [source-manifest-packaged.json](source-manifest-packaged.json) records path, SHA256, bytes and observed source mode; [source-packaged.sha256](source-packaged.sha256) verifies readonly snapshot-packaged.

Dirty-source suffix is SHA256 of the ordered sha256sum file: `{hashlib.sha256((O/'source-packaged.sha256').read_bytes()).hexdigest()}`. SHA256 of the JSON manifest itself: `{hashlib.sha256((O/'source-manifest-packaged.json').read_bytes()).hexdigest()}`.

| Capture | Files | Selection/revalidation |
|---|---:|---|
| snapshot | 339 | Comprehensive first capture plus recorded public supplements |
| snapshot-current | 342 | 17 concurrent recovery/authority paths recaptured |
| snapshot-final | 342 | Further registry source/test/doc changes revalidated |
| snapshot-expanded | 385 | Adds 43 public current broker successor files |
| snapshot-latest | 388 | Revalidates 15 safety/authority/transport paths |
| snapshot-packaged | 390 | Final bounded 16-path transport/recovery/CLI/safety delta |

Every earlier snapshot and sealed evidence remains intact. Capture transitions, stable-read consistency and exact deltas are retained. Captures are per-file stable and rehashed, not atomic across files. source-stability-packaged.json compares packaged files to the active worktree and lists later drift.

Final capture: {len(manifest)} files, {sum(x['bytes'] for x in manifest)} bytes. repository-path-inventory.json contains metadata-only inventory of 56,613 paths, including historical artifacts.

| Root | Files |
|---|---:|
'''+''.join('| '+k+' | '+str(v)+' |\n' for k,v in sorted(rootcounts.items()))+'''
Active scope includes all maintained app/client/script/evaluator code, root task utilities, Electron lock, tests/docs/dependency/deployment definitions, phase2/older phase3 baseline and current tasks/proxmox-automation-phase3-review-r1 source/deploy/release design. PROJECT_STATUS89-94 identifies the successor. Historical evidence and binaries were excluded from active implementation conclusions.

Runtime config.yaml/.env/data/logs, real databases/credentials, installed credential-bearing observer helper, models and binaries were not opened. Public examples and dummy test keys were included. One public upstream MSS writer was inspected statically through GitHub; no package/advisory downloads or installed-version inference followed. No production/provider/desktop/audio/PVE/guest operation occurred. Application source and Git index were not modified by this audit; the audit directory and append-only project completion log are its only writes.
'''
put('SCOPE-AND-INVENTORY.md',scope)

put('REPRODUCTIONS.md','''# Bounded reproduction index

No confirmed exploitable security vulnerability is claimed. Current D7 input/commands/result/fix are in [IMPLEMENTATION-DEFECTS.md](IMPLEMENTATION-DEFECTS.md). Six earlier reproduced mechanics are historical and now gated/fixed at their reviewed call sites; replay only against the recorded capture in historical-defects.json.

| Check | Fixture | Capture / result artifact |
|---|---|---|
| Conditional authority | agents/verify-latest-auth/scratch/verify_auth_packaged.py | snapshot-packaged / agents/verify-latest-auth/artifacts/verify_auth_packaged.txt |
| UE5 binary cleanup | agents/hunt-packaged-safety/scratch/ue5_binary_cleanup.py | snapshot-packaged / agents/hunt-packaged-safety/artifacts/ue5_binary_cleanup.txt |
| Safety fixes | agents/hunt-packaged-safety/scratch/packaged_safety_tests.py | snapshot-packaged / agents/hunt-packaged-safety/artifacts/packaged_safety_tests.txt |
| Transport/offline recovery | agents/hunt-packaged-transport/scratch/packaged_transport_tests.py | snapshot-packaged / agents/hunt-packaged-transport/artifacts/packaged_transport_tests.txt |
| Legacy effect denial | agents/hunt-latest-safety/scratch/latest_safety.py | snapshot-latest / agents/hunt-latest-safety/artifacts/latest_safety.txt |
| Ancestor substitution | agents/parent-current/scratch/ancestor-current.py | snapshot-current / agents/parent-current/artifacts/ancestor-current.txt |
| Hot-journal recovery | agents/parent-final/scratch/hot-journal-controls.py | snapshot-final / agents/parent-final/artifacts/hot-journal-controls.txt |
| Current broker chain | agents/hunt-infra-current-chain/scratch/current_chain_controls.py | snapshot-expanded / agents/hunt-infra-current-chain/artifacts/current_chain_controls.txt |
| Current preissuance/files | agents/hunt-infra-current-files/scratch/current-file-controls.py | snapshot-expanded / agents/hunt-infra-current-files/artifacts/current-file-controls.txt |

From this audit directory, copy a fixture to a fresh basename in the same owner's scratch, then run `python3 sandbox-runner.py OWNER COPIED_FIXTURE SNAPSHOT`. Every replay needs a fresh stem; existing results are never overwritten. Target sees readonly source/tools, empty allowlisted environment and scratch-local writes, with no external network, host home, credentials, services, devices or other agents' artifacts. Namespace/process termination precedes bounded predeclared no-follow descriptor-confined promotion.

Runner code, safe environment and exact resource limits are retained in sandbox-runner.py/validation-summary.json. Toolchain inventory is not deployment identity. No screenshot or separate-UID/native-writer qualification was performed; the current application capture path is rejected.
''')
put('OUTPUTS.md','''# Audit outputs

- [Executive summary](EXECUTIVE-SUMMARY.md), [full report](REPORT.md)
- [Scope and exact revision](SCOPE-AND-INVENTORY.md), [threat model](THREAT-MODEL.md)
- [Structured findings](findings.json), [confirmed details](FINDINGS-DETAIL.md), [conditional authority lead](NEEDS-VALIDATION.md)
- [Hypotheses/false positives](HYPOTHESES-AND-FALSE-POSITIVES.md), [current cleanup defect](IMPLEMENTATION-DEFECTS.md), [historical gated/fixed mechanics](historical-defects.json), [reproduction index](REPRODUCTIONS.md)
- [Dependency/configuration risks](DEPENDENCY-AND-CONFIGURATION-RISKS.md), [prioritized fixes](RECOMMENDED-FIXES.md)
- [Coverage/limits](COVERAGE-AND-LIMITATIONS.md), [deterministic ledger](coverage-ledger.json)
- [Validation summary](validation-summary.json), [independent final checks](record-verification.json)
- [Run metadata](run-metadata.json), [source manifest](source-manifest-packaged.json), [sha256sum input](source-packaged.sha256), [source stability](source-stability-packaged.json)
- [Installed skill identity](skill-manifest.json), [artifact index](artifact-index.json)

snapshot-packaged is the final 390-file source selection. Earlier immutable captures, reviewer outputs and synthetic fixture programs remain revision-tagged. reports-before-latest preserves superseded claims for provenance, not current exposure. Project tasks/loop-log.md remains append-only outside this directory.
''')
stability=get('source-stability-packaged.json')
drift=stability['post_capture_worktree_changes']+stability['removed_or_nonregular']+stability['new_public_source_paths']
if drift:
 note=f"**Revision limit:** ongoing implementation changed {len(stability['post_capture_worktree_changes'])} captured paths and added {len(stability['new_public_source_paths'])} public path after the cutoff. Those later bytes are unreviewed; see [exact post-cutoff list](POST-CUTOFF-CHANGES.md). Findings apply to the frozen revision."
 for name in ['REPORT.md','EXECUTIVE-SUMMARY.md','SCOPE-AND-INVENTORY.md','COVERAGE-AND-LIMITATIONS.md']:
  p=O/name;t=p.read_text();first=t.find('\n\n');p.write_text(t[:first+2]+note+'\n\n'+t[first+2:])
 p=O/'OUTPUTS.md';p.write_text(p.read_text()+'\n- [Unreviewed post-cutoff changes](POST-CUTOFF-CHANGES.md)\n')
print(json.dumps(dict(source_files=len(manifest),units=len(ledger),confirmed=0,needs_validation=len(leads),rejected=len(rejected),current_implementation_defects=1,historical_gated_or_fixed=6,selected_cases_across_captures=total)))
