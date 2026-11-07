# JARVIS Local Observability

JARVIS assigns one random UUID4 `trace_id` to each logical chat, WebSocket message, voice request, evaluation scenario, or confirmation continuation. The ID contains no user data and is propagated with Python `ContextVar`s, so concurrent asynchronous requests retain isolated trace state.

Tracing is local-only. It does not send telemetry to another process or service.

## Storage and retention

Structured spans are appended as JSONL to:

```text
data/traces/spans.jsonl
```

Tracing uses the existing `openjarvis.trace_logging_enabled` and `openjarvis.traces_dir` settings. The active file rotates at `logging.max_log_size_mb`; three numbered backups are retained beside it. With the default 100 MB setting, local trace storage is bounded to approximately 400 MB. Restic includes durable `data/` state, including these traces, so the bounded rotation also limits backup growth.

Privileged and operational audit events continue to use:

```text
logs/audit.jsonl
```

Historical audit rows remain unchanged. New audit rows use schema version 2 and include `trace_id` only when an active trace exists. Callers outside a request context remain supported.

## Span schema

Every span record contains:

- `schema_version`: currently `1`.
- `timestamp`: UTC ISO-8601 timestamp.
- `trace_id`: UUID4 for the logical request.
- `span_id`: UUID4 for this span or event.
- `parent_span_id`: enclosing span ID, or `null` for a request root.
- `stage`: stable pipeline stage.
- `event`: `start`, `end`, or `event`.
- `component`: emitting subsystem.
- `status`: `started`, `ok`, `error`, `required`, `confirmed`, or `dry_run` as applicable.
- `duration_ms`: non-negative elapsed time; untimed events use `0.0`.

Optional safe metadata fields are:

```text
tool
capability
model
origin
safety_level
confirmation_required
parameter_keys
request_id
streaming
message_count
transport
error_type
```

## Current stages

| Stage | Meaning |
|---|---|
| `request` | Complete logical HTTP, WebSocket, voice, evaluation, or confirmation request |
| `router` | Current intent routing, including deterministic rules |
| `planner` | Current complexity/model-path decision when an LLM response is needed |
| `llm` | Router-model or response-model invocation; streams end after consumption |
| `tool_parameters` | Tool parameter construction |
| `safety` | Tool safety-level and confirmation-policy evaluation |
| `confirmation` | Confirmation required or confirmed correlation event |
| `tool` | Dry-run event or actual tool execution |
| `response` | Final response cleanup/formatting |
| `stt` | Voice speech-to-text after wake audio is available |
| `tts` | Voice or WebSocket text-to-speech playback |

The continuous wake listener is not currently placed inside per-request traces because no logical request exists until audio is detected. Its existing audit events remain available.

## Audit correlation

The current trace context is added automatically to new audit rows. A confirmation retains the original trace ID in pending confirmation state so the initial safety decision and later approved tool execution can be queried together.

For a known trace ID:

```bash
grep '<trace_id>' data/traces/spans.jsonl
grep '<trace_id>' logs/audit.jsonl
```

The trace shows order and duration. The audit file preserves the existing privileged-action detail.

## Privacy

Span metadata uses an explicit allowlist. Traces deliberately do not record:

- API tokens, passwords, bearer headers, cookies, private keys, or Restic credentials;
- complete request headers, configurations, environment variables, or `.env` contents;
- full prompts or model responses;
- user message text;
- tool parameter values or exception messages.

Tool spans record only the tool/capability and sorted parameter key names. LLM spans record model and message count, not payload content. Failures record only the exception class in `error_type`.

The audit log retains its pre-existing payload semantics and should continue to be protected as durable sensitive operational data.

## Failure behavior

Trace persistence is fail-safe. Directory, permission, rotation, or write errors emit a warning through Python logging while the application operation and any unrelated exception behavior continue normally. Application exceptions are recorded with `status: error` and then re-raised unchanged.

## Evaluation and Hermes comparison

Golden evaluation reports include the generated `trace_id` and existing per-case wall-clock duration. Expected results and scenario IDs are never passed to production routing code.

Hermes must emit these stable stage names, or be bridged to them, so pre- and post-migration routing, model, safety, tool, and response timing remain directly comparable. A failed golden scenario remains evidence; observability must not change production decisions to improve its score.
