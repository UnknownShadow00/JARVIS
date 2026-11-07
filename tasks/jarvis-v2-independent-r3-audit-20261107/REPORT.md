# Independent Reliability R3 Acceptance Audit

**Verdict: APPROVE WITH CONDITIONS.** The original false-PASS defect is corrected for the explicitly enrolled suites. No remaining incorrect PASS for a missing enrolled identity was found. This permits preparation for controlled integration rehearsal subject to the conditions below; it grants no merge or production authorization.

Target: b0c8865a93608bae748445b38a3ea50175796806, branch codex/jarvis-v2-reliability-hardening-r3. The target worktree was clean before and after testing. This review reexecuted evidence and added independently written adversaries; it did not rely solely on the engineering verdict. Earlier implementation context was available in this conversation, so this is a separate verification pass, not a fresh-context organizational review.

| Finding | Verdict |
| --- | --- |
| Scheduler cleanup ownership | PASS within installed stock APScheduler3.11.3 boundary |
| False-PASS gate | PASS for explicitly enrolled required suites |
| Sensitive-information handling | PASS within reviewed public-source/trusted-plugin boundary |

## Original defect and correction

Fresh cli23/before-astra.json uses exact committed R2 runner/protocol bytes in a disposable copy. A module-level skip removes14 cases:31 execute, zero runtime skips are reported, and R2 incorrectly exits0/PASS. Fresh cli23/astra.json runs the same31 surviving cases but R3 reports required_missing14, a collection skip, FAIL/exit1 despite pytest exit0. missing14.json enumerates the exact14 missing full node identities, derived from the pinned inventory and omitted module. The machine report itself exposes aggregate missing counts rather than raw names, preserving its diagnostic privacy policy.

The fixture deliberately rebinds temporary instrumentation source hashes/digest to exercise runtime collection validation while preserving every required identity. Without that explicit fixture-only rebinding, modifying the module is rejected earlier by source validation. No reviewed worktree source or manifest was changed.

## Independent results

| Suite | Pass | Fail | Error | Skip | Incomplete | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R3 |19|0|0|0|0|0|
| R2 |45|0|0|0|0|0|
| Original Gauntlet |32|0|0|0|0|0|
| Existing selection |507|0|0|0|0|0|
| R3 seed42 repeat |19|0|0|0|0|0|
| R2 seed42 repeat |45|0|0|0|0|0|
| Original seed42 repeat |32|0|0|0|0|0|

603 distinct positive IDs were independently counted, all with successful complete setup/call/teardown and source pins matching reviewed files. The96 repeat executions are excluded from603. The23 adversarial CLI contracts and14 retained negative contracts reproduce successfully; these are separate from positive test totals. No discrepancy was found. Protocol tests are synthetic evidence checks, not additional real backend or production qualification.

Additional independent CLI probes (independent_probes.py / independent-summary.json):

- Removing an item in pytest_collection_finish, AFTER the runner's collection snapshot: BLOCKED/exit2.
- Substituting a node ID at that later stage: FAIL/exit1,44 pass plus1 incomplete. Collection agreement alone cannot conceal the missing execution evidence.
- Keyword filtering: FAIL/exit1,44 pass,1 required missing.
- An added identity in an enrolled module: FAIL/exit1 despite46 successful cases;1 unexpected identity.
- Changed pytest.ini: BLOCKED/exit2 before execution.
- Reduced manifest without matching trusted loader change: BLOCKED/exit2.
- Replacing the proposal utility with a raising sentinel: full45 PASS; acceptance does not invoke regeneration.
- Adding a new failing test file outside selected modules:45 PASS. This establishes the suite-scope limitation described below, not an omitted identity from the current authoritative inventory.

Five independently mutated child evidence objects (missing result, duplicate ID, wrong run challenge, extra private payload field, missing phase) all reject. report-tampering.json records results. These checks validate the in-flight protocol; they do not authenticate arbitrary later edits to saved JSON.

The fresh23-case matrix additionally exercises individual/parametrized/module omission, marker selection, real ignore traversal, importorskip, duplicate IDs, same-count substitution, xfail/xpass, collection-complete absence, absent execution results, abrupt zero exit, partial JSON, corrupt/duplicate/reduced manifest and changed source. Sanitization checks pass; independent injected private node strings are absent from machine reports. All negative gate exits are nonzero, including incomplete runs whose child exits0.

## Inventory and trust assessment

