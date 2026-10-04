# Client text is not control-plane state

Only exact message text enters `request`; authority-looking words/JSON inside the string remain untrusted text. Client metadata such as session_id, turn_id, correlation/correlation_id, route, tool, capability, permission, confirmed, executed and TrustedToolResult never becomes envelope state.

Tests extract only `payload['message']` in fixtures and prove changing all other keys cannot alter canonical context. Passing the whole mapping is rejected as non-string; passing extra authority constructor keywords raises TypeError. No payload parser, compatibility mapping or adapter is added to production.

Session and turn remain exactly the issued correlation's values. No client/model claim selects a ledger, snapshot, turn, permission or tool. Python type identity is structural validation, not origin authentication; transport admission is separate D01/D02 work.
