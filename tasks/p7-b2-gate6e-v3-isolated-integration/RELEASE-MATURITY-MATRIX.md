# Release maturity matrix

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

|Interface|Classification|Qualification boundary|
|---|---|---|
|Rules-first L1 and source profiles|IMPLEMENTED, ISOLATED-TESTED; DEPENDS ON OPERATOR EXPERIMENT CHOICE|No stochastic or approved experiment equivalence|
|Native transport|IMPLEMENTED, ISOLATED-TESTED|Fake HTTP only; real stack/provider qualification pending|
|REST/WS FastAPI graph|IMPLEMENTED, ISOLATED-TESTED|No live route/startup mount|
|D04 schema/receipt + D09 association extension|IMPLEMENTED, ISOLATED-TESTED|No production controller/collector migration|
|Actual D06 V1 fixture lease adapter|IMPLEMENTED, ISOLATED-TESTED|Version2 shared domains PROTOTYPED ONLY for deployment|
|AF_UNIX control / verifier|IMPLEMENTED, OS QUALIFICATION PENDING|Dummy signer, current UID only; real helper BLOCKED|
|V2 archive validator / high-water|IMPLEMENTED, ISOLATED-TESTED|Protected root DEPENDS ON PRIVILEGED PRODUCTION DEPLOYMENT|
|Coordinated checkpoints / terminal drain|IMPLEMENTED, ISOLATED-TESTED|Actual privilege/race, supervisor and host-loss qualification pending|
|Effective legacy endpoint/models/digests|DEPENDS ON VERIFIED INFRASTRUCTURE|UNVERIFIED, not approved|
|AI host/external exclusivity|DEPENDS ON VERIFIED INFRASTRUCTURE|Independent trust pending|
|Production factory, V2 retirement, V3 storage/install|BLOCKED; DEPENDS ON PRIVILEGED PRODUCTION DEPLOYMENT|No authority granted|

A complete **isolated** source-consumer graph now exists: validated synthetic V2 archive → root/acceptance guard → signed local control → FastAPI/ASGI ingress → Runtime rules/classifier/selected responder → actual D06 fixture lease/domain → bounded native fake transport → legacy delivery/history → canonical Granite observer → actual D04 schema/receipt association → coordinated checkpoint → next permit/terminal drain. The application builder verifies required consumer types and root identity. Historical fake policy is not accepted by it.

This graph is not an approved production composition or migration. Real signer, supervisor attestation, protected common storage, endpoint/model proofs, external actor exclusions and live server integration are unavailable. Passing fixtures do not make those controls proven.
