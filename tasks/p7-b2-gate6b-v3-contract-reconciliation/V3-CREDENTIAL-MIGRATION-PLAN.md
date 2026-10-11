# HUMAN-ONLY new credential provisioning — design only

The existing `/home/jarvis/.config/jarvis/p7-b2.env` remains untouched. Codex has not opened, hashed, copied or moved it, inspected process environments, or executed the human auth helper. Its current metadata is checked by the reviewed read-only collector only. V2 continues using its current private material.

The proposed service identity needs a **new human-private credential provisioning ceremony**. Do not make the old env file broadly readable or copy it through Codex. Recommend a fresh independent token provisioned privately by the human into a root-private fixed source path for systemd LoadCredential; a reviewed V3 credential loader reads only the private runtime credential. This is a code/deployment change: current code expects JARVIS_API_TOKEN/env-file handling and does not already implement this loader. No compatibility claim is made before qualification.

Future private handoff, after separate identity/credential approval:

1. Human enters the independently authenticated Core administrative session; verifies actual host, approved release/unit and fixed destination directory metadata. This must be an operator privilege unavailable to Codex as jarvis.
2. Through a reviewed private interactive provisioner, generate/provision the new high-entropy token with no terminal echo, argv, URL, environment export, shell tracing, history, clipboard/report or telemetry exposure. No generic secret-reading helper is added in this task. Verify no-symlink regular-file creation, owner root, mode0600, private0700 parent, no unexpected ACL/hard link. Codex may later inspect metadata only.
3. Human supplies that new token privately to the approved header-capable client boundary; do not paste it into Codex or task evidence. API authentication remains distinct from signed opening authority. The operator, not Codex, owns any private distribution/rotation.
4. New system supervisor provides the service-private read-only credential. Fail closed on absent/malformed/wrong metadata; no fallback to the old env file or unauthenticated operation. Loader never logs bytes, digest, header or secret-bearing exception. Keep token out of general process environments.
5. After approved V3 CLOSED startup, separately authorize a new reviewed positive-only human no-message authentication procedure and independent readback. Old Gate5 proves the V2 deployment only; old helpers pinned to V2 PID/config are not reused unchanged. No negative production auth probe.

Do not revoke or alter V2's credential while it is still running. Retain old credential private and inaccessible to new service until a later explicit retirement/disposal decision; this packet authorizes no secret deletion. Secret files are excluded from backups/evidence. A human attestation plus metadata is evidence of provisioning, not Codex verification of token value. Human live auth and post-probe zero-state evidence are separate stages.

Offline qualification must exercise the actual proposed credential loader with disposable dummy files, symlinks, wrong owners/modes/ACLs, malformed values and namespace isolation under real test UIDs before deployment. Gate6B models the access policy only; no new UID/root capability was created to claim a kernel-enforced denial test.
