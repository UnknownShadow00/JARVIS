# V2 current state (read-only readback, 2026-10-15T19:14:30Z)

The readback tool is `evidence/v2_readonly_state.py`, with output in `evidence/v2-current-state-readback.json`. It ran with an audit hook that refuses every file write, every socket and any open under `~/.config/jarvis`. Credential files were only `lstat`ed, never opened. SQLite was opened `mode=ro` with `query_only`. HTTP/WS probes: 0. Provider requests: 0.

Gate 6F's own `tools/post-state.py` was deliberately **not** run, because it writes a new file into the sealed Gate 6F `readbacks/` directory.

| Item | Observed | Expected / note |
|---|---|---|
| Host / boot | `jarvis`, boot `2486e474…` (since 03:42:45Z) | — |
| `jarvis.service` | `inactive/dead`, Result=success, ExecMainStatus=0 | stopped |
| MainPID / InvocationID | 0 / empty | historical 594042 / `103e420f…` are gone |
| NRestarts / Restart | 0 / `no` | unchanged |
| Autostart | `disabled`, NeedDaemonReload=no | unchanged |
| Started in current boot? | No (no user-journal entries for `jarvis.service` in boot 0; nothing on :8000; no app python process) | — |
| Source HEAD | `bd53dbc799fb9284a21fae8cce3f5d9539e31141` | match |
| Installed source vs Gate 4 hashes | 0 mismatches | match |
| `config.yaml` SHA256 | `00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c` | match |
| Credential metadata | matches Gate 4 | match |
| D09 epoch | `606a991a06b74fd79ed72b308417cc3f`, **CLOSED_COMPLETE**, input_complete=1 | terminal |
| D09 integrity | quick_check ok, journal_mode=delete, no stray `-journal` | — |
| Accepted attempts | **0** (attempts, attempt_events, submissions, receipt_joins, resolutions, refusals all 0) | — |
| pilot_events | exactly 1: `OPERATOR_STOP` (attempt NULL) | see `OPERATOR-STOP-SEMANTICS.md` |
| pilot_context | PILOT, Granite profile `jarvis.p7.ollama.granite41.b1r2.v1`, accepted_limit 4 | unchanged |
| Pilot admissions | **CLOSED** (process not running; a restart would refuse `PILOT_EPOCH_ALREADY_EXISTS`) | — |
| D04 | namespace absent, 0 observations, **0 receipts** | — |
| D06 | `{"version":1,"current":null,"last":null}` | clean, no remote unknown |
| Backups | Gate 4 baseline `5244a125…` (7 files) and startup `9315a199…` (5 files): manifests and components valid | — |
| Terminal backup `62f417a2…` | created 03:42:17.732Z during shutdown; manifest `1b59208c…`; 5/5 components valid; associations: epoch CLOSED_COMPLETE, 0 attempts, 0 receipts, d06_current None | **not separately verified by Gate 6F** (listed only) |
| Live D09 vs terminal backup | logically identical (all tables, schema and user_version). File bytes differ, as the SQLite backup API makes expected | — |
| Audit since Gate 4 boundary | server_start 10-09T21:25:32Z, ws_connect/ws_disconnect 10-10T19:27:29Z, **server_stop 10-15T03:42:17.597Z**; no rotation | — |

Entry-vs-exit: every field Gate 6F recorded at 18:37Z and 18:58Z is unchanged in this readback.
