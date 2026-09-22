# Recorded response schema
Only serialized JSON is accepted. Canonical examples:
```json
{"text":"Untrusted draft","proposals":[]}
{"text":"","proposals":[{"tool_name":"apps","raw_arguments":{"application_name":"vs code"}}]}
```
Exact structural keys: root text/proposals; proposal tool_name/raw_arguments. All required. A JSON object in raw_arguments is the explicitly declared P0 open data namespace; arbitrary keys there are inert, except the forbidden reasoning names.
No transport envelope exists here; provider metadata is rejected at the root. No live wire protocol is frozen.
Full type/null/numeric/duplicate and metadata rules: HERMES_ADAPTER_CONTRACT_V1.md.

