# Independent authorization-lifetime review v5

## Verdict

`PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY`

The lifetime split is internally consistent. Preparing a new session retains
the full-window requirement: the approval must remain valid for the 630-second
stop-by horizon plus 15 seconds. Native authorization for an existing timer
callback instead requires that the same reviewed approval be currently valid,
but does not incorrectly demand another full window at callback time.

The exact immutable approval hash is checked for start, worker, verify and
observe. Worker execution additionally binds the session nonce supplied in the
timer argv. These expectations are enforced inside the Engine's exact plan read
and FileStore generation binding, closing a retire/rearm race found during this
review. Cleanup and retirement retain distinct stopped-state, inactive-unit,
worker-idle and fresh-authorization gates.

The independent fixture confirms an 11-minute approval remains callback-valid
at minute 9, is insufficient to create a new session then, and is invalid at
minute 11. A disposable persistent-store test also confirms generation pinning
across an active-pointer swap and refusal while a phase-worker lock is held.
All host interfaces remained mocked under process-wide subprocess tripwires.

This does not prove wall-clock custody, scheduler timeliness, systemd behavior,
or host enforcement. A callback delayed beyond approval expiry still fails
closed, reinforcing that Policy A cannot guarantee expiration. No live
bootstrap or forced-stop authority is granted.
