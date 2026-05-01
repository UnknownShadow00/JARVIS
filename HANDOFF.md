# JARVIS — Session Handoff
> Generated: 2026-04-30. Use this to resume in a new Claude Code session or pass to Codex.

---

## Current State: Phase 0 COMPLETE (7/8)

Phase 0 (Core Brain) is fully built and tested. One item remains before moving to Phase 1.

### Task Checklist

| Task | Status | Notes |
|------|--------|-------|
| 0.1 Config + Pydantic validation | DONE | `app/config.py` — loads `config.yaml`, exposes `settings` singleton |
| 0.2 Audit logger | DONE | `app/logs/audit.py` — queue-backed JSONL, thread-safe |
| 0.3 LLM client | DONE | `app/brain/llm_client.py` — httpx direct REST, `think:false` enforced |
| 0.4 Intent router | DONE | `app/brain/router.py` — gemma3:4b, 5 intents, 20/20 test pass |
| 0.5 Tool registry + 4 tools | DONE | `app/tools/registry.py` + system_stats, web_search, apps, files |
| 0.6 Kill switch + response cleaner | DONE | `app/brain/kill_switch.py`, `app/brain/response_cleaner.py` |
| 0.6b FastAPI server | DONE | `app/server.py` — /health, /chat POST, /ws WebSocket, 4/4 pipeline PASS |
| **0.7 GitHub push** | **NEXT** | Public repo, README, one-command setup — Phase 0 final gate |
| Phase 1 | NOT STARTED | Voice + Boot (wake word, STT, TTS, streaming, morning report) |

---

## All Files Created

```
app/
  config.py                  Pydantic v2 BaseSettings — loads config.yaml, exposes settings singleton
  main.py                    Uvicorn entrypoint — re-exports app from server.py
  server.py                  FastAPI — /health GET, /chat POST, /ws WebSocket, CORS, kill switch hook

  brain/
    llm_client.py            httpx direct REST to Ollama — think:false, num_predict=120, no ollama SDK
    router.py                gemma3:4b intent classifier — RouterResult dataclass, audit on every call
    prompts.py               JARVIS system prompt + build_prompt() — 4 few-shot examples, ~595 tokens
    kill_switch.py           Ctrl+Alt+J hotkey + voice trigger set — idempotent trigger(), sys.exit(0)
    response_cleaner.py      clean() strips markdown + banned openers, truncates to 2 sentences
                             dry_run_narration() returns verbal narration string for dry-run mode

  logs/
    audit.py                 JSONL audit log — queue-backed async writer, thread-safe

  tools/
    registry.py              Auto-discovers tools via pkgutil — safety gating L0-L3, dry_run enforcement
    system_stats.py          SAFETY_LEVEL=0 — psutil CPU/RAM/disk, GPUtil for GPU (optional)
    web_search.py            SAFETY_LEVEL=0 — ddgs package (duckduckgo); fallback to duckduckgo_search
    apps.py                  SAFETY_LEVEL=0 — _APP_MAP dict, subprocess.Popen
    files.py                 SAFETY_LEVEL=1 — list/read (32KB cap)/move; NO delete

tests/
  pipeline_test.py           4/4 PASS — respond, use_tool(dry_run), retrieve_memory, confirm_action
  router_test.py             20/20 PASS — all 5 intents, timing logged, MAX_MS=40000
  ollama_test.py             PASS — basic Ollama connectivity check

config.yaml                  Project root — all models/safety/voice/server config here (never hardcode)
requirements.txt             Python deps
```

---

## Key Config Decisions

### LLM Client — CRITICAL BUG FIX THIS SESSION
The ollama Python `AsyncClient` silently ignores `think=False` for qwen3 models, causing
unbounded hidden reasoning tokens. Observed: 350–500s per call. Fix: replaced with direct
httpx POST to `{ollama_base_url}/api/chat` with `"think": false` in the JSON body.
Result: 7.6s per call. **Never revert to the ollama Python SDK for chat calls.**

`_suppress_thinking()` also injects `/no_think` into the last user message for qwen3 models
as defense-in-depth, but the httpx fix is the actual solution.

### think=False
Enforced at two levels:
1. httpx JSON body: `"think": false`
2. `/no_think` prefix injected into last user message for any model starting with `qwen3`

### num_predict cap
`"options": {"num_predict": 120}` on every LLM call. JARVIS responses are always 1–2
sentences — no reason to generate more. Prevents runaway output.

### dry_run
`config.yaml → safety.dry_run` — currently `false` in config (was `true` during testing).
When `true`: tool calls narrate instead of execute, pipeline still audits.
All tools MUST check `settings.safety.dry_run` before executing. Registry enforces this.

### Intent Classes (5, exact)
```
respond          — just answer, no tools needed
use_tool         — needs a tool (suggested_tool field populated)
retrieve_memory  — needs memory lookup before responding
vision           — needs screen capture or webcam
confirm_action   — high-risk action, always gate on user confirmation
```
Confidence threshold: 0.75 (from `settings.safety.confidence_threshold`).
If confidence < 0.75, intent overrides to `confirm_action` regardless of classification.

### Safety Levels (enforce in all tool code)
```
L0 — Safe       Never confirm    answer question, open app, web search, system stats
L1 — Reversible Low-conf only    move file, open URL, git status, start server
L2 — Risky      Always confirm   delete files, send messages, install packages, git commit
L3 — Blocked    Never automatic  spend money, delete projects, admin scripts, private data
```
L3 is always blocked. L2 requires `confirmed=True` passed to `registry.call()`.

