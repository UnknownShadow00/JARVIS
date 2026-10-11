# Remaining external verification and future authorization

Gate5 closed-state/no-message verification is complete. The AI-host SSH branch remains UNVERIFIED. No current AI-host fingerprint, Ollama PID, restart count or global provider inactivity is asserted. This separately tracked limitation must be resolved before Gate6 readiness; no unverified remote claim is promoted to PASS.

The failed destination in the sealed prior evidence was numeric 192.168.0.200:22. Examined nexus/Core trust stores lacked a matching established key; this supports missing trust, not a proven stale/replaced/authentic host. No expected public fingerprint was found in the examined trusted inventory. No new connection, keyscan, key acceptance, trust bypass or known_hosts modification occurred here.

The human must establish a trusted console to the actual AI VM (inventory associates VMID200/ai-server/.200), verify guest identity and read only its public key fingerprint:

```sh
hostname
ip -br address
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

The .50→Core management SSH connection is not verified out-of-band AI VM console access. If ED25519 is absent, inspect the actual configured public key through that trusted console; do not guess. Compare the independently obtained fingerprint with the exact destination. Any deliberate trust-store pin requires separate operator authorization under their normal policy. Afterwards, a separately authorized read-only session can inspect Ollama ActiveState/SubState/MainPID/InvocationID/NRestarts/start time with strict verification. No model request or lifecycle operation is needed.

Gate6 prerequisites, in order:

1. Review the new Gate5 seal alongside preserved Gate4/Gate5/Gate5B evidence and acknowledge the exact closed-source/runtime/config/epoch bindings and Core-local host-loss limitation.
2. Resolve remote identity/lifecycle visibility and any remaining independent-actor limitations required for pilot readiness. Preserve the distinction between durable JARVIS zero-generation evidence and unavailable global provider visibility.
3. Separately authorize implementation and security qualification of a Core-local, single-use opening mechanism bound to approval provenance, exact runtime/source/config/profile and epoch. Current release has no opening interface. Authentication must never confer opening authority.
4. Review offline tests for replay/client refusal, cap4, lifecycle suppression, D06 active/unknown refusal, checkpoint integrity, no counter/reset/restore/generation side effect and terminal stop/drain behavior.
5. Separately approve deployment. Revalidate startup/Gate5 if source, config, invocation or epoch changes; do not silently reuse obsolete bindings.
6. Obtain explicit four-attempt conversational-only LIVE/ineligible pilot authorization before opening. No measurement, Hermes activation, model/context change or formal P7 exit follows from Gate5 completion.

No action in this task crosses that boundary. The operator should not rerun the human authentication helper or send a message to demonstrate readiness.
