# Offline security qualification

Final command in the guarded private canonical copy:

```text
pytest tasks/p7-b2-gate5-human-auth-handoff/test_human_auth.py tests/execution/shadow_pilot_safety_test.py tests/test_server_auth.py -q
```

**135 passed, 0 failed, 2 existing deprecation warnings, 1.18 seconds.** Warnings concern Starlette/httpx and anyio. Source SHA256 of the qualified utility: `437276dda518b6e5f7196d38c1399fbe53df47a40aa0ac79065546f05070ee51`.

The inherited reviewed runner copies canonical application/tests plus the new helper/tests into a private temporary tree. Only the copy receives committed baseline config, as required by legacy-auth tests; the real PILOT fixture explicitly configures a private closed runtime. Existing Core dependencies were used; nothing was installed. The test import does not run main. The real private loader is replaced by a refusal sentinel except a dedicated dummy-root test, whose os.open wrapper redirects every component into an isolated tree and rejects any other path.

Audit guard: blocked credential access0; blocked production-runtime access0; blocked external writes0; blocked INET/DNS0; unapproved execution0; approved subprocess children0. Network history is empty. Fake peers use AF_UNIX socketpairs; the installed Uvicorn wire test uses a temporary private AF_UNIX listener. Helper calls still request literal127.0.0.1:8000, captured by the test adapter and mapped ONLY to the private Unix peer. No real TCP listener at8000 and no external traffic.

Coverage: exact one REST request, correct/wrong dummy Bearer, REST failure preventing WS, statuses200/301/302/307/308/401/403/423/500 rejected, no redirect/retry/proxy/DNS, fixed destination, no body/query credential, successful101 proof, one masked close 1000 and no application/pong/reconnect frames, invalid accept/extension/duplicate header/close/data/ping refusal, EOF/oversize/malformed response, explicit timeout and cumulative slow-drip deadline, sanitized exceptions containing dummy secrets, safe quoted/bare env parsing, malformed/oversize/non-ASCII/injected input, symlink/hardlink/FIFO/directory/mode/UID/GID/xattr/race/substitution refusal, complete dummy-root loader, interactive-host/argument/acknowledgement refusal, and status-only main output.

Actual deployed ASGI fixture proves positive404 and authenticated WS connect/close leave CLOSED admission, no abort, D06 unchanged, zero accepted attempts/events/submissions/receipt joins/pilot events, no D04 file, and zero fake model/legacy/voice calls. Wrong dummy auth then produces401 and AUTHENTICATION_MISMATCH. Existing tests cover WS negative auth, ingress/lifecycle/worker refusal and restart-closed behavior. No real tool execution, Ollama traffic or production runtime mutation occurred.

Preserved run history: qualification-1 was118 passed before identity-pin additions; qualification-2 was132 passed/1 failed because the dummy root inherited group-write permissions; fixture permissions were corrected to model real root/home. qualification-3 was133 passed. The final added installed-Uvicorn wire test brought the count to134. No production source/configuration was changed. Results are iterations, not additive test counts.

Limitations: real token bytes/format and live authenticated status remain deliberately untested. Standard-library Python does not guarantee erasure of immutable memory copies; there is no persisted secret or dump output. Tests cannot prove future endpoint integrity, privileged-host integrity or absence of a malicious debugger. Preflight, private execution and independent post-probe readback remain mandatory.

Final source review added UNKNOWN status for an interruption between network stages, preventing a false NOT_RUN claim. The final reviewed suite adds this case (135 total); the prior 134-case pass is retained separately.
