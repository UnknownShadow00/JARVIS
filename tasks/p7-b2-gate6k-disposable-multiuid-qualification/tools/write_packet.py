"""Generate Gate6K reports from retained evidence. Refuses a sealed packet."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent.parent;E=P/'evidence'
if (P/'SHA256SUMS').exists():raise RuntimeError('SEALED')
I=json.loads((E/'candidate-identity.json').read_text());J=json.loads((E/'gate6j-entry.json').read_text())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bootstrap=H(P/'tools/safe_extract.py')
identity=f"Gate6J source manifest `{J['source_manifest']}`; evidence seal `{J['evidence_seal']}`; archive `{J['archive_sha256']}`. Gate6K source manifest `{I['source_manifest']}`; archive `{I['archive_sha256']}`. Candidate `{I['candidate']}`."
status='GENUINE MULTI-UID QUALIFICATION: NOT RUN — AWAITING EXACT DISPOSABLE VM AUTHORIZATION.'
def put(name,text):(P/name).write_text(text.strip()+'\n')
put('GATE6J-ENTRY-VERIFICATION.md',f'''# Verified entry

{identity}

All 612 Gate6J source entries and 173 evidence entries verified. The 613 archive members match the preserved candidate byte for byte. The supplied operator prompt is the expected identity for this verification; a future human must also compare against an independently retained approval record. No signature or production authorization is inferred from SHA256.

The archive contains regular files only, 4,885,485 payload bytes, modes0600/0664, PAX mtime only. Group-writable metadata must not be restored into a privileged release. Gate6K normalizes newly created files to0644 and directories0755 while ignoring archive owner/timestamps. It rejects links/special files/privileged modes.

The Nexus worktree's existing modified loop-log and untracked Gate6I/Gate6J documents were preserved. No historical branch was assumed, no Git history was rewritten, no commit/push occurred. Gate6K uses a new release directory. `evidence/changed-files.json` and the complete diff identify every change. The actual runtime and all repo/app source are unchanged from Gate6J.

Executable evidence: `evidence/gate6j-entry.json`, `evidence/candidate-identity.json`, `evidence/SOURCE-SHA256SUMS`, `evidence/gate6j-to-gate6k.patch`.
''')
put('ARCHIVE-EXTRACTION-SECURITY.md',f'''# Archive extraction qualification

The preserved Gate6J archive has no observed traversal, duplicate member, link or special-file member. Its historical procedure nevertheless used raw tar plus recursive ownership/mode repair. A synthetic negative control created an untrusted symlink; GNU tar refused the attempted following write (exit2). No escape write occurred. This is evidence of inadequate strict rejection, not a demonstrated arbitrary-file overwrite on this tar version.

New `disposable/safe_extract.py` reads a bounded, stable regular single-link archive through O_NOFOLLOW/O_NONBLOCK, checks both independently supplied archive and source-manifest digests, and fully validates all members before creating any destination. Only canonical ASCII relative paths and regular files are allowed. Reject absolute/parent/dot/empty components, duplicate paths, file-directory conflicts, manifest collision, symlink/hardlink, sparse files, device/FIFO/directory/unknown types, setuid/setgid/sticky and world-writable mode, negative ownership, unexpected PAX attributes, oversized files/counts/payload. Retained PAX mtime is ignored. Numeric owners and ordinary modes are never restored.

Limits:32MiB uncompressed tar input,2000 members,8MiB/member,16MiB total payload,1MiB manifest. Validated bytes are retained in memory, removing extraction-time archive substitution. The destination parent is opened component-by-component with directory descriptors and O_NOFOLLOW, and must belong to root/current UID with no group/other write. Destination mkdir is exclusive0700; every file uses O_EXCL/O_NOFOLLOW; fresh file/directory modes are explicit. fsync precedes final0755 publication. Existing trees are never overwritten, repaired or removed. A failed partial extraction remains private and a retry refuses.

Tests include malicious synthetic archives, digest/inventory mismatches, parent symlinks, writable parents, FIFO input, hardlinked archives, budgets, interruption and restrictive umask. An early implementation incorrectly left child directories0700 under umask077; the failing case was preserved and fixed by assigning modes only to newly created directories. All84 combined runner/prequalification checks pass. Historical tar negative control and failed umask test remain separately recorded.

Actual extraction of the revised616-member bundle succeeded as UID1000. No root extraction occurred. The standalone bootstrap is identical to candidate source, SHA256 `{bootstrap}`. Verify this hash against an independently retained human record before executing it; never bootstrap trust from a file extracted by an unreviewed tar command.

Executable evidence: archive-before.json, extractor-umask-before.txt, archive-final.json, unprivileged-r2-final.txt; code and tests in evidence/source/disposable. Root/host-owner replacement remains outside this guarantee.
''')
put('DEPENDENCY-ARTIFACT-VERIFICATION.md','''# Dependency status: BLOCKED

Version pinning passes: requirements-versions.txt exactly matches all127 effective distribution versions in dependency-versions.json. Fresh read-only comparison of the current test runtime also matched all127 versions, Python3.14.4 / SQLite3.46.1 / cryptography46.0.5; see evidence/current-test-runtime-versions.json. This does not establish interpreter, wheel, OS image or library authenticity.

The exact missing inventory is `ARTIFACTS-REQUIRED.json` and `evidence/dependency-artifact-status.json`:127 distribution artifacts plus CPython3.14.4, SQLite3.46.1, the reviewed libseccomp.so.2 build and the reviewed Linux x86-64 image. None has been supplied with an independently approved artifact digest/provenance record. No download, package installation, network resolver or version substitution was performed. Existing test-host software is a regression environment, not the independently reviewed offline VM supply chain.

Distinct verification layers:

| Layer | Actual status | Required evidence |
|---|---|---|
| Exact versions | PASS:127 lock entries agree | retained pin files and effective runtime comparison |
| Wheel/distribution bytes | BLOCKED | each exact artifact plus independently retained SHA256 and signed upstream/build provenance |
| Interpreter | BLOCKED | reviewed offline CPython3.14.4 build, build inputs/signatures and artifact SHA256 |
| OS libraries/image | BLOCKED | reviewed offline image and SQLite/libseccomp builds, package signatures/build records and hashes |
| Future VM runtime | NOT RUN | actual interpreter/SQLite/crypto/imported distributions and OS-library build readback |

The list includes Ubuntu/system packages such as python-apt3.1.0+ubuntu1.1, python-debian1.0.1+ubuntu2, command-not-found0.3, ubuntu-drivers-common0.0.0 and ubuntu-pro-client8001. Do not assume that all127 are installable PyPI wheels or issue the historical blanket pip-install command. An operator must provide a reviewed offline image/environment that reproduces these exact effective versions, or explicitly approve a separately reviewed dependency correction with new source identity. No correction is silently selected here.

`offline_artifacts.py` verifies the hash of a separately retained ARTIFACTS.json record, exact inventory/version schema, bounded regular non-writable files, file hashes and provenance references. Its synthetic positive/tamper/missing-record tests pass. References and hashes alone are not independent authenticity; the operator must verify original signatures/build chain outside the VM. The future runner requires this record at /opt/g6k-offline, its digest in exact VM approval, and still checks actual runtime versions. It does not install artifacts or claim their contents are trustworthy merely because their version strings match.

No complete offline installation command can truthfully be supplied until those actual artifacts and OS packaging/build layout are provided. This is an external dependency blocker, not a reason to enable networking. Stop this branch; retain the prepared validators and exact missing-artifact inventory.
''')
put('DISPOSABLE-VM-IDENTITY-AND-APPROVAL.md',f'''# Phase B is not authorized

{status}

No VMID, VM UUID, guest machine-id, hypervisor, disk or console session has been approved. No VM was created, accessed or modified. No users/groups/helpers were installed. A local marker is only a record of human authorization, not evidence that a VM is disposable.

Proposed estimates:4vCPU,8GiB RAM,40GiB private ext4 disk, noGPU, Linux x86-64, noNIC, no shared mounts, no production credentials or forwarded agents. At least20GiB free is enforced immediately before fixture creation. These are estimates, not measured minimums. Use trusted management console verification of VMID/UUID/node/disk/guest identity, fresh image provenance, disconnected interfaces, mounts and absence of production attachment. No physical power cuts or snapshot rollback are approved.

`OPERATOR-APPROVAL-TEMPLATE.json` is deliberately invalid until completed. Required: actual machine-id, new nonproduction VMID+UUID, hypervisor node, exact isolated disk identity, operator console/session, exact synthetic no-powercut scope, snapshot/failure-preservation policy, source-manifest digest, archive digest and reviewed dependency-artifact-record digest. Root-owned0600 regular single-link /etc/g6k-disposable-approved.json is read with a bounded no-follow parser; duplicate keys and incomplete/wrong scopes refuse. The record must match a separately retained human approval.

This exact authorization is needed because the user explicitly reserves privileged VM execution to Phase B. Existence of a VM, this task's GO for preparation, an operator marker or silence is not authorization. New source digest requires new approval. The earlier Gate6J digest cannot authorize this revised bundle.
''')
put('PREQUALIFICATION-RESULTS.md','''# Unprivileged prequalification

PASS: Gate6J provenance; archive structural review and actual unprivileged revised extraction; syntax; exact version-lock consistency; all84 runner tests (30 inherited,54 new); bounded marker handling; shared-mount refusal; free-space boundary; artifact hash/missing-record checks; preserved failure evidence; unsafe-target simulations. Actual Nexus invocation refused before fixture creation as BLOCKED. It is not counted as a passed kernel isolation test.

The actual target preflight cannot pass here: Nexus is not the approved VM, no exact Phase B authorization exists, and reviewed offline dependencies are absent. The unprivileged positive environment/UID shapes are fixtures. No user-namespace or mock UID is relabeled as real distinct-UID evidence.

An initial extractor umask test failed and was fixed; its failing output is retained. An initial evidence-writing command used the disposable working directory and failed to find the task output path; rerun used the correct workspace destination. No evidence was overwritten or production state changed. A first r2 test invocation used the workspace cwd and failed module discovery; the corrected package-directory invocation passed84. Both outputs are preserved. All final safe checks passed; full regression results are recorded separately when complete.

Phase A engineering checks are complete for the supplied artifacts. Overall prequalification remains PARTIAL because independent dependency artifacts/runtime verification and the exact human execution environment have not been supplied. Do not claim the full real-VM preflight passed.
''')
put('MULTI-UID-KERNEL-RESULTS.md',f'''# Kernel identity results

{status}

Current unprivileged preparation/extraction ran as Nexus UID1000. A fresh disposable child kernel probe also passed: no_new_privs=1; AF_INET, AF_INET6 and AF_PACKET socket creation denied with PermissionError; AF_UNIX usable; UID unchanged. This is real per-process OS restriction evidence, not UID separation. No connection was attempted and no host policy changed; see evidence/kernel-runner-probe.json. Isolated Core unit tests use the existing jarvis identity inside private ext4 test stages with kernel write/network restrictions. These identities were not used as simultaneously separated operator/service/authority/agent principals. No genuine multi-UID or privileged VM result exists.

Future role model: AUTHORITY=root; OPERATOR=g6j-operator; SERVICE=g6j-service; AGENT=g6j-agent. Measure actual UIDs/GIDs/PIDs and private groups. Reject root/non-distinct role UID/GID, login shells and supplementary administrative/shared groups. No sudo or policy changes. Kernel DAC tests must attempt write/truncate/chmod/unlink/rename/link, key reads and socket directory replacement; only actual PermissionError counts as the expected denial. Missing files and other errors fail the test.

Prepared existing workflow tests valid signed operations and real peer enforcement across these principals, operator/service/agent storage and key denials, immutable import-file denial and retained-root rollback. Gate6K adds invalid/expired signatures from the otherwise permitted operator peer and service socket mutation denials. These future additions are code-reviewed/static-tested but have NOT executed across distinct UIDs.

Every real-UID requirement is NOT RUN in evidence/qualification-matrix.json. A successful same-UID logical test or a refused setup cannot fill those entries. A future PASS must reference the actual kernel/process evidence for each requirement, not only an aggregate runner exit.
''')
put('AF-UNIX-CROSS-UID-RESULTS.md',f'''# AF_UNIX qualification layers

{status}

The focused/full isolated suites exercise actual pathname bind/listen/accept/connect, SCM_CREDENTIALS, SO_PEERCRED, ProcessPin freshness, malformed/duplicate JSON, unknown commands/versions, bounded/partial/trickling frames, ancillary descriptors, nonreading clients, concurrent requests, socket substitution and delegated writers. These are real sockets under the SAME UID; see test results. They are not genuine cross-UID DAC proof.

The prepared privileged runner uses root:operator-private-group0750 and root:service-private-group0750 socket directories, with root:respective-group0660 sockets. Agent has neither group. Neither role owns the directories. The service now attempts actual socket path unlink/rename/chmod/symlink and counts only kernel permission denial. Valid/invalid/expired signatures are tested separately from allowed operator peer identity; wrong-peer and forged fields cannot replace kernel evidence. These future cases have not run.

SO_PEERCRED binds connection creation; SO_PASSCRED/SCM_CREDENTIALS checks the writer of each request segment. The inherited-descriptor attack remains in the real separate-PID same-UID regression. /proc start ticks+boot ID provide process freshness under a trusted kernel; they do not attest executable contents, defeat code injection in a live PID or protect against root-controlled /proc/kernel state.

Coverage limitation: the privileged workflow plus service-UID logical suite must not be represented as every malformed-wire/delegation case having run across four UIDs. The execution matrix explicitly separates prepared cross-UID workflow cases from same-UID supplements and remaining targeted real-UID confirmation. A complete helper PROCESS restart is stronger than the runner's existing journal close/reopen; it requires distinct process evidence before that row can pass.
''')
put('PROTECTED-TRANSACTION-RESULTS.md','''# Protected transactions

Gate6K does not redesign or alter authority/runtime logic. Focused regressions re-exercise Gate6J's singleton signed succession; nonce persistence; signed OPEN/CLAIM; durable one-use CONSUME before D09; exact BIND; protected SEND and one-use DISPATCH before fake provider work; terminal witness association; D04/D09 joins and checkpoint; truthful incomplete stop. Accepted attempts are never refunded, including lost acknowledgment. Four global attempts and original REST/REST/WS/WS order remain.

The future distinct-UID runner prepares a synthetic predecessor, concurrent signed successor race, CLOSED attach, signed OPEN with dropped response, signed permit/replay, concurrent consume, protected possible-send/fake blocked provider, uncertain D06/terminal and rollback. Invalid/expired operator signatures must leave the protected journal unchanged. Synthetic signing keys remain in operator-owned0700/key0600 storage.

Actual multi-UID transaction execution: NOT RUN. The current fixture scenario consumes one attempt then deliberately enters uncertainty. The logical supplement tests four-attempt exhaustion and receipt/checkpoint boundaries; it is not a four-UID positive settlement attestation. Independent terminal-completion witness and actual production topology remain unavailable. No unsigned claim of remote completion is introduced to make that scenario pass.

A missing response is not failure proof. A possible-send record is not proof inference occurred. Local timeout/cancellation/disconnect does not terminate remote inference. No retry/fallback/next permit is automatic. No production predecessor, successor or permit is signed or mutated.
''')
put('ROLLBACK-AND-CRASH-RESULTS.md','''# Rollback and crash evidence

Existing isolated tests exercise controller/accepted-attempt/D09, D04/checkpoint, old backup, source/config identity, missing/corrupt root and whole service-writable-tree rollback against retained authority. They refuse disagreement and do not automatically recreate/restore authority. Real child-process interruptions before/after durable transactions preserve consumed nonces, acceptance and possible-send uncertainty. Full results are recorded in TEST-RESULTS.md.

The negative control test_complete_authority_rollback_still_possible_to_owner deliberately succeeds in restoring an old protected checkpoint when the authority owner rolls back its whole state. Its test PASS confirms this limitation, not a defense against host rollback. Protection depends on the independently retained authority being outside the application's writable domain. Arbitrary root, hypervisor or complete host rollback is not defeated; no external witness was added.

New extraction interruption tests preserve the private partial destination and refuse reuse. Interrupted runner preparation now produces and seals FAIL evidence when a fresh fixture already exists; preflight refusal is BLOCKED with no fixture write. Old evidence is never reset or overwritten by retry.

Actual distinct-UID crash, helper process restart and rollback qualification: NOT RUN. No VM power cut, snapshot rollback or production process interruption occurred. Future runner journal reopen is not relabeled as a new helper process; that distinction remains in the execution matrix.
''')
put('AUTHORITY-AND-SIGNER-SEPARATION.md','''# Authority and signer boundaries

Intended disposable root AUTHORITY owns ledger/source/config and narrow fixed-schema transactions. OPERATOR alone among lower-privilege roles owns the ephemeral Ed25519 signing key; authority receives public verification material. SERVICE uses the restricted service interface; AGENT has no administrative authority. Bearer authentication grants no signed OPEN/STOP/succession/permit privilege. Neither client may supply executable callbacks, paths, SQL or shell/Python code.

Root can read any same-host file by design. The test evaluates protection against lower-privilege service/operator/agent, not against root. Separate kernel identities and actual filesystem/socket DAC remain NOT RUN. Existing tests use synthetic signing material only; no real private production credential or key was read/copied/generated.

Spawn and bounded fixed-type JSON IPC retain Gate6J's descriptor and deserialization protections. No lower-role pickle recv is used. The future process-local no_new_privs/seccomp guard denies non-AF_UNIX socket families; no host firewall/policy is changed. No NIC/shared mounts/credentials plus independent human VM verification remain mandatory; a local JSON approval cannot establish that independently.

Protected Python/interpreter/import and artifact ownership must be verified before execution. No service/agent writable code may be imported into root authority. The release extractor and manifest check establish the prepared package bytes; the offline interpreter/OS supply chain is still BLOCKED.
''')
put('RUNNER-DEFECTS-AND-FIXES.md','''# Concrete corrections

| Finding | Reproduction | Small correction | Final evidence |
|---|---|---|---|
| Historical raw tar policy admits symlinks and unsafe metadata before later mode repair | synthetic symlink retained; attempted follow-write refused by GNU tar | strict full archive+manifest validation and exclusive descriptor-based extraction, explicit fresh modes | archive-before/final and malicious archive tests |
| Approval schema accepts a generic VM label without exact Gate6K authorization | incomplete marker accepted by Gate6J validator | exact VMID/UUID/node/machine/disk/console/scope/preservation and source/archive/artifact digests | prefx-reproductions and approval regressions |
| Shared mount propagation accepted | shared:1 root fixture passed old validator | reject shared/master/propagate_from mount metadata | prefx-reproductions and mount tests |
| Volatile mount can cover protected authority despite ext4 root | old validator accepts tmpfs over /var/lib | refuse mounts covering protected state/code/config/interpreter paths and automounts | volatile-authority-before and three new mount regressions |
| Unbounded/ambiguous approval read could accept duplicate keys or block on special files | code path lstat mode+read_text lacked type/size/link/duplicate checks | regular single-link0600 owner check, bounded no-follow read, duplicate-key refusal | marker FIFO/size/duplicate/mode/hardlink tests |
| Interrupted preparation outside old try block could lack structured result | new fault injection creates fixture then interrupts | outer wrapper emits/seals FAIL after creation; BLOCKED before creation; preserves old evidence | FailureEvidenceTests |
| New extractor inherited restrictive umask for directories | captured test failure:0700 versus0755 | set mode only on newly created directories before publication | extractor-umask-before and final tests |

Additional justified preparation:20GiB capacity gate, immutable-artifact byte validator independent of version strings, explicit x86-64/preexisting-tree refusal, fixed creation umask, future allowed-peer invalid/expired-signature checks and service socket mutation attempts. No application/runtime protocol, experiment semantics or production config changed. All changes and tests are in the complete diff. The revised digest requires renewed human approval; older Gate6J approval cannot cover it.

No newly demonstrated authority bypass was left unfixed. Unexecuted privileged paths and missing dependencies remain qualification blockers, not claimed security PASS. The scope is preparation, not a repeated Gate6J audit.
''')
put('REMAINING-APPROVALS.md',f'''# Remaining boundaries

1. Supply and independently review the exact offline artifacts listed in ARTIFACTS-REQUIRED.json. Review OS build/provenance, interpreter, SQLite/libseccomp and all127 distributions. Complete hash-bound ARTIFACTS.json and a reproducible offline image/install record; no networking or version substitution.
2. Separately approve one new VM with VMID/UUID/node, actual guest machine-id, exact private disk, approved console/session, noNIC/noGPU/private ext4/no shared mounts/no credentials, exact synthetic test scope and failure/snapshot preservation policy. Bind this source manifest `{I['source_manifest']}`, archive `{I['archive_sha256']}` and dependency-record hash. Approval currently absent.
3. Execute the reviewed package from the named console only after both prerequisites. Preserve every failed attempt; no automatic cleanup/retry. Gather per-case distinct-UID evidence and targeted confirmations listed in the matrix. Do not turn a same-UID supplement into a multi-UID PASS.
4. X1–X11 remain operator approval pending. Retain L1 rules-first, pinned skills memory, strict bounded classifier, no deep branch, proposed Qwen8192/Gemma4096/keep_alive60 subject to attestation, zero retries/fallback,20s classifier/180s responders, nonstreaming/noTTS, safe reply refusal, topology coverage, four accepted attempts/eleven conditional operations/1500s deadlines. No new experimental delta.
5. AI/legacy immutable model digests, effective endpoints, host-key identity, GPU/runtime conflict domains, Gemma defaults, keep-alive and external lifecycle actors remain unattested. No real model endpoint was contacted.
6. Protected production signer/root/import/egress controls and terminal witness; historical V2 disposition; one signed successor; V3 install/new Gate5/provider qualification/four-attempt pilot/Gate7 all require separate later approvals. None is authorized by Gate6K.

The exact next human action is to review the sealed preparation packet, provide the missing offline artifact provenance, then issue the completed VM-specific approval. No immediate privileged execution is requested or performed on any existing host.
''')
put('HUMAN-EXECUTION-AND-EVIDENCE-HANDOFF.md',f'''# Human execution handoff — BLOCKED until artifacts and exact approval

This is a future human-console procedure, not authorization to execute it. No approved VM exists. Estimated4vCPU/8GiB/40GiB private ext4/noGPU/noNIC; require20GiB free. Independently verify the VMID/UUID/node/disk/machine-id through the trusted management console and match OPERATOR-APPROVAL-TEMPLATE.json. Verify fresh image provenance, only loopback, no routes to production, no shared mounts/host credentials/SSH agent. Copy reviewed artifacts via approved offline media, then detach media before qualification. Do not reconnect networking.

## Offline artifact preparation boundary

The exact127-version list includes system distributions. The actual interpreter/wheelhouse/OS artifact set and install procedure are NOT supplied, so installation is BLOCKED. Do not use the old blanket pip command or invent package versions. The human supply-chain reviewer must provide an offline image/environment reproducing the pins, rooted at /opt/g6j-venv, with root-owned non-writable interpreter/import paths. Keep the actual131 reviewed artifacts and completed ARTIFACTS.json in /opt/g6k-offline. Use the null-filled required inventory as a request, not an accepted manifest. Verify upstream signatures/build records externally and retain the completed artifact-record SHA256 outside the VM. This missing independent input cannot be generated from version strings.

## Reviewed release extraction

Copy the standalone tools/safe_extract.py through reviewed offline media BEFORE unpacking the source. Independently retained bootstrap SHA256: `{bootstrap}`. Archive: `{I['archive']}` (transfer only this archive); SHA256 `{I['archive_sha256']}`. Source manifest SHA256 `{I['source_manifest']}`. The following commands are explicit privileged actions for the named VM's human root console only, after exact Phase B approval. `/opt/g6j-release` is retained as a compatibility path inside this disposable VM; the installed content is Gate6K.

```sh
# Review expected values against the independent approval record first.
printf '%s  %s\\n' {bootstrap} /media/reviewed/safe_extract.py | sha256sum -c -
printf '%s  %s\\n' {I['archive_sha256']} /media/reviewed/gate6k-release-r2.tar | sha256sum -c -
# Uses an independently reviewed offline Python interpreter; no archive code import.
/opt/g6j-venv/bin/python -I -B /media/reviewed/safe_extract.py /media/reviewed/gate6k-release-r2.tar {I['archive_sha256']} {I['source_manifest']}
/opt/g6j-venv/bin/python -I -B /media/reviewed/safe_extract.py /media/reviewed/gate6k-release-r2.tar {I['archive_sha256']} {I['source_manifest']} --destination /opt/g6j-release
cd /opt/g6j-release
sha256sum -c SOURCE-SHA256SUMS
```

Do not pre-create the destination, use raw tar, recursive chown/chmod, overwrite or reset a failed extraction. Fixed modes are assigned only during creation. Preflight uses root-owned /opt/g6j-release and /opt/g6k-offline; all parent/import paths must be non-writable to the three lower roles.

## Explicit role provisioning and authorization record

Only after source/artifact approval, on the approved VM:

```sh
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6j-operator
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6j-service
useradd --system --user-group --no-create-home --shell /usr/sbin/nologin g6j-agent
id g6j-operator
id g6j-service
id g6j-agent
```

Require four distinct kernel UIDs including root, three distinct private nonzero GIDs, no sudo/admin/supplementary groups. Do not alter sudoers, SSH, systemd or firewall. Human-complete the approval template from independently verified identifiers; create /etc/g6k-disposable-approved.json exclusively with mode0600, root owner, no links. Do not place secrets in this public identity record. A concrete non-overwriting creation command, once the reviewed JSON is at /media/reviewed/approved.json:

```sh
/opt/g6j-venv/bin/python -I -B -c 'import os,pathlib; raw=pathlib.Path("/media/reviewed/approved.json").read_bytes(); fd=os.open("/etc/g6k-disposable-approved.json",os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600); os.write(fd,raw); os.fsync(fd); os.close(fd)'
```

Verify the completed approval record and dependency-artifact digest against the external human record. Detach offline media and verify mounts again. `/var/lib/g6j-disposable` must not exist. A preexisting or failed tree is preserved and blocks retry.

## Validation and execution order

```sh
cd /opt/g6j-release/disposable
/opt/g6j-venv/bin/python -B -m unittest runner_tests prequalification_tests -v
# Substitute the independently approved ARTIFACTS.json digest below; never infer approval.
/opt/g6j-venv/bin/python -B offline_artifacts.py /opt/g6j-release --root /opt/g6k-offline --expected APPROVED_ARTIFACT_RECORD_SHA256
cd /opt/g6j-release
env -i PATH=/usr/bin:/bin HOME=/root PYTHONDONTWRITEBYTECODE=1 /opt/g6j-venv/bin/python -B /opt/g6j-release/disposable/qualify_all.py
```

The standalone unprivileged tests create only temporary fixture subdirectories; run them as a dedicated preparation identity against its own reviewed copy if source tree permissions prohibit that. Do not grant service/agent write access to the installed root release to make tests pass. The privileged runner does not need to write source.

Runner order: exact approval/environment/source/dependencies/capacity → no_new_privs/non-AF_UNIX denial → exclusive fixture → four actual role processes → signature/peer/nonce/succession → CLOSED/start/OPEN lost response/permit → DAC/path attacks → concurrent acceptance → protected fake possible-send/unknown → app rollback → journal reopen/replay → logical service-UID supplement. No real models, production states or operational tools.

## Evidence, missing confirmations and failure handling

Cross-UID report, same-UID JUnit supplement and kernel UID/PID observations must remain distinct. Check evidence/qualification-matrix.json before claiming completion. Existing runner journal reopen is not actual helper process restart; the positive four-attempt/settlement and malformed-wire permutations in the supplement also do not by themselves establish all cross-UID scenarios. Obtain targeted actual-UID evidence before marking those requirements PASS. Until then qualification is incomplete even if the prepared subset exits0.

Retain /var/lib/g6j-disposable/report.json, qualification.json, suite-stdout.txt, suite/cases.xml and EVIDENCE-SHA256SUMS. Verify with `sha256sum -c EVIDENCE-SHA256SUMS`; record its digest externally. Export only these allowlisted, reviewed public reports and approved VM identity/version summaries. Never export signing.key, credentials, raw environments, arbitrary journals or whole guest filesystems. Missing acknowledgments remain uncertain; no automatic repair/refund/retry. Setup refusal=BLOCKED; an attempted invariant failure=FAIL; unattempted=NOT RUN. On any failure preserve the tree and stop. A new run requires review, new clean state and explicit approval. VM deletion/snapshot restore/fixture/key cleanup require separate authorization.
''')
print('Wrote preparation reports; final/test/production reports await completed regressions.')
