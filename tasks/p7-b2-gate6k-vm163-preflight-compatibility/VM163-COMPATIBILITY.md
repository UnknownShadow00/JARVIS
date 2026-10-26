# VM163 compatibility and remaining preflight conditions

Operator-supplied identity: pve, VM163 `jarvis-security-lab`, guest `jarvis-security`, UUID `1d279e9b-12cb-4a02-8815-a682cb9457a9`; Ubuntu26.04 LTS x86-64;4vCPU,6000MiB RAM,40GiB disk,private ext4,lo only. This task did not access the VM or hypervisor.

| Reported setup | Corrected policy / remaining status |
|---|---|
| Root-protected `/opt/g6j-release` with Gate6K source | Preserve. New approval must bind the side-by-side `/opt/g6k-preflight-r1` and its new manifest/archive. |
| `python -I -B .../qualify_all.py` | Isolated import defect repaired and import-only regression passes. Qualification entrypoint was not executed. |
| `/opt/g6j-venv/bin/python` → `/usr/bin/python3.14` | Compatible in principle with reported protected runtime. Same Python3.14.4/SQLite3.46.1/crypto46.0.5/pytest9.1.1 verified on Nexus test interpreter. VM provenance/permissions remain separately operator supplied. No runtime installation changed. |
|127 exact versions | Pin files unchanged. Operator reports VM match; fresh local VM checks still required after update. |
| `/home/jarvis` prep home | Existence alone accepted subject to exact account owner/permissions, known credential indicator refusals and independent no-imported-credentials review. |
| `/run/credentials`, service tmpfs mounts | Empty protected directory topology can pass. Actual payload files still block. Their presence is UNKNOWN; no claim that this condition is resolved. |
| `/var/lib/cloud/instance` | Canonical alias supported. Complete cache metadata must pass and populated cache requires explicit provenance review bound to its metadata digest. UNKNOWN until human-only report/review. |
| `/boot` ext4 `/dev/sda2` | Supported only through explicit `boot_source` approval. `/boot/efi` or other disks are not silently admitted. |
| `/mnt/g6l-cd` mounted ISO | Known continuing qualification blocker. Future separately authorized human detaches offline media after transfer/verification; no automatic unmount. |
| `/opt/g6k-offline` absent | Known continuing blocker. Exact reviewed131-record offline artifact export must be installed under protected ownership separately. No package substitution or network installation. |
| `/etc/g6k-disposable-approved.json` absent | Known continuing blocker; no current execution approval. Exact new release identity, VM machine-id, disk, console, policy and any cloud review are required. |
| `/var/lib/g6j-disposable` absent | Required initial state. Preserve absence until separately authorized qualification. If any attempt creates it then fails, preserve it and require new reviewed clean-state authorization. |
| UIDs0/999/995/994 | Distinct as reported, not measured here. Private distinct GIDs, non-login shells, no supplementary/admin memberships remain unverified. Do not recreate accounts. |
|6000MiB RAM | Prior8GiB was an estimate, not a runner minimum. No guaranteed memory refusal found. Resource adequacy remains unmeasured. |
|40GiB disk | At least20GiB free required at `/var/lib`; actual free space not provided. No automatic cleanup. |
| Virtual mounts | No full fresh mountinfo available. Shared propagation, bind subtrees, autofs, overrides or extra mounts still block; do not infer their absence from “ordinary systemd mounts.” |

Nexus was freshly observed as Ubuntu26.04 LTS x86-64, kernel7.0.0-38-generic. The offline test interpreter matches Python3.14.4,SQLite3.46.1,cryptography46.0.5,pytest9.1.1 and all127 required distributions. Ubuntu26.04 compatibility is therefore exercised on that actual development OS, with synthetic fixtures for the supplied VM163 mount/path topology and an isolated Python launch/import test. It is **not an actual VM163 preflight PASS**, genuine distinct-UID test, Ubuntu image boot test, or attestation that credential stores are empty. Remaining unknowns deliberately fail closed.

No application/model contract changes: L1 rules-first semantics,8192 proposed normal context, four accepted attempts, REST/REST/WS/WS order, legacy-visible/Granite-observational separation, X1–X11 pending. Golden12/20 remains historical and was not run.
