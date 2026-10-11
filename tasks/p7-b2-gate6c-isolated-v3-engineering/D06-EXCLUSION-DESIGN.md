# Isolated versioned endpoint exclusion prototype

Production D06 version1 and `/home/jarvis/JARVIS/data/model-ownership-v1` are untouched. Candidate schema 5 carries a separate per-substep lease representation; this is not a migration or qualification of legacy resources under Granite's profile.

Every resource is endpoint+model+profile. A unique partial endpoint index refuses concurrent ACTIVE/REMOTE_UNKNOWN leases; the store also refuses any next substep while any active/unknown lease exists, conservatively serializing even distinct endpoints. Lifetime writer flock plus BEGIN IMMEDIATE serializes state transitions. Named substeps cannot overlap; ownership is committed before possible provider work and released to known terminal only after exact response association. Unknown is durable and there is no reset/release/reconcile/retry API.

No lifecycle capability exists in the injected provider request protocol. No load/unload/warmup/restart method is called. This prevents this bounded adapter from issuing those operations; it does not control root, cron, other services or independent endpoint clients. Shared-model keep-alive implications and external lifecycle actors require explicit endpoint-wide pilot reservation.

Tests cover active lease conflict, uncertainty at each of router/responder/Granite, stop in each substep, exact result association, endpoint exclusion, peak generation1 and no subsequent work after unknown. Process exit, elapsed time and GPU idleness are never completion evidence. Late task results are consumed without replay/evaluation or clearing an unknown lease.

Later implementation must qualify the real transport's possible-send/terminal facts, approved legacy resource contracts, a versioned D06 namespace/validator and a protected ownership handoff from the old account. Final clean V2 metadata must be independently verified; no recursive chown, clean reset or automatic unknown resolution is authorized. Every imported preserved V2 artifact must be byte-pinned and read-only rather than passed through a validator that rewrites ownership metadata.
