# JARVIS V2 Target-Host Readiness

## Current status

Phase 2 uses loopback as the pre-Hermes network boundary. Services remain reachable only from the machine that runs them unless an operator explicitly enables the existing authenticated remote mode.

```text
Software/deterministic baseline: COMPLETE
Target hardware live baseline: PENDING
```

The current KVM guest is **not approved for Hermes inference**. Its observed allocation is 4 vCPU, 7.3 GiB RAM, no NVIDIA GPU, no Ollama or configured models, no usable audio devices, no Plex, and about 1.8 GiB free on a 97%-used root filesystem. Do not install Hermes, Ollama models, Chatterbox models, or large STT models here unless an explicit infrastructure decision replaces this constraint.

## Phase 2 network boundary

Default listeners and client targets are:

| Service or client | Port | Default boundary | Classification | Notes |
| --- | ---: | --- | --- | --- |
| Native FastAPI HTTP/WebSocket (`/ws`, `/ue5`) | 8000 | `127.0.0.1` | HOST-LOCAL | `/ue5` is disabled by default and shares the FastAPI listener. |
| Containerized FastAPI | 8000 | Container `0.0.0.0`; host `127.0.0.1:8000` | HOST-LOCAL | The all-interface bind exists only inside the isolated container namespace. |
| Containerized Ollama | 11434 | Host `127.0.0.1:11434` | HOST-LOCAL | JARVIS containers use the internal service name; the host publication remains loopback-only. |
| Neo4j browser | 7474 | Host `127.0.0.1:7474` | HOST-LOCAL | Retained for local administration; not exposed to the LAN. |
| Neo4j Bolt | 7687 | Host `127.0.0.1:7687` | HOST-LOCAL | Local Graphiti configuration uses `bolt://localhost:7687`. |
| Mem0 example | 8001 | Disabled; loopback mapping shown | FUTURE-REMOTE | Do not activate before its phase and authentication review. |
| ChromaDB example | 8002 | Disabled; loopback mapping shown | HOST-LOCAL | Container-internal access may replace publication later; no redesign is needed in Phase 2. |
| PWA | None | `ws://localhost:8000/ws` | HOST-LOCAL CLIENT | Server URL is user-configurable, but its default is local and it stores no credential. |
| Electron HUD | None | `ws://localhost:8000/ws` | HOST-LOCAL CLIENT | Native WebSocket client; it sends no browser Origin header. |
| Hologram HUD | None | `ws://localhost:8000/ws` | HOST-LOCAL CLIENT | Browser Origin remains subject to the server allowlist. |
| Sensor node | None | `http://127.0.0.1:8000` | HOST-LOCAL CLIENT | A remote destination requires an explicit `JARVIS_URL` override. |
| Ollama client | None | `http://localhost:11434` | HOST-LOCAL CLIENT | No repository default sets public `OLLAMA_HOST`. |
| Audio2Face bridge | None | No default; caller supplies URL | FUTURE-REMOTE CLIENT | It creates an outbound connection and no listener. |
| Tailscale helper | None | Disabled/unavailable unless separately installed | FUTURE-REMOTE | Phase 2 does not install or configure Tailscale. |
| MCP wrapper/stubs | None | No server listener | FUTURE-REMOTE | MCP is not activated in this phase. |

`EXPOSE 8000` in the Dockerfile is image metadata; it does not publish a host port. Compose is the publishing boundary and all active host mappings explicitly use `127.0.0.1`.

### Browser policy

Default CORS origins are local development origins only. Wildcard CORS is rejected. When `remote_access_enabled` is false, non-loopback CORS origins are rejected during configuration loading.

WebSocket policy remains:

- explicitly trusted local browser Origin: accepted;
- untrusted browser Origin: rejected with policy violation;
- missing Origin: accepted intentionally for native/non-browser clients;
- bearer authentication: unchanged when an API token is configured;
- query-string token authentication: rejected.

The PWA stores its server URL and non-sensitive UI preferences in browser storage. It does not store an API credential or add credentials to WebSocket URLs.

