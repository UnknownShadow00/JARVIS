# Exact argument schemas

| Registry key / action | Required keys and exact types | Allowed values | Optional keys | Unknown/missing handling | Canonicalization and comparison |
|---|---|---|---|---|---|
| `apps` / OPEN_APP | `action: str`, `app: str` | `action` exactly `"open"`; `app` satisfies `TARGET_SCHEMAS.md` | **none** | any missing or extra key: no V1 binding / proposal mismatch | raw map retains routed `app`; P3 V1 changes only declared VS Code aliases; compare complete map with exact scalar types |
| `browser` / OPEN_URL | `action: str`, `url: str` | `action` exactly `"open"`; `url` passes absolute HTTP(S) predicate | **none** | any missing or extra key: no V1 binding / proposal mismatch | P3 V1 has no browser rule; exact URL string retained; compare complete map |

The handlers accept a wider legacy shape (`apps` also reads `name`/`query` and defaults action; `browser` defaults action and also handles search). V1 deliberately **does not** admit those variants. This closed subset is supported by the actual handler fields while avoiding implicit defaults and unknown-key drops. Handler acceptance is not permission authority. All expected raw/canonical maps are JARVIS-owned and immutable; a model argument map is only a candidate for P7's exact comparison. There is no fuzzy coercion, silent repair, ranking or model-supplied target.
