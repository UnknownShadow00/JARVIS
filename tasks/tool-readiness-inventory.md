# Tool Readiness Inventory

Last updated: 2026-05-30

## Working

| Surface | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Browser | Working | `tests/test_browser_tool.py`, router coverage | Opens URLs/searches through the default browser; Level 1 gated and dry-run aware. |
| Files | Working | `tests/test_files_tool.py` | Read/list/search/move within allowed roots; no delete action. |
| Calendar | Working | `tests/test_calendar_tool.py` | Reads local `.ics` files when present; returns empty result when none are available. |
| Screenshot | Working | `tests/test_screenshot.py`, `tests/test_screenshot_tool.py` | Uses `mss`; returns dependency error if package is missing. |
| System stats | Working | `tests/test_system_stats_tool.py` | CPU/RAM/disk works through `psutil`; GPU is optional through `GPUtil`. |
| Shell | Working with confirmation | `tests/test_shell_tool.py` | Level 2 gated, root-bound, timeout-limited, and blocks hard-denied command patterns. |
| Apps | Working for allowlisted apps | `tests/test_apps_tool.py` | Launch/close support is limited to the hardcoded friendly-name map. |
| Mouse/keyboard | Working with confirmation | `tests/test_mouse_keyboard.py`, `tests/test_phase3_integration.py` | PyAutoGUI-backed Level 2 control with failsafe enabled. |
| Voice text/TTS route | Working | `python tasks/manual_voice_smoke.py --text "hello jarvis" --speak` | Ollama streaming response and Piper playback returned successfully in the last attended pass. |
| Mock voice pipeline | Working | `python tasks/manual_voice_smoke.py --mock-pipeline` | Wake/STT/router/TTS call order verified without hardware. |
| Dictation mode | Working, hardware-gated | `tests/test_dictation.py` | Separate hotkey path routes STT transcripts to clipboard and optional type-out without brain, LLM, or TTS. |
| Obsidian vault tool | Working | `tests/test_obsidian_tool.py` | Constrained note create/append/read/search stays inside `jarvis-vault/`; optional MCP handoff remains stubbed. |
| Embedding tool selector | Working, disabled by default | `tests/test_tool_embeddings.py` | Feature-flagged second-pass tool selection uses Ollama embeddings when `routing.embedding_enabled=true`. |
| python-kasa | Installed, discovery/status only | `python tasks/readiness_report.py`, `tests/test_phase8_integrations.py` | Status/discovery are Level 0. Control actions remain dry-run Level 1 semantics until devices are selected. |
| build123d CAD | Installed, dry-run export planning | `python tasks/readiness_report.py`, `tests/test_phase8_integrations.py` | CAD tool returns a design/export plan only. It does not slice or print. |
| OBS/FFmpeg/Blender CLI harness | Stubbed readiness | `python tasks/readiness_report.py`, `python tasks/tool_readiness_smoke.py` | Reports local command availability and returns dry-run plans for execution. |

## Needs Config Or Attended Input

| Surface | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Live voice loop | Needs attended input | `python tasks/manual_voice_smoke.py --live --speak --listen-timeout 45` | Passing requires wake/PTT, STT, response, TTS playback, and kill-switch in one real microphone/speaker run. |
| Wake-word tuning | Needs attended input | `python scripts/wake_diag.py --duration 10` | Diagnostic captures mic frames; meaningful tuning requires spoken wake phrases in the target room. |
| Web search | Needs network | `tests/test_web_search_tool.py` | Fetch path is implemented; live search still depends on network and DuckDuckGo availability. |
| Vision screen analysis | Needs model/service | `tests/test_vision.py`, `tests/test_vision_vlm.py` | Screenshot capture and Ollama `/api/generate` path exist; requires configured vision model. |
| Vision webcam | Needs dependency/device | `tests/test_vision.py`, `tests/test_vision_vlm.py` | Webcam path requires OpenCV, a camera, and the configured vision model. |
| Graphiti temporal memory | Implemented, disabled by default | `tests/test_graphiti_client.py`, `docs/graphiti_setup.md` | Requires Docker/Neo4j, `NEO4J_PASSWORD`, `graphiti-core`, and `memory.graphiti_enabled=true` before live use. |
| ChromaDB RAG | Implemented, disabled by default | `tests/test_rag_client.py`, `tests/test_phase8_integrations.py` | Requires `chromadb`, configured index paths, and `memory.chromadb_enabled=true`. |
| Voice clone sample | Intentionally skipped | `python tasks/readiness_report.py` | No real personal 10-second WAV is configured. Chatterbox continues without conditioning and falls back to Kokoro/Piper if needed. |

## Stubbed Or Deferred

| Surface | Status | Evidence | Notes |
| --- | --- | --- | --- |
| browser-use live execution | Plan-only stub | `python tasks/readiness_report.py`, `tests/test_phase8_integrations.py` | Package import is available, but runtime tool returns an action plan until live browser-agent automation is intentionally enabled. |
| FastMCP/MCP wrapper | Stubbed with whitelist | `tests/test_phase8_integrations.py` | Whitelists baseline MCP servers and rejects unknown servers. Live client calls remain deferred. |
| Open computer-use | Stubbed | `tests/test_computer_use_tool.py` | Detects missing package and returns a Phase 3 stub after dependency check. |
| Mem0 long-term memory | Stubbed by default | `tests/test_memory_client.py`, `tests/test_memory_stubs.py` | Disabled unless `memory.mem0_enabled` and the package/service are configured. |
| Discord comms | Stubbed by default | `tests/test_discord_bot.py`, `tests/test_comms_stubs.py` | Requires enable flag, package/API availability, bot token, channel ID, and approval flow. |
| Telegram comms | Stubbed by default | `tests/test_telegram_bot.py`, `tests/test_comms_stubs.py` | Requires enable flag, package/API availability, token, chat ID, and approval flow. |
| UE5 / Audio2Face | Deferred bridge | `tests/test_ue5_bridge.py`, `tests/test_audio2face.py` | Event-building and disabled-manager behavior are covered; live bridge requires external runtime. |
| OrcaSlicer | Skipped by scope | `python tasks/readiness_report.py` | 3D printing/slicing is out of scope for this pre-Proxmox pass. |

## Immediate Next Gates

Run the automated local gate:

```powershell
python tasks/pre_server_readiness.py
```

Run the attended voice gate:

```powershell
python tasks/manual_voice_smoke.py --live --speak --listen-timeout 45
```

During the listen window, press and hold `ctrl+space`, speak one short request, then release. Passing this gate requires `wake_or_ptt`, `stt`, `response`, and TTS playback to complete in one run.
