> **DRAFT — NOT FROZEN. P-B05 prevents final contract and fixture freeze. P-B04 authorization is separately resolved.**

# V2 security invariants

1. Zero production importers of the sealed confirmation machine. No direct, indirect, dynamic, function-local, service-locator or record-protocol access from P7.
2. Exactly three admission modes; B and C mutually exclusive. No authority boolean or resting CONFIRMED state.
3. Projection is owner-produced, immutable, plain data with exact type identity. No model payload can populate it, expected binding, permission query, invocation or result. Identity alone does not authenticate owner origin; passive caller trust is explicit.
4. B-01 through B-07 preserve ownership, pending state, exact half-open freshness, audit reference, absence of claim linkage, exact action binding and confirmable action. No record methods are needed.
5. P7 never validates by calling confirm and never claims by calling claim_for_dispatch. Only P4/P5 owns that edge; no execution edge from mode B.
6. S09 admits recorded results only. It validates C-00 through C-08 using existing types and obligations.NON_ACTION_OUTCOMES. No dispatcher dependency.
7. Proposal cardinality, exact tool identity, advertisement, full scalar-type-sensitive canonical equality and actual recomputed permission precede result admission. Model claims cannot replace any gate.
8. Every stop reason remains in the existing closed 23-member PipelineStopReason vocabulary. Confirmation failures remain uniform. No raw operational fallback.
9. Existing associated results survive downstream failures truthfully; unassociated results are never retained on early stops. No invented result or permission denial.
10. Zero executor calls, dispatch entries, claims, invocation/result creation, provenance writes and audit emissions by the future passive composer. Correlation, supplied timestamps and immutable inputs make repeated admission deterministic.
11. No mode change, live importer, provider, Hermes, Ollama, real registry or real tool activation. registry.call remains four legacy server sites.
12. V1 history, prior evidence, production sources and tests remain unchanged in this repair. Future test exceptions are restricted to the frozen inventory; all other bans stay effective.
