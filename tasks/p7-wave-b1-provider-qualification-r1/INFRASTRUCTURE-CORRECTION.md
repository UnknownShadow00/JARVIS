# Current B1-R1 infrastructure authority

Date/task: 2026-10-08, P7 Wave B1-R1 provider qualification recovery.
Source: operator-supplied Proxmox verification and guest/Core preflight in the
task authorization. These facts supersede historical D06/B1 endpoint and memory
claims for current qualification. They are not fresh measurements by this session.

| Fact | Old fact, retired for current qualification | New verified fact | Security effect |
|---|---|---|---|
| AI endpoint | 192.168.0.27:11434 | 192.168.0.200:11434 | Exact target only; no fallback or redirects to another target. |
| Memory | 32 GB hard RAM cap | **24 GiB FIXED VM ALLOCATION; NO BALLOONING** | Qualification must fit the actual allocation; no RAM, swap, ballooning, quantization or context changes. |
| Runtime version | Historical D06 installed-file 0.31.2 observation | Operator verified Ollama 0.35.1 | Qualification must establish this exact native profile; old observations do not qualify the new runtime. |

Proxmox proof summary: VMID 200, name AI-VM, hostname ai-server;
`memory: 24576` MiB; `balloon: 0`; runtime `maxmem: 25769803776` bytes.
24576 MiB and 25769803776 bytes both equal 24 GiB. Guest Linux's approximately
22 GiB usable total is not a different hypervisor allocation. Proxmox must not
be modified or reconfigured.

Operator preflight: approximately 21–23 GiB available at idle, essentially unused
swap; NVIDIA GeForce RTX 5090, driver 580.178.04, 32607 MiB total VRAM,
0 MiB used, no GPU processes. Ollama 0.35.1 listens at the new endpoint;
`/api/ps` returned `{"models":[]}`. Core 192.168.0.162 reached AI directly
through ens18, with zero ping loss and a successful version request.

Candidate remains `hermes-candidate-granite41-30b-q3km-64k`, underlying
Granite 4.1 30B Q3_K_M, configured context **64000**. Immediately before Q01,
fresh guest memory/GPU/runner and exact candidate identity checks are required.
A mismatch blocks calls; it does not authorize model recreation or pulling.

Historical documents under `tasks/p7-shadow-provider-resource-contract-v1/`
and their sealed canonical evidence remain records of their original review.
Their old endpoint/RAM observations have no current qualification authority.
The previous blocked B1 bundle must remain byte-for-byte unchanged.

Production remains `execution.mode=legacy`. B1 qualification requires neither
a production Bearer credential nor operational backup activation. All temporary
qualification evidence must be privately preserved and sealed. B2 authentication
readiness: **NO**. Measurement backup readiness: **NO**, pending a separate
operational decision or adequate existing read-only proof. No credentials or
backup automation may be changed in this task.

Every real qualification attempt must be LIVE and measurement-ineligible for
its entire lifetime. No generation is authorized until the accounting fix,
persistence/recovery, attack tests, and focused regressions pass and the focused
accounting commit exists. Measurement and B2 activation remain forbidden.
