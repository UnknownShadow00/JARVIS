# Human-private Gate 5 procedure

**Prepared and offline-qualified. Live human authentication tests have NOT been executed. Gate 5 remains PARTIAL.**

This procedure is for the human operator in the separate private Core terminal. Codex must not execute HUMAN-ONLY-GATE5-AUTH.py against the real credential. Do not use a Codex terminal/tool, shared screen recording, HTTP debugger, shell tracing, PWA/Electron client or script recorder for the private run. No token is typed, pasted, exported or placed on a command line.

## Review and preflight

1. In the private Proxmox-to-Core SSH management session, confirm `hostname` is `jarvis` and `id -un` is `jarvis`. The management path is .50 → .162; it is not evidence of an out-of-band console. Keep the existing session connected. Do not alter SSH, networking or services.
2. Run `set +x` if shell tracing is enabled. Read the source locally with:

```sh
less /home/jarvis/JARVIS/tasks/p7-b2-gate5-human-auth-handoff/HUMAN-ONLY-GATE5-AUTH.py
less /home/jarvis/JARVIS/tasks/p7-b2-gate5-human-auth-handoff/READ-ONLY-PREFLIGHT.py
```

3. Verify the source hashes before execution:

```sh
sha256sum /home/jarvis/JARVIS/tasks/p7-b2-gate5-human-auth-handoff/HUMAN-ONLY-GATE5-AUTH.py /home/jarvis/JARVIS/tasks/p7-b2-gate5-human-auth-handoff/READ-ONLY-PREFLIGHT.py
```

Expected auth utility: `437276dda518b6e5f7196d38c1399fbe53df47a40aa0ac79065546f05070ee51`.

Expected read-only preflight: `cd836ec3c9df91892365c09b5dfc19e8b64755f032a82f3b112cc1fae07f218b`.

4. Run the separate, nonsecret read-only preflight:

```sh
/usr/bin/python3 -I -S -B /home/jarvis/JARVIS/tasks/p7-b2-gate5-human-auth-handoff/READ-ONLY-PREFLIGHT.py
```

Proceed ONLY if it prints PREFLIGHT=PASS and the expected PID 594042, unchanged invocation 103e420f4f334237a96654048a3edaf4, restarts 0, source-bound CLOSED admission, epoch 606a991a06b74fd79ed72b308417cc3f, authentication-abort records 0, attempts/submissions/D04 0, D06 IDLE and backup PASS. It verifies HEAD bd53dbc799fb9284a21fae8cce3f5d9539e31141, config SHA256 00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c, source inventory, unit/drop-in hashes, no pending daemon reload, disabled autostart, startup checkpoint components and read-only controller state. CLOSED is established by immutable reviewed source plus continuity; it is not a process-memory read. D09 epoch OPEN does not mean admission OPEN.

A refusal means STOP. Do not restart, change permissions/configuration, edit pins, replace the credential or retry authentication to force a pass. Ask for review of the nonsecret discrepancy. This preflight is not post-probe verification.

## Human-only execution — once

After reviewing and passing preflight, the HUMAN runs this exact command privately:

```sh
/usr/bin/python3 -I -S -B /home/jarvis/JARVIS/tasks/p7-b2-gate5-human-auth-handoff/HUMAN-ONLY-GATE5-AUTH.py
```

At the static acknowledgement prompt type only:

```text
RUN GATE5 NO-MESSAGE CHECKS
```

The helper requires an interactive Core terminal and the reviewed UID. It then checks directory/file metadata and identity pins before privately reading the existing credential. It accepts one bare or simply quoted JARVIS_API_TOKEN assignment (32–512 ASCII Bearer characters; optional final LF). More general systemd env syntax is deliberately refused locally. File contents were not inspected by Codex, so parse compatibility remains for this private run. Do not change the file or reveal it on refusal.

It sends once GET http://127.0.0.1:8000/gate5-auth-inspection with a Bearer header, requiring404. Only after that succeeds does it send once the /ws upgrade request with the same header, validate101 and Sec-WebSocket-Accept, send one masked close 1000 frame and require a normal close echo. ZERO application frames, automatic pings, redirects, retries, reconnects, proxies or external hosts. Each network stage has a five-second total deadline. No provider/model/tool operation or unlock exists in the utility.

Expected successful status:

```text
REST=PASS_404 WS=PASS_101_CLOSE_1000
```

An unexpected interruption after checks begin is reported as `REST=UNKNOWN WS=UNKNOWN LOCAL=REFUSED`; it is never reported as proof that no requests occurred. Possible other failures: `REST=FAIL WS=NOT_RUN`, `REST=PASS_404 WS=FAIL`, or `REST=NOT_RUN WS=NOT_RUN LOCAL=REFUSED`. STOP on any unexpected result; do not repeat the utility or substitute credentials. A failed/timeout stage may already have reached the server, and wrong authentication can terminally abort the pilot. Preserve only the fixed status and approximate UTC time. Do not collect headers, exception dumps, token hashes or credential contents. The utility cannot prevent a human from manually launching it a second time; the one-run instruction is mandatory.

## After the private run

Tell Codex only that you personally ran it, the sanitized status line and UTC time. Then request the separate POST-PROBE-READBACK.md checklist. Codex must obtain fresh independent PID/invocation/epoch, zero-count, D06, checkpoint and minimized audit evidence AFTER this confirmation and seal a new supplemental bundle. Do not relabel preparation observations as post-probe evidence or alter existing seals.

| Stage | Current status |
| --- | --- |
| Utility prepared | Yes |
| Source reviewed / offline qualified | Yes, 135 tests passed |
| Human live tests pending | Yes |
| Human live tests actually executed | No |
| Gate 5 independently verified | No; positive statuses alone are insufficient |

The separate AI-host SSH trust question is documented in AI-HOST-KEY-VERIFICATION.md. The helper does not contact that host. Gate6, pilot opening, measurement and formal P7 exit remain unauthorized/incomplete.
