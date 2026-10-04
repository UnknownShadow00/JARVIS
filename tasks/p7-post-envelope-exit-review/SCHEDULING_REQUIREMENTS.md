# Scheduling requirements — no mechanism selected

Existing server REST/WS handlers and _process/_process_stream are async, but classification and some legacy calls are synchronous. WS waits for token streaming/TTS before sending its reply; REST returns only after _process. asyncio.create_task and to_thread exist elsewhere (startup, graph calls, emotion broadcast), but no canonical shadow scheduler exists. 13B11A says runs in parallel; it does not fix an asyncio task, thread, queue, worker or post-response hook.

Required: shadow failure/result cannot change legacy text, routing, stream order, cancellation, confirmation, tool behavior or resource wake/sleep. Capture one immutable request-time snapshot before deferred evaluation. Bound memory and work, count admitted/dropped/failed observations truthfully, prevent cross-session leaks, and preserve shutdown/rollback behavior. Scheduling must not accidentally inherit a mutable global cancel token or read a stale tracing context instead of the captured trace association. No numeric timeouts, capacities or latency SLO are selected.

| Option for later decision | Benefit | Required proof/tradeoff |
|---|---|---|
| response-completion-triggered in-process work | legacy response ready before evaluation begins | REST/WS completion differs; tasks still consume event-loop/CPU/memory and need cancellation/lifetime rules |
| bounded background queue/worker | can isolate overload and account for drops | infrastructure/ownership, immutable transfer, restart semantics and resource budgets need approval |
| bounded synchronous pure evaluation | simpler causality | directly adds response latency and contends on event loop; incompatible with a strict latency interpretation of unchanged behavior without explicit acceptance |

Recommendation: decide post-response versus bounded worker after measuring safe baseline architecture costs; no task/thread/queue is chosen now. Async syntax alone proves no latency isolation. Future live-model work additionally needs model resource ownership; merely moving it to a task does not prevent shared-model unload conflicts.
