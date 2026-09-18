# Current production call chain — evidence

Traced by reading `app/server.py` at production commit `2d7a2ec8`. Each stage lists file, symbol,
input, output, side effects, trust level, and whether model prose is authoritative there.

| # | Stage | File : symbol | Input | Output | Side effects | Trust | Model prose authoritative? |
|---|---|---|---|---|---|---|---|
| 1 | HTTP entry | `app/server.py:358 chat()` | `ChatRequest.message` | `ChatResponse` | opens a trace; wakes the runtime | trusted (our code) | — |
| 2 | Lifecycle gate | `app/resource_manager.py:159 ensure_awake_for_interaction` | source string | bool | may wake services, preload a model | trusted | — |
| 3 | Turn pipeline | `app/server.py:598 _process()` | message | `(reply, RouterResult)` | see below | trusted | — |
| 4 | Cancel / kill switch | `app/server.py:611-627` | message | early return | cancels token, stops TTS | trusted | no |
| 5 | Intent classification | `app/brain/router.py:57 classify` → `163 _classify_by_rules`, `89 _classify_with_ollama`, `116 _finalize` | message | `RouterResult(intent, confidence, suggested_tool, reasoning)` | audit `intent_classified`; HTTP call to Ollama when rules miss | **mixed** — regex rules deterministic, fallback is an LLM | partly: the LLM picks the intent and the tool |
| 6 | Argument construction | `app/brain/tool_params.py:33 build_tool_params` | tool name, message | `params` dict | none | deterministic regex | no |
| 7 | Tool gate + execution | `app/tools/registry.py:153 call()` | tool, params, confirmed | `ToolResult` or `ToolError` | audit `tool_call`/`tool_result`/`tool_error`; **real side effects** via `module.execute` | trusted gate | no |
| 8a | Confirmation branch | `app/server.py:640-670` | `ToolError` matching `_is_confirmation_required_error` (788) | pending record + notice text | writes `_pending_confirmations` (87); sends Discord/Telegram; audit `approval_gate_triggered` | trusted store, **unbound + unexpiring** | no |
| 8b | Approval | `app/server.py:792 confirm_request()` | `request_id` | execution result | pops the record; `registry.call(..., confirmed=True)` → **real side effect**; audit `approval_gate_confirmed` | trusted | no |
| 9 | Prompt assembly | `app/brain/prompts.py build_prompt` | message, `context=str(result.output)[:1000]` | message list | none | trusted | — |
| 10 | Model call | `app/brain/llm_client.py:32 chat` | messages, model decision | reply text | HTTP to Ollama; audit `llm_call`/`llm_response` | **untrusted output** | — |
| 11 | Cleaning | `app/brain/response_cleaner.py:36 clean` | model text | cleaned text | strips `[ACTION:*]`/`[EMOTION:*]`, markdown, banned openers, truncates to 2 sentences | cosmetic only | — |
| 12 | Finalize | `app/server.py:602 finalize_reply` | cleaned text | user-visible reply | emotion event to UE5 | — | **yes — this is the answer the user sees** |

## Streaming variant

`app/server.py:840 _process_stream` follows stages 5-10 and returns an async iterator of model
tokens; on any `ToolError` it returns `None` and the WebSocket handler falls back to `_process`
(529). Model prose is authoritative there as well.

## Deterministic exceptions in today's code

* `app/brain/direct_responder.py try_direct_reply` — deterministic answers for trivial queries
  (invoked at `app/server.py:715`).
* `app/server.py:711` — the fixed `confirm_action` sentence.
* `app/brain/response_cleaner.py:57 dry_run_narration` — deterministic dry-run narration.

Everything else that reaches the user on an operational turn is model text.

## Contract mapping

Stage 12 is the boundary contract v1 forbids on operational turns (INV-001). Stages 5-6 are the
ones the contract replaces with deterministic classification and routing. Stage 7 is the only
stage that survives largely intact — it becomes the last mile behind the new dispatcher.
