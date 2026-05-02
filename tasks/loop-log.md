## [2026-05-01] Phase 1 Hardening — 4 tasks
- Fixed `audio_stream.py`: voice pipeline now calls `_process_stream()` + `tts.speak_stream()` for true streaming TTS; falls back to `_process()` + `speak()` for tool/kill-switch paths.
- Fixed `wake_word.listen()`: added `timeout: float | None` param, loop breaks on deadline, `queue.get(timeout=0.1)` replaces blocking `.get()` so self-suppression check runs even under timeout.
- Fixed `boot.py`: `last_project_name()` reads `tasks/loop-log.md`; `pending_task_count()` reads unchecked items from `tasks/todo.md`.
- Wrote `README.md`: hardware requirements, quick start, model stack, phase roadmap, safety levels, kill switch, test commands.
- Fixed `tests/tts_test.py`: added `@pytest.mark.asyncio` and `import pytest`; installed `pytest-asyncio`.
- Result: `pytest -m "not manual"` — 1 passed, 6 deselected (all green).

## [2026-05-01] Task Completed
- Task: Created `tests/hardware_smoke_test.py` (6 manual audio hardware tests) and `tests/conftest.py` (manual marker registration).
- Files changed: tests/hardware_smoke_test.py, tests/conftest.py
- Result: Pass. `python -m compileall` clean, `pytest --collect-only` collects all 6 tests in 0.01s with no warnings.
- Next: Run `pytest -m manual` on live hardware once Piper model files are installed.

