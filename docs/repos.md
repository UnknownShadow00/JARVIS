# JARVIS — Repository Verdicts

## ADD (integrate directly)

| Repo | Stars | Purpose | Install |
|------|-------|---------|---------|
| NousResearch/hermes-agent | 23k+ | Self-improving Kanban multi-agent board, 19 platforms, Curator, MCP, cron | WSL2: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh \| bash` |
| NousResearch/hermes-labyrinth | — | Observability plugin for Hermes — always install alongside Hermes | `git clone ... ~/.hermes/plugins/hermes-labyrinth` |
| builderz-labs/mission-control | 4.8k | Self-hosted agent orchestration dashboard, SQLite, 26 panels, real-time WebSocket. **Replaces hermes-workspace as primary Hermes UI** | `git clone`, `pnpm install`, `pnpm dev` |
| wondelai/skills | 750+ | Cross-platform skill library, MIT license. Install into Hermes after it is running | `git clone ... ~/.hermes/skills/wondelai && hermes skills reload` |
| resemble-ai/chatterbox | — | Chatterbox Turbo TTS — voice clone + paralinguistic tags, CUDA | `pip install chatterbox-tts` |
| hexgrad/kokoro | — | Kokoro-82M fallback TTS, Apache 2.0, CUDA | `pip install kokoro` |
| browser-use/desktop | — | Full Chrome agent with real cookies/sessions (Level 1 tool) | `pip install browser-use` |
| anthropics/cli-anything-hub | — | JSON-output CLI harnesses for OBS, FFmpeg, Blender | `pip install cli-anything-hub` |
| modelcontextprotocol/python-sdk (FastMCP) | — | MCP client wrapper for Playwright, GitHub, Obsidian, HA | `pip install fastmcp` |
| microsoft/playwright-mcp | — | Accessibility-tree browser automation via MCP | `npx @playwright/mcp` |
| OpenJarvis/openjarvis | — | Stanford SAIL skill optimizer — trace logging already wired, audit.jsonl compatible | Phase 4+ only; activate after 500 real interactions |
| graphiti-core | — | Temporal knowledge graph — `pip install graphiti-core` + Neo4j | Phase 4+ only |
| nazirlouis/ada_v2 | — | Workshop tool patterns — CAD + smart home patterns cherry-picked into cad.py / kasa.py | Patterns absorbed; do not import directly |

## STUDY (cherry-pick patterns only — do not clone wholesale)

| Repo | Why |
|------|-----|
| ethanplusai/jarvis | Request routing patterns, intent classification examples |
| huwprosser/jarvis-mlx | STT/TTS pipeline architecture for Apple Silicon (reference only) |
| unreal-audio2lipsync | Audio2Face-3D lip sync timing patterns |
| voicebox | Streaming TTS buffer management |
| kanban-video-pipeline | Hermes Kanban multi-agent workflow patterns |

## REFERENCE (bookmark for later — do not install yet)

| Repo / URL | When to use |
|------------|-------------|
| awesome-hermes-agent | Community plugin catalog and Hermes ecosystem index |
| homeassistant-ai | Home Assistant AI integration — relevant if HA is ever added |
| obsidian-memory-mcp | Obsidian vault MCP server — Phase 4+ when Obsidian vault is active |
| steel-browser | Alternative headless browser if browser-use has issues |
| agentskills.io | OpenClaw community skill catalog — 13,700+ skills, compatible with audit.jsonl format |
| livekit/agents | Real-time audio agent framework — relevant if voice pipeline needs rearchitecting |
| open-webui | Local LLM UI — reference if a web chat frontend is ever needed |
| NousResearch/hermes-agent-self-evolution | ICLR 2026 oral — evolutionary self-improvement for Hermes skills via DSPy + GEPA. **Replaces the OpenJarvis skill optimization role** after 500 interactions |

## SKIP (with reasons)

| Repo | Reason |
|------|--------|
| boop-agent | Unmaintained, no Ollama support, duplicates what Hermes already does |
| mercury-agent | Commercial/closed trajectory, not self-hostable cleanly |
| AnubhavChaturvedi/jarvis-ai-assistant | Toy project, no multi-agent or local-first architecture, no skill optimizer |
| hermes-workspace | Superseded by mission-control — richer dashboard, better WebSocket, SQLite backend |
