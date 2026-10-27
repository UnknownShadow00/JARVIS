# VM164 continuation handoff

**Ready for guarded stopped-VM console preparation; NO-GO for starting6000MiB from current memory evidence. No VM exists as a result of this task.**

The trusted operator reports successful pve inventory and candidate164. This session did not retry SSH, contact the PVE API or execute privileged PVE/guest commands. The operator summary advances infrastructure knowledge; live backend/identity/capacity checks still belong immediately before allocation. VM163 remains running and preserved as reported. No access/change to VM162 or the AI server, provider request, production service launch, namespace/propagation change, final approval marker or privileged qualification occurred.

## Deliverables

- [Immediate read-only console block](NEXT-CONSOLE.sh):30-second PSI/swap/OOM/headroom sample, running allocation summary, downloads backend and VMID recheck.
- [Provisioning plan](VM164-PROVISIONING-PLAN.md), [inspect-only block](INSPECT-CREATION-CONSOLE.sh), [stopped creation block](CREATE-STOPPED-CONSOLE.sh) and [verified media attachment block](ATTACH-INSTALLER-CONSOLE.sh): exact standalone commands for the trusted node console. No start path. They are source-reviewed and their pure guards/command construction are tested; execution on PVE is **not tested**.
- [Media/provenance record](MEDIA-PROVENANCE.md): validated source-image omission of the proven-empty public `/root/.ssh`, pre-first-boot cloud-init sentinel, full unchanged-file comparison, original media/tool chain, derived ISO hashes and limits.
- [Offline installation/fresh identity procedure](OFFLINE-INSTALL-AND-VALIDATION.md): input verification, VM/disk-bound virgin-disk guards, target evidence, role identities, console bootstrap option, metadata-only diagnostics and protected-installation stop points.
- `VM164-PLAN.json`: **planned** UUID/serial/hardware; actual volume and machine-id remain null.
- `evidence/`: original/derived comparisons, tool/package provenance, operator-reported memory assessment, guard tests and verification report.

## Decisions supported now

6000MiB is6.291GB. The reported12.64GB available leaves6.349GB before overhead/growth, while swap has only0.89GB left. Existing swap use is not alone a measurement of current thrashing, but runtime admission is unsupported. This plan retains8GiB physical headroom plus a1GiB allowance, requiring15.955GB available even before representative peak/commitment review. Do not start with current evidence or reclaim RAM from existing VMs. Stopped creation configures6000MiB without consuming that guest RAM and is separately feasible only after live storage/target checks pass.

The exact signed source was transformed without mounting, privileged extraction, deleting evidence or editing a Gate6K check. The only source-tree differences are omission of the proven-empty directory object and addition of an empty cloud-init disable sentinel. All other79,986 metadata/data records compare equal. Original65,249 regular-file records retain their contents. The unchanged corrected release's618 files reverify against the retained source digest.

Final r3 installer ISO and the nonbootable public-data ISO are physically prepared on Nexus. Their embedded file inventories/hashes validate. Eleven ISO-pinned literal installer schemas and synthetic UUID/serial/NIC/virgin-disk refusal cases pass. Full installer execution, actual first boot and scanner acceptance remain **not tested**. The target guard stops if `.ssh` is regenerated; it never repairs/deletes the finding. Neither image is represented as an Ubuntu-signed derivative. Intermediate r1/r2 drafts remain retained and must not be uploaded in place of r3.

## Outstanding gates

1. Execute trusted-console read-only checks; confirm actual downloads directory/backing storage supports the reviewed implementation. Unsupported/thin/network backends refuse pending backend-specific review. Recheck free164/no orphan volumes and capacity immediately before creation. Return actual protected creation evidence before claiming a built VM.
2. Establish representative memory safety before any boot. Short samples cannot establish all future workload peaks; no auto-start follows a successful screen.
3. Actual Subiquity/curtin validation, root console boot, first-boot provenance, fresh disk/filesystem/machine identities and role metadata. Preserve installer/cache/credential findings on refusal; no post-boot deletion/chmod workaround.
4. Protected offline runtime and source/artifact installation, resolved interpreter/native-library protection, exact pins/inventory, at least20GiB available and media removal. The supplied old fixture builder still refuses root and is not a protected runtime installer; that exact protected implementation remains pending.
5. Explicit mount-policy scope approval and corresponding metadata checks. Keep shared-propagation findings visible until policy is decided. Then separately reviewed identity-bound final marker and, later, explicit privileged qualification authorization; neither is part of this task.

VM163 should stay running and unchanged now. A later graceful power-off recommendation requires a real independently reviewed replacement, an agreed evidence/volatile-state retention plan and explicit VM163 lifecycle authorization. No shutdown, snapshot, cloning, export of unknown secrets or space reclamation is proposed to make room for164.

This turn used the repository's [verification-loop skill](</opt/apps/IT TRAINING PROJECT CODE/tools/everything-claude-code/skills/verification-loop/SKILL.md>) for scoped build, guard-test, source-preservation, syntax/security and diff checks. No application runtime changed; no application regression or kernel qualification result is claimed.
