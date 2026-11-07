# Current implementation defect and historical resolutions

No vulnerability severity is assigned to these mechanics. P2 is repair order. The final captured source fixes or gates all six earlier reproduced call-site defects; it retains one sibling cleanup defect.

## D7 — Binary frame leaves a stale /ue5 entry (P2)

Source: [app/server.py:529](snapshot-packaged/app/server.py#L529), [app/server.py:540](snapshot-packaged/app/server.py#L540), [app/server.py:541](snapshot-packaged/app/server.py#L541), [app/comms/ue5_bridge.py:23](snapshot-packaged/app/comms/ue5_bridge.py#L23).

Observed: One credentialed in-memory /ue5 session sent the single binary byte 0x78. receive_text raised KeyError and the manager retained one entry after session exit. A normal disconnect retained zero. No lifespan, real socket, browser, other UID, connection flood or shared-service outage was tested.

Scope: Per-session input/cleanup reliability defect. No unauthorized data access, authentication bypass, privilege gain or shared-service denial was demonstrated. Later broadcasts can remove dead connections.

Latest [retained result](agents/hunt-packaged-safety/artifacts/ue5_binary_cleanup.txt). Reproduce from this audit directory under the bounded runner:

```sh
cp agents/hunt-packaged-safety/scratch/ue5_binary_cleanup.py agents/hunt-packaged-safety/scratch/repro_ue5_1.py
python3 sandbox-runner.py hunt-packaged-safety agents/hunt-packaged-safety/scratch/repro_ue5_1.py snapshot-packaged
```

Use a fresh basename for every replay; exclusive promotion refuses overwrite. The fixture clears only its isolated in-memory manager and uses a dummy token.

Fix: Validate the accepted frame type and always disconnect in finally, including unexpected exceptions and cancellation. Apply explicit connection/send/size limits.

Regression: Send one binary frame and cancel one accepted session; assert a defined close/error and no retained entry after each.

## Historical observations — not current exposed effects

| ID | Earlier reproduced mechanics | Final captured disposition |
|---|---|---|
| D1 | Confirmation invokes dummy effect after emergency stop | Gated: confirmation route removed; every registry/server invocation refuses real effects |
| D2 | Narration failure duplicates a note append | Gated: first tool effect is refused in normal and streaming/fallback dispatch |
| D3 | Generic argv marker selects an unrelated same-UID child for termination | Fixed: signals require in-process child lease plus PID/creation-time/executable/cwd/ppid checks |
| D4 | Continuous positive speech exceeds configured recording cap | Fixed: frame/deadline/cancel guards apply before every branch; callback/wake queues are bounded |
| D5 | Malformed /ws messages leave manager entries | Fixed for /ws: input shape/size validation and finally cleanup; /ue5 D7 remains separate |
| D6 | CLI POST omits configured credential and HTTP failures trigger local fallback | Fixed: Bearer is sent; HTTP/ambiguous outcomes refuse fallback; local control requires explicit offline intent |

Original native inputs, conditions, artifacts and precise fixes are preserved in [historical-defects.json](historical-defects.json) and [superseded report](reports-before-latest/IMPLEMENTATION-DEFECTS.md). These records describe their exact older captures. Latest controls have [six-group denial evidence](agents/hunt-latest-safety/artifacts/latest_safety.txt) and [eight packaged regression cases](agents/hunt-packaged-safety/artifacts/packaged_safety_tests.txt). No application fix was made by this audit; the concurrent implementation changed these files and was independently re-reviewed.
