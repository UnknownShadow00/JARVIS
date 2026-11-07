# Actual offline results

Final fresh combined run: **294 unique test methods,294 passed,0 failures,
0 errors,0 skips**. This is an executed regression result, not a sum of historical
claims. Detailed counters/logs: evidence/regression-release/RESULTS.json.

| Executed suite | Methods | Fail / error / skip |
|---|---:|---:|
| R3 author lifecycle/policy tests |60|0 /0 /0|
| R3 author adapter/store/clock/prerequisite tests |45|0 /0 /0|
| R3 independently written security tests |18|0 /0 /0|
| Preserved r2 remediation replay |87|0 /0 /0|
| Preserved bootstrap r1 replay |43|0 /0 /0|
| Preserved strict validator replay |32|0 /0 /0|
| Preserved legacy hazard reproductions |9|0 /0 /0|
| **Total** |**294**|**0 /0 /0**|

R3 contributes123 methods (105 author,18 independently written). Subcases are
reported separately and are not added to294. The final9 methods pass by confirming
the defects remain in the untouched legacy code, not by declaring it remediated.

The runner installs process-wide Popen/killpg tripwires; test-specific mocks
replace them only with simulated interfaces. Predecessor temporary files are
relocated into this new packet; the old local cgroup observation is replaced
with an empty disposable fixture. No real host timer, system manager, VM, guest,
package query, signal, network or Proxmox connection is part of these tests.

Additional executed checks, NOT added to294:

-15 saved synthetic snapshot cases:1 expected consistency success,14 expected
  refusals (identity, hardware, ISO, agent/network, pending, digest/freshness/epoch).
-7 local CLI checks: defaults/named dry-run, unknown prerequisite refusal, A
  cooperative/refusing cases and B modeled force. No native execution flag is
  passed. A refusal remains running with explicit NO_EXPIRATION_GUARANTEE; B
  results remain simulated and runtime force disabled.
-Source/AST/inventory checks and deterministic inert archive verification; no
  extraction into real host locations. All247 predecessor files/5 links and old
  seals/log prefix are independently rehashed by the local verifier.

## Required negative-case coverage

| Requested case | Exercised behavior |
|---|---|
| Wrong VMID/UUID/disk/serial | Strict snapshot and independent negative tests; no VM action |
| Unexpected boot order | Refuse order=scsi0;ide2 and other shapes |
| Missing/wrong ISO | Exact volume, bytes, content hash and digest binding required |
| Extra NIC or device | Conservative explicit config allowlist, no ignored efidisk/args/channel |
| Guest agent enabled/missing | No unsafe default; refuse |
| Pending config | Reject pending markers, malformed/duplicate/current-mismatch rows |
| Changed digest/config | Recheck exact digest and canonical config hash, including same-digest drift |
| Running before verification | Refuse both initial prepare and later start; no timer/start shortcut |
| Timer creation failure | Owned rollback attempt, quarantine unknown/orphan state, no start |
| Timer exists but inactive | Exact timer/service proof refuses; creation is not execution proof |
| Expiration service fails | Simulated grace failure leaves independent deadline job; A reports blocker |
| Shutdown timeout/refused ACPI | No stopped claim without fresh stopped snapshot; never force in A |
| Unauthorized forced stop | B grant negatives; native B rejected; no qm-stop allowlist |
| Unit collision | Refuse without resetting/overwriting/cancelling foreign unit |
| Two operator attempts | Actual disposable flock contention plus consumed generation/approval |
| Duplicate cleanup | Historical CLOSED no-op, no new observation or action |
| Cleanup interrupted halfway | CLOSING preserved; resume only stopped; idle worker barrier |
| Host reboot while active | Epoch mismatch, no stale resume/expiration or success claim |
| Stale approval | UTC/coverage/purpose/source validation; existing callback/new-lease distinction |
| Stale/malformed saved data | Bounded duplicate/nonfinite/malformed/future/stale parsing refuses |
| Evidence write failure | Strict durable intent before command; incomplete post-action evidence |
| Host command timeout | Mocked process-group kill, bounded single reap, shared budget exhaustion |
| Natural poweroff race | Error/lost ack reconciled only through fresh stopped snapshot |
| Change to another VM | Fixed target selectors and independent wrong-ID/endpoint refusal |
| Watchdog too late | Late trigger/stopped-after-criterion are LATE, never on-time PASS |
| Timer cancel/rearm/manager loss | Drift/refusal, consumed approval, immutable deadlines, no survival claim |
| Session/source/grant replacement | Expected-context binding, pinned directory, stale-source refusal |
| Retirement/reuse | Archived pointer/evidence, fresh new approval, old-grant replay prevention |
| Clock domain/suspend model | Large legitimate offset conversion; unknown domain/skew refuses |
| Resource/stdio weakening | Exact8 resource/I/O/start properties rejected when weakened |

No simulated timer proves real scheduling, supported CLI flags, ACPI behavior,
protection/lock semantics or host survival. Reboot/reexec/suspend/real expiry,
forced stop, installation, root bootstrap and Gate6K are excluded qualifications,
not silently passing tests or hidden skips.

## Failure evidence retained

Independent initial reviews reproduced setup rollback, phase-claim retry,
retirement/idempotence and pre-action evidence issues; later review found source/
grant/session-generation and approval-lifetime gaps. These were fixed and rerun.
The independent review also caught incomplete service-property readback and a
clock-domain assumption, now addressed with strict fields/qualified conversion.
An initial arithmetic concern was explicitly retracted after a realistic suspend
fixture; evidence records that correction rather than pretending it was a fix.

Earlier author run tests-author-v3.log contains one error in the independent
positive fixture after source added reviewed kinds/package checks. Fixture was
updated to mock the new metadata interface; no real dpkg-query ran. Initial
independent/import-failure notes and all subsequent logs are retained. The final
release run above is the acceptance record.

Reproduce without effects, with new exclusive output destinations:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/run_checks.py --out /NEW-LOCAL-TEST-OUTPUT
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/replay_fixtures.py --out /NEW-LOCAL-FIXTURE-OUTPUT
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/tools/verify_packet.py
```
