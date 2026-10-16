# Exact operator decisions still needed

Ordered; each is a distinct authority. None is inferred from this packet.

0. **NEW — V2 production state.** V2 has been stopped since the 2026-10-15T03:42:17Z host power-off; its epoch is `CLOSED_COMPLETE` with an unattributed `OPERATOR_STOP` and zero use. Decide: (a) leave V2 stopped as the retirement candidate (then step 4 below can use the current closed epoch), or (b) authorize a separate V2 restart gate. Restart behaviour against the existing controller is not neutral (pilot start refuses `PILOT_EPOCH_ALREADY_EXISTS`) and must be qualified first. Also identify the source of the power-button event.
1. **Experiment contract** — X1–X11 in EXPLICIT-EXPERIMENT-DECISION, notably X3 (pinned memory), X4 (`num_ctx` 8192 proposal), X6 (keep-alive) and X10 (topology).
2. **Independent identity** — AI-HOST-TRUST-RUNBOOK and LEGACY-IDENTITY-ATTESTATION-DESIGN by the operator: VM 200 placement, host-key fingerprint from console vs network, Ollama version/models/Modelfile digests, effective legacy endpoint, server keep-alive/context policy, external actor inventory, pilot window. Separate approval for SSH enrollment.
3. **OS/privilege design and disposable qualification** — approve the identity/mode contract and the disposable-VM test plan (OS-IDENTITY-QUALIFICATION), and the protected high-water authority (PROTECTED-LINEAGE). Then separately authorize actual provisioning.
4. **V2 zero-use retirement and one V3 successor** — signed payload acknowledging the unattributed stop.
5. **V3 installation** with exact source/config/provider identities, then a **new Gate 5** for V3.
6. **Pilot opening** and per-attempt permits, only after 1–5. Real provider traffic and measurement remain unauthorized now.
