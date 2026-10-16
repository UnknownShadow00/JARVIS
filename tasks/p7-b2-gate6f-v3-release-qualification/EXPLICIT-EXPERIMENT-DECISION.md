# Explicit experiment decision (for the operator)

Nothing is approved by inference. Each line needs an explicit APPROVE / REVISE / REJECT.

## Fixed (not open for change)

Four original inputs; 2 REST + 2 WS accepted conversations; 4 accepted attempts maximum, never refunded; legacy-only client replies; Granite observational with the frozen profile; no tools, voice, TTS, fallback, retries or measurement eligibility.

## Decisions

| # | Item | Gate 6F recommendation |
|---|---|---|
| X1 | Strict classifier refusal instead of original `confirm_action` on low confidence / parse error / Ollama error | APPROVE as a safety restriction (original path would produce a client-visible confirmation turn, outside a conversation-only pilot) |
| X2 | Deep branch unavailable (refusal) | APPROVE; none of the four inputs selects it |
| X3 | Memory: pinned snapshot of `skills.md` (`3a61af60…`, 1,877 B) vs original live read | APPROVE the pinned snapshot; REJECT the 6E empty snapshot (changes the experiment). Re-verify the production file hash immediately before any pilot |
| X4 | Normal responder `num_ctx` | REVISE to **8192** (source Modelfile value, G6F-LP-2), subject to attestation of the installed Modelfile; 32768 is not source-faithful |
| X5 | Trivial responder `num_ctx` 4096 | APPROVE only after the server default context is attested; otherwise REVISE to the attested value |
| X6 | Explicit `keep_alive: 60` on legacy operations (original sends none) | Operator choice: 60 bounds residency next to Granite but differs from original server policy; decide together with topology (A vs B/C) |
| X7 | Zero responder retries, whole-operation deadlines 20 s / 180 s | APPROVE as a safety restriction |
| X8 | Non-streaming WS responder (TTS off) | APPROVE; client sees one reply frame as before |
| X9 | Empty-reply and action/tool-proposal refusal | APPROVE |
| X10 | Resource topology | Require HUMAN_ATTESTED topology; if B/C, explicitly approve `SHARED_HOST_SERIAL_RESIDENCY_APPROVED` or provide separate hosts |
| X11 | Workload | 3 classifier + 4 responder + 4 Granite = 11 conditional operations, ≤1,500 s provider deadline time |

Approving these approves an **experiment contract for further qualification only**, not deployment, credentials, retirement or pilot opening.
