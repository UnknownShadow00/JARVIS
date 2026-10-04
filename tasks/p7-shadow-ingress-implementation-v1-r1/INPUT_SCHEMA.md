# Exact input schema

| Input | Required type | Source / owner | Trust |
|---|---|---|---|
| request | exact plain `str` | accepted untrusted message primitive | content only, no authority |
| context | exact `SettledShadowTurnContextV1` | JARVIS-issued immutable view | canonical P1/P2 association and observational trace |

No defaults. Missing fields raise TypeError. Non-string request and wrong context type raise ValueError before an envelope is issued. String subclasses, including callable subclasses, are rejected without coercion. Full HTTP/JSON payload dictionaries, lists, headers, connection objects and client metadata are excluded, not interpreted by the composer.

The exact string is preserved, including whitespace, case, Unicode, empty text and embedded code points. Empty text receives no semantic validation here; downstream validators remain authoritative. No transport enum, origin label, serializer, continuation token, confirmation/result, route, tool or permission field exists.
