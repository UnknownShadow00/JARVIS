# Archived attempt import graph

Evidence/import-graph.json lists exact direct imports and transitive app edges from the archived draft and unchanged production dependencies. No confirmation.py, dispatch.py or registry node is reachable. Adapter import is one exact ImportFrom containing AdapterRequest, AdapterError, parse_recorded_response, without aliases. No provider/runtime/server dependency or live consumer was added.

P-B03/P-B04 isolation checks passed in the 733-test isolation run; the only failure was the canonicalizer whole-app gate. After restoration pipeline.py is absent, all attempted consumer relationships are gone, and baseline zero-importer invariants hold again. No final deployed-module graph is claimed.
