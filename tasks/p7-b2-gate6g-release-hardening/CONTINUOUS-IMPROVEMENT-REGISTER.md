# Gate 6G continuous improvement register

All implemented entries apply only to release-r1 in the isolated candidate. Gate 6F and production are unchanged.

| ID | Finding | Change | Validation |
|---|---|---|---|
| G01 / H-1 | An archive proof could be stale relative to live predecessor state | Read-only logical-state reader, source/config/service/D06 checks twice around signature verification | Drift and read-only fixtures; mid-verifier mutation tests |
| G02 / H-2 | Signed retirement did not bind deployed config/logical live state | Explicit source/config/archive/controller/live-state digest fields | All nine payload fields tested for substitution |
| G03 / H-3 | Injected callable was the only succession authority | Distinct signed verb, strict existing Authority seam, durable nonce/operator/body binding and atomic reservation | Replay, competing writers, identity/presence, expiry and insert-failure rollback |
| G04 / H-4 | Generic OPERATOR_STOP overstated shutdown attribution | Mechanism-specific runtime events and an actual isolated ASGI lifespan drain | Lifespan, signed stop, explicit control-mechanism and generic-stop tests |
| G05 | Global high-water joins omitted the request commitment | Enforce exact commitment/permit/ordinal/transport/session joins; validate schema/inode; immutable accepted identities and one-time attempt join | SQL mutation, permit corruption, schema drift, competing reservation and retained crash/no-refund tests |
| G06 | Coordinated snapshots did not verify succession evidence or commitments | Validate new schema, signed payload/root/bindings, exact permit commitments on snapshot review | Recomputed-checksum tamper refusal plus existing restore/rollback suite |
| G07 | Idle WS disconnect left admissions unchanged | Record CLIENT_DISCONNECT and close the isolated runtime | No-generation ASGI disconnect test; historical handshake assertion strengthened to require the refusal state/event |
| G08 | drain() stopped before validating its arguments | Validate bounded duration and mechanism before effects | Negative, oversized, boolean, NaN and infinity values leave runtime state unchanged |

One initial test failure was a fixture bug: the ordinal-immutability test used a string, so SQLite rejected its INTEGER PRIMARY KEY type before the trigger. It now uses integer 2 and still requires the exact immutability refusal. No assertion was relaxed. Earlier test runs and their exact source checks are retained.

The historical synthetic fixture's unconditional authorize=True was replaced with an explicitly synthetic signed envelope and fresh-proof fixture. Archive validation assertions remain, with signing preparation added. These fixture signatures do not certify a live host or operator.

Unchanged source: RulesFirstL1, source rules/prompts/profiles/memory, Granite observer and profile, transport, D06 ownership/domain ledger/topology, and all app/ production-source files. Existing tests continue to exercise legacy-only replies/history, 11 conditional provider operations, Granite nonvisibility, REST/WS framing/auth/disconnects, D06 uncertainty and non-refunding failures.

Pending improvements requiring outside authority remain: protected/off-host global high-water and nonce service; distinct OS identities; production human signer; AI-host/legacy identity/topology attestations; explicit X1–X11 experiment decisions (including normal responder context 8192 proposal vs current unapproved 32768); external D06 actor inventory/exclusion; power-loss and host-loss recovery qualification. None was treated as an approval or silently installed.
