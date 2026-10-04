# Trace association remains observational

The primitive accepts only a nonempty exact plain `str` or explicit `None` as optional observational metadata. It stores that immutable value unchanged. It does not read tracing/server APIs, infer a transport, convert/hash/parse the trace, derive a TurnId, mint a fake trace or let a trace select state.

Future trusted transport callers capture the active server trace before settlement; that integration is not implemented. Tests use server-observation-shaped metadata only, reject empty/non-string/callable-subclass values, retain absence as None and repeat traces across distinct newly minted turns. A trace equal to a different owner's session still selects only the current owner's ledger. UUID-shaped trace text remains metadata.

`trace-turn-proof.json` records the separate P1 composite and observational string. No claim that trace can never coincidentally share an identical string is introduced; the authorities and minting paths are independent.
