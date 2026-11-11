# Enrollment reconciliation

The input audit classifies84 offline-labelled exclusions (30 relevant,38 out of scope,8 unsafe,8 unclear), plus two separately hardware-labelled modules. MODULE-DECISIONS.json/MD covers all86 explicitly. scripts/test_enrollment.json is the independently digest-pinned authority for all136 Python files, including helpers; scripts/required_tests.json pins exact positive/negative node inventories and relevant source/data hashes. scripts/coverage_modules.json is an explicit36-module allowlist, not discovery output.

All30 relevant modules are now required and pass217-case coverage together with six previously unresolved modules. Feature coverage includes mocked end-to-end cancellation/router behavior; host-control refusal and native child ownership; computer safety; browser/files/screen/vision/shell/notes boundaries; configuration/loopback/auth; dictation privacy; deterministic eval interception/schema/grading; wake/backoff and PTT suppression; resource lifecycle; sensor routes/store; trace context, redaction and retired confirmation behavior. None is skipped or xfailed. Per-module tests and port notes are in MODULE-DECISIONS.json.

| Former unresolved module | Final decision | Actual basis |
| --- | --- | --- |
| tests/direct_responder_test.py | Required | Deterministic arithmetic/direct replies and malicious-expression refusal; no LLM/tool dispatch. |
| tests/vad_test.py | Required | Pure WAV packaging from supplied bytes; no microphone path. |
| tests/voice_pipeline_test.py | Required | Fake wake listener, patched TTS stop, bounded synthetic thread start/stop and timeout assertions. |
| tests/test_error_recovery.py | Required | Forced TTS import failure plus symbol/phrase checks; no real playback. |
| tests/test_boot_events.py | Required | Wait/provider/sound/TTS/HUD/voice and sleeps mocked; checks event shape/report/no-client behavior. |
| tests/test_boot_integration.py | Required | HTTP, Popen, sound, TTS and sleeps intercepted; offline timeout and missing-HUD cases retained. |
| tests/sounds_test.py | Unsafe exclusion | SoundsManager.play starts an audio thread reaching pygame. No playback was attempted. |
| tests/test_restic_scripts.py | Out of scope | Backup administration source/shell environment guard, unrelated to runtime reconciliation. No backup script, provider, repository or password-file operation was executed. |

Of38 old out-of-scope modules,37 remain outside qualification with path-specific feature/call review. The exception is tests/test_switch_models.py: it copies/reads/writes repository config.yaml and executes switch_models.py, so it is explicitly unsafe for read-only acceptance rather than assumed safely out of scope. The eight original unsafe modules remain excluded: boot_test, ollama_test, pipeline_test, router_test, safety_test, stt_test, tts_test, wake_word_test. They contain legacy provider/audio/runtime paths without complete interception. hardware_smoke_test and sounds_test are additionally unsafe. No excluded module is executed to discover whether it is safe.

The final partition is67 required +17 support +2 negative fixtures +39 out-of-scope +11 unsafe =136 Python files. Required module membership must equal the union of positive-suite node modules. Content hash/module-set changes, a declassified required module, changed manifests, added modules and substituted/dropped identities refuse acceptance. Coverage module selection itself is source-pinned, preventing accidental selection of an excluded module. Four earlier module-policy CLI cases remain represented within the expanded11-contract matrix.

Ports are limited to six files:

- test_dictation and test_config_check: change stale enabled defaults to the explicitly reviewed false opt-in contract; retain all credential/remote/CORS and clipboard/type-out/privacy negatives.
- test_obsidian_tool: absolute tmp_path vault matches project-relative application path resolution; CRUD and traversal/MCP-stub assertions retained.
- test_sensor_endpoints and test_phase3_integration: explicitly admitted disposable Authority and synthetic Bearer. Closed chat tools assert disabled response AND no mocked call, preserving401/closed-executor boundaries rather than reopening them.
- test_tracing: keep secret-value redaction through real trace_span, while registry execution must raise and never call the injected effect. Retired confirmation now tests404/no execution/no confirmed event instead of requiring a removed positive execution path. The old callable remains absent.

All669 previous node IDs are preserved. The217 new identities are separately collected and reviewed, then promoted manually with matching loader digests. The maintenance proposal command produces a NEW candidate only; it never promotes a policy, changes authority during acceptance, or turns incomplete collection into fewer requirements. Further changes require a reviewed module safety decision, explicit node/source diff, updated separate digests, adversarial tests and independent review. Exclusions are bounded coverage decisions, not a claim of whole-repository PASS.
