# Reproduced implementation defects

These are observed safety, integrity, cleanup and coordination defects. Their security gate did not establish lower-trust authority gain or demonstrated shared-service damage, so no vulnerability severity is assigned. P1/P2 below are remediation priorities. Source paths for these behaviours are hash-identical between their recorded fixture capture and snapshot-expanded.

## D1 — Queued confirmation executes while emergency stop remains active (P1)

Source: `app/server.py:751; app/brain/kill_switch.py:28`.

Observed: A genuine pending Level 2 confirmation was created with a dummy tool. After kill_switch.trigger, active remained false; credentialed POST confirmation returned 200 and invoked the dummy sink once. No shell ran.

Scope: The same authenticated operator later confirmed the action; no separate approver role or lower-trust privilege gain was established. Stock HTTP startup was not exercised.

Evidence: [agents/hunt-legacy/artifacts/legacy_effects.txt](agents/hunt-legacy/artifacts/legacy_effects.txt). Run from this audit directory through the bounded runner:

```sh
cp agents/hunt-legacy/scratch/legacy_effects.py agents/hunt-legacy/scratch/repro_D1.py
python3 sandbox-runner.py hunt-legacy agents/hunt-legacy/scratch/repro_D1.py snapshot
```

The shown repro stem is new. Choose another fresh stem on subsequent replays because evidence promotion is exclusive and refuses overwrite. The existing artifacts already preserve the recorded run. All fixture state is synthetic and scratch-local.

Fix: Enforce emergency-stop/revocation state at the common ToolRegistry dispatch boundary, invalidate pending approvals on stop, and bind each pending item to a short lifetime and revocation epoch. confirmed=True must satisfy the stop gate.

Regression: Create pending dummy action, trigger stop, confirm it and assert zero dummy effects; repeat through native and HTTP dispatch.

## D2 — Streaming failure repeats an already completed tool effect (P2)

Source: `app/server.py:818; app/server.py:835; app/server.py:487; app/voice/audio_stream.py:96`.

Observed: One note_append input wrote one marker before a mocked Ollama failure. The exact stream-then-normal fallback wrote a second marker to the scratch-only note.

Scope: Demonstrated integrity/retry defect is a Level 1 local note append in balanced mode. Level 2 confirmation gates were not bypassed; no arbitrary command replay was demonstrated.

Evidence: [agents/hunt-legacy/artifacts/legacy_effects.txt](agents/hunt-legacy/artifacts/legacy_effects.txt). Run from this audit directory through the bounded runner:

```sh
cp agents/hunt-legacy/scratch/legacy_effects.py agents/hunt-legacy/scratch/repro_D2.py
python3 sandbox-runner.py hunt-legacy agents/hunt-legacy/scratch/repro_D2.py snapshot
```

The shown repro stem is new. Choose another fresh stem on subsequent replays because evidence promotion is exclusive and refuses overwrite. The existing artifacts already preserve the recorded run. All fixture state is synthetic and scratch-local.

Fix: Return a distinct already-executed/tool-result state from _process_stream. Reuse that result when narration fails rather than redispatching the tool. Preserve one logical operation identity across retry/fallback.

Regression: Make narration fail after a dummy append, enter fallback and assert one append with both WebSocket and voice callers.

## D3 — Shutdown selects and terminates an unrelated same-UID process (P1)

Source: `app/cli.py:65; app/cli.py:186; app/resource_manager.py:752; app/resource_manager.py:789`.

Observed: One harmless child outside the project, with inert app.main:app argv, was classified fastapi_server and terminated by genuine discovery/termination helpers. Every other PID was excluded inside the isolated PID namespace.

Scope: This violates the CLI JARVIS-owned resource scope. The operator already controlled the same-UID child; no lower-trust authority gain, arbitrary PID selection or remote privilege escalation was established.

Evidence: [agents/hunt-process/artifacts/process_selection.txt](agents/hunt-process/artifacts/process_selection.txt). Run from this audit directory through the bounded runner:

```sh
cp agents/hunt-process/scratch/process_selection.py agents/hunt-process/scratch/repro_D3.py
python3 sandbox-runner.py hunt-process agents/hunt-process/scratch/repro_D3.py snapshot
```

The shown repro stem is new. Choose another fresh stem on subsequent replays because evidence promotion is exclusive and refuses overwrite. The existing artifacts already preserve the recorded run. All fixture state is synthetic and scratch-local.

