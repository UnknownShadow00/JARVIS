# What V2's `OPERATOR_STOP` actually means

Source read from production `/home/jarvis/JARVIS` at `bd53dbc7` (read-only).

## Code path

- `app/server.py:117-148` `lifespan`. In the `finally` of the ASGI lifespan, it calls `_shadow_runtime.stop_admissions()` with **no argument**, then `await _shadow_runtime.close()`. This runs on **every** orderly ASGI shutdown: SIGTERM from systemd, `systemctl --user stop`, a guest power-off, or Ctrl-C.
- `app/execution/shadow_pilot.py:459` `stop_admissions(self, reason='OPERATOR_STOP')`. The default reason is `OPERATOR_STOP`.
- `app/execution/shadow_pilot.py:237`. The driver records `stop_reason='OPERATOR_STOP'` when input was complete (otherwise `CONTROLLER_FAILURE`).
- `app/execution/shadow_pilot.py:491` `install_core_stop`. The only deliberate-operator path (SIGUSR1 to MainPID) calls the **same** `stop_admissions` with the **same** default. It is indistinguishable in the record.
- `app/execution/shadow_controller.py:317-319` `close_epoch`. On close, OPEN becomes CLOSED_COMPLETE when the reconciled summary is complete. With 0 attempts it is complete.
- The `pilot_events` table has `(position, attempt, code)` and **no timestamp and no actor**.

## Separating the five things

| Question | Answer | Basis |
|---|---|---|
| Actual shutdown mechanism | Guest ACPI power-off. systemd stopped the user manager, which sent SIGTERM to `jarvis.service`, which ran the lifespan `finally`, which called `stop_admissions()` with the default | Core journal plus source |
| Actual operator intention | **Unknown.** The operator neither confirms nor denies rebooting Core. Nothing shows an intention to retire the B2 pilot | operator statement; no retirement record |
| Recorded V2 event code | `OPERATOR_STOP` (one row) | D09 |
| Durable terminal epoch state | `CLOSED_COMPLETE`, zero use. **This is truthful**: the epoch closed, and with 0 attempts the accounting is complete | D09, terminal backup |
| Authorization for a V3 successor | **None exists.** It cannot be inferred from the label or from the terminal state | — |

**Conclusion:** `OPERATOR_STOP` here means "orderly process shutdown". It is a **misleading label, not a false record**. The epoch state is truthful. The event name overstates what is known about intent. The historical row is not rewritten, and no replacement retirement record is created.

**Attribution of the historical V2 `OPERATOR_STOP`:** attributable to a *mechanism* (orderly SIGTERM during the guest power-off at 03:42:17Z), not to a *person* or a *decision*.
