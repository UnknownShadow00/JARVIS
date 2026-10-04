# Per-session store

The owner holds the existing instance-owned LedgerStore. Each active JARVIS session maps to one ProvenanceLedger, with its own records. `for_session(session_id)` provides get-or-create under the existing store lock; another session must resolve to another ledger. No global ledger, parallel provenance scheme, client-owned ledger or model-created state.

The owner may establish association and read snapshots. Ownership does not authorize record_user_fact, record_tool_result, record_control_state, confirmation writes or any other provenance promotion in inert shadow. Do not expose LedgerStore or ProvenanceLedger in the settled context. Existing drop/clear are lifecycle mechanisms only; retention policy and lifecycle triggers are not selected.