Fix: Track processes actually launched by JARVIS with PID plus creation time and verified executable/project provenance, and revalidate immediately before signalling. Reject a generic command-line marker as sufficient ownership.

Regression: Run one owned dummy child and one unrelated same-entrypoint dummy child; shutdown must stop only the tracked owned child and tolerate PID reuse.

## D4 — Continuous speech bypasses recording frame cap (P2)

Source: `app/voice/vad.py:42; app/voice/vad.py:69; app/voice/vad.py:85`.

Observed: A finite fake stream supplied 41 speech frames and 1 silence frame. The genuine recorder returned 42 frames (1.26s encoded audio) against a configured 20-frame / 0.6 s cap, using 40,364 WAV bytes. This is encoded duration, not wall time.

Scope: The fixture establishes cap failure and source shows unbounded callback queues/weak active-recording cancellation. It does not establish a shared-service outage or physical audio attack.

Evidence: [agents/hunt-voice/artifacts/vad_bounds.txt](agents/hunt-voice/artifacts/vad_bounds.txt). Run from this audit directory through the bounded runner:

```sh
cp agents/hunt-voice/scratch/vad_bounds.py agents/hunt-voice/scratch/repro_D4.py
python3 sandbox-runner.py hunt-voice agents/hunt-voice/scratch/repro_D4.py snapshot
```

The shown repro stem is new. Choose another fresh stem on subsequent replays because evidence promotion is exclusive and refuses overwrite. The existing artifacts already preserve the recorded run. All fixture state is synthetic and scratch-local.

Fix: Check absolute monotonic deadline, frame budget and cancellation on every iteration before the speech continue; bound callback queues and avoid retaining an outer wake-listener backlog during nested capture.

Regression: Use finite continuous-positive VAD input exceeding a small cap and assert recording ends at the cap; cancel during active capture and assert prompt exit with bounded queues.

## D5 — Malformed accepted WebSocket sessions retain manager entries (P2)

Source: `app/server.py:465; app/server.py:517`.

Observed: Three in-memory credentialed sessions: [] raised AttributeError and retained 1 entry; a nonstring message raised TypeError and retained 1; normal disconnect retained 0.

Scope: This proves per-session parsing/cleanup defects. No connection flood, shared-service denial or authentication bypass was demonstrated; normal later broadcast may remove dead sockets.

Evidence: [agents/hunt-ws/artifacts/ws_cleanup.txt](agents/hunt-ws/artifacts/ws_cleanup.txt). Run from this audit directory through the bounded runner:

```sh
cp agents/hunt-ws/scratch/ws_cleanup.py agents/hunt-ws/scratch/repro_D5.py
python3 sandbox-runner.py hunt-ws agents/hunt-ws/scratch/repro_D5.py snapshot
```

The shown repro stem is new. Choose another fresh stem on subsequent replays because evidence promotion is exclusive and refuses overwrite. The existing artifacts already preserve the recorded run. All fixture state is synthetic and scratch-local.

Fix: Validate incoming object/message type and size before processing. Always remove the connection in finally for disconnect, malformed input, exception and cancellation; add explicit connection/send limits.

Regression: Submit nonobject/nonstring JSON and cancel a session; assert a defined close/error and an empty manager after each session.

## D6 — CLI POST omits credential and treats HTTP failure as offline (P2)

Source: `app/cli.py:228; app/cli.py:132`.

Observed: A configured dummy token was present, but the mocked CLI POST had no Authorization header. Its mocked 401 led to the local light-sleep fallback.

Scope: The local same-UID operator is trusted, so this is not an HTTP authentication bypass. It can silently choose a different resource-control path than the active server.

Evidence: [agents/hunt-deploy/artifacts/deploy-controls.txt](agents/hunt-deploy/artifacts/deploy-controls.txt). Run from this audit directory through the bounded runner:

```sh
cp agents/hunt-deploy/scratch/deploy-controls.py agents/hunt-deploy/scratch/repro_D6.py
python3 sandbox-runner.py hunt-deploy agents/hunt-deploy/scratch/repro_D6.py snapshot
```

The shown repro stem is new. Choose another fresh stem on subsequent replays because evidence promotion is exclusive and refuses overwrite. The existing artifacts already preserve the recorded run. All fixture state is synthetic and scratch-local.

Fix: Use one authenticated GET/POST helper. Distinguish authentication/authorization failures from transport absence and require explicit handling before local fallback.

Regression: Verify Bearer on POST;401/403 must report failure without invoking the local resource manager, while genuine offline handling remains explicit.
