# Independent Stage 2 remediation R2 audit

**Verdict: REJECT.** R2 fixes the ten original narrow audit reproductions, but its admission and result validators still accept stale, temporally contradictory and incomplete evidence. The complete procedure is not ready to present for human authorization. Correct these defects in a new versioned packet and repeat independent review. This verdict authorizes no host operation.

The reported engineering results were independently reproduced: original71 pass; original audit20 pass/10 fail; all30 audit assertions pass against R2; all95 new R2 methods pass; the published synthetic12-case artifact passes R2's validator. Those counts are accurate for those suites. **Additional independent probes:51 tests,35 pass,16 fail, zero errors/skips.** The failures are required safeguards that R2 does not enforce, not test infrastructure errors or actual host incidents.

## Decisions on the seven original findings

| Finding | Decision for the complete requested safeguard | Independent conclusion |
|---|---|---|
| A / F01 — NSS and sudo locality | **PASS — offline design only** | Network-capable getent/id/sudo calls are removed. File-only gate rejects network/ambiguous NSS, missing policy prerequisites and unknown environment sources. Independent complete local policy/mount/module/custody proof remains mandatory; passwd alone grants no assurance. |
| B / F02 — bounded reads and timeout failure semantics | **FAIL — partial fix** | Size-first descriptor reads, bounded gzip, resource ceilings and explicit client budgets pass inspection/probes. General command receipts reject timeout. However collision evidence can explicitly carry timeout=true and still pass; not every qualification evidence path enforces timeout failure. See R2-A03. No decompression-bomb bypass was found. |
| C / F03 — collision validation | **FAIL — partial fix** | Original malformed-string bypass is fixed. Renderer accepts a60-second-old collision proof for a new plan; collision result accepts a duplicate issued after firing with earlier waiting snapshots. See R2-A01/A03. |
| D / F04 — cleanup ownership and freshness | **FAIL — partial fix** | Exact base/boot/pair/argv restrictions and scoped repeated/interrupted cleanup pass. Fresh claimed observation time can mask raw-show receipts879seconds older, and final cgroup proof need not contain raw capture/receipts. See R2-A01/A05. |
| E / F05 — rearm-a cancellation | **FAIL — partial fix** | Direct fired-rearm-a acceptance is corrected, and old-generation/UID/boot checks work. Actual stop receipts after D+10s can pass an earlier claimed cancel time; an empty journal captured before cancellation can be asserted complete through closure. See R2-A01/A02. |
| F / F06 — inherited environment | **PASS — conditional offline design** | Minimal parent/unit environment, resets, preactivation manager/loader/drop-in review and non-root guard improve the original design. Unknown variables/review block. No real environment was inspected; exact manager-generated variables and257 behavior remain prerequisites. |
| G / F07 — complete evidence bindings | **FAIL — partial fix** | Many missing/mismatched fields and altered artifact bytes are rejected. Chronology, exit/state consistency, raw cgroup evidence and top-level review-seal coverage remain incomplete. See R2-A01/A02/A04/A05. |

**Corrected twelve-case procedure: FAIL.** Its non-root/non-VM scope, explicit window, command budget table and no-extension recovery policy are sound design constraints. Its validation contract is incomplete, and R21's literal path validator rejects `/` despite the mandatory root-ancestry inspection. The per-case review is in CASE-REVIEW.md; exact counterexamples and source locations are in FINDINGS.md.

## Principal remaining defects

- R2 can accept records in which timer creation occurs after its deadline and after its supposedly waiting observations. It also accepts old show/journal receipts as current evidence and ignores journal monotonic timestamp inconsistency.
- Rearm-a cancellation can pass despite stop receipts occurring after its deadline, or an unexpected service failure. The `late` case accepts a callback timestamp after the approved window and after final capture.
- A success case can retain ActiveState=failed or contradictory ExecStart exit7 while being accepted as success. A failedtimer case can show a later service invocation/exit7 and still pass its no-execution qualification.
- The external case-artifact seal does not cover top-level privilege-review references. Changing the VM-authority review hash leaves that seal unchanged and is accepted. Raw cgroup capture/exit/timeout evidence is not required.
- The renderer's collision proof is not freshness-bound to the new proposal. The required R21 root-path command cannot complete as written.

