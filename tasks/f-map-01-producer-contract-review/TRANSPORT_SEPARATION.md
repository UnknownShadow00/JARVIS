# Transport separation

HTTP/WS/UI fields may identify the request channel and carry original user text. A future ingress adapter must validate session ownership and strip transport-only fields, client flags, claimed route/tool/capability/permission/confirmation/result values and any provider envelope before invoking JARVIS control-plane composition. The deterministic projection uses typed JARVIS IDs, P2 state and existing P3/P4 outputs; it has no HTTP request object, UI component state or client control flag in its schema.

Transport may forward user text as **untrusted text** to existing classifier/router. It cannot inject a `RouteResult`, `RouterContext.supported_actions`, `PermissionRequest`, `CanonicalizationResult`, confirmation projection or `TrustedToolResult`. Any future UI metadata used as operational state needs a separately frozen trust/source contract; none is inferred here.
