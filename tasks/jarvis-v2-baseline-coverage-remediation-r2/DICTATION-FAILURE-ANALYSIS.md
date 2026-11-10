# Dictation default failure

Classification: stale test expectation following an intentional documented configuration contract change, not an application regression or unresolved design conflict.

The exact parent5c878448a sets VoiceConfig.dictation_enabled=False and its public example also false. RC1 REPORT.md and INTEGRATION-MATRIX.md explicitly retain safe offline opt-in defaults; reconciliation FIVE-FILE-COMPATIBILITY-MATRIX.md and its static example test reaffirm that decision. The adjacent dictation tests already require independent authorization: clipboard/type-out are refused even when dictation flags are true, and transcripts must not enter audit values.

Before any test edit, reproduce_dictation_before.py ran the unchanged test module/source in the existing networkless cage. dictation-before.json records0 pass/1 fail, complete failed call, exit1. The dedicated selection is test_dictation_config_defaults_present; it expected True from load_settings(), while the mounted public example correctly supplies False. initial.json separately records the same failure among205 passes/12 failures. Diagnostic runs retain the old reconciliation authority and therefore cannot be promoted to acceptance.

Smallest justified resolution: rename the default case to test_dictation_config_defaults_require_opt_in and assert False. Preserve the configured hotkey and False type-out checks, all existing clipboard/type-out/authorization/audit-redaction negatives, and the mocked dictation pipeline's no-LLM/no-TTS assertions. No product code, default, credential, live configuration or privacy requirement changed. The six dictation cases now pass within exact-node-pinned coverage. TEST-PORTS.json records the old/new function bodies.

Do not restore automatic dictation merely to satisfy an old assertion. Any future opt-in clipboard/typing adapter needs a separate independently authorized design; this remediation introduces none.
