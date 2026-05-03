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

## [2026-05-01 21:36:57 -05:00] Task Completed
- Task: Created the public GitHub repository, renamed the local branch to `main`, committed the Phase 1 voice checkpoint, and pushed it to GitHub.
- Files changed: tasks/todo.md, tasks/loop-log.md
- Result: Pass. `UnknownShadow00/JARVIS` exists, `origin` points to `https://github.com/UnknownShadow00/JARVIS.git`, and `git push -u origin main` succeeded.
- Next: Run the remaining full spoken live loop test before closing Phase 1 acceptance.

## [2026-05-01 21:45:38 -05:00] Task Completed
- Task: Continued Phase 1 live voice-loop validation and fixed VoicePipeline shutdown responsiveness while the final spoken wake loop remains pending.
- Files changed: app/voice/audio_stream.py, tests/voice_pipeline_test.py, CLAUDE.md, tasks/loop-log.md
- Result: Fail against final live-loop acceptance. `python -m pytest tests\voice_pipeline_test.py` passed, `python -m pytest -m "not manual"` passed 11/11, and `python -m pytest -m manual` passed 6/6. The bounded live voice loop now exits cleanly, but the audit log showed repeated `wake_timeout` events and no `wake_detected`, `stt_transcribed`, `voice_request`, or `voice_reply` events during the spoken acceptance attempt.
- Next: Re-run the spoken acceptance close to the active microphone, verify input device selection and wake-word sensitivity if detection still times out, then close Phase 1 once wake word -> STT -> response -> streaming TTS is captured.

## [2026-05-01 21:53:16 -05:00] Task Completed
- Task: Diagnosed microphone input routing for the blocked Phase 1 live wake-word loop.
- Files changed: tasks/loop-log.md
- Result: Fail against live-loop acceptance. `config.yaml` uses `voice.input_device_index: -1`, so JARVIS listens to Windows default input device 1. A 5-second default-input level test reported `peak=31`, `rms=7.95`, `heard_audio=False`. A scan across available input devices found no strong speech signal; the highest peak was device 6 at `peak=286`, and SteelSeries Sonar devices 15 and 17 failed to open with PortAudio `Invalid device`.
- Next: Confirm the user spoke during the scan. If yes, fix Windows/default mic routing or choose a working physical input device before rerunning the live wake loop; if no, rerun the scan while speaking continuously.

## [2026-05-01 21:56:00 -05:00] Task Completed
- Task: Re-ran mic scan with clear speaking cue and re-ran the live wake loop.
- Files changed: tasks/loop-log.md
- Result: Fail against full live-loop acceptance. The mic scan passed with strong input on default device 1 (`peak=10856`, `rms=711.27`). The live loop detected the wake word repeatedly (`wake_detected` scores 0.536, 0.956, 0.989, 0.990) and VAD recorded speech, but STT failed because `faster-whisper` tried to download/load `medium.en` from Hugging Face and no local cached model exists; the environment returned `WinError 10013` for network access. TTS error handling worked and spoke the fallback error response.
- Next: Download/cache the configured faster-whisper model locally or point `voice.stt_model` at a local CTranslate2 Whisper model path, then rerun the full wake word -> STT -> response -> streaming TTS acceptance test.

## [2026-05-01 21:57:55 -05:00] Task Completed
- Task: Checked whether the faster-whisper STT model was cached after the user requested another run.
- Files changed: tasks/loop-log.md
- Result: Fail against full live-loop acceptance. `WhisperModel('medium.en', local_files_only=True)` failed for both configured CUDA/float16 and CPU/int8 loads with `LocalEntryNotFoundError`; no Hugging Face cache environment variables or `models--Systran--faster-whisper-medium.en` directory were found under the user profile.
- Next: Run the faster-whisper model cache command from a normal internet-enabled PowerShell, then rerun the full live loop.

