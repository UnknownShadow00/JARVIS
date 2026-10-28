# VM164 r4 engineering result

**Corrected ISO built and locally verified; no VM access or successful installation claimed.** Task profile: `workspace-write`. All engineering/tests used local public artifacts on Nexus. No network/private-infrastructure request, privileged qualification, final marker, lifecycle operation or virtual-disk operation was performed. The current failed VM164 state was not accessed or changed.

Output:

```text
/home/nexus/.local/share/jarvis-g6k-vm164-installer-r4/ubuntu-26.04.1-g6k-vm164-r4.iso
SHA256 050875e2f3ffd5a7711bb2f520bce98404416d2117faedf2ba608831e2a416f3
Bytes  3042836480
```

The original r3 ISO remains at its previous path, unchanged, SHA256 `4161509164bcaff08506ad2ffcd52a6782eb34eb4b08d47f1bb8754016a07346`. Original r3 configuration, late guard and exact Subiquity7403 sources were copied into this packet's evidence for review. The operator-reported failure and identity values are retained; raw guest logs/RAM were not exported, and no external evidence retention is falsely claimed.

[Root cause and correction](ROOT-CAUSE-AND-CORRECTION.md): r3's `serial` selector used `lsblk`'s QEMU hardware serial, whereas7403 matches udev ID_SERIAL. r4 supplies one exact conjunction of `/dev/sda`, observed ID_SERIAL and ID_PATH, backed by an independent guard that keeps the QEMU serial/UUID/size/single-disk/signature checks and adds udev uniqueness. No arbitrary selection, wildcard or fallback exists.

Tests: **18 passed,0 failed**, using synthetic positive/negative cases, the actual pinned Subiquity matching method bodies and pure future-console bindings. r3's zero-candidate failure is reproduced; r4 selects only the intended fixture disk. These are userspace/fixture results, not an installation, firmware/kernel proof or Gate6K qualification.

ISO verification:839 r3 file records→840 r4 records, no removed files, one new early guard. Only autoinstall YAML, checksum manifest and relocated boot catalog changed;836 r3 file records remain identical. The BIOS boot image has no byte changes; the hidden UEFI payload is also byte-identical. The entire credential-free source Squashfs and late target guard remain byte-identical.833 original public OS file records, including original kernel/initrd/package payloads, reverify against the independently pinned original ISO; its previously documented derivative source/boot/checksum changes remain the only original-file differences.

All other autoinstall configuration, credential/isolation requirements and mount policy are unchanged. The new ISO is a locally built derivative of retained authenticated-input media, not newly Ubuntu-signed. Existing supplier/tooling trust limitations carry forward. No application/security-release source or dependency pins were changed, so no application regression result is claimed. Full runtime Subiquity/curtin installation remains untested.

[Exact trusted-console handoff](TRUSTED-CONSOLE-HANDOFF.md) provides failed-state retention checkpoints, standalone inspect/stopped optical replacement/prestart blocks and the conditional future retry command. Current authorization is ISO engineering only. **Next authorization:** after sufficient independently retained failure evidence, explicitly authorize VM164-only lifecycle/media replacement and normal installation writes during retry. If volatile evidence cannot be retained adequately, leave the failed VM intact. No automatic shutdown/reset or disk erasure is proposed.

Build/test sources are in `tools/`; source and ISO comparisons are in `evidence/`. Outputs are exclusive: repeat builds must use a separately reviewed new output location/revision, never overwrite r3/r4 or prior evidence. `SHA256SUMS` and its external seal cover this packet. `tasks/loop-log.md` records completion of this engineering stage only.
