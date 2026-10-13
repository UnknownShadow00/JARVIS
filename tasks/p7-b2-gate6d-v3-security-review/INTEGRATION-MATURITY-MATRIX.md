# Integration maturity

Classification is for the candidate interface, not for the unchanged live V2 service.

| Interface | Classification | Evidence / remaining work |
|---|---|---|
| Strict JSON, authority schema and signed-body verification seam | IMPLEMENTED AND ISOLATED-TESTED | Dummy HMAC verifier and typed peer only; no production signer |
| Four-attempt ledger and one-parent successor reservation | IMPLEMENTED AND ISOLATED-TESTED | Transactions, crash/race/replay cases pass; protected global authority still missing |
| REST ASGI adapter/envelope | IMPLEMENTED AND ISOLATED-TESTED | Direct in-process ASGI calls; not mounted in FastAPI |
| WS ASGI adapter/envelope/continuation | IMPLEMENTED AND ISOLATED-TESTED | Malformed/control/binary/auth tested; actual origin middleware and disconnect receiver missing |
| API authentication integration | PROTOTYPED ONLY | Candidate injected bytes; no private loader or canonical app middleware connection |
| Legacy L1/L2 response adapter | PROTOTYPED ONLY | Fake providers; single responder differs from legacy complexity path |
| Canonical Granite capture/normalizer/evaluator | IMPLEMENTED AND ISOLATED-TESTED | Exact resource/frozen limits + request body verified; canonical passive projection tested |
| Real bounded native provider transport | DESIGNED BUT NOT IMPLEMENTED | Need response-size enforcement while reading, exact terminal/send proof, no redirects/retries/discovery |
| D06 durable ownership | PROTOTYPED ONLY | Isolated schema5 steps/leases; no production coordinator/exclusion/migration adapter |
| D04/D09 operational event association | PROTOTYPED ONLY | Minimized local receipt append/join; not production sink/controller API |
| Backup writer | IMPLEMENTED AND ISOLATED-TESTED | Fixture manifest3/checkpoint/forensic validation; target filesystem/ownership/restore integration missing |
| Stop/drain | PROTOTYPED ONLY | Local cancellation bounded around await; synchronous I/O and final checkpoint/supervisor incomplete |
| Production startup/routing/factory | DESIGNED BUT NOT IMPLEMENTED | Factory deliberately refuses; new source-consumer graph must be reviewed |
| Operator control transport, kernel peers, signer | DESIGNED BUT NOT IMPLEMENTED | No Unix listener/helper/credential mechanism installed |
| Protected global predecessor validator and reservation publication | DESIGNED BUT NOT IMPLEMENTED | Strings/local reservation cannot attest V2 closure or global uniqueness |
| Dedicated identity, credentials, protected unit/release | REQUIRES NEW APPROVAL | Real users/units/permissions were not created; actual separate-UID tests pending |
| Provider/router/prompt/memory contract | REQUIRES NEW APPROVAL | G6D-LP-1 proposal; no defaults inferred |
| V2 retirement / V3 install / renewed Gate5 / pilot | REQUIRES NEW APPROVAL | Distinct authorities; no operational actions |

Canonical source/fixture separation is preserved: candidate_v3 is standalone; all canonical app and original test bytes unchanged. The full suite proves the isolated copy against its baseline configuration plus explicit pilot fixtures. It does not certify live adapter mounting, operating-system separation or the new release graph.
