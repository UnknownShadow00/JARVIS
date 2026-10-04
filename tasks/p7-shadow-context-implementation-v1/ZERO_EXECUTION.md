# Runtime forbidden-event proof

The frozen corpus guards owner construction, issuance and passive reload with a call-profile sentinel that rejects every app module outside context/correlation/provenance/types. It patches actual P2 mutation APIs, socket creation/connect and subprocess startup. HTTP/provider module calls also fail before execution. Allowed passive fixture imports/setup occur before the guard.

`runtime-sentinels.json` reports registry.call=0; dispatcher=0; executor=0; real tool handlers=0; model/provider=0; Ollama inference=0; confirmation mutation=0; trusted provenance writes=0; operational audit emission=0; server/API/UI calls=0; external I/O=0. `zero-write-proof.json` independently allows real allocation while failing every mutation surface; `snapshot-forbidden-events.json` covers the structured later-snapshot proof.

No network/model/AI service operation is part of implementation or its runtime tests. SSH for authorized Core source/evidence/Git maintenance is separate from the passive execution boundary. Baseline/full pytest use their established isolated mocks. Deterministic golden traps registry.call and HTTP/provider calls and disables trace persistence. No live shadow, provider, model runner, process scheduling or operational audit emission is introduced.
