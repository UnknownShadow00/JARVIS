# Existing trace and P1 correlation differ

`app/observability/tracing.py:120-139` creates `str(uuid.uuid4())` for each `start_trace`, normally a hyphenated 36-character UUID. `app/execution/correlation.py:44-64` mints 32-character UUID hex IDs; `binding_projection.py:58-65` demands well-formed P1 IDs. `tasks/task13b11c/SCHEMA_V3.md:23-24` says audit `trace_id` carries the turn ID, and `correlation.py:56-62` allows an adapter to carry an active trace ID, but no existing adapter or exact format conversion is assigned.

The server also uses a separate short legacy confirmation `request_id`, which is neither P1 turn nor trace. **CORRELATION ASSOCIATION DECISION REQUIRED:** freeze whether tracing adopts the P1 turn ID at trace creation, an existing trace is normalized into P1 format with a proved one-to-one mapping, or the two IDs remain separate and explicitly joined. Do not silently alias them. Client/provider IDs remain observational only.
