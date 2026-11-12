# Final independent integration acceptance audit

**Verdict: APPROVE FOR CONTROLLED CANONICAL INTEGRATION PROPOSAL.**

The exact rehearsal evidence and freshly rerun offline gates support preparing a separately authorized, isolated canonical development integration proposal. No current required-test or preserved-safeguard blocker was established. This verdict authorizes planning/proposal review only; it does not authorize a canonical merge, deployment, privileged execution, Proxmox/VM activity or Gate6K.

Reviewed rehearsal: `674aff2c25d050420145f9b102808f194f0544fa`, branch codex/jarvis-v2-final-integration-rehearsal-r2. Its sole parent is approved source `da67d936566d330fad02fa8f23f8e1be2d4b80ad`. Canonical remains `b09fa10a661c9704f51e900ec857a51153cbcbbe`, branch docs/p7-d06-d07-passive-review. The reviewed worktree remained committed and clean throughout this audit. Audit output is separate under canonical tasks/jarvis-v2-final-independent-integration-audit; no reviewed source or manifest was changed.

Earlier engineering/review context is inherited in this conversation. This is a separate verification pass with fresh execution, an independently written evidence verifier and additional attacks; it is not a fresh-context organizational audit or independent evidence custody. Neither a requested role name nor local hashes establish those stronger guarantees.

## Required decisions

| Area | Result | Independent basis |
|---|---|---|
|Rehearsal evidence integrity|PASS|All171 packet files inventoried/read,83 JSON files parsed;170 outer hashes and123 acceptance hashes verify; every packet file equals its pinned Git blob.|
|Enrollment and test completeness|PASS for reviewed offline scope|All136 Python files classified and hashed;886 exact required identities reconstructed, with successful ordered setup/call/teardown.|
|Preserved security safeguards|PASS|Application source matches reviewed Reliability R3 and reconciliation; nine source differences from canonical inspected and covered by fresh tests.|
|Source preservation|PASS|266 approved-source Git blob hashes equal original/fresh snapshot and source before/after inputs; reviewed worktree clean; refs preserved.|
|Independent immutable custody/signing|NOT ESTABLISHED|Owner permissions/read-only mounts and unsigned local hashes do not establish custody or signing.|

No digest mismatch, missing required proof within the defined input set, unjustified rehearsal source change or new security-test replacement was found. The original rehearsal verifier was not trusted as the sole proof; verify_independently.py imports no engineering verifier, inventory loader or application.

## Exact ancestry and change scope

The rehearsal commit adds exactly171 expected packet artifacts and no application/test/script/config/dependency/inventory change. Its CHANGED-FILES list equals the actual Git diff and file set. Approved-source Git tree is `9cc1a9ecc3134b2f835017f6b5b0a55d215cebb4`; the later rehearsal tree differs only by those artifacts. Fresh acceptance records the actual rehearsal commit/tree, while all266 acceptance bytes independently match da67d936. Thus the differing metadata commits are correctly explained, not silently relabelled source.

Canonical has **not advanced** since rehearsal. Shared ancestor is `b738a473d27471f35df60d31ccd93047bf9d1a6e`. Canonical changed128 audit/log paths after that ancestor. Approved source changed761 paths; rehearsal adds171, making932. Both source/canonical and rehearsal/canonical changed-path intersections and file/directory prefix collisions are empty. Canonical has no committed runtime delta since that ancestor, and no dirty or untracked runtime files. Its pre-existing uncommitted tasks/loop-log.md is administrative and must remain preserved.

RC1 (`e9b4734740070b9e7c990735e43801e592c114c6`) and Reliability R3 (`b0c8865a93608bae748445b38a3ea50175796806`) are historical reviewed source lineages, not invented ancestors of the reconciliation branch. All app/ bytes in da67 match R3 and reconciliation5c878448a. `18a9d82c` precedes da67 and changes no accepted runtime inputs relative to it. No sealed/VM164/bootstrap path occurs in the rehearsal diff or source changes after the common baseline; RC1/earlier reviewed refs remain unchanged. No frozen/sealed artifact was modified by this audit.

