# Tool Readiness Inventory

Last updated: 2026-05-06

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
| Voice text/TTS route | Working | `python tasks/manual_voice_smoke.py --text "hello jarvis" --speak` | Ollama streaming response and Piper playback returned successfully. |
| Mock voice pipeline | Working | `python tasks/manual_voice_smoke.py --mock-pipeline` | Wake/STT/router/TTS call order verified without hardware. |
| browser-use | Installed, stubbed live execution | `python tasks/readiness_report.py`, `tests/test_phase8_integrations.py` | Import is available. Runtime tool returns an action plan only until live browser-agent automation is intentionally enabled. |
| python-kasa | Installed, discovery/status only | `python tasks/readiness_report.py`, `tests/test_phase8_integrations.py` | Status/discovery are Level 0. Control actions remain dry-run Level 1 semantics. |
| build123d CAD | Installed, dry-run export planning | `python tasks/readiness_report.py`, `tests/test_phase8_integrations.py` | CAD tool returns a design/export plan only. It does not slice or print. |
| FastMCP/MCP wrapper | Stubbed with whitelist | `tests/test_phase8_integrations.py` | Whitelists baseline MCP servers and rejects unknown servers. Live client calls remain deferred. |
| OBS/FFmpeg/Blender CLI harness | Stubbed readiness | `python tasks/readiness_report.py`, `python tasks/tool_readiness_smoke.py` | Reports local command availability and returns dry-run plans for execution. |

## Needs Config Or Attended Input

| Surface | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Live voice loop | Needs attended input | `python tasks/manual_voice_smoke.py --live --speak --listen-timeout 45` | Startup checks passed, but no wake/PTT audio reached the process during the attended window. PTT is now polled during the listen loop. |
| Wake-word tuning | Needs attended input | `python scripts/wake_diag.py --duration 10` | Diagnostic captured mic frames from the default input device but saw near-zero scores without a spoken wake phrase. |
| Web search | Needs dependency/network | `tests/test_web_search_tool.py` | Fetch path is implemented; search requires `ddgs` or `duckduckgo_search` and network access. |
| Vision screen analysis | Needs model/service | `tests/test_vision.py`, `tests/test_vision_vlm.py` | Screenshot capture and Ollama `/api/generate` path exist; requires configured vision model. |
| Vision webcam | Needs dependency/device | `tests/test_vision.py`, `tests/test_vision_vlm.py` | Webcam path requires OpenCV and a camera. |
| Open Interpreter | Needs dependency/config | `tests/test_interpreter_tool.py` | Level 2 bridge exists; requires `interpreter` CLI and Ollama-compatible config. |
| Voice clone sample | Intentionally skipped | `python tasks/readiness_report.py` | No real personal 10-second WAV is available while the operator is away. Chatterbox continues without conditioning and falls back to Kokoro/Piper if needed. |

## Stubbed Or Deferred

| Surface | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Open computer-use | Stubbed | `tests/test_computer_use_tool.py` | Detects missing package and returns a Phase 3 stub after dependency check. |
| Memory / Mem0 | Stubbed by default | `tests/test_memory_client.py`, `tests/test_memory_stubs.py` | Disabled unless `mem0_enabled` and package are configured. |
| RAG / ChromaDB | Stubbed by default | `tests/test_rag_client.py`, `tests/test_memory_stubs.py` | Index/query methods return stubs without ChromaDB. |
| Discord comms | Stubbed by default | `tests/test_discord_bot.py`, `tests/test_comms_stubs.py` | Requires enable flag, package/API availability, bot token, and channel ID. |
| Telegram comms | Stubbed by default | `tests/test_telegram_bot.py`, `tests/test_comms_stubs.py` | Requires enable flag, package/API availability, token, and chat ID. |
| UE5 / Audio2Face | Deferred bridge | `tests/test_ue5_bridge.py`, `tests/test_audio2face.py` | Event-building and disabled-manager behavior are covered; live bridge requires external runtime. |
| OrcaSlicer | Skipped by scope | `python tasks/readiness_report.py` | 3D printing/slicing is out of scope for this pre-5090 pass. |

## Immediate Next Gate

Run:

```powershell
python tasks\manual_voice_smoke.py --live --speak --listen-timeout 45
```

During the listen window, press and hold `ctrl+space`, speak one short request, then release. Passing this gate requires `wake_or_ptt`, `stt`, `response`, and TTS playback to complete in one run.
