# Resource identity and D06 ownership

Gate 6F isolated qualification. No production D06 change, no Ollama contact, no lifecycle action.

## New in 6F: attested topology, fail closed (`candidate_v3/topology.py`)

D06 serializes operations; it does not prove that two endpoints are physically independent. 6F adds `qualify_topology(legacy, granite, attestations, residency_approval=None)`:

| Topology | Detection | Result |
|---|---|---|
| A. Separate legacy and Granite hosts | different endpoint, service, host and GPU | `A_SEPARATE_HOSTS`, allowed |
| B. Different Ollama services, same host | same host **or** same GPU, different service | `B_SAME_HOST_SEPARATE_SERVICES`, refused unless `SHARED_HOST_SERIAL_RESIDENCY_APPROVED` |
| C. Same endpoint, different models (or alias endpoints of one service) | same endpoint or same service identity | `C_SAME_SERVICE`, refused unless approved |
| D. Unverified shared domain | any endpoint without attestation, mixed fixture/human sources, conflicting claims | **refused** (`TOPOLOGY_UNVERIFIED`, `TOPOLOGY_MIXED_SOURCE`, `TOPOLOGY_CONFLICTING_ATTESTATION`) |

The isolated application graph now refuses to build without a qualified topology (`INCOMPLETE_ISOLATED_GRAPH`). Attested `host:`, `gpu:` and `service:` domains are **added** to each binding's conflict domains, so a Granite hold on the AI host's GPU blocks a legacy call to another port on the same host before any possible-send (`test_same_host_other_port_conflicts_through_attested_domain`). Test fixtures label their attestations `OFFLINE_FIXTURE`; they say nothing about the real hosts.

Why B/C need an explicit decision: a completed request may leave its model resident for the keep-alive window (60 s proposed; `-1` = forever if the server default applies). Responder → Granite runs back-to-back, so on a shared GPU the qwen3-nothink KV cache (32k proposed, see PROVIDER-BOUNDING) can still be resident when the 30B Granite at 64k loads. That is a lifecycle conflict D06 cannot see.

## Qualification table

| Item | Status |
|---|---|
| Router / trivial / normal / Granite resource identity | Exact `(endpoint, model, profile)` binding, durable step association (TEST). Effective identity: **UNVERIFIED** |
| Endpoint/model binding | Wrong resource/substep/lease refuse before transport (6E TEST) |
| Endpoint-wide exclusion | `endpoint:` domain always held (TEST) |
| Shared host/GPU | Only via attestation (6F TEST); never inferred from IPs |
| Model residency after completion | **Not controllable** by the candidate; keep-alive is a hint only |
| Ambiguous keep-alive | Explicit value proposed; server-side policy and co-residency UNVERIFIED |
| Remote unknown after possible send | Held durably in D06 + domain ledger; drain does not clear it (TEST) |
| Cancellation/timeout | Treated as possible-send: `REMOTE_UNKNOWN`, no release, no next permit (TEST) |
| Automatic lease release on uncertainty | None (TEST) |
| Unapproved load/unload | `lifecycle()` always refuses; only `/api/chat` reachable (TEST) |
| Pre-dispatch conflicts | 6F: refused before possible-send, so counts stay truthful (TEST) |

## Not covered

External cron jobs, supervisors, the JARVIS idle unloader, other direct clients and any other V1 D06 caller are **not** excluded by candidate tests. Their inventory and a finite exclusive pilot window remain human tasks (AI-HOST-TRUST-RUNBOOK). The multi-resource D06/domain root is a same-UID prototype; production migration needs privileged provisioning.
