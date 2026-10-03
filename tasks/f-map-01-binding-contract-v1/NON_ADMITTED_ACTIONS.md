# Actions/capabilities not admitted in V1

| Examined action or capability | Reason | Frozen disposition |
|---|---|---|
| `DEPLOY` | P4 marks unavailable; no registered routed capability/handler; no invented deployment tool | no binding; existing P7/P6 unsupported/clarification path |
| `DELETE_PATH` | P4 `files.delete` is unregistered DENY; handler has no delete operation | no binding; existing refusal |
| `GET_DATABASE_STATUS` | P4 has no routable registered database-status capability | no binding; existing unavailable result |
| `NONE` | conversational/non-action outcome, not a tool action | no expected/query; zero proposal only |
| `UNKNOWN_ACTION` | unsupported or unavailable action | no tool substitution |
| `MULTI_ACTION_UNSUPPORTED` | distinct actions not merged or selected | no binding |
| `browser.search` / `web_search.search` | P4 rows exist, but P3 has no separate routable `PrimaryAction` and frozen action→capability pair for them | no model/registry-derived expansion |
| other registry keys and P4 rows | no complete P3 action→P4 capability→registry tool/target/argument chain in V1 | outside schema version 1 |

An OPEN_APP/OPEN_URL request whose metadata or target predicate fails is **not admitted for that turn** despite its action being a V1 row. This is fail-closed data, not a policy or router change. Future coverage requires a reviewed V2 mapping, not silent fallback to a handler or model choice.
