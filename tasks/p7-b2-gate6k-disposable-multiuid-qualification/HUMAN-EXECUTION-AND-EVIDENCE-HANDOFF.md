# Human execution handoff — BLOCKED until artifacts and exact approval

This is a future human-console procedure, not authorization to execute it. No approved VM exists. Estimated4vCPU/8GiB/40GiB private ext4/noGPU/noNIC; require20GiB free. Independently verify the VMID/UUID/node/disk/machine-id through the trusted management console and match OPERATOR-APPROVAL-TEMPLATE.json. Verify fresh image provenance, only loopback, no routes to production, no shared mounts/host credentials/SSH agent. Copy reviewed artifacts via approved offline media, then detach media before qualification. Do not reconnect networking.

## Offline artifact preparation boundary

The exact127-version list includes system distributions. The actual interpreter/wheelhouse/OS artifact set and install procedure are NOT supplied, so installation is BLOCKED. Do not use the old blanket pip command or invent package versions. The human supply-chain reviewer must provide an offline image/environment reproducing the pins, rooted at /opt/g6j-venv, with root-owned non-writable interpreter/import paths. Keep the actual131 reviewed artifacts and completed ARTIFACTS.json in /opt/g6k-offline. Use the null-filled required inventory as a request, not an accepted manifest. Verify upstream signatures/build records externally and retain the completed artifact-record SHA256 outside the VM. This missing independent input cannot be generated from version strings.

## Reviewed release extraction

Copy the standalone tools/safe_extract.py through reviewed offline media BEFORE unpacking the source. Independently retained bootstrap SHA256: `1a0c09e8e5ee5c76870deb41986328a3cf7836ae2ea0548d29b1dfacc77f589b`. Archive: `/home/nexus/.local/share/jarvis-gate6k-prequalification/gate6k-release-r2.tar` (transfer only this archive); SHA256 `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d`. Source manifest SHA256 `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03`. The following commands are explicit privileged actions for the named VM's human root console only, after exact Phase B approval. `/opt/g6j-release` is retained as a compatibility path inside this disposable VM; the installed content is Gate6K.

```sh
# Review expected values against the independent approval record first.
printf '%s  %s\n' 1a0c09e8e5ee5c76870deb41986328a3cf7836ae2ea0548d29b1dfacc77f589b /media/reviewed/safe_extract.py | sha256sum -c -
printf '%s  %s\n' ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d /media/reviewed/gate6k-release-r2.tar | sha256sum -c -
# Uses an independently reviewed offline Python interpreter; no archive code import.
/opt/g6j-venv/bin/python -I -B /media/reviewed/safe_extract.py /media/reviewed/gate6k-release-r2.tar ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d 5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03
/opt/g6j-venv/bin/python -I -B /media/reviewed/safe_extract.py /media/reviewed/gate6k-release-r2.tar ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d 5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03 --destination /opt/g6j-release
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
