# JARVIS V2 unified offline RC1

**PASS for controlled offline synthetic lab testing. Live/VM164/production and
privileged Gate 6K readiness remain BLOCKED.**

Release `jarvis-v2-unified-rc1-345626bddd36028e` integrates the execution/recovery application and
latest security remediation. The actual merged build passed **1,023 distinct
pytest cases**, zero final failures/skips, **37 crash cases**, **20 application
scenario groups** and **13 benchmarks**. Nine hardware/desktop cases are explicitly
excluded. Historical totals were not added together.

## Exact source and release

- Git revision: `e9b4734740070b9e7c990735e43801e592c114c6`.
- Base: `f4cac30259a7bf4610add2063679ae49138ee637`; branch `release/jarvis-v2-unified-rc1`.
- Exclusive worktree: `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-unified-rc1`; clean after the two integration/source-fixture commits.
- Source manifest: `345626bddd36028e791e07233e280ee45519ef1ad07f8d8509fe52542f267bd8`; 315 allowlisted public files, including 102 application Python files.
- [Release archive](release/jarvis-v2-unified-rc1-345626bddd36028e.tar.gz), 399138 bytes.
- Archive SHA-256: `373948f3b6592f116ba0623afbb0ec04656c572bb07254ce8dae713795b3eaf1`.

[BUILD](release/BUILD.json), [source revision](SOURCE-REVISION.json),
[source hashes](SOURCE-SHA256.json) and [source patch](SOURCE.patch) bind committed
bytes. The archive was rebuilt deterministically and every member verified.
One previously ignored public CSV fixture from Codex1 was committed unchanged,
including original CRLF endings, to make every archived source byte addressable
by the Git revision. This changed no tested application/test/configuration byte.

## Reconciliation and implemented fixes

Both candidates were dirty snapshots of the same Git base, not two separate
commits. Codex1's 306-file frozen candidate and Codex2's 398-file snapshot differ in 36
common files. [BASIS.json](BASIS.json) records original identities; the
[408-row integration matrix](INTEGRATION-MATRIX.md) and JSON companion preserve
file-by-file decisions/hashes and all exact differing alternatives.

All four headline security fixes already existed in Codex1 in some form. The
unified source retains Codex1's stronger bounded WebSocket send/close and active
connection accounting; integrates Codex2's asynchronous exact Bearer check and
whitespace-token refusal; combines race-refusing descriptor-relative directory
creation with post-create ancestor verification; and combines Docker's COPY-input
allowlist with nested private/config/credential exclusions. Safe offline class
and example defaults remain disabled for host controls, boot, dictation and traces.

Codex2's expanded WebSocket/auth tests were merged without removing Codex1's
stronger release boundary cases. Independent review found a real startup mismatch:
whitespace-only tokens could start an explicitly bound synthetic transport worker
although HTTP authority refused them. The lifespan now rejects them before
scheduler/worker activity; three new negative tests verify cleanup and zero dispatch.

Every authority route, including `/ready`, requires a configured nonblank matching
Bearer. The merged `app/cli.py` provides a fail-closed credentialed `ready`
command with 12 tests and an actual readiness-payload application demonstration.
Existing task/recovery clients send credentials; reporter uses bound in-process
Authority; PWA/Electron do not call `/ready`; Compose probes `/health` liveness.
Operator guidance now names the authenticated command. No anonymous compatibility
fallback was introduced. Installed external clients/probes remain unqualified.

The canonical development checkout and original release worktree were preserved.
Integration happened only in the exclusive sibling. No dirty tree was reset,
replaced, stashed or promoted, and no predecessor evidence was rewritten.

## Current merged-source verification

| Final mode | Collected cases / inventory | Wall seconds |
|---|---:|---:|
| benchmark | 13 benchmark cases | 49.08 |
| broad-collect | 952 | 1.48 |
| broad-legacy | 17 | 3.56 |
| broad-safe | 525 | 29.85 |
| broad-security | 36 | 7.78 |
| core | 254 | 96.87 |
| enrollment | 59 | 17.66 |
| focused | 60 | 42.49 |
| full-app | 103 | 26.58 |
| recovery | 72 | 66.54 |

The inventory contains 952 repository cases: 943 pass and 9 are excluded. An additional
80 retained authority/router/process packet cases pass, giving 1,023 unique cases.
Full-app's 103 pytest cases and Codex2's 179 selected cases are repeated subsets and
are not added. The selected groups are 120 HTTP/WS/auth/storage, 33 execution/lifecycle,
13 transport and 13 durability cases; they exercise the original 168-case selected
coverage plus retained stronger/new regressions. Codex2's four shared-history
scenario groups and distinct native client/server socket fixture also pass afresh.
The 20 application groups remain the reported scenario count; repeated demos are
not counted as new unique scenarios.

[RESULTS.json](RESULTS.json), [test inventory](TEST-INVENTORY.json),
[all normalized outcomes](TEST-OUTCOMES.json), [selected security results](SECURITY-SELECTED-RESULTS.json),
[synthetic demonstration](SYNTHETIC-DEMONSTRATION.md),
[crash evidence](CRASH-RECOVERY.json) and [security crosswalk](SECURITY-CROSSWALK.md)
provide exact source/input hashes, node IDs, exclusions and run attribution.
Random fixture UUIDs are normalized for case identity; original node IDs remain
retained and repository normalized identities are collision-free.

