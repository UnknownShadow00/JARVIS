# Current JARVIS Production Architecture — as inspected at commit `2d7a2ec8`

**Status:** factual inspection record for Task 13B11A. Planning input only; nothing here was changed.

**Inspection basis.** Production repo `/home/jarvis/JARVIS` at
`2d7a2ec816500610eafdba4c1a3c0d73f5594c18`, clean tree, 83 Python files under `app/`. The
workspace copy used for reading is byte-identical for the inspected paths: `git ls-tree` gives
the same `app/` tree object `7d6e31f42ba43fb1b478a7b999ec819e23c1973a` and the same
`config.yaml` blob `1e5d30f0699c3d9bf2bbfea7317cdfc8ff2c79cb` at both `2d7a2ec8` and the
workspace HEAD, so line numbers below are production line numbers.

---

## 1. Entrypoints

| Surface | File | Notes |
|---|---|---|
| Runtime entry | `app/main.py:1-15` | `uvicorn.run(app, host=settings.server.host, port=settings.server.port)` |
| FastAPI app | `app/server.py` (962 lines) | REST + WebSocket + lifespan |
| CLI | `app/cli.py` (230 lines) | `jarvis status/wake/sleep`, used by `jarvis.cmd` |
| Boot sequence | `app/boot.py` (310 lines) | context prefetch, HUD, morning report |

`python -m app.server` imports the module and exits without serving; the supported entry is
`python -m app.main` (README line 97).

## 2. HTTP / WebSocket surface (`app/server.py`)

| Route | Line | Purpose |
|---|---|---|
| `GET /health` | 293 | status, `resource_state`, `dry_run`, models |
| `GET /resource/status`, `POST /resource/sleep/light|deep`, `/resource/wake`, `/resource/shutdown` | 306-334 | lifecycle control |
| `GET /health/tools`, `/health/readiness` | 335-344 | tool availability |
| `POST /chat` | 357 | the main text path |
| `POST /stop` | 382 | cancel token + TTS stop |
| `POST /confirm/{request_id}` | 792 | approve a pending tool call |
| `POST/GET/PATCH/DELETE /tasks…`, `/schedule/jobs…`, `/memory/…`, `/network/status` | 389-470 | agent queue, scheduler, memory, network |
| `WS /ws` | ~500-560 | streaming chat, uses `_process_stream` (840) then falls back to `_process` |

Auth: bearer token middleware (`_api_token_ok` 174, `api_token_middleware` 227) and WebSocket
origin/token checks (187-217). Binding is loopback by default (`settings.server.host`).

## 3. The request-to-response pipeline

`chat()` (358) → `resource_manager.ensure_awake_for_interaction("chat")` → `_process(message)`
(598) → `finalize_reply()` (602).

`_process` in order:

1. **Cancel / kill switch** — `_is_cancel_command`, `check_voice`, `is_active()` (611-627).
2. **Intent classification** — `intent_router.classify(message)` (630), `app/brain/router.py`.
3. **Branch on intent**:
   * `use_tool` (632-702): `_build_tool_params_traced(tool, message)` → `registry.call(tool, params)`
     → on `ToolError` whose text contains "confirmation" (`_is_confirmation_required_error`, 788)
     a pending confirmation is created (646) and a Discord/Telegram approval message is sent
     (652-668); otherwise the error string becomes `context`. Then `build_prompt(message,
     context=context)` → `llm_client.chat(...)` → **the model writes the user-visible reply**.
   * `confirm_action` (704-712): emits a confirmation event and returns a fixed string
     `f"That action requires your confirmation, sir. Shall I proceed with: {message}?"`.
   * `respond` (714-717): `try_direct_reply` (`app/brain/direct_responder.py`) may answer
     deterministically for trivial queries (time, stats); otherwise falls through.
   * `deep_reasoning` (719), `vision` (731), `retrieve_memory` (755), default (769): each builds a
     prompt and returns model prose.
4. **`finalize_reply`** (602): `clean(reply)` (`app/brain/response_cleaner.py:36`) then emotion
   parse for UE5.

`_process_stream` (840) is the WebSocket variant and ends in model prose as well; on any
`ToolError` it returns `None` and the caller falls back to `_process`.

**Trust characterisation.** In every branch except `try_direct_reply` and the fixed
`confirm_action` string, the final user-visible text is model output that has been cosmetically
cleaned. Tool results enter only as a truncated `context` string inside the prompt
(`str(result.output)[:1000]`, 640). Nothing verifies that the model's sentence matches the tool
result, and nothing prevents the model from asserting an action that never ran.

## 4. Intent router (`app/brain/router.py`, 323 lines)

