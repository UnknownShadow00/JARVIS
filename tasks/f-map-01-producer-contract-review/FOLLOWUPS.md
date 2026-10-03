# Exact decisions needed to unblock F-MAP-01

**Decision 1 — closed live binder schema:** For each approved routed action/capability, sign the exact tool namespace, required/optional/forbidden argument keys and types, target-bearing field and mapping from P3 `RouteResult.target` into it, rules for extras/ambiguity/unknown targets, and versioning. Existing P4 pairs alone are insufficient. Do not infer `apps.open`→`apps` or `browser.open`→`browser` from spelling or legacy/harness code.

**Decision 2 — capability truth source:** Identify the JARVIS-owned, independently validated live inventory that can narrow `RouterContext.supported_actions` and agree with registered P4 rows. A model-advertised schema, default router vocabulary or client flag is not a grant. This is LIVE-02 from `task13b11o/FOLLOWUPS.md`.

**Decision 3 — implementation path:** The conceptual P7 execution integration owner is fixed, but no separate producer module is named in 13B11A. Freeze its exact path and ingress handoff before coding; keep server transport adaptation separate.

These are operator/architecture decisions required for **this full contract freeze**; no alternative was silently selected. F-P7R1-01, F-REPLAY-01, F-FALLBACK-01, F-AUDIT-01, browser D-01 and FUTURE-AGENT-BRIDGE retain their prior classifications in `DEFERRED.md`. Next smallest unit is an operator-signed binder-schema and inventory-source decision packet, not producer implementation.
