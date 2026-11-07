# JARVIS — Phase 0 Build Tasks for Claude Code

> Give this file to Claude Code at the start of a Phase 0 session.
> Claude Code should also read CLAUDE.md before starting any work.
> Complete tasks in order. Run the test after each task before moving on.

---

## Before You Start

1. Read `CLAUDE.md` completely
2. Read `config.yaml` completely
3. Verify Ollama is running: `curl http://localhost:11434/api/tags`
4. Verify the router model is pulled: `ollama pull gemma3:4b`
5. Verify the main model is pulled: `ollama pull qwen3:14b` (or qwen3:32b on 5090)

---

## Task 0.1 — Create the repo structure

Create every folder in the structure defined in CLAUDE.md.
Create empty `__init__.py` files in every Python package folder.
Do NOT create any implementation files yet — just the structure.

**Test:** `find . -type d | sort` should show all folders.

---

## Task 0.2 — Build config.py

**File:** `app/config.py`

Load and validate `config.yaml` using Pydantic.
Expose a single `settings` object that all other modules import.
If the config file is missing or malformed, raise a clear error with the path.

```python
# Usage pattern every other file should follow:
from app.config import settings
model = settings.models.main
```

**Test:** `python -c "from app.config import settings; print(settings.models.main)"` should print the model name.

---

## Task 0.3 — Build the audit logger

**File:** `logs/audit.py`

Write a structured JSONL logger. Every event must log:
- `timestamp` (ISO 8601)
- `event_type` (e.g. "user_input", "intent_classified", "tool_called", "tool_result", "error")
- `data` (dict — event-specific payload)
- `session_id` (UUID generated at startup, same for whole session)

Expose: `audit.log(event_type, data)` — non-blocking, async-safe.

**Test:** Call `audit.log("test", {"message": "audit works"})` and verify a line appears in `./logs/audit.jsonl`.

---

## Task 0.4 — Build the Ollama client

**File:** `brain/llm_client.py`

Build a wrapper around the Ollama Python client with three methods:
- `chat(messages, model=None, stream=False)` — general conversation (uses `settings.models.main`)
- `code(messages, stream=False)` — coding tasks (uses `settings.models.coder`)
- `vision(messages, images=None)` — vision tasks (uses `settings.models.vision`)

All calls must:
- Read model names from `settings.models` — never hardcoded
- Log every call and response to audit log
- Handle Ollama connection errors gracefully — raise `OllamaConnectionError` with a clear message
- Support streaming when `stream=True`

**Test:** `python tests/ollama_test.py` — must confirm connection to Ollama and get a response.

---

## Task 0.5 — Write the JARVIS system prompt

**File:** `brain/prompts.py`

Write the JARVIS system prompt. This is the most important file for making it feel right.

Rules (enforce all of these):
- Always address user as "sir"
- Responses: 1 sentence ideal, 2 maximum. NEVER 3.
- No markdown, no bullets, no code blocks in voice responses
- Never say "as an AI" or break character
- Lead with action, not self-reference (never start with "I")
- Banned phrases: "Absolutely", "Great question", "I'd be happy to", "Of course", "How can I help", "Is there anything else", "I apologize"
- Append action tags after speech: `[ACTION:TYPE:PARAMS]`

Expose:
- `JARVIS_SYSTEM_PROMPT` — base system prompt string
- `build_prompt(user_message, context=None, project=None)` — builds full message list

Include a few-shot examples block inside the system prompt covering:
- Simple answer
- Tool action
- Level 2 confirmation gate
- Uncertainty / asking instead of guessing

**Test:** Call `llm_client.chat([{"role":"user","content":"What time is it?"}])` and verify the response says "sir" and is under 2 sentences.

---

## Task 0.6 — Build the intent router

**File:** `brain/router.py`

Build a fast intent classifier using `gemma3:4b` that runs in under 50ms.

Must classify every user message into exactly one of:
- `respond` — just answer, no tools needed
- `use_tool` — needs a tool (include suggested tool name)
- `retrieve_memory` — needs memory lookup first
- `vision` — needs screen or webcam
- `confirm_action` — high-risk action needs confirmation

Return a `RouterResult` dataclass:
```python
@dataclass
class RouterResult:
    intent: str           # one of the 5 above
    confidence: float     # 0.0 to 1.0
    suggested_tool: str   # tool name if intent == "use_tool", else ""
    reasoning: str        # one-sentence explanation (for audit log)
```

If confidence < `settings.safety.confidence_threshold`, set `intent = "confirm_action"`.

Log every classification to the audit log.

**Test:** Run 20 test queries covering all 5 intents. All must classify correctly. Print timing — must be under 200ms on GPU.

---

## Task 0.7 — Build the tool registry

**File:** `tools/registry.py`

Build a dynamic tool registry that:
- Auto-discovers all tool files in `tools/` folder
- Each tool file exposes: `TOOL_NAME`, `SAFETY_LEVEL`, `DESCRIPTION`, `execute(params)`
- Registry exposes: `get_tool(name)`, `list_tools()`, `execute(name, params)`
- Before executing any tool: checks `settings.safety.dry_run`
  - If `dry_run=True`: returns `{"dry_run": True, "would_do": description}` instead of executing
- Checks safety level against `settings.safety.approval_mode`
- Logs every execution to audit log

