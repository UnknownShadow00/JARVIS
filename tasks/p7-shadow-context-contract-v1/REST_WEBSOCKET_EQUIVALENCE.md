# Transport equivalence

REST and WS both resolve JARVIS session, mint one P1 turn, capture P2, settle and then compose. The same logical context uses the same continuation authority across transports. Transport changes neither trust nor correlation rules. Distinct turns have distinct IDs even when request text is equal; compare semantic fields after accounting for those minted IDs and observational traces.

REST captures after acceptance/wake succeeds, before _process. WS captures once after message acceptance/wake and active trace, before _process_stream; the _process fallback and output chunks reuse the same attempt. Exact line anchors belong to Envelope V1 continuation. Voice directly reaches these internals and is not covered.
