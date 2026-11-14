# Complete twelve-case operator review

**Overall: FAIL for authorization readiness.** The intended non-root/non-VM scope passes. Case validation and mandatory preflight completeness do not. The following is a review of proposed commands only; none was executed.

## Common exact argument and prerequisite contract

The actual R2 command catalogue and literal bodies were inspected, not only their tests. For a future fresh session, `packet.plan(..., case, ...)['argv']` constructs the exact systemd-run array, with `--system --no-ask-password --expand-environment=no`, explicit base name/description, absolute `--on-boot=<D seconds with six fractional digits>s`, WakeSystem=yes, accuracy1us/no jitter, RemainAfterElapse=yes/Persistent=no. It includes Type=exec, User/Group65534, environment/credential/extra-command resets, the encoded non-root ExecCondition and the exact fixed payload after `--`.

No shell, VM program or root service payload occurs in these arrays. The sealed R3 root-worker timer builder is a different interface and must not be used for Stage2. The callback source SHA256 remains `a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa`; its source has no process/network/VM actuation interface.

Names remain `jarvis-vm164-r3-stage2-<fresh32hex>-<case>.timer` and `.service`. Actual nonce/boot/clock/deadline values are mandatory future inputs. Synthetic names/times are not presented as host arguments to execute. Complete exact arrays/bodies remain in the unchanged reviewed packet; this audit does not produce an alternative live command set.

All cases require independently reviewed local-only privilege/credential denial, existing UID/group/process proof, trusted interpreter/loader/minimal environment, callback path/hash/root custody, current namespace/UnitPath absence, owned pending-generation ledger, fresh clock/UTC budget, bounded recorder and separate signed authority. These are not established by the test fixture.

Common bounds: maximum45-minute session; new creation/duplicate/install stop at35minutes with at least6minutes remaining; case budget90seconds; D=current BOOTTIME+30seconds; create/duplicate/show/cgroup/stop5seconds each, clock/read10seconds, journal10seconds, installer20seconds, each with2seconds reserve. Service startup5seconds/runtime10seconds (timeout case3)/stop2seconds. Memory128MiB, tasks16, CPU10%, NOFILE64, CORE0. All final cleanup is exact-owned timer then service, no deletion/reset/wildcard/foreign dependency stop.

Raw requirements: actual command argv/exit/timeout/output and clock brackets; complete timer/service show and exact pairing/configuration; two waiting captures except failedtimer; full relevant journal bytes with boot/unit/UID/invocation/cursor/time; expected payload and actual waitid code/status; post-stop/final states, no jobs/PIDs, raw cgroup/process emptiness. Unexpected outcomes stop qualification, retain all evidence and trigger bounded owned recovery only while authorized. Host-expiry recovery needs new finite readback/stop-only authority.

## Per-case assessment

| Case | Exact payload/variant inspected | Expected result and special prerequisite | Evidence, deadline and independent result |
|---|---|---|---|
| success | Python `-I -B -S /opt/jarvis-vm164-r3-stage2/canary.py --approved-nonvm-callback --expected-source-sha256 <pinned hash> --mode success` | Same-boot UID/eUID65534 canary at D..D+1s, non-VM/root-bootstrap-false; Code1/Status0/Resultsuccess | Guard+canary+raw exits; observe by D+15s then scoped cleanup. **FAIL validation:** contradictory failed state/ExecStart exit and impossible creation chronology accepted. |
| exit7 | Same canary, `--mode failure` | Exactly one canary followed by Code1/Status7/Resultexit-code; failure is intentional | Same bounded observation/cleanup; no reset-failed. Expected negative exit handling passes controls. **FAIL complete evidence contract:** shared stale receipt/cgroup/seal gaps remain. |
| missingexec | Absolute nonce-qualified absent executable under public callback directory | Independently prove absence; guard then actual203/EXEC, Resultexit-code, EXEC diagnostic, no canary | If setup refuses before exec, remain BLOCKED_EXEC_NOT_OBSERVED. Do not install substitute. **FAIL complete contract:** shared gaps; real203 behavior unqualified. |
| missingdep | Isolated Python encoded `import jarvis_stage2_intentionally_absent_dependency_<nonce>` | Exact missing-module diagnostic, exit1/Resultexit-code, guard/no canary | Unexpected import success stops session; no module changes. **FAIL complete contract:** shared capture/closure gaps. |
| timeout | Encoded fixed Python numeric-ID/groups print, then sleep30 | RuntimeMaxSec3s; guard+probe; Resulttimeout, Code2/signal9 or15; no canary | D+15s ceiling, then exact stop and raw empty cgroup. **FAIL complete contract:** raw cgroup capture is not mandatory in accepted results. Actual signal/runtime behavior unqualified. |
| late | Encoded sleep2 then runpy of unchanged canary with exact argv | Exit0/canary>D+1s; expected lateness rejection, not a timing pass | Same finite case/window. **FAIL:** callback at session+2800s and after final capture is accepted. |
| inactive | Normal canary argv, timer stopped by D−5s | Waiting then no trigger/guard/callback/invocation through D+2s and closure | Cleanup exact-owned service as needed. **FAIL:** shared cancellation timing/capture coverage not receipt-bound. |
| failedtimer | Normal argv plus timer Requires/After for exact absent `<base>-absent.service` | Actual loaded failed timer/non-success Result, no service invocation or callback | Inactive/refused setup remains unobserved, not PASS; no dependency creation or stop. **FAIL:** later service invocation/exit7 is accepted despite no-execution contract. |
| collision | One extra submission of identical original create argv while waiting | Nonzero refusal; unchanged before/after definitions/deadline/invocation; one eventual callback |5s duplicate limit, pre/post raw proof. **FAIL:** stale renderer proof and duplicate-after-firing chronology pass. |
| cancel | Normal argv, exact timer then service stops by D−5s | Post-first-stop checkpoint; no execution through D+2s and closure; repeated cleanup is no-op | Scope/repeated/interrupted helper controls pass. **FAIL complete cancellation proof:** old empty journals/late stops can pass. |
| rearm-a | Same cancellation contract, retained tombstone | Never a successful fired case; remain unexecuted through B's final proof | Direct original false positive is fixed. **FAIL complete proof:** late stop receipts and unexpected resources failure accepted. |
| rearm-b | Distinct case name/generation, new future D within original window | Prior proved A cancellation; one new bound guard/canary/exit0; A remains inactive | Wrong generation/UID/boot controls pass. **FAIL complete sequence:** required earlier cancellation/action chronology is not bound end-to-end. |

## Procedure and interface constraints

R21 explicitly rejects `/`, so the mandatory step1.6 root ancestry check cannot complete as written. No in-session fallback should be invented. That defect alone needs an offline revision even before a timer is considered.

The command/reset syntax, ExecCondition representation, invocation continuity and raw normalized properties remain exact-version257 prerequisites. Existing local manuals/retained excerpts support interface-level reasoning; they are not live pve evidence. The parser also accepts only a narrow set of substates, so elapsed/transitional/garbage-collected unit handling must be reviewed before relying on cleanup. No unsupported-property fallback or parser relaxation is authorized here.

CLOCK_BOOTTIME scheduling with WakeSystem and the exported NextElapseUSecMonotonic domain are separate questions. Both clock hypotheses and tight measured offset must agree with exact-version evidence; equal clocks are not proof. UNKNOWN must fail. Physical wake, suspend/reboot/reexec survival, host failure expiration and VM termination remain outside scope. No host operation is needed or permitted to fix the independently demonstrated offline defects.
