# Independent canonical merge candidate audit

**Verdict: APPROVE WITH CONDITIONS.**

The exact combined application source, required offline suites, Git ancestry and evidence integrity pass. The proposal is **not an unconditional repository/CI qualification**: archived Python tests remain automatically discoverable outside enrollment, and the unchanged legacy CI selection reaches an explicitly excluded configuration-mutating module. Conditions C1–C4 below must be resolved or explicitly bound into a Gate-only development integration decision before human authorization. No merge is performed or authorized by this report.

| Required area | Decision |
|---|---|
|Exact merge, ordered parents and tree|PASS|
|Canonical committed-history preservation|PASS|
|49-path reviewed application/test/tool delta|PASS within qualified offline scope|
|883-file packet provenance/integrity|PASS; working-tree discovery/inclusion policy CONDITIONAL|
|Preserved application security safeguards|PASS|
|886 required identities/complete execution|PASS|
|266 source inputs, inventory/digests/dependencies|PASS|
|Independent custody/signing|NOT ESTABLISHED|
|Whole-repository default pytest / legacy CI qualification|NOT ESTABLISHED; specific hazards reproduced with inert fixtures|

Earlier implementation/review context is inherited. This is a separate verification pass with fresh exact-commit execution, an independently written verifier and new discovery probes; it is not a fresh-context organizational audit or independent evidence custody.

## Exact Git objects and preservation

Integration target **`6341648131cec7318ea961c3b081878fb86c4fe7`**, ordered parents **`b09fa10a661c9704f51e900ec857a51153cbcbbe`** then **`674aff2c25d050420145f9b102808f194f0544fa`**, tree **`8838c386db3bbe2d4b6e51d0ef884bdc844bc99d`** all match the pins. Evidence-only child **`ddf7b89f0e55269f337cd05c19b6ee915dd31dcd`** has exactly one parent, the tested merge, and adds exactly201 expected evidence/report files. Every child file matches its Git blob; its CHANGED-FILES list and actual diff/file set agree. The evidence child is **not** the integration target.

Canonical remains `b09fa10a661c9704f51e900ec857a51153cbcbbe` on docs/p7-d06-d07-passive-review; it has not advanced. Shared base b738a473d27471f35df60d31ccd93047bf9d1a6e yields128 newer canonical audit/log paths and932 candidate changes with no overlap. All128 paths are byte-identical to the canonical parent in the merge, and all932 candidate paths byte-identical to the reviewed parent. Git objects therefore establish the exact disjoint union; zero textual conflicts alone is not the semantic evidence.

The932 changes are904 additions and28 modifications; no deletion/rename/type change. All imported paths have mode100644: no symlink, submodule or executable mode import. Application source exactly matches approved da67d936, reconciliation5c878448a and reviewed Reliability R3b0c8865a. The nine app changes versus canonical restore documented safeguards/reliability fixes, not newer canonical behavior accidentally overwritten. Data/SQL schema, execution transport and Authority authentication interfaces are unchanged. COMMIT/DIFF evidence is independently reconstructed in VERIFICATION.json and FULL-DIFF-REVIEW.json.

All11 pre-existing worktree heads, tracked states and dirty tracked file hashes remain unchanged, including40 detached release-r1 modifications. Canonical's pre-existing log bytes are preserved before the required final append. Frozen Unified RC1/e9b473474 and other reviewed refs remain unchanged and clean where initially clean. No sealed/bootstrap/VM164/Gate6K path is imported or modified. A NEW private detached audit checkout of the exact merge was created only for read-only testing; no existing checkout/ref was repurposed.

## Full source and packet review

SOURCE-REVIEW.md/JSON individually cover all49 source paths:9 app,9 runner/inventory,30 tests/fixtures and1 public example. Each equals the approved second-parent blob. The current-contract fixture/test replacements retain the accepted durable Authority/closed-executor model; they do not newly weaken tests to obtain this PASS. Retired legacy implementation fault matrices are not claimed one-to-one requalified.

