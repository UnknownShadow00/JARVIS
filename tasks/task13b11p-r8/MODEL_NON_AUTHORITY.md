# Model remains untrusted

Adapter consumption is exact and passive. parse_recorded_response returns ModelDraft/ToolProposal with caller-owned IDs. The model cannot supply admission mode, route, capability, permission, confirmation, invocation/result, provenance trust or operational output. Extra authority fields fail parser validation. Prose that claims ALLOW/confirmed/SUCCESS/yes remains text and cannot replace settled control-plane data.

Operational output always uses obligations.derive and response.build; no raw draft fallback. Conversation may return MODEL_RAW only on the frozen conversational branch without operational obligation. The test corpus verifies fake authority, route/capability creation attempts, replay errors and cross-association, and direct closed-schema attempts to inject executable collaborators.
