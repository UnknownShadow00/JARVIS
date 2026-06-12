# JARVIS - Repository Verdicts

Last reviewed: 2026-05-30

## Add Or Keep Integrated

| Repo | Purpose | Current JARVIS decision |
| --- | --- | --- |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | Browser automation for AI agents on top of browser tooling. | Keep installed/import-checked, but leave JARVIS live execution plan-only until explicit confirmation-gated browser automation is enabled. |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Official Playwright MCP server for browser automation through MCP. | Best next MCP browser experiment; do not replace the simpler built-in browser tool. |
| [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | Official Python SDK for MCP servers and clients, including FastMCP. | Use for future live MCP client/server work; current wrapper stays whitelisted and stubbed. |
| [getzep/graphiti](https://github.com/getzep/graphiti) | Temporal knowledge graph engine for agent memory. | Implemented behind `memory.graphiti_enabled`; enable only after live Neo4j/Docker validation. |
| [chroma-core/chroma](https://github.com/chroma-core/chroma) | Local search/vector/RAG infrastructure. | Use for document/project RAG when `memory.chromadb_enabled=true`; keep separate from Graphiti temporal memory. |
| [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox) | Voice clone / expressive TTS path. | Optional later; needs a real private voice sample before enabling conditioning. |
| [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | Lightweight local TTS fallback. | Optional fallback path; do not prioritize over current Piper validation. |

## Reference For Later

| Repo | When to use |
| --- | --- |
| [livekit/agents](https://github.com/livekit/agents) | Reference only if the current local voice pipeline needs a larger WebRTC/realtime-agent rearchitecture. |
| [open-webui/open-webui](https://github.com/open-webui/open-webui) | Reference or run separately if a full local LLM chat UI is wanted; not needed inside the current FastAPI/PWA/Electron stack. |
| [OpenJarvis/openjarvis](https://github.com/OpenJarvis/openjarvis) | Consider only after enough real JARVIS traces exist to justify optimizer work. |
| Home Assistant AI repos | Relevant only if Home Assistant becomes the primary smart-home layer. |
| Steel Browser / hosted browser services | Fallback only if local browser-use or Playwright MCP cannot satisfy browser automation needs. |

## Defer Until Proxmox Or Credentials

| Tool family | Reason |
| --- | --- |
| Hermes / mission-control style multi-agent dashboards | Useful for always-on autonomous work, but the current project can finish local assistant gates before adding another orchestration surface. |
| Discord and Telegram live sending | Requires real tokens, channel IDs, and remote approval policy. |
| UE5 / Audio2Face / hologram runtimes | External cinematic stack; keep bridge tests but defer live wiring. |
| Docker GPU validation | Needs Docker/NVIDIA runtime on the target host. |

## Skip

| Repo | Reason |
| --- | --- |
| Open Interpreter / open computer-use style broad GUI control | High-risk overlap with existing gated shell, browser, mouse/keyboard, and screenshot tools. Keep explicit stubs until a narrow safe use case exists. |
| Toy JARVIS assistant repos | Most duplicate current Phase 0-3 behavior without the local-first safety and test coverage already present here. |
| OrcaSlicer integration | 3D printing/slicing is out of scope for this pre-Proxmox pass. |
