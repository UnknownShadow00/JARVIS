# Resource and identity threats

| Threat | Required defense / current result |
|---|---|
| Alias silently replaced | Pin/reverify manifest, config, parameter and model blob hashes; current identity verified |
| Shared legacy unload or concurrent load | Exact owner/in-flight policy required; BLOCKED, do not alter resource manager |
| Model OOM escalates authority | Shadow failure only; no tools, restart policy or fallback |
| Model-selected tool treated as approval | Preserve canonical adapter/P3/P4 separation |
| Browser reaches model directly | Core-owned edge only; actual network restriction proof still required |
| Timeout releases cap while remote call continues | Future scheduler must prove end of generation before reuse |
| D03 fields overloaded with model identity | Separate D05 evidence/controller join |
| Idle daemon called disabled | Report service PID separately from runner and session-call counts |
| Memory cap bypass | No plan requiring >32 GB system RAM; no VM/GPU change |
| Raw prompts collected during inventory | Only public model/config/OS facts collected; no provider request |

No security authority is inferred from successful SSH access or from an installed alias.