## [2026-05-01 22:00:17 -05:00] Task Completed
- Task: Rechecked faster-whisper local cache before another live-loop attempt.
- Files changed: tasks/loop-log.md
- Result: Fail against full live-loop acceptance. `WhisperModel('medium.en', local_files_only=True)` still failed for both configured CUDA/float16 and CPU/int8 loads with `LocalEntryNotFoundError`, and no `models--Systran--faster-whisper-medium.en` cache directory was found under the user profile.
- Next: Run the cache command in the same Python environment used by this project, verify with a local-only load, then rerun the full live voice loop.

## [2026-05-01 22:14:52 -05:00] Task Completed
- Task: Verified cached faster-whisper model, added STT CPU fallback for missing CUDA runtime, and reran live voice-loop acceptance.
- Files changed: app/voice/stt.py, tests/stt_test.py, CLAUDE.md, tasks/loop-log.md
- Result: Fail against full live-loop acceptance. `WhisperModel('medium.en', local_files_only=True)` now loads for configured CUDA/float16 and CPU/int8. The first live run detected wake word and loaded STT but failed on missing `cublas64_12.dll`; STT now retries CPU/int8 after CUDA transcription errors. `python -m pytest tests\stt_test.py` passed 2/2 and `python -m pytest -m "not manual"` passed 12/12. The delayed-cue live loop exited cleanly but did not detect the wake phrase, so no STT transcript or final response was produced.
- Next: Rerun the live loop with the wake phrase spoken after the delayed cue and close to the active mic; if wake detection remains intermittent, lower `voice.wake_word_sensitivity` or add a one-shot wake diagnostics script that logs per-frame scores during the cue window.

## [2026-05-02 19:06:45 -05:00] Task Completed
- Task: Created `app/tools/shell.py` with hard-denied command patterns, allowed-root cwd validation, bounded subprocess execution, and added pytest coverage for direct tool behavior plus registry confirmation and dry-run handling.
- Files changed: app/tools/shell.py, tests/test_shell_tool.py, tasks/loop-log.md
- Result: Pass. `pytest tests/test_shell_tool.py -q` passed 7/7, `pytest -m "not manual" -q` passed 19/19, and `python -c "from app.tools.shell import execute, SAFETY_LEVEL; print(SAFETY_LEVEL)"` printed `2`.
- Next: No immediate follow-up needed.

## [2026-05-02 19:08:49 -05:00] Task Completed
- Task: Migrated app/server.py from FastAPI's deprecated startup event hook to a lifespan async context manager and added shutdown cleanup/audit logging.
- Files changed: app/server.py, tasks/loop-log.md
- Result: Pass. python -m pytest tests/ -m 'not manual' -q passed 19/19 with 6 deselected and no FastAPI on_event DeprecationWarning in the output.
- Next: No immediate follow-up needed.

## [2026-05-02 19:35:31 -05:00] Task Completed
- Task: Added oice_pipeline.start() to the FastAPI lifespan startup sequence in pp/server.py
- Files changed: app/server.py, tasks/loop-log.md
- Result: pass against acceptance criteria; pytest 	ests/ -m ''not manual'' -q reported 19 passed and oice_pipeline.start is present in pp/server.py
- Next: None

## [2026-05-02 20:56:39] Task Completed
- Task: Created scripts/wake_diag.py and tests/test_wake_diag.py for wake-word diagnostics and verification.
- Files changed: scripts/wake_diag.py, tests/test_wake_diag.py, tasks/loop-log.md
- Result: pass against acceptance criteria; python -m pytest tests/test_wake_diag.py -q passed (4 tests).
- Next: Optional live-device validation with PyAudio/OpenWakeWord hardware input to tune final threshold.

## [2026-05-02 21:03:01 -05:00] Task Completed
- Task: Created the Phase 2 calendar tool for reading local .ics events by date, added registry wiring for the calendar tool, and added pytest coverage for dry-run, empty results, .ics parsing, and registration.
- Files changed: app/tools/calendar.py, app/tools/registry.py, tests/test_calendar_tool.py, tasks/loop-log.md
- Result: Pass. `python -m pytest tests/test_calendar_tool.py -q` passed 5/5 and `python -m pytest -m 'not manual' -q` passed 28/28 with 6 deselected.
- Next: No immediate follow-up needed.

