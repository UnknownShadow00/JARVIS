# Root and signer provisioning — NOT AUTHORIZED / NOT EXECUTED

Actual Core users/groups/helpers/permissions/units/SSH/sudo/credentials remain unchanged. Execute MULTI-UID-QUALIFICATION in an approved disposable VM before production provisioning. The protected writer should run as non-login jarvis-authority; root installs immutable helper/policy and protected parents. Service and agent must lack ACL/group/parent/import/descriptor access; review backup/process-manager privileges too.

Separately approved human-only change set:

1. Freeze verified release/config/dependency/unit/public-key-policy identities; preserve V2 archive and current metadata. No automatic source pull or dependency download during cutover.
2. Provision jarvis-v3 and jarvis-authority non-login identities, separate human jarvis-op and dedicated control group. No shared service/human UID, service sudo or agent-held key.
3. Install root-owned release/config/dependency paths and parent0755, private authority0700/DB0600 and service0700 roots per design. Verify all ancestors, ACLs, mounts, capabilities and groups. Copy real predecessor archive read-only without rewriting bytes/meaning or blind chown/reset of D06.
4. Provision real human signing key outside agent/service access. Public key only in root policy. Prefer a reviewed hardware signer with explicit presence; Ed25519 alone does not prove touch. If authenticated private-console signing is chosen, explicitly approve its confirmation/presence policy and threat model. No Bearer-accessible signer. Display exact canonical fixed-schema command and bindings before signing. Real signer/presence integration is absent.
5. Install narrowly confined helper: no shell/network/provider/admin/path/SQL API. Separate operator/service AF_UNIX sockets, actual peer checks, bounded request/reply. Bind source/config/release, epoch, PID/start/boot/invocation/challenge, checkpoint, nonce, expiry. Use shared wall-clock UTC, not boot-relative monotonic time for signer envelopes; refuse clock drift/rollback. Durable nonces/seq supply replay protection.
6. Decide/provision independently controlled external witness and backup/recovery if stronger host/root rollback assurance is required. Receipt durable before acknowledgement; recovery must preserve consumed authority. No witness exists here; no local-only acceptance inferred.
7. Provision application credentials using approved human/root loader, e.g. systemd LoadCredential plus reviewed private credential-file reader. No source/argv/environment dump/task document/agent access. A root0600 drop-in alone is not a safe service credential interface. Loader and explicit pinned crypto dependency remain unimplemented release prerequisites.
8. Verify real service/agent write denials, signer isolation, checkpoint/terminal reader trust and no production bypass. Startup remains CLOSED with zero generation. Provisioning alone never authorizes retirement, succession, deployment/pilot opening or measurement.

No private keys/passwords, secret hashes or protected environment contents are requested. Exact future commands require approved host/path/UID/release records; placeholders are never defaults.
