# Canonical authority and source inventory

All actual source references are pinned to Core d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c. Production git has the production revision; documentation revisions are separately resolved from workspace git and canonical sealed documentation-commit inventory.

| Authority | Canonical location / significance |
|---|---|
| Context V1 | autonomous bundle unit-a/docs; commit 63984cac4bacb0d1a28ef9bff9f0ab3ee7e52200; correlation/snapshot/trace source |
| Envelope V1 | autonomous bundle unit-b/docs; commit 4fb1d4da1342b35f7ed997550a45dccd69922eca; exact raw request + settled context, no transport field |
| Preparation / exact D03 | autonomous bundle unit-d/docs; commit f523900decbde453858e808c93d678b97657ef9b; historical field gaps and remaining decisions |
| Binding projection implementation | binding-projection-v1-r1 sealed docs; source binding_projection.py:30-51,154-208,211-238; five-field V1 and closed two rows |
| Registry metadata | registry-metadata-snapshot-r1; registry_metadata.py:45-50 canonical JSON/SHA256; no observation call to its file-reading source function |
| Passive pipeline | R8 reports and actual pipeline.py:29-80,104-159,197-202,231-277,345-499; return shapes, discarded private guard label and settled local facts |
| Existing response/identity/policy vocabulary | types.py:41,102-107,154-169,189-211,326-352; correlation.py:110-159; permissions.py:387-427; router.py:290-309 |
| Full P7 requirement | sealed 13B11A phase/graph and PRODUCTION_INTEGRATION_PLAN §7; formal measured shadow and P8 gate preserved |
| CT definitions | sealed 13B10D CONFORMANCE_TESTS.md:26-32,117-123; visible-path CT-001 and conversational CT-013 |

Seven required/supporting bundles verified with 593 checks, zero failures. 100 local authority files compared byte-for-byte with the sealed canonical copies, zero differences. Evidence includes copied sources, exact historical decision and type collision scan. No runtime evaluation was needed to derive this contract.