The manifest exists before the run. Its exact bytes are pinned separately in trusted loader source; suites bind complete raw public node identities and selected test/app/config hashes. The loader rejects byte corruption and duplicate/schema errors. Actual nodes map through the precomputed full manifest, so omitted parameter variants cannot renumber surviving cases into missing identities. Unexpected nodes receive opaque positional identifiers without exporting their names. Parent acceptance always supplies authoritative identities; the optional legacy validator argument is not a CLI bypass.

Collection-skipped/deselected counters and exact identity equality supplement ordered terminal phases, normal session completion, timeout state and real process exit. Expected identities cannot shrink automatically. Xfail and xpass are rejected. Exceptions are not interpreted as successful verification.

The proposal tool is separate and produces only a new candidate. Its collector comes from R2, so its output alone is NOT proof of full intended inventory: it can propose a reduced inventory if an entire module disappears. The documented independent review/diff procedure is essential; acceptance never calls this tool. Promotion requires changing both manifest and loader digest in reviewed code.

An actor controlling trusted loader/source/manifest or pytest plugins can forge success; cryptographic protection against that actor is not claimed or required here. Plugins/test code can report successful phases without meaningful assertions. The gate establishes execution as reported by the trusted pytest runtime, not semantic test adequacy. Source read-only mounts still reflect host writes: there is a check-to-use window. Pinning and running an immutable checkout/dependency set is an operational prerequisite. Environment clearing and plugin-autoload disablement reduce ambient influence, but installed pytest/plugin/interpreter code remains trusted.

Saved JSON is unsigned and not a replay-verification format. Changing its status after execution does not rerun validation. Use observed process exit plus protected artifacts and an independently retained digest. The run challenge binds live child evidence to the current invocation, not saved reports to an external verifier.

## Ranked remaining weaknesses and conditions

1. **P3 / low — suite enrollment is explicit, not repository-wide discovery.** A new file outside the hardcoded selection is silently outside acceptance, even if it contains a failing test. Existing enrolled-file edits are hash-fenced and new collected identities are rejected. Before integration, explicitly adopt/document the selected-suite scope and require every new test module to receive a reviewed enrollment or exclusion decision. Do not advertise603 as all repository tests. If repository-wide new-file refusal is desired, add and independently review a discovery-coverage policy first.
2. **P3 / low — source/dependency immutability and evidence custody are operational.** Source checks do not snapshot files; saved reports are not signed. Before rehearsal, use a clean immutable combined checkout and existing qualified dependencies, retain process exits and artifact digests outside mutable report files. No protection against a fully compromised host is asserted.
3. **P3 / low — proposal generation can inherit partial collection.** Never automatically promote generated inventory. Review removed identities and module coverage against the intended change; updating both manifest and digest must remain an explicit policy decision. This is documented and does not reopen runtime acceptance.

No critical/high/medium defect was established in the current enrolled-suite acceptance path. The conditions constrain interpretation and integration workflow; they are not production qualification.

## Regression and integration safety

All application bytes are identical to R2, including scheduler/backend, Authority, Simulator, timestamp handling and authorization. Fresh R2 tests exercise actual locally installed APScheduler3.11.3 resources with injected cleanup faults, partial retries, cancellation, timeout and immediate restart. Original32 and existing507 retain protocol/timestamp/authorization regression coverage. No custom executor/native-thread cancellation or live backend qualification is inferred.

The committed diff is269 paths: six runner/inventory/test paths and263 packet files. The packet was inventoried and JSON parsed; all268 integrity-manifest entries verify. No unrelated application or VM164 packet change occurs in the R2-to-R3 diff. Frozen Unified RC1 remains clean at e9b4734740070b9e7c990735e43801e592c114c6. This audit did not execute or rewrite any sealed VM164 packet; lack of changed paths is not live packet qualification.

Before controlled integration, build a separately authorized RC1-compatible combined candidate rather than copying into dirty canonical main. Review any source-hash/inventory updates explicitly and rerun all603 positives, seeded repeats and negative matrices on that exact candidate. Coordinate ongoing host-enforcement work; no direct path overlap establishes combined semantic safety. Obtain the separate operator decision for integration.

Audit artifacts are isolated in canonical JARVIS/tasks/jarvis-v2-independent-r3-audit-20261107. The mandatory canonical completion log is append-only. No reviewed source, manifest or commit was modified; no network, dependency download, credential action, Proxmox/VM/provider/production access, privileged activation, Gate6K qualification, merge/rebase/cherry-pick/push or deployment occurred.