An initial final-preservation diagnostic incorrectly expected every unrelated worktree to be clean. Detached JARVIS-release-r1 has40 modified files; the exact modified-path list already appears in rehearsal INITIAL-STATE/PRESERVATION. No head changed, no edit there was made or approved, and the current path/status list matches. It is not the clean frozen Unified RC1 worktree or the approved source. PRESERVATION-DIAGNOSTIC.json retains the failed non-acceptance check and FINAL-PRESERVATION.json records its resolution. Unrelated dirty bytes were not independently hash-pinned at audit start, so their byte identity is not claimed. These concurrent edits must remain outside this proposal unless separately reviewed.

No Git merge was attempted, so absence of overlap is path analysis, not a claimed successful merge. Semantic differences were separately reviewed: credentialed ready is restored; unsafe automatic defaults are disabled; ancestry and startup checks strengthened; WebSocket owners retained; Simulator protocol guard/timestamp normalization/owned scheduler cleanup added. Authority API authentication and persistence SQL schema are not replaced. Existing runtime configs are private and were not accessed; old explicit user settings are not automatically migrated or qualified by safe example defaults.

## Fresh independent acceptance

| Suite | Pass | Fail | Error | Skip | Missing / incomplete | Gate / child exit |
|---|---:|---:|---:|---:|---:|---|
|coverage|217|0|0|0|0|0 / 0|
|reconciliation|66|0|0|0|0|0 / 0|
|r3|19|0|0|0|0|0 / 0|
|r2|45|0|0|0|0|0 / 0|
|original|32|0|0|0|0|0 / 0|
|existing|507|0|0|0|0|0 / 0|

**886 distinct positive identities**; all required collection/execution sets exactly match the pinned inventory. No duplicate, substitution, missing item, collection skip/deselection, unexpected report, timeout or incomplete session/phase is accepted. Seed16401 positives and seed42 repeats are checked separately. **379 seeded repeat executions** pass (217+66+19+45+32), excluded from886. These are fresh results, not reuse of the engineering acceptance.

Fresh22 gate contracts,14 retained negative contracts,11 enrollment adversaries and12 replayed audit attacks all meet their expected outcomes. Contract positive controls and deliberately negative runs are not counted as additional unique application tests. Original R2 again reports PASS/exit0 for31 executions/zero skips; the current gate reports FAIL/exit1 and14 missing requirements despite child exit0. VERIFICATION.json lists all14 absent trusted identities.

Six additional CLI probes pass: five negative cases (late run-loop omission, late skip, late xfail, early clean exit and pytest.ini keyword filtering) reject with gate exits1/1/1/2/1 while each child exits0. A late omission has0 missing collection identities but216 passes/1 incomplete execution and fails. Keyword filtering produces210 passes/7 missing and fails. The positive poisoned-environment control ignores host PYTEST_ADDOPTS/PYTEST_PLUGINS through the cleared child environment and completes217 cases. Those217 supplemental repeat executions are disclosed separately, excluded from886 and the379 seeded repeats.

Three additional tampered-report copies (wrong count, missing phase, locally rewritten seal) fail comparison with the original pinned report digest and execution invariants. This proves detection relative to retained original bytes; it does not prove protection from a writer who controls reports and all trusted digests/Git references.

The real installed APScheduler3.11.3 cases exercise executor/store failure, retained ownership, cancellation, partial retry and restart fences. The14-case scheduler-hardening module also contains synthetic backend/protocol cases; it is not14 production backend qualifications. No hardware, live provider, native/thread/custom executor, real credential or physical power-loss qualification is claimed.

## Enrollment scope

All136 test Python files are accounted for:67 required +17 support +2 intentional negative fixtures +39 out-of-scope +11 unsafe/live-dependent. The prior84 exclusions were84 offline-labelled plus2 separately hardware-labelled;36 promoted +50 remaining equals86, without new or missing files. This audit introduces no enrollment changes. ENROLLMENT-REVIEW.json includes every path, disposition, reason, hash and required node list.

The67 required modules exactly equal the union of positive inventory modules. Required nodes are independently pinned; discovery cannot lower requirements. Added/deleted/modified modules, changed classifications, substituted/duplicate identities, collection-time skipping and missing terminal phases reject. The proposal utility remains separate and is not run by acceptance. Unsafe/live-dependent modules have no executed required identities; explicit unsafe-selection attacks reject before child launch and replace the unsafe module with an inert sentinel, avoiding effects even under a defective guard.

