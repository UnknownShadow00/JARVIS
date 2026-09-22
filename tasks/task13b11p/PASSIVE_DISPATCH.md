# S08–S09 boundary not selected by a concrete API
V1 UPDATED_GUARD_ORDER.md:22–23 describes eligible confirmation handoff followed by recorded current-result/invocation/claim linkage, or a later explicitly isolated P5 boundary. Its dispatch proof explicitly says the recorded core makes no dispatch call.

Current ConfirmationStore.claim_for_dispatch is a mutating atomic authority, not an immutable observation; TrustedDispatcher owns its invocation and settlement. ConfirmationRecord is only a snapshot. Existing P5 can support isolated tests, but selecting/inventing a production P7 executor callback seam would be an additional input contract.

Recommended resolution for review, NOT FROZEN: choose recorded-only production composition and generate all replay evidence outside it with actual P4/P5 inert test setup; enumerate exact evidence fields and admission rules. Alternatively explicitly freeze an isolated P5 continuation API and its authority/isolation requirements. Do not smuggle that choice through an untyped session, arbitrary callback or confirmed bool.

No new dispatcher or executor was called in this task's diagnostics. The mandated existing regression suite retains its existing inert component fixtures; that is not P7 execution-count/replay proof.