The main final modes recorded 10 warnings: the same two upstream Starlette/httpx
and AnyIO deprecations across five modes. Selected replays recorded 5 warnings,
and the additional integrated replay emitted one timezone-default-to-UTC warning:
16 final warning occurrences, three distinct messages. All are retained in
WARNINGS.json, SECURITY-WARNINGS.json and raw artifacts. No warning was called a pass.

Unsuccessful attempts are retained and excluded from acceptance: initial test
union had three incorrect malformed-frame close-code expectations, corrected to
1008 while binary remains1003; an instrumentation hook failed validation before
running any core tests, then was corrected. Earlier source-bound passes preceding
the final startup fix are not selected. No application regression remains open.

## Independent review and integrity

A separate read-only reviewer reviewed the merged trust boundaries and source,
found the startup gap above, and reviewed its correction plus final documentation.
No remaining critical/high/medium defect was found in that reviewed source.
[Independent review](INDEPENDENT-SECURITY-REVIEW.md) and 39 exact source/test/doc pins
are checked against the archive. Execution results are separately attributed to
the lead engineer; predecessor reviews are not inherited as approval.

The synthetic demonstration joins actual lifespan, API identity, witnessed enrolled
Authority, queue, scheduler callbacks, independently permitted signed AF_UNIX pure
execution, receipts, cancellation, lost-response UNKNOWN, FD-only CLI reconciliation,
restart publication hold, separately permitted publication, inert archive restore
and nonactivating durable approval. It retains original UUIDs and makes zero
redispatch calls after uncertainty/restart. Crash evidence includes 15 signed-transport
and 22 registry/witness SIGKILL cases on current source, not physical power loss.

All heavy payloads ran sequentially in unshared network/user/mount/PID/IPC/UTS
namespaces with no host runtime state, credentials, devices or service sockets.
Main guards remained AS1GiB/process, aggregate RSS768MiB, CPU120/121s, wall120s,
FD64, core0, controlled storage256MiB/20,000 files. Selected security replay guards
remained AS512MiB, CPU10s, wall25s, scratch32MiB, output256KiB, FD96/processes64.
No final guard stop occurred; no limit was raised.

Predecessor preservation covers 177,460 initially existing task files, original
symlinks, the canonical log prefix, known shared public source and 306 predecessor
worktree source files. The final read-only verifier checks them again. Artifact
hashes are retained in SHA256SUMS; independent external retention is still needed.
Same-UID file controls are not WORM storage or public-key signatures.

## Dependency/configuration status and exclusions

Main application runs verify the retained exact 28 dependency target before use;
broader modes add three pinned/RECORD-verified wheels. The source archive embeds
the 31-package offline lock and retained artifact hashes in BUILD.json. The selected
security harness additionally pins 15,998 files in its pre-existing 127-distribution
local target before and after every final replay. Fresh metadata consistency
checked 107 applicable requirements with no missing/incompatible dependency;
`pip check` passed. Safe public configuration and Electron lock parsing passed.
No package was installed, upgraded or downloaded.

**Fresh advisory qualification is not passed:** pip_audit is absent in the qualified
cage; offline npm audit hit the fixed 512MiB address-space limit during Node startup.
The errors are retained in DEPENDENCY-CONFIGURATION.json, not suppressed or called
clean audits. Current intended dependencies/native binaries/advisories are a live
deployment blocker. AST parsing covered 240 public Python files and diff whitespace
checks passed; a full typechecker, linter or line/branch coverage percentage is not
claimed. Docker rules/COPY inputs were reviewed statically; no daemon build ran.

The exact nine unexecuted cases are six `hardware_smoke_test` cases (TTS, sound,
VAD, STT, wake word, self suppression) and three desktop `test_vad_timeout` cases
(no speech, bytes result, short timeout). TEST-INVENTORY.json lists exact node IDs.
The manual Ollama helper has zero test functions and is excluded before its
optional SDK import; it is neither a pass nor a skipped test. Real desktop/audio,
GPU/model providers, browser/ingress/TLS, physical power loss, real VM/broker and
privileged Gate6K tests remain NOT RUN.

## Readiness decision and next authorization

This candidate is ready for **controlled offline synthetic lab testing only**.
[Known limitations](KNOWN-LIMITATIONS.md) and
[exact authorization requirements](AUTHORIZATION-REQUIREMENTS.md) remain blockers
to live/VM164/production claims. Shared Bearer is one service actor, co-located HMAC
is not privilege separation, transport grants remain lifetime-capped/scan-based,
and actual independent custody/installed storage/UID/ingress facts are unresolved.

LIVE-READONLY-PROPOSAL.json binds the new candidate while leaving every actual UID,
grant, time window, machine/boot ID and installed acceptance field null. The sole
possible later action is one identity request through an already qualified
standalone VM164 broker, with a retained 32-hex protocol request ID and separate
operator authorization after prerequisites. If setup is absent, stop for the exact
separate staged setup request. Keep VM164 without a NIC. VM162, VM163 and the AI
server are outside scope. Privileged Gate6K qualification requires its own reviewed
identity-bound scope and authorization; no real JARVIS adapter or V3 is authorized.

No production startup/deployment, real executor/provider request, Proxmox/VM change,
credential/permission grant, real runtime migration or privileged qualification
occurred. Source links to task evidence resolve in the canonical JARVIS workspace
or retained evidence companion, not a standalone source-only extraction.
