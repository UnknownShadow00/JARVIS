# VM163 offline side-by-side update — human review only

**NOT EXECUTED. No privileged VM update or qualification is authorized by this packet.** Obtain the exact update approval described in REMAINING-AUTHORIZATION.md first. The procedure preserves `/opt/g6j-release` and `/opt/g6j-venv`. Never run `qualify_all.py` as part of this update.

## Transfer and independently verify

From the private Nexus artifact directory, transfer exactly:

- `gate6k-vm163-preflight-r1.tar`
- `safe_extract_vm163_r1.py`
- `REPLACEMENT-ARTIFACTS-SHA256SUMS`
- This review packet and separately retained evidence seal.

Do not transfer `release-r1` test runtime directories, synthetic signing material, Nexus virtualenvs, environment files or arbitrary home-directory contents. Use approved offline media, not a NIC or SSH forwarding. The example below requires the approved human to present reviewed read-only update media at `/mnt/g6k-update`; mounting/presenting that media requires its own reviewed operation. The existing `/mnt/g6l-cd` is preserved until separately approved media detachment.

Through the trusted console independently verify pve,VM163,UUID `1d279e9b-12cb-4a02-8815-a682cb9457a9`, guest `jarvis-security`, machine-id, exact disk, no NIC/routes/shared mounts, no imported credentials, and the approved console/session. Do not infer these from a local marker. Compare the hashes below against the independently retained operator record before executing any supplied Python.

## Explicit root-console update commands, only after update approval

Stop on the first failure and preserve the newly created directory. No automatic cleanup/retry, directory replacement or broad chmod/chown.

```bash
set -eu
umask 077
test "$(id -u)" = 0
test "$(hostname -s)" = jarvis-security
test ! -e /opt/g6k-update-r1
test ! -L /opt/g6k-update-r1
test ! -e /opt/g6k-preflight-r1
test ! -L /opt/g6k-preflight-r1
test ! -e /var/lib/g6j-disposable
test ! -L /var/lib/g6j-disposable
mkdir -m 0700 /opt/g6k-update-r1
install -o root -g root -m 0600 /mnt/g6k-update/safe_extract_vm163_r1.py /opt/g6k-update-r1/safe_extract_vm163_r1.py
install -o root -g root -m 0600 /mnt/g6k-update/gate6k-vm163-preflight-r1.tar /opt/g6k-update-r1/gate6k-vm163-preflight-r1.tar
printf '%s  %s\n' '31f77b42d6ee41f73abef56f8a59d5191a8695686cc2e79ced28236b623639d8' /opt/g6k-update-r1/safe_extract_vm163_r1.py | sha256sum -c -
printf '%s  %s\n' '15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55' /opt/g6k-update-r1/gate6k-vm163-preflight-r1.tar | sha256sum -c -
/opt/g6j-venv/bin/python -I -B /opt/g6k-update-r1/safe_extract_vm163_r1.py /opt/g6k-update-r1/gate6k-vm163-preflight-r1.tar 15d2fe9c5acb517b7b0b94595a8940d60c027889b5a60a66050993171088ae55 b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc --destination /opt/g6k-preflight-r1
printf '%s  %s\n' 'b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc' /opt/g6k-preflight-r1/SOURCE-SHA256SUMS | sha256sum -c -
(cd /opt/g6k-preflight-r1 && sha256sum -c SOURCE-SHA256SUMS)
```

Expected extraction result: PASS,619 members. This is archive installation only, not qualification. The extractor rejects unsafe archive structure and verifies all bytes before exclusive destination creation; it does not execute archive members. It normalizes only newly created files/directories and preserves partial failures. Code is executed from the newly protected staging directory after pinned hash verification, not directly from a preparation-user-writable home.

## Read-only diagnostics, only after approved installation

These commands do not invoke the qualification runner or create its fixture. They inspect protected source, package version metadata, and directory metadata. They do not open credential/cache contents. Review output locally and share only aggregate diagnostic codes/counts/digests. No raw environment, cloud-init data, private key or credential-file dump.

```bash
/opt/g6j-venv/bin/python -I -B - <<'PY'
import json,sys
from pathlib import Path
root=Path('/opt/g6k-preflight-r1')
sys.path.insert(0,str(root/'disposable'))
from safety_preflight import verify_manifest,validate_dependencies
count=verify_manifest(root,'b69f43a9b77c066342834a78dbabc40fefe71aeef18588def03d8a2878e559fc')
validate_dependencies(root)
print(json.dumps({'verified_source_files':count,'required_versions':'MATCH','qualification':'NOT_RUN'}))
PY
/opt/g6j-venv/bin/python -I -B /opt/g6k-preflight-r1/disposable/preflight_report.py > /opt/g6k-update-r1/preflight-metadata.json
cat /opt/g6k-update-r1/preflight-metadata.json
```

Expected source count618. Report status is always INFORMATION_ONLY / QUALIFICATION_NOT_RUN. A still-mounted transfer ISO, missing artifact root/marker, unreviewed cloud cache or actual credential payload are unresolved prerequisites, not successful security tests. The metadata report intentionally does not certify interpreter filesystem protection, VM identity, role groups, free disk, complete artifact integrity or external isolation.

The existing dependency export must be separately reviewed/provisioned at `/opt/g6k-offline` (currently absent). Historical expected `ARTIFACTS.json` SHA256 is `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837`; verify actual exported bytes and independently approve their provenance. This source update does not install/copy dependencies or grant that provisioning authority. After its separately reviewed installation, this read-only check is available:

```bash
/opt/g6j-venv/bin/python -I -B - <<'PY'
import json,sys
sys.path.insert(0,'/opt/g6k-preflight-r1/disposable')
from offline_artifacts import verify_artifacts
print(json.dumps(verify_artifacts('/opt/g6k-preflight-r1','/opt/g6k-offline','9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837')))
PY
```

Expected131 artifact records. This verifies integrity, not publisher authentication or permission to run. No old archive/source digest is silently substituted.

## Approval record review, not installation

`APPROVAL-TEMPLATE.json` is intentionally invalid and **must not be installed as-is**. It identifies known VM163 facts and replacement hashes; it leaves machine-id,disk,console,preservation and cloud provenance unresolved. Optional `boot_source` must match `/dev/sda2` only if the human reconfirms it. If populated cloud cache can legitimately receive the explicit review, include its exact current metadata digest. If no regular cache files exist after metadata inspection, omit `cloud_cache_review`; do not erase files to create that condition.

Only a separately approved human may create the final root-owned0600 `/etc/g6k-disposable-approved.json`, after all identity, isolation, artifact and credential conditions pass. Do not overwrite an existing marker automatically. Capture current private-group/non-login-role evidence and minimum20GiB free. Separately approve detachment of all offline media before qualification. No change to mounts, services or credentials is authorized merely because a check refuses.

The future qualification command, requiring another explicit execution authorization, is listed in REMAINING-AUTHORIZATION.md and deliberately not included in these executable update blocks. Preserve all update and later failure evidence. No V2/V3 production changes or model operations are permitted.
