# VM164 trusted-bootstrap remediation r2

**Offline engineering complete. VM164 remains NO-GO for a new root bootstrap.**
The required host-side pre-root enforcement backend is not implemented/deployed/
qualified. This packet implements a safer diagnostic workflow, cleanup candidate,
conservative admission model, revised state gate, reproducible candidate media,
negative tests and a gated operator procedure. A synthetic PASS never opens the
root gate. No unresolved hardware/hypervisor assumption has been labeled PASS.

Only this new task folder and the required append to tasks/loop-log.md were changed.
No network access, Proxmox connection, VM/guest command, production or credential
change, Gate6K execution, JARVIS install/start, model request, database migration,
Git commit/push or V3 action occurred. Existing dirty application work was preserved.
Local native ISO building used the retained pinned tool, read-only, in its
unprivileged no-network sandbox; no dependency was downloaded or installed.

## Starting facts and source reconciliation

New operator report: VM164 stopped, successful order=scsi0 correction, approved
192KiB r4 bootstrap ISO still attached to ide2. These are reported facts, not our
live readback. Do not repeat the old boot-order fix or infer CD absence. No live
observer or secret/token was used. The requested predecessor SECURITY-AUDIT.md
was absent. Actual FINDINGS.md, FAILURE-ANALYSIS.md, REPORT.md, OPERATOR-HANDOFF.md,
pinned procedure and implementation/tests were read instead; absence is recorded
in evidence/ENTRY.json. Nothing was invented or written into that old folder.

## Four hazards addressed

| Hazard | Implemented change | Honest disposition |
|---|---|---|
| H1 live ejection/hotplug0 | No running eject path. Keep media read-only, run unchanged probe, retain true optical presence; require stop before detach. Fixed new-media state gate and attached diagnostic decoder. | Avoided for r2 diagnostics, not empirically resolved for old ejection. Attached result is NOT installable readiness; original installer refusal regression passes. |
| H2 root before guest watchdog | Require independent host expiry armed/read back while stopped before start. Frozen per-boot/target/config/clock/deadline policy, missing-worker/authority/restart/clock negatives. | OPEN/high: model and requirements only. No runtime backend or real cutoff proof. Every tool receipt denies root_boot_go. Separate host facts/backend review/non-root qualification required. |
| H3 exception cleanup bypass | Independent narrow identity; once verified, state/receipt/command failures cannot skip nested cleanup/poweroff attempts. Unknown target causes no guest mutation; host fence remains mandatory. | Software regression remediated; real closure/SIGKILL/manager loss still depend on qualified independent enforcement. No actual stopped state claimed. |
| H4 insufficient timeout | No sleep; 8x(5s command+1s reap)=48s nominal wait envelope, global60s with6s poweroff reserve; manager90s/stop5/control-group/no-restart settings; process-group timeout cleanup. | Corrected software budgets, tested with virtual clocks/failures. Kernel/spawn/manager/host stop latency remains unqualified; request/ack is not proof of safe termination. |

Host schedule contract: grace request at arm+540s; hard escalation at+600s;
actual stopped proof demanded by+630s. These are future qualification criteria,
not observed or guaranteed behavior. Root cannot be admitted merely because
someone sets active/qualified flags in saved JSON. A reliable forced cutoff needs
new exact authority and acceptance of possible Ubuntu crash/filesystem loss.

## Actual verification of this candidate

Final run: evidence/regression-release/RESULTS.json and four detailed logs.

| Suite actually executed now | Unique test methods | Failures / errors / skips |
|---|---:|---:|
| New r2 cleanup, budget, fence-policy, diagnostic, state/artifact/capture tests | 87 | 0 / 0 / 0 |
| Preserved bootstrap r1 tests replayed | 43 | 0 / 0 / 0 |
| Preserved strict offline validator tests replayed | 32 | 0 / 0 / 0 |
| Preserved known-hazard reproduction tests replayed | 9 | 0 / 0 / 0 |
| **Total actual unique methods** | **171** | **0 / 0 / 0** |

The final9 methods pass by reproducing the unchanged legacy defects, not by
showing r1 was fixed. Subcases are recorded separately and not added to171.
All actual guest/process/TTY/service calls were mocked. A process-wide unexpected
subprocess tripwire covered the regression runner; test-specific mocks replaced
it only for simulated calls. All predecessor temporary fixtures were relocated
into this NEW packet. No fixture was allowed to change an old evidence directory.

Six additional local CLI fixture executions matched their expected results:
2 consistency/model-only successes,4 expected NO-GO refusals; all return
root_boot_go=false. They are not included in171. New byte-identical media builds5/6
passed independent ISO9660 member/manifest/nonboot inspection without mounting.
No systemd generator/real manager, hardware, Proxmox, VM, live stop or Gate6K test
was executed or counted as skipped/pass. Those remain explicit qualification
exclusions. No app regression was needed because application source was unchanged.

