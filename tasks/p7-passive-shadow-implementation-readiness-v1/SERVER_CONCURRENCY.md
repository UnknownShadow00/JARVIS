# Independent server inventory — D07 not run

Pinned actual app/server.py:110 lifespan schedules startup checks with asyncio.create_task(asyncio.to_thread(...)), starts existing scheduler and idle monitor; finally stops idle monitor and TTS. This is not a lifecycle-managed shadow queue. app/resource_manager.py also owns a wake thread and idle task; neither owns shadow attempts.

REST chat:358–380 awaits _process after trace/wake setup. Frozen capture is before :370. WS:497–559 resolves input, wakes, sets trace, calls _process_stream at :527 then _process fallback at :529; capture once after :525/before :527. Chunks and fallback must reuse the same turn/envelope. _process:598 and _process_stream:840 contain synchronous work despite async declarations. Voice wrappers directly enter those helpers and remain deferred.

Existing REST try/finally resets trace without a shadow exception guard; WS handles disconnect and listening cleanup. A future shadow-only boundary must prevent exception/latency from changing response, stream or socket health. There is no canonical bounded shadow queue or numeric capacity, and existing 600s/retry legacy client behavior is not adopted. Execution style remains IMPLEMENTATION DECISION REQUIRED. No D07 freeze, mechanism or numerical policy is selected in this independent inventory.
