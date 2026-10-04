# Invariants

1. JARVIS alone mints and resolves authoritative session/turn association.
2. Client strings and model claims never select authoritative P2 state.
3. One accepted logical input produces one turn, including WS fallback.
4. One session owns one ledger; cross-session snapshots are rejected.
5. Turn creation precedes immutable snapshot, which precedes evaluation.
6. Settled output exposes no mutable store or execution-capable object.
7. Shadow writes no provenance, confirmation or operational audit truth.
8. Trace is observational and cannot stand in for turn or session.
9. Correlation reuses P1 without a competing ID family.
10. A shadow failure neither changes legacy output nor creates fallback authority.
11. Voice, retry protocol, retention, live wiring and scheduling remain unimplemented.
12. No permission, confirmation, audit-v3, browser D-01 or P8 gate changes.
