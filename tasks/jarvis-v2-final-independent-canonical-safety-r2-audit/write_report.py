from pathlib import Path
import json,datetime
A=Path(__file__).resolve().parent
v=json.loads((A/'VERIFICATION.json').read_text());static=json.loads((A/'STATIC-REVIEW.json').read_text());C=Path(json.loads((A/'CHECKOUT.json').read_text())['path'])
S=v['git']['source'];T=v['git']['tree'];P=v['git']['parent'];CP=v['git']['canonical_head'];E=v['technical_seal']['sha256']
(A/'REPORT.md').write_text(f'''# Final independent canonical safety R2 audit

**Verdict: APPROVE FOR EXPLICIT HUMAN CANONICAL MERGE AUTHORIZATION.**

The two earlier medium findings are closed for the supported offline acceptance and CI entrypoints. Exact source identity, historical preservation, enrolled test completeness and preserved application safeguards PASS. No merge, push, deployment, remote CI or infrastructure action is performed or authorized by this audit. A separate human decision must identify the exact source below; approval does not extend to an evidence branch tip or a subsequently changed tree.

This is a fresh technical verification with a new exact-commit checkout, fresh execution, independent stdlib verifier and new inert discovery/report probes. Earlier engineering/review context is inherited. It is not a fresh-context organizational audit, independent evidence custody or a claim of actual external Astra review.

| Area | Result |
|---|---|
|Pinned source/tree/immediate parent and preserved lineages|PASS|
|Canonical history and existing local work preservation|PASS|
|Historical pytest discovery remediation, supported entrypoints|PASS; deliberate configuration overrides are outside the guarantee|
|Legacy CI selection and fail-closed prerequisite behavior|PASS in source/local qualification; remote execution NOT QUALIFIED|
|922 exact identities and complete terminal execution|PASS|
|Preserved application safeguards|PASS within offline scope|
|883 historical files and 274 public inputs|PASS|
|943 technical / 957 outer evidence entries|PASS|
|Independent cryptographic custody/signing|NOT ESTABLISHED|

## Exact objects and current canonical state

Integration source **`{S}`**, tree **`{T}`**, immediate parent **`{P}`** match the pins. Its chain is32bc552e→0bc7e3c→e1e1994f→6341648. Original merge6341648131cec7318ea961c3b081878fb86c4fe7 retains ordered parents `{CP}` then674aff2c25d050420145f9b102808f194f0544fa. Both are ancestors of the corrected source. Old evidence child ddf7b89f is not an ancestor.

New evidence-only child2af89d5a5521aa0c1237417a5fd98b1081dabcbc has exactly one parent, the tested source, and958 added files confined to the new engineering packet. Every file matches its child Git blob. It is **not the integration target**. The technical seal covers943 files; the outer957-file seal plus itself account for all958 child files.

Canonical remains `{CP}` on docs/p7-d06-d07-passive-review, with its pre-existing dirty administrative log. All128 newer committed canonical paths are preserved byte-identically in the source; no intervening canonical commit or runtime overlap exists. Frozen RC1/e9b473474 and pre-existing worktrees are preserved. Detached JARVIS-release-r1 has40 pre-existing changed files; they are not mistaken for clean state or modified by this audit. Initial/final HEAD/status/dirty-byte checks are recorded separately. Only new audit output, a new detached checkout/temporary fixtures and the mandated append-only canonical log entry are written.

## Discovery remediation

All12 exact archival paths are listed in DISCOVERY-REVIEW.md and VERIFICATION.json. Each equals its6341648 historical blob and earlier canonical test blob; its current tests/ counterpart is required and executes. All883 historical files, including their eight old seals, remain unchanged. Old source-bound seals retain their original-revision meaning; they are not falsely presented as current-source inventories.

The former root collector had no discovery boundary. Current pytest.ini sets testpaths=tests and excludes tasks/dependency directories after confirming all68 required modules reside in tests/. Configuration alone would not stop explicit filenames: root conftest now rejects ordinary host pytest at configure time before test-module imports. The qualified namespace child requires its fixed readonly context and restricts exact collector files; explicit non-enrolled modules are refused before Module.collect. Parent preflight rejects altered/new modules, policy/source drift and links. The new36 cases exercise these rules, actual inert pytest subprocesses, environment rejection, inventory/history/CI membership, and incomplete evidence, rather than asserting counts alone.

Independent synthetic probes:13 ordinary invocation variants exit4 with no inert test import, covering root/tests/archive/external cwd, collection-only, explicit unsafe/archive paths, rootdir change, /dev/null config and environment-selected archive arguments. Three deliberate bypass controls import only the inert sentinel and exit0: --noconftest, --confcutdir=tasks/archive, and an explicitly selected archive-local alternate.ini from that directory. No original historical/unsafe test was imported. These controls establish the boundary: the guard is not an enforcement mechanism against a user disabling trusted pytest configuration. No such option is available through supported full acceptance or CI; child environment is replaced, plugin autoload disabled and pytest arguments fixed. The report does not claim all arbitrary pytest invocations are safe.

The137 current test Python files reconcile exactly:68 required +17 support +2 negative fixtures +39 out-of-scope +11 unsafe/live-dependent. All136 earlier entries, including reasons and content hashes, are preserved; one new required module contributes36 cases. All886 earlier node IDs remain mandatory, not just the number886. No unclassified module, weakened old test or executing exclusion was found. Scope is explicit tests/ enrollment plus separately pinned historical folders, not automatic qualification of arbitrary Python files anywhere in the repository. Expected manifests are checked in, source-bound and digest-pinned; acceptance never generates or shrinks them. A maintainer update requires explicit reviewed promotion and loader digest changes.

## CI remediation

The only current automated workflow is .github/workflows/tests.yml. Its previous broad pytest selection included the excluded unmarked test_switch_models.py module, which copies config.yaml to config.yaml.test-backup, rewrites model profiles via scripts/switch_models.py and restores/removes the backup. This actual module and private configuration were never executed or opened.

The workflow now has one run step: `python3 -B scripts/offline_acceptance.py --output-dir "$RUNNER_TEMP/jarvis-offline-acceptance"`. Push/PR main and manual triggers remain active. No apt/pip/setup-Python/cache installer, rawpytest/subset/listing fallback, skip condition or continue-on-error remains. Checkout permissions are contents:read with persist-credentials:false. New workflow membership and bytes require review. Local script/module runs exercised the complete implementation; no remote workflow was launched.

Exact Python3.14.4, bubblewrap0.11.1 and127 distribution versions are required, including APScheduler3.11.3. An empty bundle is independently BLOCKED/nonzero before job execution. Standard ubuntu-latest is not qualified and must fail if prerequisites are absent. The operator-owned variable may select a separately qualified disposable hosted image; no image/variable/runner was provisioned. Never use a trusted persistent/self-hosted or production PR runner. Remote image availability, workflow-event checkout behavior and orchestration remain separate qualifications, not a green remote CI claim.

Manual install.py/install_piper.py remain legacy opt-in installers, not supported acceptance/CI. Their obsolete rawpytest call/hint is not executed; the actual installer checks a failed smoke subprocess and exits nonzero. Their provider/network/package behavior remains unauthorized. Historical manual tools are data, not automated entrypoints.

## Fresh exact-source results

Both commands ran from new clean detached checkout `{C}` at `{S}`, not the evidence child. EXECUTIONS.json preserves exact commands, timestamps, cwd and exit0. Outputs are separate from source. The independent verifier imports no application, engineer verifier or inventory loader; it reconstructs node-to-report identities and every successful ordered setup/call/teardown phase.

| Suite | Distinct pass | Fail | Error | Skip | Missing / incomplete | Gate / child exit |
|---|---:|---:|---:|---:|---:|---|
|Safety R2|36|0|0|0|0|0 / 0|
|Coverage|217|0|0|0|0|0 / 0|
|Reconciliation|66|0|0|0|0|0 / 0|
|Reliability R3|19|0|0|0|0|0 / 0|
|Reliability R2|45|0|0|0|0|0 / 0|
|Original Gauntlet|32|0|0|0|0|0 / 0|
|Existing V2|507|0|0|0|0|0 / 0|

**922 distinct tests**, including all886 previous identities and36 new regressions. Each script/module entrypoint also passes415 seed42 repeats and22 gate contracts +14 retained negatives +11 enrollment adversaries +12 replayed attacks. All17 child jobs per full invocation exit0. Both full invocations total2674 positive executions:922 unique plus1752 repeated executions, including830 seed42 executions. Controls inside negative matrices are not added to unique totals. Seven additional invocation contracts pass. Both reported engineering final runs were independently reverified as well; they are not counted as our fresh executions.

The R2 before contract freshly reproduces PASS/exit0 with31 executed/zero skips. The corrected gate rejects the same45-required case with14 missing/FAIL/exit1 while the pytest child returns0. A same-count substitution of217 identities yields1 missing+1 unexpected and fails. A late execution substitution has no collection omission yet1 incomplete execution and fails. New modules, changed policy/classification, source mismatch, skipped imports, omitted parameter cases, duplicate IDs, xfail/xpass and missing terminal/collection evidence all reject. Negative evidence/nonzero exits are preserved, not reported as positive test failures.

Additional independent outer-CLI report probes use retained fresh reports as explicitly simulated subprocess outputs. Eight fault cases—missing, duplicate, substitution, skip, interruption, missing collection completion, malformed JSON and absent terminal file—produce FAIL/BLOCKED with outer exit1 despite every simulated subprocess returning0. The valid replay control returns PASS/0. These nine contracts are not new real pytest executions. A first overbroad audit stub intercepted preflight subprocesses; its valid control exposed it. HARNESS-CORRECTION.json preserves that invalid diagnostic attempt, the narrow correction and the successful new v2 outputs. A failed exploratory read of a nonexistent authority_api.py was corrected to app/agent/api.py; neither diagnostic is hidden as a required-suite error.

## Application safeguards

PASS for authenticated nonblank exact-Bearer readiness, embedded-router identity checks, non-ready/invalid responses and no startup/retry fallback; credential/remote-origin validation and whitespace rejection before transport background startup; post-create no-follow storage ancestry checks; bounded WebSocket sends/closes with endpoint-owned registration until exit; disabled automatic resource controls; opt-in dictation/public-example defaults and privacy negatives; Simulator rejection of execution envelopes; timestamp overflow normalization; retained APScheduler asynchronous cleanup, partial retry/cancellation/timeout ownership and restart fencing; sanitized structured failure evidence; durable Authority receipts, ledger/checkpoint and recovery invariants.

All app/ bytes are identical to original combined merge6341648 and approved source da67d936. The15 corrective paths are individually assessed in SOURCE-REVIEW.md; no runtime schema, transport, authorization or dependency behavior was silently replaced. Fresh tests include real installed APScheduler3.11.3 executor/job-store lifecycle cases alongside explicitly synthetic failure fixtures. They do not qualify native/custom/thread executors, real providers/hardware or physical-loss behavior. Ordinary legacy loopback routes are not falsely described as universally authenticated; the strict Authority/readiness boundary is preserved.

## Historical inclusion and integrity

All883 packet files total26,337,809 bytes; all are textual mode100644 blobs, with no imported symlink/executable mode/binary. Of27 Python files,12 are archived tests, one an archived helper and14 historical manual tools. Their provenance is established by the earlier source lineages and exact old blobs. Bounded private-key/provider-key shape scans find no flags; this is not proof against arbitrary encoded secrets. Keeping them is defensible audit continuity now that default discovery and automated entrypoints are controlled. Do not bulk-run old tools or count historical PASS logs as current acceptance. No frozen RC1/sealed bootstrap/VM164/Gate6K path changes are present.

All274 source inputs match Git blobs, before/after maps, both fresh readonly snapshots and both engineering final snapshots. Fingerprint e41d155cc3e41aaeac6b502b1af6cecf54a350e5be7980627663da196f35aca6. Inventory SHA256 c62ffae6ff57487af4aeeff9b8cb0dad3c47ac933c17b017f7fc31198772af52; module policy da49ec83861d077578daea20d7cfc168b6af3feabd2d16949a2040914ec1eb98. Each full acceptance155-entry seal verifies. Expected technical digest **`{E}`** matches943 entries; outer digest f41dc8f2968560408f3793131775a0001b53cf056c48b4ec5231be9025e6f22c matches957. Source/evidence child chronology truthfully identifies the pre-existing exact tested source; no retrospective source substitution occurs.

Read-only snapshot modes0444/0555, actual namespace ro-binds and isolated output/fault copies establish local integrity. Directory permissions are not preserved by Git; evidence in a checkout is not thereby independently protected. JSON/hashes are unsigned; local host, same-UID/root, Git, interpreter/plugins and dependency backing bytes remain trusted. Version metadata is not package supply-chain attestation. Matching pre/post hashes do not exclude transient tampering. Existing synthetic negative input parameter strings in candidate inventory drafts are source fixtures, not raw exception leaks in reports; generated fresh failure JSON scans find no injected private/secret marker. No independent custody/signing is claimed.

## Ranked remaining risks and integration conditions

No unresolved high/medium offline blocker was found. Prior discovery and CI medium findings are CLOSED within the documented supported-entrypoint scope.

- LOW — Deliberate trusted-config overrides bypass raw-host pytest protection, as inert controls demonstrate. Keep rawpytest/legacy scripts unsupported; require the complete pinned controller for any acceptance decision.
- LOW operational — Remote CI image/variable/orchestration is not provisioned or qualified. Standard images fail closed rather than supply usable green evidence. Qualify a disposable hosted environment separately if remote CI is desired; local acceptance may gate this development-only decision without it.
- LOW custody/environment — Evidence is unsigned and dependencies are version-checked rather than independently attested. Retain the pinned digests independently; use the qualified local environment. No network advisory/package audit was attempted under offline/no-install boundaries.
- LOW procedural — Canonical's dirty log deliberately fails the controller's clean-checkout preflight. Preserve it. Verify actual canonical public inputs, then use a new clean detached exact-HEAD checkout for post-update acceptance; do not reset/stash/commit unrelated work.

Before any separately authorized integration: recheck canonical HEAD/branch, dirty/untracked collisions, exact source/tree, both lineages, public byte maps, dependencies and evidence seals. Any source/parent/environment or intervening canonical change requires a new reviewed exact candidate and complete acceptance, not a forced fast-forward or untested wrapper merge. Keep the39/11 exclusions and mandatory922 identities; no inventory regeneration.

A normal development-only fast-forward from the unchanged canonical parent to the exact source is structurally possible and preserves both lineages. This audit performs none. After a separately authorized update, compare actual canonical HEAD/tree and274 public bytes to the reviewed source, confirm local work/log preservation, and run BOTH full entrypoints from a NEW clean detached checkout of that exact canonical HEAD into NEW outputs. Zero failure/error/skip/missing/incomplete and fresh negative matrices remain mandatory. No deployment follows.

Rollback is feasible by preserving history and preparing a separately reviewed compensating reversal in an isolated branch against the then-current tree, accounting for original merge mainline1 and the three later corrections. Restoring older insecure behavior is not automatically safe. Never force-reset canonical or alter running state as rollback under this audit.

## Next operator action and exact authorization

Review this report and its separate evidence first. If accepted, request the explicit development-only authorization in HUMAN-AUTHORIZATION.md, binding `{S}`, canonical `{CP}`, tree `{T}` and technical digest `{E}`. Exclude evidence child2af89d5a, mutable branch tips, all pushes/deployments/infrastructure/provider/credential/privileged operations. Human authorization and immediate revalidation remain necessary; the verdict is not that authorization.
''')