The883 packet files are374 reconciliation +338 coverage +171 rehearsal files, totaling **26,337,809 bytes** (about25.1MiB). They are423 JSON,278 text,118 logs,28 Markdown,27 Python,8 checksum manifests and1 patch; all decode as text and all JSON parses. Largest file600,826 bytes. No unexpected binary, symlink, executable mode, unapproved task folder or large payload was found. Bounded private-key/AWS/GitHub/provider-key shape scans find no flags; explicit synthetic fixture tokens are test data, not accessed live credentials. This is not a mathematical proof against arbitrary encoded secrets.

Historical failures, before/after false-PASS reports and repeated logs are deliberate forensic evidence, not new positive proof. All eight historical seals verify against their intended revision/directory (1575 manifest-entry checks, with overlap; not1575 tests). The old reconciliation/root and preserved recovery seals must be checked against5c878448a/18a9d82c, not misrepresented as current source inventories.

**F1 — MEDIUM, new discovery/inclusion gap.** Of27 packet Python files,13 are exact older canonical test/helper bytes:12 `test_*.py` modules and1 helper in preserved-development-tests/. They are historical evidence, not part of the136-file tests/ enrollment policy. The current pytest.ini has no testpaths/norecursedirs rule excluding them. Safe inert replicas of those exact paths are collected by ordinary root pytest:12 archive modules plus1 control, versus only1 control without the archive. A prospective testpaths=tests fixture excludes all12. Original archive code was never imported/executed. Static review also identifies obsolete imports such as ScheduledJob in the archived scheduler test, absent from the current scheduler module. Thus generic root discovery can collect incompatible historical tests; the886-case gate does not govern them. PACKET-REVIEW.md lists the scope/provenance and preferred quarantine options.

**F2 — MEDIUM, inherited workflow qualification gap.** .github/workflows/tests.yml is unchanged from canonical; it targets main push/PR, installs packages and runs broad pytest tests/ with only directory/manual/hardware exclusions. A safe inert replica confirms this selection includes all3 unmarked tests in tests/test_switch_models.py, which the reviewed policy deliberately excludes. Actual source setup copies config.yaml, runs a profile-rewriting script and restores a backup; if the file is absent it fails instead. This is not newly introduced behavior and is not invoked by a local update to the current docs branch, but the old workflow is not a safe/qualified substitute for the reviewed offline gate. No real module/config/CI/provider was executed. No claim of successful remote CI or Python3.11 qualification is made; fresh acceptance used the recorded3.14.4 environment.

The other14 Python packet tools are explicit historical acceptance/reproduction/verifier tools, not application imports or hooks. Some historical tools depend on old absolute worktree paths and intentionally reproduce failures. Do not bulk-run arbitrary packet tools as current acceptance. Their inclusion is defensible forensic provenance, not a new trusted runtime surface; default discovery isolation and supported entrypoint policy still need explicit closure.

## Fresh exact combined-tree acceptance

Fresh acceptance was run from detached HEAD `6341648131cec7318ea961c3b081878fb86c4fe7`, not from the evidence child or an earlier rehearsal. Source/tree metadata names the exact target. Outputs are separate; source is copied into a retained read-only public snapshot before tests. EXECUTION.json records the exact command, checkout, timestamps and exit0.

| Fresh suite | Pass | Fail | Error | Skip | Missing / incomplete | Gate / child exit |
|---|---:|---:|---:|---:|---:|---|
|coverage|217|0|0|0|0|0 / 0|
|reconciliation|66|0|0|0|0|0 / 0|
|r3|19|0|0|0|0|0 / 0|
|r2|45|0|0|0|0|0 / 0|
|original|32|0|0|0|0|0 / 0|
|existing|507|0|0|0|0|0 / 0|