### Banned Phrases (enforce in prompts.py and response_cleaner.py)
```
Absolutely / Great question / I'd be happy to / Of course
How can I help / Is there anything else / I apologize
Never start a sentence with "I"
```
`response_cleaner.clean()` strips these from LLM output before returning to user.

### Action Tag Format (universal — no exceptions)
```
[ACTION:BROWSER:https://...]
[ACTION:APP:vscode]
[ACTION:FILE:read:/path]
[ACTION:SHELL:npm run dev]
[ACTION:MESSAGE:discord:text]
[ACTION:VISION:screen]
[ACTION:HERMES:task:params]
[EMOTION:neutral|success|concern|thinking]
```

### JARVIS Personality (non-negotiable)
- Always "sir"
- 1 sentence ideal, 2 max, never 3
- No markdown/bullets/code blocks in voice output
- Never break character, never say "as an AI"
- Lead with action/outcome, never self-reference

---

## Model Assignments

| Role | Model | Notes |
|------|-------|-------|
| Main brain | `qwen3:14b` | 4070 Ti fallback. Upgrade to `qwen3:32b` when 5090 arrives |
| Coder | `qwen2.5-coder:14b` | Same — upgrade to `qwen2.5-coder:32b` with 5090 |
| Intent router | `gemma3:4b` | Fast classifier only — never use for generation |
| Vision | `qwen3-vl` | Phase 4+. Requires Ollama 0.21.0+. Name is `qwen3-vl` NOT `qwen3.5-vl` |
| Ollama endpoint | `http://localhost:11434` | All models via Ollama |

---

## Ollama Environment Variables

Set this session (requires admin PowerShell + Ollama restart to take effect):

```powershell
setx OLLAMA_NUM_PARALLEL 1 /M       # single user, sequential — no wasted KV slots
setx OLLAMA_NUM_THREADS 2 /M        # minimal CPU threads; GPU does the work
setx OLLAMA_FLASH_ATTENTION 1 /M    # reduces VRAM during attention, CUDA-safe on Windows
setx OLLAMA_KV_CACHE_TYPE q8_0 /M   # half VRAM vs fp16; verify var name for 0.21.0
setx OLLAMA_KEEP_ALIVE -1 /M        # never unload models — critical to avoid cold loads
setx OLLAMA_MAX_LOADED_MODELS 2 /M  # keep gemma3:4b + qwen3:14b both hot simultaneously
```

**Status:** Commands needed elevation — run the block above in admin PowerShell, then
restart Ollama. Verify with:
```powershell
[System.Environment]::GetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "Machine")
[System.Environment]::GetEnvironmentVariable("OLLAMA_MAX_LOADED_MODELS", "Machine")
```
Both should return `-1` and `2`.

**Note on `OLLAMA_KV_CACHE_TYPE`:** May be silently ignored on Ollama 0.21.0 if not
recognized as a system env var. Fallback: set in Modelfile with
`PARAMETER cache_type_k q8_0` / `PARAMETER cache_type_v q8_0`.

---

## Exact Next Action

**Task 0.7 — GitHub push (Phase 0 final gate)**

1. Create `README.md` in project root with:
   - What JARVIS is (one paragraph)
   - Hardware requirements (GPU, Ollama, Python 3.11+)
   - One-command setup: `pip install -r requirements.txt && uvicorn app.main:app`
   - How to test: `PYTHONPATH=. python tests/pipeline_test.py`
   - Phase roadmap table (0–7)

2. Create public GitHub repo `JARVIS` under `UnknownShadow00`

3. Push:
   ```bash
   git add .
   git commit -m "feat: Phase 0 complete — core brain, intent router, tools, FastAPI server"
   git remote add origin https://github.com/UnknownShadow00/JARVIS.git
   git push -u origin main
   ```

4. After push → start Phase 1 planning (voice pipeline + boot sequence)

---

## Phase 1 Preview (what comes next)

```
app/voice/
  wake_word.py      OpenWakeWord — pip install openwakeword
  vad.py            webrtcvad — pip install webrtcvad
  stt.py            faster-whisper CUDA — pip install faster-whisper
  tts.py            Piper TTS → Kokoro upgrade path
  audio_stream.py   input/output device management
  sounds.py         SFX manager — boot/listening/working/done/error chimes

app/boot.py         Orchestrates: music → Electron HUD → morning report → is_listening=True
```

Phase 1 done when: wake word fires in noisy env, STT < 0.5s, TTS streams (starts before
full response generated), self-suppression confirmed (10 tests), boot sequence runs end-to-end.

---

## Known Gotchas (learned this session)

1. **Ollama Python SDK breaks think=False** — use httpx direct REST, never `AsyncClient.chat()`
2. **PYTHONPATH=.** — required prefix for all test runs from project root
3. **ddgs package** — `duckduckgo_search` was renamed; `web_search.py` handles both via try/except
4. **Router timing on 4070 Ti** — cold: ~37s, warm: ~8–12s. Set MAX_MS=40000 in router tests
5. **qwen3-vl name** — exact string `qwen3-vl`, not `qwen3.5-vl`; Ollama 0.21.0 required
6. **dry_run in config** — set to `false` for normal operation; tests may temporarily flip it
7. **L2 tools need confirmed=True** — registry blocks them otherwise; test this before adding new L2 tools
8. **Self-triggering loop (Phase 1)** — `is_speaking=True` must mute wake word during TTS output