* `classify` (57) → `_classify` (62): deterministic regex rules first (`_classify_by_rules`, 163),
  then a Gemma3 call to Ollama (`_classify_with_ollama`, 89) returning JSON, then `_finalize` (116).
* Intents: `respond`, `use_tool`, `retrieve_memory`, `vision`, `confirm_action`, `deep_reasoning`
  (`_VALID_INTENTS`, 32).
* Deterministic rules include: Obsidian action tag → `obsidian`; shell verbs → `shell`;
  a destructive/communication verb set (`delete|format|wipe|erase|destroy|remove all|commit|push|
  deploy|install|uninstall|send|message|email|purchase|buy`) → `confirm_action`; screenshot; vision.
* `_finalize` (116) applies optional embedding tool selection and demotes any result below
  `settings.safety.confidence_threshold` to `confirm_action`, then writes `intent_classified` to audit.

This is an *intent* classifier, not the contract's request classifier: it has no notion of
primary action, reporting intent, target, multi-action or capability, and it produces a tool name
rather than a routed action.

## 5. Argument construction (`app/brain/tool_params.py`, 148 lines)

`build_tool_params(tool_name, message)` (33) maps free text to tool parameters with regexes:
`web_search` strips search verbs; `apps` decides open/close and calls `extract_app_name` (26),
which lower-cases the message, replaces "visual studio code" with "vscode" and strips verbs;
`files` picks `read`/`list` and a root from `settings.paths`; `shell` strips the leading verb and
passes the rest as `command`; `calendar` computes a date window.

There is one canonicalization-like rule (the vscode replacement) embedded in extraction. Raw vs
canonical arguments are not separately represented anywhere.

## 6. Tool registry and safety gate (`app/tools/registry.py`, 273 lines)

* Tools are modules under `app/tools/` exposing `execute(params)` and `SAFETY_LEVEL`
  (`_load_tool`, 90; validity check at 105).
* `registry.call(tool, params, confirmed=False)` (153): reads `SAFETY_LEVEL`, computes
  `confirmation_required = self._requires_confirmation(level) and not confirmed` (236: `strict`
  → ≥0, `safe` → ≥1, otherwise ≥2), writes `tool_call` audit, then:
  level ≥ 3 → `ToolError` "Level 3 (blocked)"; confirmation required → `ToolError` "Requires user
  confirmation before executing."; `settings.safety.dry_run` → returns a `[DRY RUN]` string;
  else `module.execute(params)` inside a trace span, then `tool_result` audit.
* `ToolResult` (41) carries `tool`, `output`, `dry_run` — no invocation id, no status field, no
  structured facts, no error object.
* `_capability_for` (255) derives a coarse capability label for tracing.

Installed tools and declared levels: `apps` 0, `calendar` 0, `kasa` 0, `screenshot` 0,
`system_stats` 0, `vision` 0, `web_search` 0, `browser` 1, `browser_use` 1, `files` 1,
`mcp_client` 1, `obsidian` 1, `cli` 1, `cad` 2, `computer_use` 2, `shell` 2; plus
`app/computer/mouse_keyboard.py` 2.

## 7. Confirmation handling

* Store: `_pending_confirmations: dict[str, dict] = {}` at `app/server.py:87` — a module-level
  in-memory dict keyed by an 8-character UUID slice (645).
* Creation (646): stores `{tool, params, trace_id}` and audits `approval_gate_triggered`.
* Approval (`confirm_request`, 792): pops the entry and calls
  `registry.call(tool_name, params, confirmed=True)`, audits `approval_gate_confirmed`.
* Properties: no user or session binding, no expiry or freshness, no re-validation of arguments at
  approval time, no persistence — the dict is lost on restart and on the deep-sleep process exit.
* A second, parallel gate exists for computer control: `ComputerSafetyGate.check` in
  `app/computer/safety.py:9` (`blocked` / `confirmation_required` / `dry_run_active` / `ok`).

## 8. Audit and tracing

* `app/logs/audit.py` — `AuditLogger.log(event_type, data)` (46) enqueues
  `{schema_version: 2, timestamp, event_type, data, session_id, trace_id?}` onto a
  `queue.SimpleQueue`; a daemon thread writes JSONL via `JsonlTraceWriter` with rotation, with a
  direct-append fallback on writer failure. Output: `logs/audit.jsonl` (`settings.logging.audit_log`).
* Event types observed in code: `intent_classified`, `tool_call`, `tool_result`, `tool_error`,
  `tool_load_error`, `approval_gate_triggered`, `approval_gate_confirmed`, `computer_safety_check`,
  `resource_*` (transitions, unloads, state write errors), `ws_origin_rejected`,
  `task_queue_save_error`, `tool_embedding_warning`.
