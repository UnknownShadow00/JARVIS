# Fresh focused offline checks

Canonical Core's existing Python environment ran an isolated source copy through the reviewed guarded runner, with no dependency installation. Selected paths:

```text
tasks/p7-b2-gate5-human-auth-handoff/test_human_auth.py
tests/test_server_auth.py
tests/test_model_ownership.py
tests/execution/shadow_pilot_safety_test.py
tests/execution/shadow_pilot_server_test.py
tests/execution/shadow_pilot_test.py
tests/execution/shadow_controller_test.py
tests/execution/shadow_pilot_backup_test.py
tests/execution/shadow_backup_recovery_test.py
```

Result: **477 passed, 0 failed, 2 existing deprecation warnings, 3.36s**. Warnings concern installed Starlette/httpx and AnyIO compatibility; no install was attempted. Coverage is focused behavioral qualification, not a newly measured whole-project coverage percentage.

The runner copied tracked source/tests and sealed helper tests, excluding production data/logs/.env. It used the committed config in the isolated copy to preserve legacy-test assumptions; explicit private PILOT fixtures exercise actual deployed ASGI paths and fake model transports. Production configuration remains exact and separately hash-bound. Per-file copied-source manifest, fixture config fingerprints, output and per-process guards are sealed in evidence.

Guard results: zero INET/DNS, real credential, production runtime, external write or unapproved execution attempts; three approved fixture subprocess invocations. Real wire tests used private AF_UNIX sockets, not port8000. The helper was only imported in the isolated copy; loader/main boundary tests replace privileged paths and transports with dummy fixtures. Neither canonical human helper nor preflight executable was launched, and no real token was loaded.

Historical full regression7166/11deselected/0fail, Golden12/20 and its eight known failures were not rerun. The historical model-capable legacy digest was not regenerated.
