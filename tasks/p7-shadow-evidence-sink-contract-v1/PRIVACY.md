# No content enrichment

Persist exactly the frozen observation record and minimal sink schema/version/order/UTC/integrity metadata. No raw user request, model/candidate text, tool argument maps, P2 values, credentials, headers, cookies, framework object or exception prose. Do not scrape extra context, call to_mapping on an input owner object with extra fields, or log a failed input for convenience.

IDs, trace associations and existing binding fingerprints can be linkable or sensitive; this is observational conformance evidence with private local access, not public/anonymous telemetry. UTC chronology adds association potential; it is the approved minimum chronology fact. Fixed failure codes avoid exception/path/content leakage. No network/provider logging or operational audit/provenance fallback. P7 no-prune retention is explicitly temporary in policy scope; post-P7 privacy/cleanup decisions remain open. No raw CT text requirement is silently solved by the sink.
