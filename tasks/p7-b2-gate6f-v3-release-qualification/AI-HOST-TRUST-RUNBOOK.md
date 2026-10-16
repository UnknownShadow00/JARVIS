# AI-host trust runbook (human only)

Status: **PENDING**. Nothing below was executed. No known_hosts change, no Ollama API call, no Proxmox change, no external actor change.

Also investigate: Core (192.168.0.162) received an ACPI power-button event at 2026-10-15T03:42:17Z and rebooted. Identify who or what issued it (Proxmox task log for Core's VMID) before trusting any pilot window on this cluster.

## Steps (Proxmox console, management 192.168.0.50)

1. **Placement** — `pvesh get /cluster/resources --type vm --output-format json` → find VMID 200 and its node. On that node: `qm config 200`. Record node, name, MACs, disks. Also record `pvesh get /nodes/<node>/tasks --vmid <Core VMID> --limit 20` for the 2026-10-15 power event.
2. **Guest identity** (VM 200 console, not SSH): `hostnamectl`, `ip -br address`, `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256`.
3. **Independent comparison** — from a separate machine, into a new private temp file: `ssh-keyscan -t ed25519 192.168.0.200 > /tmp/g6f-ai.keyscan; ssh-keygen -lf /tmp/g6f-ai.keyscan -E sha256`. Fingerprints must match step 2. Never append to known_hosts.
4. **Enrollment** — stop here. SSH enrollment needs separate written approval.
5. **Ollama identity and counters** (console): `systemctl show ollama.service -p MainPID -p ExecStart -p ActiveState -p NRestarts`, `ollama --version`, `ollama list`, `ollama ps`, `ss -ltnp | grep 11434`. Then run LEGACY-IDENTITY-ATTESTATION-DESIGN step 3–4 for the models. No generate/load/unload.
6. **External actors** — `systemctl list-timers --all`, `crontab -l` for each user, `systemctl list-units --type=service | grep -i -E 'ollama|jarvis|hermes|unload|wake'`, and `ss -tnp | grep 11434` over a few minutes for direct clients. Record names and schedules only; redact secrets.
7. **Pilot window proposal** — a finite window (e.g. 60 min) where the operator pauses every listed actor, with before/after readbacks of `ollama ps` and step 5 counters. Pausing anything needs its own approval.

Output: one nonsecret record with placement, fingerprints (both sources), Ollama identity, actor inventory, proposed window, operator name and UTC. That record feeds `HostAttestation(..., 'HUMAN_ATTESTED')`.