review={
'.github/workflows/tests.yml':'Replaces unsafe broad/config-writing selection and installers with the sole full gate; read-only checkout permissions, explicit hosted-image trust/qualification boundary.',
'conftest.py':'Configure-time host refusal; exact qualified path context and per-suite file allowlist; explicit collector rejection. Intentional overrides documented and independently demonstrated.',
'docs/offline-acceptance.md':'Accurately specifies supported invocation, archive/default policy, explicit inventory updates, remote limits and dirty-log preservation.',
'pytest.ini':'Discovery restricted to tests/ with historical/dependency recursion excluded; all required current modules remain in scope.',
'scripts/historical_packet_inventory.json':'883 exact old file hashes/membership; no historical mutation or source substitution.',
'scripts/offline_acceptance.py':'Exact seven positive suites, environment/preflight/clean snapshot, 17 job orchestration, actual exits, full identity/phase checks and safe failure output. Independent outer evidence faults reject.',
'scripts/offline_contracts.py':'Three audited historical tools receive additive public fixture inputs in-memory only; originals unchanged, mutations restricted to disposable copies.',
'scripts/offline_environment.json':'127 exact package versions, Python3.14.4, bwrap0.11.1 and explicit workflow membership; versions are not backing-byte attestation.',
'scripts/reliability_gauntlet.py':'Adds safety mode, required readonly mounts and pre-hash link rejection; structured event validator, sandbox/environment and fail exits retained.',
'scripts/required_nodes_6341648.json':'Independent earlier886 exact identity baseline confirmed directly against6341648 Git inventory.',
'scripts/required_test_inventory.py':'Only reviewed inventory digest promotion; strict source/identity/policy loader retained.',
'scripts/required_tests.json':'Exactly36 new positive IDs/source bindings; all886 old IDs remain. No observed-count authority or acceptance-time generation.',
'scripts/test_enrollment.json':'All136 prior entries unchanged; one required module added. All50 exclusions unchanged.',
'scripts/test_enrollment.py':'Rejects unsafe relative components and symlink parents; exact files, disposition/hash/digest checks retained.',
'tests/test_canonical_safety_r2.py':'36 genuine cases across guard subprocesses, enrollment/history/CI/dependencies and negative outer evidence, plus valid control. No old assertion weakened.'}
(A/'SOURCE-REVIEW.md').write_text('# Corrective source review\n\nAll15 paths relative to6341648, with zero app/ or historical task delta.\n\n| Path | Assessment |\n|---|---|\n'+''.join('|`'+n+'`|'+review[n]+'|\n' for n in v['source_changes'])+'\nThe inherited nine application deltas versus canonical were also inspected: authority timestamp normalization, Simulator boundary, scheduler/owned backend, storage post-create validation, authenticated CLI ready, server/UE5 lifecycle and resource defaults. Fresh selected tests cover these plus unchanged API/ledger/recovery contracts.\n')
(A/'DISCOVERY-REVIEW.md').write_text('# Exact archival disposition and independent probes\n\n| Historical path | Required current counterpart | Decision |\n|---|---|---|\n'+''.join('|`'+n+'`|`tests/'+Path(n).name+'`|Byte-identical forensic evidence; never executed|\n' for n in v['historical']['test_modules'])+'\nAll12 also match prior canonical test blobs. See DISCOVERY-PROBES.json for exact commands/exits from inert fixtures. Thirteen ordinary variants reject with4/no imports; three intentionally defeating the policy import only an inert marker. No actual unsafe code or private configuration is used.\n\nThe guard cannot secure an arbitrary interpreter against operator disabling conftest/config or executing files directly. Supported full gates accept no pytest flags, clear child environment and disable plugin autoload. New unreviewed tests/ modules and new workflows fail preflight; historical directories have separately pinned membership and byte hashes.\n')
(A/'TEST-RESULTS.md').write_text('# Fresh execution details\n\nCommands/timestamps/cwd/exits: EXECUTIONS.json. Full authoritative output: acceptance-script/ and acceptance-module/. Independently reconstructed node IDs and every suite/phase/count/source map: VERIFICATION.json. Positive commands each exit0 with922 complete passes and415 seeded repetitions; no fail/error/skip/missing/incomplete. The36 new cases are genuinely collected and executed under the same required identity protocol.\n\nEach invocation passes22 gate contracts,14 negative contracts,11 enrollment adversaries and12 replayed attacks. Total unique pytest cases922; total qualified positive executions2674, including830 seed42 and922 repetitions of the primary identity set. Seven additional entrypoint contracts pass. Independent outer report faults8/8 reject and replayed valid control passes; these simulated reports are not real additional positive executions. Sixteen discovery probes13 ordinary refusal+3 deliberate-bypass controls use inert modules only.\n\nThe original R2 before reproducer again passes31 instead45; after rejects with14 missing/exit1 despite child0. Late execution omission, substitution preserving totals, skip/xfail and source/classification corruption all reject. Negative status/exits are retained in output, not suppressed.\n\nHARNESS-CORRECTION.json discloses a diagnostic stub correction exposed by its valid control. The first outer-report-probes/ is invalid diagnostic material, never acceptance proof. Only outer-report-probes-v2/ supplies these nine contracts. An exploratory read used a nonexistent authority_api.py path and was corrected to api.py; required suites/verifier were unaffected.\n')
(A/'ENROLLMENT-REVIEW.md').write_text('# Enrollment and visible exclusions\n\n137 Python files =68 required +17 support +2 negative fixtures +39 out-of-scope +11 unsafe/live-dependent. All136 old records, reasons and hashes remain identical; only one36-case required module is added. Every922 required identity is collected and executed; all886 prior identities remain. Negative fixtures and excluded modules are not positive cases.\n\n| Excluded exact path | Classification | Reviewed reason preserved |\n|---|---|---|\n'+''.join('|`'+n+'`|'+e['disposition']+'|'+e['reason'].replace('|','/')+'|\n' for n,e in sorted(static['excluded_modules'].items()))+'\nPolicy updates require a separate candidate, safety review, explicit node/source/disposition diffs and loader digest promotion. Acceptance never invokes a generator. Existing classification tampering and attempted unsafe selection reject before a child starts.\n')
(A/'HUMAN-AUTHORIZATION.md').write_text(f'''# Separate later human decision — not granted here

Proposed wording, only after report/evidence review and immediate unchanged-state revalidation:

> Authorize a development-only ordinary fast-forward of canonical branch docs/p7-d06-d07-passive-review from {CP} to exact source {S}, tree {T}, immediate parent {P}, preserving original merge6341648131cec7318ea961c3b081878fb86c4fe7 and its ordered parents {CP} and674aff2c25d050420145f9b102808f194f0544fa. I have reviewed technical evidence digest {E}, the final independent audit, exact922-case acceptance and documented configuration/remote-CI/dependency/custody limits. Preserve all uncommitted work, logs and detached worktrees. Recheck exact HEAD/source/environment/evidence immediately; abort on differences or collisions. After updating, verify actual canonical source bytes and perform complete fresh offline acceptance in a new clean detached checkout of that exact HEAD. This excludes evidence child2af89d5a5521aa0c1237417a5fd98b1081dabcbc and any mutable branch tip. This authorizes no push, deployment, production/Student Flow/Proxmox/VM/provider/credential/network/package/privileged/Gate6K action.

No such authorization is inferred from this audit verdict or requested as an action within this turn. If canonical advances or source/environment differs, prepare and independently review a new exact combined candidate. Preserve history for any separately reviewed compensating rollback; never force-reset canonical or sacrifice the dirty administrative log to pass preflight.
''')
print('Reports written')
