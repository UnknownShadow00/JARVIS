from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
b=json.loads((P/'BUNDLE.json').read_text());inv=json.loads((P/'SMOKE-INVOCATION.json').read_text());sm=json.loads((P/inv['run']/'SMOKE-RESULT.json').read_text());dep=json.loads((P/inv['run']/'work/DEPENDENCY-CHECK.json').read_text())
report=f'''# Unified RC1 — VM164 lab preparation

**Engineering preparation PASS. Protected installation and VM164 lab qualification
remain BLOCKED; no VM/production/privileged action was performed.**

This sprint produced an actual verified offline package, working guarded installer,
read-only probes, complete synthetic installation/rollback evidence, installed-
package application regression, broker replay, SBOM and fresh advisory findings.
The next human action is the single bounded preflight request below.

## Final package and exact identities

- [Final offline installation bundle]({b['bundle']}): **{b['bundle_bytes']:,} bytes** (22.46MiB).
- Bundle SHA256: `{b['bundle_sha256']}`.
- Standalone [bootstrap/validator](tools/lab_package.py) SHA256: `{b['bootstrap_tool_sha256']}`.
- Installed manifest SHA256: `{b['installed_manifest_sha256']}`.
- Source revision: `{b['source_git_revision']}`.
- Original RC1 archive SHA256: `{b['source_archive_sha256']}`.
- **315 exact public source files,31 exact wheel artifacts,2,444 installed files,
  {b['installed_bytes']:,} installed bytes** (76.70MiB).

[BUNDLE.json](BUNDLE.json), [bundle manifest]({str(Path(b['bundle']).parent/'MANIFEST.json')}),
[wheel provenance](WHEEL-PROVENANCE.json), [SBOM](SBOM.cdx.json) and
[final verifier](tools/verify_preparation.py) bind these results. An independent
USTAR/gzip reconstruction produced byte-identical package bytes. Every wheel
artifact and every wheel RECORD entry verified; no Nexus virtualenv was copied.
The fixed wheel unpacker rejects executable .pth, relocated .data, symlinks,
traversal, duplicates, hash/size/identity mismatches and expansion overflow. It
supports this exact closure and module launches, not arbitrary pip entry-point
installation. No package was installed globally or in a guest.

Earlier package drafts/builds are preserved for engineering history; **only the
bundle named in BUNDLE.json is the delivery candidate**. It contains dormant
reviewed serial source/examples/tests, public application source,31 wheel files,
the installer, metadata checker, standalone smoke runner and fixed smoke inputs.
It contains no real config.yaml, authority enrollment/key, credentials, real DB,
model files, privileged activation marker, OS image or copied runtime environment.
Public CA data in certifi is not a private credential and remains advisory-affected.

## Working tools and demonstrated behavior

| Tool | Behavior and current verification |
|---|---|
| lab_package.py verify | Checks independent archive pin, exact source/dependency inventory and wheel contents before extraction; actual standalone invocation passed. |
| lab_package.py probe | Future VM164 read-only identity/rootfs/native-library/network/mount/resource JSON; different DMI UUID/disk refuses before broader inspection. Not run on VM164 or used as guest attestation. |
| lab_package.py install | Requires actual guest root, protected bootstrap/interpreter/approval ancestry, exact root0600 finite approval, target/runtime/rootfs bindings and adequate headroom. Uses exclusive descriptor-relative no-follow/fsynced publication; no overwrite, cleanup, accounts, credentials, database, units or service start. Actual unprivileged invocation refused before guest inspection. |
| validate-installed / quarantine | Exact owner/mode/file/hash inventory; complete inactive release can be moved to an exclusive same-parent quarantine with every byte preserved. Partial/changed state refuses and stays in place. |
| worker_preflight.py | Read-only reviewed source/root protection, existing nonroot identity, tty metadata/getty/kernel-console/open-holder checks; never opens serial/credentials/state or starts a service. Metadata success explicitly leaves activation false. |
| smoke_runner.py | Independent install-manifest pin; verified public inputs and31 read-only dependencies in unshared capability-free networkless namespace; disposable synthetic state only. Tested using the actual installed final package. |
| observer.py | Reuses hash-pinned existing GET-only observer, enforces exact allowed paths, suppresses credential-bearing output/errors and records minimized diagnostics. Current result is HTTP401; token/grants unchanged by this work. |
| verify_preparation.py | Rebuilds/verifies package, current tests/quarantine, SBOM/advisory evidence and full sealed RC1 predecessor chain without importing app or opening runtime stores. |

[Installation procedure](INSTALLATION-PROCEDURE.md),
[rollback procedure](ROLLBACK-AND-PRESERVATION.md) and null-filled
[approval template](approval.example.json) are executable-tool handoffs, not an
approval or a claim of root/multi-UID guest installation.

## Actual new execution results

| Verification | Current result |
|---|---|
| Installation/target/archive/ownership/race/rollback tests | **67 passed**,0 failures/errors/skips, fixture UID1000 |
| Actual installed-source application regressions | **210 passed**,0 failures/skips |
| Joined synthetic application lifespan/execution/recovery scenarios | **20 groups passed** |
| Current reviewed broker/worker fixture suite | **71 methods,305 subtests passed**,0 failures/errors/skips |
| Complete release quarantine rollback | **2,444 files preserved and rehashed** |
| Fresh exact dependency closure | **31 distributions,33 active metadata edges passed**; native NumPy/BS4/Pydantic/YAML/psutil and SQLite/OpenSSL checks passed |
| CycloneDX1.6 SBOM schema and references | **45 components validated offline**, no remote schema resolution |
| Independent sealed RC1 recheck | **18,582 RC1 evidence files and177,460 predecessor files verified**, source/worktree pins unchanged |

These are current executions, not historical counts added together. RC1's earlier
1,023-case/37-crash/13-benchmark evidence was independently verified as historical
source-bound evidence; this sprint does not relabel those observations as fresh
runs. The nine hardware/desktop exclusions remain NOT RUN, along with actual
browser/GUI/GPU/model/provider, VM/broker, power-loss and privileged Gate6K work.

The installed smoke used real FastAPI lifespan, authority/API auth, queue, scheduler,
signed AF_UNIX pure execution, receipts, cancellation, UNKNOWN/restart/reconciliation,
witnesses, inert restoration and nonactivating decisions. It also reran anonymous/
invalid auth, hostile WebSocket, filesystem-race and blank-token startup controls.
No external route, host runtime config, service socket, device or credential was
available in the cage. The actual full smoke took **{sm['wall_seconds']:.2f}s** and
peaked at **{sm['peak_rss']/1024**2:.2f}MiB aggregate RSS** on Nexus, not VM164.

Main smoke bounds remained AS1GiB/process, aggregate RSS768MiB, CPU120/121s,
wall120s, FD64, core0,20,000 files/256MiB controlled state and at most4 owned
processes including namespace machinery. NumPy threads were fixed to1. Installer
fixtures/broker runs used AS1GiB, CPU120s, wall120s, FD96 and64 payload processes
inside fresh namespaces. No heavy test batches overlapped.

One initial installer-harness invocation stopped before executing tests because
RLIMIT_NPROC was applied outside the new namespace and counted existing Nexus
processes. The unchanged64-process cap was moved inside the fresh namespace before
payload imports, and all final tests passed. All drafts/attempts are retained.
Final application pytest emits two upstream Starlette/httpx and AnyIO deprecations,
recorded in the raw results. No warning or namespace refusal was counted as a pass.

## Current VM164 observation — blocked, not inferred

At2026-11-06T14:44:20Z the unchanged installed observer
`5a6d834d5d1941eb34483aa81a8a856186c0fe3f237f33451b3d680e1dde5e7a`
received **HTTP401 on GET /nodes/pve/qemu/164/config**. The wrapper recorded one
allowed request and no guest, console or mutation calls. An earlier generic failed observer invocation is also retained; the classified
invocation supplies the measured request/status log. The cause of401 was not
diagnosed by opening, replacing or changing credentials. No fallback principal,
permission expansion or call to another VM was attempted.

[evidence/observer-classified.json](evidence/observer-classified.json) is the current
result. Successful old metadata is historical only:4 vCPUs,6000MiB RAM,64GiB disk,
serial0 socket, no NIC, agent disabled, scsi0-only boot and no media. Current
configuration/status/pending changes, permissions and installed guest boot/root
facts remain unverified. The incident/installation records do not prove a completed
trusted installed OS; no old installer/guard was rerun.

## Fresh advisory findings and SBOM scope

Fresh OSV queries completed for all31 Python pins and13 locked npm pairs;
all28 returned IDs were retrieved. **This is not a clean advisory verdict.**
Certifi2026.7.22 is reported affected by the emSign CA issue (two alias records,
fixed2026.10.18 according to OSV); Electron42.10.1 has8 records and undici7.29.0
has18. The original RC1 versions remain unchanged. No Node/Electron binary is
installed in this headless bundle; their source lock entries are explicitly
metadata-only SBOM components. Networked/frontend use remains blocked pending a
separately reviewed remediation/release and affected verification.

[Advisory assessment](ADVISORY-ASSESSMENT.md), [exact batch results](ADVISORY-RESULTS.json),
[full advisory details](ADVISORY-DETAILS.json) and [SBOM validation](SBOM-VALIDATION.json)
distinguish findings from unavailable installed native/OS advisory data. SBOM
contains31 installed Python components,13 npm lock components and one dormant
serial candidate. Retained official CycloneDX schemas were validated in a networkless
cage using pre-existing tooling, with exact schema hashes retained. No advisory
silence is treated as proof of security; the full historical127-package tools,
native OS/runtime, desktop/provider graph and installed VM remain unqualified.

## Broker reconciliation and protected installation requirements

The packaged reviewed13-file successor source manifest is
`{b['broker_source_manifest_sha256']}`. All13 source pins match RC1's standalone
broker proposal;59 sealed broker-packet files were freshly verified. The older
Phase3 candidate has12 files and lacks the reviewed lifetime-budget, lock-through-
receipt, fresh synchronization and precredential-canary corrections.
[Reconciliation](BROKER-RECONCILIATION.md) preserves every per-file identity.
The fresh71/305 fixture replay is same-UID synthetic TLS/PTY/Unix/kernel-child
behavior, not installed/cross-UID qualification.

The serial candidate stays dormant under the application release. It is not
promoted to /opt/g6k-serial or installed into systemd. No actual worker UID/GID,
locked-account/root bootstrap, exclusive TTY, service/egress/DAC/seccomp, finite
grant/token/CA/time custody or preissuance acceptance was established. JARVIS has
no live adapter or implicit36-character task UUID to32-hex broker ID bridge.
[Bootstrap/worker blockers](BOOTSTRAP-AND-WORKER-BLOCKERS.md) lists exact remaining
facts. None is silently satisfied by a synthetic PASS or a root metadata check.

## Resource and offline-media review

The final package needs about23.55MB transfer space and80.43MB installed space;
allow at least64MiB approved nonboot transfer capacity plus a separate private
smoke/evidence scratch budget up to256MiB. The conservative guest gate requires
4 vCPUs, actual RAM>=5GiB with>=3GiB available,20GiB free on the original64GiB
private ext4 disk. Historical6000MiB is compatible with that narrower headless
budget only if fresh guest headroom verifies; it does not qualify the separate
8GiB/full127-package Gate6K recommendation. No resource change was made or proposed
automatically. Nexus had sufficient recorded headroom; RESOURCE-REVIEW.json retains
current preparation-host measurements separately from unknown guest facts.

This is a source/wheel transfer archive, not an ISO/OS image. It requires an
already approved signed Ubuntu26.04.1/CPython3.14.4/native-library/bwrap foundation.
No system library, native runtime, apt/dpkg installer or copied Nexus venv is
bundled. Missing prerequisites block; no automatic package installation/fallback.
No ISO tool was present, and no ISO, media attach/mount/detach, boot, disk, NIC,
shared mount, cloud-init or Proxmox modification occurred. Do not reuse the prior
r4 autoinstall ISO or erase the initialized incident disk to stage this package.

## One human action and final verdict

**Preparation is complete; protected installation/testing is not authorized.**
The minimal next action is the single bounded trusted VM164 host/guest preflight
window in [AUTHORIZATION-REQUEST.md](AUTHORIZATION-REQUEST.md). It obtains fresh
trusted configuration and actual guest identity/runtime/rootfs facts, while keeping
the observer unchanged. If an already trusted installed-root console or approved
probe-delivery path is absent, stop for a separate exact preservation/bootstrap
scope; no generic rescue, install retry, root unlock, console workaround or VM
lifecycle operation is authorized here. Once facts pass review, a later exact
finite approval can authorize dormant file installation and isolated unprivileged
smoke using these tested tools.

Known advisory findings, independent installed custody/privilege/storage/ingress
facts and privileged Gate6K qualification remain explicit gates. No real executor,
provider request, credentials/permission grant, guest agent, actual serial broker,
production startup, real database migration, VM162/VM163/AI-server change, evidence
deletion or V3 action occurred. Package/evidence hashes need independent external
retention; same-UID hashes/permissions are not WORM or public-key approval.
'''
# Only tidy numeric prose; never alter source pins, paths, identifiers or command text.
for a,z in [('all31','all 31'),('and13','and 13'),('and177,460','and 177,460'),('66 passed**,0','66 passed**, 0'),('71 methods,305','71 methods, 305'),('At2026','At 2026'),('cause of401','cause of 401'),('claims_','claims_')]:report=report.replace(a,z)
(P/'REPORT.md').write_text(report)
results={'status':'PREPARATION_COMPLETE_INSTALLATION_BLOCKED','source_revision':b['source_git_revision'],'bundle':b,'installation_tests':67,'application_tests':210,'application_scenario_groups':20,'broker_methods':71,'broker_subtests':305,'full_rollback_files':2444,'metadata_dependency_edges':len(dep['active_metadata_edges_checked']),'sbom_components':45,'advisory_records':28,'observer_status':401,'hardware_live_tests_executed':False,'privileged_guest_or_production_actions':0,'minimal_human_action':'one trusted VM164 preservation/preflight console window, not installation retry or activation'}
(P/'RESULTS.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
(P/'DRAFT-CANDIDATES.json').write_text(json.dumps({'delivery':b['bundle'],'retained_superseded_drafts':[str(f.relative_to(P)) for f in P.glob('bundle*/*.tar.gz') if str(f.relative_to(P))!=b['bundle']],'drafts_are_not_delivery':True},indent=2)+'\n')
print('Report and current result summary written.')
if __name__=='__main__':pass