**886 distinct required identities** complete successful ordered setup/call/teardown; no duplicate/substitution/missing/unexpected identity, collection skip/deselection, error, timeout or incomplete session is accepted. **379 seed42 repeats** pass and are excluded from886. Seed16401 originals and repeat sets are reconstructed independently without importing the engineering verifier, inventory loader or application. Both original engineering and fresh audit results identify the exact merge and identical case sets.

Fresh22 gate contracts,14 negatives,11 enrollment adversaries,12 replayed attacks,6 additional CLI probes and3 report-tampering checks pass their expected outcomes. Positive controls within these groups are not additional distinct tests. The217-case environment-control repeat is separately disclosed, excluded from886/379. Intentionally failing JSON/logs/nonzero exits remain present.

The original R2 defect again reproduces PASS/exit0 with31 executions/zero test skips. The proposed gate rejects the same45-required/31-executed case with14 missing/exit1 even when pytest exits0. Late run-loop omission has0 missing collection identities yet1 incomplete execution and correctly fails. Skip/xfail, filtering, missing terminal evidence, source/policy tampering and unsafe selection fail closed. Raw injected private exception/token/payload markers are absent from machine failure reports. No false PASS was found within the trusted gate's required scope.

All136 test Python files reconcile:67 required +17 support +2 negative fixtures +39 out-of-scope +11 unsafe/live-dependent. Required module membership exactly matches the union of886 pinned nodes. Unsafe/live modules are not positive execution evidence; selection attacks replace them with inert sentinels and reject before child startup. The12 archived modules outside tests/ are separately accounted for rather than concealed in136. No inventory authority is regenerated during acceptance.

## Security safeguards

PASS: authenticated/nonblank/exact readiness; no readiness start/retry fallback; credential/transport startup validation; no-follow post-create ancestry; bounded retained WebSocket ownership; disabled automatic resource/default activation; dictation/public-example opt-in and privacy negatives; Simulator/ExecutionPipeline separation; timestamp overflow normalization; owned APScheduler cleanup/partial retry/cancellation/restart fencing; sanitized structured evidence; durable receipts, ledger/checkpoint and recovery boundaries. SECURITY-REVIEW.md gives implementation/test links.

Real installed APScheduler3.11.3 cleanup cases run alongside explicitly synthetic backend/protocol/future fixtures. The14-case scheduler-hardening module is not14 production backend qualifications. Native/custom/thread resources, providers/audio/hardware and physical power loss remain unqualified. No merge-specific app behavior or safety-sensitive source conflict was found.

## Dependencies and evidence guarantees

All266 source-input bytes match both merge and approved-da67 Git blobs, engineering pre/post maps, original snapshot and fresh snapshot. Fingerprint da3f737d827f7e33cc18e82a6dee65808af399823a8ac7b9a1db829055667373. Required inventory digest bc7359fc23710f82d780943e15c10a45d4df53380884c84c92699c3bc6139f15; module policy287ab432aa03ac8750a6c58257627077c097e80f98794eaf25c058d6acbdcd1f. No legitimate inventory update is required for this unchanged input tree; any future source/policy change needs explicit review.

Expected technical digest **`c2ebb33e9c88fa62afc5f6cb9efc1de6c5c2e65557fa7d4a7e68ae78cf9895a7`** matches187 entries. The outer full packet has200 matching entries, including the technical seal/narratives; all201 child paths equal Git objects. Each fresh acceptance seal has123 matching entries. Narrative evidence created after the merge truthfully names the already committed tested merge; the child does not alter its source. The technical/outer seal distinction avoids recursive self-reference and is accurately disclosed.

Qualified127 installed distributions exactly match engineering metadata (113 dist-info +14 egg-info), including APScheduler3.11.3. No package was installed/upgraded. Broad lower bounds such as APScheduler>=3.10.0 do not qualify arbitrary versions; dependencies/interpreter/backing bytes remain trusted, not attested. Historical b199ace Git objects required by the before contract are available offline and must not be bypassed in a shallow export.

