# Human-only AI host trust procedure

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

Status: PENDING. No independent public host-key fingerprint or effective Ollama process identity was established by this task. No known_hosts changes or model requests.

Through the operator's already trusted Proxmox console/inventory (management192.168.0.50), first identify actual placement; do not assume VMID200 runs on that node:
```
pvesh get /cluster/resources --type vm --output-format json
qm config 200
```
Run qm config on the node actually owning VMID200. Compare inventory VM name, interfaces/MACs, disk and console identity. These are prepared human commands, not executed by Codex.

From the trusted guest console, read public host-key fingerprints:
```
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
hostnamectl
ip -br address
```
Compare independently with network-presented public material. A human may save `ssh-keyscan -t ed25519 192.168.0.200` to a new private temporary comparison file and run `ssh-keygen -lf <file> -E sha256`. ssh-keyscan alone is not trusted identity and must never append automatically to known_hosts. Preserve fingerprint, console/inventory provenance and matching result; obtain separate enrollment approval before changing trust files.

After trusted access is approved, inspect Ollama identity without generation/lifecycle actions:
```
systemctl show ollama.service -p MainPID -p FragmentPath -p ExecStart -p ActiveState
ps -eo pid,ppid,user,comm
ss -ltnp
systemctl list-timers --all
```
Do not dump process environments or credential-bearing service contents. Have the operator inventory cron, supervisors, wake/unload jobs and direct clients using trusted access with secret-aware redaction. Establish ownership of every endpoint/host/GPU conflict domain and a bounded pilot window with independent readbacks before/after. Any suspension or modification of competing automation requires separate approval; these commands do not authorize it. No Ollama restart/load/unload/generation or Proxmox change is part of this task.
