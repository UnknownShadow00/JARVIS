# Exact remaining human boundaries

This task authorizes Nexus engineering only. It does not approve a VM update or privileged qualification. VM163's existence, its manually prepared runtime and its four reported UIDs are not an execution authorization.

## Approval 1 — offline side-by-side update and read-only diagnostic

Human approval must identify pve, VMID163, UUID `1d279e9b-12cb-4a02-8815-a682cb9457a9`, guest `jarvis-security`, the trusted console/session, exact private disk and offline media; authorize exclusive creation of `/opt/g6k-update-r1` and `/opt/g6k-preflight-r1`; and bind the replacement archive/manifest/bootstrap hashes in SOURCE-AND-MANIFEST.md. Preserve `/opt/g6j-release`, `/opt/g6j-venv`, historical archives, preparation files and the absent qualification fixture. Read-only metadata diagnostics are a separate operation from qualification. The update procedure never runs `qualify_all.py`.

## Approval 2 — unresolved environment preparation

The human must review and approve any needed changes separately: protected offline artifact installation at `/opt/g6k-offline`, media detachment, and any response to actual credential/mount findings. Neither this package nor its report authorizes deleting credentials, hiding paths, stopping services, modifying mount propagation, changing permissions broadly, reconfiguring accounts or connecting a NIC. If active credentials or unsafe topology remain, stop and review them; do not bypass the refusal.

Cloud-init review cannot be assumed from fresh-looking filenames or root ownership. Only when independently established from installation/preparation provenance may the human approve `FRESH_DISPOSABLE_IMAGE_NO_IMPORTED_CREDENTIALS` bound to the report's current metadata digest. Unknown provenance remains blocked. The report never asks for cache contents, keys, passwords or environment dumps.

## Approval 3 — exact privileged qualification

After the above prerequisites, a separate explicit authorization must name:

- VMID163, UUID above, pve, guest machine-id, exact private disk identity and approved console/session.
- Exact replacement archive/manifest identities and protected release `/opt/g6k-preflight-r1`.
- Protected interpreter `/opt/g6j-venv/bin/python`, independently verified127 pins and artifact record digest/provenance approval (including previously reported integrity-only packages).
- `/boot` source `/dev/sda2`, fresh safe mount inventory, no media/shared mounts, no external interfaces/routes/forwarded agents, no production credentials.
- Measured UIDs0/999/995/994, private GIDs, non-login shells and no supplementary/admin group access.
- Current cloud-cache metadata review when populated, no active systemd credential payloads, and minimum20GiB free.
- Scope `SYNTHETIC_MULTI_UID_NO_POWERCUT`, no provider/network/production operations, exact command, and snapshot/failure-preservation policy.

The future command is `/opt/g6j-venv/bin/python -I -B /opt/g6k-preflight-r1/disposable/qualify_all.py`. **It is not authorized or executed by this task.** The new root-owned0600 marker must bind the approved values; an old-digest marker cannot authorize changed source. Missing/placeholder values must refuse. A failed attempt after fixture creation must preserve all evidence; no automatic retry, reset or cleanup.

Genuine multi-UID qualification remains NOT RUN. Same-host root compromise and complete host rollback remain outside the protected-authority guarantee. X1–X11 and AI/legacy attestations remain pending. No V2 retirement, real successor, deployment, model generation, pilot opening or measurement authority is granted.