Snapshot files0444/directories0555 and actual read-only namespace binds protect tests from ordinary source writes. Output is separate0700/owner-restricted; only fault copies become writable. Both266-input snapshots and reviewed source remain unchanged after all probes. These are local integrity checks, not independent signing/custody or tamper-proof preservation. Same-UID/root, trusted Git/runner/pytest/plugins/interpreter/dependencies can fabricate a consistent local set or transiently interfere; pre/post hashes do not exclude that. Obtain independently held digest custody before a later decision.

**F3 — LOW, post-update verification runbook constraint.** The snapshot launcher requires the entire tracked checkout to be clean, including tasks/loop-log.md. Canonical intentionally has a preserved dirty administrative log, so invoking that launcher directly in canonical after a ref-only update would reject. Do not stash/reset or silently commit the log to bypass this. Verify actual canonical HEAD/tree and all266 public input bytes, then run fresh acceptance from a new clean detached checkout of that exact HEAD with output elsewhere. This procedural correction preserves work and requires no alteration of the pinned merge.

## Conditions before canonical integration

**C1 — packet/discovery decision.** Preferred closure is quarantine the12 historical test modules as non-collectible evidence or add a reviewed discovery boundary. That changes the candidate: produce a new pinned tree, re-evaluate affected hashes/tooling and run full fresh acceptance/independent review; this audit never approves a silent substitute for6341648. Alternatively, the repository owner must explicitly accept the exact current tree as a **Gate-only offline development checkpoint**, record its forensic archive policy, and treat generic root pytest/archived-module execution as unsupported until separately remediated. This is a scope decision, not a claim that a prose policy technically excludes those files.

**C2 — safe test entrypoints.** The old broad CI command is not covered by this approval and must not be invoked as safe acceptance. Before any main/CI qualification, separately review/remediate its unsafe selection and environment. For an unchanged6341648 local development-only update, authorization must explicitly bind testing to the qualified enrolled offline gate and exclude broad legacy/live/config-mutating suites. No push/main/CI/provider activation is authorized here.

**C3 — exact source/environment/custody.** Canonical must still equal `b09fa10a661c9704f51e900ec857a51153cbcbbe`; use the recorded qualified dependencies (especially3.11.3) and retain the named evidence digest independently. Any source/parent/environment change requires new review and exact-tree acceptance. Do not treat broad requirement ranges or matching unsigned hashes as supply-chain/custody proof.

**C4 — separate human decision and post-update verification.** Human authorization must name the exact merge, both parents, tree, digest, target branch and accepted C1/C2 scope decision. It must exclude the evidence child and all infrastructure/live operations. After any separately authorized ref update, verify canonical HEAD/tree/input fingerprint, inventory/dependency versions and preserved local work; first compare actual canonical public-input bytes to the approved Git tree, then run complete fresh offline acceptance from a NEW clean detached checkout of that exact canonical HEAD into a NEW separate output. The dirty administrative log must be preserved and must not be stashed/reset/committed merely to pass the launcher clean-checkout preflight. A changed tree invalidates this approval. Preserve Git history; use a separately reviewed compensating revert if later needed, never force-reset development.

Until these conditions are explicitly closed, this is not an unconditional recommendation to authorize a merge. The exact application/required-gate result passes; repository-level test-entrypoint/inclusion governance remains conditional.

## Next operator action

Resolve/record C1–C2 first: preferred non-collectible archive and safe-entrypoint remediation requires a new reviewed candidate; a consciously bounded unchanged Gate-only development checkpoint requires explicit owner scope acceptance. Then obtain a separate exact-commit human decision using HUMAN-AUTHORIZATION.md. Do not merge during this audit or authorize an unreviewed altered tree/evidence child.

No canonical merge/reset/rebase/cherry-pick/push, deployment, VM/Proxmox/provider/network/credential/package/privileged/Gate6K action occurred. Only separate audit output, a new detached audit checkout and the mandatory append-only completion log are written. Existing reviewed source/evidence and sealed/frozen worktrees remain unchanged.