**Test:** `python -c "from tools.registry import registry; print(registry.list_tools())"` should print an empty list (no tools built yet — that's fine).

---

## Task 0.8 — Build the first 4 tools

Build these tools in `tools/`. Each file follows the exact same pattern:

```python
TOOL_NAME = "tool_name"
SAFETY_LEVEL = 0  # 0=safe, 1=reversible, 2=risky, 3=blocked
DESCRIPTION = "One sentence describing what this tool does."

def execute(params: dict) -> dict:
    """Execute the tool. Return {"success": bool, "result": any, "error": str|None}"""
    ...
```

**Tool 1: `tools/system_stats.py`** (Safety Level 0)
- Returns: CPU%, RAM used/total, GPU name + VRAM used/total (GPUtil), disk usage, top 5 processes by CPU

**Tool 2: `tools/web_search.py`** (Safety Level 0)
- Uses `duckduckgo_search` — no API key
- Params: `{"query": str, "max_results": int = 5}`
- Returns: list of `{title, url, snippet}`
- Also expose `fetch_page(url)` that reads a URL and returns clean text (BeautifulSoup)

**Tool 3: `tools/apps.py`** (Safety Level 0)
- `open_app(name)` — opens an application by name on Windows (subprocess + known app paths)
- `close_app(name)` — closes an application by name
- Maintain a map of common app names → executable paths

**Tool 4: `tools/files.py`** (Safety Level 1)
- `read_file(path)` — returns file content as string
- `list_dir(path)` — returns directory listing
- `search_files(path, query)` — finds files by name or content
- All paths must be within `settings.paths.projects_dir` or explicitly whitelisted

**Test:** Call each tool directly and verify output. Then test via registry: `registry.execute("system_stats", {})`.

---

## Task 0.9 — Build the kill switch

**File:** `app/server.py` (partial — just the kill switch for now)
**File:** `brain/kill_switch.py`

The kill switch must:
- Listen for voice command: any message containing "stop", "cancel", "freeze", "abort"
- Listen for keyboard hotkey: `Ctrl+Alt+J` using the `keyboard` library
- On activation: set a global `JARVIS_ACTIVE = False` flag
- Cancel any running tasks/tool calls
- Stop any TTS output
- Speak: "Understood, sir. Standing by."
- Log the kill event to audit log

**Test:** Manually trigger both the voice and keyboard kill switch. Verify the flag is set and a log entry appears.

---

## Task 0.10 — Build the dry-run mode

**Already partially built in Task 0.7 (registry checks dry_run).**

Add dry-run to the response pipeline:
- When `dry_run=True` and a tool would be called, JARVIS says:
  "I would [describe action], sir. Dry run mode is active — no action taken."
- The audit log still records the would-be action
- All safety checks still run (so you can verify them in dry-run)

**Test:** Set `dry_run: true` in config.yaml. Call a tool via voice/text. Verify it narrates instead of executing.

---

## Task 0.11 — Build the FastAPI server (minimal Phase 0 version)

**File:** `app/server.py`

Build a minimal FastAPI server that:
- WebSocket endpoint at `/ws` — accepts text messages, returns JARVIS responses
- REST endpoint `GET /health` — returns status, active model, uptime
- REST endpoint `POST /chat` — accepts `{message: str}`, returns `{response: str}`
- On startup: verify Ollama is responding, log startup to audit
- On each message:
  1. Route via `router.py` → get intent
  2. If `use_tool` → execute via registry (respecting dry_run and safety)
  3. Pass to `llm_client.chat()` with JARVIS system prompt
  4. Return response
  5. Log everything to audit

**Test:** Start server with `uvicorn app.server:app --reload`. Connect via browser WebSocket at `ws://localhost:8000/ws`. Type "what time is it" and verify JARVIS responds in character.

---

## Task 0.12 — Write test scripts

Write these in `tests/`:

**`tests/ollama_test.py`**
- Connects to Ollama
- Verifies all configured models are available (main, coder, router)
- Sends a test prompt to main model
- Measures response time
- Prints pass/fail

**`tests/pipeline_test.py`**
- Starts the full server
- Sends 10 test messages via WebSocket
- Verifies: personality rules (sir, concise), intent routing, tool execution, audit logging
- Prints pass/fail for each test

**`tests/safety_test.py`**
- Tests all 4 safety levels
- Tests dry_run mode
- Tests confidence gating
- Tests kill switch
- Prints pass/fail

---

## Task 0.13 — Write README.md

Write a clean README that explains:
- What JARVIS is (2 sentences)
- Hardware requirements
- One-command setup:
  ```bash
  git clone https://github.com/[username]/jarvis
  cd jarvis
  pip install -r requirements.txt
  ollama pull qwen3:14b && ollama pull gemma3:4b
  python app/main.py
  ```
- Configuration (point to config.yaml)
- Project structure overview
- Current phase and what's built

---

## Phase 0 Complete When

Run this checklist before moving to Phase 1:

- [ ] `python tests/ollama_test.py` — PASS
- [ ] `python tests/pipeline_test.py` — PASS
- [ ] `python tests/safety_test.py` — PASS
- [ ] Type "open VS Code" → dry_run narrates, does not open
- [ ] Type "what is 2+2" → JARVIS responds with "sir", under 2 sentences
- [ ] Type "JARVIS stop" → kill switch activates, logs to audit
- [ ] `cat logs/audit.jsonl | wc -l` shows > 0 entries
- [ ] Change `models.main` in config.yaml → server picks up new model without restart
- [ ] GitHub repo is public with README

**After Phase 0 passes: update the "Current Status" section in CLAUDE.md.**

---

## Notes for Claude Code

- Always check `dry_run` before executing anything real
- Always log to audit before AND after every tool call
- Model names come from `settings.models.*` — never strings
- If Ollama is down, speak the error: "Afraid the AI service is unavailable, sir. Retrying."
- Every function should have a docstring
- Use async/await throughout the FastAPI server
- The personality is everything — test it constantly during build