The review does **not** claim an attacker bypassed SHA256 or authentic external custody. Most probes deliberately rehash internally contradictory synthetic records so the validator must assess their semantics. One distinct probe changes a top-level review reference while retaining the original external evidence seal. This separates missing consistency checks from provenance that cryptographic hashes cannot independently establish.

## Timeout, cleanup and authorization assessment

All proposed external-operation classes have explicit caps:10s ordinary read/manual/journal (journal/manual output8MiB),20s installer,5s create/duplicate/show/cgroup/stop, plus2s kill/reap reserve. Ordinary-read/show/create/stop output is1MiB, stderr64KiB. Future Python helpers apply128MiB address-space,3s CPU and64FD limits; the unchanged R01 relies on the recorder. Command admission checks both UTC and BOOTTIME and the full cap/reserve. The inspected APIs produce proposals, not host execution.

These are conditional software controls, not an independently tested recorder or physical expiration guarantee. Killing a client cannot prove manager transaction cancellation, nor can Python guarantee interruption of kernel I/O. Collision proof and result chronology defects prevent claiming end-to-end timeout/freshness guarantees. Exact-owned stop scope passes; complete cleanup proof does not.

The written window is <=2700seconds, creation cutoff35minutes, final cleanup by40minutes and closure before45minutes. Expiry prohibits commands under that grant, including cleanup. Any later recovery needs new finite readback/stop-only authority for exact previously owned names; no automatic extension, restart/rearm, other-unit action, deletion or VM operation is allowed. This is a correct authorization policy, but the late-callback/result chronology checks do not fully enforce its evidence contract.

## Scope, preservation and independence

Audit task class: strict/read-only review of the target trees. Only this new audit folder, disposable synthetic fixtures and the required append-only project log are written. Existing runtime permissions were not changed; the replay harness adds filesystem mutation, process/network/signaling and NSS/private-path tripwires. No Proxmox/systemd/VM command, R01, callback installer, host inspection, network/provider request, credential action, package install, root shell, deployment or Gate6K was executed.

Read/hash-indexed all207 files across R2(67), preparation(29), rejection audit(15), and sealed R3(96); parsed JSON and Python sources; reviewed the reports, actual command bodies, tests, callback, codec, catalogue and retained primary-interface evidence. Integrity verifiers pass, including R3's original source/callback and predecessor chain. All207 files remain byte-identical. Tracked canonical changes remain confined to the preexisting/append-only task log; canonical application code has no diff. See PRESERVATION-AND-LIMITS.md.

This is a new technical audit pass with independent adversarial assertions, not an assertion of a different authenticated model or human signoff. The conversation includes the preparation history. Local seals and test logs establish reproducibility and byte consistency; they cannot independently prove every historical external action did not occur. Engineering source/logs reviewed contain no evidence of live operations, and this audit performed none.

## Readiness and next action

**Not safe enough to request authorization for the complete R2 procedure.** Fix R2-A01 through R2-A06 in a new immutable revision, preserve the failed audit and all earlier evidence, then independently re-review. Fresh host prerequisites are listed in HOST-PREREQUISITES.md; they are not substitutes for these offline fixes.

**Now: no supervised host action.** After a corrected revision is independently accepted and separately authorized for a finite window, the first proposed action remains the exact read-only R01 array copied into FIRST-SUPERVISED-ACTION.json. It reads only boot ID, UTC and paired BOOTTIME/MONOTONIC clocks after console/interpreter/recorder/budget prerequisites. It was not executed. Stage2 remains NOT AUTHORIZED; actual systemd257, clock mapping, WakeSystem, cancellation, cleanup and failure timing remain unqualified.
