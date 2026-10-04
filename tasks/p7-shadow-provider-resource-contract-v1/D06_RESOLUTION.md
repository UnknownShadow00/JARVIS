# D06 resolution matrix

| Component | Status | Evidence / gap |
|---|---|---|
| Provider/runtime/endpoint choice | OPERATOR APPROVED; installed listener verified | Local Ollama 192.168.0.27:11434 |
| Candidate alias / quantization | VERIFIED | Exact manifest/model blob; Granite 28.9B marketed 30B, Q3_K_M |
| Context ceiling | VERIFIED | Parameter blob num_ctx=64000 |
| Hardware / RAM ceiling | OBSERVED / APPROVED | RTX 5090 32607 MiB; no >32 GB design authorized |
| Concurrent shadow generations | OPERATOR APPROVED | One; scheduler enforcement missing |
| Fallback / trust / failure policy | OPERATOR APPROVED | None; untrusted output; legacy unchanged |
| Shared model ownership / unload coordination | OPERATOR DECISION REQUIRED | 13B11A §§11,21; current unload union persists |
| Runtime globally inactive | ACCEPTANCE NOT MET | Core zero; AI existing idle daemon PID 1370, runner zero |
| Core-only network enforcement | ACTIVATION PROOF REQUIRED | LAN bind verified; ACL not proven or changed |
| Provider wire normalization / prompt sources | IMPLEMENTATION CONTRACT MISSING | D05 handoff; no native provider→recorded mapping exists |
| Evidence identity collection | CONTROLLER CONTRACT MISSING | No D03/D04 schema amendment |

Verdict: JARVIS P7 SHADOW PROVIDER RESOURCE CONTRACT BLOCKED. Approved selections remain recorded; no full resource-ownership freeze. D07 NOT RUN under the explicit Unit B entry rule.