## [2026-04-30 17:31:10 -05:00] Task Completed
- Task: Built `app/config.py` to load and validate `config.yaml` with Pydantic models and expose a module-level `settings` singleton.
- Files changed: app/config.py, tasks/loop-log.md
- Result: Pass. Import checks returned `qwen3:14b`, `True`, and `8000`; missing config paths raise `FileNotFoundError` with the full path.
- Next: Add targeted unit tests for malformed YAML and validation failures when the test suite is expanded.
## [2026-04-30 17:33:07 -05:00] Task Completed
- Task: Built `app/logs/audit.py` as a structured JSONL audit logger with a per-process session UUID and background-thread writes.
- Files changed: app/logs/audit.py, tasks/loop-log.md
- Result: Pass. `from app.logs.audit import audit; audit.log('test', {'message': 'audit works'})` executed without error, `logs/audit.jsonl` was created, entries parsed as valid JSON, and sync plus async calls shared the same `session_id` within one process.
- Next: Add focused tests for malformed payloads and shutdown/drain behavior if the project starts formalizing logging test coverage.
## [2026-04-30 17:36:08 -05:00] Task Completed
- Task: Built the async Ollama client wrapper in app/brain/llm_client.py and added the standalone Ollama smoke test at tests/ollama_test.py.
- Files changed: app/brain/llm_client.py, tests/ollama_test.py, tasks/loop-log.md
- Result: Partial pass. Syntax checks passed, the client raises OllamaConnectionError when Ollama is unavailable, and python tests/ollama_test.py is ready to run once the ollama package is installed in the environment.
- Next: Install the Python ollama package in this environment and rerun python tests/ollama_test.py against the local Ollama server.
## [2026-04-30 17:39:02 -05:00] Task Completed
- Task: Built app/brain/prompts.py with the JARVIS system prompt, embedded few-shot examples, and the build_prompt helper for llm_client.chat() messages.
- Files changed: app/brain/prompts.py, tasks/loop-log.md
- Result: Pass. `from app.brain.prompts import JARVIS_SYSTEM_PROMPT, build_prompt` succeeded, `build_prompt('What time is it?')` returned 2 dicts, the system prompt contains `sir` and the banned phrases list, and the few-shot examples are embedded.
- Next: Wire the prompt builder into the assistant runtime once the conversation orchestration layer is added.
## [2026-04-30 20:32:04 -05:00] Task Completed
- Task: Hardened Phase 0 routing, safety gates, tools, tests, dry-run behavior, kill switch handling, and README documentation.
- Files changed: app/brain/router.py, app/brain/kill_switch.py, app/brain/response_cleaner.py, app/server.py, app/tools/apps.py, app/tools/files.py, app/tools/registry.py, app/tools/system_stats.py, app/tools/web_search.py, tests/router_test.py, tests/pipeline_test.py, tests/safety_test.py, README.md, tasks/loop-log.md
- Result: Pass. `python -m compileall app tests`, `$env:PYTHONPATH='.'; python tests/router_test.py`, `$env:PYTHONPATH='.'; python tests/pipeline_test.py`, `$env:PYTHONPATH='.'; python tests/safety_test.py`, and `python tests/ollama_test.py` all passed.
- Next: Phase 0 is ready for a final manual server smoke test and GitHub push before Phase 1 voice work starts.
## [2026-04-30 20:54:35 -05:00] Task Completed
- Task: Ran the final Phase 0 server smoke test, fixed the blocking `what is 2+2` path with a deterministic arithmetic responder, and verified the full Phase 0 test suite.
- Files changed: app/brain/direct_responder.py, app/server.py, tests/direct_responder_test.py, logs/smoke-uvicorn.out.log, logs/smoke-uvicorn.err.log, logs/audit.jsonl, tasks/loop-log.md
- Result: Pass. `python -m compileall app tests`, `$env:PYTHONPATH='.'; python tests/direct_responder_test.py`, `$env:PYTHONPATH='.'; python tests/router_test.py`, `$env:PYTHONPATH='.'; python tests/pipeline_test.py`, `$env:PYTHONPATH='.'; python tests/safety_test.py`, `python tests/ollama_test.py`, and the local FastAPI smoke test all passed. The smoke test confirmed `/health`, dry-run `open VS Code`, deterministic `what is 2+2`, and `JARVIS stop`/`cancel`/`freeze`/`abort` without killing the server.
- Next: Decide whether `projects/JARVIS` should become its own git repo or be committed from the parent workspace; live `qwen3:14b` latency remains high at 131.67s for the Ollama prompt.
## [2026-04-30 21:25:47 -05:00] Task Completed
- Task: Initialized `projects/JARVIS` as its own Git repository and prepared the Phase 0 checkpoint commit after verification.
- Files changed: .git repository metadata, .gitignore, tasks/loop-log.md
- Result: Pass. `.gitignore` excludes runtime logs, data, models, caches, build output, and local Claude permission settings; `python -m compileall app tests`, `$env:PYTHONPATH='.'; python tests/direct_responder_test.py`, `$env:PYTHONPATH='.'; python tests/router_test.py`, `$env:PYTHONPATH='.'; python tests/pipeline_test.py`, `$env:PYTHONPATH='.'; python tests/safety_test.py`, and `python tests/ollama_test.py` all passed.
- Next: Commit the staged Phase 0 checkpoint locally, then set up or confirm a GitHub remote before pushing.
## [2026-04-30 21:37:53 -05:00] Task Completed
- Task: Built the Phase 1 voice and boot scaffold while leaving live model latency improvements for later.
- Files changed: app/voice/sounds.py, app/voice/tts.py, app/voice/vad.py, app/voice/stt.py, app/voice/wake_word.py, app/voice/audio_stream.py, app/boot.py, scripts/setup_autostart.py, assets/audio/README.md, assets/audio/*.wav, tests/tts_test.py, tests/stt_test.py, tests/wake_word_test.py, tests/boot_test.py, tests/sounds_test.py, tests/vad_test.py, CLAUDE.md, tasks/loop-log.md
- Result: Pass. `python -m compileall app tests scripts`, `$env:PYTHONPATH='.'; python tests/sounds_test.py`, `$env:PYTHONPATH='.'; python tests/vad_test.py`, `$env:PYTHONPATH='.'; python tests/tts_test.py`, `$env:PYTHONPATH='.'; python tests/stt_test.py`, `$env:PYTHONPATH='.'; python tests/wake_word_test.py`, `$env:PYTHONPATH='.'; python tests/boot_test.py`, `$env:PYTHONPATH='.'; python tests/direct_responder_test.py`, `$env:PYTHONPATH='.'; python tests/router_test.py`, `$env:PYTHONPATH='.'; python tests/pipeline_test.py`, `$env:PYTHONPATH='.'; python tests/safety_test.py`, and `python tests/ollama_test.py` passed.
- Next: Install/verify live audio dependencies and assets, then run manual hardware acceptance for Piper playback, microphone VAD/STT, OpenWakeWord, push-to-talk, self-suppression, boot autostart, and the full voice loop.
## [2026-05-01 14:21:56 -05:00] Task Completed
- Task: Attempted to push JARVIS Phase 0 to public GitHub, but the workflow stopped at step 1 because `gh auth status` could not run in this environment.
- Files changed: tasks/loop-log.md
- Result: Fail. GitHub CLI is not installed or not on PATH, so authentication could not be verified and the release flow was blocked before repo creation, remote setup, staging, commit, or push.
- Next: Install GitHub CLI and authenticate with `gh auth login`, then rerun the Phase 0 public push workflow.
## [2026-05-01 14:24:31 -05:00] Task Completed
- Task: Verified and fixed streaming TTS so the WebSocket path now feeds live LLM tokens into sentence-buffered speech playback before the full reply is complete, and added a flag-focused `speak_stream` test.
- Files changed: app/voice/tts.py, app/server.py, tests/tts_test.py, tasks/loop-log.md
- Result: Pass. `python -m compileall app tests` and `$env:PYTHONPATH='.'; python tests/tts_test.py` passed, `speak_stream()` now accepts token iterators, flips the module-level `is_speaking` flag for the full stream lifetime, and `/ws` uses LLM streaming while `/chat` remains unchanged.
- Next: Run a live WebSocket + Piper smoke test against Ollama to confirm audible first-chunk latency on real hardware.
## [2026-05-01 14:22:57 -05:00] Task Completed
- Task: Built `scripts/install_piper.py` as a self-contained stdlib installer for the Piper Windows x64 binary and JARVIS voice model, including idempotent downloads, ZIP extraction, verification checks, and clear failure output.
- Files changed: scripts/install_piper.py, tasks/loop-log.md
- Result: Pass. `python -m py_compile scripts/install_piper.py` succeeded, and `python scripts/install_piper.py` started cleanly, printed the expected download steps, exercised the failure path with blocked network access, and printed PASS/FAIL verification lines plus the final pytest instruction.
- Next: Rerun `python scripts/install_piper.py` in an environment with outbound access to GitHub and Hugging Face to complete the actual downloads.
## [2026-05-01 21:09:10 -05:00] Task Completed
- Task: Fixed Phase 1 voice setup blockers: Python 3.13 voice dependencies, stable Piper model download, OpenWakeWord ONNX loading, wake-word/manual test contracts, VAD/STT public aliases, and pytest collection for existing acceptance tests.
- Files changed: CLAUDE.md, config.yaml, config.yaml.example, requirements.txt, scripts/install_piper.py, app/voice/tts.py, app/voice/wake_word.py, app/voice/vad.py, app/voice/stt.py, tests/hardware_smoke_test.py, tests/direct_responder_test.py, tests/router_test.py, tests/pipeline_test.py, tests/safety_test.py, tests/sounds_test.py, tests/stt_test.py, tests/vad_test.py, tests/wake_word_test.py, tasks/todo.md
- Result: Pass. Installed voice dependencies, downloaded Piper en_US-lessac-high model, downloaded OpenWakeWord hey_jarvis resources, `python -m pytest -m manual` passed 6/6, `python -m pytest -m "not manual"` passed 10/10, and targeted py_compile passed.
- Next: Run the full live voice loop with spoken wake word -> STT -> response -> streaming TTS, then install/authenticate GitHub CLI for the push workflow.

## [2026-05-01 21:26:47 -05:00] Task Completed
- Task: Prepared the Phase 1 checkpoint for closeout by ignoring local Piper runtime files, refreshing stale project status docs, rerunning unit and manual hardware smoke tests, and installing GitHub CLI.
- Files changed: .gitignore, README.md, CLAUDE.md, tasks/todo.md, tasks/loop-log.md
- Result: Fail. `python -m pytest -m "not manual"` passed 10/10 and `python -m pytest -m manual` passed 6/6, but the final spoken live loop was not verified in this agent run and GitHub push remains blocked until `gh auth login` is completed.
- Next: Run the spoken test "hey jarvis, what time is it?" against the live voice pipeline, then authenticate `C:\Program Files\GitHub CLI\gh.exe`, create/confirm `UnknownShadow00/JARVIS`, commit the checkpoint, rename/push the branch to `main`.

## [2026-05-01 21:33:05 -05:00] Task Completed
- Task: Checked GitHub CLI authentication after user reported GitHub confirmation.
- Files changed: tasks/loop-log.md
- Result: Fail. `gh auth status` finds account `UnknownShadow00`, but the default token is invalid, so repo creation and push are still blocked.
- Next: Re-authenticate with `& "C:\Program Files\GitHub CLI\gh.exe" auth login -h github.com`, then rerun `& "C:\Program Files\GitHub CLI\gh.exe" auth status`.
