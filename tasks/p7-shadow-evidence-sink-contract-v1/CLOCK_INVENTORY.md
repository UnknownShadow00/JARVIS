# Actual canonical clock owners

| Source at production d3f44e01 | Owner and suitability |
|---|---|
| execution/correlation.py:103–106 | P1 utc_now helper, aware UTC; selected without audit/P2 writes |
| execution/provenance.py:221 | Uses the same helper as default record timestamp; reuse does not promote evidence |
| execution/audit_events.py:486 | aware record timestamp .isoformat serialization; convention only, no emitter reuse |
| observability/tracing.py:242 | Direct UTC, millisecond Z; trace durations/rotation are separate, not sink latency/source |
| logs/audit.py:49 | Direct UTC ISO at queue submission; operational queue semantics unsuitable for durable shadow ack |
| execution/dispatch.py:410,470,792 | Injected operational clock; do not import dispatcher or use execution lifecycle |
| agent/task_queue.py:22; scheduler.py:149; sensor_store.py:15 | Domain direct UTC timestamps, not generic authority wrapper |
| resource_manager.py:492; memory/graphiti_client.py:116 | Domain state/reference UTC; no resource/provider calls authorized |
| boot.py:218; brain/morning_report.py:14 | Local naive datetime, unsuitable for UTC evidence |
| server.py:155,302 | time.time for uptime, not persistence chronology |

No generic clock class/module was found by a full tracked app/docs/scripts clock scan. The existing suitable public P1 helper is sufficient; no new clock wrapper, host-locale rule or infrastructure selection needed.
