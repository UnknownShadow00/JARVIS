# D06 resource and ownership integration

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

`OwnedProvider` validates a durable accepted substep's attempt/resource/profile/request hash before acquiring ownership. Actual ModelOwnershipCoordinatorV1 fixture coordinators use exact endpoint/model keys. A separate version2 DomainLedger records an operation once and durably excludes all named conflict domains plus the endpoint. It retains completed operation identities to prevent replay after release. Separate model/profile coordinators sharing an endpoint cannot overlap through this graph. Distinct endpoints with an explicitly shared GPU domain also conflict; host sharing is never inferred.

NativeTransport requires the actual GenerationLeaseV1 and consumes claim_transport once. Wrong resource, wrong substep, absent lease, replay, conflict or uncertain owner refuses before transport. Successful terminal evidence closes the correct model lease, then the durable domain hold; failures preserve REMOTE_UNKNOWN. A crash between these writes remains conservatively blocked. Store.begin independently serializes the accepted conversation's router/responder/Granite substeps. Router and responder never inherit Granite's lease.

The lifecycle entry point always refuses. No wake/load/unload helper or tool executor is imported. This is a versioned isolated seam over actual V1 fixture APIs; V1 production storage cannot simply support multiple models by creating more namespaces. All cooperating lifecycle clients must adopt the common exclusion domain and a protected configuration. External cron, supervisors, direct clients and another V1 caller remain an independent exclusivity risk. Their exclusion is NOT proven by candidate tests.

Classification: IMPLEMENTED, ISOLATED-TESTED adapter; multi-resource production migration PROTOTYPED ONLY / DEPENDS ON PRIVILEGED PRODUCTION DEPLOYMENT and verified infrastructure. No production D06 changes.
