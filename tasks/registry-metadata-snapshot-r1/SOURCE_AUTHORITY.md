# Source authority and inventory

Canonical `app/tools/registry.py::_EXPLICIT_TOOL_MODULES` declares 17 fixed key/module-path pairs and also has dynamic discovery. `ToolRegistry.list_tools()` calls `_load_tool` and imports handler modules, so it is not a passive metadata API. `registry.call()` executes. The new module imports neither; it parses the reviewed registry source declaration as AST data. Duplicate keys/paths, nonliteral fields and unsupported shapes fail closed.

Selected exact declarations: `apps → app.tools.apps`, `browser → app.tools.browser`. Their handlers statically declare `SAFETY_LEVEL=0/1`, `execute(params)`, and the V1 field/action evidence. `apps.py::_APP_MAP` provides the 19 app-name keys; `browser.py` declares `ACTION_KEY=action`, `URL_KEY=url`, `OPEN_ACTION=open`. The snapshot exposes these metadata facts, not command arrays, handler functions or P4 capability identifiers. P4 and the closed F-MAP-01 table own the capability crosswalk.

Reviewed SHA256: registry `e70d4d50cc11395253648194a82506bb5a2a53be446f47bb7d00f7a720b99b41`; apps `faafc0f7712552a5392ed4c952560abd64fe098306fd01f89a9ab90d38f94407`; browser `7f1974d32a17ec0f88548b9c15c840786295c718b220cc065eea7b8bbe051d5a`.