* `app/observability/tracing.py` (276 lines) provides `start_trace`, `trace_span`, `emit_event`,
  `current_trace_id` and a JSONL writer under `data/traces`; `/chat` opens a trace at 359 and
  `/confirm` correlates to the original trace id (795-800).

## 9. Lifecycle (`app/resource_manager.py`, 835 lines)

* `RuntimeState` (29): `ACTIVE`, `LIGHT_SLEEP`, `DEEP_SLEEP`.
* `_idle_monitor` (314) drives transitions from `settings.resource_mode` timeouts; `light_sleep`
  (199) stops voice/background services and unloads models; `deep_sleep` (223) additionally exits
  the process (observed in production audit as `resource_auto_deep_sleep_exit`).
* `unload_all_ollama_models()` (559) collects **every model currently loaded in the shared Ollama**
  (`list_loaded_ollama_models`, 530) *plus* `configured_ollama_models()` (502) and unloads each via
  `keep_alive=0`. This is the mechanism that unloaded the Granite candidate mid-run during Task
  13B10C4.
* State is persisted to `data/resource_state.json` (`_write_state`, 485): state, previous state,
  reason, timestamp, pid, last activity, resources. No conversational or confirmation state is
  persisted.

## 10. Configuration (`app/config.py`, 277 lines; `config.yaml`)

Pydantic `StrictModel` sections: `models`, `safety`, `voice`, `boot`, `server`, `resource_mode`,
`memory`, `tools`, `routing`, `agent`, `comms`, `computer`, `paths`, `logging`, `openjarvis`.
Relevant fields: `safety.approval_mode`, `safety.dry_run`, `safety.confidence_threshold`,
`safety.max_tool_chain`; `agent.hermes_enabled: false` (config.yaml line 168, `AgentConfig` 176);
`routing.embedding_enabled: false`.

Existing feature-flag style: plain booleans in `config.yaml` validated by a strict pydantic model.

## 11. Persistence

There is **no database**. State lives in files: `logs/audit.jsonl`, `data/traces/*`,
`data/resource_state.json`, `data/agent_tasks.json` (`app/agent/task_queue.py:14`, `_save` 110),
`data/chroma/` for the optional RAG store, plus the Obsidian vault directory.

## 12. Model layer

`app/brain/llm_client.py` (338 lines): `chat`, `deep_reasoning`, `code`, `vision`, streaming
support, `OllamaConnectionError`, thinking suppression. Models are selected by
`app/brain/complexity_router.py` (`_plan_traced` in server) across
`settings.models.main|main_thinking|main_trivial|coder|router|vision`. Prompts are assembled by
`app/brain/prompts.py` (`build_prompt`), which instructs the model to append `[ACTION:*]` and
`[EMOTION:*]` tags.

## 13. Legacy action tags

* The system prompt (`app/brain/prompts.py:30-50`) teaches the model to emit
  `[ACTION:BROWSER:…]`, `[ACTION:APP:…]`, `[ACTION:FILE:…]`, `[ACTION:SHELL:…]`,
  `[ACTION:MESSAGE:…]`, `[ACTION:OBSIDIAN:…]`, `[ACTION:VISION:…]`, `[EMOTION:…]`.
* `clean()` (`app/brain/response_cleaner.py:36`) **strips every `[ACTION:*]` and `[EMOTION:*]` tag**
  from the reply before it is returned.
* The only tag actually consumed is Obsidian: `_classify_by_rules` routes a message containing
  `[action:obsidian:` to the `obsidian` tool (`app/brain/router.py:170`) and
  `_extract_note_target` (`app/brain/tool_params.py:133`) reads its payload. `[EMOTION:*]` is read
  by `parse_emotion_from_reply` (`app/comms/ue5_bridge.py:69`) before cleaning.
* Net effect: action tags are, today, mostly decorative — execution happens through the router's
  `suggested_tool`, not through the tags.

## 14. Tests and evaluation

* `tests/` — pytest suite (`router_test.py`, `safety_test.py`, `pipeline_test.py`,
  `direct_responder_test.py`, `boot_test.py`, plus `e2e/`, `perf/`, hardware smoke), `pytest.ini`
  markers exclude e2e/stress/perf/hardware in CI.
* `evals/` — deterministic harness: `runner.py`, `grader.py`, `adapter.py`, `schema.py`,
  `golden.jsonl`, `fixtures/`. `python -m evals.runner --mode deterministic` is the golden gate
  (currently 12/20 with eight known failures).

## 15. Frontend / UI

`frontend/electron` (HUD), `frontend/pwa`, `frontend/hologram`. They consume `/chat`, `/ws` and
`/health`; the confirmation flow today is surfaced out-of-band through Discord/Telegram text and
the `/confirm/{id}` URL, not through a first-class UI affordance.