Static checks parsed all23 Python files/copies and8 shell examples without
executing their commands. Final preservation checks verified143 predecessor files,
5 links,104 original bootstrap manifest files and36 audit-manifest entries, with
the original log prefix intact (evidence/static-and-preservation-final.json).

Retained earlier test evidence includes a75-method run with1 failure/4 errors
from whitespace escaping in synthetic mountinfo. Corrected kernel-style path
escaping and decoding, reran affected/combined suites, and retained the failing
log. No failed run was silently overwritten. Earlier builds/fixtures and delivery/
are superseded local history; only candidate/ below is the new review artifact.

## Pinned candidate, not currently approved or attached

```text
candidate/vm164-trusted-bootstrap-r2-09185f1f69108ab1.iso
bytes196608
SHA25609185f1f69108ab18fbdf2b589c5eba9bb8b8e90c85dd92a797926b8972aa2ee
BOOT.PY SHA25639ff990b630a7ec361fba543526bcdf72a545301400b758c0319ac977ef86182
LABPKG.PY SHA25608eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a
```

Exactly3 files: BOOT.PY, LABPKG.PY, SHA256.SUM. No boot descriptor, boot system-area
code, installer, cloud-init, JARVIS application, credentials, provider or executor.
Probe is byte-identical to the pinned lab-readiness tool. Its install predicate
was not relaxed. New helper code exists only under the new packet; do NOT run
old BOOT.PY or mix old/new cleanup procedures. Same size/label is not image identity.

The old approved r4 image remains exactly fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154.
All143 predecessor regular files and5 symlinks captured at entry remain unchanged;
original104-file/5-link bootstrap seal, audit SHA256SUMS and canonical loop-log
prefix are rechecked locally. No /home-wide delegated verification or historical
release test aggregation is claimed. Existing dependency/advisory/VM164/Gate6K
limitations remain; no fresh advisory lookup was possible/performed under no-network.

## Files and reproducibility

- OPERATOR-PROCEDURE.md: one gated path from current stopped/attached report,
  through qualified pre-root fence, truthfully attached diagnostic, early cleanup,
  stopped detach, separately fenced clean verification and final stopped state.
- AUTHORIZATION-REQUEST.md: next read-only host facts, reviewed backend and
  separately scoped non-root qualification; only afterward a new root decision.
- RISK-REGISTER.md, GO-NO-GO.md, SECURITY-AUDIT.md: exact residual high-severity
  blockers, independent-stop proof criteria, preservation/authority tradeoff.
- HOST-FENCE-CONTRACT.json and tools/lease_policy.py: frozen replay policy and
  requirements, explicitly missing runtime driver. No hidden Proxmox transport.
- payload/BOOT.PY, units/guest-close-r2.service: standalone candidate diagnostic/
  abort/cleanup implementation and intended transient settings; never installed.
- tools/state_gate.py, decode_diagnostic.py: conservative inherited strict evidence
  parser with new fixed media/state edges, and lossless same-boot capture checks.
- tools/build_candidate.py, check_candidate.py: pinned retained offline builder
  and independent read-only parser wrappers; tools/run_regressions.py and
  replay_fixtures.py reproduce tests without guest operations.
- evidence/, fixtures-final/, candidate/: actual logs, explicitly synthetic
  replay cases and final image. MANIFEST.json/SEAL.json provide local integrity,
  not a signature, live origin or operator authority.

Reproduce from the project root; use NEW destinations outside this sealed packet:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tools/verify_packet.py
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tools/run_regressions.py --out /NEW-LOCAL-REGRESSION-DIR
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tools/replay_fixtures.py --out /NEW-LOCAL-CLI-DIR
python3 -I -B -S tasks/jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tools/build_candidate.py --out /NEW-LOCAL-MEDIA-DIR
```

Existing native builder/bwrap must remain available at their pinned paths; stop
if missing rather than downloading/installing anything. All tools act locally;
no payload command is part of reproduction. Local manifest covers source/artifact
hashes; verify_packet checks packet, predecessor bytes, source/media agreement,
reproducibility and recorded final results without invoking any other process.

## Recommendation and exact remaining blockers

**Do not start another VM164 root/bootstrap session now.** The current hardware
report and passing offline tests do not establish pre-root expiration. Required:
new trusted host/interface facts; implemented/reviewed root-protected host backend;
explicit preservation/VM164 emergency-stop scope; real supervised non-root fence/
shutdown/failure qualification; fresh per-boot target/media/worker/deadline proof;
then a separate finite root authorization. Actual guest cleanup and clean-return
compatibility must also be observed. Every unresolved required assumption remains
a blocker. Do not approve root simply by accepting a risk table or replay receipt.

Safe next scope is the finite read-only host fact collection in the authorization
request, followed by backend engineering/review; no host change is authorized here.
Installation, broker/real executor, providers, real databases, Gate6K, production
VM162/preserved VM163/VM200/AI server and V3 remain outside this packet. The root
boot-id and /run evidence disappear at shutdown; attached diagnostics cannot be
reused as later optical-free installation authority.
