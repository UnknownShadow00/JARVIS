# AI-host SSH trust investigation — separate pending human step

Gate5 attempted numeric jarvis@192.168.0.200:22, first from nexus-services.101 and then from Core.162. Both returned exit255, Host key verification failed, before remote application inspection. No alias, alternate IP or model HTTP fallback was used.

Read-only ssh -G confirms hostname 192.168.0.200, port 22, StrictHostKeyChecking=ask, CheckHostIP=no, normal per-user/global known_hosts paths and no configured ProxyJump/ProxyCommand or HostKeyAlias for that destination. BatchMode suppresses the interactive trust prompt; absence of a trusted key can therefore produce this failure. No SSH setting was changed.

On nexus-services, ssh-keygen -F for both 192.168.0.200 and ai-server found no match in current known_hosts or known_hosts.old. No matching global entry was found. Core has no ~/.ssh/known_hosts, known_hosts2 or either examined global known_hosts file. This supports missing prior trust in these contexts; it does NOT prove that a presented remote key is authentic, nor that the host was replaced. No key was fetched, accepted, removed or overwritten. No current remote fingerprint or Ollama PID/restart count is asserted.

No expected SSH public host-key fingerprint was found in the examined trusted B2/Gate4/Gate5 and B1 infrastructure evidence/documentation. Artifact SHA256 seals are not SSH host-key fingerprints. The sealed B1 inventory associates AI-VM with VMID 200, hostname ai-server and endpoint192.168.0.200; it does not supply a current trusted public SSH key.

Smallest remaining HUMAN step: establish an independently trusted console to the correct AI VM (for example, authenticated Proxmox UI console after verifying VMID 200 and the actual guest IP/hostname). Existing .50→Core SSH is not that console. On the verified AI guest console, read ONLY public host-key metadata:

```sh
hostname
ip -br address
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

Record key type and SHA256 fingerprint from that trusted channel. If ED25519 is not configured, inspect the actual configured public host key through the same trusted console; do not guess or fall back blindly. Never read a private host key. Compare the public fingerprint with the SSH key presented for the exact numeric destination. Only after independent identity verification may the operator separately authorize a deliberate known_hosts pin under their normal policy. No automatic acceptance, StrictHostKeyChecking=no, ssh-keygen -R, blanket deletion or overwrite is appropriate here.

After that separate trust step, a later authorized read-only session can inspect Ollama systemd ActiveState/SubState/MainPID/InvocationID/NRestarts/start timestamp with StrictHostKeyChecking=yes. No privileged remote action, model HTTP request or lifecycle operation is necessary. This unresolved visibility issue does not require changing Core or running the human application-auth helper against another address.
