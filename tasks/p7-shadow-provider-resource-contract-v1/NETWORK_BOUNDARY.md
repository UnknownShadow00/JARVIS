# Existing private network boundary

Future model transport is Core 192.168.0.162 → 192.168.0.27:11434 only. ss -ltn shows the local bound address 192.168.0.27:11434, not a wildcard local listener. The peer-column 0.0.0.0:* is not a public local bind. No browser/UI → AI edge is authorized.

Do not infer that LAN binding enforces Core-only access. No firewall/ACL enforcement was proven or modified. Existing planned Core→AI restriction remains an activation prerequisite. No public ingress, proxy, additional interface, network test to Ollama or network configuration change. SSH inventory is the only cross-host activity in this review.
