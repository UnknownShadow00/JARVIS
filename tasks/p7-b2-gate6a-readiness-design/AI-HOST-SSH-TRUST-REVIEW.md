# AI host identity: pending independent human verification

Status: **AI_HOST_IDENTITY_TRUST_PENDING_HUMAN_VERIFICATION**. No guest SSH connection, network keyscan, model request, key acceptance or trust-store modification was performed in Gate6A.

The sealed Gate5 failures targeted numeric `jarvis@192.168.0.200:22` from nexus and Core. Fresh `ssh -G` inspection on both hosts confirms hostname .200, port22, no canonicalization, HostKeyAlias, ProxyJump, ProxyCommand or KnownHostsCommand override; StrictHostKeyChecking=ask, CheckHostIP=no, VerifyHostKeyDNS=false. The permitted algorithms include ED25519, ECDSA, RSA-SHA2, security-key and certificate variants. **That list is not a negotiated algorithm.** The original minimized error does not establish which public key was presented. No new guest handshake was made to obtain one.

On nexus, applicable paths are `/home/nexus/.ssh/known_hosts`, `known_hosts2`, `/etc/ssh/ssh_known_hosts`, `ssh_known_hosts2`; `known_hosts.old` was additionally examined. ssh-keygen lookups for numeric .200, `[192.168.0.200]:22` and ai-server return no matching public key. Core's four applicable files are absent. The numeric default-port lookup normally uses .200; bracket form and historical alias were checked without treating them as interchangeable authorities.

These findings support **missing established trust** in the examined contexts. They do not prove a host replacement, stale/mismatched key, authentic new key or benign network path. Numeric destination/no canonicalization makes hostname remapping unsupported by the inspected configuration. No current fingerprint is asserted. A network-observed key would be only a candidate until independently compared.

Fresh checks found one existing nexus known_hosts match for Proxmox .50. This is a pin for that host, not proof of guest .200's identity, VM placement, available administrative credentials, a console session or guest authority. No documented authenticated Proxmox administrative route available to Codex was established from the examined records, and no guessed account/credential or guest-execution fallback was attempted. Subsequent Core metadata sessions explicitly disable UpdateHostKeys so they cannot learn additional keys implicitly.

Historical sealed B1-R2/operator inventory associates .200 with ai-server, AI-VM/VMID200, 24576MiB and balloon0. It does not prove the VM's current hosting node, a relationship to .50's physical placement, or an SSH public-key fingerprint. B1 and B1-R2 bundles are checksum-consistent; Gate4's pinned seal anchors its historical AI observations. Examined B1/B2 trust/infrastructure records supply no authoritative current public fingerprint. An artifact checksum is not a host-key fingerprint.

## Smallest remaining human step

Through the operator's authenticated Proxmox management UI, inspect cluster inventory to identify VMID200's **actual node**, guest name and console. Do not assume VM200 is hosted on .50 merely because .50 is the management entry. Confirm the guest IP/hostname through the verified VM console. Read public metadata only:

```sh
hostname
ip -br address
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

Record the verified node/VM relationship, exact guest IP, key type and SHA256 public fingerprint from that trusted channel. If ED25519 is absent, inspect the actual configured public host key through the same console; never inspect a private host key or guess the algorithm. Public fingerprints are safe to report; no private key/password is requested.

Compare the independently obtained fingerprint with the key offered for the exact numeric destination and matching algorithm. Any deliberate known_hosts pin is a **separate operator action/approval**, not authorized automation in Gate6A. Do not use StrictHostKeyChecking=no, autoaccept, delete a mismatch or overwrite trust. Only after that identity and access are established should fresh guest read-only inspection proceed. The existing .50→Core SSH session is not proof of AI VM console access.
