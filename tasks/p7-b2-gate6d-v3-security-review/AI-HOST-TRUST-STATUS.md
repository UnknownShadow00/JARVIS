# AI-host identity remains PENDING

No independently trusted current public SSH fingerprint for192.168.0.200 was established. Prior sealed Gate6A/6B trusted inventories and runbooks retain the unresolved status. No new guest login, keyscan, known_hosts write, host-key bypass, Ollama metadata/model call or Proxmox operation occurred. Historical Gate4 Ollama PID3405/restart0 and VM200 facts are historical only.

Human trusted-console comparison, prepared but not executed:

1. Through the operator's authenticated Proxmox management path at192.168.0.50, identify actual VMID200 hosting node. `.50` is not assumed to host the VM. Read-only shell equivalent: `pvesh get /cluster/resources --type vm --output-format json`; inspect the VM200 entry only. On the verified node: `qm config 200`.
2. Open that VM's authenticated console. Run `hostname` and `ip -br address` and verify the guest owns192.168.0.200.
3. In the guest console: `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256`. Record public algorithm/SHA256 fingerprint only. Never read the private host key.
4. Compare against an independently obtained public-key candidate for the intended client/host/port. Any future `ssh-keyscan` is untrusted network evidence until it exactly matches the console fingerprint. Do not append it automatically or change existing pins. Enrollment is separate authority.
5. After trust approval, authorize read-only provider identity/version/model-digest and actor inventory. No generation, warmup, load/unload or restart follows from metadata approval.

Proposed pilot-window exclusivity: inventory endpoint owner, system/user units/timers, cron/scheduled model clients, interactive services, JARVIS wake/unload callers, supervisor restart policy and privileged/hypervisor actors. Obtain a named endpoint reservation covering both generation and model lifecycle, with explicit disposition of any already-possible sends. Unknown topology/actors block opening. Any pause of a job/service, firewall change or restoration requires separate explicit operations authority; none was performed. Local D06 alone cannot fence remote root or other network clients.