## Loopback is not the final security architecture

Loopback is the Phase 2 containment boundary, not a multi-device authentication system. Before phone or remote access, Phase 11 must add device identities, authenticated sessions, scoped authority, requester-bound approvals, nonces, expiry, revocation, and Tailscale transport. Do not solve those concerns by exposing an unauthenticated loopback-era service.

## Target-host readiness checklist

All required items must be checked on the machine selected for the pinned Hermes proof.

### Required

- [ ] The Windows target host is identified and approved for inference.
- [ ] The JARVIS repository is present, clean, and current.
- [ ] The protected rollback tag and Restic recovery path are known and accessible.
- [ ] Free SSD capacity has been measured and passes the disk-space gate below.
- [ ] An NVIDIA GPU is detected if GPU inference is expected.
- [ ] The NVIDIA driver is healthy and reports the expected GPU and VRAM.
- [ ] Ollama is installed without being upgraded as part of measurement.
- [ ] Configured baseline models are installed, or an explicit baseline-model decision is documented.
- [ ] Ollama is local-only for the first proof.
- [ ] Microphone input is visible to the current JARVIS runtime.
- [ ] Speaker/audio output is visible to the current JARVIS runtime.
- [ ] Existing pre-Hermes JARVIS starts and serves `/health` on loopback.
- [ ] Chatterbox package/model/cache requirements are feasible on the selected GPU and disk.
- [ ] Plex installation, running state, and coexistence relevance are known.
- [ ] Required localhost ports are free or conflicts have an approved resolution.
- [ ] No JARVIS, Ollama, Neo4j, Hermes, or supporting port is unexpectedly LAN/public-bound.

### Capture before Hermes installation

- [ ] OS, kernel/build, CPU, logical/physical cores, and total RAM.
- [ ] GPU, driver, CUDA capability where relevant, total VRAM, and idle VRAM.
- [ ] Filesystem layout and free disk space.
- [ ] Python, Node/npm, and Ollama versions.
- [ ] Installed Ollama model names and sizes.
- [ ] Configured main, thinking, router, vision, STT, and TTS models/providers.
- [ ] Input/output audio devices.
- [ ] Plex state and whether an active transcode can be observed safely.
- [ ] Current listeners using `ss`, `netstat`, or the Windows equivalent.

## Disk-space gate

Do not install Hermes or model payloads on a host without adequate working headroom. There is no universal fixed gigabyte threshold: calculate the requirement for the exact planned installation before changing the host.

The calculation must include:

1. Hermes checkout/install and its Python environment;
2. each planned Ollama model at its actual local size;
3. the configured STT model;
4. Chatterbox model/cache and any voice conditioning assets;
5. temporary download and extraction space;
6. logs, traces, package caches, and normal operational growth;
7. a meaningful safety margin so updates and rollback do not fill the disk.

Record the estimate and measured free space. If the safety margin is not clearly positive, stop before installation. The approximately 1.8 GiB free on the current KVM guest fails this gate without further calculation.

## Mandatory target-hardware baseline gate

Before accepting any Phase 3 Hermes comparison, repeat the missing Task 7 work on the selected target host:

- three live 20-case golden runs;
- request, router/planner, LLM, and response latency;
- CPU, RAM, GPU, VRAM, thermal, and headroom measurements;
- STT latency and accuracy with labeled or attended samples;
- TTS synthesis and first-audio latency;
- wake/voice pipeline timing where safely possible;
- Plex coexistence baseline where relevant;
- one live tool/safety request with matching trace and audit `trace_id`.

This baseline must be recorded before Hermes can change model/runtime behavior. Unsupported calendar/habit features and the eight existing deterministic failures remain comparison evidence, not Phase 2 defects.

## First Hermes proof boundary

For an initial proof running natively on the same Windows host, use:

```text
Hermes -> localhost Ollama
```

If a later WSL2 or container topology cannot use loopback directly, stop and document the trusted private path before changing bind addresses. Do not use `0.0.0.0` as a convenience workaround.