The39 out-of-scope and11 unsafe decisions remain the independently approved, disclosed backend/reliability scope, not whole-project qualification. No new source/scope change calls for their silent reclassification. Future frontend/hardware/provider/host-enforcement scope requires a new enrollment decision. Test locations outside tests/ are not automatically governed by this policy.

## Integrity and trust boundary

Original and fresh acceptance each verify266 tracked public input files and123 acceptance hashes. Input fingerprint is `da3f737d827f7e33cc18e82a6dee65808af399823a8ac7b9a1db829055667373`. Manifest digest `bc7359fc23710f82d780943e15c10a45d4df53380884c84c92699c3bc6139f15`; module-policy digest `287ab432aa03ac8750a6c58257627077c097e80f98794eaf25c058d6acbdcd1f`. Rehearsal outer-manifest digest is `c496f52e3cbea829fdde5a24e99a83ac2444eb1b77052a0e0aa170336e49636c`.

Fresh snapshot `/tmp/jarvis-coverage-acceptance-3p85tini/source` and the earlier snapshot retain no write bits; actual tests use read-only namespace mounts. Output is separate and owner-restricted. Fault copies alone become writable. Post-probe checks find both snapshots and approved inputs unchanged. Reports record commands, process exits, identities, phases, counts and source hashes; all failing evidence is retained.

These are local integrity guarantees, not tamper-proof custody. Host/same-UID/root, interpreter, dependency/plugin implementation and trusted Git objects are assumptions. Before/after hashes do not prove absence of transient tampering; unsigned JSON and replacement hashes can be fabricated by a fully compromised trusted environment. The complete repository, dependency backing bytes and private configuration are not the266-input fingerprint. Public source paths/hashes are intentional report metadata; raw exception/token/payload markers are not exported. No independent channel custody transfer or signature was demonstrated.

## Ranked risks and required conditions

No critical/high current source defect or required-suite failure was reproduced. Remaining issues are:

1. **Medium — future dependency qualification drift.** requirements-core.txt permits APScheduler>=3.10.0, while this private-API cleanup adapter is qualified here only with locally installed3.11.3. Other dependencies also use broad lower bounds. Preserve the recorded local environment for the proposal; do not treat a fresh install/upgrade as qualified. Any version change requires explicit dependency review and complete requalification (or a separately reviewed lock/bounds policy).
2. **Medium — future merged tree not yet tested.** Textual non-overlap does not prove semantic compatibility or a future tree's behavior. Preserve canonical history and run full acceptance on the exact proposed combined commit, rechecking all source fingerprints/enrollment first. Any newer canonical source change requires explicit additional review; no stale approval may substitute.
3. **Low — local evidence custody.** Hold the final evidence digest outside this writer's control before making a merge decision; recreate restrictive outputs on fresh review. No custody/signing claim is made.
4. **Low — bounded coverage/operational limits.** Retain the39/11 exclusions and execution boundaries. Native/custom/thread backends, real providers/audio/hardware and private runtime configuration need separate qualification before activation.
5. **Informational — inherited review context.** Fresh technical verification is established; a policy requiring organizational or fresh-context independence requires another reviewer. Do not relabel this conversation as independent custody.

These do not prevent planning/preparing an isolated development proposal within the qualified offline environment. They remain mandatory constraints before a later canonical integration decision.

## Required next step and authorization

Follow INTEGRATION-PROPOSAL.md. The next operator action is to review this report/digests and separately authorize a NEW isolated proposal worktree from the rechecked canonical HEAD, preserving both histories. Prepare a normal merge candidate there only after that authorization, retain both parents, rerun complete exact combined-tree offline acceptance, then present its exact commit/tree and fresh results for a separate human canonical-merge decision.

No actual canonical merge is authorized by this audit. Required later authorization must name the then-current canonical commit, exact proposed merge commit and both parents, evidence manifest digest, successful fresh combined-tree results, and the canonical target branch. It must explicitly exclude deployment, VM/Proxmox operations, credentials, privileged execution and Gate6K. Any changed source/parent/environment invalidates that narrowly bound authorization.

No merge/rebase/reset/cherry-pick/push, deployment, network/provider/credential/package operation, privileged activation or VM164 action occurred. Only new audit artifacts and the mandated append-only canonical completion log entry are written; reviewed source remains unchanged.
