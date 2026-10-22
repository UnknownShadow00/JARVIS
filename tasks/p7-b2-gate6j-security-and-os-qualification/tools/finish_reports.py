from pathlib import Path
import json,re
T=Path(__file__).resolve().parent.parent
assert not (T/'SHA256SUMS').exists()
I=json.loads((T/'evidence/candidate-identity.json').read_text())
result=json.loads((T/'evidence/runs/full-final/full-final-result.json').read_text());assert result['exit']==0
log=(T/'evidence/runs/full-final/full-final.txt').read_text();match=re.search(r'(\d+) passed, (\d+) deselected, (\d+) warnings',log);assert match
passed,deselected,warnings=map(int,match.groups());assert passed==7741 and deselected==11
entry=json.loads((T/'evidence/production-entry.json').read_text());final=json.loads((T/'evidence/production-final.json').read_text())
diff={k:{'before':entry[k],'after':final.get(k)} for k in entry if k!='utc' and entry[k]!=final.get(k)}
(T/'evidence/production-comparison.json').write_text(json.dumps({'comparable_fields':len(entry)-1,'differences':diff},indent=2)+'\n');assert not diff
(T/'TEST-RESULTS.md').write_text(f'''# Actual test results

Final release-r2 full applicable suite: **{passed} passed / {deselected} deselected / zero failures / {warnings} existing warnings**, {result['seconds']:.2f} seconds, ext4 disposable Core stage under Landlock8 and non-AF_UNIX socket denial. All613 staged bundle files match the final candidate. The earlier full-r1 also passed7741/11/zero, before final runner packaging/security changes; it is retained, not mislabeled as final.

Historical Gate6I baseline7719 passes is preserved; **22 new candidate regression cases** account for the full-suite increase. Additionally **30 unprivileged runner unit cases** and **3 supplemental actual-socket probes** pass. Thus55 new test cases across these three sets, plus a separately recorded real same-UID kernel-confinement probe. Do not add focused re-runs to the full-suite count.

| Run | Actual outcome | Interpretation |
|---|---|---|
| redteam-before | 2 failed | Confirmed direct provider/native bypasses on unchanged Gate6I code |
| redteam-r1 | 110 passed | First15 new cases plus95 prior protected-runtime cases |
| delegated-before | 1 failed /15 deselected | Real second-PID writer inherited connector authority |
| terminal-before | 1 failed /17 deselected | Protected INCOMPLETE disagreed with local COMPLETE |
| focused-r2 | 569 passed /1 failed | Newly introduced runner module import path error; corrected, no assertion weakened |
| redteam-final | 22 passed | All candidate red-team regressions after fixes |
| full-r1 | 7741 passed /11 deselected /0 failed | Intermediate complete runtime regression |
| full-final | {passed} passed /{deselected} deselected /0 failed | Exact final bundle regression |
| wire-final | 3 passed | Final613 candidate files plus separately manifested wire probe harness |
| runner-final-r2.txt | 30 passed | Actual unprivileged package tests; source matches final copied runner |
| kernel-runner-probe.json | PASS | Child UID1000 unchanged; actual no_new_privs and socket-family refusal |
| compile.json | 147 modules PASS | No bytecode written |
| dependency-pin-check-final.json | 127 effective package pins match | Python3.14.4/SQLite3.46.1/crypto46.0.5 match; no installation |
| current-host runner entry | BLOCKED as expected | Nonroot preflight refusal; not OS security qualification |
| genuine distinct-UID VM run | NOT RUN | No approved VM or privileged execution |

Intermediate runner manifest-fixture failure (22 pass/1 error) is retained. Its newly created parent directories were group-writable; only new Gate6J directory modes were tightened. Initial dependency capture had11 duplicate system/venv metadata mismatches; effective-version capture corrected them. Earlier unprivileged runner passes are retained as intermediate revisions. No failing test was silently skipped and no security assertion was relaxed.

The two full-suite warnings are existing FastAPI/Starlette/httpx/AnyIO deprecations. No package upgrade was made. Historical Golden12/20 with eight failures remains historical; model-capable Golden evaluations were not run. No live provider, model lifecycle or operational execution was used. New process-crash tests use disposable child os._exit, not VM power cuts. Same-UID actual sockets/processes and pure fixture checks are labeled separately from NOT RUN cross-UID tests.
''')
(T/'PRODUCTION-NONMUTATION.md').write_text(f'''# Fresh read-only production comparison

Entry {entry['utc']}; final {final['utc']}. Trusted SSH with BatchMode/StrictHostKeyChecking; no enrollment/bypass. The minimized reader does not import the application, invoke HTTP/WS, open providers or read secret environments. {len(entry)-1} comparable fields: zero differences. Complete minimized records and comparison are in evidence/production-entry.json, production-final.json and production-comparison.json.

HEAD `{final['source_head']}`. Config SHA256 `{final['config_sha256']}`; app file inventory and pre-existing dirty worktree unchanged. V2 inactive/dead, disabled, PID0, Restart=no. Historical epoch606a991a06b74fd79ed72b308417cc3f CLOSED_COMPLETE/input_complete1; accepted attempts/submissions/D04 joins/refusals0. D06 current=None/last=None. D04 namespace absent; Hermes flagsfalse; admissions closed. Proposed V3 roots absent and V3 unit not-found; no production successor observed on canonical inspected surfaces.

No production source/config/state/unit/identity/policy mutation, real successor, retirement, deployment or pilot operation was performed. Test writes are confined to new private nonproduction stages; the Core venv was read-only. No production corrective action was attempted. The unchanged boot identity is current preflight/readback metadata, not a reopened historical reboot investigation. OPERATOR_REPORTED_MAINTENANCE does not rewrite OPERATOR_STOP or authorize retirement.

Zero task real provider requests is supported by the action record and offline kernel restrictions, not a claim of independent global AI-host traffic telemetry. The AI host and Proxmox were not contacted by this task.
''')
(T/'FINAL-REPORT.md').write_text(f'''# JARVIS P7 GATE 6J — SECURITY REVIEW COMPLETE, DISPOSABLE QUALIFICATION READY

The independent examination of the received Gate6I source found and repaired concrete runtime and future-runner boundary defects. The exact new bundle is ready for review and a separately approved disposable VM execution. Actual distinct-UID qualification has not run. Production remains unchanged. This verdict describes the reviewed/tested isolated scope, not production security certification or absence of all vulnerabilities.

## Provenance and source

Gate6I source manifest c0aac0e6a33e0dbfcd00616651354ed42c70aa3be22774b83b3348d180a3f461 and evidence seal09f6347a0bdd30e2153727b0a7ba5e6485ddd3d0705268b290ec7e989f5ebb22 verified before copying; all235 evidence/606 source members match. Gate6H245 evidence members and both historical seals were reverified unchanged.

New candidate `{I['candidate']}`. Full source manifest `{I['source_manifest']}` (612 source members); full inventory `{I['inventory_digest']}` (613 including manifest). Archive `{I['archive']}`, SHA256 `{I['archive_sha256']}`. Sixteen changed/new files including the manifest; no repo/app changes. Exact diff, changed sources, pre-fix reproductions and per-run source associations are supplied. Earlier candidate releases remain intact.

## Security findings and qualification

The audit traced REST/WS/continuations, signed operator and service transports, singleton succession, claims/permits, D09 acceptance/high-water, pre-send and actual native dispatch, D06 ownership, D04/receipt joins, checkpoints and stop/restart. Confirmed fixes: direct OwnedProvider/NativeTransport calls could bypass protected SEND; delegated socket writers retained connector identity; protected INCOMPLETE could be presented locally as COMPLETE; future runner fork leaked unrelated descriptors and pickle accepted executable lower-privilege input. New native DISPATCH claims, per-message kernel credentials, protected terminal readback, spawn and bounded fixed-type JSON close those demonstrated paths.

Additional hardening bounds privileged snapshot reads/SQLite evaluation and validates the same captured bytes, enforces the proposed ordinal2 classifier omission/eleven-operation budget at the authority root, rejects false DAC-denial successes and retains timeout/failure evidence. A runner import error and dependency-lock capture error were found and corrected; no test assertion was loosened.

Real accept-based socket tests cover framing, identity/signature separation, replay, malformed UTF-8/duplicate keys, stale pins, descriptors, symlink/replacement/modes, partial/trickling/nonreading clients, concurrency and dropped responses. Actual separate-PID delegation is tested under one UID. Genuine cross-UID tests: **NOT RUN — AWAITING DISPOSABLE VM AUTHORIZATION**. Kernel per-process network restriction was exercised unprivileged in a child without changing host policy.

Durable tests cover singleton succession and nonces, nonrefundable acceptance, one-use dispatch including concurrent claims and real child crashes before/after commit, protected possible-send uncertainty, settlement witness refusal, receipt joins/checkpoints and truthful terminal closure. Missing acknowledgment never refunds authority. D06 unknown survives cancellation/timeout and blocks conflict. Provider/legacy/Granite separation is maintained; no tool/confirmation/TTS/fallback/startup inference is enabled.

Rollback attempts against controller/D09/D04/checkpoints/backups/source/config and all service-writable state refuse when retained protected history disagrees. The negative control intentionally confirms that the authority owner can roll back the entire authority. This is not root/host rollback protection. Real protected OS storage, source/interpreter/import controls, signer custody/presence, independent terminal witness, production egress and external actor control remain prerequisites. Arbitrary service-code execution could bypass in-process Python guards by using its own network client; independent infrastructure controls are required. No external witness or provider proxy was silently added.

## Runner readiness, tests and approvals

GATE6J-DISPOSABLE-VM-EXECUTION-PROPOSAL.md contains the exact archive/hashes, estimated4vCPU/8GiB/40GiB private-ext4/no-NIC VM requirements, independent human identity/mount/credential checks, root AUTHORITY plus three non-login private identities, explicit provisioning commands,127 pinned effective dependencies, execution order, evidence and separate cleanup boundary. The runner needs no production credential, mutable Core path or real provider. Its approval marker is a human declaration, not independent VM proof. The review packet and unprivileged checks establish execution readiness, not a predicted privileged PASS.

Final full suite: **{passed} passed /{deselected} deselected /zero failed**, {warnings} existing warnings.22 new candidate regressions;30 runner cases and3 supplemental socket cases also pass.147 Python modules compile;127 dependency version checks match. Failing reproductions/intermediate engineering failures are preserved. Historical Golden12/20 is untouched; no live-capable evaluation ran.

All X1–X11 remain approval pending. Original four inputs, REST/REST/WS/WS order, L1 rules-first/legacy-visible/Granite-observational behavior and proposed Qwen8192 remain. Effective endpoints, immutable model identities, Gemma defaults, keep-alive/shared residency, physical GPU/runtime topology and outside lifecycle actors remain unattested. No proposal became active production config.

Evidence SHA256SUMS is verified; its seal is recorded separately in the sibling .seal file and final response to avoid self-reference. It is integrity evidence, not operator authorization. Source archives and report exports contain no real credentials/private keys/environment dumps or real conversations.

## Production and next action

Fresh final readback {final['utc']}: {len(entry)-1} comparable fields, zero differences. HEADbd53dbc799fb9284a21fae8cce3f5d9539e31141; source/config/worktree unchanged; V2inactive/dead/disabled/PID0; historical epochCLOSED_COMPLETE/zero attempts and submissions; D06clean; no D04 namespace; Hermesfalse; no production V3 installation/successor observed. No real provider request was made by this task under its offline execution controls.

Exact next operator action: review this sealed packet and authorize one specifically identified throwaway VM plus the explicit offline provisioning/run proposal for the exact Gate6J archive. Do not run it on Nexus/Core/AI/Proxmox. After genuine OS evidence, separately resolve X1–X11, infrastructure/model/witness controls, historical V2 disposition, one successor, installation/newGate5/provider qualification/pilot/Gate7. No current retirement, succession, deployment, pilot or measurement authorization exists.

GATE 5: COMPLETE HISTORICALLY FOR V2

PRODUCTION V2: VERIFIED INACTIVE/DEAD, DISABLED, PID0, UNCHANGED

V2 EPOCH: CLOSED_COMPLETE / ZERO USE, REVERIFIED

V3 CANDIDATE: ISOLATED ONLY

PROTECTED AUTHORITY: ISOLATED IMPLEMENTATION; SAME-UID SECURITY/CRASH/SOCKET TESTS PASS; PRODUCTION OS/WITNESS QUALIFICATION PENDING

GENUINE MULTI-UID QUALIFICATION: NOT RUN

AI/LEGACY ATTESTATIONS: PENDING

X1–X11: OPERATOR APPROVAL PENDING

V2 RETIREMENT: NOT AUTHORIZED

V3 SUCCESSOR: NOT CREATED

V3 DEPLOYMENT: NOT AUTHORIZED

PILOT ADMISSIONS: CLOSED

REAL PILOT ATTEMPTS: ZERO, REVERIFIED

MEASUREMENT: NOT STARTED

FORMAL P7 EXIT: NOT COMPLETE
''')
print({'full_passed':passed,'production_fields':len(entry)-1,'production_differences':len(diff)})
