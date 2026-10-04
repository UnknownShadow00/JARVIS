# Exact source decisions before retry

1. **P1 SESSION/TURN SOURCE DECISION REQUIRED:** choose the JARVIS-owned session lifecycle across REST and WS, turn minting point, and retry/reconnection rule using existing P1 constructors. Current production has no such live owner.
2. **P2 SNAPSHOT SOURCE DECISION REQUIRED:** assign the per-session `LedgerStore` owner/lifetime and request-time read point, or approve another existing canonical source with equal P2 semantics. Current request paths have none.
3. **CORRELATION ASSOCIATION DECISION REQUIRED:** specify exact trace UUID ↔ P1 TurnId relation and mapping, preserving audit join and binder validation.

After these, finish exact envelope field schema and capture placement; then address F-SHADOW-ADAPTER-INPUT/scheduling/audit/CT separately. Do not guess any missing owner in this record.
