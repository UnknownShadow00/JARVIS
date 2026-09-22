# Trust boundary
The module imports exactly P0 ModelDraft/ToolProposal and P1 TurnId/is_well_formed_id from app; all other imports are standard-library data/serialization support.
Zero production consumers. Existing response, provenance, permission, confirmation, dispatcher, registry and live provider modules are not imported.
Repository-wide constructor scan: TrustedToolResult and ToolInvocation construction remains in dispatch.py; ApprovedOperationalResponse remains in response.py. The four legacy registry.call sites remain in server.py.
Model text and raw argument data may contain hostile assertions; those are preserved as untrusted data. Structural attempts to add authority are rejected.
The parser grants no final conversational response authority either: it returns ModelDraft, not ConversationalResponse.
